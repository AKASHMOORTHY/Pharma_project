#process_waste.py

from sqlalchemy import Column, Integer, Float, String, Date
from ..base import Base

class ProcessWaste(Base):
    __tablename__ = "process_waste"

    id = Column(Integer, primary_key=True, index=True)
    waste_type = Column(String, nullable=False)  # e.g. “Wood Pulp Waste”
    quantity = Column(Float, default=0.0)        # amount in kg
    date = Column(Date, nullable=False)          # when it occurred
