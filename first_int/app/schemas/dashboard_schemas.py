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
    material: int
    quantity: int
    status: str
    location: str
    updated_at: datetime

    class Config:
        from_attributes = True

class AnomalyOut(BaseModel):

    status: str
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True

class ReportRequest(BaseModel):
    report_name: str
    format: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    shift: Optional[str] = None

