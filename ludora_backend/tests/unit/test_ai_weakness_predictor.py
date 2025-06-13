import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from ludora_backend.app.schemas.ai_models import WeaknessPredictionInput, WeaknessPredictionOutput, PredictedWeakness
from ludora_backend.app.services.ai_models.weakness_predictor import predict_user_weakness
# Import the 'session' object from the service to mock its state
from ludora_backend.app.services.ai_models import weakness_predictor

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def sample_weakness_input():
    return WeaknessPredictionInput(
        average_score_per_topic={"algebra": 0.5, "geometry": 0.9, "calculus": 0.4},
        recent_quiz_scores=[0.6, 0.45, 0.7],
        time_spent_per_topic_minutes={"algebra": 100, "geometry": 150, "calculus": 80}
    )

async def test_predict_user_weakness_model_not_loaded(sample_weakness_input: WeaknessPredictionInput):
    """Test behavior when the ONNX model session is None (not loaded)."""
    with patch.object(weakness_predictor, 'session', None):
        result = await predict_user_weakness("user123", sample_weakness_input)
        assert isinstance(result, WeaknessPredictionOutput)
        assert len(result.predicted_weaknesses) == 1
        assert result.predicted_weaknesses[0].topic_id == "service_unavailable"

@patch('ludora_backend.app.services.ai_models.weakness_predictor.run_onnx_inference')
async def test_predict_user_weakness_placeholder_logic(
    mock_run_onnx_inference: MagicMock,
    sample_weakness_input: WeaknessPredictionInput
):
    """Test the placeholder logic with a mocked ONNX session and inference call."""

    # Mock the ONNX session to be not None
    mock_session = MagicMock()
    # Mock get_inputs to return a dummy input name, required by the service's current preproc.
    dummy_input_meta = MagicMock()
    dummy_input_meta.name = "input_features" # Or whatever the service expects
    mock_session.get_inputs.return_value = [dummy_input_meta]

    # Define a plausible dummy output from the mocked run_onnx_inference
    # The current placeholder post-processing in predict_user_weakness generates random outputs
    # if the model_outputs from run_onnx_inference isn't structured as it might expect.
    # So, the exact output of run_onnx_inference doesn't critically affect the dummy postproc path.
    # However, if we wanted to test a more specific postprocessing path, we'd mock this more carefully.
    # For now, an empty list is fine as the service falls back to random generation for dummy output.
    mock_run_onnx_inference.return_value = []

    with patch.object(weakness_predictor, 'session', mock_session):
        result = await predict_user_weakness("user123", sample_weakness_input)

        assert isinstance(result, WeaknessPredictionOutput)
        assert result.user_id == "user123"

        # The number of predicted weaknesses in the placeholder logic depends on sorted unique keys from input
        expected_topic_keys = sorted(list(
            set(sample_weakness_input.average_score_per_topic.keys()) |
            set(sample_weakness_input.time_spent_per_topic_minutes.keys())
        ))
        assert len(result.predicted_weaknesses) == len(expected_topic_keys)

        for weakness in result.predicted_weaknesses:
            assert isinstance(weakness, PredictedWeakness)
            assert weakness.topic_id in expected_topic_keys
            assert 0.0 <= weakness.weakness_probability <= 1.0
            assert 1 <= weakness.suggested_action_level <= 3

        # Check if run_onnx_inference was called (it should be if session is not None)
        mock_run_onnx_inference.assert_called_once()

        # Verify the structure of input_feed passed to run_onnx_inference
        # This depends on the placeholder preprocessing logic.
        # The current preprocessing concatenates scores, recent scores (padded), and time spent.
        args, kwargs = mock_run_onnx_inference.call_args
        input_feed_arg = args[1] # input_data is the second argument to run_onnx_inference

        assert dummy_input_meta.name in input_feed_arg
        processed_input_np = input_feed_arg[dummy_input_meta.name]
        assert isinstance(processed_input_np, np.ndarray)

        # Expected length: num_unique_topics * 2 (for avg_score & time_spent) + num_recent_scores (padded to 3)
        num_unique_topics = len(expected_topic_keys)
        expected_feature_length = num_unique_topics * 2 + 3
        assert processed_input_np.shape == (1, expected_feature_length)
        assert processed_input_np.dtype == np.float32
