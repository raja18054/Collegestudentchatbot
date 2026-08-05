from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "college_chatbot_secret"

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
    except:
        conn.close()
        return "Email already exists."

    conn.close()

    return redirect("/login")


# ---------------- LOGIN ---------------- #

@app.route("/login")
def login():
    return render_template("login.html")


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

    message = request.form["message"].lower()

    replies = {
        "hello": "Hello Student 👋",
        "attendance": "Your attendance is 92%.",
        "result": "Your result is First Class.",
        "fees": "Semester fees are ₹25,000.",
        "exam": "Your next exam starts on 20 September.",
        "assignment": "You have 4 pending assignments.",
        "notice": "Check the Notice Board for the latest updates.",
        "bye": "Goodbye! Have a nice day."
    }

    reply = replies.get(message, "Sorry, I don't understand your question.")

    return {"reply": reply}


# ---------------- ATTENDANCE ---------------- #

@app.route("/attendance")
def attendance():

    if "user" not in session:
        return redirect("/login")

    return render_template("attendance.html")


# ---------------- RESULTS ---------------- #

@app.route("/results")
def results():

    if "user" not in session:
        return redirect("/login")

    return render_template("results.html")


# ---------------- ASSIGNMENTS ---------------- #

@app.route("/assignments")
def assignments():

    if "user" not in session:
        return redirect("/login")

    return render_template("assignments.html")


# ---------------- NOTICES ---------------- #

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
    app.run(debug=True)
