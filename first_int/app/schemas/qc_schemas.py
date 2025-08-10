from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class QCParameterSchema(BaseModel):
    material: str
    name: str
    min_value: Optional[float]
    max_value: Optional[float]
    unit: str
    id: Optional[int] = None  # Ensure this is at the end and has a default

    class Config:
        from_attributes = True  # Required for SQLAlchemy compatibility



class QCTestResultSchema(BaseModel):
    parameter_id: int
    observed_value: float
    is_within_spec: bool

    class Config:
        from_attributes = True

class QCTestSchema(BaseModel):
    id: Optional[str]
    source_type: str
    source_id: str
    date: Optional[datetime] = None
    status: str
    remarks: Optional[str]
    attachment_filename: Optional[str]
    results: List[QCTestResultSchema]
    performed_by_id: int  # Only in response, not in request
    production_batch_id: int
    material_batch_id: int

    class Config:
        from_attributes = True

class QCOverrideSchema(BaseModel):
    test_id: str
    new_status: str
    comment: str
    
    class Config:
        from_attributes = True