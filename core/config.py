import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Project root ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ── API keys ──────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# ── Provider selection ────────────────────────────────────────────────────────
# Options: "groq" | "openrouter" | "local"
ACTIVE_PROVIDER = os.getenv("ACTIVE_PROVIDER", "groq")

# ── Model names ───────────────────────────────────────────────────────────────
GROQ_MODEL = os.getenv("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
LOCAL_MODEL = os.getenv("LOCAL_MODEL", "llava")
LOCAL_API_BASE = os.getenv("LOCAL_API_BASE", "http://localhost:11434/v1")

# ── Inference settings ────────────────────────────────────────────────────────
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1024"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))

# ── Storage paths ─────────────────────────────────────────────────────────────
UPLOAD_DIR = BASE_DIR / "uploads"
CHROMA_DB_PATH = str(BASE_DIR / "chroma_db")
DB_PATH = str(BASE_DIR / "agent_data.db")

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
