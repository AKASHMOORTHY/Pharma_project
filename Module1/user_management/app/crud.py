# app/crud.py
from sqlalchemy.orm import Session
from user_management.app import models
from user_management.app.utils.security import hash_password
from user_management.app.schemas import UserCreate, UserUpdate

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_all_users(db: Session):
    return db.query(models.User).all()

def create_user(db: Session, user: UserCreate):
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        shift=user.shift,
        role_id=user.role_id,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.User, updates: UserUpdate):
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: models.User):
    db_user.is_active = False
    db.commit()
    return db_user
