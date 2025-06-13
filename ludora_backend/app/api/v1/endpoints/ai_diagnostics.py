from fastapi import APIRouter, Depends, Request, HTTPException

from ludora_backend.app.schemas.ai_models import WeaknessPredictionInput, WeaknessPredictionOutput
from ludora_backend.app.services.ai_models.weakness_predictor import predict_user_weakness, session as predictor_session
from ludora_backend.app.api.dependencies import get_current_active_user
from ludora_backend.app.core.limiter import limiter
from ludora_backend.app.models.user import User # For type hinting current_user

router = APIRouter()

@router.post("/ai/predict-weakness", response_model=WeaknessPredictionOutput)
@limiter.limit("10/minute") # Example rate limit
async def predict_weakness_endpoint(
    request: Request, # Required by the limiter
    payload: WeaknessPredictionInput,
    current_user: User = Depends(get_current_active_user)
):
    """
    Predicts user weaknesses based on provided features.
    """
    # Check if the model session was loaded correctly in the service module
    if predictor_session is None:
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail="AI Weakness Prediction service is currently unavailable due to model loading issues."
        )

    user_id = str(current_user.id)

    # The predict_user_weakness function already handles the case where its 'session' is None,
    # but an additional check here using the imported 'predictor_session' adds robustness at endpoint level.
    # However, the service function itself returning a specific error-like Pydantic model is also a valid strategy.
    # Let's rely on the service function's handling as implemented.

    prediction_output = await predict_user_weakness(user_id=user_id, input_features=payload)

    # If the service returned a specific "service_unavailable" marker in its output
    if prediction_output.predicted_weaknesses and \
       prediction_output.predicted_weaknesses[0].topic_id == "service_unavailable":
        raise HTTPException(
            status_code=503,
            detail="AI Weakness Prediction service is currently unavailable (model not loaded)."
        )

    return prediction_output
