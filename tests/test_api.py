import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)

def test_predict():
    with TestClient(app) as client:
        response = client.post("/predict", json={
            "wall_material": "монолит",
            "avg_house_area": 120.0,
            "avg_construction_period": 18.0,
            "foundation_type": "ленточный",
            "roof_type": "скатная",
            "usage_count": 150
        })
        assert response.status_code == 200

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
