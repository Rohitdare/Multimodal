import easyocr

# Initialize reader once
reader = easyocr.Reader(['en'])


def extract_text(image_path):

    try:

        results = reader.readtext(image_path)

        extracted_text = []

        for result in results:

            text = result[1]

            extracted_text.append(text)

        return "\n".join(extracted_text)

    except Exception as e:

        return f"OCR Error: {e}"
