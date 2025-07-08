# semi_finished_good.py

from sqlalchemy import Column, Integer, Float, String, Date
from ..base import Base

class SemiFinishedGood(Base):
    __tablename__ = "semi_finished_goods"

    #Auto-incrementing primary key
    id = Column(Integer, primary_key=True, index=True)

    #Name of the semi-finished product, eg. "MCC Wet"
    name = Column(String, nullable=False)

    #Quqntity on hand
    stock = Column(Float, default=0.0)

    #The date these figures apply to
    date = Column(Date, nullable=False)
