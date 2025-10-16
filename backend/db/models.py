from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from db.db_config import Base, engine
# from db_config import Base, engine
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
import enum


class StatusEnum(enum.Enum):
    NOT_STARTED = "not started"
    IN_PROGRESS = "in progress"
    COMPLETE = "complete"


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


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
    email: Mapped[str]
    role: Mapped[str] = mapped_column(default="user")  # Add this
    created_at: Mapped[datetime]
    todos = relationship("TodoList", back_populates="user",
                         cascade="all, delete")


class Admin(Base):
    __tablename__ = "admins"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    password: Mapped[str]
    role: Mapped[str] = mapped_column(default="admin")  # Add this
    created_at: Mapped[datetime]


Base.metadata.create_all(engine)
