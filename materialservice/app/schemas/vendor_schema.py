# Pdms/materialservice/app/schemas/vendor_schema.py

from pydantic import BaseModel, ConfigDict

class VendorBase(BaseModel):
    name: str
    contact_info: str

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
