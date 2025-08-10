from fastapi import Depends, HTTPException, Query, UploadFile, File, Form, APIRouter
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud.qc_crud import create_qc_parameter, get_all_parameters, create_qc_test,get_test_by_id
from app.schemas.qc_schemas import QCParameterSchema, QCTestSchema, QCOverrideSchema, QCTestResultSchema, QCOverrideSchema
from datetime import timedelta,datetime
from app.models.qc_models import QCTestResult, QCTest, QCParameter
from typing import List
from app.models import user_models
from app.auth import role_required
from app.models.user_models import RoleNames


router = APIRouter(
    prefix="/api/qc",
    tags=["QC"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Role: Not enforced (see function body for manual checks if any)
@router.post("/parameters/", response_model=QCParameterSchema)
def add_param(param: QCParameterSchema, db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(role_required(RoleNames.ADMIN))):
    return create_qc_parameter(db, param)

# Role: Not enforced (see function body for manual checks if any)
@router.get("/parameters/", response_model=List[QCParameterSchema])
def list_params(db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.ADMIN))):
    return get_all_parameters(db)


# Role: Not enforced (see function body for manual checks if any)
@router.post("/tests/", response_model=QCTestSchema)
def log_test(test: QCTestSchema, db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(role_required(RoleNames.QA))):
    test_data = test.dict()
    test_data["performed_by_id"] = current_user.id
    return create_qc_test(db, test_data)

    # def log_test(test: QCTestSchema, db: Session = Depends(get_db)):
    # # if users.get(test.performed_by) != "QA":
    # #     raise HTTPException(status_code=403, detail="Only QA can log tests")
    # return create_qc_test(db, test)


# Role: Not enforced (see function body for manual checks if any)
@router.put("/tests/{test_id}", response_model=QCTestSchema)
def update_qc_test_json(
    test_id: str,
    payload: QCTestSchema,
    db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.QA))
):
    test = get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    if datetime.utcnow() - test.date > timedelta(hours=24):
        raise HTTPException(status_code=403, detail="Test entry locked after 24 hours")

    # Update remarks and attachment filename if provided
    test.remarks = payload.remarks or test.remarks
    test.attachment_filename = payload.attachment_filename or test.attachment_filename

    # Delete old results and insert new
    db.query(QCTestResult).filter(QCTestResult.test_id == test_id).delete()

    for r in payload.results:
        db_result = QCTestResult(
            test_id=test_id,
            parameter_id = r.parameter_id,
            observed_value = r.observed_value,
            is_within_spec = r.is_within_spec
        )
        db.add(db_result)

    db.commit()

    # Re-evaluate QC status
    from app.crud.qc_crud import evaluate_qc
    evaluate_qc(db, test_id)
    db.refresh(test)
    return test

# Role: Not enforced (see function body for manual checks if any)
@router.get("/tests/{test_id}", response_model=QCTestSchema)
def get_qc_test(test_id: str, db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.QA))
    ):
    test = get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

# Role: Not enforced (see function body for manual checks if any)
@router.get("/final-status/{source_id}")
def get_final_status(source_id: str, db: Session = Depends(get_db), 
    current_user: user_models.User = Depends(role_required(RoleNames.QA,RoleNames.MANAGER,RoleNames.SUPERVISOR,RoleNames.ADMIN))    
    ):
    tests = db.query(QCTest).filter(QCTest.source_id == source_id).all()
    if not tests:
        raise HTTPException(status_code=404, detail="No tests found for this source_id")

    # Final status is HOLD if any test is still on HOLD
    if any(test.status == "HOLD" for test in tests):
        return {"source_id": source_id, "final_status": "HOLD"}

    return {"source_id": source_id, "final_status": "PASS"}


# Role: Manager (manual check in function body)
@router.post("/override/", response_model=QCTestSchema)
def override_test(override_data: QCOverrideSchema, db: Session = Depends(get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.MANAGER))
    ):

    try:
        from app.crud.qc_crud import override_test_status
        test = override_test_status(db, override_data)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    return test
