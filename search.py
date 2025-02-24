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
from datetime import timedelta

# Database name
DB_NAME = "upwork_jobs.db"

# Timeout for the script (5 min max)
TIMEOUT = 300

# Handle timeout
signal.signal(signal.SIGALRM, lambda signum, frame: exit(1))
signal.alarm(TIMEOUT)

# Set up the database
def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            budget TEXT,
            client_hires INTEGER,
            job_link TEXT,
            posted_time TEXT,
            scraped_time TEXT
        )'''
    )
    conn.commit()
    conn.close()

# Keywords to search
SEARCH_KEYWORDS = [
    "scraping", "python", "ai", "api", "bot", "automation", 
    "chrome", "selenium", "chatbot", "developer", "integration", 
    "web", "backend", "frontend"
]

# Convert posted time to minutes
def parse_posted_time(posted_time):
    match = re.search(r'(\d+)\s*(minute|hour)', posted_time)
    if match:
        num = int(match.group(1))
        unit = match.group(2)
        return num if unit == "minute" else num * 60
    return 9999

# Start Selenium driver
def start_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return uc.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Scrape Upwork job listings
def scrape_upwork_jobs():
    driver = start_driver()
    all_jobs = []

    for keyword in SEARCH_KEYWORDS:
        search_url = f"https://www.upwork.com/nx/jobs/search/?q={keyword}&sort=recency"
        driver.get(search_url)
        time.sleep(random.randint(3, 10))

        jobs = driver.find_elements(By.CSS_SELECTOR, "article[data-test='JobTile']")
        for job in jobs:
            try:
                title_element = job.find_element(By.CSS_SELECTOR, "h2.job-tile-title a")
                title = title_element.text.strip()
                job_link = title_element.get_attribute("href")

                posted_time_element = job.find_element(By.CSS_SELECTOR, "span[data-test='posted-on']")
                posted_time = posted_time_element.text.strip()

                post_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                all_jobs.append((title, "N/A", 0, job_link, posted_time, post_time))

            except Exception as e:
                print(f"❌ Error scraping job: {e}")

        time.sleep(random.randint(5, 15))

    driver.quit()
    return all_jobs

# Store jobs in the database
def store_jobs_in_db(jobs):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    two_hours_ago = datetime.datetime.now() - timedelta(hours=2)
    cursor.execute("DELETE FROM jobs WHERE scraped_time < ?", (two_hours_ago.strftime('%Y-%m-%d %H:%M:%S'),))

    for job in jobs:
        cursor.execute(
            '''INSERT INTO jobs (title, budget, client_hires, job_link, posted_time, scraped_time)
               VALUES (?, ?, ?, ?, ?, ?)''', job
        )

    conn.commit()
    conn.close()

# Main function
if __name__ == "__main__":
    setup_database()
    jobs = scrape_upwork_jobs()
    if jobs:
        store_jobs_in_db(jobs)
    else:
        print("❌ No matching jobs found.")

    print("✅ Scraper finished.")