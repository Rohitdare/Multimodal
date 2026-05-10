import base64
import json
import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from db import init_db, save_analysis, get_all_analyses, clear_history

# -------------------------
# App setup
# -------------------------
st.set_page_config(page_title="Structured Vision Agent", layout="wide")
st.title("Structured Multimodal Agent")

load_dotenv()
init_db()

# -------------------------
# API setup
# -------------------------
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY not found in .env")
    st.stop()

client = Groq(api_key=api_key)

# -------------------------
# Helpers
# -------------------------
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")


SYSTEM_PROMPT = """
You are a multimodal reasoning agent.

You will receive:
1. an image
2. a user question about that image

Your job:
- inspect the image carefully
- understand the user's intent
- decide what information is most useful
- return ONLY a valid JSON object

Rules:
- Return only JSON
- No markdown
- No code blocks
- No explanation outside JSON
- Use clear field names
- Use arrays for lists
- Use nested objects when useful
- Be specific and actionable
"""

# -------------------------
# Input UI
# -------------------------
uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp"]
)

question = st.text_input("Ask something about the image")

# -------------------------
# Main analysis flow
# -------------------------
if uploaded_file:
    image_bytes = uploaded_file.getvalue()
    st.image(image_bytes, caption="Uploaded Image", width=350)

    if question and st.button("Analyze Image"):
        try:
            base64_image = encode_image(image_bytes)

            with st.spinner("Analyzing image..."):
                response = client.chat.completions.create(
                    model="meta-llama/llama-4-scout-17b-16e-instruct",
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": question
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{uploaded_file.type};base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                    max_tokens=1024
                )

                raw_output = response.choices[0].message.content
                parsed = json.loads(raw_output)

                save_analysis(uploaded_file.name, question, parsed)

                st.success("Analysis complete")
                st.caption("Saved to database")

                st.subheader("Structured Output")
                st.json(parsed)

        except json.JSONDecodeError:
            st.error("Model returned invalid JSON")
            st.code(raw_output)

        except Exception as e:
            st.error(f"Error: {e}")

# -------------------------
# History section
# -------------------------
st.divider()
st.subheader("Analysis History")

if st.button("Clear History"):
    clear_history()
    st.success("History cleared")
    st.rerun()

history = get_all_analyses()

if not history:
    st.info("No analysis history yet.")
else:
    for row in history:
        record_id, image_name, question_text, result_json, created_at = row

        with st.expander(f"{image_name} | {question_text} | {created_at}"):
            st.write(f"**Record ID:** {record_id}")
            st.write(f"**Image:** {image_name}")
            st.write(f"**Question:** {question_text}")

            try:
                st.json(json.loads(result_json))
            except Exception:
                st.code(result_json)