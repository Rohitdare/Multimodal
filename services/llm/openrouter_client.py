import requests
from core.config import OPENROUTER_API_KEY, OPENROUTER_MODEL

_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(messages: list[dict]) -> str:
    response = requests.post(
        _BASE_URL,
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/multimodal-agent",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": messages,
            "response_format": {"type": "json_object"},
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()

    if "choices" not in data:
        raise ValueError(f"OpenRouter unexpected response: {data}")

    return data["choices"][0]["message"]["content"]
