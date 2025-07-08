from pydantic import BaseModel, Field
from datetime import datetime

class StageLogCreate(BaseModel):
    production_batch_id: int
    stage_id: int
    input_quantity: float
    output_quantity: float
    machine_id: str
    operator_name: str
    start_time: datetime
    end_time: datetime
    remarks: str | None = None

class StageLogOut(StageLogCreate):
    id: int

    class Config:
        from_attributes = True
