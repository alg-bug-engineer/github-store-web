from datetime import timedelta
from typing import Any
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from app.models.user import User as UserModel
from app.schemas.user import Token, User, UserCreate, UserLogin
from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud import user as crud_user

router = APIRouter()
logger = logging.getLogger(__name__)


class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    user: User


@router.post("/login", response_model=TokenWithUser)
def login_access_token(
    *,
    db: Session = Depends(deps.get_db),
    login_data: UserLogin,
) -> Any:
    """
    JSON login endpoint - get an access token for future requests
    """
    user = crud_user.get_by_phone(db, phone=login_data.phone)
    if not user or not security.verify_password(
        login_data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect phone or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return TokenWithUser(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        token_type="bearer",
        user=User.model_validate(user),
    )


@router.post("/token", response_model=Token)
def login_for_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """
    OAuth2 compatible token login (form data)
    """
    user = crud_user.get_by_phone(db, phone=form_data.username)
    if not user or not security.verify_password(
        form_data.password, user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect phone or password",
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        token_type="bearer",
    )


@router.post("/register", response_model=TokenWithUser)
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    logger.info(f"Register attempt with phone: {user_in.phone}, nickname: {user_in.nickname}")
    
    # Validate required fields
    if not user_in.phone or not user_in.phone.strip():
        logger.warning("Registration failed: phone is empty")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is required",
        )
    
    if not user_in.password or len(user_in.password) < 6:
        logger.warning("Registration failed: password too short")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters",
        )
    
    # Check if user already exists
    user = crud_user.get_by_phone(db, phone=user_in.phone)
    if user:
        logger.warning(f"Registration failed: user with phone {user_in.phone} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this phone already exists in the system.",
        )
    
    try:
        user = crud_user.create(db, obj_in=user_in)
        logger.info(f"User created successfully: id={user.id}, phone={user.phone}")
    except IntegrityError as e:
        logger.error(f"Database integrity error during registration: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this phone already exists or database constraint violated.",
        )
    except Exception as e:
        logger.error(f"Unexpected error during user creation: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return TokenWithUser(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        token_type="bearer",
        user=User.model_validate(user),
    )


@router.get("/me", response_model=User)
def read_users_me(
    current_user: UserModel = Depends(deps.get_current_active_user),
) -> User:
    """
    Get current user.
    """
    return current_user


@router.post("/logout")
def logout(
    current_user: UserModel = Depends(deps.get_current_active_user),
) -> dict:
    """
    Logout current user (client-side should clear token).
    """
    return {"message": "Successfully logged out"}
