import requests
from core.config import LOCAL_API_BASE, LOCAL_MODEL, MAX_TOKENS, TEMPERATURE


def call_local(messages: list[dict]) -> str:
    response = requests.post(
        f"{LOCAL_API_BASE}/chat/completions",
        headers={"Content-Type": "application/json"},
        json={
            "model": LOCAL_MODEL,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "temperature": TEMPERATURE,
            "max_tokens": MAX_TOKENS,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]
