import sqlite3
from flask import Flask, render_template

app = Flask(__name__)

DB_NAME = "upwork_jobs.db"

# Function to fetch recent jobs from the database
def get_recent_jobs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get current time and subtract 2 hours
    two_hours_ago = datetime.datetime.now() - datetime.timedelta(hours=2)

    # Query to fetch jobs within the last 2 hours
    cursor.execute("""
        SELECT title, job_link, posted_time 
        FROM jobs 
        WHERE posted_time LIKE '%minute%' 
        OR (posted_time LIKE '%hour%' AND CAST(SUBSTR(posted_time, 1, INSTR(posted_time, ' ') - 1) AS INTEGER) <= 2)
        ORDER BY id DESC
    """)

    jobs = cursor.fetchall()
    conn.close()
    return jobs


# Flask route to display the jobs
@app.route("/")
def home():
    jobs = get_recent_jobs()
    return render_template("index.html", jobs=jobs)

# Main entry point to run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)