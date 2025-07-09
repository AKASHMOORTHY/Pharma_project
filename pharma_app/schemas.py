from pydantic import BaseModel
from datetime import date
from typing import Optional

class VendorBase(BaseModel):
    name: str
    contact_person: str
    contact_email: str
    gst_number: str

class RawMaterialBase(BaseModel):
    name: str
    code: str
    unit: str

class MaterialBatchBase(BaseModel):
    raw_material_id: int
    batch_code: str
    vendor_id: Optional[int] = None
    quantity_received: float  
    quantity_available: float
    received_date: date
    qc_status: str = "PENDING"
    remarks: Optional[str] = None

class QCUpdate(BaseModel):
    qc_status: str
    remarks: Optional[str] = None