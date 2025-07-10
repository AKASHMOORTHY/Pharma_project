from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from crud import create_qc_parameter, get_all_parameters, create_qc_test,get_test_by_id
from schemas import QCParameterSchema, QCTestSchema, QCOverrideSchema,QCTestResultSchema
from datetime import timedelta,datetime
from json import loads
from models import QCTestResult, QCTest
from fastapi.responses import JSONResponse
import os
import shutil


app = FastAPI()

users = {"qa1": "QA", "manager1": "Manager", "admin1": "Admin"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/qc/parameters/", response_model=QCParameterSchema)
def add_param(param: QCParameterSchema, db: Session = Depends(get_db)):
    return create_qc_parameter(db, param)

@app.get("/api/qc/parameters/", response_model=List[QCParameterSchema])
def list_params(db: Session = Depends(get_db)):
    return get_all_parameters(db)


@app.post("/api/qc/tests/", response_model=QCTestSchema)
def log_test(test: QCTestSchema, db: Session = Depends(get_db)):
    if users.get(test.performed_by) != "QA":
        raise HTTPException(status_code=403, detail="Only QA can log tests")
    return create_qc_test(db, test)

@app.put("/api/qc/tests/{test_id}", response_model=QCTestSchema)
def update_qc_test_json(
    test_id: str,
    payload: QCTestSchema,
    db: Session = Depends(get_db)
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
            parameter_id=r.parameter_id,
            observed_value=r.observed_value,
            is_within_spec=False
        )
        db.add(db_result)

    db.commit()

    # Re-evaluate QC status
    from utils import evaluate_qc
    evaluate_qc(db, test_id)
    db.refresh(test)
    return test

@app.get("/api/qc/tests/{test_id}", response_model=QCTestSchema)
def get_qc_test(test_id: str, db: Session = Depends(get_db)):
    test = get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@app.get("/api/qc/final-status/{source_id}")
def get_final_status(source_id: str, db: Session = Depends(get_db)):
    tests = db.query(QCTest).filter(QCTest.source_id == source_id).all()
    if not tests:
        raise HTTPException(status_code=404, detail="No tests found for this source_id")

    # Final status is HOLD if any test is still on HOLD
    if any(test.status == "HOLD" for test in tests):
        return {"source_id": source_id, "final_status": "HOLD"}

    return {"source_id": source_id, "final_status": "PASS"}


from schemas import QCOverrideSchema

@app.post("/api/qc/override/", response_model=QCTestSchema)
def override_test(override_data: QCOverrideSchema, db: Session = Depends(get_db)):
    # Check if user is Manager
    if users.get(override_data.overridden_by) != "Manager":
        raise HTTPException(status_code=403, detail="Only Managers can override test results")

    try:
        from crud import override_test_status
        test = override_test_status(db, override_data)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    return test
