import sqlite3
import time
import random
import threading
from flask import Flask, render_template_string
import os

DB_NAME = "upwork_jobs.db"
SEARCH_KEYWORDS = ["scraping", "python", "ai", "web", "api", "bot"]  # Add more if needed

app = Flask(__name__)

# HTML Template for displaying jobs
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upwork Job Listings</title>
    <meta http-equiv="refresh" content="600"> <!-- Refresh every 10 minutes -->
    <style>
        body { font-family: Arial, sans-serif; background: #f4f4f4; margin: 20px; }
        .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #0073aa; color: white; }
        a { text-decoration: none; color: #0073aa; font-weight: bold; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upwork Job Listings</h1>
        <table>
            <tr>
                <th>Title</th>
                <th>Budget</th>
                <th>Hires</th>
                <th>Posted</th>
                <th>Link</th>
            </tr>
            {% for job in jobs %}
            <tr>
                <td>{{ job[0] }}</td>
                <td>{{ job[1] }}</td>
                <td>{{ job[2] }}</td>
                <td>{{ job[4] }}</td>
                <td><a href="{{ job[3] }}" target="_blank">View</a></td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

# Load jobs from the database
def load_jobs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT title, budget, client_hires, job_link, posted_time FROM jobs ORDER BY id DESC")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

# Flask Route: Display Jobs
@app.route("/")
def home():
    jobs = load_jobs()
    return render_template_string(HTML_TEMPLATE, jobs=jobs)

# Run Flask Server
def run_server():
    app.run(debug=True, port=5000, use_reloader=False)

# Scrape Jobs Automatically (Runs in Background)
def run_scraper():
    while True:
        for keyword in SEARCH_KEYWORDS:
            os.system(f"python3 search.py {keyword}")  # Runs scraper for each keyword
            time.sleep(random.randint(5, 15))  # Random delay to avoid detection
        
        print("✅ Waiting 10 minutes before next scrape cycle...")
        time.sleep(600)  # Wait 10 minutes before restarting

# Start Web Server & Scraper
if __name__ == "__main__":
    threading.Thread(target=run_scraper, daemon=True).start()  # Start scraper in background
    run_server()  # Start the web server
