from fastapi import APIRouter, Query
from core.vector_store import query_similar

router = APIRouter(prefix="/memory")


@router.get("/search", summary="Semantic search over past analyses")
def search_memory(
    query: str = Query(..., description="Search query"),
    task_type: str | None = Query(None, description="Filter by task type"),
    n_results: int = Query(5, ge=1, le=20, description="Max results to return"),
):
    """Return semantically similar past analyses from ChromaDB."""
    results = query_similar(query, task_type=task_type, n_results=n_results)
    return {"query": query, "results": results}
