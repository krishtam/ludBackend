import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from ludora_backend.app.schemas.ai_models import WordProblemInput, WordProblemOutput
from ludora_backend.app.services.ai_models.word_problem_generator import generate_ai_word_problem
# Import the 'session' and 'tokenizer' objects from the service to mock their state
from ludora_backend.app.services.ai_models import word_problem_generator

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def sample_word_problem_input():
    return WordProblemInput(
        topic="Basic Algebra",
        keywords=["apples", "cost"],
        prompt_prefix="generate a word problem about: ",
        max_length=100
    )

async def test_generate_ai_word_problem_service_unavailable(sample_word_problem_input: WordProblemInput):
    """Test behavior when the ONNX model session or tokenizer is None."""
    # Scenario 1: Session is None
    with patch.object(word_problem_generator, 'session', None), \
         patch.object(word_problem_generator, 'tokenizer', MagicMock()): # Assume tokenizer is fine
        result = await generate_ai_word_problem(sample_word_problem_input)
        assert isinstance(result, WordProblemOutput)
        assert "Error: Word problem generator service not available" in result.generated_problem_text

    # Scenario 2: Tokenizer is None
    with patch.object(word_problem_generator, 'session', MagicMock()), \
         patch.object(word_problem_generator, 'tokenizer', None): # Assume session is fine
        result = await generate_ai_word_problem(sample_word_problem_input)
        assert isinstance(result, WordProblemOutput)
        assert "Error: Word problem generator service not available" in result.generated_problem_text

    # Scenario 3: Both are None
    with patch.object(word_problem_generator, 'session', None), \
         patch.object(word_problem_generator, 'tokenizer', None):
        result = await generate_ai_word_problem(sample_word_problem_input)
        assert isinstance(result, WordProblemOutput)
        assert "Error: Word problem generator service not available" in result.generated_problem_text


@patch('ludora_backend.app.services.ai_models.word_problem_generator.run_onnx_inference') # Mock this if it were called
async def test_generate_ai_word_problem_placeholder_logic(
    mock_run_onnx_inference: MagicMock, # Even if not called by dummy logic, good to have if structure changes
    sample_word_problem_input: WordProblemInput
):
    """Test the placeholder (dummy) output generation logic."""

    mock_session_obj = MagicMock()
    mock_tokenizer_obj = MagicMock()

    # Mock tokenizer's encode_plus method (used by the service's preprocessing)
    # It should return a dictionary-like object with 'input_ids' and 'attention_mask'
    mock_tokenizer_obj.encode_plus.return_value = {
        'input_ids': np.array([[101, 102, 103, 104, 105, 106, 107, 108, 109, 102]], dtype=np.int64), # Dummy IDs
        'attention_mask': np.array([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]], dtype=np.int64)    # Dummy mask
    }
    # Mock tokenizer's decode method (used by the service's postprocessing)
    # Also mock pad_token_id and eos_token_id which are used in the dummy output generation path
    mock_tokenizer_obj.pad_token_id = 0
    mock_tokenizer_obj.eos_token_id = 1 # or some other integer

    # The dummy logic constructs text and then encodes it, then decodes.
    # So, the decode mock needs to reflect what it would get.
    # The dummy text is: f"This is a generated word problem about {topic} focusing on {keywords}."
    expected_dummy_core_text = f"This is a generated word problem about {sample_word_problem_input.topic} focusing on {', '.join(sample_word_problem_input.keywords)}."

    # Mock tokenizer.encode for the part where dummy text is created
    # This ensures that the `dummy_text_tokens` in the service are what we expect
    mock_tokenizer_obj.encode.return_value = [200, 300, 400, 500] # Dummy token IDs for the core text

    # Mock tokenizer.decode to return based on the dummy_generated_ids_list structure
    # The service creates: [pad_token_id] + dummy_text_tokens[:max_length-2] + [eos_token_id]
    # So, when decode is called with this, it should return our expected_dummy_core_text
    mock_tokenizer_obj.decode.return_value = expected_dummy_core_text

    with patch.object(word_problem_generator, 'session', mock_session_obj), \
         patch.object(word_problem_generator, 'tokenizer', mock_tokenizer_obj):

        result = await generate_ai_word_problem(sample_word_problem_input)

        assert isinstance(result, WordProblemOutput)
        assert result.generated_problem_text == expected_dummy_core_text

        # Verify tokenizer methods were called as expected by the dummy logic path
        mock_tokenizer_obj.encode_plus.assert_called_once() # For initial prompt tokenization
        # The dummy logic path also calls tokenizer.encode for the dummy text and tokenizer.decode
        assert mock_tokenizer_obj.encode.call_count > 0 # Called for the dummy text
        mock_tokenizer_obj.decode.assert_called_once() # Called to decode the dummy IDs

        # run_onnx_inference should NOT have been called in the dummy path
        mock_run_onnx_inference.assert_not_called()

# Test with AutoTokenizer being None (transformers not installed)
async def test_generate_ai_word_problem_no_tokenizer_lib(sample_word_problem_input: WordProblemInput):
    with patch.object(word_problem_generator, 'AutoTokenizer', None), \
         patch.object(word_problem_generator, 'tokenizer', None), \
         patch.object(word_problem_generator, 'session', MagicMock()): # session could be anything if tokenizer is None

        # Re-evaluate module-level tokenizer initialization with AutoTokenizer as None
        # This requires a bit of care, as the module-level code runs on import.
        # A simple way is to ensure word_problem_generator.tokenizer is None for this test.
        # The current setup in the service correctly sets tokenizer to None if AutoTokenizer is None.

        result = await generate_ai_word_problem(sample_word_problem_input)
        assert isinstance(result, WordProblemOutput)
        assert "Error: Word problem generator service not available" in result.generated_problem_text
