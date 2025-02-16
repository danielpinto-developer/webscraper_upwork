import sqlite3
from flask import Flask

app = Flask(__name__)

def scrape_data():
    print("🔄 Scraper started...")  # Debugging output
    jobs = [
        ("Python Developer", "Upwork", "https://www.upwork.com/job/12345"),
        ("API Integration Expert", "Freelancer", "https://www.freelancer.com/job/54321")
    ]  # Mock jobs to test if they get saved

    conn = sqlite3.connect("jobs.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (title TEXT, company TEXT, url TEXT)''')

    for job in jobs:
        cursor.execute("INSERT INTO jobs (title, company, url) VALUES (?, ?, ?)", job)
        print(f"✅ Saved job: {job[0]}")  # Debugging output

    conn.commit()
    conn.close()
    print("✅ Scraper completed.")

@app.route("/")
def home():
    scrape_data()  # Ensure scraper runs when visiting the root URL
    return "Scraper ran successfully!"

if __name__ == "__main__":
    scrape_data()  # Force run when Flask starts
    app.run(debug=True, host="0.0.0.0", port=5000)
