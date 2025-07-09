# app/routers/inventory.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models, schemas
from app.utils import get_next_available_stock
from decimal import Decimal


router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1. Inward Entry
@router.post("/inward/", response_model=schemas.InventoryResponse)
def create_inventory_item(item: schemas.InventoryCreate, db: Session = Depends(get_db)):
    db_item = models.InventoryItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# 2. Stock Transfer
@router.post("/transfer/", response_model=schemas.StockMovementResponse)
def transfer_stock(movement: schemas.StockMovementCreate, db: Session = Depends(get_db)):
    inventory_item = db.query(models.InventoryItem).filter(
        models.InventoryItem.id == movement.item_id,
        models.InventoryItem.status != "REJECTED"
    ).first()

    if not inventory_item:
        raise HTTPException(status_code=404, detail="Item not found or rejected")

    if inventory_item.quantity < movement.quantity_moved:
        raise HTTPException(status_code=400, detail="Not enough quantity to move")

    inventory_item.location = movement.to_location
    db_movement = models.StockMovement(**movement.dict())
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement

# 3. Get by Batch Code
@router.get("/{batch_code}", response_model=list[schemas.InventoryResponse])
def get_inventory_by_batch(batch_code: str, db: Session = Depends(get_db)):
    items = db.query(models.InventoryItem).filter(
        models.InventoryItem.batch_code == batch_code
    ).all()

    if not items:
        raise HTTPException(status_code=404, detail="Batch not found")
    return items


@router.post("/consumption/")
def consume_inventory(material_id: int, quantity: Decimal, db: Session = Depends(get_db)):
    selected_batches = get_next_available_stock(db, material_id, quantity)

    if not selected_batches:
        raise HTTPException(status_code=404, detail="No available stock for this material")

    total_selected = sum(qty for _, qty in selected_batches)
    if total_selected < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock available")

    for item, qty in selected_batches:
        item.quantity -= qty
        if item.quantity == 0:
            item.status = "CONSUMED"
        db.add(item)

    db.commit()

    return {
        "message": "Stock consumed successfully using FIFO",
        "batches_used": [
            {
                "item_id": item.id,
                "batch_code": item.batch_code,
                "quantity_deducted": float(qty)
            }
            for item, qty in selected_batches
        ]
    }

@router.post("/adjust/")
def adjust_inventory(
    adjustment: schemas.StockAdjustmentRequest,
    db: Session = Depends(get_db)
):
    item = db.query(models.InventoryItem).filter(
        models.InventoryItem.id == adjustment.item_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    if adjustment.adjustment_type == "decrease":
        if item.quantity < adjustment.quantity:
            raise HTTPException(status_code=400, detail="Cannot reduce more than available stock")
        item.quantity -=Decimal(str(adjustment.quantity))

    elif adjustment.adjustment_type == "increase":
        item.quantity += Decimal(str(adjustment.quantity))

    else:
        raise HTTPException(status_code=400, detail="Invalid adjustment type")

    # Optional: Log the reason (you can create a separate Audit model later)
    db.add(item)
    db.commit()

    return {
        "message": "Stock adjusted successfully",
        "item_id": item.id,
        "new_quantity": float(item.quantity),
        "reason": adjustment.reason
    }
