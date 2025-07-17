from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import Shift
from schemas import ShiftCreate, ShiftOut
from typing import List
from datetime import datetime
from fastapi import HTTPException

router = APIRouter()

@router.get("/", response_model=List[ShiftOut])
def get_shifts(db: Session = Depends(get_db)):
    return db.query(Shift).all()


@router.post("/", response_model=ShiftOut)
def create_shift(shift: ShiftCreate, db: Session = Depends(get_db)):
    try:
        # Convert strings to datetime.time objects
        start_time = datetime.strptime(shift.start_time, "%H:%M:%S").time()
        end_time = datetime.strptime(shift.end_time, "%H:%M:%S").time()

        db_shift = Shift(
            name=shift.name,
            start_time=start_time,
            end_time=end_time,
            supervisor_id=shift.supervisor_id
        )
        db.add(db_shift)
        db.commit()
        db.refresh(db_shift)
        return ShiftOut.from_orm_with_time(db_shift)


    except Exception as e:
        print("Error creating shift:", e)
        raise HTTPException(status_code=500, detail="Invalid shift data format.")

