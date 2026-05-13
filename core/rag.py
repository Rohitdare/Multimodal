def build_rag_context(similar_docs, max_items=3):

    if not similar_docs:
        return ""

    context = "Relevant past analyses:\n\n"

    for i, doc in enumerate(similar_docs[:max_items], start=1):

        context += f"{i}. (score: {doc['score']:.2f}) {doc['text']}\n\n"

    return context
