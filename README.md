# 🧠 Multimodal AI Agent

A full-stack document intelligence system that combines **OCR**, **vector memory (RAG)**, and **multi-provider LLM reasoning** to extract structured JSON from images.

Built with **FastAPI** (backend) + **Next.js 16** (frontend).

---

## Architecture

```
Image Upload
     │
     ▼
OCR Agent (EasyOCR)
     │
     ▼
Memory Agent (ChromaDB RAG) ──► similar past analyses
     │
     ▼
Reasoning Agent (Groq → OpenRouter → Local fallback)
     │
     ▼
Validator Agent (Pydantic schema enforcement)
     │
     ▼
Structured JSON Response
```

### Task Types

| Task | Triggered by |
|------|-------------|
| `receipt` | "receipt", "spending", "expense", "bill" |
| `product` | "buy", "product", "worth", "review" |
| `notes` | "summary", "summarize", "meeting", "notes" |
| `documents` | "document", "paper", "letter", "form" |
| `screenshots` | "screenshot", "app", "ui", "interface" |
| `general` | everything else |

---

## Project Structure

```
multimodal-agent/
├── agents/                 # Agent modules (OCR, memory, reasoning, validator, coordinator)
├── backend/
│   ├── main.py             # FastAPI app entry point
│   └── routes/             # API route handlers
├── core/                   # Shared utilities (config, OCR, RAG, prompts, router, parser)
├── database/               # SQLite persistence
├── frontend/               # Next.js UI
├── models/                 # Pydantic response schemas
├── services/
│   ├── llm/                # LLM provider clients (Groq, OpenRouter, Local)
│   └── storage_service.py  # File upload handling
├── .env.example            # Environment variable template
└── requirements.txt
```

---

## Quick Start

### 1. Clone & set up environment

```bash
git clone <repo-url>
cd multimodal-agent

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required:
- `GROQ_API_KEY` — [Get one at console.groq.com](https://console.groq.com)
- `OPENROUTER_API_KEY` — [Get one at openrouter.ai](https://openrouter.ai) *(fallback)*

### 3. Start the backend

```bash
uvicorn backend.main:app --reload
# API available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 4. Start the frontend

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
# UI available at http://localhost:3000
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/analyze/` | Analyse an image — multipart form with `file` + `question` |
| `GET` | `/history/` | Get all past analyses |
| `DELETE` | `/history/` | Clear all history |
| `GET` | `/memory/search?query=...` | Semantic search over past analyses |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |

### Analyze request example

```bash
curl -X POST http://localhost:8000/analyze/ \
  -F "file=@receipt.jpg" \
  -F "question=Analyze this receipt"
```

### Analyze response example

```json
{
  "task_type": "receipt",
  "ocr_text": "Walmart\nMilk $3.49\nBread $2.99\nTotal $6.48",
  "output": {
    "result": {
      "store": "Walmart",
      "total_spent": 6.48,
      "largest_category": "Groceries",
      "expensive_items": ["Milk"],
      "verdict": "Low spending, within budget."
    }
  }
}
```

---

## LLM Provider Fallback

The system automatically tries providers in order:

1. **Groq** (primary — fast inference)
2. **OpenRouter** (fallback — GPT-4o-mini)
3. **Local Ollama** (final fallback — llava)

Configure via `ACTIVE_PROVIDER` env var or let the fallback chain handle it automatically.

---

## Environment Variables

See [`.env.example`](.env.example) for the full list with documentation.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Uvicorn |
| Frontend | Next.js 16, TypeScript, Tailwind CSS v4 |
| OCR | EasyOCR |
| Vector Memory | ChromaDB (persistent) |
| LLM | Groq / OpenRouter / Ollama |
| Database | SQLite |
| Validation | Pydantic v2 |
