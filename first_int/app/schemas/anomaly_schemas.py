from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# For creating a new rule
class AnomalyRuleCreate(BaseModel):
    name: str
    source_table: str
    field_name: str
    condition: str
    severity: str
    is_active: Optional[bool] = True
    notify_roles: Optional[str] = "Manager"

class AnomalyRuleOut(AnomalyRuleCreate):
    id: int
    class Config:
        from_attributes = True

# ✅ For creating a new detected anomaly (INPUT schema)
class DetectedAnomalyCreate(BaseModel):
    test_id: str
    parameter: str
    value: float
    anomaly_type: str
    severity: str
    timestamp: datetime

# ✅ For reading anomaly from DB (OUTPUT schema)
class DetectedAnomalyOut(BaseModel):
    id: int
    source_id: str
    status: str
    severity: str
    description: str
    detected_at: datetime

    class Config:
        from_attributes = True

class AnomalyResolveInput(BaseModel):
    resolved_by: str
    resolution_notes: str

class DetectedAnomalyResponse(BaseModel):
    id: int
    test_id: int
    rule_id: int | None
    anomaly_type: str
    description: str
    timestamp: datetime

    class Config:
        from_attributes = True
