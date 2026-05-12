import base64

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")
