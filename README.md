\# Note-Taking App 📝



A simple \*\*Flask\*\*-based web app to create, view, and manage notes — built as part of my Python learning journey.  

This project demonstrates \*\*Flask basics\*\*, clean project structure, and good development practices with virtual environments.



---



\## 🚀 Features

\- Add, view, and delete notes

\- Minimal UI for easy usage

\- Runs locally using Flask

\- Isolated Python environment with `requirements.txt` for easy setup



---



\## 🛠 Installation (Windows)



\### 1. Clone the Repository

```powershell

git clone https://github.com/Gitoddity/note-taking-app.git

cd note-taking-app

````



\### 2. Create \& Activate Virtual Environment



```powershell

py -m venv .venv

. .\\.venv\\Scripts\\Activate.ps1

```



\### 3. Install Dependencies



```powershell

pip install -r requirements.txt

```



---



\## ▶️ Running the App



\### Set Environment Variables (Windows PowerShell)



```powershell

$env:FLASK\_APP="work\_notes\_web\_search\_paged.py"

$env:FLASK\_ENV="development"

flask run

```



\### Or in Command Prompt (cmd)



```cmd

set FLASK\_APP=work\_notes\_web\_search\_paged.py

set FLASK\_ENV=development

flask run

```



\### Access in Browser



Go to: http://127.0.0.1:5000



---



\## 📂 Project Structure



```

note-taking-app/

│

├── .venv/                  # Virtual environment (ignored in Git)

├── requirements.txt        # Project dependencies

├── work\_notes\_web\_search\_paged.py  # Main Flask application

└── README.md               # Documentation

```



---



\## 📌 Requirements



\* Python 3.8+ (tested with Python 3.12 on Windows 10/11)

\* Flask (see requirements.txt for version)



---



\## 📷 Screenshots



https://github.com/user-attachments/assets/e8bbea8f-9e61-4aaa-9a3c-417c88e96888

https://github.com/user-attachments/assets/f8156ddd-de7d-4149-83c3-855b97adcf11

https://github.com/user-attachments/assets/62fb4d14-a9ef-47b4-a5b8-8495ea805bec



---



\## 🗒️ Future Improvements



\* Add note categories/tags

\* Store notes in a database (SQLite/PostgreSQL)

\* User authentication for personal notes

\* Improved UI/UX with Bootstrap or Tailwind CSS



---



\## 📜 License



This project is open-source under the \[MIT License](LICENSE).



```



---



If you want, I can also:

\- \*\*Make you a GIF demo\*\* of the app running locally and embed it here (looks great on a portfolio).

\- \*\*Add a simple Flask HTML template\*\* so it doesn’t just output plain text but has a minimal styled web UI.  



Do you want me to do both so your repo looks more professional? That way it’s ready to impress on GitHub.

```



