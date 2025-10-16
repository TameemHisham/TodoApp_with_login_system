from pydantic import BaseModel
import datetime
from db.db_config import SessionLocal
from db.models import TodoList as TodoListDB, StatusEnum
from fastapi import APIRouter, Form, HTTPException
from sqlalchemy import select, delete, update
from typing import Annotated
router = APIRouter(prefix="/todo", tags=["todo"])


class TodoList(BaseModel):

    title: str
    description: str | None
    status: StatusEnum
    due_date: datetime.date


@router.post("/{current_user_id}")
def new_todo(todo: Annotated[TodoList, Form()], current_user_id: int):
    if current_user_id:
        with SessionLocal() as session:
            try:
                if not todo.title:
                    raise ValueError("Title must be at least 1 character long")
                if not todo.description:
                    todo.description = ""
                db_todo = TodoListDB(
                    user_id=current_user_id,
                    title=todo.title,
                    description=todo.description,
                    status=todo.status,
                    due_date=todo.due_date,
                    created_at=datetime.datetime.now()
                )
                session.add(db_todo)
                session.commit()
                session.refresh(db_todo)
                return {"task_id": db_todo.id, "user_id": current_user_id, "message": "New task created"}
            except ValueError as e:
                return {"response": str(e)}


@router.get("/{current_user_id}")
def get_todos(current_user_id: int):
    with SessionLocal() as session:
        select_statement = select(TodoListDB).where(
            TodoListDB.user_id == current_user_id)
        rows = session.execute(select_statement).all()
        return {"response": [list(row) for row in rows]}


@router.get("/{current_user_id}/{todo_id}")
def get_todo(current_user_id: int, todo_id: int):
    with SessionLocal() as session:
        select_statement = select(TodoListDB).where(
            TodoListDB.id == todo_id)
        row = session.execute(select_statement).first()
        if row:
            return {"response": list(row)}
        raise HTTPException(status_code=404, detail={
                            "response": f"todo with id:  {todo_id} doesn't exits"})


@router.delete("/{current_user_id}/{todo_id}")
def delete_todo(current_user_id: int, todo_id: int):
    with SessionLocal() as session:
        user_exists = session.query(TodoListDB).where(
            TodoListDB.id == todo_id).first()
        if user_exists:
            delete_statement = delete(TodoListDB).where(
                TodoListDB.id == todo_id)
            session.execute(delete_statement)
            session.commit()
            return {"response": f"successfully deleted todo with id {todo_id}"}
        raise HTTPException(status_code=404, detail={
                            "response": f"todo with id:  {todo_id} doesn't exits"})


@router.post("/{current_user_id}/{todo_id}")
def update_user(todo: Annotated[TodoList, Form()], current_user_id: int, todo_id: int):
    with SessionLocal() as session:
        user_exists = session.query(TodoListDB).where(
            TodoListDB.id == todo_id).first()
        if user_exists:
            update_statement = update(TodoListDB).where(
                TodoListDB.id == todo_id).values(
                title=todo.title,
                description=todo.description,
                status=todo.status,
                due_date=todo.due_date,
            )
            session.execute(update_statement)
            session.commit()
            return {"response": f"successfully updated user with id {id}"}
        raise HTTPException(status_code=404, detail={
                            "response": f"user with id:  {id} doesn't exits"})
