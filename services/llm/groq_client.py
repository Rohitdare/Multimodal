from groq import Groq
from core.config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS, TEMPERATURE

_client = Groq(api_key=GROQ_API_KEY)


def call_groq(messages: list[dict]) -> str:
    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content
