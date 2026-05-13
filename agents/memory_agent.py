"""
Memory Agent: Responsible for managing semantic RAG memory and storing/retrieving past analyses.
"""
from core.vector_store import query_similar

def retrieve_memory(question, task_type):

    results = query_similar(
        question,
        task_type=task_type,
        n_results=5
    )

    return {
        "memory": results
    }
