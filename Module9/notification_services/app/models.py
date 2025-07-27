from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from notification_services.app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"))  # Assuming user table exists
    message = Column(Text, nullable=False)
    event_type = Column(String(50), nullable=False)
    related_object_id = Column(Integer, nullable=True)
    seen = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    recipient = relationship("User", back_populates="notifications")


class EscalationRule(Base):
    __tablename__ = "escalation_rules"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    trigger_after_minutes = Column(Integer, nullable=False)
    escalate_to_id = Column(Integer, ForeignKey("users.id"))
    active = Column(Boolean, default=True)

    escalate_to = relationship("User", back_populates="escalation_rules")

# Dummy users for table for devlopemt purpose later removed while integrating

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    phone=Column(String,nullable=True)

    notifications = relationship("Notification", back_populates="recipient")
    escalation_rules = relationship("EscalationRule", back_populates="escalate_to")
