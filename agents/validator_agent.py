"""
Validator Agent: Responsible for enforcing structured JSON outputs against Pydantic schemas.
"""
from core.parser import parse_json
from core.validator import validate_output

def validate_result(raw_output, schema_class):

    parsed, error = parse_json(raw_output)

    if error:
        return {"error": error}

    validated, val_error = validate_output(
        schema_class,
        parsed
    )

    if val_error:
        return {"error": val_error, "raw": parsed}

    return {"result": validated}
