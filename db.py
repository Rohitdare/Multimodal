import sqlite3
import json

DB_NAME = "agent_data.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT,
            question TEXT,
            result_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_analysis(image_name, question, result):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analyses (image_name, question, result_json)
        VALUES (?, ?, ?)
    """, (image_name, question, json.dumps(result)))

    conn.commit()
    conn.close()


def get_all_analyses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, image_name, question, result_json, created_at
        FROM analyses
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM analyses")

    conn.commit()
    conn.close()