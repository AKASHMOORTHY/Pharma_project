from fastapi import FastAPI
from db import Base, engine, get_db
from routers import users, shifts, qc_params, rules, preferences
from models import Shift
from schemas import ShiftCreate, ShiftOut

app = FastAPI(title="Admin & Configuration Management API")

# Create all DB tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router, prefix="/api/admin/users", tags=["Users"])
app.include_router(shifts.router, prefix="/api/admin/shifts", tags=["Shifts"])
app.include_router(qc_params.router, prefix="/api/admin/qc-params", tags=["QC Parameters"])
app.include_router(rules.router, prefix="/api/admin/rules", tags=["Rules"])
app.include_router(preferences.router, prefix="/api/admin/preferences", tags=["Preferences"])

@app.get("/")
def root():
    return {"message": "Welcome to Admin & Configuration Management API"}
