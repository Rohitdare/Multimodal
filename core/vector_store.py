import chromadb

# Create persistent DB
client = chromadb.Client()

collection = client.get_or_create_collection(
    name="analysis_memory"
)


def store_embedding(record_id, question, result_text, task_type):

    text_data = f"{question} {result_text}"

    collection.add(
        documents=[text_data],
        ids=[str(record_id)],
        metadatas=[{
            "task_type": task_type
        }]
    )


def query_similar(query, task_type=None, n_results=5):

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    filtered = []

    for doc, meta, dist in zip(documents, metadatas, distances):

        meta_dict = meta or {}
        if task_type and meta_dict.get("task_type") != task_type:
            continue

        filtered.append({
            "text": doc,
            "score": 1 - dist if dist else 0
        })

    return filtered
