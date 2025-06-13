import onnxruntime
import numpy as np
from typing import List, Dict, Any # Ensure Any, Dict, List are imported

# Attempt to import transformers, handle if not available for this subtask's core logic
try:
    from transformers import AutoTokenizer
except ImportError:
    print("WARNING: 'transformers' library not found. AI Paraphraser service will not be fully operational.")
    AutoTokenizer = None # type: ignore # Make AutoTokenizer None if import fails

from .utils import load_onnx_model, run_onnx_inference # Assuming utils.py is in the same directory
from ludora_backend.app.schemas.ai_models import ParaphraseInput, ParaphraseOutput

# Hypothetical model and tokenizer paths/names
MODEL_PATH = "ludora_backend/app/services/ai_models/onnx_placeholder_models/paraphraser_model.onnx"
TOKENIZER_NAME_OR_PATH = "t5-small" # Using "t5-small" as a common seq2seq tokenizer.

session: onnxruntime.InferenceSession | None = None
tokenizer: Any | None = None # Using Any for tokenizer type due to conditional import

# Initialize tokenizer and ONNX session at module level
if AutoTokenizer:
    try:
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME_OR_PATH)
        print(f"Tokenizer '{TOKENIZER_NAME_OR_PATH}' loaded successfully for Paraphraser.")
    except Exception as e:
        print(f"WARNING: Could not load T5 tokenizer '{TOKENIZER_NAME_OR_PATH}' for Paraphraser: {e}")
        tokenizer = None
else:
    tokenizer = None # If AutoTokenizer itself failed to import

try:
    session = load_onnx_model(MODEL_PATH)
except FileNotFoundError:
    print(f"WARNING: ONNX model file not found at {MODEL_PATH} for Paraphraser. Service will not be operational.")
    session = None
except Exception as e:
    print(f"WARNING: An unexpected error occurred while loading the Paraphraser ONNX model: {e}")
    session = None


async def generate_paraphrase(input_params: ParaphraseInput) -> ParaphraseOutput:
    """
    Generates a paraphrase for the given text using a preloaded ONNX model and tokenizer.
    """
    if session is None or tokenizer is None:
        error_message = "Error: Paraphrasing service not available due to missing model or tokenizer."
        print(f"ERROR in generate_paraphrase: {error_message}")
        return ParaphraseOutput(
            original_text=input_params.text_to_paraphrase,
            paraphrased_text=error_message
        )

    # Preprocessing: Construct the input prompt and tokenize
    # For T5-like models, a prefix indicating the task is common.
    # The simplification_level could be used to adjust the prompt or generation parameters.
    prompt_text = f"paraphrase (level {input_params.simplification_level}): {input_params.text_to_paraphrase}"

    print(f"Generating paraphrase with prompt: {prompt_text}")

    try:
        # Tokenize the prompt
        tokenized_inputs = tokenizer.encode_plus(
            prompt_text,
            return_tensors='np',
            max_length=input_params.max_length, # Max input sequence length for the encoder
            truncation=True,
            padding='max_length'
        )
        input_ids = tokenized_inputs['input_ids'].astype(np.int64)
        attention_mask = tokenized_inputs['attention_mask'].astype(np.int64)

        input_feed = {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }

        # --- Placeholder for actual inference ---
        # model_outputs = run_onnx_inference(session, input_feed)
        # generated_ids = model_outputs[0] # Assuming the first output contains the token IDs
        # --- End Placeholder ---

        # --- Dummy output generation for this subtask ---
        print("Note: Actual ONNX inference for paraphraser skipped. Generating dummy text.")
        dummy_paraphrase_core = f"Simplified version of '{input_params.text_to_paraphrase}' at level {input_params.simplification_level}."
        dummy_text_tokens = tokenizer.encode(dummy_paraphrase_core, add_special_tokens=False)
        # Ensure dummy output respects max_length approximately (after decoding special tokens)
        max_output_tokens = input_params.max_length - 2 # Account for potential special tokens added by encode
        dummy_generated_ids_list = [tokenizer.pad_token_id] + dummy_text_tokens[:max_output_tokens] + [tokenizer.eos_token_id if tokenizer.eos_token_id is not None else 0]
        generated_ids = np.array([dummy_generated_ids_list], dtype=np.int64)
        # --- End Dummy Output Generation ---

        # Postprocessing: Decode token IDs to text
        paraphrased_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)

        return ParaphraseOutput(
            original_text=input_params.text_to_paraphrase,
            paraphrased_text=paraphrased_text.strip()
        )

    except Exception as e:
        print(f"Error during paraphrase generation: {e}")
        return ParaphraseOutput(
            original_text=input_params.text_to_paraphrase,
            paraphrased_text=f"Error generating paraphrase: {e}"
        )
