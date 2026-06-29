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

# Путь к новой модели
MODEL_PATH = "models/best_cat_model.pkl"
model = None

@app.on_event("startup")
def startup():
    global model
    init_db()
    if not os.path.exists(MODEL_PATH):
        logger.error(f"Модель не найдена: {MODEL_PATH}")
        raise RuntimeError(f"Модель не найдена: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    logger.info("CatBoost модель загружена успешно")

@app.post("/predict", response_model=PredictionResult)
async def predict(params: ProjectParams):
    if model is None:
        raise HTTPException(503, "Модель не загружена")
    
    try:
        # Преобразуем входные данные
        df = pd.DataFrame([params.dict()])
        
        # Создаём признаки, которые использовались при обучении
        df['avg_project_floors'] = 10
        df['area_per_floor'] = df['avg_house_area'] / (df['avg_project_floors'] + 1)
        df['complexity_index'] = df['avg_project_floors'] * df['avg_construction_period']
        df['cost_per_area'] = 0
        
        # Добавляем недостающие категориальные признаки
        df['interior_type'] = 'unknown'
        df['interior_wall_material'] = 'unknown'
        df['facade_material'] = 'unknown'
        df['slab_material'] = 'unknown'
        df['is_green_house'] = False
        
        df['material_facade'] = df['wall_material'] + '_' + df['facade_material']
        df['roof_foundation'] = df['roof_type'] + '_' + df['foundation_type']
        
        expected_features = [
            'wall_material',
            'avg_house_area',
            'avg_construction_period',
            'foundation_type',
            'roof_type',
            'usage_count',
            'interior_type',
            'interior_wall_material',
            'facade_material',
            'slab_material',
            'is_green_house',
            'cost_per_area',
            'material_facade',
            'roof_foundation'
        ]
        
        # Проверка колонок
        for col in expected_features:
            if col not in df.columns:
                df[col] = 'unknown' if col not in ['is_green_house', 'cost_per_area'] else 0
        
        # Приводим к правильному порядку
        df = df[expected_features]
        
        # Предсказание
        pred = model.predict(df)[0]
        
        # Обратное преобразование (если модель обучалась с log1p)
        pred = np.expm1(pred)
        
        # Сохраняем предсказание в БД
        pred_id = save_prediction(params.dict(), float(pred))
        logger.info(f"Prediction made: params={params.dict()}, cost={pred:.2f}")
        
        return PredictionResult(id=pred_id, params=params, predicted_cost=float(pred))
        
    except Exception as e:
        logger.error(f"Ошибка при предсказании: {e}")
        raise HTTPException(500, detail=f"Ошибка сервиса: {str(e)}")

@app.get("/history")
async def history(limit: int = 10):
    return get_history(limit)

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None}