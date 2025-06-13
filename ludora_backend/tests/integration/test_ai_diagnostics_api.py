import pytest
from httpx import AsyncClient

from ludora_backend.app.schemas.ai_models import WeaknessPredictionInput, WeaknessPredictionOutput
# Import the session from the service to allow mocking it for testing 503
from ludora_backend.app.services.ai_models import weakness_predictor
from unittest.mock import patch

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

async def test_predict_weakness_success(authenticated_client: AsyncClient):
    """Test successful weakness prediction endpoint call with placeholder logic."""
    payload = WeaknessPredictionInput(
        average_score_per_topic={"algebra": 0.6, "geometry": 0.7},
        recent_quiz_scores=[0.65, 0.75],
        time_spent_per_topic_minutes={"algebra": 100, "geometry": 80}
    )

    # Ensure the model is considered "loaded" for this test path
    # (it might be None by default if the placeholder file doesn't exist)
    with patch.object(weakness_predictor, 'session', MagicMock()): # Simulate session is loaded
        response = await authenticated_client.post("/api/v1/ai/predict-weakness", json=payload.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data # User ID comes from authenticated_client's user
    assert "predicted_weaknesses" in data
    # Further assertions depend on the dummy logic in predict_user_weakness
    # For example, if dummy logic generates predictions for all input topics:
    input_topics = set(payload.average_score_per_topic.keys()) | set(payload.time_spent_per_topic_minutes.keys())
    if data["predicted_weaknesses"] and data["predicted_weaknesses"][0]["topic_id"] != "service_unavailable":
         assert len(data["predicted_weaknesses"]) == len(input_topics)
         for item in data["predicted_weaknesses"]:
            assert item["topic_id"] in input_topics

async def test_predict_weakness_model_not_loaded(authenticated_client: AsyncClient):
    """Test predict-weakness endpoint when the ONNX model is not loaded."""
    payload = WeaknessPredictionInput(
        average_score_per_topic={"algebra": 0.6},
        recent_quiz_scores=[0.65],
        time_spent_per_topic_minutes={"algebra": 100}
    )

    # Simulate that the ONNX session is None (model not loaded)
    # The endpoint checks `predictor_session` (which is `weakness_predictor.session`)
    with patch.object(weakness_predictor, 'session', None):
        response = await authenticated_client.post("/api/v1/ai/predict-weakness", json=payload.model_dump())

    assert response.status_code == 503 # Service Unavailable
    data = response.json()
    assert "AI Weakness Prediction service is currently unavailable" in data["message"]


async def test_predict_weakness_unauthenticated(client: AsyncClient):
    """Test predict-weakness endpoint without authentication."""
    payload = WeaknessPredictionInput(
        average_score_per_topic={"algebra": 0.6},
        recent_quiz_scores=[0.65],
        time_spent_per_topic_minutes={"algebra": 100}
    )
    response = await client.post("/api/v1/ai/predict-weakness", json=payload.model_dump())
    assert response.status_code == 401 # Unauthorized (due to get_current_active_user dependency)
    # The exact error message/detail might depend on your global HTTPException handler
    # or FastAPI's default for missing token.
    # For now, checking the status code is primary.
    # data = response.json()
    # assert data["type"] == "HTTPException" # Based on our custom handler
    # assert "Not authenticated" in data["message"] # Or similar, FastAPI's default is "Not authenticated"

async def test_predict_weakness_invalid_input(authenticated_client: AsyncClient):
    """Test predict-weakness with invalid input data (missing required fields)."""
    invalid_payload = {
        "average_score_per_topic": {"algebra": 0.6},
        # "recent_quiz_scores": [0.65], # Missing this required field
        "time_spent_per_topic_minutes": {"algebra": 100}
    }
    response = await authenticated_client.post("/api/v1/ai/predict-weakness", json=invalid_payload)
    assert response.status_code == 422 # Unprocessable Entity for Pydantic validation errors
    data = response.json()
    assert data["type"] == "RequestValidationError"
    assert any("recent_quiz_scores" in error["loc"] for error in data["details"] if "loc" in error)
