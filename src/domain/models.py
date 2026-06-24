from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProjectParams(BaseModel):
    wall_material: str
    avg_house_area: float
    avg_construction_period: float
    foundation_type: str
    roof_type: str
    usage_count: int

class PredictionResult(BaseModel):
    id: Optional[int] = None
    params: ProjectParams
    predicted_cost: float
    created_at: datetime = datetime.now()
