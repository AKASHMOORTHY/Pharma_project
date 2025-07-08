from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..db import Base

class MaterialBatch(Base):
    __tablename__ = "material_batches"

    id = Column(Integer, primary_key=True, index=True)
    batch_code = Column(String, unique=True, index=True)
    material_type = Column(String)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    quantity_kg = Column(Float)
    received_date = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="batches")
