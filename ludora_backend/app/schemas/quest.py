from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from ludora_backend.app.models.enums import QuestStatus, QuestObjectiveType

# Quest Objective Schemas
class QuestObjectiveBase(BaseModel):
    objective_type: QuestObjectiveType
    target_id: Optional[str] = None # Corresponds to Quiz ID, Minigame ID, or Topic ID/slug
    target_count: int = Field(1, gt=0) # Must be at least 1
    description_override: Optional[str] = None

class QuestObjectiveRead(QuestObjectiveBase):
    id: int
    current_progress: int
    is_completed: bool

    class Config:
        orm_mode = True
        # Pydantic V2: from_attributes = True

# Quest Schemas
class QuestBase(BaseModel):
    name: str = Field("Learning Quest", min_length=3, max_length=200)
    description: Optional[str] = None
    reward_currency: int = Field(0, ge=0)

class QuestCreate(QuestBase): # For internal service use primarily
    """
    Schema for creating a new quest, typically used by the quest generation service.
    Objectives are defined at creation.
    """
    objectives: List[QuestObjectiveBase]
    # user_id would be passed directly to the service create function, not part of this payload typically

class QuestRead(QuestBase):
    id: int
    user_id: int # Assuming the User model's ID is int
    status: QuestStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    objectives: List[QuestObjectiveRead]

    class Config:
        orm_mode = True
        # Pydantic V2: from_attributes = True
