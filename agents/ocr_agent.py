"""
OCR Agent: Responsible for extracting text from images.
"""
from core.ocr import extract_text

def run_ocr(image_path):

    text = extract_text(image_path)

    return {
        "ocr_text": text
    }