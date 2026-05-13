import logging

from services.llm.groq_client import call_groq
from services.llm.openrouter_client import call_openrouter
from services.llm.local_client import call_local

logger = logging.getLogger(__name__)

_PROVIDERS = [
    ("Groq", call_groq),
    ("OpenRouter", call_openrouter),
    ("Local", call_local),
]


def call_model_with_fallback(messages: list[dict]) -> str:
    """
    Try each provider in order: Groq → OpenRouter → Local.
    Raises if all three fail.
    """
    last_error: Exception | None = None

    for name, fn in _PROVIDERS:
        try:
            result = fn(messages)
            logger.info("Provider '%s' succeeded.", name)
            return result
        except Exception as exc:
            logger.warning("Provider '%s' failed: %s", name, exc)
            last_error = exc

    raise RuntimeError("All model providers failed.") from last_error
