"""
Pydantic schemas for Minigames.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any

# Assuming TopicRead is in a sibling file 'question.py' within the same 'schemas' directory
from .question import TopicRead 

# Minigame Schemas
class MinigameBase(BaseModel):
    """
    Base schema for Minigame.
    """
    name: str
    description: Optional[str] = None
    topic_focus_id: Optional[int] = None # To be used for creation/update if topic_focus is set by ID
    question_count_per_session: int = Field(10, gt=0) # Ensure positive number of questions
    # Pydantic field 'metadata' will map to model's 'metadata_' field.
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata_")

class MinigameCreate(MinigameBase):
    """
    Schema for creating a Minigame.
    """
    pass

class MinigameRead(MinigameBase):
    """
    Schema for reading Minigame data.
    """
    id: int
    topic_focus: Optional[TopicRead] = None # Nested full topic information

    class Config:
        orm_mode = True
        # Pydantic V2 uses from_attributes instead of orm_mode
        # from_attributes = True 

# MinigameProgress Schemas
class MinigameProgressBase(BaseModel):
    """
    Base schema for MinigameProgress.
    """
    minigame_id: int
    score: int
    currency_earned: int = 0
    tickets_used: int = 0
    powerups_applied: Optional[List[Dict[str, Any]]] = None
    session_duration_seconds: Optional[int] = None

class MinigameProgressCreate(MinigameProgressBase):
    """
    Schema for creating a MinigameProgress record.
    """
    pass

class MinigameProgressRead(MinigameProgressBase):
    """
    Schema for reading MinigameProgress data.
    """
    id: int
    user_id: int
    completed_at: datetime

    class Config:
        orm_mode = True
        # Pydantic V2 uses from_attributes instead of orm_mode
        # from_attributes = True
