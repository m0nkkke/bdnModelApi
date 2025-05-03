import pytesseract
from pytesseract import TesseractNotFoundError
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
from fastapi import HTTPException
from pyzbar.pyzbar import decode as decode_barcode

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
    """
    Рисует боксы и подписи на PIL‑картинке по данным из result:
      type, value, confidence и bbox из каждого item.
    """
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", size=16)
    except:
        font = ImageFont.load_default()

    for item in result.get("items", []):
        x1, y1, x2, y2 = item["bbox"]
        # Формируем подпись: тип, значение и confidence
        label = f"{item['type']}: {item['value']} ({item['confidence']:.2f})"

        # Определяем размеры текста с помощью textbbox
        left, top, right, bottom = draw.textbbox((0, 0), label, font=font)
        text_width, text_height = right - left, bottom - top

        # Рисуем прямоугольник вокруг объекта
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        # Рисуем фон для текста
        draw.rectangle(
            [x1, y1 - text_height, x1 + text_width, y1],
            fill="white"
        )
        # Рисуем сам текст
        draw.text((x1, y1 - text_height), label, fill="red", font=font)

    return image

def crop(image: Image.Image, bbox: tuple) -> Image.Image:
    """
    Обрезает из PIL‑изображения регион, заданный bbox.
    """
    x1, y1, x2, y2 = map(int, bbox)
    return image.crop((x1, y1, x2, y2))

def ocr_text(image: Image.Image) -> str:
    """
    Запускает Tesseract OCR, возвращает распознанный текст.
    Если Tesseract не найден — возвращает пустую строку.
    """
    try:
        return pytesseract.image_to_string(image, lang='rus', config="--psm 6").strip()
    except TesseractNotFoundError:
        return ""
    
# def ocr_date(image: Image.Image) -> str:
#     """
#     OCR для даты: сначала предобрабатываем ROI, 
#     затем Tesseract с whitelist цифр и точек.
#     """
#     # 1) переводим в градации серого
#     gray = image.convert("L")
#     # 2) растягиваем контраст
#     gray = ImageOps.autocontrast(gray)
#     # 3) бинаризуем (порог 128)
#     bw = gray.point(lambda x: 0 if x < 128 else 255, mode="1")
#     # 4) увеличиваем в 2–3 раза, чтобы буквы были чётче
#     w, h = bw.size
#     bw = bw.resize((w * 2, h * 2), resample=Image.BILINEAR)

#     # 5) вызываем tesseract только для цифр и точки
#     config = "--oem 1 --psm 7 -c tessedit_char_whitelist=0123456789."
#     try:
#         txt = pytesseract.image_to_string(bw, lang="eng", config=config).strip()
#     except TesseractNotFoundError:
#         return ""
#     # 6) отфильтруем «лишние» символы регуляркой
#     import re
#     m = re.search(r"\d{1,2}\.\d{1,2}\.?\d{0,4}", txt)
#     return m.group(0) if m else txt

def decode_barcode_value(image: Image.Image) -> str:
    """
    Декодирует штрих‑код в ROI с помощью pyzbar.
    """
    codes = decode_barcode(image)
    return codes[0].data.decode("utf-8") if codes else ""
