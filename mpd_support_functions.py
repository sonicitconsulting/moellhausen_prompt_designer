from PIL import Image
from io import BytesIO
import base64

def load_image(image_path):
    with Image.open(image_path) as img:
        buf = BytesIO()
        img.save(buf, format="PNG")  # puoi forzare PNG anche se il file è jpg
        b64 = base64.b64encode(buf.getvalue()).decode()
        data_url = f"data:image/png;base64,{b64}"

    return data_url

def load_system_prompt(system_prompt_path):
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def save_system_prompt(system_prompt_path, contenuto):
    with open(system_prompt_path, "w", encoding="utf-8") as f:
        f.write(contenuto)