"""
Minigame related API endpoints for Ludora backend.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from tortoise.transactions import atomic
from tortoise.exceptions import DoesNotExist

from ludora_backend.app.models.user import User
from ludora_backend.app.models.profile import UserProfile
from ludora_backend.app.models.topic import Topic # Not directly used but good for context
from ludora_backend.app.models.question import Question
from ludora_backend.app.models.minigame import Minigame, MinigameProgress
from ludora_backend.app.schemas.minigame import MinigameRead, MinigameCreate, MinigameProgressRead, MinigameProgressCreate
from ludora_backend.app.schemas.question import QuestionRead # For response model
from ludora_backend.app.api.dependencies import get_current_active_user

router = APIRouter()

# Minigame Admin/Helper Endpoints
# TODO: Protect this endpoint - should only be accessible by admin/superuser.
@router.post("/minigames", response_model=MinigameRead, status_code=status.HTTP_201_CREATED)
async def create_minigame(minigame_data: MinigameCreate): # Add auth dependency (e.g. current_user: User = Depends(get_current_admin_user)))
    """
    Creates a new minigame. (Admin/Helper endpoint)
    """
    if minigame_data.topic_focus_id:
        if not await Topic.exists(id=minigame_data.topic_focus_id):
            raise HTTPException(status_code=404, detail=f"Topic with id {minigame_data.topic_focus_id} not found.")

    # The 'metadata' field in schema maps to 'metadata_' in model due to alias in schema
    # Pydantic model_dump will produce a dict with 'metadata' if present.
    # We need to ensure our create call matches the model field name 'metadata_'.
    minigame_dict = minigame_data.model_dump(exclude_unset=True)
    if 'metadata' in minigame_dict: # Pydantic model_dump will use field name 'metadata' from schema
        minigame_dict['metadata_'] = minigame_dict.pop('metadata')

    new_minigame = await Minigame.create(**minigame_dict)
    await new_minigame.fetch_related('topic_focus') # Load for response
    return new_minigame

@router.get("/minigames", response_model=List[MinigameRead])
async def list_minigames():
    """
    Lists all available minigames.
    """
    minigames = await Minigame.all().prefetch_related('topic_focus')
    return minigames

# Minigame Gameplay Endpoints
@router.get("/minigames/{minigame_id}/questions", response_model=List[QuestionRead])
async def get_minigame_questions(
    minigame_id: int,
    current_user: User = Depends(get_current_active_user) # Auth ensures user context
):
    """
    Retrieves a list of questions for a specific minigame session.
    """
    try:
        minigame = await Minigame.get(id=minigame_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Minigame not found")

    if minigame.topic_focus_id:
        questions = await Question.filter(topic_id=minigame.topic_focus_id).order_by("?").limit(minigame.question_count_per_session)
    else:
        # Fallback: get random questions if no topic focus
        questions = await Question.all().order_by("?").limit(minigame.question_count_per_session)

    # Ensure topics are fetched for each question if QuestionRead schema expects it
    # (QuestionRead already defines `topic: Optional[TopicRead] = None`, so prefetch is good)
    # A bit tricky with .order_by("?").limit() and prefetch_related.
    # It might be better to fetch IDs then fetch full questions with topics.
    # For now, assume this simplified version works or QuestionRead handles lazy loading.
    # A more robust way:
    # question_ids = [q.id for q in questions]
    # questions_with_topics = await Question.filter(id__in=question_ids).prefetch_related('topic')
    # return questions_with_topics

    # For simplicity, let's assume the schema or ORM handles the nested topic correctly for now.
    # If issues arise, the above prefetching pattern would be needed.
    # We can try to prefetch directly on the query:
    if minigame.topic_focus_id:
        questions = await Question.filter(topic_id=minigame.topic_focus_id).prefetch_related('topic').order_by("?").limit(minigame.question_count_per_session)
    else:
        questions = await Question.all().prefetch_related('topic').order_by("?").limit(minigame.question_count_per_session)

    return questions


@router.post("/minigames/{minigame_id}/progress", response_model=MinigameProgressRead, status_code=status.HTTP_201_CREATED)
@atomic()
async def submit_minigame_progress(
    minigame_id: int, # From path
    progress_data: MinigameProgressCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Submits the progress/outcome of a minigame session for the current user.
    """
    if minigame_id != progress_data.minigame_id:
        raise HTTPException(
            status_code=400,
            detail="Minigame ID in path does not match minigame ID in request body."
        )

    try:
        minigame = await Minigame.get(id=progress_data.minigame_id) # Use ID from body as source of truth
    except DoesNotExist:
        raise HTTPException(status_code=404, detail=f"Minigame with id {progress_data.minigame_id} not found.")

    # Create MinigameProgress record
    new_progress = await MinigameProgress.create(
        user=current_user,
        minigame=minigame, # Use the fetched minigame instance
        score=progress_data.score,
        currency_earned=progress_data.currency_earned,
        tickets_used=progress_data.tickets_used,
        powerups_applied=progress_data.powerups_applied,
        session_duration_seconds=progress_data.session_duration_seconds
    )

    # Update user's profile (in-app currency)
    if progress_data.currency_earned > 0:
        user_profile = await UserProfile.get(user_id=current_user.id) # Should exist due to signal
        user_profile.in_app_currency += progress_data.currency_earned
        await user_profile.save()

    # (Future: Link to LearningProgress or create a LearningProgress entry)
    # Example:
    # await LearningProgress.create(
    #     user=current_user,
    #     minigame_id=str(minigame.id),
    #     score=new_progress.score,
    #     topic_id=str(minigame.topic_focus_id) if minigame.topic_focus_id else None,
    #     completed_at=new_progress.completed_at
    # )

    return new_progress
