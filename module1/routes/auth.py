# fastapi_project/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..database import get_db
from ..schemas.user import UserCreate, UserOut
from ..services.auth_service import (
    authenticate_user,
    register_user,
    refresh_access_token,
    AuthError,
)
from ..utils.security import create_access_token, create_refresh_token
from .dependencies import require_role

router = APIRouter(prefix="/auth", tags=["auth"])


class RefreshTokenIn(BaseModel):
    refresh_token: str


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Authenticate and issue access + refresh tokens.
    """
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
    except AuthError as e:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = {"sub": user.email,
                "role": user.role.name}
    access_token = create_access_token(data=token_data)
    refresh_token = create_refresh_token(data=token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserOut)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new user account.
    """
    try:
        return register_user(db, user_in)
    except AuthError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/admin-only",
    dependencies=[Depends(require_role(["admin"]))],
)
def admin_data():
    """
    A protected endpoint only accessible by admin users.
    """
    return {"message": "You have admin access."}


@router.post("/refresh_token")
def refresh_token_header(request: Request):
    """
    Given a valid refresh token in the Authorization header,
    issue a new access token.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header",
        )

    token = auth_header.split(" ", 1)[1]
    try:
        new_access = refresh_access_token(token)
    except AuthError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/refresh", response_model=dict)
def refresh_token_body(token_in: RefreshTokenIn):
    """
    Given a valid refresh token in the request body,
    issue a new access token.
    """
    try:
        new_access = refresh_access_token(token_in.refresh_token)
    except AuthError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return {"access_token": new_access, "token_type": "bearer"}
