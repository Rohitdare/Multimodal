def build_rag_context(similar_docs, max_items=3):

    if not similar_docs:
        return ""

    context = "<historical_memory>\nRelevant past analyses that you can use to inform your current analysis. DO NOT copy these exactly, just use them for context:\n\n"

    for i, doc in enumerate(similar_docs[:max_items], start=1):

        context += f"--- Past Example {i} (Similarity: {doc['score']:.2f}) ---\n{doc['text']}\n\n"

    context += "</historical_memory>"

    return context
