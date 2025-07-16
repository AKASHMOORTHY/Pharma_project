from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from .database import Base

class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    contact_person = Column(String(100))
    contact_email = Column(String(100))
    gst_number = Column(String(15))

class RawMaterial(Base):
    __tablename__ = "raw_materials"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    code = Column(String(10), unique=True)
    unit = Column(String(10))  # KG, Litre, etc.

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