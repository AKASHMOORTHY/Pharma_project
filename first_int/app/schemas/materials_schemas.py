from pydantic import BaseModel, ConfigDict, Field, validator
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
    vendor_id: int

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
    expiry_date: date  # New
    qc_status: str = "PENDING"
    remarks: Optional[str] = None

class MaterialBatchBase(MaterialBatchCreate):
    id: int
    created_by_id: int  # Only in response, not in request
    model_config = ConfigDict(from_attributes=True)

# class QCUpdate(BaseModel):
#     moisture: float = Field(..., ge=0, le=100)  # 0-100%
#     foreign_matter: str = Field(..., pattern="^(None|Sand|Dust|Metal)$")  # Allowed values
    
#     @validator('moisture')
#     def validate_moisture(cls, v):
#         if v < 4 or v > 6:
#             raise ValueError("Moisture must be 4-6% for MCC")
#         return v
