"""
Leaderboard related API endpoints for Ludora backend.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional

from ludora_backend.app.models.leaderboard import Leaderboard
from ludora_backend.app.schemas.leaderboard import LeaderboardRead, LeaderboardCreate, LeaderboardEntryRead
from ludora_backend.app.services import leaderboard_service
from ludora_backend.app.models.enums import ScoreType, Timeframe
from ludora_backend.app.api.dependencies import get_current_active_user # If needed for some endpoints

router = APIRouter()

# Admin/Helper Endpoints
# TODO: Protect this endpoint - should only be accessible by admin/superuser.
@router.post("/leaderboards", response_model=LeaderboardRead, status_code=status.HTTP_201_CREATED)
async def create_leaderboard(leaderboard_data: LeaderboardCreate): # Add auth dependency (e.g. current_user: User = Depends(get_current_admin_user)))
    """
    Creates a new leaderboard definition. (Admin/Helper endpoint)
    """
    # Check for existing leaderboard by name
    if await Leaderboard.exists(name=leaderboard_data.name):
        raise HTTPException(status_code=400, detail=f"Leaderboard with name '{leaderboard_data.name}' already exists.")

    # Validate linked IDs if present
    if leaderboard_data.score_type == ScoreType.MINIGAME_HIGH_SCORE and not leaderboard_data.minigame_id:
        raise HTTPException(status_code=400, detail="minigame_id is required for MINIGAME_HIGH_SCORE leaderboards.")
    if leaderboard_data.score_type == ScoreType.TOPIC_PROFICIENCY and not leaderboard_data.topic_id:
        raise HTTPException(status_code=400, detail="topic_id is required for TOPIC_PROFICIENCY leaderboards.")

    # TODO: Add checks if minigame_id or topic_id exist if provided for other types or for the specific ones.

    new_leaderboard = await Leaderboard.create(**leaderboard_data.model_dump())
    return new_leaderboard

@router.get("/leaderboards", response_model=List[LeaderboardRead])
async def list_leaderboards(
    score_type: Optional[ScoreType] = None,
    timeframe: Optional[Timeframe] = None,
    is_active: bool = True
):
    """
    Lists leaderboard definitions, with optional filters.
    """
    filters = {"is_active": is_active}
    if score_type:
        filters["score_type"] = score_type
    if timeframe:
        filters["timeframe"] = timeframe

    return await Leaderboard.filter(**filters)

# TODO: Protect this endpoint - should only be accessible by admin/superuser.
@router.post("/leaderboards/{leaderboard_id}/update", status_code=status.HTTP_202_ACCEPTED)
async def trigger_leaderboard_update(leaderboard_id: int): # Add auth dependency (e.g. current_user: User = Depends(get_current_admin_user)))
    """
    Manually triggers an update for a specific leaderboard. (Admin/Helper endpoint)
    """
    leaderboard = await Leaderboard.get_or_none(id=leaderboard_id)
    if not leaderboard:
        raise HTTPException(status_code=404, detail="Leaderboard not found")

    # Call the appropriate service function based on leaderboard.score_type
    if leaderboard.score_type == ScoreType.QUIZ_OVERALL:
        await leaderboard_service.update_quiz_overall_leaderboard(leaderboard)
    elif leaderboard.score_type == ScoreType.MINIGAME_HIGH_SCORE:
        await leaderboard_service.update_minigame_high_score_leaderboard(leaderboard)
    elif leaderboard.score_type == ScoreType.TOPIC_PROFICIENCY:
        await leaderboard_service.update_topic_proficiency_leaderboard(leaderboard)
    elif leaderboard.score_type == ScoreType.OVERALL_XP:
        await leaderboard_service.update_overall_xp_leaderboard(leaderboard)
    else:
        raise HTTPException(status_code=400, detail="Unknown or unsupported score type for this leaderboard.")

    return {"message": f"Leaderboard '{leaderboard.name}' update process initiated."}


# Public Endpoints
@router.get("/leaderboards/{leaderboard_id}/entries", response_model=List[LeaderboardEntryRead])
async def get_leaderboard_entries_api( # Renamed to avoid conflict with service function
    leaderboard_id: int,
    limit: int = Query(100, gt=0, le=200)
):
    """
    Retrieves entries for a specific leaderboard.
    """
    if not await Leaderboard.exists(id=leaderboard_id, is_active=True):
        raise HTTPException(status_code=404, detail="Active leaderboard not found.")

    entries = await leaderboard_service.get_leaderboard_entries(leaderboard_id, limit)
    return entries
