from flask import Flask, request, redirect, render_template
import sqlite3
import string
import random
app = Flask(__name__)
# Database connection
def get_db():
    return sqlite3.connect("urls.db")
# Create table
def create_table():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE,
            long_url TEXT
        )
    """)
    db.commit()
    db.close()
create_table()
# Generate short code
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
# Home page
@app.route("/", methods=["GET", "POST"])
def index():
    short_url = None
    if request.method == "POST":
        long_url = request.form["long_url"]
        short_code = generate_short_code()
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO urls (short_code, long_url) VALUES (?, ?)",
            (short_code, long_url)
        )
        db.commit()
        db.close()
        short_url = request.host_url + short_code

    return render_template("index.html", short_url=short_url)
# Redirect route
@app.route("/<short_code>")
def redirect_url(short_code):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT long_url FROM urls WHERE short_code = ?",
        (short_code,)
    )
    result = cursor.fetchone()
    db.close()

    if result:
        return redirect(result[0])
    else:
        return "URL not found", 404
if __name__ == "__main__":
    app.run(debug=True)