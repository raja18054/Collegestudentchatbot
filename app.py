import os
import sqlite3
from flask import Flask, render_template, request, redirect, session
from google import genai
from google.genai.errors import APIError

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "college_chatbot_secret")

# ---------------- GEMINI SETUP ---------------- #

def get_gemini_client():
    """Initializes the Gemini client using GEMINI_API_KEY from environment variables."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

# ---------------- DATABASE ---------------- #

def get_db():
    conn = sqlite3.connect("chatbot.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ---------------- #

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register_student", methods=["POST"])
def register_student():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO students(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )
        conn.commit()
    except Exception:
        conn.close()
        return "Email already exists."

    conn.close()
    return redirect("/login")

# ---------------- LOGIN & AUTH ---------------- #

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/forgot_password")
def forgot_password():
    return render_template("forgot_password.html")

@app.route("/login_student", methods=["POST"])
def login_student():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM students WHERE email=? AND password=?",
        (email, password)
    )

    user = cur.fetchone()
    conn.close()

    if user:
        session["user"] = user["name"]
        return redirect("/dashboard")

    return "Invalid Email or Password"

@app.route("/reset_password", methods=["POST"])
def reset_password():
    email = request.form["email"]
    new_password = request.form["password"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM students WHERE email=?",
        (email,)
    )

    user = cur.fetchone()

    if user:
        cur.execute(
            "UPDATE students SET password=? WHERE email=?",
            (new_password, email)
        )
        conn.commit()
        conn.close()
        return redirect("/login")

    conn.close()
    return "Email not found."

# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html", user=session["user"])

# ---------------- CHATBOT ---------------- #

@app.route("/chatbot")
def chatbot():
    if "user" not in session:
        return redirect("/login")

    return render_template("chatbot.html")

@app.route("/get_reply", methods=["POST"])
def get_reply():
    if "user" not in session:
        return {"reply": "Please login first."}

    message = request.form.get("message", "")

    if not message.strip():
        return {"reply": "Please enter a valid message."}

    client = get_gemini_client()
    if not client:
        return {"reply": "Error: GEMINI_API_KEY environment variable is missing on Render."}

    prompt = f"""
You are a helpful College Student Assistant.

Answer only questions related to:
- College
- Attendance
- Results
- Assignments
- Notices
- Exams
- Programming
- Python
- Career Guidance

Student Question:
{message}
"""

    try:
        # Changed to gemini-1.5-flash
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )
        
        if response and response.text:
            return {"reply": response.text}
        else:
            return {"reply": "Sorry, could not generate a response."}

    except APIError as e:
        print(f"Gemini API Error: {e}")
        return {"reply": f"Gemini API Error: {e.message}"}
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {"reply": f"Sorry, AI is currently unavailable. Error: {str(e)}"}

# ---------------- ATTENDANCE / RESULTS / ASSIGNMENTS / NOTICES ---------------- #

@app.route("/attendance")
def attendance():
    if "user" not in session:
        return redirect("/login")
    return render_template("attendance.html")

@app.route("/results")
def results():
    if "user" not in session:
        return redirect("/login")
    return render_template("results.html")

@app.route("/assignments")
def assignments():
    if "user" not in session:
        return redirect("/login")
    return render_template("assignments.html")

@app.route("/notices")
def notices():
    if "user" not in session:
        return redirect("/login")
    return render_template("notices.html")

# ---------------- VIEW STUDENTS (TESTING ONLY) ---------------- #

@app.route("/students")
def students():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    conn.close()

    return str([dict(row) for row in data])

# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
