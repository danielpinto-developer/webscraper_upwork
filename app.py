from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

DB_NAME = "upwork_jobs.db"

def get_jobs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT title, job_link, posted_time FROM jobs ORDER BY id DESC")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

@app.route("/")
def home():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, job_link, posted_time
        FROM jobs
        WHERE posted_time >= datetime('now', '-2 hours')
        ORDER BY posted_time DESC
    """)
    jobs = cursor.fetchall()
    conn.close()

    return render_template("index.html", jobs=jobs)

