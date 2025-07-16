from sqlalchemy.orm import Session
from .models import Vendor, RawMaterial, MaterialBatch
from .schemas import VendorBase, RawMaterialBase, MaterialBatchBase, QCUpdate  
from fastapi import HTTPException

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


from sqlalchemy import func

def allocate_material(db: Session, material_id: int, required_qty: float):
    # Get oldest PASSED batches first (FIFO)
    batches = (
        db.query(MaterialBatch)
        .filter(
            MaterialBatch.raw_material_id == material_id,
            MaterialBatch.qc_status == "PASS",
            MaterialBatch.quantity_available > 0
        )
        .order_by(MaterialBatch.received_date)
        .all()
    )
    
    # Deduct quantities
    for batch in batches:
        if required_qty <= 0:
            break
        alloc_qty = min(batch.quantity_available, required_qty)
        batch.quantity_available -= alloc_qty
        required_qty -= alloc_qty
    
    db.commit()
    return {"allocated": required_qty == 0}

def update_qc_status(db: Session, batch_id: int, moisture: float, foreign_matter: str):
    batch = db.query(MaterialBatch).get(batch_id)
    if not batch:
        raise HTTPException(404, detail="Batch not found")
    
    # Auto-determine status (from PDF rules)
    if moisture < 4 or moisture > 6 or foreign_matter != "None":
        batch.qc_status = "FAIL"
    else:
        batch.qc_status = "PASS"
    
    db.commit()
    return batch

def get_low_stock_items(db: Session):
    # Raw materials where available stock < reorder_level
    low_stock = (
        db.query(RawMaterial)
        .join(MaterialBatch)
        .group_by(RawMaterial.id)
        .having(func.sum(MaterialBatch.quantity_available) < RawMaterial.reorder_level)
        .all()
    )
    return low_stock