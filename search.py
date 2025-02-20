import sqlite3
import time
import random
import signal
import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import re

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
SEARCH_KEYWORDS = ["scraping", "python", "ai", "api", "bot", "automation", "data", "developer", "flask", "django", "bubble", "chatbot", "web", "app", "software"]

# Convert posted time to datetime
def parse_posted_time(posted_time):
    match = re.search(r"(\d+)\s*(minute|hour)", posted_time)
    if match:
        value, unit = int(match.group(1)), match.group(2)
        if unit == "minute":
            return datetime.datetime.now() - datetime.timedelta(minutes=value)
        elif unit == "hour":
            return datetime.datetime.now() - datetime.timedelta(hours=value)
    return None

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
        time.sleep(random.randint(3, 10))  # Wait for page to load

        jobs = driver.find_elements(By.CSS_SELECTOR, "article[data-test='JobTile']")
        print(f"🔍 Found {len(jobs)} job listings for '{keyword}'")

        for job in jobs:
            try:
                title_element = job.find_element(By.CSS_SELECTOR, "h2.job-tile-title a")
                title = title_element.text.strip()
                job_link = title_element.get_attribute("href")

                try:
                    # Updated selector for Upwork's new format
                    posted_time_element = job.find_element(By.CSS_SELECTOR, "span[data-test='posted-on']")
                    posted_time = posted_time_element.text.strip()
                except:
                    posted_time = "Unknown"

                # Convert posted time to datetime & filter only jobs in the last 2 hours
                actual_posted_time = parse_posted_time(posted_time)
                if not actual_posted_time:
                    print(f"🕒 Skipping (Invalid Time): {title} - {posted_time}")
                    continue

                two_hours_ago = datetime.datetime.now() - datetime.timedelta(hours=2)

                if actual_posted_time < two_hours_ago:
                    print(f"🕒 Skipping (Too Old): {title} - {posted_time}")
                    continue

                print(f"✅ Found Job: {title} | {actual_posted_time}")

                all_jobs.append((title, "N/A", 0, job_link, actual_posted_time.isoformat()))

            except Exception as e:
                print(f"❌ Error scraping job: {e}")

        time.sleep(random.randint(5, 15))  # Human-like delay

    driver.quit()

    # Sort jobs from most recent to oldest
    all_jobs.sort(key=lambda x: x[4], reverse=True)
    return all_jobs

# Store Jobs in SQLite Database
def store_jobs_in_db(jobs):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

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
