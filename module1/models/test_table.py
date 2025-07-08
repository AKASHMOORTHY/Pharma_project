from sqlalchemy import Column, Integer, String
from ..base import Base

class TestTable(Base):
    __tablename__ = 'test_table'
    id = Column(Integer, primary_key=True)
    name = Column(String)
