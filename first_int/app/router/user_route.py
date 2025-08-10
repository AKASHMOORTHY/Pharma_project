# app/routes/user.py
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.utils.shift import is_within_shift
from app.utils.security import hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm
from app import auth
from app.models import user_models
from app.models.user_models import User, UserSessionLog, RoleNames
from app.schemas import user_schemas
from app.crud import user_crud
from app.auth import role_required
from app.schemas.user_schemas import PasswordChangeRequest
from typing import List


router = APIRouter(
    prefix="/api/auth",     
    tags=["Auth"]
)

# Role: Any authenticated user
@router.post("/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db), ):
    user = db.query(User).filter(User.email == form_data.username,User.is_active == True).first()    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    session_log = UserSessionLog(
        user_id = user.id,
        ip_address = request.client.host,
        user_agent = request.headers.get("user-agent")
    )
    db.add(session_log)
    db.commit()
    return {"access_token": access_token, "token_type": "bearer"}


# Role: Any authenticated user
@router.get("/profile", response_model=user_schemas.UserOut)
def get_profile(current_user: User = Depends(auth.get_current_user)):
    return current_user

def is_admin(user):
    return user.role and user.role.name == "Admin"

# Role: Admin
@router.get("/users/", response_model=List[user_schemas.UserOut])
def get_users(
    db: Session = Depends(auth.get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.ADMIN))
):
    return user_crud.get_all_users(db)

# Role: Admin
@router.post("/users/", response_model=user_schemas.UserOut)
def create_user(
    user: user_schemas.UserCreate,
    db: Session = Depends(auth.get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.ADMIN))
):
    return user_crud.create_user(db, user)

# Role: Admin
@router.get("/users/{user_id}", response_model=user_schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(auth.get_db), 
    current_user: user_models.User = Depends(auth.get_current_user)
    ):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Role: Admin
@router.put("/users/{user_id}", response_model=user_schemas.UserOut)
def update_user(user_id: int, updates: user_schemas.UserUpdate, db: Session = Depends(auth.get_db), current_user: User = Depends(auth.get_current_user)):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    db_user = user_crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.update_user(db, db_user, updates)

# Role: Admin
@router.delete("/users/{user_id}", response_model=user_schemas.UserOut)
def delete_user(user_id: int, db: Session = Depends(auth.get_db), 
    current_user: user_models.User = Depends(auth.get_current_user)
    ):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin only")
    db_user = user_crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.delete_user(db, db_user)

# Role: Any authenticated user (with shift check)
@router.post("/some-data-entry")
def restricted_entry(current_user: User = Depends(auth.get_current_user)):
    if not is_within_shift(current_user.shift):
        raise HTTPException(status_code=403, detail="Access outside assigned shift is denied.")
    return {"message": "Data accepted for shift."}

# Role: Any authenticated user
@router.post("/logout")
def logout(
    current_user: user_models.User = Depends(auth.get_current_user),
    db: Session = Depends(auth.get_db)
):
    session_log = (
        db.query(UserSessionLog)
        .filter(UserSessionLog.user_id == current_user.id)
        .order_by(UserSessionLog.login_time.desc())
        .first()
    )
    if session_log and session_log.logout_time is None:
        session_log.logout_time = datetime.utcnow()
        db.commit()
    return {"message": "Logout recorded"}

# Role: Any authenticated user
@router.post("/change-password")
def change_password(
    data: PasswordChangeRequest,
    db: Session = Depends(auth.get_db),
    current_user: user_models.User = Depends(auth.get_current_user)
):
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

# Role: Admin
@router.put("/users/{user_id}/update-role-shift")
def update_role_shift(
    user_id: int,
    updates: user_schemas.UserUpdate,
    db: Session = Depends(auth.get_db),
    current_user: user_models.User = Depends(role_required(RoleNames.ADMIN))
):
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_crud.update_user(db, user, updates)

