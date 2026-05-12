import streamlit as st

from database.db import (
    init_db,
    save_analysis,
    get_all_analyses,
    clear_history
)

from core.vision import encode_image
from core.parser import parse_json
from core.router import classify_task, get_prompt, get_schema
from core.validator import validate_output
from core.ocr import extract_text

from services.analysis_service import analyze_image
from services.storage_service import save_uploaded_file

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

            ocr_text = extract_text(image_path)

            st.subheader("Extracted OCR Text")

            st.code(ocr_text[:2000])

            # -------------------------
            # Encode image
            # -------------------------
            base64_image = encode_image(image_bytes)

            # -------------------------
            # Task routing
            # -------------------------
            task_type = classify_task(question)

            system_prompt = get_prompt(task_type)

            schema_class = get_schema(task_type)

            st.info(f"Detected Task Type: {task_type}")

            # -------------------------
            # Build messages
            # -------------------------
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""
User Question:
{question}

OCR Extracted Text:
{ocr_text}
"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{uploaded_file.type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

            # -------------------------
            # Model inference
            # -------------------------
            with st.spinner("Analyzing image..."):

                raw_output = analyze_image(messages)

            # -------------------------
            # Parse response
            # -------------------------
            parsed_output, error = parse_json(raw_output)

            validated_output, validation_error = validate_output(
                schema_class,
                parsed_output
            )

            if validation_error:

                st.error("Schema validation failed")

                st.code(validation_error)

                st.json(parsed_output)

                st.stop()

            if error:   
                st.error(error)
                st.code(raw_output)
                st.stop()

            # -------------------------
            # Save analysis
            # -------------------------
            save_analysis(
                uploaded_file.name,
                question,
                validated_output
            )

            # -------------------------
            # Render results
            # -------------------------
            st.success("Analysis complete")

            st.caption(f"Saved image to: {image_path}")

            st.subheader("Structured Output")

            st.json(validated_output)

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