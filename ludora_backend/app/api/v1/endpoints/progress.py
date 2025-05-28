"""
Learning Progress endpoints for Ludora backend.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List # Make sure List is imported from typing

from ludora_backend.app.models.user import User
from ludora_backend.app.models.progress import LearningProgress
from ludora_backend.app.schemas.progress import LearningProgressCreate, LearningProgressRead
from ludora_backend.app.api.dependencies import get_current_active_user

router = APIRouter()

@router.post("/progress", response_model=LearningProgressRead)
async def create_learning_progress_record(
    progress_data: LearningProgressCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Creates a new learning progress record for the currently authenticated user.
    """
    # model_dump() is the Pydantic v2 equivalent of .dict()
    new_progress_record = await LearningProgress.create(
        user=current_user, **progress_data.model_dump()
    )
    return new_progress_record

@router.get("/progress/me", response_model=List[LearningProgressRead])
async def get_my_learning_progress_records(
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves all learning progress records for the currently authenticated user,
    ordered by completion date (most recent first).
    """
    progress_records = await LearningProgress.filter(user_id=current_user.id).order_by("-completed_at")
    # Tortoise returns a list of ORM objects. Pydantic will handle conversion
    # for each item in the list if the response_model is List[Schema] and Schema.Config.orm_mode = True.
    return progress_records
