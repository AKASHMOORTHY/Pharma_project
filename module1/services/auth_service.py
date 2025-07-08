

from sqlalchemy.orm import Session
from jose import JWTError, jwt

from ..models.user import User
from ..models.role import Role  # ✅ ensure you import Role model
from ..schemas.user import UserCreate, UserOut
from ..utils.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token,
    SECRET_KEY,
    ALGORITHM,
)

class AuthError(Exception):
    """Authentication/authorization failure."""
    pass


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.query(User).filter(User.email == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid credentials")
    return user


def register_user(db: Session, user_in: UserCreate) -> UserOut:
   # ✅ Check if email or username already exists
    existing_user = db.query(User).filter(
    (User.email == user_in.email) | (User.username == user_in.username)
).first()

    if existing_user:
        raise AuthError("Username or Email already registered")

    # ✅ Fetch the Role object from DB
    role_obj = db.query(Role).filter(Role.name == user_in.role).first()
    if not role_obj:
        raise AuthError(f"Invalid role: {user_in.role}")

    # ✅ Create new user with role object
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=role_obj  # relationship field expects Role object
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserOut.from_orm(new_user)


def refresh_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        role = payload.get("role")
        if email is None or role is None:
            raise AuthError("Invalid token payload")
        return create_access_token({"sub": email, "role": role})
    except JWTError:
        raise AuthError("Invalid or expired token")
