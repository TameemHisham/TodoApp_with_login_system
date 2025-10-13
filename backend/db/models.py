from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from db.db_config import Base, engine
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class StatusEnum(enum.Enum):
    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    COMPLETE = "complete"

# -----------------------------
# * USER TABLE
# -----------------------------


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    todos = relationship("TodoList", back_populates="user",
                         cascade="all, delete")

# -----------------------------
# * TODO LIST TABLE
# -----------------------------


class TodoList(Base):
    __tablename__ = "todo_list"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    status = Column(Enum(StatusEnum), default=StatusEnum.NOT_STARTED)
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)

    # Relationship back to user
    user = relationship("User", back_populates="todos")


Base.metadata.create_all(engine)
