import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from ludora_backend.app.schemas.ai_models import ParaphraseInput, ParaphraseOutput
from ludora_backend.app.services.ai_models.paraphraser import generate_paraphrase
# Import the 'session' and 'tokenizer' objects from the service to mock their state
from ludora_backend.app.services.ai_models import paraphraser

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def sample_paraphrase_input():
    return ParaphraseInput(
        text_to_paraphrase="The quick brown fox jumps over the lazy dog.",
        simplification_level=1,
        max_length=100
    )

async def test_generate_paraphrase_service_unavailable(sample_paraphrase_input: ParaphraseInput):
    """Test behavior when the ONNX model session or tokenizer is None."""
    # Scenario 1: Session is None
    with patch.object(paraphraser, 'session', None), \
         patch.object(paraphraser, 'tokenizer', MagicMock()): # Assume tokenizer is fine
        result = await generate_paraphrase(sample_paraphrase_input)
        assert isinstance(result, ParaphraseOutput)
        assert result.original_text == sample_paraphrase_input.text_to_paraphrase
        assert "Error: Paraphrasing service not available" in result.paraphrased_text

    # Scenario 2: Tokenizer is None
    with patch.object(paraphraser, 'session', MagicMock()), \
         patch.object(paraphraser, 'tokenizer', None): # Assume session is fine
        result = await generate_paraphrase(sample_paraphrase_input)
        assert isinstance(result, ParaphraseOutput)
        assert result.original_text == sample_paraphrase_input.text_to_paraphrase
        assert "Error: Paraphrasing service not available" in result.paraphrased_text

    # Scenario 3: Both are None
    with patch.object(paraphraser, 'session', None), \
         patch.object(paraphraser, 'tokenizer', None):
        result = await generate_paraphrase(sample_paraphrase_input)
        assert isinstance(result, ParaphraseOutput)
        assert result.original_text == sample_paraphrase_input.text_to_paraphrase
        assert "Error: Paraphrasing service not available" in result.paraphrased_text


@patch('ludora_backend.app.services.ai_models.paraphraser.run_onnx_inference') # Mock this if it were called
async def test_generate_paraphrase_placeholder_logic(
    mock_run_onnx_inference: MagicMock, # Even if not called by dummy logic
    sample_paraphrase_input: ParaphraseInput
):
    """Test the placeholder (dummy) output generation logic."""

    mock_session_obj = MagicMock()
    mock_tokenizer_obj = MagicMock()

    mock_tokenizer_obj.encode_plus.return_value = {
        'input_ids': np.array([[101, 102, 103, 104, 105]], dtype=np.int64),
        'attention_mask': np.array([[1, 1, 1, 1, 1]], dtype=np.int64)
    }
    mock_tokenizer_obj.pad_token_id = 0
    mock_tokenizer_obj.eos_token_id = 1

    expected_dummy_core_text = f"Simplified version of '{sample_paraphrase_input.text_to_paraphrase}' at level {sample_paraphrase_input.simplification_level}."

    # Mock tokenizer.encode for the part where dummy text is created
    mock_tokenizer_obj.encode.return_value = [200, 300, 400] # Dummy token IDs for the core text

    # Mock tokenizer.decode for the final output
    mock_tokenizer_obj.decode.return_value = expected_dummy_core_text

    with patch.object(paraphraser, 'session', mock_session_obj), \
         patch.object(paraphraser, 'tokenizer', mock_tokenizer_obj):

        result = await generate_paraphrase(sample_paraphrase_input)

        assert isinstance(result, ParaphraseOutput)
        assert result.original_text == sample_paraphrase_input.text_to_paraphrase
        assert result.paraphrased_text == expected_dummy_core_text

        mock_tokenizer_obj.encode_plus.assert_called_once()
        assert mock_tokenizer_obj.encode.call_count > 0
        mock_tokenizer_obj.decode.assert_called_once()

        mock_run_onnx_inference.assert_not_called() # As dummy logic path is taken

async def test_generate_paraphrase_no_tokenizer_lib(sample_paraphrase_input: ParaphraseInput):
    """Test behavior when the transformers library (AutoTokenizer) is not available."""
    with patch.object(paraphraser, 'AutoTokenizer', None), \
         patch.object(paraphraser, 'tokenizer', None), \
         patch.object(paraphraser, 'session', MagicMock()):

        # This test relies on the module-level conditional import of AutoTokenizer
        # and subsequent setting of paraphraser.tokenizer to None.
        result = await generate_paraphrase(sample_paraphrase_input)
        assert isinstance(result, ParaphraseOutput)
        assert "Error: Paraphrasing service not available" in result.paraphrased_text
