from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    phone: str
    email: str = Field(index=True)
    hashed_password: str
    is_admin: bool = False
    is_validated: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

class Policy(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.now)
    active: bool = True
    collection_name: Optional[str] = None
