from sqlmodel import SQLModel, create_engine, Session
from app.config import DATABASE_URL
from app.models import User, Policy

# SQLite (for Windows local dev)
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
