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
    jobs = get_jobs()
    return render_template("index.html", jobs=jobs)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
