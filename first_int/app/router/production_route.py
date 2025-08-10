# app/routers/production_batch.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Generator

from app.crud import production_crud    
from app.schemas.production_schemas import ProductionBatchCreate, ProductionBatchResponse, StageLogResponse, StageLogCreate, StageLogUpdate, ProcessStageCreate, ProcessStageResponse

from app.database import SessionLocal
from app.auth import role_required, get_current_user
from app.models import user_models
from app.models.user_models import RoleNames


router = APIRouter(prefix="/api", tags=["ProductionBatch"])
    
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Role: Supervisor
@router.post("/production-batch")
def create_batch(batch: ProductionBatchCreate, db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR))
):
    batch_data = batch.dict()
    return production_crud.create_batch(db, batch_data)

# Role: Supervisor
@router.get("/production-batch", response_model=List[ProductionBatchResponse])
def get_batches(db: Session = Depends(get_db),  
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR))
    ):
    
    return production_crud.get_all_batches(db)

@router.post("/process-stage")
def create_process_stage(stage: ProcessStageCreate, db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR))
):
    return production_crud.create_process_stage(db, stage)


@router.get("/process-stage", response_model=List[ProcessStageResponse])
def get_process_stages(db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR))
):
    return production_crud.get_all_process_stages(db)

# app/routers/stage_log.py

# Role: Supervisor
@router.post("/stage-log")
def create_stage(
    log: StageLogCreate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR))
):
    return production_crud.create_stage_log(db, log)

# Role: Supervisor
@router.put("/stage-log/{log_id}")
def update_stage(
    log_id: int,
    log: StageLogUpdate,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.SUPERVISOR))
):
    return production_crud.update_stage_log(db, log_id, log)

# Role: Any authenticated user
@router.get("/stage-log/batch/{batch_code}/", response_model=List[StageLogResponse])
def get_logs_by_batch(
    batch_code: str,
    db: Session = Depends(get_db),
):
    return production_crud.get_stage_logs_by_batch(db, batch_code)