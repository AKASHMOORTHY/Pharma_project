from pydantic import BaseModel, validator, Field
from datetime import datetime, date
from typing import Optional

class ProductionBatchCreate(BaseModel):
    batch_code: str
    date: date
    shift: str
    operator_id: int
    batch_id: int

class StageLogBase(BaseModel):
    production_batch_id: int
    stage_id: int
    input_material_batch: str
    input_quantity: float
    output_quantity: float
    machine_id: str
    operator_name: str
    start_time: datetime
    end_time: datetime
    remarks: str
    status: str

    @validator("end_time")
    def check_time(cls, end_time, values):
        if "start_time" in values and end_time <= values["start_time"]:
            raise ValueError("End time must be after start time")
        return end_time

    @validator("output_quantity")
    def check_qty(cls, out_qty, values):
        if "input_quantity" in values and out_qty > values["input_quantity"]:
            raise ValueError("Output quantity cannot exceed input")
        return out_qty

class StageLogCreate(StageLogBase):
    pass

class StageLogUpdate(StageLogBase):
    pass


class StageLogResponse(BaseModel):
    id: int
    production_batch_id: int
    stage_id: int
    input_material_batch: str
    input_quantity: float
    output_quantity: float
    machine_id: str
    operator_name: str
    start_time: datetime
    end_time: datetime
    remarks: str
    status: str
    is_locked: int

    class Config:
        from_attributes = True


class ProductionBatchResponse(BaseModel):
    id: int
    batch_code: str
    date: date
    shift: str
    operator_id: int = Field(...,alias="created_by")

    class Config:
        from_attributes = True
        validate_by_name = True

class ProcessStageCreate(BaseModel):
    name: str

class ProcessStageResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
