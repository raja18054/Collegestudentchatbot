from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "college_chatbot_secret"

# Database Connection
def get_db():
    conn = sqlite3.connect("chatbot.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create Tables
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

    cur.execute("""
    CREATE TABLE IF NOT EXISTS notices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS assignments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        due_date TEXT
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# Home
@app.route("/")
def home():
    return render_template("index.html")

# Register Page
@app.route("/register")
def register():
    return render_template("register.html")

# Login Page
@app.route("/login")
def login():
    return render_template("login.html")

# Register Student
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
    except:
        return "Email already exists"

    conn.close()

    return redirect("/login")

# Login Student
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

# Dashboard
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    return render_template("dashboard.html", user=session["user"])

# Chatbot
@app.route("/chatbot")
def chatbot():

    if "user" not in session:
        return redirect("/login")

    return render_template("chatbot.html")

@app.route("/get_reply", methods=["POST"])
def get_reply():

    message = request.form["message"].lower()

    replies = {
        "hello": "Hello Student 👋",
        "attendance": "Your attendance is 92%.",
        "result": "Your result is First Class.",
        "fees": "Semester fees are ₹25,000.",
        "exam": "Your next exam starts on 20 September.",
        "bye": "Goodbye! Have a nice day."
    }

    reply = replies.get(message, "Sorry, I don't understand.")

    return {"reply": reply}

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
