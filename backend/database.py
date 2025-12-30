import sqlite3
from datetime import datetime

DB_NAME = "bugwise.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bugs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bug_text TEXT NOT NULL,
            language TEXT,
            context TEXT,
            explanation TEXT,
            root_cause TEXT,
            fix_steps TEXT,
            example_code TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
