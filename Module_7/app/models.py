from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class ProductionBatch(Base):
    __tablename__ = "production_batch"
    id = Column(Integer, primary_key=True)
    shift = Column(String)
    status = Column(String)
    duration = Column(Float)
    production_date = Column(DateTime, default=datetime.utcnow)

class QualityCheck(Base):
    __tablename__ = "quality_check"
    id = Column(Integer, primary_key=True)
    result = Column(String)  # 'Pass' or 'Fail'
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True)
    material = Column(String)
    quantity = Column(Integer)
    category = Column(String)
    location = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(Integer, primary_key=True)
    category = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
