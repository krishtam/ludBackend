import pytest
from httpx import AsyncClient

from ludora_backend.app.schemas.ai_models import GuideInput, GuideOutput, ProblemState, ParaphraseOutput
# To mock paraphraser availability within the guide_agent service for testing this endpoint
from ludora_backend.app.services.ai_models import guide_agent
from unittest.mock import patch, MagicMock, AsyncMock

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def sample_guide_api_input():
    problem_state = ProblemState(
        question_id="q_integration_test",
        current_problem_statement="What is the capital of France?"
    )
    return GuideInput(
        problem_state=problem_state,
        user_attempt="I think it's Paris."
    )

async def test_submit_attempt_success(client: AsyncClient, sample_guide_api_input: GuideInput):
    """Test successful call to the guide's submit-attempt endpoint with placeholder logic."""

    # The guide_agent's placeholder logic might try to call the paraphraser.
    # We need to ensure the paraphraser service is "available" or mock its call
    # if we want to test the path where paraphrasing is attempted.
    # For this basic success test, let's assume paraphraser is available and returns valid output.

    with patch.object(guide_agent, 'paraphraser_session', MagicMock()), \
         patch.object(guide_agent, 'paraphraser_tokenizer', MagicMock()), \
         patch.object(guide_agent, 'generate_paraphrase', new_callable=AsyncMock) as mock_paraphrase:

        # Define what the mocked generate_paraphrase should return
        mock_paraphrase.return_value = ParaphraseOutput(
            original_text="Some original hint",
            paraphrased_text="A simpler version of the hint."
        )

        response = await client.post("/api/v1/ai/guide/submit-attempt", json=sample_guide_api_input.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert "feedback_correctness" in data
    assert "hints" in data

    # Based on current placeholder logic in guide_agent.py:
    # If user_attempt is not empty and doesn't contain "correct_answer_placeholder",
    # it's marked "incorrect", gets 2 hints + 1 paraphrased if paraphraser works.
    if "correct_answer_placeholder" not in sample_guide_api_input.user_attempt.lower() and \
       sample_guide_api_input.user_attempt.strip():
        assert data["feedback_correctness"] == "incorrect"
        assert len(data["hints"]) == 3 # Two original hints + one paraphrased
        assert "A simpler version of the hint." in data["hints"][2].hint_text
    elif not sample_guide_api_input.user_attempt.strip():
         assert data["feedback_correctness"] == "unknown" # or "no_attempt"

async def test_submit_attempt_paraphraser_unavailable(client: AsyncClient, sample_guide_api_input: GuideInput):
    """Test guide endpoint when its internal paraphraser service is unavailable."""

    # Simulate paraphraser service (session or tokenizer) being None within guide_agent context
    with patch.object(guide_agent, 'paraphraser_session', None): # Tokenizer could be MagicMock()
        response = await client.post("/api/v1/ai/guide/submit-attempt", json=sample_guide_api_input.model_dump())

    assert response.status_code == 200 # Endpoint itself is up, but internal functionality might be reduced
    data = response.json()
    assert "feedback_correctness" in data

    # If user_attempt is not empty and not "correct", it generates 2 hints.
    # Paraphrased hint should not be present if paraphraser is down.
    if "correct_answer_placeholder" not in sample_guide_api_input.user_attempt.lower() and \
       sample_guide_api_input.user_attempt.strip():
        assert len(data["hints"]) == 2
        for hint in data["hints"]:
            assert "another way to think about that" not in hint.hint_text # Check paraphrased text is missing

async def test_submit_attempt_invalid_input(client: AsyncClient):
    """Test guide's submit-attempt endpoint with invalid input data."""
    invalid_payload = {
        "problem_state": {
            # "question_id": "q123", # Missing required field
            "current_problem_statement": "A problem."
        },
        "user_attempt": "An attempt."
    }
    response = await client.post("/api/v1/ai/guide/submit-attempt", json=invalid_payload)
    assert response.status_code == 422 # Unprocessable Entity
    data = response.json()
    assert data["type"] == "RequestValidationError"
    assert any("question_id" in error["loc"] for error in data["details"] if "loc" in error)

# Note: This endpoint is currently public but rate-limited.
# If it required authentication, we'd use `authenticated_client` and test for 401s.
# For now, assuming it's public for broader access to "The Guide".
