import streamlit as st

from database.db import (
    init_db,
    save_analysis,
    get_all_analyses,
    clear_history
)

from core.vector_store import store_embedding, query_similar
from services.storage_service import save_uploaded_file
from agents.coordinator import run_pipeline

# -------------------------
# App setup
# -------------------------
st.set_page_config(
    page_title="Structured Vision Agent",
    layout="wide"
)

st.title("🧠 Structured Multimodal Agent")

init_db()

# -------------------------
# Input UI
# -------------------------
uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp"]
)

question = st.text_input(
    "Ask something about the image"
)

max_context_items = st.slider(
    "Memory Context Size",
    min_value=1,
    max_value=5,
    value=3
)

# -------------------------
# Main analysis flow
# -------------------------
if uploaded_file:

    image_bytes = uploaded_file.getvalue()

    st.image(
        image_bytes,
        caption="Uploaded Image",
        width=350
    )

    if question and st.button("Analyze Image"):

        try:

            # -------------------------
            # Save uploaded image
            # -------------------------
            image_path = save_uploaded_file(
                uploaded_file,
                image_bytes
            )

            with st.spinner("Analyzing image..."):
                result = run_pipeline(
                    uploaded_file,
                    image_bytes,
                    question,
                    max_context_items=max_context_items
                )

            st.info(f"Task: {result['task_type']}")

            with st.expander("Extracted OCR Text"):
                st.code(result["ocr"]["ocr_text"][:2000])

            with st.expander("RAG Context (Optimized)"):
                if not result["memory"]["memory"]:
                    st.write("No similar memory found")
                else:
                    for item in result["memory"]["memory"]:
                        st.write(f"Score: {item['score']:.2f}")
                        st.write(item["text"])
                        st.divider()

            if "error" in result["final"]:
                st.error(result["final"]["error"])
                if "raw" in result["final"]:
                    st.json(result["final"]["raw"])
                st.stop()
            else:
                st.subheader("Structured Output")
                st.json(result["final"]["result"])

                # -------------------------
                # Save analysis
                # -------------------------
                save_analysis(
                    uploaded_file.name,
                    question,
                    result["final"]["result"]
                )

                store_embedding(
                    record_id=str(uploaded_file.name),
                    question=question,
                    result_text=str(result["final"]["result"]),
                    task_type=result["task_type"]
                )

            st.success("Analysis complete")
            st.caption(f"Saved image to: {image_path}")

        except Exception as e:

            st.error(f"Error: {e}")

# -------------------------
# History section
# -------------------------
st.divider()

st.subheader("📜 Analysis History")

if st.button("Clear History"):

    clear_history()

    st.success("History cleared")

    st.rerun()

history = get_all_analyses()

if not history:

    st.info("No analysis history yet.")

else:

    for row in history:

        (
            record_id,
            image_name,
            question_text,
            result_json,
            created_at
        ) = row

        with st.expander(
            f"{image_name} | {question_text} | {created_at}"
        ):

            st.write(f"**Record ID:** {record_id}")

            st.write(f"**Image:** {image_name}")

            st.write(f"**Question:** {question_text}")

            try:

                st.json(result_json)

            except Exception:

                st.code(result_json)

st.divider()
st.subheader("🔍 Semantic Search")

search_query = st.text_input("Search similar past analyses")

if search_query and st.button("Search Memory"):

    results = query_similar(search_query)

    st.write("### Similar Results")

    try:
        for doc in results:
            st.write(doc)
    except Exception:
        st.write(results)