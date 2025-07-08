from sqlalchemy import Column, Integer, Float, String, Date
from ..base import Base

class RawMaterial(Base):
    __tablename__ = 'raw_materials'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    unit = Column(String, default="kg")
    opening_stock = Column(Float, default=0.0)
    receipts = Column(Float, default=0.0)
    issues = Column(Float, default=0.0)
    closing_stock = Column(Float, default=0.0)
    date = Column(Date)
