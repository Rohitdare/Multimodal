from pydantic import BaseModel, field_validator
from typing import List, Optional, Any


class Entity(BaseModel):
    name: str
    type: str
    confidence: Optional[float] = None


def normalize_list_strings(v: Any) -> List[str]:
    """Helper to convert strings or lists of mixed types to a clean list of strings."""
    if v is None:
        return []
    if isinstance(v, str):
        if v.lower().strip() in ("", "none", "n/a", "none found", "nothing"):
            return []
        # If it's a comma-separated or newline-separated list, split it
        if "," in v:
            return [x.strip() for x in v.split(",") if x.strip()]
        if "\n" in v:
            return [x.strip() for x in v.split("\n") if x.strip()]
        return [v.strip()]
    if not isinstance(v, list):
        return [str(v)]
    return [str(item).strip() for item in v if item is not None]


class ProductAnalysis(BaseModel):
    buy: bool
    score: int
    best_for: str
    pros: List[str]
    cons: List[str]
    verdict: str

    @field_validator("pros", "cons", mode="before")
    @classmethod
    def validate_lists(cls, v: Any) -> List[str]:
        return normalize_list_strings(v)


class ReceiptAnalysis(BaseModel):
    store: str
    total_spent: float
    largest_category: str
    expensive_items: List[str]
    verdict: str

    @field_validator("expensive_items", mode="before")
    @classmethod
    def validate_lists(cls, v: Any) -> List[str]:
        return normalize_list_strings(v)


class NotesAnalysis(BaseModel):
    topic: str
    key_points: List[str]
    action_items: List[str]
    open_questions: List[str]

    @field_validator("key_points", "action_items", "open_questions", mode="before")
    @classmethod
    def validate_lists(cls, v: Any) -> List[str]:
        return normalize_list_strings(v)


class DocumentAnalysis(BaseModel):
    document_type: str
    subject: str
    entities: List[Entity]
    summary: str

    @field_validator("entities", mode="before")
    @classmethod
    def normalize_entities(cls, v: Any) -> List[dict]:
        if v is None:
            return []
        if isinstance(v, str):
            if v.lower().strip() in ("", "none", "n/a", "no entities", "none found"):
                return []
            names = [x.strip() for x in v.split(",") if x.strip()]
            return [{"name": name, "type": "unknown"} for name in names]
        
        if isinstance(v, dict):
            v = [v]
        elif not isinstance(v, list):
            v = [v]
        
        normalized = []
        for item in v:
            if isinstance(item, str):
                normalized.append({"name": item, "type": "unknown"})
            elif isinstance(item, dict):
                name = item.get("name") or item.get("entity") or ""
                if not name:
                    # Try to find any other string field
                    for k, val in item.items():
                        if k != "type" and isinstance(val, str):
                            name = val
                            break
                entity_type = item.get("type") or "unknown"
                confidence = item.get("confidence")
                try:
                    confidence = float(confidence) if confidence is not None else None
                except (ValueError, TypeError):
                    confidence = None
                normalized.append({
                    "name": str(name),
                    "type": str(entity_type),
                    "confidence": confidence
                })
            else:
                normalized.append({"name": str(item), "type": "unknown"})
        return normalized


class ScreenshotAnalysis(BaseModel):
    application: str
    ui_elements: List[str]
    text_content: str
    context: str

    @field_validator("ui_elements", mode="before")
    @classmethod
    def validate_lists(cls, v: Any) -> List[str]:
        return normalize_list_strings(v)

