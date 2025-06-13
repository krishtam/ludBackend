import pytest
from httpx import AsyncClient

from ludora_backend.app.schemas.ai_models import ParaphraseInput, ParaphraseOutput
# Import the session and tokenizer from the service to allow mocking for testing 503
from ludora_backend.app.services.ai_models import paraphraser
from unittest.mock import patch, MagicMock

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def sample_paraphrase_api_input():
    return ParaphraseInput(
        text_to_paraphrase="This is a complex sentence that requires simplification for better understanding.",
        simplification_level=2,
        max_length=100
    )

async def test_paraphrase_success(client: AsyncClient, sample_paraphrase_api_input: ParaphraseInput):
    """Test successful paraphrase endpoint call with placeholder logic."""

    # Ensure the model & tokenizer are considered "loaded" for this test path
    with patch.object(paraphraser, 'session', MagicMock()), \
         patch.object(paraphraser, 'tokenizer', MagicMock()):

        # Mock the tokenizer methods used by the dummy logic in the service
        paraphraser.tokenizer.encode_plus.return_value = {
            'input_ids': np.array([[1] * 10]), # Dummy data
            'attention_mask': np.array([[1] * 10])
        }
        paraphraser.tokenizer.pad_token_id = 0
        paraphraser.tokenizer.eos_token_id = 1

        expected_dummy_core_text = f"Simplified version of '{sample_paraphrase_api_input.text_to_paraphrase}' at level {sample_paraphrase_api_input.simplification_level}."
        paraphraser.tokenizer.encode.return_value = [10, 20, 30] # Dummy token IDs
        paraphraser.tokenizer.decode.return_value = expected_dummy_core_text

        response = await client.post("/api/v1/ai/paraphrase", json=sample_paraphrase_api_input.model_dump())

    assert response.status_code == 200
    data = response.json()
    assert data["original_text"] == sample_paraphrase_api_input.text_to_paraphrase
    # Check if the dummy text is returned, as per placeholder logic in service
    assert data["paraphrased_text"] == expected_dummy_core_text

async def test_paraphrase_service_unavailable_model_not_loaded(client: AsyncClient, sample_paraphrase_api_input: ParaphraseInput):
    """Test paraphrase endpoint when the ONNX model is not loaded."""
    with patch.object(paraphraser, 'session', None), \
         patch.object(paraphraser, 'tokenizer', MagicMock()): # Assume tokenizer is fine for this case
        response = await client.post("/api/v1/ai/paraphrase", json=sample_paraphrase_api_input.model_dump())

    assert response.status_code == 503
    data = response.json()
    assert "AI Paraphrasing service is currently unavailable" in data["message"]

async def test_paraphrase_service_unavailable_tokenizer_not_loaded(client: AsyncClient, sample_paraphrase_api_input: ParaphraseInput):
    """Test paraphrase endpoint when the tokenizer is not loaded."""
    with patch.object(paraphraser, 'session', MagicMock()), \
         patch.object(paraphraser, 'tokenizer', None): # Tokenizer is None
        response = await client.post("/api/v1/ai/paraphrase", json=sample_paraphrase_api_input.model_dump())

    assert response.status_code == 503
    data = response.json()
    assert "AI Paraphrasing service is currently unavailable" in data["message"]

async def test_paraphrase_invalid_input(client: AsyncClient):
    """Test paraphrase endpoint with invalid input data."""
    invalid_payload = {
        # "text_to_paraphrase": "This is some text.", # Missing required field
        "simplification_level": 1,
        "max_length": 50
    }
    response = await client.post("/api/v1/ai/paraphrase", json=invalid_payload)
    assert response.status_code == 422 # Unprocessable Entity
    data = response.json()
    assert data["type"] == "RequestValidationError"
    assert any("text_to_paraphrase" in error["loc"] for error in data["details"] if "loc" in error)

async def test_paraphrase_invalid_simplification_level(client: AsyncClient):
    """Test paraphrase endpoint with out-of-range simplification_level."""
    payload = {
        "text_to_paraphrase": "This is some text.",
        "simplification_level": 5, # Out of range (ge=1, le=3)
        "max_length": 50
    }
    response = await client.post("/api/v1/ai/paraphrase", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["type"] == "RequestValidationError"
    assert any("simplification_level" in error["loc"] for error in data["details"] if "loc" in error)
