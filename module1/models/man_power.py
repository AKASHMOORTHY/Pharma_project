#man_power.py

from sqlalchemy import Column, Integer, String, Date
from ..base import Base

class ManPower(Base):
    __tablename__ = "man_power"

    id    = Column(Integer, primary_key=True, index=True)
    role  = Column(String, nullable=False)   # e.g. “Operator”
    shift = Column(String, nullable=False)   # e.g. “G”, “A”, “B”, “C”
    count = Column(Integer, default=0)       # number of people
    date  = Column(Date, nullable=False)     # snapshot date
