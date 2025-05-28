"""
User schemas for Ludora backend.
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserBase(BaseModel):
    """
    Base schema for User.
    """
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """
    Schema for creating a User.
    """
    password: str

class UserRead(UserBase):
    """
    Schema for reading User data.
    """
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
