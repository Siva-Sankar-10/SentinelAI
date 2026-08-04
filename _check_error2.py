import traceback

import app as flask_app

client = flask_app.app.test_client()

try:
    resp = client.get("/dashboard")
    print("Status:", resp.status_code)
    print("Final /dashboard response length:", len(resp.data))
except Exception:
    print("=" * 60)
    print("EXCEPTION ON /dashboard:")
    traceback.print_exc()
    print("=" * 60)

# Also test the insert statement that /predict uses
import sqlite3
conn = sqlite3.connect("sentinel.db")
cursor = conn.cursor()
try:
    cursor.execute("""
        INSERT INTO history(file_name, total, attack, normal, threat, upload_time)
        VALUES(?,?,?,?,?,?)
    """, ("x.csv", 10, 5, 5, "LOW", "now"))
    conn.commit()
    print("INSERT OK")
except Exception as e:
    print("INSERT ERROR:", e)
finally:
    conn.close()

# What columns does app.py's init_db expect vs database.py?
print("=" * 60)
print("app.py init_db columns    : id, file_name, total, attack, normal, threat, upload_time")
print("database.py create_database: id, filename, total, attack, normal, date")
print("ACTUAL TABLE SCHEMA:")
conn = sqlite3.connect("sentinel.db")
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(history)")
for col in cursor.fetchall():
    print("  ", col[1])
conn.close()

