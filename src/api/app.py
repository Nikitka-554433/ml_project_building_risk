from fastapi import FastAPI, HTTPException
import joblib
import pandas as pd
import numpy as np
import os
from src.domain.models import ProjectParams, PredictionResult
from src.db.database import init_db, save_prediction, get_history
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Construction Cost Predictor")
MODEL_PATH = "models/best_model.pkl"
model = None

@app.on_event("startup")
def startup():
    global model
    init_db()
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(f"Модель не найдена: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)

@app.post("/predict", response_model=PredictionResult)
async def predict(params: ProjectParams):
    if model is None:
        raise HTTPException(503, "Модель не загружена")
    df = pd.DataFrame([params.dict()])
    pred = model.predict(df)[0]
    pred = np.expm1(pred) 
    pred_id = save_prediction(params.dict(), float(pred))
    logger.info(f"Prediction made: params={params.dict()}, cost={pred:.2f}")
    return PredictionResult(id=pred_id, params=params, predicted_cost=float(pred))

@app.get("/history")
async def history(limit: int = 10):
    return get_history(limit)

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None}
