from db.models import User as UserDB, Admin as AdminDB  # Import your actual models
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import timedelta, datetime
from db.db_config import SessionLocal
from auth.hashing import verify_password, hash_password
from auth.jwt_handler import create_access_token
from pydantic import BaseModel
from routers.users import UserIn
from typing import Annotated
router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 30


class Token(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(model_class, username: str, password: str, session: Session):
    """Helper function to authenticate against any model."""
    user = session.execute(
        select(model_class).where(model_class.username == username)
    ).scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        return None
    return user


@router.post("/token/user")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate regular user and issue JWT token."""
    with SessionLocal() as session:
        user = authenticate_user(
            UserDB, form_data.username, form_data.password, session)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "type": "user"},
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")


@router.post("/token/admin")
def login_admin(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate admin and issue JWT token."""
    with SessionLocal() as session:
        admin = authenticate_user(
            AdminDB, form_data.username, form_data.password, session)

        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": admin.username, "type": "admin"},
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup_user(user: Annotated[UserIn, Form()]):
    with SessionLocal() as session:
        # Check if username or email already exists
        existing_user = session.execute(
            select(UserDB).where(
                (UserDB.username == user.username) | (
                    UserDB.email == user.email)
            )
        ).scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )

        # Hash the password
        hashed_password = hash_password(user.password)

        # Create new UserDB instance
        new_user = UserDB(
            username=user.username,
            email=user.email,
            password=hashed_password,
            role="user",
            created_at=datetime.utcnow()
        )

        # Add to DB
        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        return {"message": "User created successfully", "user_id": new_user.id}
