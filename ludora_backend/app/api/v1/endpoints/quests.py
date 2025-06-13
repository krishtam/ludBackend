from fastapi import APIRouter, Depends, HTTPException, status, Request # Added Request
from typing import List

from ludora_backend.app.models.user import User
from ludora_backend.app.models.quest import Quest # Needed for Quest.filter()
from ludora_backend.app.schemas.quest import QuestRead
from ludora_backend.app.services import quest_generator_service # Import the service module
from ludora_backend.app.api.dependencies import get_current_active_user
from ludora_backend.app.core.limiter import limiter # If rate limiting is needed

router = APIRouter()

@router.post(
    "/users/me/quests/generate",
    response_model=List[QuestRead],
    status_code=status.HTTP_201_CREATED,
    summary="Generate New Quests for Current User",
    description="Triggers the quest generation process for the authenticated user based on their performance and predicted weaknesses. Returns a list of newly created quests."
)
@limiter.limit("5/hour") # Example: Rate limit quest generation
async def generate_user_quests_endpoint(
    request: Request, # If using limiter
    current_user: User = Depends(get_current_active_user)
):
    """
    Generates new quests for the currently authenticated user.
    This process may involve analyzing user performance, predicting weaknesses (conceptually),
    and applying a rule engine to create personalized quests.
    Returns a list of newly created active quests.
    """
    try:
        created_quests = await quest_generator_service.generate_quests_for_user(current_user)
        if not created_quests:
            # It's not an error if no quests were generated, could be by design (e.g., user has enough active quests or no new recommendations)
            return []
        return created_quests
    except Exception as e:
        # Log the exception e
        print(f"Error during quest generation for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while generating quests."
        )

@router.get(
    "/users/me/quests",
    response_model=List[QuestRead],
    summary="Get My Quests",
    description="Retrieves all quests (active, pending, completed, etc.) for the currently authenticated user, ordered by most recent first."
)
async def get_my_quests( # Renamed for clarity from get_my_active_quests
    current_user: User = Depends(get_current_active_user)
    # status: Optional[QuestStatus] = Query(None, description="Filter quests by status.") # Example of a filter
):
    """
    Retrieves all quests associated with the currently authenticated user.
    Results are ordered by creation date (newest first).
    Objectives for each quest are prefetched.
    """
    # Example: Fetch all quests for the user. Can be filtered by status in future.
    # query_filters = {"user": current_user}
    # if status:
    #     query_filters["status"] = status
    # quests = await Quest.filter(**query_filters).prefetch_related('objectives').order_by('-created_at')
    quests = await Quest.filter(user=current_user).prefetch_related('objectives').order_by('-created_at')
    return quests
