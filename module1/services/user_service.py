# fastapi_project/services/user_service.py

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from module1.models.user import User
from module1.schemas.user import UserCreate

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate) -> User:
    hashed = pwd.hash(user_in.password)
    db_user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed,
        role_id=user_in.role_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
