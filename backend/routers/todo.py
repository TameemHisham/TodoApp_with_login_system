from pydantic import BaseModel
import datetime
from db.db_config import SessionLocal
from db.models import TodoList as TodoListDB, StatusEnum, User as UserDB
from fastapi import APIRouter, Form, HTTPException, Depends
from sqlalchemy import select, delete, update
from typing import Annotated
from auth.dependencies import require_role, Role  # Import here

router = APIRouter(prefix="/todo", tags=["todo"])


class TodoList(BaseModel):
    title: str
    description: str | None
    status: StatusEnum
    due_date: datetime.date

# Add current_user dependency to each endpoint


@router.post("/")
def new_todo(
    todo: Annotated[TodoList, Form()],
    current_user: Annotated[UserDB, Depends(
        require_role(Role.USER))]  # Add this
):
    with SessionLocal() as session:
        try:
            if not todo.title:
                raise ValueError("Title must be at least 1 character long")
            if not todo.description:
                todo.description = ""
            db_todo = TodoListDB(
                user_id=current_user.id,  # Use current_user.id instead of parameter
                title=todo.title,
                description=todo.description,
                status=todo.status,
                due_date=todo.due_date,
                created_at=datetime.datetime.now()
            )
            session.add(db_todo)
            session.commit()
            session.refresh(db_todo)
            return {"task_id": db_todo.id, "user_id": current_user.id, "message": "New task created"}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
# Add this
def get_todos(current_user: Annotated[UserDB, Depends(require_role(Role.USER))]):
    with SessionLocal() as session:
        select_statement = select(TodoListDB).where(
            TodoListDB.user_id == current_user.id)  # Use current_user.id
        rows = session.execute(select_statement).scalars().all()
        return {"response": [
            {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "status": row.status,
                "due_date": row.due_date
            }
            for row in rows
        ]}


@router.get("/{todo_id}")
def get_todo(
    todo_id: int,
    current_user: Annotated[UserDB, Depends(
        require_role(Role.USER))]  # Add this
):
    with SessionLocal() as session:
        select_statement = select(TodoListDB).where(
            TodoListDB.id == todo_id,
            TodoListDB.user_id == current_user.id  # Security: ensure it's their todo
        )
        row = session.execute(select_statement).scalar_one_or_none()
        if row:
            return {"response": {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "status": row.status,
                "due_date": row.due_date
            }}
        raise HTTPException(
            status_code=404, detail=f"todo with id: {todo_id} doesn't exist")


@router.delete("/{todo_id}")
def delete_todo(
    todo_id: int,
    current_user: Annotated[UserDB, Depends(
        require_role(Role.USER))]  # Add this
):
    with SessionLocal() as session:
        todo_exists = session.query(TodoListDB).where(
            TodoListDB.id == todo_id,
            TodoListDB.user_id == current_user.id  # Security check
        ).first()
        if todo_exists:
            delete_statement = delete(TodoListDB).where(
                TodoListDB.id == todo_id)
            session.execute(delete_statement)
            session.commit()
            return {"response": f"successfully deleted todo with id {todo_id}"}
        raise HTTPException(
            status_code=404, detail=f"todo with id: {todo_id} doesn't exist")


@router.put("/{todo_id}")  # Changed from POST to PUT
def update_todo(
    todo: Annotated[TodoList, Form()],
    todo_id: int,
    current_user: Annotated[UserDB, Depends(
        require_role(Role.USER))]  # Add this
):
    with SessionLocal() as session:
        todo_exists = session.query(TodoListDB).where(
            TodoListDB.id == todo_id,
            TodoListDB.user_id == current_user.id  # Security check
        ).first()
        if todo_exists:
            update_statement = update(TodoListDB).where(
                TodoListDB.id == todo_id
            ).values(
                title=todo.title,
                description=todo.description,
                status=todo.status,
                due_date=todo.due_date,
            )
            session.execute(update_statement)
            session.commit()
            return {"response": f"successfully updated todo with id {todo_id}"}
        raise HTTPException(
            status_code=404, detail=f"todo with id: {todo_id} doesn't exist")
