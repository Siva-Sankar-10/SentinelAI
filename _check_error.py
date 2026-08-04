import os
import sqlite3

# Check if DB exists and its schema
print("DB exists:", os.path.exists("sentinel.db"))
if os.path.exists("sentinel.db"):
    conn = sqlite3.connect("sentinel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables:", cursor.fetchall())
    try:
        cursor.execute("PRAGMA table_info(history)")
        print("history columns:", cursor.fetchall())
    except Exception as e:
        print("ERROR reading schema:", e)
    conn.close()

# Render the dashboard template with sample data
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader("templates"))
t = env.get_template("dashboard.html")
try:
    html = t.render(
        total=100, attack=40, normal=60, accuracy=99.42, threat="MEDIUM",
        file_name="test.csv", file_type="CSV", file_size=1.5, upload_time="01-01-2026 10:00:00",
        recent_history=[("test.csv", 100, 40, 60)],
        chart_labels=["test.csv"], chart_attack=[40], chart_normal=[60]
    )
    print("Rendered OK, length:", len(html))
except Exception as e:
    import traceback
    traceback.print_exc()
