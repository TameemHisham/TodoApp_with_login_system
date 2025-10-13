from pydantic import BaseModel
import datetime
from db.db_config import SessionLocal
from db.models import User as UserDB
from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
router = APIRouter(prefix="/todo", tags=["users"])


class User_in(BaseModel):
    """used for sign in"""
    username: str | None
    email: str | None
    password: str


class User_up(BaseModel):
    """used for sign up"""
    username: str
    email: str
    password: str


@router.post("/sign_in")
def sign_in(user: User_in):
    if user.username:
        with SessionLocal() as session:
            select_statement = select(UserDB).where(
                UserDB.username == user.username)
            user_data = session.execute(select_statement).scalar_one_or_none()
            if user_data is None:
                return {"response": "user doesn't exist"}
            if getattr(user_data, "password") == user.password:
                return {"response": user_data}
            return {"response": "wrong password"}
    if user.email:
        pass
    return {"response": "No username or email"}


@router.post("/sign_up")
def sign_up(user: User_up):
    with SessionLocal() as session:
        try:
            db_user = UserDB(
                username=user.username,
                email=user.email,
                password=user.password,
                created_at=datetime.datetime.now()
            )
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return {"id": db_user.id, "message": "User created successfully"}
        except IntegrityError:
            return {"response": "username or email has been taken!"}
