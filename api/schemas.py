from pydantic import BaseModel
from typing import List, Tuple

class Item(BaseModel):
    name: str
    confidence: float   
    bbox: Tuple[float, float, float, float]  # (x1, y1, x2, y2)

class PredictionResponse(BaseModel):
    barcodes: List[str]
    items: List[Item]
