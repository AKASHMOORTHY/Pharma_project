from fastapi import FastAPI
from app.models import user_models, materials_models, qc_models, inventory_models, production_models, anomaly_models, dashboard_models, escalation_models
from app.router import user_route, materials_route, qc_route, inventory_route, production_route, anomaly_route, dashboard_route, escalation_route
from app.database import SessionLocal, engine


user_models.Base.metadata.create_all(bind=engine)
materials_models.Base.metadata.create_all(bind=engine)
production_models.Base.metadata.create_all(bind=engine)
qc_models.Base.metadata.create_all(bind=engine)
inventory_models.Base.metadata.create_all(bind=engine)
anomaly_models.Base.metadata.create_all(bind=engine)
dashboard_models.Base.metadata.create_all(bind=engine)
escalation_models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_route.router)
app.include_router(materials_route.router)
app.include_router(production_route.router)
app.include_router(qc_route.router)
app.include_router(inventory_route.router)
app.include_router(anomaly_route.router)
app.include_router(dashboard_route.router)
app.include_router(escalation_route.router)
