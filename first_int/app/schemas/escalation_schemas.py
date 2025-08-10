from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.user_schemas import UserOut

# # ---------- User ----------
# class UserBase(BaseModel):
#     email: str
#     full_name: Optional[str] = None

# class UserCreate(UserBase):
#     pass

# class User(UserBase):
#     id: int

#     class Config:
#         from_attributes = True

# ---------- Notification ----------
class NotificationBase(BaseModel):
    event_type: str
    message: str
    related_object_id: Optional[int] = None

class NotificationCreate(NotificationBase):
    recipient_id: int
    created_at: Optional[datetime] = None


class Notification(NotificationBase):
    id: int
    seen: bool
    created_at: datetime
    recipient: UserOut

    class Config:
        from_attributes = True

# ---------- Escalation Rule ----------
class EscalationRuleBase(BaseModel):
    event_type: str
    trigger_after_minutes: int
    escalate_to_id: int

class EscalationRuleCreate(EscalationRuleBase):
    pass

class EscalationRule(EscalationRuleBase):
    id: int
    active: bool
    escalate_to: UserOut

    class Config:
        from_attributes = True


class SMSRequest(BaseModel):
    to_number: str  # E.g., +91XXXXXXXXXX
    message: str
