import chromadb
from core.config import CHROMA_DB_PATH

# Persistent client — survives server restarts
_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

_collection = _client.get_or_create_collection(
    name="analysis_memory_v2"
)


def store_embedding(record_id: str, question: str, result_text: str, task_type: str) -> None:
    """Upsert a past analysis into the vector store."""
    text_data = f"Past Question: {question}\nPast Analysis: {result_text}"
    _collection.upsert(
        documents=[text_data],
        ids=[str(record_id)],
        metadatas=[{"task_type": task_type}],
    )


def query_similar(query: str, task_type: str | None = None, n_results: int = 5) -> list[dict]:
    """Return semantically similar past analyses."""
    if _collection.count() == 0:
        return []

    actual_n = min(n_results, _collection.count())

    results = _collection.query(query_texts=[query], n_results=actual_n)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    filtered = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        meta_dict = meta or {}
        if task_type and meta_dict.get("task_type") != task_type:
            continue
        # Normalise distance to a 0-1 score (lower distance = higher score)
        score = max(0.0, 1.0 - dist) if dist is not None else 0.0
        filtered.append({"text": doc, "score": score})

    return filtered


def clear_embeddings() -> None:
    """Remove all stored embeddings."""
    all_ids = _collection.get()["ids"]
    if all_ids:
        _collection.delete(ids=all_ids)
