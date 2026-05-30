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
                task_type   TEXT,
                ocr_text    TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Dynamic migration to add task_type and ocr_text columns if they do not exist
        cursor = conn.execute("PRAGMA table_info(analyses)")
        columns = [row[1] for row in cursor.fetchall()]
        if "task_type" not in columns:
            conn.execute("ALTER TABLE analyses ADD COLUMN task_type TEXT")
        if "ocr_text" not in columns:
            conn.execute("ALTER TABLE analyses ADD COLUMN ocr_text TEXT")
        conn.commit()


def save_analysis(image_name: str, question: str, result: dict, task_type: str = "", ocr_text: str = "") -> int:
    """Persist one analysis record."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO analyses (image_name, question, result_json, task_type, ocr_text) VALUES (?, ?, ?, ?, ?)",
            (image_name, question, json.dumps(result), task_type, ocr_text),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_analyses() -> list[tuple]:
    """Return all analyses, newest first."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT id, image_name, question, result_json, created_at "
            "FROM analyses ORDER BY created_at DESC"
        )
        return cursor.fetchall()


def get_all_analyses_extended() -> list[tuple]:
    """Return all analyses with extra columns (task_type, ocr_text), newest first."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "SELECT id, image_name, question, result_json, task_type, ocr_text, created_at "
            "FROM analyses ORDER BY created_at DESC"
        )
        return cursor.fetchall()


def clear_history() -> None:
    """Delete all analysis records."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM analyses")
        conn.commit()