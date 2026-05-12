import os

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_uploaded_file(uploaded_file, image_bytes):

    filepath = os.path.join(UPLOAD_DIR, uploaded_file.name)

    with open(filepath, "wb") as f:
        f.write(image_bytes)

    return filepath 
