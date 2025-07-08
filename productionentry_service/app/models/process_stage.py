from sqlalchemy import Column, Integer, String
from db import Base

class ProcessStage(Base):
    __tablename__ = "process_stages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
