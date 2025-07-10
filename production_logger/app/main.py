from fastapi import FastAPI
from app.routers import production_batch, stage_log

app = FastAPI()

app.include_router(production_batch.router, prefix="/api/production-batch", tags=["ProductionBatch"])
app.include_router(stage_log.router, prefix="/api/stage-log", tags=["StageLog"])
