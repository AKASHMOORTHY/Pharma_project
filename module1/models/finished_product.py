from sqlalchemy import Column, Integer, Float, String, Date
from ..base import Base

class FinishedProduct(Base):
    __tablename__ = "finished_products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    opening_stock = Column(Float, default=0.0)
    produced = Column(Float, default=0.0)
    despatched = Column(Float, default=0.0)
    closing_stock = Column(Float, default=0.0)
    date = Column(Date, nullable=False)
