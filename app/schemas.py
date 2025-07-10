from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class VendorCreate(BaseModel):
    name: str
    contact_person: str
    contact_email: str
    gst_number: str

class VendorBase(VendorCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class RawMaterialCreate(BaseModel):
    name: str
    code: str
    unit: str

class RawMaterialBase(RawMaterialCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class MaterialBatchCreate(BaseModel):
    raw_material_id: int
    batch_code: str
    vendor_id: Optional[int] = None
    quantity_received: float
    quantity_available: float
    received_date: date
    qc_status: str = "PENDING"
    remarks: Optional[str] = None

class MaterialBatchBase(MaterialBatchCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

class QCUpdate(BaseModel):
    qc_status: str
    remarks: Optional[str] = None
