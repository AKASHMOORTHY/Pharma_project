from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class InventoryBase(BaseModel):
    material_id: int
    batch_code: str
    quantity: float
    uom: str
    location: str
    status: str  # AVAILABLE, RESERVED, etc.
    expiry_date: Optional[date]

class InventoryCreate(InventoryBase):
    pass

class InventoryResponse(InventoryBase):
    id: int
    material_id: int
    batch_code: str
    location: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class StockMovementBase(BaseModel):
    item_id: int
    from_location: str
    to_location: str
    quantity_moved: float
    purpose: str
    moved_by: Optional[int] = None  # You can later relate this to user_id

class StockMovementCreate(StockMovementBase):
    pass

class StockMovementResponse(StockMovementBase):
    id: int
    from_location: str
    to_location: str
    quantity_moved: float
    purpose: str
    timestamp: datetime

    class Config:
        from_attributes = True

class StockAdjustmentRequest(BaseModel):
    item_id: int
    adjustment_type: str  # increase or decrease
    quantity: float
    reason: str

class PlantCreate(BaseModel):
    name: str
    location: str

class PlantResponse(BaseModel):
    id: int
    name: str
    location: str
