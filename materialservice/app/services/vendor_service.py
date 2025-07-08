# Pdms/materialservice/app/services/vendor_service.py

from sqlalchemy.orm import Session
from ..models.vendor import Vendor
from ..schemas.vendor_schema import VendorCreate

def create_vendor(db: Session, vendor: VendorCreate):
    db_vendor = Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def get_vendors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Vendor).offset(skip).limit(limit).all()
