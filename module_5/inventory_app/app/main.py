from fastapi import FastAPI
from app.routers import inventory
from app import models
from app.database import Base,engine
app = FastAPI(title="Inventory & Material Movement API")

# Base.metadata.create_all(bind=engine)


app.include_router(inventory.router)  