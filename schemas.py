from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel
from typing import Optional

class QCParameterSchema(BaseModel):
    material: str
    name: str
    min_value: Optional[float]
    max_value: Optional[float]
    unit: str
    id: Optional[int] = None  # Ensure this is at the end and has a default

    class Config:
        orm_mode = True  # Required for SQLAlchemy compatibility



class QCTestResultSchema(BaseModel):
    parameter_id: int
    observed_value: float
    is_within_spec: bool = False

    class Config:
        orm_mode = True

class QCTestSchema(BaseModel):
    id: Optional[str]
    source_type: str
    source_id: str
    performed_by: str
    date: Optional[datetime] = None
    status: str
    remarks: Optional[str]
    attachment_filename: Optional[str]
    results: List[QCTestResultSchema]

    class Config:
        orm_mode = True

class QCOverrideSchema(BaseModel):
    test_id: str
    overridden_by: str
    new_status: str
    comment: str