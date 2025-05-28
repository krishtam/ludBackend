"""
Pydantic schemas for LearningProgress.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class LearningProgressBase(BaseModel):
    """
    Base schema for LearningProgress.
    """
    module_id: Optional[str] = None
    quiz_id: Optional[str] = None
    minigame_id: Optional[str] = None
    topic_id: Optional[str] = None
    subtopic_id: Optional[str] = None
    score: Optional[int] = None
    progress_percentage: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class LearningProgressCreate(LearningProgressBase):
    """
    Schema for creating a LearningProgress record.
    """
    pass

class LearningProgressRead(LearningProgressBase):
    """
    Schema for reading LearningProgress data.
    """
    id: int
    user_id: int # This will be populated from the related User model
    completed_at: datetime

    class Config:
        orm_mode = True
