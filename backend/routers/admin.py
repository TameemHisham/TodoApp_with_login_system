from fastapi import APIRouter, HTTPException, Form, Depends
from pydantic import BaseModel
from db.models import Admin as AdminDB, User as UserDB
from db.db_config import SessionLocal
from sqlalchemy import select, delete, update
from routers.users import UserIn
from auth.hashing import hash_password
from typing import Annotated
from auth.dependencies import require_role, Role  # Import dependencies

router = APIRouter(prefix="/admin", tags=["admin"])


class Admin(BaseModel):
    username: str
    password: str


# Protected: Only admins can access these routes
@router.get("/users")
def get_users(current_admin: Annotated[AdminDB, Depends(require_role(Role.ADMIN))]):
    """Get all users - Admin only."""
    with SessionLocal() as session:
        users = session.execute(select(UserDB)).scalars().all()
        return {
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "created_at": user.created_at
                }
                for user in users
            ]
        }


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_admin: Annotated[AdminDB, Depends(require_role(Role.ADMIN))]
):
    """Delete a user - Admin only."""
    with SessionLocal() as session:
        user_exists = session.query(UserDB).where(UserDB.id == user_id).first()

        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail=f"User with id {user_id} doesn't exist"
            )

        delete_statement = delete(UserDB).where(UserDB.id == user_id)
        session.execute(delete_statement)
        session.commit()

        return {"message": f"Successfully deleted user with id {user_id}"}


@router.put("/users/{user_id}")
def update_user(
    user_id: int,
    user_data: Annotated[UserIn, Form()],
    current_admin: Annotated[AdminDB, Depends(require_role(Role.ADMIN))]
):
    """Update a user - Admin only."""
    with SessionLocal() as session:
        user_exists = session.query(UserDB).where(UserDB.id == user_id).first()

        if not user_exists:
            raise HTTPException(
                status_code=404,
                detail=f"User with id {user_id} doesn't exist"
            )

        update_statement = update(UserDB).where(UserDB.id == user_id).values(
            username=user_data.username,
            email=user_data.email,
            password=hash_password(user_data.password)
        )
        session.execute(update_statement)
        session.commit()

        return {"message": f"Successfully updated user with id {user_id}"}


@router.get("/users/{user_id}")
def get_user(
    user_id: int,
    current_admin: Annotated[AdminDB, Depends(require_role(Role.ADMIN))]
):
    """Get specific user details - Admin only."""
    with SessionLocal() as session:
        user = session.query(UserDB).where(UserDB.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User with id {user_id} doesn't exist"
            )

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at
        }


# Optional: Admin can view all todos across all users
@router.get("/todos")
def get_all_todos(current_admin: Annotated[AdminDB, Depends(require_role(Role.ADMIN))]):
    """Get all todos from all users - Admin only."""
    from db.models import TodoList as TodoListDB

    with SessionLocal() as session:
        todos = session.execute(select(TodoListDB)).scalars().all()
        return {
            "todos": [
                {
                    "id": todo.id,
                    "user_id": todo.user_id,
                    "title": todo.title,
                    "description": todo.description,
                    "status": todo.status,
                    "due_date": todo.due_date,
                    "created_at": todo.created_at
                }
                for todo in todos
            ]
        }
