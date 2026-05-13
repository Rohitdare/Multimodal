import json
import logging

from fastapi import APIRouter, HTTPException

from database.db import clear_history, get_all_analyses

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/history")


@router.get("/", summary="Get all past analyses")
def get_history():
    """Return all analyses ordered by most recent first."""
    rows = get_all_analyses()
    return [
        {
            "id": r[0],
            "image_name": r[1],
            "question": r[2],
            "result": _safe_json(r[3]),
            "created_at": r[4],
        }
        for r in rows
    ]


@router.delete("/", summary="Clear all analysis history")
def delete_history():
    """Delete all stored analysis records."""
    try:
        clear_history()
    except Exception as exc:
        logger.exception("Failed to clear history")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"message": "History cleared."}


def _safe_json(raw: str):
    try:
        return json.loads(raw)
    except Exception:
        return raw
