from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from db import Base

class ProductionBatch(Base):
    __tablename__ = "production_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_code = Column(String, unique=True, index=True)
    date = Column(Date)
    shift = Column(String)
    created_by = Column(Integer)  # Optionally FK to User table

    stage_logs = relationship("StageLog", back_populates="production_batch")
