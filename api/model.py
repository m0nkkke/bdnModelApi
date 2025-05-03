from ultralytics import YOLO
from torchvision import transforms
from PIL import Image

class Recognizer:
    """
    Обёртка над моделью Ultralytics YOLO, 
    загруженной из .pt с весами и конфигом.
    """
    def __init__(self, model_path: str, device: str = "cpu"):
        self.model = YOLO(model_path)
        self.model.to(device)

        self.transform = transforms.Compose([
            transforms.Resize((640, 640)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[.485, .456, .406],
                                 std=[.229, .224, .225]),
        ])

    def predict(self, image: Image.Image) -> dict:
        """
        Принимает PIL.Image, возвращает dict с результатами детекции.
        `results` — объект Ultralytics Results, из которого можно брать
        координаты, метки, confidence и т.д.
        """
        results = self.model(image)

        return self._parse(results)

    def _parse(self, results) -> dict:
        """
        Преобразуем Ultralytics Results в dict с confidence.
        """
        barcodes = []
        items = []
        for r in results:                 # один результат на картинку
            for box in r.boxes:           # объект Box с attrs cls, conf, xyxy
                cls = r.names[int(box.cls)]
                conf = float(box.conf)    # уверенность от 0.0 до 1.0
                xyxy = box.xyxy.tolist()[0]
                items.append({
                    "name": cls,
                    "confidence": conf,
                    "bbox": xyxy
                })
        return {"barcodes": barcodes, "items": items}

