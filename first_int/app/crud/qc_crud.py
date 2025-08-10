from sqlalchemy.orm import Session
from app.models.qc_models import QCParameter, QCTest, QCTestResult
from app.schemas.qc_schemas import QCParameterSchema, QCTestSchema, QCTestResultSchema, QCOverrideSchema
from uuid import uuid4
from datetime import datetime,timedelta


def create_qc_parameter(db: Session, param: QCParameterSchema):
    db_param = QCParameter(**param.dict())
    db.add(db_param)
    db.commit()
    db.refresh(db_param)
    return db_param


def get_all_parameters(db: Session):
    return db.query(QCParameter).all()


def create_qc_test(db: Session, test_data: dict):
    test_id = str(uuid4())
    db_test = QCTest(
        id=test_id,
        source_type=test_data["source_type"],
        source_id=test_data["source_id"],
        performed_by_id=test_data["performed_by_id"],
        status="HOLD",  # initial, updated after evaluation
        remarks=test_data.get("remarks"),
        attachment_filename=test_data.get("attachment_filename"),
        production_batch_id=test_data.get("production_batch_id"),
        material_batch_id=test_data.get("material_batch_id")
    )
    db.add(db_test)
    db.commit()

    for r in test_data["results"]:
        db_result = QCTestResult(
            test_id=test_id,
            parameter_id=r["parameter_id"],
            observed_value=r["observed_value"],
            is_within_spec=False  # updated in eval
        )
        db.add(db_result)
    db.commit()

    evaluate_qc(db, test_id)
    return db.query(QCTest).filter(QCTest.id == test_id).first()


def get_test_by_id(db: Session, test_id: str):
    return db.query(QCTest).filter(QCTest.id == test_id).first()

def override_test_status(db: Session, override_data: QCOverrideSchema):
    test = db.query(QCTest).filter(QCTest.id == override_data.test_id).first()
    if not test:
        return None

    if datetime.utcnow() - test.date > timedelta(hours=24):
        raise Exception("Test entry locked after 24 hours")

    test.status = override_data.new_status
    test.remarks = (test.remarks or '') + f"\n[Overridden by Manager]: {override_data.comment}"
    db.commit()
    return test



def evaluate_qc(db: Session, test_id: str):
    test = db.query(QCTest).filter(QCTest.id == test_id).first()
    results = db.query(QCTestResult).filter(QCTestResult.test_id == test_id).all()

    failed = False
    for r in results:
        param = db.query(QCParameter).filter(QCParameter.id == r.parameter_id).first()
        if param.min_value is not None and r.observed_value < param.min_value:
            r.is_within_spec = False
            failed = True
        elif param.max_value is not None and r.observed_value > param.max_value:
            r.is_within_spec = False
            failed = True
        else:
            r.is_within_spec = True
    test.status = "PASS" if not failed else "HOLD"
    db.commit()


def update_qc_test(
    db: Session,
    test_id: str,
    remarks: str,
    attachment_filename: str,
    results: list[QCTestResultSchema]
):
    test = db.query(QCTest).filter(QCTest.id == test_id).first()
    if not test:
        return None

    if datetime.utcnow() - test.date > timedelta(hours=24):
        raise Exception("Test entry locked after 24 hours")

    test.remarks = remarks
    test.attachment_filename = attachment_filename

    db.query(QCTestResult).filter(QCTestResult.test_id == test_id).delete()

    for r in results:
        db_result = QCTestResult(
            test_id=test_id,
            parameter_id=r.parameter_id,
            observed_value=r.observed_value,
            is_within_spec=False
        )
        db.add(db_result)

    db.commit()
    evaluate_qc(db, test_id)
    db.refresh(test)
    return test

