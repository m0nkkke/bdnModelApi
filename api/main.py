import io

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .model import Recognizer
from .schemas import PredictionResponse
from .utils import read_image, annotate_image

app = FastAPI(title="Recognizer API", version="1.0")

# Статика и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Инициализируем модель один раз
recognizer = Recognizer(model_path="models/recog.pt", device="cpu")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Отдаём одну страницу с формой загрузки
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict", response_model=PredictionResponse)
async def predict_json(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(415, "Unsupported file type")
    img = read_image(await file.read())
    result = recognizer.predict(img)
    return JSONResponse(content=result)

@app.post("/predict/image")
async def predict_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(415, "Unsupported file type")
    img = read_image(await file.read())
    result = recognizer.predict(img)
    annotated = annotate_image(img, result)

    buf = io.BytesIO()
    annotated.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
