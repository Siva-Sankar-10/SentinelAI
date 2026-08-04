import sqlite3


def create_database():

    conn = sqlite3.connect("sentinel.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            file_name TEXT NOT NULL,

            total INTEGER NOT NULL DEFAULT 0,

            attack INTEGER NOT NULL DEFAULT 0,

            normal INTEGER NOT NULL DEFAULT 0,

            threat TEXT NOT NULL DEFAULT 'LOW',

            upload_time TEXT NOT NULL

        )
    """)

    legacy_columns = [
        row[1]
        for row in cursor.execute("PRAGMA table_info(history)").fetchall()
    ]

    if legacy_columns and "file_name" not in legacy_columns:

        cursor.execute("ALTER TABLE history RENAME TO history_legacy")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                file_name TEXT NOT NULL,

                total INTEGER NOT NULL DEFAULT 0,

                attack INTEGER NOT NULL DEFAULT 0,

                normal INTEGER NOT NULL DEFAULT 0,

                threat TEXT NOT NULL DEFAULT 'LOW',

                upload_time TEXT NOT NULL

            )
        """)

        if "filename" in legacy_columns and "date" in legacy_columns:
            cursor.execute("""
                INSERT INTO history(file_name, total, attack, normal, threat, upload_time)
                SELECT filename, total, attack, normal, 'LOW', date
                FROM history_legacy
            """)

        cursor.execute("DROP TABLE history_legacy")

    cursor.execute("""
        DELETE FROM history
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM history
            GROUP BY file_name, total, attack, normal, threat, upload_time
        )
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_history_unique_result
        ON history(file_name, total, attack, normal, threat, upload_time)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_upload_time
        ON history(upload_time)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_history_file_name
        ON history(file_name)
    """)

    conn.commit()
    conn.close()


create_database()