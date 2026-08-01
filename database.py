import sqlite3

def create_database():

    conn = sqlite3.connect("sentinel.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT,

            total INTEGER,

            attack INTEGER,

            normal INTEGER,

            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)

    conn.commit()
    conn.close()


create_database()