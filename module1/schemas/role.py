# schemas/role.py
from pydantic import BaseModel

class RoleOut(BaseModel):
    id: int
    name: str
    description: str | None = None

    class Config:
        from_attributes = True
