import sqlite3
from flask import Flask, render_template

app = Flask(__name__)
DB_NAME = "upwork_jobs.db"

# Fetch jobs from SQLite
def get_jobs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    two_hours_ago = (datetime.datetime.utcnow() - datetime.timedelta(hours=2)).isoformat()
    cursor.execute("SELECT title, job_link, posted_time FROM jobs ORDER BY posted_time DESC")  # Now shows the latest first
    jobs = cursor.fetchall()
    conn.close()
    return jobs

# Home route to display jobs
@app.route("/")
def home():
    jobs = get_jobs()
    return render_template("index.html", jobs=jobs)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
