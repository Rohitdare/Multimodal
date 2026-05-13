"""
Coordinator: Orchestrates the OCR → Memory → Reasoning → Validation pipeline.
Accepts plain Python types — no Streamlit dependency.
"""
from core.router import classify_task, get_prompt, get_schema
from core.vision import encode_image
from core.rag import build_rag_context

from agents.ocr_agent import run_ocr
from agents.memory_agent import retrieve_memory
from agents.reasoning_agent import run_reasoning
from agents.validator_agent import validate_result


def run_pipeline(
    image_path: str,
    image_bytes: bytes,
    content_type: str,
    question: str,
    max_context_items: int = 3,
) -> dict:
    """
    Run the full multimodal analysis pipeline.

    Args:
        image_path:       Absolute path to the saved image file.
        image_bytes:      Raw image bytes (for base64 encoding).
        content_type:     MIME type, e.g. "image/jpeg".
        question:         User question / instruction.
        max_context_items: How many RAG memories to inject.

    Returns:
        dict with keys: task_type, ocr, memory, final
    """
    # ── Task detection ────────────────────────────────────────────────────────
    task_type = classify_task(question)
    prompt = get_prompt(task_type)
    schema = get_schema(task_type)

    # ── OCR ───────────────────────────────────────────────────────────────────
    ocr_data = run_ocr(image_path)

    # ── Memory / RAG ──────────────────────────────────────────────────────────
    memory_data = retrieve_memory(question, task_type)
    rag_context = build_rag_context(memory_data["memory"], max_items=max_context_items)

    # ── Build LLM messages ────────────────────────────────────────────────────
    base64_image = encode_image(image_bytes)

    user_content = (
        f"User Question:\n{question}\n\n"
        f"OCR Extracted Text:\n{ocr_data['ocr_text']}\n\n"
        f"{rag_context}\n\n"
        "Please ensure your JSON output is tailored ONLY to the current image and OCR text. "
        "Use historical memory only for contextual hints."
    )

    messages = [
        {"role": "system", "content": prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_content},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{content_type};base64,{base64_image}"},
                },
            ],
        },
    ]

    # ── Reasoning ─────────────────────────────────────────────────────────────
    reasoning_output = run_reasoning(messages)

    # ── Validation ────────────────────────────────────────────────────────────
    final = validate_result(reasoning_output["raw_output"], schema)

    return {
        "task_type": task_type,
        "ocr": ocr_data,
        "memory": memory_data,
        "final": final,
    }
