import re
from pydantic import BaseModel, field_validator
from typing import List, Optional, Any


class Entity(BaseModel):
    name: str = ""
    type: str = "unknown"
    confidence: Optional[float] = None


def normalize_bool(v: Any) -> bool:
    """Helper to convert various types to boolean, handling string representations."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return bool(v)
    if isinstance(v, str):
        val = v.lower().strip()
        if val in ("true", "yes", "1", "y", "t", "active", "buy", "recommend"):
            return True
        if val in ("false", "no", "0", "n", "f", "inactive", "avoid", "don't buy"):
            return False
    return False


def normalize_int(v: Any) -> int:
    """Helper to convert string/float to int, extracting digits if necessary."""
    if isinstance(v, int):
        return v
    if isinstance(v, float):
        return int(v)
    if isinstance(v, str):
        match = re.search(r'\d+', v)
        if match:
            return int(match.group(0))
    return 0


def normalize_float(v: Any) -> float:
    """Helper to convert currency string or formatted string to float."""
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        cleaned = re.sub(r'[^\d.,-]', '', v)
        if ',' in cleaned and '.' in cleaned:
            cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            if cleaned.count(',') == 1:
                cleaned = cleaned.replace(',', '.')
            else:
                cleaned = cleaned.replace(',', '')
        try:
            return float(cleaned)
        except ValueError:
            pass
    return 0.0


def normalize_list_strings(v: Any) -> List[str]:
    """Helper to convert strings or lists of mixed types to a clean list of strings."""
    if v is None:
        return []
    if isinstance(v, str):
        if v.lower().strip() in ("", "none", "n/a", "none found", "nothing"):
            return []
        if "," in v:
            return [x.strip() for x in v.split(",") if x.strip()]
        if "\n" in v:
            return [x.strip() for x in v.split("\n") if x.strip()]
        return [v.strip()]
    if not isinstance(v, list):
        return [str(v)]
    result = []
    for item in v:
        if item is None:
            continue
        if isinstance(item, dict):
            # If the LLM returned a dict instead of a string, extract a meaningful value
            result.append(item.get("name", "") or item.get("value", "") or str(item))
        else:
            result.append(str(item).strip())
    return result


def normalize_entities(v: Any) -> List[dict]:
    """Normalize any shape of entities data into a list of {name, type, confidence} dicts."""
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
        if item is None:
            continue
        if isinstance(item, str):
            normalized.append({"name": item, "type": "unknown"})
        elif isinstance(item, Entity):
            normalized.append(item.model_dump())
        elif isinstance(item, dict):
            name = item.get("name") or item.get("entity") or item.get("value") or ""
            if not name:
                for k, val in item.items():
                    if k not in ("type", "confidence") and isinstance(val, str):
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
                "confidence": confidence,
            })
        else:
            normalized.append({"name": str(item), "type": "unknown"})
    return normalized


class ProductAnalysis(BaseModel):
    buy: bool = False
    score: int = 0
    best_for: str = ""
    pros: List[str] = []
    cons: List[str] = []
    verdict: str = ""

    @field_validator("buy", mode="before")
    @classmethod
    def validate_buy(cls, v: Any) -> bool:
        return normalize_bool(v)

    @field_validator("score", mode="before")
    @classmethod
    def validate_score(cls, v: Any) -> int:
        return normalize_int(v)

    @field_validator("pros", "cons", mode="before")
    @classmethod
    def validate_lists(cls, v: Any) -> List[str]:
        return normalize_list_strings(v)


class ReceiptAnalysis(BaseModel):
    store: str = ""
    total_spent: float = 0.0
    largest_category: str = ""
    expensive_items: List[str] = []
    verdict: str = ""

    @field_validator("total_spent", mode="before")
    @classmethod
    def validate_total(cls, v: Any) -> float:
        return normalize_float(v)

    @field_validator("expensive_items", mode="before")
    @classmethod
    def validate_lists(cls, v: Any) -> List[str]:
        return normalize_list_strings(v)


class NotesAnalysis(BaseModel):
    topic: str = ""
    key_points: List[str] = []
    action_items: List[str] = []
    open_questions: List[str] = []

    @field_validator("key_points", "action_items", "open_questions", mode="before")
    @classmethod
    def validate_lists(cls, v: Any) -> List[str]:
        return normalize_list_strings(v)


class DocumentAnalysis(BaseModel):
    document_type: str = ""
    subject: str = ""
    entities: List[Entity] = []
    summary: str = ""

    @field_validator("entities", mode="before")
    @classmethod
    def validate_entities(cls, v: Any) -> List[dict]:
        return normalize_entities(v)


class ScreenshotAnalysis(BaseModel):
    application: str = ""
    ui_elements: List[str] = []
    text_content: str = ""
    context: str = ""

    @field_validator("ui_elements", mode="before")
    @classmethod
    def validate_lists(cls, v: Any) -> List[str]:
        return normalize_list_strings(v)
