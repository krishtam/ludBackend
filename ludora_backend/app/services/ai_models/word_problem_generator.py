import onnxruntime
import numpy as np
from typing import List, Dict, Any # Ensure Any, Dict, List are imported

# Attempt to import transformers, handle if not available for this subtask's core logic
try:
    from transformers import AutoTokenizer
except ImportError:
    print("WARNING: 'transformers' library not found. AI Word Problem Generator will not be fully operational.")
    AutoTokenizer = None # type: ignore # Make AutoTokenizer None if import fails

from .utils import load_onnx_model, run_onnx_inference
from ludora_backend.app.schemas.ai_models import WordProblemInput, WordProblemOutput

# Hypothetical model and tokenizer paths/names
MODEL_PATH = "ludora_backend/app/services/ai_models/onnx_placeholder_models/t5_small_word_problem.onnx"
TOKENIZER_NAME_OR_PATH = "t5-small" # Standard Hugging Face model name

session: onnxruntime.InferenceSession | None = None
tokenizer: Any | None = None # Using Any for tokenizer type due to conditional import

# Initialize tokenizer and ONNX session at module level
if AutoTokenizer:
    try:
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME_OR_PATH)
        print(f"Tokenizer '{TOKENIZER_NAME_OR_PATH}' loaded successfully.")
    except Exception as e:
        print(f"WARNING: Could not load T5 tokenizer '{TOKENIZER_NAME_OR_PATH}': {e}")
        tokenizer = None
else:
    tokenizer = None

try:
    session = load_onnx_model(MODEL_PATH)
except FileNotFoundError:
    print(f"WARNING: ONNX model file not found at {MODEL_PATH}. Word problem generator service will not be fully operational.")
    session = None
except Exception as e:
    # load_onnx_model already prints details, this is an additional catch
    print(f"WARNING: An unexpected error occurred while loading the T5 ONNX model: {e}")
    session = None


async def generate_ai_word_problem(input_params: WordProblemInput) -> WordProblemOutput:
    """
    Generates an AI-powered word problem based on input parameters.
    Uses a preloaded T5-small ONNX model and tokenizer.
    """
    if session is None or tokenizer is None:
        error_message = "Error: Word problem generator service not available due to missing model or tokenizer."
        print(f"ERROR in generate_ai_word_problem: {error_message}")
        # Fallback to a very generic problem or raise an exception
        # For this subtask, returning a placeholder error message in the output.
        return WordProblemOutput(generated_problem_text=error_message)

    # Preprocessing: Construct the input prompt and tokenize
    prompt_text = f"{input_params.prompt_prefix}{input_params.topic}"
    if input_params.keywords:
        prompt_text += f" keywords: {', '.join(input_params.keywords)}"

    print(f"Generating word problem with prompt: {prompt_text}")

    try:
        # Tokenize the prompt
        # For T5 ONNX models, input names are typically 'input_ids', 'attention_mask', and 'decoder_input_ids' for generation.
        # The tokenizer prepares 'input_ids' and 'attention_mask'.
        # For text generation, the model might internally handle decoder_input_ids starting with a pad token.
        # Or, some ONNX T5 models might only need input_ids.
        # This depends on how the model was exported to ONNX.

        # Simplified approach: Assume the ONNX model (if it were real) can generate from just input_ids
        # and the run_onnx_inference utility or the model itself handles attention_mask if needed.
        # A more complete implementation would pass attention_mask too.

        tokenized_inputs = tokenizer.encode_plus(
            prompt_text,
            return_tensors='np',
            max_length=input_params.max_length, # Max input sequence length
            truncation=True,
            padding='max_length' # Pad to max_length for consistent input shape
        )
        input_ids = tokenized_inputs['input_ids']
        attention_mask = tokenized_inputs['attention_mask'] # Typically needed by transformer models

        # ONNX T5 generation often requires decoder_input_ids as well, starting with pad_token_id
        # decoder_input_ids = np.full((input_ids.shape[0], 1), tokenizer.pad_token_id, dtype=np.int64)

        # For this placeholder, we'll assume the `run_onnx_inference` and the hypothetical ONNX model
        # are set up to handle what's given. The input_feed keys must match model's expected input names.
        # Common names for T5 ONNX: "input_ids", "attention_mask", "decoder_input_ids" (for encoder-decoder models)
        # If just "input_ids" is used, it implies a simpler ONNX export or an encoder-only setup used differently.
        # For a standard T5 generation task, you'd use model.generate() in PyTorch, which handles the autoregressive loop.
        # ONNX inference for generate is more manual: you might need to run the encoder, then loop with the decoder.
        # OR the ONNX model is exported with the generate loop embedded (less common for raw T5).

        # For the purpose of this structural task, let's assume a simplified ONNX model that
        # takes 'input_ids' and 'attention_mask' and directly outputs generated sequence IDs.
        # This is a major simplification of T5's generative process in ONNX.

        input_feed = {
            "input_ids": input_ids.astype(np.int64), # Ensure correct dtype
            "attention_mask": attention_mask.astype(np.int64) # Ensure correct dtype
            # "decoder_input_ids": decoder_input_ids # If model requires it
        }

        # Inference: model_outputs is a list of numpy arrays
        # For T5, this would typically be the generated sequence of token IDs.
        # Example: model_outputs = [output_sequences_ids]
        # output_sequences_ids shape might be (batch_size, sequence_length)

        # --- Placeholder for actual inference ---
        # model_outputs = run_onnx_inference(session, input_feed)
        # generated_ids = model_outputs[0] # Assuming the first output contains the token IDs
        # --- End Placeholder ---

        # --- Dummy output generation for this subtask ---
        # Instead of calling run_onnx_inference which might fail without a real model/matching inputs,
        # we'll generate plausible dummy output as requested.
        print("Note: Actual ONNX inference skipped for this placeholder service. Generating dummy text.")
        dummy_generated_ids_list = [
            tokenizer.pad_token_id,
            tokenizer.eos_token_id if tokenizer.eos_token_id else 0 # Placeholder for EOS
        ]
        # Create some plausible dummy text based on input
        dummy_text_tokens = tokenizer.encode(f"This is a generated word problem about {input_params.topic} focusing on {', '.join(input_params.keywords) if input_params.keywords else 'general concepts'}.", add_special_tokens=False)
        dummy_generated_ids_list = [tokenizer.pad_token_id] + dummy_text_tokens[:input_params.max_length-2] + [tokenizer.eos_token_id if tokenizer.eos_token_id else 0]
        generated_ids = np.array([dummy_generated_ids_list], dtype=np.int64)
        # --- End Dummy Output Generation ---

        # Postprocessing: Decode token IDs to text
        generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)

        return WordProblemOutput(generated_problem_text=generated_text.strip())

    except Exception as e:
        print(f"Error during word problem generation: {e}")
        # Fallback or re-raise
        return WordProblemOutput(generated_problem_text=f"Error generating problem: {e}")
