import sqlite3

# Connect to the database
conn = sqlite3.connect("upwork_jobs.db")
cursor = conn.cursor()

# Fetch all stored jobs
cursor.execute("SELECT * FROM jobs")
rows = cursor.fetchall()

# Print the jobs in a readable format
for row in rows:
    print(f"ID: {row[0]} | Title: {row[1]} | Budget: {row[2]} | Client Hires: {row[3]} | Link: {row[4]} | Posted: {row[5]}")

conn.close()