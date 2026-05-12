from groq import Groq

from core.config import (
    GROQ_API_KEY,
    MODEL_NAME,
    MAX_TOKENS,
    TEMPERATURE
)

client = Groq(api_key=GROQ_API_KEY)

def analyze_image(messages):

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS
    )

    return response.choices[0].message.content
