# fastapi_project/main.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
# Database setup
from .database import get_db, engine
from .base import Base
# Ensure all models are registered with SQLAlchemy
from . import models  # noqa: F401
# Service functions & Pydantic schemas
from .services.user_service import get_user, create_user
from .schemas.user import UserCreate, UserOut
# Routers
from .routes.auth import router as auth_router
from .routes.users import router as users_router
from materialservice.app.routes.material_routes import router as material_router
from materialservice.app.routes.vendor_routes   import router as vendor_router



app = FastAPI(debug=True)


@app.on_event("startup")
def create_tables():
    """
    On startup, create any missing tables.
    """
    Base.metadata.create_all(bind=engine)


# Mount your routers
app.include_router(auth_router)
app.include_router(users_router)



# include the merged Material & Vendor routes
app.include_router(
    material_router,
    prefix="/materials",
    tags=["Materials"],
)
app.include_router(
    vendor_router,
    prefix="/vendors",
    tags=["Vendors"],
)


@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "Welcome to FastAPI"}
