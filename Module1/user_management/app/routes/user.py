# app/routes/user.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from user_management.app.utils.shift import is_within_shift
from user_management.app.utils.security import hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm
from user_management.app import models, auth,schemas,crud
from typing import List
from user_management.app.models import UserSessionLog, RoleNames
from starlette.requests import  Request
from user_management.app.auth import role_required
from user_management.app.schemas import PasswordChangeRequest



router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"]
)
 
@router.post("/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db), ):
    user = db.query(models.User).filter(models.User.email == form_data.username,models.User.is_active == True).first()    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    session_log = UserSessionLog(
        user_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    db.add(session_log)
    db.commit()
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=schemas.UserOut)
def get_profile(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

def is_admin(user):
    return user.role and user.role.name == "Admin"

@router.get("/users/", response_model=List[schemas.UserOut])
def get_users(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(role_required(RoleNames.ADMIN))
):
    return crud.get_all_users(db)

@router.post("/users/", response_model=schemas.UserOut)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(role_required(RoleNames.ADMIN))
):
    return crud.create_user(db, user)

@router.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=schemas.UserOut)
def update_user(user_id: int, updates: schemas.UserUpdate, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db, db_user, updates)

@router.delete("/users/{user_id}", response_model=schemas.UserOut)
def delete_user(user_id: int, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db, db_user)

@router.post("/some-data-entry")
def restricted_entry(current_user: models.User = Depends(auth.get_current_user)):
    if not is_within_shift(current_user.shift):
        raise HTTPException(status_code=403, detail="Access outside assigned shift is denied.")
    return {"message": "Data accepted for shift."}

@router.post("/logout")
def logout(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(auth.get_db)
):
    session_log = (
        db.query(models.UserSessionLog)
        .filter(models.UserSessionLog.user_id == current_user.id)
        .order_by(models.UserSessionLog.login_time.desc())
        .first()
    )
    if session_log and session_log.logout_time is None:
        session_log.logout_time = datetime.utcnow()
        db.commit()
    return {"message": "Logout recorded"}

@router.post("/change-password")
def change_password(
    data: PasswordChangeRequest,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@router.put("/users/{user_id}/update-role-shift")
def update_role_shift(
    user_id: int,
    updates: schemas.UserUpdate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(role_required(RoleNames.ADMIN))
):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db, user, updates)


