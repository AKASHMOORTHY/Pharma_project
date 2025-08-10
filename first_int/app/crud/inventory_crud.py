# utils.py

from sqlalchemy.orm import Session
from app.models.inventory_models import InventoryItem

def get_next_available_stock(db: Session, material_id: int, required_qty: float):
    """
    Fetches available stock batches using FIFO order based on created_at.
    Returns a list of (InventoryItem, quantity_taken) tuples.
    """
    available_items = db.query(InventoryItem).filter(
        InventoryItem.material_id == material_id,
        InventoryItem.status == "available"
    ).order_by(InventoryItem.created_at.asc()).all()

    selected_items = []
    qty_accumulated = 0

    for item in available_items:
        if qty_accumulated >= required_qty:
            break

        take_qty = min(item.quantity, required_qty - qty_accumulated)
        selected_items.append((item, take_qty))
        qty_accumulated += take_qty

    return selected_items
