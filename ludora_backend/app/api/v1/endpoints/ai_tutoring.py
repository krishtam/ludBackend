from fastapi import APIRouter, Depends, Request, HTTPException # Ensure HTTPException is imported

from ludora_backend.app.schemas.ai_models import GuideInput, GuideOutput
from ludora_backend.app.services.ai_models.guide_agent import get_hint_or_feedback
from ludora_backend.app.core.limiter import limiter
# from ludora_backend.app.api.dependencies import get_current_active_user # Optional: If endpoint needs auth
# from ludora_backend.app.models.user import User # For type hinting current_user if using get_current_active_user

router = APIRouter()

@router.post("/ai/guide/submit-attempt", response_model=GuideOutput)
@limiter.limit("60/minute") # Example rate limit
async def submit_user_attempt_to_guide(
    request: Request, # Required by the limiter
    payload: GuideInput
    # current_user: User = Depends(get_current_active_user) # Uncomment if user context is needed
):
    """
    Submits a user's attempt for a problem to "The Guide" for feedback and hints.
    """
    # Optional: Pass user_id to the service if it personalizes responses
    # if current_user:
    #     payload.user_id = str(current_user.id) # Assuming GuideInput schema is updated to take user_id

    # The get_hint_or_feedback service function currently has placeholder logic
    # and will return a GuideOutput object.
    # It also includes internal checks for its dependencies (like paraphraser).

    guide_response = await get_hint_or_feedback(payload)

    # Example of checking for a specific error condition from the service, if needed.
    # The current service function returns a valid GuideOutput even on internal errors,
    # but might populate messages indicating issues.
    # If the service were to raise custom exceptions for critical failures (e.g., paraphraser always needed but unavailable),
    # those could be caught here or handled by global exception handlers.

    # For instance, if a critical sub-service like paraphraser was essential and failed,
    # the service might return a specific hint or message, or the endpoint could check:
    # if "Error: Paraphrasing service not available" in str(guide_response.hints): # Example check
    #     raise HTTPException(status_code=503, detail="A critical component of The Guide is unavailable.")

    return guide_response
