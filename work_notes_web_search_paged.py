from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, abort, flash
import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_NOTES_FOLDER = os.path.join(BASE_DIR, "notes")
os.makedirs(WORK_NOTES_FOLDER, exist_ok=True)

PAGE_SIZE = 50
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def date_to_filename(date_str: str) -> str:
    if not DATE_RE.match(date_str):
        abort(400, "Invalid date format. Use YYYY-MM-DD.")
    return f"{date_str}.txt"

def filename_to_date(filename: str) -> str:
    if filename.endswith(".txt"):
        base = filename[:-4]
        if DATE_RE.match(base):
            return base
    return None

def list_all_dates():
    dates = []
    for name in os.listdir(WORK_NOTES_FOLDER):
        if name.endswith(".txt"):
            d = filename_to_date(name)
            if d:
                dates.append(d)
    dates.sort(reverse=True)
    return dates

def read_note(date_str: str) -> str:
    filename = date_to_filename(date_str)
    path = os.path.join(WORK_NOTES_FOLDER, filename)
    if not os.path.exists(path):
        abort(404, "Note not found.")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_note(date_str: str, content: str) -> None:
    filename = date_to_filename(date_str)
    path = os.path.join(WORK_NOTES_FOLDER, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def delete_note_file(date_str: str) -> None:
    filename = date_to_filename(date_str)
    path = os.path.join(WORK_NOTES_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)

app = Flask(__name__)
app.secret_key = "dev-only"

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Work Notes</title>
    <style>
        body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; line-height: 1.5; }
        .container { max-width: 1000px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }
        a { text-decoration: none; }
        .btn { display: inline-block; padding: 8px 12px; border: 1px solid #999; border-radius: 8px; }
        .btn:hover { background: #f3f3f3; }
        .list { margin-top: 16px; }
        .note-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #eee; gap: 8px; }
        textarea { width: 100%; height: 420px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Courier New', monospace; font-size: 14px; }
        pre { white-space: pre-wrap; word-wrap: break-word; border: 1px solid #eee; padding: 12px; border-radius: 8px; background: #fafafa; }
        form { margin-top: 12px; }
        label { display: block; font-weight: 600; margin-bottom: 6px; }
        input[type='date'], input[type='text'] { padding: 6px 8px; border: 1px solid #ccc; border-radius: 6px; }
        .actions { display: flex; gap: 8px; flex-wrap: wrap; }
        .flash { color: #090; margin: 0 0 12px 0; }
        .searchbar { display: grid; grid-template-columns: 1fr auto auto auto; gap: 8px; align-items: end; }
        .meta { color: #666; font-size: 14px; }
        .pagination { display: flex; gap: 6px; margin-top: 12px; flex-wrap: wrap; }
        .page-link { padding: 6px 10px; border: 1px solid #ccc; border-radius: 6px; }
        .page-link.active { background: #eee; font-weight: 700; }
        .no-wrap { white-space: nowrap; }
    </style>
    <script>
      function confirmDelete(dateStr) {
        return confirm('Delete note ' + dateStr + '? This cannot be undone.');
      }
    </script>
</head>
<body>
<div class="container">
    <header>
        <h1><a href="{{ url_for('home') }}">Work Notes</a></h1>
        <div class="actions">
            <a class="btn" href="{{ url_for('new_note') }}">New Note</a>
        </div>
    </header>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        {% for m in messages %}
          <div class="flash">{{ m }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}
    {{ body | safe }}
</div>
</body>
</html>
'''

def render(body: str, **kwargs):
    return render_template_string(BASE_TEMPLATE, body=body, **kwargs)

def apply_date_filter(dates, date_from, date_to):
    def in_range(d):
        ok = True
        if date_from:
            ok = ok and (d >= date_from)
        if date_to:
            ok = ok and (d <= date_to)
        return ok
    return [d for d in dates if in_range(d)]

def apply_search_filter(dates, query):
    if not query:
        return dates, 0
    q = query.lower()
    matched = []
    scanned = 0
    for d in dates:
        content = read_note(d).lower()
        scanned += 1
        if q in content or q in d:
            matched.append(d)
    return matched, scanned

def pagination_slices(items, page, page_size):
    total = len(items)
    pages = (total // page_size) + (1 if total % page_size else 0)
    if page < 1: page = 1
    if page > pages and pages > 0: page = pages
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], page, pages, total

@app.route("/")
def home():
    q = request.args.get("q", "").strip()
    date_from = request.args.get("from", "").strip()
    date_to = request.args.get("to", "").strip()
    page = int(request.args.get("page", "1"))

    all_dates = list_all_dates()
    filtered_dates = apply_date_filter(all_dates, date_from if DATE_RE.match(date_from) else None,
                                                 date_to   if DATE_RE.match(date_to)   else None)
    result_dates, scanned = apply_search_filter(filtered_dates, q)

    page_items, page, pages, total = pagination_slices(result_dates, page, PAGE_SIZE)

    def link_with_params(target_page):
        base = {"page": target_page}
        if q: base["q"] = q
        if date_from: base["from"] = date_from
        if date_to: base["to"] = date_to
        return url_for("home", **base)

    body = [f"""
    <form class="searchbar" method="GET" action="{url_for('home')}">
        <div>
            <label for="q">Search</label>
            <input id="q" type="text" name="q" value="{q}" placeholder="Search text or date (YYYY-MM-DD)">
        </div>
        <div class="no-wrap">
            <label for="from">From</label>
            <input id="from" type="date" name="from" value="{date_from}">
        </div>
        <div class="no-wrap">
            <label for="to">To</label>
            <input id="to" type="date" name="to" value="{date_to}">
        </div>
        <div>
            <button class="btn" type="submit">Apply</button>
        </div>
    </form>
    <div class="meta">
        Showing <strong>{len(page_items)}</strong> of <strong>{total}</strong> matching notes {f"(scanned {scanned} files for search)" if q else ""}.
    </div>
    <div class='list'>
    """]

    if not page_items:
        body.append("<p>No matching notes.</p>")
    else:
        for d in page_items:
            body.append(f"""
            <div class="note-item">
                <div>
                    <a href="{url_for('read_note_view', date_str=d)}"><strong>{d}</strong></a>
                </div>
                <div class="actions">
                    <a class="btn" href="{url_for('download_note', date_str=d)}">Download</a>
                    <a class="btn" href="{url_for('edit_note', date_str=d)}">Edit</a>
                    <a class="btn" style="border-color:#c00;color:#c00" href="{url_for('delete_note', date_str=d)}" onclick="return confirmDelete('{d}')">Delete</a>
                </div>
            </div>
            """)
    body.append("</div>")

    if pages > 1:
        body.append('<div class="pagination">')
        if page > 1:
            body.append(f'<a class="page-link" href="{link_with_params(page-1)}">&laquo; Prev</a>')
        else:
            body.append('<span class="page-link" style="opacity:.4; pointer-events:none;">&laquo; Prev</span>')
        start_p = max(1, page - 3)
        end_p = min(pages, page + 3)
        if start_p > 1:
            body.append(f'<a class="page-link" href="{link_with_params(1)}">1</a>')
            if start_p > 2:
                body.append('<span class="page-link" style="border:none;">…</span>')
        for p in range(start_p, end_p + 1):
            cls = "page-link active" if p == page else "page-link"
            body.append(f'<a class="{cls}" href="{link_with_params(p)}">{p}</a>')
        if end_p < pages:
            if end_p < pages - 1:
                body.append('<span class="page-link" style="border:none;">…</span>')
            body.append(f'<a class="page-link" href="{link_with_params(pages)}">{pages}</a>')
        if page < pages:
            body.append(f'<a class="page-link" href="{link_with_params(page+1)}">Next &raquo;</a>')
        else:
            body.append('<span class="page-link" style="opacity:.4; pointer-events:none;">Next &raquo;</span>')
        body.append('</div>')

    return render("".join(body))

@app.route("/new", methods=["GET", "POST"])
def new_note():
    if request.method == "POST":
        date_str = request.form.get("date", "").strip()
        content = request.form.get("notes", "")
        if not date_str:
            date_str = datetime.today().strftime("%Y-%m-%d")
        if not DATE_RE.match(date_str):
            flash("Invalid date format. Use YYYY-MM-DD.")
        else:
            write_note(date_str, content)
            flash(f"✅ Saved {date_str}.txt")
            date_str = datetime.today().strftime("%Y-%m-%d")
            body = f"""
            <form method="POST">
                <label for="date">Date</label>
                <input type="date" id="date" name="date" value="{date_str}" required>
                <label for="notes">Notes</label>
                <textarea id="notes" name="notes" placeholder="- Bullet points work great here..." required></textarea>
                <div class="actions">
                    <button class="btn" type="submit">Save</button>
                    <a class="btn" href="{url_for('home')}">Back</a>
                </div>
            </form>
            """
            return render(body)

    default_date = datetime.today().strftime("%Y-%m-%d")
    body = f"""
    <form method="POST">
        <label for="date">Date</label>
        <input type="date" id="date" name="date" value="{default_date}" required>
        <label for="notes">Notes</label>
        <textarea id="notes" name="notes" placeholder="- Bullet points work great here..." required></textarea>
        <div class="actions">
            <button class="btn" type="submit">Save</button>
            <a class="btn" href="{url_for('home')}">Back</a>
        </div>
    </form>
    """
    return render(body)

@app.route("/note/<date_str>")
def read_note_view(date_str):
    if not DATE_RE.match(date_str):
        abort(400, "Invalid date.")
    content = read_note(date_str)
    body = f"""
    <h2>{date_str}</h2>
    <pre>{content}</pre>
    <div class="actions" style="margin-top:12px;">
        <a class="btn" href="{url_for('edit_note', date_str=date_str)}">Edit</a>
        <a class="btn" href="{url_for('download_note', date_str=date_str)}">Download</a>
        <a class="btn" style="border-color:#c00;color:#c00" href="{url_for('delete_note', date_str=date_str)}" onclick="return confirm('Delete note {date_str}? This cannot be undone.')">Delete</a>
        <a class="btn" href="{url_for('home')}">Back</a>
    </div>
    """
    return render(body)

@app.route("/edit/<date_str>", methods=["GET", "POST"])
def edit_note(date_str):
    if not DATE_RE.match(date_str):
        abort(400, "Invalid date.")
    if request.method == "POST":
        content = request.form.get("notes", "")
        write_note(date_str, content)
        flash(f"✅ Updated {date_str}.txt")
        return redirect(url_for("read_note_view", date_str=date_str))

    content = read_note(date_str)
    body = f"""
    <h2>Edit {date_str}</h2>
    <form method="POST">
        <label for="notes">Notes</label>
        <textarea id="notes" name="notes" required>{content}</textarea>
        <div class="actions">
            <button class="btn" type="submit">Save</button>
            <a class="btn" href="{url_for('read_note_view', date_str=date_str)}">Cancel</a>
        </div>
    </form>
    """
    return render(body)

@app.route("/download/<date_str>")
def download_note(date_str):
    if not DATE_RE.match(date_str):
        abort(400, "Invalid date.")
    filename = date_to_filename(date_str)
    return send_from_directory(WORK_NOTES_FOLDER, filename, as_attachment=True)

@app.route("/delete/<date_str>")
def delete_note(date_str):
    if not DATE_RE.match(date_str):
        abort(400, "Invalid date.")
    delete_note_file(date_str)
    flash(f"🗑️ Deleted {date_str}.txt")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)