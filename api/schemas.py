from pydantic import BaseModel
from typing import List, Tuple

class DetectionItem(BaseModel):
    type: str                     # "barcode" | "date" | "name"
    value: str                    # распознанный текст
    confidence: float             # вероятность
    bbox: Tuple[float, float, float, float]

class PredictionResponse(BaseModel):
    items: List[DetectionItem]
