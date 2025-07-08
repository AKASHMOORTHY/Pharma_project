# main.py

from fastapi import FastAPI
from routes import material_routes, vendor_routes

app = FastAPI()

app.include_router(material_routes.router)
app.include_router(vendor_routes.router)
