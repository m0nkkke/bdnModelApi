import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from .model import Recognizer
from .schemas import PredictionResponse
from .utils import read_image, annotate_image

app = FastAPI(
    title="Recognizer API",
    version="1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# загружаем модель один раз при старте
recognizer = Recognizer(model_path="models/recog.pt", device="cpu")

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    # проверка типа
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Неподдерживаемый тип файла")
    data = await file.read()
    img = read_image(data)
    result = recognizer.predict(img)
    return JSONResponse(content=result)

@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    """
    Возвращает аннотированное изображение PNG с боксами и подписями.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(415, "Unsupported file type")
    data = await file.read()
    img = read_image(data)

    # 1) получаем детекции
    result = recognizer.predict(img)

    # 2) аннотируем исходную картинку
    annotated = annotate_image(img, result)

    # 3) сериализуем в PNG в память
    buf = io.BytesIO()
    annotated.save(buf, format="PNG")
    buf.seek(0)

    # 4) возвращаем поток
    return StreamingResponse(buf, media_type="image/png")