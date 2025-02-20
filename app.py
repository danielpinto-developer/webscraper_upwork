import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

DB_NAME = "upwork_jobs.db"

def get_recent_jobs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, job_link, posted_time 
        FROM jobs 
        WHERE posted_time LIKE '%hour%' OR posted_time LIKE '%minute%'
        ORDER BY CASE
            WHEN posted_time LIKE '%minute%' THEN CAST(SUBSTR(posted_time, 1, INSTR(posted_time, ' ') - 1) AS INTEGER)
            WHEN posted_time LIKE '%hour%' THEN CAST(SUBSTR(posted_time, 1, INSTR(posted_time, ' ') - 1) AS INTEGER) * 60
            ELSE 9999
        END ASC
    """)
    jobs = cursor.fetchall()
    conn.close()
    return jobs

@app.route("/")
def home():
    jobs = get_recent_jobs()
    return render_template("index.html", jobs=jobs)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
