from sqlalchemy import Column, Integer, Float, Date
from ..base import Base

class PowerConsumption(Base):
    __tablename__ = "power_consumption"

    id = Column(Integer, primary_key=True, index=True)
    eb_power = Column(Float, default=0.0)
    dg_run_hours = Column(Float, default=0.0)
    diesel_consumption = Column(Float, default=0.0)
    date = Column(Date, nullable=False)      
