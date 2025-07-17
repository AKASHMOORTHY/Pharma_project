from pydantic import BaseModel
from typing import Optional
from datetime import time

# User & Role
class RoleOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    phone: str
    role_id: int
    is_active: Optional[bool] = True

class UserOut(UserCreate):
    id: int
    class Config:
        orm_mode = True

# Shift
class ShiftCreate(BaseModel):
    name: str
    start_time: str
    end_time: str
    supervisor_id: Optional[int]

class ShiftOut(ShiftCreate):
    id: int
    name: str
    start_time: str
    end_time: str
    supervisor_id: Optional[int]

    @classmethod
    def from_orm_with_time(cls, shift):
        return cls(
            id=shift.id,
            name=shift.name,
            start_time=shift.start_time.strftime("%H:%M"),
            end_time=shift.end_time.strftime("%H:%M"),
            supervisor_id=shift.supervisor_id
        )

    class Config:
        orm_mode = True

# QC Parameter
class QCParameterCreate(BaseModel):
    name: str
    product_id: int
    min_value: float
    max_value: float
    unit: str

class QCParameterOut(QCParameterCreate):
    id: int
    class Config:
        orm_mode = True

# Anomaly Rule
class AnomalyRuleCreate(BaseModel):
    name: str
    condition: str
    severity: str
    active: Optional[bool] = True

class AnomalyRuleOut(AnomalyRuleCreate):
    id: int
    class Config:
        orm_mode = True

# System Preference
class SystemPreferenceCreate(BaseModel):
    key: str
    value: str
    description: Optional[str] = ""

class SystemPreferenceOut(SystemPreferenceCreate):
    id: int
    class Config:
        from_attributes = True
