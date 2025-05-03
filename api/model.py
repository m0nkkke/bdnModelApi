from typing import Any, Dict, List
from PIL import Image
from ultralytics import YOLO

from .utils import crop, ocr_text, decode_barcode_value

class Recognizer:
    """
    Обёртка над моделью Ultralytics YOLO для распознации
    штрих‑кодов, дат и названий.
    """
    def __init__(self, model_path: str, device: str = "cpu"):
        self.model = YOLO(model_path)
        self.model.to(device)

    def predict(self, image: Image.Image) -> Dict[str, List[Dict[str, Any]]]:
        """
        Принимает PIL.Image, возвращает словарь вида:
        {
            "items": [
                {
                    "type": "barcode"|"date"|"name",
                    "value": "<распознанный текст>",
                    "confidence": 0.87,
                    "bbox": [x1, y1, x2, y2]
                },
                ...
            ]
        }
        """
        results = self.model(image)
        # Передаём и результаты, и исходное изображение в парсер
        return self._parse(results, image)

    def _parse(
        self,
        results: Any,
        image: Image.Image
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Преобразуем Ultralytics Results и исходное PIL.Image
        в формат, понятный фронтенду.
        """
        items: List[Dict[str, Any]] = []

        for r in results:  # обычно один результат на картинку
            for box in r.boxes:
                cls_idx = int(box.cls)
                cls_name = r.names[cls_idx]            # "barcode", "date" или "name"
                bbox = box.xyxy.tolist()[0]            # [x1, y1, x2, y2]
                confidence = float(box.conf)           # уверенность 0.0–1.0

                # вырезаем ROI из исходного PIL‑изображения
                roi = crop(image, bbox)

                # в зависимости от класса подбираем метод распознавания
                if cls_name == "barcode":
                    value = decode_barcode_value(roi)
                elif cls_name == "date":
                    value = ocr_text(roi)
                else:  # name
                    value = ocr_text(roi)

                items.append({
                    "type":       cls_name,
                    "value":      value,
                    "confidence": confidence,
                    "bbox":       bbox
                })

        return {"items": items}
