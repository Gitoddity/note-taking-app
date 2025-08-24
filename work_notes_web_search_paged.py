# work_notes_web_search_paged.py (DictLoader templates)
import os
import re
import datetime
from flask import Flask, request, redirect, url_for, send_from_directory, abort, flash, render_template
from markupsafe import Markup
from jinja2 import DictLoader

app = Flask(__name__)
app.secret_key = "dev-secret"  # change for production

# --- Storage location ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_DIR = os.getenv("NOTES_DIR", os.path.join(BASE_DIR, "notes"))
os.makedirs(NOTES_DIR, exist_ok=True)

# --- Helpers ---
SAFE_CHARS_RE = re.compile(r"[^A-Za-z0-9\-_]")

def sanitize_text(s: str) -> str:
    s = (s or "").strip().replace(" ", "_")
    return SAFE_CHARS_RE.sub("", s)

def today_str() -> str:
    return datetime.date.today().strftime("%Y-%m-%d")

def build_filename(single_date: str, from_date: str, to_date: str, text: str) -> str:
    st = sanitize_text(text)
    if from_date and to_date:
        base = f"{from_date}_to_{to_date}"
        return f"{base}_{st}.txt" if st else f"{base}.txt"
    if single_date:
        base = f"{single_date}"
        return f"{base}_{st}.txt" if st else f"{base}.txt"
    if st:
        return f"{st}.txt"
    return f"{today_str()}.txt"

def is_valid_date_str(s: str) -> bool:
    try:
        datetime.date.fromisoformat(s)
        return True
    except Exception:
        return False

def list_notes():
    items = []
    for name in os.listdir(NOTES_DIR):
        if not name.lower().endswith(".txt"):
            continue
        path = os.path.join(NOTES_DIR, name)
        if os.path.isfile(path):
            stat = os.stat(path)
            items.append((name, stat.st_mtime))
    items.sort(key=lambda t: t[1], reverse=True)  # newest first
    return [name for name, _ in items]

# --- Templates (registered with DictLoader) ---
TPL_BASE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{{ title or "Work Notes" }}</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { --bg:#0b0f14; --card:#121822; --muted:#95a1b3; --fg:#e8eef8; --acc:#4ea1ff; }
    body { margin:0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; background: var(--bg); color: var(--fg);}
    header, main { max-width: 920px; margin: 0 auto; padding: 16px; }
    header { display:flex; gap:12px; align-items:center; justify-content:space-between; }
    a { color: var(--acc); text-decoration: none; }
    .btn { display:inline-block; padding:8px 12px; border-radius:10px; background:#1b2533; color:var(--fg); border:1px solid #273244; }
    .btn:hover { background:#233041; }
    .card { background: var(--card); border:1px solid #1e2837; border-radius:14px; padding:16px; }
    .grid { display:grid; gap:12px; }
    .list li { display:flex; justify-content:space-between; border-bottom:1px dashed #1e2837; padding:8px 0; }
    input, textarea { width: 100%; padding:10px; border-radius:10px; border:1px solid #273244; background:#0f141c; color:var(--fg); }
    label { color: var(--muted); font-size: 0.9rem; margin-top: 8px; display:block; }
    .row { display:grid; grid-template-columns: 1fr 1fr; gap:12px; }
    .flash-ok { background:#12331c; border:1px solid #1e6b2c; color:#a7e8b8; padding:10px 12px; border-radius:10px; }
    .flash-err{ background:#381616; border:1px solid #7a2727; color:#ffc2c2; padding:10px 12px; border-radius:10px; }
    code { background:#0f141c; padding:2px 6px; border-radius:6px; border:1px solid #273244; }
    .muted { color: var(--muted); }
  </style>
</head>
<body>
<header>
  <div><a href="{{ url_for('index') }}" class="btn">📓 Notes</a></div>
  <div class="grid" style="grid-auto-flow: column; gap:8px;">
    <a href="{{ url_for('new_note') }}" class="btn">➕ New</a>
  </div>
</header>
<main class="grid">
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for cat, msg in messages %}
        <div class="{{ 'flash-ok' if cat=='ok' else 'flash-err' if cat=='error' else 'card' }}">{{ msg|safe }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}
  {% block content %}{% endblock %}
</main>
</body>
</html>"""

TPL_INDEX = r"""{% extends "base.html" %}
{% block content %}
<div class="card grid" style="gap:14px;">
  <form method="get">
    <label for="q">Search filenames</label>
    <input id="q" name="q" value="{{ q }}" placeholder="e.g. weekly, 2025-08, retro">
  </form>
  <div class="muted">Showing {{ files|length }} file{{ '' if files|length==1 else 's' }}.</div>
  <ul class="list" style="list-style:none; padding-left:0;">
    {% for f in files %}
      <li>
        <a href="{{ url_for('view_note', name=f) }}">{{ f }}</a>
        <a href="{{ url_for('download', name=f) }}" class="muted">download</a>
      </li>
    {% else %}
      <li class="muted">No notes yet. Click “New”.</li>
    {% endfor %}
  </ul>
</div>
{% endblock %}"""

TPL_NEW = r"""{% extends "base.html" %}
{% block content %}
<div class="card grid" style="gap:16px;">
  <form method="post" id="noteForm">
    <div class="row">
      <div>
        <label for="date">Single Date</label>
        <input type="date" id="date" name="date" value="">
      </div>
      <div></div>
    </div>

    <div class="row">
      <div>
        <label for="from_date">From</label>
        <input type="date" id="from_date" name="from_date">
      </div>
      <div>
        <label for="to_date">To</label>
        <input type="date" id="to_date" name="to_date" disabled>
      </div>
    </div>

    <div>
      <label for="filename">Filename text (optional)</label>
      <input type="text" id="filename" name="filename" placeholder="e.g. weekly_recap or meeting_notes">
      <div class="muted">If date(s) are selected, the date(s) will come first and this text will be appended.</div>
    </div>

    <div>
      <label for="notes">Notes</label>
      <textarea id="notes" name="notes" rows="10" placeholder="Write your notes here..."></textarea>
    </div>

    <div class="grid" style="grid-auto-flow: column; justify-content: start; gap:8px;">
      <button type="submit" class="btn">Save</button>
      <a class="btn" href="{{ url_for('index') }}">Cancel</a>
    </div>
  </form>
</div>

<script>
  // Enforce: To disabled until From set; To >= From
  const fromEl = document.getElementById('from_date');
  const toEl   = document.getElementById('to_date');

  function syncDates() {
    if (fromEl.value) {
      toEl.disabled = false;
      toEl.min = fromEl.value;
      if (toEl.value && toEl.value < fromEl.value) {
        toEl.value = fromEl.value;
      }
    } else {
      toEl.disabled = true;
      toEl.value = "";
      toEl.removeAttribute('min');
    }
  }
  fromEl.addEventListener('change', syncDates);
  toEl.addEventListener('focus', () => {
    if (toEl.disabled) {
      alert('Pick a From date first.');
    }
  });
</script>
{% endblock %}"""

TPL_VIEW = r"""{% extends "base.html" %}
{% block content %}
<div class="card grid" style="gap:12px;">
  <div><strong>Viewing:</strong> <code>{{ name }}</code></div>
  <pre style="white-space: pre-wrap; margin:0;">{{ text }}</pre>
  <div><a class="btn" href="{{ url_for('download', name=name) }}">Download</a></div>
</div>
{% endblock %}"""

# Register templates
app.jinja_loader = DictLoader({
    "base.html": TPL_BASE,
    "index.html": TPL_INDEX,
    "new.html": TPL_NEW,
    "view.html": TPL_VIEW,
})

# --- Routes ---
@app.route("/", methods=["GET"])
def index():
    q = (request.args.get("q") or "").strip().lower()
    files = list_notes()
    if q:
        files = [f for f in files if q in f.lower()]
    return render_template("index.html", files=files, q=q)

@app.route("/new", methods=["GET", "POST"])
def new_note():
    if request.method == "POST":
        single_date = (request.form.get("date") or "").strip()
        from_date   = (request.form.get("from_date") or "").strip()
        to_date     = (request.form.get("to_date") or "").strip()
        filename_tx = (request.form.get("filename") or "").strip()
        content     = request.form.get("notes") or ""

        if to_date and not from_date:
            flash("Please select a From date before a To date.", "error")
            return redirect(url_for("new_note"))

        if single_date and not is_valid_date_str(single_date):
            flash("Invalid single date format.", "error")
            return redirect(url_for("new_note"))
        if from_date and not is_valid_date_str(from_date):
            flash("Invalid From date format.", "error")
            return redirect(url_for("new_note"))
        if to_date and not is_valid_date_str(to_date):
            flash("Invalid To date format.", "error")
            return redirect(url_for("new_note"))

        if from_date and to_date and to_date < from_date:
            flash("To date cannot be before From date.", "error")
            return redirect(url_for("new_note"))

        final_name = build_filename(single_date, from_date, to_date, filename_tx)

        try:
            path = os.path.join(NOTES_DIR, final_name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            flash(Markup(f"Saved <code>{final_name}</code>"), "ok")
            return redirect(url_for("index"))
        except Exception as e:
            flash(f"Error saving note: {e}", "error")
            return redirect(url_for("new_note"))
    return render_template("new.html", today=today_str())

@app.route("/view/<path:name>")
def view_note(name):
    safe = os.path.basename(name)
    path = os.path.join(NOTES_DIR, safe)
    if not (os.path.isfile(path) and safe.lower().endswith(".txt")):
        abort(404)
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return render_template("view.html", name=safe, text=text)

@app.route("/download/<path:name>")
def download(name):
    safe = os.path.basename(name)
    if not (safe.lower().endswith(".txt")):
        abort(404)
    return send_from_directory(NOTES_DIR, safe, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
