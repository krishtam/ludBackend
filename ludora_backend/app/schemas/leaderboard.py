"""
Pydantic schemas for Leaderboards.
"""
from pydantic import BaseModel
from datetime import datetime, date # Ensure date is imported
from typing import List, Optional

from ludora_backend.app.models.enums import ScoreType, Timeframe
from .user import UserRead # Assuming UserRead is in ludora_backend/app/schemas/user.py

class LeaderboardBase(BaseModel):
    """
    Base schema for Leaderboard, used for creation.
    """
    name: str
    score_type: ScoreType
    timeframe: Timeframe
    minigame_id: Optional[int] = None
    topic_id: Optional[int] = None
    is_active: bool = True

class LeaderboardCreate(LeaderboardBase):
    """
    Schema for creating a Leaderboard.
    """
    pass

class LeaderboardRead(LeaderboardBase):
    """
    Schema for reading Leaderboard data.
    """
    id: int
    last_updated: datetime

    class Config:
        orm_mode = True
        # Pydantic V2 uses from_attributes instead of orm_mode
        # from_attributes = True

class LeaderboardEntryRead(BaseModel):
    """
    Schema for reading LeaderboardEntry data.
    """
    id: int
    user: UserRead # Nested user info
    score: float
    rank: Optional[int] = None
    entry_date: date
    updated_at: datetime

    class Config:
        orm_mode = True
        # Pydantic V2 uses from_attributes instead of orm_mode
        # from_attributes = True
