import json
import logging

from fastapi import APIRouter, HTTPException

from database.db import clear_history, get_all_analyses_extended
from core.vector_store import clear_embeddings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history")


@router.get("/", summary="Get all past analyses")
def get_history():
    """Return all analyses ordered by most recent first."""
    rows = get_all_analyses_extended()
    return [
        {
            "id": r[0],
            "image_name": r[1],
            "question": r[2],
            "result": _safe_json(r[3]),
            "task_type": r[4],
            "ocr_text": r[5],
            "created_at": r[6],
        }
        for r in rows
    ]


@router.delete("/", summary="Clear all analysis history")
def delete_history():
    """Delete all stored analysis records and vector store memory."""
    try:
        clear_history()
        clear_embeddings()
    except Exception as exc:
        logger.exception("Failed to clear history")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"message": "History cleared."}


def _safe_json(raw: str):
    try:
        return json.loads(raw)
    except Exception:
        return raw
