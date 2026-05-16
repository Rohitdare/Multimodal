import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import analyze, memory, history
from database.db import init_db


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("Initialising database…")
    init_db()
    logger.info("Database ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Multimodal AI Agent API",
    description="Vision + OCR + RAG reasoning agent with multi-provider LLM fallback.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, tags=["Analyze"])
app.include_router(memory.router, tags=["Memory"])
app.include_router(history.router, tags=["History"])


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "version": "1.0.0"}
