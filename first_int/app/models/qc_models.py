from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


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

    performed_by_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    remarks = Column(String, nullable=True)
    attachment_filename = Column(String, nullable=True)

    # Replace source_type/source_id with relational fields
    production_batch_id = Column(Integer, ForeignKey("production_batches.id"), nullable=False)
    material_batch_id = Column(Integer, ForeignKey("material_batches.id"), nullable=False)

    production_batch = relationship("app.models.production_models.ProductionBatch", back_populates="qc_tests")
    material_batch = relationship("app.models.materials_models.MaterialBatch", back_populates="qc_tests")
    performed_by = relationship("app.models.user_models.User", back_populates="qc_tests")
    results = relationship("QCTestResult", back_populates="test")

class QCTestResult(Base):
    __tablename__ = "qc_test_results"
    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(String, ForeignKey("qc_tests.id"))
    parameter_id = Column(Integer, ForeignKey("qc_parameters.id"))
    observed_value = Column(Float)
    is_within_spec = Column(Boolean)
    
    test = relationship("QCTest", back_populates="results")
    anomaly_test = relationship("DetectedAnomaly", back_populates="test")
   
