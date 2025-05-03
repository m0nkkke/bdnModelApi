from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from fastapi import HTTPException

def read_image(data: bytes) -> Image.Image:
    """
    Преобразует байты в PIL.Image, бросает HTTPException при ошибке.
    """
    try:
        img = Image.open(BytesIO(data)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Невозможно обработать изображение")
    return img

def annotate_image(image: Image.Image, result: dict) -> Image.Image:
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", size=16)
    except:
        font = ImageFont.load_default()

    for item in result.get("items", []):
        x1, y1, x2, y2 = item["bbox"]
        label = f"{item['name']} {item['confidence']:.2f}"  

        # рассчитываем размер текста
        l, t, r, b = draw.textbbox((0, 0), label, font=font)
        tw, th = r - l, b - t

        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        draw.rectangle([x1, y1 - th, x1 + tw, y1], fill="white")
        draw.text((x1, y1 - th), label, fill="red", font=font)

    return image