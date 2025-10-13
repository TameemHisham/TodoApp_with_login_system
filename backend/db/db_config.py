# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# _T_ Engine connects to the database
engine = create_engine("sqlite:///todo_list.db", echo=True)

# _T_ Base class for ORM models
Base = declarative_base()

# _T_ Session factory for talking to the database
SessionLocal = sessionmaker(bind=engine)
