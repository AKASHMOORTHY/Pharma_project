from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship
from db import Base

class StageLog(Base):
    __tablename__ = "stage_logs"

    id = Column(Integer, primary_key=True, index=True)
    production_batch_id = Column(Integer, ForeignKey("production_batches.id"))
    stage_id = Column(Integer, ForeignKey("process_stages.id"))
    input_quantity = Column(Float)
    output_quantity = Column(Float)
    machine_id = Column(String)
    operator_name = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    remarks = Column(Text, nullable=True)

    production_batch = relationship("ProductionBatch", back_populates="stage_logs")
    stage = relationship("ProcessStage")
