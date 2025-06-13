from fastapi import APIRouter, Depends, Request, HTTPException

from ludora_backend.app.schemas.ai_models import ParaphraseInput, ParaphraseOutput
from ludora_backend.app.services.ai_models.paraphraser import generate_paraphrase, session as paraphraser_session, tokenizer as paraphraser_tokenizer
# Importing session and tokenizer to check their availability at endpoint level
from ludora_backend.app.core.limiter import limiter
# from ludora_backend.app.api.dependencies import get_current_active_user # Optional, not used for this public endpoint

router = APIRouter()

@router.post("/ai/paraphrase", response_model=ParaphraseOutput)
@limiter.limit("30/minute") # Example rate limit
async def paraphrase_text_endpoint(
    request: Request, # Required by the limiter
    payload: ParaphraseInput
    # current_user: User = Depends(get_current_active_user) # If endpoint needs to be protected
):
    """
    Paraphrases the input text using an AI model.
    Optionally adjusts simplification level.
    """
    # Check if the model and tokenizer were loaded correctly in the service module
    if paraphraser_session is None or paraphraser_tokenizer is None:
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail="AI Paraphrasing service is currently unavailable due to model or tokenizer loading issues."
        )

    paraphrase_result = await generate_paraphrase(payload)

    # The service function itself returns an error message in the paraphrased_text field
    # if generation fails internally (e.g. after successful model load but runtime error).
    # We can check for that specific pattern if needed, or trust the 503 check above for setup issues.
    if "Error:" in paraphrase_result.paraphrased_text and \
       ("service not available" in paraphrase_result.paraphrased_text or \
        "generating paraphrase" in paraphrase_result.paraphrased_text):
        # This can happen if the service's internal check also fails after initial load
        # For example, if tokenizer is present but session is not, or vice-versa,
        # or if an unexpected error occurs during the dummy generation process.
        raise HTTPException(
            status_code=503,
            detail=paraphrase_result.paraphrased_text # Pass the more specific error from the service
        )

    return paraphrase_result
