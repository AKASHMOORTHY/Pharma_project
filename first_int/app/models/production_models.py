from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, DECIMAL, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class ProductionBatch(Base):
    __tablename__ = "production_batches"

    id = Column(Integer, primary_key=True)
    batch_code = Column(String(50), unique=True, index=True)
    date = Column(Date, nullable=False)
    shift = Column(String(2), nullable=False)  # "A", "B", or "C"

    stage_logs = relationship("StageLog", back_populates="production_batch")

    batch_id = Column(Integer, ForeignKey("material_batches.id"))
    operator_id = Column(Integer, ForeignKey("users.id"))    #created_by 


    batch = relationship("app.models.materials_models.MaterialBatch", back_populates="production_batches")
    operator = relationship("app.models.user_models.User", back_populates="production_batches")
    qc_tests = relationship("app.models.qc_models.QCTest", back_populates="production_batch")

class ProcessStage(Base):
    __tablename__ = "process_stages"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    stage_logs = relationship("StageLog", back_populates="stage")


class StageLog(Base):
    __tablename__ = "stage_logs"

    id = Column(Integer, primary_key=True)
    production_batch_id = Column(Integer, ForeignKey("production_batches.id"))
    stage_id = Column(Integer, ForeignKey("process_stages.id"))
    
    input_material_batch = Column(String(50))
    input_quantity = Column(DECIMAL(10, 2))
    output_quantity = Column(DECIMAL(10, 2))

    machine_id = Column(String(50))
    operator_name = Column(String(100))  # Keep for backward compatibility
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime)
    remarks = Column(Text, nullable=True)
    status = Column(String(50), nullable=False)

    is_locked = Column(Boolean, default=False)  

    production_batch = relationship("ProductionBatch", back_populates="stage_logs")
    stage = relationship("ProcessStage", back_populates="stage_logs")

