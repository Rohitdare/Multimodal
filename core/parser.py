import json

def parse_json(raw_output):
    try:
        return json.loads(raw_output), None

    except json.JSONDecodeError:
        return None, "Invalid JSON returned by model"
