import sqlite3
import json
import logging
from core.config import DB_PATH

logger = logging.getLogger(__name__)


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
    
    # Run historical validation error migration
    migrate_old_validation_errors()


def migrate_old_validation_errors() -> None:
    """Migrate historical database records that saved validation errors so they contain actual results instead."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT id, result_json FROM analyses")
            rows = cursor.fetchall()
            updated_count = 0
            for row_id, result_str in rows:
                try:
                    data = json.loads(result_str)
                    if isinstance(data, dict) and "error" in data and "raw" in data:
                        raw_data = data["raw"]
                        # If raw_data is a string, check if we can parse it as json
                        if isinstance(raw_data, str):
                            try:
                                raw_data = json.loads(raw_data)
                            except Exception:
                                pass
                        # If we got a dict or list for raw_data, update the database
                        if isinstance(raw_data, (dict, list)):
                            conn.execute(
                                "UPDATE analyses SET result_json = ? WHERE id = ?",
                                (json.dumps(raw_data), row_id)
                            )
                            updated_count += 1
                except Exception as e:
                    logger.warning("Failed to migrate row %s: %s", row_id, e)
            if updated_count > 0:
                conn.commit()
                logger.info("Successfully migrated %s database records from old validation format.", updated_count)
    except Exception as exc:
        logger.warning("Database migration failed: %s", exc, exc_info=True)


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