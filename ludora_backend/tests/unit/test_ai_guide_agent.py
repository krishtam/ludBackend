import pytest
from unittest.mock import patch, MagicMock

from ludora_backend.app.schemas.ai_models import GuideInput, GuideOutput, GuideHint, ProblemState, ParaphraseOutput
from ludora_backend.app.services.ai_models.guide_agent import get_hint_or_feedback
# Import service objects to mock them if paraphraser is called
from ludora_backend.app.services.ai_models import guide_agent

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def sample_problem_state():
    return ProblemState(
        question_id="q123",
        current_problem_statement="What is 2 + 2?"
    )

@pytest.fixture
def sample_guide_input_empty_attempt(sample_problem_state: ProblemState):
    return GuideInput(
        problem_state=sample_problem_state,
        user_attempt="  " # Empty or whitespace only
    )

@pytest.fixture
def sample_guide_input_correct_attempt(sample_problem_state: ProblemState):
    return GuideInput(
        problem_state=sample_problem_state,
        user_attempt="The correct_answer_placeholder is 4." # Contains the dummy keyword
    )

@pytest.fixture
def sample_guide_input_incorrect_attempt(sample_problem_state: ProblemState):
    return GuideInput(
        problem_state=sample_problem_state,
        user_attempt="I think it's 5."
    )

async def test_get_hint_or_feedback_empty_attempt(sample_guide_input_empty_attempt: GuideInput):
    """Test guide's response to an empty user attempt."""
    result = await get_hint_or_feedback(sample_guide_input_empty_attempt)

    assert isinstance(result, GuideOutput)
    assert result.feedback_correctness == "unknown" # or "no_attempt"
    assert "haven't made an attempt yet" in result.feedback_message
    assert len(result.hints) == 1
    assert result.hints[0].hint_type == "general"

async def test_get_hint_or_feedback_correct_attempt(sample_guide_input_correct_attempt: GuideInput):
    """Test guide's response to a (dummy) correct user attempt."""
    result = await get_hint_or_feedback(sample_guide_input_correct_attempt)

    assert isinstance(result, GuideOutput)
    assert result.feedback_correctness == "correct"
    assert "That's right!" in result.feedback_message
    assert len(result.hints) == 0 # No hints for correct answer in placeholder

@patch('ludora_backend.app.services.ai_models.guide_agent.generate_paraphrase')
async def test_get_hint_or_feedback_incorrect_attempt_with_paraphraser(
    mock_generate_paraphrase: MagicMock,
    sample_guide_input_incorrect_attempt: GuideInput
):
    """Test guide's response to an incorrect attempt, simulating paraphraser success."""

    # Mock paraphraser service to be available
    with patch.object(guide_agent, 'paraphraser_session', MagicMock()), \
         patch.object(guide_agent, 'paraphraser_tokenizer', MagicMock()):

        # Setup mock for generate_paraphrase call
        paraphrased_text = "This is a simpler version of the hint."
        mock_generate_paraphrase.return_value = ParaphraseOutput(
            original_text="Double-check your calculations...", # Original hint text
            paraphrased_text=paraphrased_text
        )

        result = await get_hint_or_feedback(sample_guide_input_incorrect_attempt)

        assert isinstance(result, GuideOutput)
        assert result.feedback_correctness == "incorrect"
        assert "Not quite" in result.feedback_message
        assert len(result.hints) == 3 # Original hint, next_step hint, and paraphrased hint
        assert result.hints[0].hint_type == "general"
        assert result.hints[1].hint_type == "next_step"
        assert result.hints[2].hint_type == "clarification"
        assert paraphrased_text in result.hints[2].hint_text

        mock_generate_paraphrase.assert_called_once()

async def test_get_hint_or_feedback_incorrect_attempt_no_paraphraser(
    sample_guide_input_incorrect_attempt: GuideInput
):
    """Test guide's response to an incorrect attempt when paraphraser is unavailable."""

    # Mock paraphraser service to be unavailable
    with patch.object(guide_agent, 'paraphraser_session', None), \
         patch.object(guide_agent, 'paraphraser_tokenizer', None):

        result = await get_hint_or_feedback(sample_guide_input_incorrect_attempt)

        assert isinstance(result, GuideOutput)
        assert result.feedback_correctness == "incorrect"
        assert "Not quite" in result.feedback_message
        assert len(result.hints) == 2 # Original hint and next_step hint, no paraphrased one
        assert result.hints[0].hint_type == "general"
        assert result.hints[1].hint_type == "next_step"

@patch('ludora_backend.app.services.ai_models.guide_agent.generate_paraphrase')
async def test_get_hint_or_feedback_paraphraser_error(
    mock_generate_paraphrase: MagicMock,
    sample_guide_input_incorrect_attempt: GuideInput
):
    """Test guide's response when paraphraser call returns an error message."""
    with patch.object(guide_agent, 'paraphraser_session', MagicMock()), \
         patch.object(guide_agent, 'paraphraser_tokenizer', MagicMock()):

        mock_generate_paraphrase.return_value = ParaphraseOutput(
            original_text="Some hint.",
            paraphrased_text="Error: Could not paraphrase." # Paraphraser service indicates an error
        )

        result = await get_hint_or_feedback(sample_guide_input_incorrect_attempt)

        assert isinstance(result, GuideOutput)
        assert result.feedback_correctness == "incorrect"
        assert len(result.hints) == 2 # Only original hints, no clarification hint
        mock_generate_paraphrase.assert_called_once()

@patch('ludora_backend.app.services.ai_models.guide_agent.generate_paraphrase')
async def test_get_hint_or_feedback_paraphraser_returns_same_text(
    mock_generate_paraphrase: MagicMock,
    sample_guide_input_incorrect_attempt: GuideInput
):
    """Test guide's response when paraphraser returns the same text as original."""
    with patch.object(guide_agent, 'paraphraser_session', MagicMock()), \
         patch.object(guide_agent, 'paraphraser_tokenizer', MagicMock()):

        original_hint_text = "Double-check your calculations and make sure you've understood what the question is asking for."
        mock_generate_paraphrase.return_value = ParaphraseOutput(
            original_text=original_hint_text,
            paraphrased_text=original_hint_text # Paraphraser returns identical text
        )

        result = await get_hint_or_feedback(sample_guide_input_incorrect_attempt)

        assert isinstance(result, GuideOutput)
        assert result.feedback_correctness == "incorrect"
        assert len(result.hints) == 2 # Only original hints, no clarification hint as paraphrase was same
        mock_generate_paraphrase.assert_called_once()
