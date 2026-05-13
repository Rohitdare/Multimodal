from pathlib import Path
from core.config import UPLOAD_DIR


def ensure_upload_dir() -> None:
    """Create the uploads directory if it doesn't exist."""
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def save_file(filename: str, data: bytes) -> str:
    """
    Save raw bytes to the uploads directory.

    Returns the absolute path as a string.
    """
    ensure_upload_dir()
    filepath = Path(UPLOAD_DIR) / filename
    filepath.write_bytes(data)
    return str(filepath)
