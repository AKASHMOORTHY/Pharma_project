from sqlalchemy.orm import Session
from models import QCTest, QCTestResult, QCParameter

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