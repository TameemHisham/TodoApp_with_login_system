from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from db.models import Admin as AdminDB, User as UserDB
from db.db_config import SessionLocal
from sqlalchemy import select, delete, update
from routers.users import User
router = APIRouter(prefix="/admin", tags=["admin"])


class Admin(BaseModel):
    username: str
    password: str


def verify_admin(credentials: Admin):
    with SessionLocal() as session:
        select_statement = select(AdminDB).where(
            AdminDB.username == credentials.username,
            AdminDB.password == credentials.password
        )
        result = session.execute(select_statement).first()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Basic"},
            )

        return True


@router.post("/users")
def get_users(admin: Admin):
    if verify_admin(admin):
        with SessionLocal() as session:
            select_statement = select(UserDB)
            rows = session.execute(select_statement).all()
            return {"response": [list(row) for row in rows]}


@router.delete("/user/{id}")
def delete_user(admin: Admin, id: str):
    if verify_admin(admin):
        with SessionLocal() as session:
            user_exists = session.query(UserDB).where(
                UserDB.id == id).first()
            if user_exists:
                delete_statement = delete(UserDB).where(
                    UserDB.id == id)
                session.execute(delete_statement)
                session.commit()
                return {"response": f"successfully deleted user with id {id}"}
            return {"response": f"user with id:  {id} doesn't exits"}


@router.post("/user/{id}")
def update_user(admin: Admin, id: str, user_data: User):
    if verify_admin(admin):
        with SessionLocal() as session:
            user_exists = session.query(UserDB).where(
                UserDB.id == id).first()
            if user_exists:
                update_statement = update(UserDB).where(
                    UserDB.id == id).values(
                    username=user_data.username,
                    email=user_data.email,
                    password=user_data.password
                )
                session.execute(update_statement)
                session.commit()
                return {"response": f"successfully updated user with id {id}"}
            return {"response": f"user with id:  {id} doesn't exits"}
