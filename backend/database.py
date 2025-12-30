import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bugwise.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_tables(conn)
    return conn

def ensure_tables(conn):
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
