import sqlite3
import time
import random
import signal
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re
import datetime

# Database Name
DB_NAME = "upwork_jobs.db"

# Set Timeout for the script (5 min max)
TIMEOUT = 300  # 5 minutes

def timeout_handler(signum, frame):
    print("⏳ Timeout reached! Exiting...")
    exit(1)

# Apply timeout
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(TIMEOUT)

# Set Up Database
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            budget TEXT,
            client_hires INTEGER,
            job_link TEXT,
            posted_time TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database setup complete.")

# Keywords to Search
SEARCH_KEYWORDS = ["scraping", "python", "ai", "api", "bot", "automation", "chrome", "selenium", "chatbot", "developer", "integration", "web", "backend", "frontend"]

# Convert posted time to datetime
def parse_posted_time(posted_time):
    match = re.search(r'(\d+)\s*(minute|hour)', posted_time)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        if unit == "minute":
            return num
        elif unit == "hour":
            return num * 60
    return 9999  # Default for older posts


# Start Selenium WebDriver
def start_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = uc.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Scrape Upwork Job Listings
def scrape_upwork_jobs():
    driver = start_driver()
    all_jobs = []

    for keyword in SEARCH_KEYWORDS:
        search_url = f"https://www.upwork.com/nx/jobs/search/?q={keyword}&sort=recency"
        print(f"🔍 Searching for: {keyword}")
        driver.get(search_url)
        time.sleep(random.randint(3, 10))

        jobs = driver.find_elements(By.CSS_SELECTOR, "article[data-test='JobTile']")
        print(f"🔍 Found {len(jobs)} job listings for '{keyword}'")

        for job in jobs:
            try:
                title_element = job.find_element(By.CSS_SELECTOR, "h2.job-tile-title a")
                title = title_element.text.strip()
                job_link = title_element.get_attribute("href")

                try:
                    posted_time_element = job.find_element(By.CSS_SELECTOR, "span[data-test='posted-on']")
                    posted_time = posted_time_element.text.strip()

                    # Convert to datetime and filter within 2 hours
                    job_post_time = parse_posted_time(posted_time)

                    # Filter Step 1: Ensure time is valid, else skip.
                    if not job_post_time:
                        print(f"⚠️ Skipping job with unknown time: {title}")
                        continue

                    # Filter Step 2: Show only jobs within the last 2 hours.
                    if (datetime.datetime.now() - job_post_time).total_seconds() > 7200:
                        print(f"🕒 Skipping (Too Old): {title} - {posted_time}")
                        continue

                except Exception as e:
                    print(f"❌ Failed to get posted time: {e}")
                    continue

                print(f"✅ Found Job: {title} | {posted_time}")
                all_jobs.append((title, "N/A", 0, job_link, posted_time))

            except Exception as e:
                print(f"❌ Error scraping job: {e}")

        time.sleep(random.randint(5, 15))

    driver.quit()

    # 🔄 Sort by Newest First (based on parsed datetime)
    all_jobs.sort(key=lambda x: parse_posted_time(x[4]), reverse=True)

    return all_jobs

# Store Jobs in SQLite Database
def store_jobs_in_db(jobs):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Clear old jobs to keep only fresh ones
    cursor.execute("DELETE FROM jobs")

    for job in jobs:
        cursor.execute('''
            INSERT INTO jobs (title, budget, client_hires, job_link, posted_time)
            VALUES (?, ?, ?, ?, ?)
        ''', job)

    conn.commit()
    conn.close()
    print(f"💾 Stored {len(jobs)} new job(s) in database.")

# Run the Scraper
if __name__ == "__main__":
    setup_database()
    jobs = scrape_upwork_jobs()
    if jobs:
        store_jobs_in_db(jobs)
    else:
        print("❌ No matching jobs found.")

    print("✅ Scraper finished.")
