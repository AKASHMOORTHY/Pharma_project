from sqlalchemy.orm import Session
from .models import Vendor, RawMaterial, MaterialBatch
from .schemas import VendorBase, RawMaterialBase, MaterialBatchBase, QCUpdate  

# Vendor operations
def create_vendor(db: Session, vendor: VendorBase):
    db_vendor = Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

# Raw Material operations
def create_raw_material(db: Session, material: RawMaterialBase):
    db_material = RawMaterial(**material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

# Batch operations
def create_material_batch(db: Session, batch: MaterialBatchBase):
    db_batch = MaterialBatch(**batch.dict())
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch

def update_qc_status(db: Session, batch_id: int, qc_update: QCUpdate):
    db_batch = db.query(MaterialBatch).filter(MaterialBatch.id == batch_id).first()
    if db_batch:
        db_batch.qc_status = qc_update.qc_status
        db_batch.remarks = qc_update.remarks
        db.commit()
        db.refresh(db_batch)
    return db_batch

def get_inventory(db: Session):
    return db.query(MaterialBatch).filter(
        MaterialBatch.qc_status == "PASS",
        MaterialBatch.quantity_available > 0
    ).all()

def get_all_vendors(db: Session):
    return db.query(Vendor).all()

def get_all_raw_materials(db: Session):
    return db.query(RawMaterial).all()

def get_all_material_batches(db: Session):
    return db.query(MaterialBatch).all()
