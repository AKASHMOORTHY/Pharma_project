from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import schemas, crud, models
from .database import SessionLocal, engine
from fastapi import Header, HTTPException


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Vendor Endpoints
@app.post("/vendors/", response_model=schemas.VendorBase)
def create_vendor(vendor: schemas.VendorBase, db: Session = Depends(get_db)):
    return crud.create_vendor(db, vendor)


@app.get("/api/vendors/", response_model=List[schemas.VendorBase])
def get_vendors(
    db: Session = Depends(get_db),
    x_role: str = Header(default="user")
):
    if x_role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view vendors")
    return crud.get_all_vendors(db)

# Raw Material Endpoints
@app.post("/raw-materials/", response_model=schemas.RawMaterialBase)
def create_raw_material(material: schemas.RawMaterialBase, db: Session = Depends(get_db)):
    return crud.create_raw_material(db, material)

@app.get("/api/raw-materials/", response_model=List[schemas.RawMaterialBase])
def get_raw_materials(
    db: Session = Depends(get_db),
    x_role: str = Header(default="user")
):
    if x_role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only admin can view raw materials")
    return crud.get_all_raw_materials(db)

# Batch Endpoints
@app.post("/material-batches/", response_model=schemas.MaterialBatchBase)
def create_material_batch(batch: schemas.MaterialBatchBase, db: Session = Depends(get_db)):
    return crud.create_material_batch(db, batch)

@app.get("/api/material-batches/", response_model=List[schemas.MaterialBatchBase])
def get_material_batches(
    db: Session = Depends(get_db),
    x_role: str = Header(default="user")
):
    if x_role.lower() != "supervisor":
        raise HTTPException(status_code=403, detail="Only supervisors can view material batches")
    return crud.get_all_material_batches(db)

@app.post("/material-batches/{batch_id}/qc/")
def update_qc_status(batch_id: int, qc_update: schemas.QCUpdate, db: Session = Depends(get_db)):
    return crud.update_qc_status(db, batch_id, qc_update)

# Inventory Endpoint
@app.get("/inventory/", response_model=List[schemas.MaterialBatchBase])
def read_inventory(db: Session = Depends(get_db)):
    return crud.get_inventory(db)