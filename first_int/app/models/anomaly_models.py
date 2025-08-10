# app/models/anomaly_models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class AnomalyRule(Base):
    __tablename__ = 'anomaly_rules'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    source_table = Column(String(100))
    field_name = Column(String(100))
    condition = Column(String(50))  # e.g., outside_min_max
    severity = Column(String(20))  # low, medium, high
    is_active = Column(Boolean, default=True)
    notify_roles = Column(String(255))  # comma-separated: 'Manager,QA'

    rules = relationship("DetectedAnomaly", back_populates="rule")

class DetectedAnomaly(Base):
    __tablename__ = 'detected_anomalies'

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey("qc_test_results.id"), nullable=True) 
    rule_id = Column(Integer, ForeignKey('anomaly_rules.id'))
    source_id = Column(String(100))
    detected_at = Column(DateTime, server_default=func.now())
    status = Column(String(20), default='open')  # open, resolved, ignored
    severity = Column(String(20))
    description = Column(Text)
    resolved_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    resolved_at = Column(DateTime, nullable=True)

    rule = relationship("AnomalyRule", back_populates="rules" )
    test = relationship("QCTestResult", back_populates = "anomaly_test")
    resolved = relationship("app.models.user_models.User", back_populates="detected_anomalies")
