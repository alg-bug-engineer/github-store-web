from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud
from app.models.user import User # Explicitly import User
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.schemas.user import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")
reusable_oauth2_optional = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login", auto_error=False)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User: # Use imported User
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user_or_none(
    db: Session = Depends(get_db), token: Optional[str] = Depends(reusable_oauth2_optional)
) -> Optional[User]:
    if token is None:
        return None
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        return None  # Invalid token, return None
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        return None  # User not found, return None
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user), # Use imported User
) -> User: # Use imported User
    if current_user.status == 0:  # Assuming status 0 means inactive
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_user_or_none(
    current_user: Optional[User] = Depends(get_current_user_or_none),
) -> Optional[User]:
    if current_user and current_user.status == 0:
        return None  # Inactive user, treat as no user for optional dependency
    return current_user
