\# Note-Taking App 📝



A simple \*\*Flask\*\*-based web app to create, view, and manage notes — built as part of my AI and Python learning journey.  

I wanted a simple way to save my observation from work and life in  notes , i know there are so many apps available for it like keep notes, notion , evernote. i just wanted something that is not on the cloud or owned by any companies so i whipped this up relatively quickly using ChatGPT

My  python fluentcy falls somewhere between an absolute beginner and an intermediate user depending on the problems that needs to be solved . I usually have an idea of the solution so using AI and my own understanding of python i created this app , hope you find it as usefull as i did.


---



\## 🚀 Features

\- Add, view, and delete notes

\- Search for notes using text or date rate

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



![Screenshot 1](https://github.com/user-attachments/assets/e8bbea8f-9e61-4aaa-9a3c-417c88e96888)


![Screenshot 2](https://github.com/user-attachments/assets/f8156ddd-de7d-4149-83c3-855b97adcf11)

![Screesnhot_3](https://github.com/user-attachments/assets/62fb4d14-a9ef-47b4-a5b8-8495ea805bec)



---



\## 🗒️ Future Improvements



\* Add note categories/tags

\* Store notes in a database (SQLite/PostgreSQL)

\* User authentication for personal notes

\* Improved UI/UX with Bootstrap or Tailwind CSS



---



\## 📜 License



This project is open-source under the \[MIT License](LICENSE).


