from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, DECIMAL
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ProductionBatch(Base):
    __tablename__ = "production_batches"
    id = Column(Integer, primary_key=True)
    batch_code = Column(String, unique=True, index=True)
    date = Column(Date)
    shift = Column(String)
    created_by = Column(String)  # Simplified: string instead of ForeignKey to User

class ProcessStage(Base):
    __tablename__ = "process_stages"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class StageLog(Base):
    __tablename__ = "stage_logs"
    id = Column(Integer, primary_key=True)
    production_batch_id = Column(Integer, ForeignKey("production_batches.id"))
    stage_id = Column(Integer, ForeignKey("process_stages.id"))
    input_material_batch = Column(String)  # Simplified
    input_quantity = Column(DECIMAL(10, 2))
    output_quantity = Column(DECIMAL(10, 2))
    machine_id = Column(String)
    operator_name = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    remarks = Column(Text, nullable=True)
    is_locked = Column(Integer, default=0)

    production_batch = relationship("ProductionBatch")
    stage = relationship("ProcessStage")
