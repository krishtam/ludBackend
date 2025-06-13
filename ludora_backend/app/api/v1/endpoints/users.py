"""
User Profile endpoints for Ludora backend.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from ludora_backend.app.models.user import User
from ludora_backend.app.models.profile import UserProfile
from ludora_backend.app.schemas.profile import ProfileRead, ProfileUpdate
from ludora_backend.app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("/users/me/profile", response_model=ProfileRead)
async def get_my_profile(current_user: User = Depends(get_current_active_user)):
    """
    Retrieves the profile for the currently authenticated user.
    If a profile does not exist (e.g., due to signal not running or manual deletion),
    it will be created on-the-fly.
    """
    profile = await UserProfile.get_or_none(user_id=current_user.id) # Use user_id for direct lookup
    if not profile:
        # This case should ideally not happen if the post_save signal is working correctly.
        # However, as a fallback or for robustness:
        profile = await UserProfile.create(user=current_user)
    return profile

@router.put("/users/me/profile", response_model=ProfileRead)
async def update_my_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Updates the profile for the currently authenticated user.
    If a profile does not exist, it will be created with the provided data.
    """
    profile = await UserProfile.get_or_none(user_id=current_user.id) # Use user_id for direct lookup

    update_data = profile_in.model_dump(exclude_unset=True)

    if not profile:
        # If profile doesn't exist, create it with the update data.
        # Ensure all required fields for UserProfile (if any beyond user_id) are handled.
        # UserProfile model has defaults for gamification fields.
        profile = await UserProfile.create(user=current_user, **update_data)
    else:
        # Update existing profile
        for key, value in update_data.items():
            setattr(profile, key, value)
        await profile.save()

    return profile
