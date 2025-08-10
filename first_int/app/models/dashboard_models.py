from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Date, Text, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class DashboardProductionBatch(Base):
    __tablename__ = "dashboard_production"
    id = Column(Integer, primary_key=True)
    shift = Column(String)
    status = Column(String)
    duration = Column(Float)
    production_date = Column(DateTime, default=datetime.utcnow)

class QualityCheck(Base):
    __tablename__ = "dashboard_quality_check"
    id = Column(Integer, primary_key=True)
    result = Column(String)  # 'Pass' or 'Fail'
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Inventory(Base):
    __tablename__ = "dashboard_inventory"
    id = Column(Integer, primary_key=True)
    material = Column(Integer)
    quantity = Column(DECIMAL(10, 2))
    status = Column(String)
    location = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Anomaly(Base):
    __tablename__ = "dashboard_anomalies"
    id = Column(Integer, primary_key=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)    
    resolved_at = Column(DateTime, nullable=True)

