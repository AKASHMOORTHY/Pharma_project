# schemas/user.py
from pydantic import BaseModel
from .role import RoleOut  # 👈 import RoleOut schema

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str | None = None
    role: str  # Role name (not object)

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    role: RoleOut  # 👈 expects nested RoleOut

    class Config:
        from_attributes = True  # or orm_mode = True if using Pydantic v1
