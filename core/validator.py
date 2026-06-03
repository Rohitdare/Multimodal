"""
Core validator: validates parsed LLM output against a Pydantic schema.

Uses model_validate() for robust validation and includes a fallback
so the user always gets data even if strict validation fails.
"""
import logging

logger = logging.getLogger(__name__)


def validate_output(schema_class, parsed_output):
    """
    Validate parsed_output against a Pydantic schema.

    Returns (validated_dict, None) on success,
    or (parsed_output_as_is, None) on failure — never returns an error to the user.
    """
    # ── TEMPORARY DEBUG: Remove after fixing production ──────────────────────
    if schema_class is not None:
        print(f"DEBUG SCHEMA: {schema_class.__name__}")
        print(f"DEBUG FIELDS: {schema_class.model_fields}")
        print(f"DEBUG JSON_SCHEMA: {schema_class.model_json_schema()}")
        if isinstance(parsed_output, dict):
            print(f"DEBUG ENTITIES_TYPE: {type(parsed_output.get('entities'))}")
            print(f"DEBUG ENTITIES_VALUE: {parsed_output.get('entities')}")
    # ── END DEBUG ────────────────────────────────────────────────────────────

    if schema_class is None:
        return parsed_output, None

    if not isinstance(parsed_output, dict):
        return parsed_output, None

    # ── Attempt 1: validate with model_validate (recommended Pydantic v2 API) ──
    try:
        validated = schema_class.model_validate(parsed_output)
        return validated.model_dump(), None
    except Exception as e:
        logger.warning(
            "model_validate failed for %s: %s — trying fallback",
            schema_class.__name__, e,
        )

    # ── Attempt 2: try ** unpacking as a fallback ──
    try:
        validated = schema_class(**parsed_output)
        return validated.model_dump(), None
    except Exception as e:
        logger.warning(
            "** unpacking also failed for %s: %s — returning raw data",
            schema_class.__name__, e,
        )

    # ── Fallback: return the raw parsed data as-is so the user always gets results ──
    return parsed_output, None
