import sqlite3
import json
from core.config import DB_PATH


def init_db() -> None:
    """Create the analyses table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                image_name  TEXT,
                question    TEXT,
                result_json TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_analysis(image_name: str, question: str, result: dict) -> None:
    """Persist one analysis record."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO analyses (image_name, question, result_json) VALUES (?, ?, ?)",
            (image_name, question, json.dumps(result)),
        )
        conn.commit()


def get_all_analyses() -> list[tuple]:
    """Return all analyses, newest first."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT id, image_name, question, result_json, created_at "
            "FROM analyses ORDER BY created_at DESC"
        )
        return cursor.fetchall()


def clear_history() -> None:
    """Delete all analysis records."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM analyses")
        conn.commit()