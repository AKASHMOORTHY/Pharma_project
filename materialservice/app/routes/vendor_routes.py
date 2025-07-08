# Pdms/materialservice/app/routes/vendor_routes.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..schemas.vendor_schema import Vendor, VendorCreate
from ..services import vendor_service
from ..dependencies import get_db

router = APIRouter(
    prefix="/vendors",
    tags=["Vendors"]
)

@router.post("/", response_model=Vendor)
def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    return vendor_service.create_vendor(db, vendor)

@router.get("/", response_model=list[Vendor])
def list_vendors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return vendor_service.get_vendors(db, skip, limit)
