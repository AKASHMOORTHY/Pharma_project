from pydantic import BaseModel, ConfigDict
from datetime import datetime

class MaterialBatchBase(BaseModel):
    batch_code: str
    material_type: str
    vendor_id: int
    quantity_kg: float

class MaterialBatchCreate(MaterialBatchBase):
    pass

class MaterialBatch(MaterialBatchBase):
    id: int
    received_date: datetime

    model_config = ConfigDict(from_attributes=True)
