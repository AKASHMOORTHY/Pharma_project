# app/models.py
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(20), unique=True)
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    shift = Column(String)
    last_login = Column(DateTime, default=None)
    phone_number = Column(String, nullable=True)

    role = relationship("Role", back_populates="users")
    sessions = relationship("UserSessionLog", back_populates="user")
    material_batches = relationship("app.models.materials_models.MaterialBatch", back_populates="creator")

    production_batches = relationship("app.models.production_models.ProductionBatch", back_populates="operator")
    
    qc_tests = relationship("app.models.qc_models.QCTest", back_populates="performed_by")
    

    stock_movements = relationship("app.models.inventory_models.StockMovement", back_populates="user")
    detected_anomalies = relationship("app.models.anomaly_models.DetectedAnomaly", back_populates="resolved")

    notifications = relationship("Notification", back_populates="recipient")
    escalation_rules = relationship("EscalationRule", back_populates="escalate_to")


class UserSessionLog(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    login_time = Column(DateTime, default=datetime.datetime.utcnow)
    logout_time = Column(DateTime, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    user = relationship("User", back_populates="sessions")

class RoleNames:
    ADMIN = "Admin"
    SUPERVISOR = "Supervisor"
    QA = "QA"
    MANAGER = "Manager"
    VENDOR = "Vendor"

