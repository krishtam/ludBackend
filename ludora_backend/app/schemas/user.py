"""
User schemas for Ludora backend.
"""
from pydantic import BaseModel, EmailStr, Field # Import Field
from datetime import datetime
from typing import Optional # For optional fields in example or future use

class UserBase(BaseModel):
    """
    Base schema for User properties shared across different operations.
    """
    email: EmailStr = Field(..., description="User's email address.", example="user@example.com")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username for the user.", example="john_doe")

class UserCreate(UserBase):
    """
    Schema used for creating a new user. Inherits email and username from UserBase.
    """
    password: str = Field(..., min_length=8, description="User's password. Must be at least 8 characters long.", example="Str0ngP@sswOrd")

class UserRead(UserBase):
    """
    Schema for returning user data to the client. Excludes sensitive information like password.
    """
    id: int = Field(..., description="Unique identifier for the user.", example=1)
    is_active: bool = Field(..., description="Indicates if the user account is active.", example=True)
    is_superuser: bool = Field(..., description="Indicates if the user has superuser privileges.", example=False)
    created_at: datetime = Field(..., description="Timestamp of when the user account was created.")
    updated_at: datetime = Field(..., description="Timestamp of the last update to the user account.")
    # Example of adding a field from a related model (UserProfile) if it were to be included here
    # profile: Optional[Any] = None # Replace Any with actual ProfileRead schema if needed

    class Config:
        orm_mode = True
        # Pydantic V2: from_attributes = True
