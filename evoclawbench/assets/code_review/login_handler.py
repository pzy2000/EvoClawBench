from flask import Flask, request, session, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = "hardcoded-secret-key-12345"

DB_PATH = "/var/data/users.db"


def get_db():
    return sqlite3.connect(DB_PATH)


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    db = get_db()
    cursor = db.cursor()
    query = "SELECT id, username, password FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    user = cursor.fetchone()

    if user:
        session["user_id"] = user[0]
        session["username"] = user[1]
        return redirect("/dashboard")
    else:
        return "Invalid credentials", 401


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    email = request.form.get("email")

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, email) VALUES ('" + username + "', '" + password + "', '" + email + "')"
    )
    db.commit()
    return "User registered", 201


@app.route("/reset-password", methods=["POST"])
def reset_password():
    email = request.form.get("email")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM users WHERE email = '" + email + "'")
    user = cursor.fetchone()
    if user:
        new_password = "temp123"
        cursor.execute("UPDATE users SET password = '" + new_password + "' WHERE id = " + str(user[0]))
        db.commit()
    return "If that email exists, a reset has been initiated."
