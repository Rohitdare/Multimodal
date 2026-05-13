import json

def parse_json(raw_output):
    cleaned = raw_output.strip()
    
    # Strip markdown
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
        
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
        
    cleaned = cleaned.strip()

    # Extract just the JSON object
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx:end_idx+1]
        
    try:
        return json.loads(cleaned), None

    except json.JSONDecodeError as e:
        return None, f"Invalid JSON returned by model. Error: {e}"
