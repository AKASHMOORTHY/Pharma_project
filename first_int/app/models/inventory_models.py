# app/models.py

from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from decimal import Decimal


class InventoryItem(Base):
    __tablename__ = 'inventory_items'

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey('raw_materials.id'))  # FK to raw_material table
    batch_code = Column(String(50), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)
    uom = Column(String(20), nullable=False)
    location = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # AVAILABLE, RESERVED, etc.
    expiry_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock_movements = relationship("StockMovement", back_populates="item")
    material = relationship("RawMaterial", back_populates="inventory_items")


class StockMovement(Base):
    __tablename__ = 'stock_movements'

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('inventory_items.id'))
    from_location = Column(String(100))
    to_location = Column(String(100))
    moved_by = Column(Integer, ForeignKey('users.id'),nullable=True,)  # placeholder for FK to user table
    timestamp = Column(DateTime, default=datetime.utcnow)
    quantity_moved = Column(DECIMAL(10, 2))
    purpose = Column(String(100))

    item = relationship("InventoryItem", back_populates="stock_movements")
    user = relationship("app.models.user_models.User", back_populates="stock_movements")


class Plant(Base):
    __tablename__ = 'plants'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100), nullable=False)
