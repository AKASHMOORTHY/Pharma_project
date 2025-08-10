from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    contact_person = Column(String(100))
    contact_email = Column(String(100))
    gst_number = Column(String(15))
    
    raw_materials = relationship("RawMaterial", back_populates="vendor")

class RawMaterial(Base):
    __tablename__ = "raw_materials"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    code = Column(String(10), unique=True)
    unit = Column(String(10))  # KG, Litre, etc.
    vendor_id = Column(Integer, ForeignKey("vendors.id"))

    vendor = relationship("Vendor", back_populates="raw_materials")
    batches = relationship("MaterialBatch", back_populates="raw_material")
    inventory_items = relationship("InventoryItem", back_populates="material")

class MaterialBatch(Base):
    __tablename__ = "material_batches"
    id = Column(Integer, primary_key=True, index=True)
    raw_material_id = Column(Integer, ForeignKey("raw_materials.id"))
    batch_code = Column(String(50), unique=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=True) 
    quantity_received = Column(Float)
    quantity_available = Column(Float)
    received_date = Column(Date)
    expiry_date = Column(Date)
    qc_status = Column(String(10), default="PENDING")  # PENDING, PASS, FAIL
    remarks = Column(String, nullable=True)

    created_by_id = Column(Integer, ForeignKey("users.id"))
    raw_material = relationship("RawMaterial", back_populates="batches")

    creator = relationship("app.models.user_models.User", back_populates="material_batches")
    production_batches = relationship("app.models.production_models.ProductionBatch", back_populates="batch")
    qc_tests = relationship("app.models.qc_models.QCTest", back_populates="material_batch")

# class QCRecord(Base):
#     __tablename__ = "qc_records"
#     id = Column(Integer, primary_key=True, index=True)
#     batch_id = Column(Integer, ForeignKey("material_batches.id"))
#     batch = relationship("MaterialBatch", back_populates="qc_records")