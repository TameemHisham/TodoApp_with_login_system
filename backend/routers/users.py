from pydantic import BaseModel
from db.db_config import SessionLocal
from db.models import User as UserDB
from fastapi import APIRouter, Form, HTTPException
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime
router = APIRouter(prefix="/user", tags=["users"])


class UserBase(BaseModel):
    """used for sign in"""
    username: str | None = None
    email: str | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


async def sign_in_using_x(user: Annotated[UserIn, Form()], user_identity):
    with SessionLocal() as session:
        select_statement = select(UserDB).where(
            (UserDB.username if user.username else UserDB.email) == user_identity)
        user_data = session.execute(select_statement).scalar_one_or_none()
        if user_data is None:
            return HTTPException(status_code=404, detail={"response": "user doesn't exist"})
        if getattr(user_data, "password") == user.password:
            return {"response": user_data}
        return HTTPException(status_code=401, detail={"response": "wrong password"})


@router.post("/sign_in")
async def sign_in(user: Annotated[UserIn, Form()]):
    if user.username:
        res = await sign_in_using_x(user, user.username)
        return res
    elif user.email:
        res = await sign_in_using_x(user, user.email)
        return res
    return HTTPException(status_code=400, detail={"response": "No username or email"})


@router.post("/sign_up")
async def sign_up(user: Annotated[UserIn, Form()]):
    with SessionLocal() as session:
        try:
            if user.username:
                if len(user.username) < 5:
                    raise ValueError("Username length less than 5")
            if user.email:
                if len(user.email) < 3:
                    raise ValueError("Email length less than 3")
            if len(user.password) < 8:
                raise ValueError("Password length less than 8")
            db_user = UserDB(
                username=user.username,
                email=user.email,
                password=user.password,
                created_at=datetime.now()
            )
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return {"id": db_user.id, "message": "User created successfully"}
        except IntegrityError:
            return HTTPException(status_code=409, detail={"response": "username or email has been taken!"})
        except ValueError as e:
            return HTTPException(status_code=400, detail={"response": str(e)})
