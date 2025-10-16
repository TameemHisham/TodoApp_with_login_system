from pydantic import BaseModel, EmailStr
from fastapi import APIRouter
router = APIRouter(prefix="/user", tags=["users"])


class UserBase(BaseModel):
    """used for sign in"""
    username: str | None = None
    email: EmailStr | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass
