from sqlalchemy import Column, Integer, String, Boolean, Time, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from db import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True)
    phone = Column(String(15))
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role")

class Shift(Base):
    __tablename__ = "shifts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    start_time = Column(Time)
    end_time = Column(Time)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=True)

class Plant(Base):
    __tablename__ = "plants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    location = Column(String(100))

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    code = Column(String(20), unique=True)
    description = Column(Text)

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    code = Column(String(20), unique=True)
    uom = Column(String(10))

class Machine(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    serial_number = Column(String(50), unique=True)
    location = Column(String(100))

class QCParameter(Base):
    __tablename__ = "qc_parameters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    product_id = Column(Integer, ForeignKey("products.id"))
    min_value = Column(DECIMAL(6, 2))
    max_value = Column(DECIMAL(6, 2))
    unit = Column(String(20))

class AnomalyRule(Base):
    __tablename__ = "anomaly_rules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    condition = Column(Text)
    severity = Column(String(10))
    active = Column(Boolean, default=True)

class SystemPreference(Base):
    __tablename__ = "system_preferences"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True)
    value = Column(Text)
    description = Column(Text, default="")
