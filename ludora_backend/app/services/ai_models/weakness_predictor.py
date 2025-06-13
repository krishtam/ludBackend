import onnxruntime
import numpy as np
from typing import List, Dict, Any # Ensure Any, Dict, List are imported

from .utils import load_onnx_model, run_onnx_inference
from ludora_backend.app.schemas.ai_models import WeaknessPredictionInput, PredictedWeakness, WeaknessPredictionOutput

# Hypothetical model path
MODEL_PATH = "ludora_backend/app/services/ai_models/onnx_placeholder_models/lightgbm_weakness_predictor.onnx"
session: onnxruntime.InferenceSession | None = None # Allow session to be None

try:
    # Initialize the ONNX session by loading the model at module level
    session = load_onnx_model(MODEL_PATH)
except FileNotFoundError:
    print(f"WARNING: ONNX model file not found at {MODEL_PATH}. Weakness prediction service will not be operational.")
    session = None # Ensure session is None if model loading fails
except Exception as e:
    print(f"ERROR: An unexpected error occurred while loading the ONNX model from {MODEL_PATH}: {e}")
    session = None # Ensure session is None

async def predict_user_weakness(user_id: str, input_features: WeaknessPredictionInput) -> WeaknessPredictionOutput:
    """
    Predicts user weaknesses based on input features using a preloaded ONNX model.
    """
    if session is None:
        # Model is not loaded, return a default response or raise an appropriate exception
        # For this example, returning an empty list of weaknesses or a specific error message.
        # This indicates to the caller that the prediction service is not operational.
        print("ERROR: Weakness prediction service is not operational because the ONNX model could not be loaded.")
        # Option 1: Raise an exception
        # raise HTTPException(status_code=503, detail="Weakness prediction service is currently unavailable.")
        # Option 2: Return a default/error response (chosen for this example)
        return WeaknessPredictionOutput(
            user_id=user_id,
            predicted_weaknesses=[
                PredictedWeakness(
                    topic_id="service_unavailable",
                    weakness_probability=0.0,
                    suggested_action_level=1
                )
            ]
        )

    # Preprocessing: Convert input_features (Pydantic model) into a format suitable for the ONNX model.
    # This is highly dependent on the actual (hypothetical) model's expected input.
    # Example (very simplified, needs to match hypothetical model's input structure):

    # Assume a fixed order of topics for the model features if the model expects a flat array.
    # This mapping should be consistent with how the model was trained.
    # For dynamic topics, more complex feature engineering is needed (e.g., embeddings, aggregations).

    # Placeholder: let's define a fixed set of topic keys the model might expect
    # These would ideally come from a configuration or be derived from the model's metadata.
    expected_topic_keys_in_order = sorted(list(input_features.average_score_per_topic.keys()) + \
                                        list(input_features.time_spent_per_topic_minutes.keys()))
    # This creates a sorted list of unique topic keys present in the input.
    # A real model would need a fixed, predefined feature order.
    # For this placeholder, we'll use the sorted keys from the input itself.
    # If a key is missing in one dict, it won't be included, which isn't ideal for a fixed-size model.

    feature_vector_list = []
    # 1. Average scores per topic
    for topic_key in expected_topic_keys_in_order:
        feature_vector_list.append(input_features.average_score_per_topic.get(topic_key, 0.0)) # Default to 0.0 if missing

    # 2. Recent quiz scores (assuming model takes a fixed number, e.g., last 3, padded if fewer)
    max_recent_scores = 3 # Example: model expects features from last 3 scores
    padded_recent_scores = input_features.recent_quiz_scores[:max_recent_scores] + \
                           [0.0] * (max_recent_scores - len(input_features.recent_quiz_scores))
    feature_vector_list.extend(padded_recent_scores)

    # 3. Time spent per topic
    for topic_key in expected_topic_keys_in_order:
        feature_vector_list.append(float(input_features.time_spent_per_topic_minutes.get(topic_key, 0))) # Default to 0 if missing

    # This feature vector's size now depends on `len(expected_topic_keys_in_order) * 2 + max_recent_scores`.
    # A real model needs a fixed input size. This placeholder is illustrative.
    # Ensure the feature vector is of a consistent size, padding if necessary.

    if not feature_vector_list: # Handle case with no features (e.g., empty input dicts)
        # This case should ideally be validated by Pydantic (e.g. min_items for lists/dicts)
        # or handled based on model requirements.
        return WeaknessPredictionOutput(user_id=user_id, predicted_weaknesses=[])


    processed_input_np = np.array(feature_vector_list, dtype=np.float32).reshape(1, -1)

    # The actual input names and shapes would come from the ONNX model's metadata.
    # Assuming the ONNX model expects a single input tensor named 'input_features'.
    # (e.g., sess.get_inputs()[0].name could give the actual name)
    # For now, hardcode 'input_features' as the name.
    model_input_name = session.get_inputs()[0].name if session.get_inputs() else "input_features"
    input_feed = {model_input_name: processed_input_np}

    # Inference
    # run_onnx_inference returns a list of outputs.
    model_outputs = run_onnx_inference(session, input_feed)

    # Postprocessing: Convert model_outputs into WeaknessPredictionOutput.
    # This also depends on the hypothetical model's output structure.

    weaknesses = []
    # Assume model_outputs[0] is a numpy array of shape (1, num_predicted_topics * 2)
    # where pairs are (weakness_probability, suggested_action_level) for each topic.
    # Or, model_outputs could be a list with two arrays: one for probs, one for actions.
    # This is highly speculative.

    # For this placeholder, we'll create dummy output based on the topics
    # that were part of the input feature vector construction (expected_topic_keys_in_order).

    # Example: Assume the model outputs probabilities for the same 'expected_topic_keys_in_order'
    # and corresponding action levels.
    # Let's say model_outputs[0] is shape (1, N) for probs, model_outputs[1] is shape (1, N) for actions.
    # This means the ONNX model has two output nodes.

    # Simplified dummy post-processing using random values, as model output structure is unknown:
    if not expected_topic_keys_in_order and model_outputs:
        # If we couldn't derive topic keys from input but model produced output,
        # we need a predefined mapping from model output indices to topic_ids.
        # This scenario is too complex for a placeholder without that mapping.
        # For now, if expected_topic_keys_in_order is empty, return empty weaknesses.
        pass

    # Assuming model_outputs[0] contains probabilities and model_outputs[1] contains action levels
    # This is a strong assumption. A real model might output a single array or a dictionary.
    # For a more robust placeholder, let's simulate based on the number of input topics.

    # Let's simulate that the model outputs one probability and one action level per topic_key it was "aware of".
    # And assume the output order matches `expected_topic_keys_in_order`.
    # And model_outputs[0] has shape (1, len(expected_topic_keys_in_order)) for probabilities
    # And model_outputs[1] has shape (1, len(expected_topic_keys_in_order)) for action levels.

    num_output_topics = len(expected_topic_keys_in_order)

    # This is where you would map the raw ONNX output to your Pydantic schemas.
    # Example: if model_outputs = [probs_array, actions_array]
    # probs_array = model_outputs[0][0] # Assuming batch size 1
    # actions_array = model_outputs[1][0] # Assuming batch size 1

    for i, topic_key in enumerate(expected_topic_keys_in_order):
        # ---- DUMMY OUTPUT GENERATION ----
        # Replace this with actual processing of `model_outputs`
        # This dummy logic assumes the model might output something related to the input topics.
        # If the ONNX model is a black box for this task, we just need plausible transformations.

        # Example: Generate random probability and action level for each topic key from input
        dummy_prob = float(np.random.rand())
        dummy_action = int(np.random.randint(1, 4)) # Action levels 1, 2, or 3

        # If you had actual model_outputs:
        # if len(model_outputs) >= 2 and \
        #    isinstance(model_outputs[0], np.ndarray) and model_outputs[0].ndim == 2 and model_outputs[0].shape[1] > i and \
        #    isinstance(model_outputs[1], np.ndarray) and model_outputs[1].ndim == 2 and model_outputs[1].shape[1] > i:
        #     dummy_prob = float(model_outputs[0][0, i])
        #     dummy_action = int(model_outputs[1][0, i])
        #     # Ensure action is within 1-3, clip if necessary
        #     dummy_action = max(1, min(3, dummy_action))
        # else:
        #     # Fallback if model output structure is not as expected
        #     print(f"Warning: Unexpected model output structure for topic {topic_key}. Using default values.")
        #     # This case means the actual output from run_onnx_inference wasn't what we assumed here.

        weaknesses.append(PredictedWeakness(
            topic_id=topic_key, # Use the topic identifier from input features
            weakness_probability=dummy_prob,
            suggested_action_level=dummy_action
        ))
        if len(weaknesses) >= num_output_topics: # Safety break if num_output_topics was smaller
            break

    return WeaknessPredictionOutput(user_id=user_id, predicted_weaknesses=weaknesses)
