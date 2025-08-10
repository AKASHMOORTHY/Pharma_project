from fastapi import APIRouter, Depends, HTTPException, APIRouter, Header
from typing import List
from app.schemas import materials_schemas 
from app.crud import materials_crud 
from app.models import materials_models, user_models 
from app.database import SessionLocal, engine
from sqlalchemy.orm import Session, joinedload
from app.auth import role_required
from app.models.user_models import RoleNames
from app.auth import get_current_user


router = APIRouter(
    prefix="/api",
    tags=["Raw_Materials"]
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Role: Admin
@router.post("/vendors/", response_model=materials_schemas.VendorBase)
def create_vendor(vendor: materials_schemas.VendorBase, 
db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.ADMIN))
    ):
    return materials_crud.create_vendor(db, vendor)


# Role: Any authenticated user
@router.get("/vendors/", response_model=List[materials_schemas.VendorBase])
def get_vendors(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.ADMIN))
):
    return materials_crud.get_all_vendors(db)

# Role: Admin
@router.post("/raw-materials/", response_model=materials_schemas.RawMaterialBase)
def create_raw_material(material: materials_schemas.RawMaterialBase, 
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.ADMIN))
    ):
    return materials_crud.create_raw_material(db, material)

# Role: Any authenticated user
@router.get("/raw-materials/", response_model=List[materials_schemas.RawMaterialBase])
def get_raw_materials(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.ADMIN))
):  
    if current_user.role is None:
        raise HTTPException(403, "Access denied: user has no role assigned.")

    if current_user.role.name not in ("Supervisor", "Admin"):
        raise HTTPException(403, f"Access denied: user role '{current_user.role.name}' not in allowed roles")

    return materials_crud.get_all_raw_materials(db)

# Role: Supervisor
@router.post("/material-batches/", response_model=materials_schemas.MaterialBatchBase)
def create_material_batch(batch: materials_schemas.MaterialBatchCreate, 
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR))
    ):
    if current_user.role is None:
        raise HTTPException(403, "Access denied: user has no role assigned.")

    if current_user.role.name not in ("Supervisor"):    
        raise HTTPException(403, f"Access denied: user role '{current_user.role.name}' not in allowed roles")

    # Set created_by_id automatically from the authenticated user
    batch_data = batch.dict()
    batch_data["created_by_id"] = current_user.id
    return materials_crud.create_material_batch(db, batch_data)

# Role: Any authenticated user
@router.get("/material-batches/", response_model=List[materials_schemas.MaterialBatchBase])
def get_material_batches(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR))
):
    if current_user.role is None:
        raise HTTPException(403, "Access denied: user has no role assigned.")

    if current_user.role.name not in ("Supervisor", "Admin"):
        raise HTTPException(403, f"Access denied: user role '{current_user.role.name}' not in allowed roles")

    return materials_crud.get_all_material_batches(db)


# Roles: Supervisor, Manager
@router.get("/inventory/", response_model=List[materials_schemas.MaterialBatchBase])
def read_inventory(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR,RoleNames.MANAGER))
):
    if current_user.role is None:
        raise HTTPException(403, "Access denied: user has no role assigned.")

    if current_user.role.name not in ("Supervisor", "Admin"):
        raise HTTPException(403, f"Access denied: user role '{current_user.role.name}' not in allowed roles")

    return materials_crud.get_inventory(db)


# Roles: Supervisor, Manager
@router.post("/materials/allocate/")
def allocate_material(
    material_id: int, 
    qty: float, 
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR, RoleNames.ADMIN))
):
    if current_user.role is None:
        raise HTTPException(403, "Access denied: user has no role assigned.")

    if current_user.role.name not in ("Supervisor", "Admin"):
        raise HTTPException(403, f"Access denied: user role '{current_user.role.name}' not in allowed roles")

    result = materials_crud.allocate_material(db, material_id, qty)

    if not result["allocated"]:
        raise HTTPException(400, "Insufficient stock")

    return {"message": "Allocation successful"}


# Roles: Supervisor, Manager
@router.get("/materials/low-stock/")
def check_low_stock(
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR, RoleNames.ADMIN))
):
    if current_user.role is None:
        raise HTTPException(403, "Access denied: user has no role assigned.")

    if current_user.role.name not in ("Supervisor", "Admin"):
        raise HTTPException(403, f"Access denied: user role '{current_user.role.name}' not in allowed roles")
    return materials_crud.get_low_stock_items(db)


# # Enhanced QC Update
# @router.post("/material-batches/{batch_id}/qc/")
# def update_qc(
#     batch_id: int, 
#     qc_data: materials_schemas.QCUpdate, 
#     db: Session = Depends(get_db),
#     current_user: user_models.User = Depends(role_required(RoleNames.QA))
# ):
#     if current_user.role is None:
#         raise HTTPException(403, "Access denied: user has no role assigned.")

#     if current_user.role.name not in ("QA",):
#         raise HTTPException(403, f"Access denied: user role '{current_user.role.name}' not in allowed roles")

#     return materials_crud.update_qc_status(db, batch_id, qc_data.moisture, qc_data.foreign_matter)
