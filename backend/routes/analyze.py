import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from agents.coordinator import run_pipeline
from core.vector_store import store_embedding
from database.db import save_analysis
from services.storage_service import save_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze")


@router.post("/", summary="Analyse an uploaded image")
async def analyze_image(
    file: UploadFile = File(..., description="Image file (jpg/png/webp)"),
    question: str = Form(..., description="Question or instruction about the image"),
    max_context_items: int = Form(3, description="Number of RAG memory items to inject"),
):
    """
    Run the full multimodal pipeline:
    OCR → RAG memory retrieval → LLM reasoning → JSON validation.
    """
    allowed_types = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {allowed_types}",
        )

    image_bytes = await file.read()

    try:
        image_path = save_file(file.filename, image_bytes)

        result = run_pipeline(
            image_path=image_path,
            image_bytes=image_bytes,
            content_type=file.content_type,
            question=question,
            max_context_items=max_context_items,
        )
    except Exception as exc:
        logger.exception("Pipeline failed for file '%s'", file.filename)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Persist to SQLite + vector store (best-effort)
    final = result["final"]
    if "result" in final:
        try:
            analysis_id = save_analysis(
                file.filename,
                question,
                final["result"],
                task_type=result["task_type"],
                ocr_text=result["ocr"]["ocr_text"]
            )
            store_embedding(
                record_id=str(analysis_id),
                question=question,
                result_text=str(final["result"]),
                task_type=result["task_type"],
            )
        except Exception:
            logger.warning("Failed to persist analysis — non-fatal.", exc_info=True)

    return {
        "task_type": result["task_type"],
        "ocr_text": result["ocr"]["ocr_text"],
        "output": final,
    }
