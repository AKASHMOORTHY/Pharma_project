from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductionOut(BaseModel):
    date: Optional[datetime]
    shift: Optional[str]
    total_batches: Optional[int]
    completed_batches: Optional[int]
    avg_batch_time: Optional[float]

    class Config:
        from_attributes = True

class QCOut(BaseModel):
    result: str
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class InventoryOut(BaseModel):
    material: str
    quantity: int
    category: str
    location: str
    updated_at: datetime

    class Config:
        from_attributes = True

class AnomalyOut(BaseModel):
    category: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

