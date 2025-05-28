"""
Pydantic schemas for UserProfile.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProfileBase(BaseModel):
    """
    Base schema for UserProfile.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

class ProfileCreate(ProfileBase):
    """
    Schema for creating a UserProfile.
    Can be empty if profile is created automatically with user registration,
    or include fields required at creation.
    """
    pass

class ProfileUpdate(ProfileBase):
    """
    Schema for updating a UserProfile.
    All fields are optional.
    """
    pass

class ProfileRead(ProfileBase):
    """
    Schema for reading UserProfile data.
    """
    id: int
    user_id: int # This will be populated from the related User model
    current_streak: int
    max_streak: int
    in_app_currency: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
