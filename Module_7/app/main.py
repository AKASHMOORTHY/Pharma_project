from fastapi import FastAPI
from app.database import engine, Base
from app.router import production, qc, inventory, anomalies, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dashboard & Reporting System")

app.include_router(production.router)
app.include_router(qc.router)
app.include_router(inventory.router)
app.include_router(anomalies.router)
app.include_router(reports.router)
