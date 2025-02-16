import sqlite3
import time
import random
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

DB_NAME = "upwork_jobs.db"

# Get search keyword from command line argument
if len(sys.argv) < 2:
    print("❌ No keyword provided!")
    sys.exit(1)
keyword = sys.argv[1]

# Start Chrome
def start_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Scrape Jobs
def scrape_upwork_jobs():
    driver = start_driver()
    search_url = f"https://www.upwork.com/nx/jobs/search/?q={keyword}&sort=recency"
    
    print(f"🔍 Searching for: {keyword}")
    driver.get(search_url)
    time.sleep(random.randint(3, 8))  # Wait for page to load

    jobs = driver.find_elements(By.CSS_SELECTOR, "article[data-test='JobTile']")
    print(f"🔍 Found {len(jobs)} job listings for '{keyword}'")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for job in jobs:
        try:
            title_element = job.find_element(By.CSS_SELECTOR, "h2.job-tile-title a")
            title = title_element.text.strip()
            job_link = title_element.get_attribute("href")

            try:
                budget_element = job.find_element(By.CSS_SELECTOR, "span[data-test='budget']")
                budget = budget_element.text.strip()
            except:
                budget = "N/A"

            try:
                client_hires_element = job.find_element(By.CSS_SELECTOR, "span[data-test='client-hires']")
                client_hires = int(client_hires_element.text.strip().split()[0])
            except:
                client_hires = 0  # Accepts no hires

            try:
                posted_time_element = job.find_element(By.CSS_SELECTOR, "small[data-test='job-pubilshed-date']")
                posted_time = posted_time_element.text.strip()
            except:
                posted_time = "Unknown"

            print(f"✅ Found Job: {title} | {posted_time} | Hires: {client_hires}")

            cursor.execute('''
                INSERT INTO jobs (title, budget, client_hires, job_link, posted_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, budget, client_hires, job_link, posted_time))

        except Exception as e:
            print(f"❌ Error scraping job: {e}")

    conn.commit()
    conn.close()
    driver.quit()

# Run the scraper
scrape_upwork_jobs()
