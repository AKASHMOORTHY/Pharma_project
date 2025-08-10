from sqlalchemy.orm import Session
from app.models import materials_models
from app.schemas.materials_schemas import VendorBase, RawMaterialBase, MaterialBatchBase
from fastapi import HTTPException

# Vendor operations
def create_vendor(db: Session, vendor: VendorBase):
    db_vendor = materials_models.Vendor(**vendor.dict())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor

def get_vendor_by_id(db: Session, vendor_id: int):
    return db.query(materials_models.Vendor).filter(materials_models.Vendor.id == vendor_id).first()

def delete_vendor(db: Session, vendor_id: int):
    db_vendor = db.query(materials_models.Vendor).filter(materials_models.Vendor.id == vendor_id).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.delete(db_vendor)
    db.commit()
    return db_vendor

# Raw Material operations
def create_raw_material(db: Session, material: RawMaterialBase):
    db_material = materials_models.RawMaterial(**material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

# Batch operations
def create_material_batch(db: Session, batch: dict):
    db_batch = materials_models.MaterialBatch(**batch)
    db.add(db_batch)
    db.commit()
    db.refresh(db_batch)
    return db_batch


def get_inventory(db: Session):
    return db.query(materials_models.MaterialBatch).filter(
        materials_models.MaterialBatch.qc_status == "PASS",
        materials_models.MaterialBatch.quantity_available >= 0
    ).all()

def get_all_vendors(db: Session):
    return db.query(materials_models.Vendor).all()

def get_all_raw_materials(db: Session):
    return db.query(materials_models.RawMaterial).all()

def get_all_material_batches(db: Session):
    return db.query(materials_models.MaterialBatch).all()


from sqlalchemy import func

def allocate_material(db: Session, material_id: int, required_qty: float):
    # Get oldest PASSED batches first (FIFO)
    batches = (
        db.query(materials_models.MaterialBatch)
        .filter(
            materials_models.MaterialBatch.raw_material_id == material_id,
            materials_models.MaterialBatch.qc_status == "PASS",
            materials_models.MaterialBatch.quantity_available > 0
        )
        .order_by(materials_models.MaterialBatch.received_date)
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


def get_low_stock_items(db: Session):
    # Raw materials where available stock < reorder_level
    low_stock = (
        db.query(materials_models.RawMaterial)
        .join(materials_models.MaterialBatch)
        .group_by(materials_models.RawMaterial.id)
        .having(func.sum(materials_models.MaterialBatch.quantity_available) < 50)
        .all()
    )
    return low_stock    