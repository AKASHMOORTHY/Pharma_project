from pydantic import BaseModel
from datetime import date

class ProductionBatchCreate(BaseModel):
    batch_code: str
    date: date
    shift: str
    created_by: int

class ProductionBatchOut(ProductionBatchCreate):
    id: int

    class Config:
        from_attributes = True
