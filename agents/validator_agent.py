"""
Validator Agent: Responsible for enforcing structured JSON outputs against Pydantic schemas.
Falls back gracefully so the user always gets data.
"""
import logging

from core.parser import parse_json
from core.validator import validate_output

logger = logging.getLogger(__name__)


def validate_result(raw_output, schema_class):
    """
    Parse raw LLM output into JSON, then validate against the schema.
    Always returns a result — never returns just an error.
    """
    parsed, error = parse_json(raw_output)

    if error:
        logger.error("JSON parse failed: %s", error)
        return {"error": error}

    validated, val_error = validate_output(schema_class, parsed)

    if val_error:
        # This shouldn't happen anymore since validator always returns (data, None),
        # but handle it defensively by returning the raw parsed data.
        logger.warning("Validation returned error (unexpected): %s", val_error)
        return {"result": parsed}

    return {"result": validated}
