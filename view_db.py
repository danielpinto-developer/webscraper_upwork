import sqlite3

# Connect to the database
conn = sqlite3.connect("upwork_jobs.db")
cursor = conn.cursor()

# Fetch all stored jobs
cursor.execute("SELECT id, title, job_link, posted_time FROM jobs ORDER BY id DESC")
rows = cursor.fetchall()

# Print the jobs in a readable format
for row in rows:
    print(f"ID: {row[0]} | Title: {row[1]} | Link: {row[2]} | Posted: {row[3]}")

conn.close()