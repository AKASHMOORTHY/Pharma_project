from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class QCParameter(Base):
    __tablename__ = "qc_parameters"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    material = Column(String)
    name = Column(String)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    unit = Column(String)

class QCTest(Base):
    __tablename__ = "qc_tests"
    id = Column(String, primary_key=True, index=True)
    source_type = Column(String)
    source_id = Column(String)
    performed_by = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    remarks = Column(String, nullable=True)
    attachment_filename = Column(String, nullable=True)
    results = relationship("QCTestResult", back_populates="test")

class QCTestResult(Base):
    __tablename__ = "qc_test_results"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String, ForeignKey("qc_tests.id"))
    parameter_id = Column(Integer, ForeignKey("qc_parameters.id"))
    observed_value = Column(Float)
    is_within_spec = Column(Boolean)
    test = relationship("QCTest", back_populates="results")
