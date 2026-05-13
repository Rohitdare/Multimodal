"""
Reasoning Agent: Responsible for analyzing images and text, leveraging the LLM.
"""
from services.llm.model_router import call_model_with_fallback

def run_reasoning(messages):

    output = call_model_with_fallback(messages)

    return {
        "raw_output": output
    }
