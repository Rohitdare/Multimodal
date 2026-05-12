from pydantic import BaseModel
from typing import List

class ProductAnalysis(BaseModel):
    buy: bool
    score: int
    best_for: str
    pros: List[str]
    cons: List[str]
    verdict: str

class ReceiptAnalysis(BaseModel):
    store: str
    total_spent: float
    largest_category: str
    expensive_items: List[str]
    verdict: str

class NotesAnalysis(BaseModel):
    topic: str
    key_points: List[str]
    action_items: List[str]
    open_questions: List[str]

class DocumentAnalysis(BaseModel):
    document_type: str
    subject: str
    entities: List[str]
    summary: str

class ScreenshotAnalysis(BaseModel):
    application: str
    ui_elements: List[str]
    text_content: str
    context: str

