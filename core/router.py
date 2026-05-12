from core.prompts import (
    GENERAL_PROMPT,
    RECEIPT_PROMPT,
    PRODUCT_PROMPT,
    NOTES_PROMPT,
    DOCUMENTS_PROMPT,
    SCREENSHOTS_PROMPT
)

from models.schemas import (
    ProductAnalysis,
    ReceiptAnalysis,
    NotesAnalysis,
    DocumentAnalysis,
    ScreenshotAnalysis
)


def classify_task(question: str):

    q = question.lower()

    if (
        "receipt" in q
        or "spending" in q
        or "expense" in q
        or "bill" in q
    ):
        return "receipt"

    if (
        "buy" in q
        or "product" in q
        or "worth" in q
        or "review" in q
    ):
        return "product"

    if (
        "summary" in q
        or "summarize" in q
        or "meeting" in q
        or "notes" in q
    ):
        return "notes"

    if (
        "document" in q
        or "paper" in q
        or "letter" in q
        or "form" in q
    ):
        return "documents"

    if (
        "screenshot" in q
        or "app" in q
        or "ui" in q
        or "interface" in q
    ):
        return "screenshots"

    return "general"


def get_prompt(task_type):

    prompt_map = {
        "receipt": RECEIPT_PROMPT,
        "product": PRODUCT_PROMPT,
        "notes": NOTES_PROMPT,
        "documents": DOCUMENTS_PROMPT,
        "screenshots": SCREENSHOTS_PROMPT,
        "general": GENERAL_PROMPT
    }

    return prompt_map.get(task_type, GENERAL_PROMPT)


def get_schema(task_type):

    schema_map = {
        "receipt": ReceiptAnalysis,
        "product": ProductAnalysis,
        "notes": NotesAnalysis,
        "documents": DocumentAnalysis,
        "screenshots": ScreenshotAnalysis
    }

    return schema_map.get(task_type)