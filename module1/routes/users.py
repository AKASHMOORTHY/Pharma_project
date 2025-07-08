from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

# climb out of routes/ into the package root:
from ..database          import get_db
from ..services.user_service import get_user, create_user
from ..schemas.user      import UserCreate, UserOut

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get("/{user_id}", response_model=UserOut)
def read_user(user_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserOut)
def add_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user_in)
