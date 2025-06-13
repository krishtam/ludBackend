# AI Model Integration Guide

This guide provides instructions and considerations for integrating AI models into the Ludora backend services.

## 1. Weakness Prediction Module (LightGBM -> ONNX)

### 1.1. Model Purpose
The Weakness Prediction model analyzes user performance data to identify topics or areas where the user might be struggling. This information can be used to generate personalized quests, recommend specific learning content, or alert educators. It is currently envisioned as a LightGBM model converted to ONNX format for efficient inference.

### 1.2. Input/Output Schemas
The Pydantic schemas define the expected input and output for this model's API interaction:
-   **Input Schema:** `WeaknessPredictionInput` (defined in `ludora_backend/app/schemas/ai_models.py`)
    -   `average_score_per_topic: Dict[str, float]`
    -   `recent_quiz_scores: List[float]`
    -   `time_spent_per_topic_minutes: Dict[str, int]`
-   **Output Schema:** `WeaknessPredictionOutput` (defined in `ludora_backend/app/schemas/ai_models.py`)
    -   `user_id: str`
    -   `predicted_weaknesses: List[PredictedWeakness]`
        -   Each `PredictedWeakness` includes `topic_id`, `weakness_probability`, and `suggested_action_level`.

### 1.3. Model Training (General Guidance)
-   **Data Needed:**
    -   Aggregated user performance data: average scores per topic, number of attempts per topic, time spent on topics/modules.
    -   Quiz/minigame completion data, including scores and timestamps.
    -   User interaction patterns (e.g., hint usage, content re-visits).
    -   Labels for "weakness" could be derived from failing specific assessments, low scores sustained over time, or explicit feedback.
-   **Suggested Libraries:** `scikit-learn` for preprocessing, `lightgbm` for model training.
-   **Feature Engineering:** Critical for good performance. Examples:
    -   Rolling averages of scores.
    -   Time decay factors for older performance data.
    -   Comparison against average performance of peers (if available).
    -   Number of failed attempts vs. successful attempts on a topic.
-   **Key Considerations:**
    -   **Class Imbalance:** Users might not be "weak" in most topics most of the time. Address potential class imbalance for weakness labels.
    -   **Hyperparameter Tuning:** Use techniques like grid search, random search, or Bayesian optimization.
    -   **Validation Strategy:** Use appropriate cross-validation, potentially time-series aware if user performance evolves.
    -   **Interpretability:** Consider using SHAP values or similar if model explanations are needed.

### 1.4. Exporting to ONNX
-   **General Steps:**
    -   Train your LightGBM model using the `lightgbm` library.
    -   Use `skl2onnx` (or `lgbm2onnx` if available and suitable) to convert the trained LightGBM model to ONNX format. Example: `onltools.convert_lightgbm(lgbm_model, initial_types=initial_type_list, target_opset=OPSET_VERSION)`.
    -   Define `initial_types` carefully to match the expected input tensor's shape and data type (e.g., `[('input_features', FloatTensorType([None, num_features]))]`).
-   **Input/Output Names:**
    -   The ONNX model's input and output node names must match what the backend service expects.
    -   Currently, the service (`weakness_predictor.py`) has a placeholder input name derived from `session.get_inputs()[0].name` which defaults to `"input_features"` if that fails. This **must** be updated to match the actual name in your exported ONNX model.
    -   Similarly, the service needs to know how to interpret the output(s) from the ONNX model.
-   **Versioning:** Consider a versioning strategy for your ONNX models.

### 1.5. Quantization (General Guidance)
-   **Benefits:** Can significantly reduce model size and may speed up CPU inference.
-   **Tools:** ONNX Runtime provides tools for static and dynamic quantization.
    -   `onnxruntime.quantization.quantize_dynamic()`
    -   `onnxruntime.quantization.quantize_static()` (requires a calibration dataset)
-   **Considerations:**
    -   Always measure accuracy impact after quantization.
    -   Test performance (latency, throughput) on the target deployment environment.

### 1.6. Backend Integration Notes
-   **Service File:** `ludora_backend/app/services/ai_models/weakness_predictor.py`
-   **Model Path:** The service currently expects the model at `ludora_backend/app/services/ai_models/onnx_placeholder_models/lightgbm_weakness_predictor.onnx`. Replace the placeholder file with your trained and converted `.onnx` model.
-   **Preprocessing (`predict_user_weakness` function):**
    -   The current preprocessing logic is a placeholder. It must be updated to:
        1.  Take the `WeaknessPredictionInput` Pydantic model.
        2.  Extract and transform features exactly as expected by your trained LightGBM model (e.g., one-hot encoding, scaling, feature order).
        3.  Produce a `numpy.ndarray` that matches the ONNX model's input tensor name, shape, and data type.
-   **Postprocessing (`predict_user_weakness` function):**
    -   The current postprocessing logic generates dummy random data. It must be updated to:
        1.  Take the raw output list from `run_onnx_inference` (which are numpy arrays).
        2.  Interpret these outputs based on your model's design (e.g., probabilities for each topic, action levels).
        3.  Map these raw outputs to the `PredictedWeakness` schema, including `topic_id`, `weakness_probability`, and `suggested_action_level`. This might involve looking up topic identifiers based on output indices.
        4.  Assemble and return the `WeaknessPredictionOutput`.

### 1.7. Local Model Usage & Testing
-   Place your trained and converted `.onnx` model at the path specified in `MODEL_PATH` within `weakness_predictor.py`.
-   Ensure the `onnxruntime` package is installed in your environment.
-   Use the integration tests in `ludora_backend/tests/integration/test_ai_diagnostics_api.py` to test the `/api/v1/ai/predict-weakness` endpoint.
-   You may need to update the test payloads and assertions to match your model's actual expected inputs and outputs.
-   The unit tests in `ludora_backend/tests/unit/test_ai_weakness_predictor.py` can be adapted to test your specific preprocessing/postprocessing logic by providing mock ONNX outputs.

---

## 2. Word Problem Generator (T5-small -> ONNX)

### 2.1. Model Purpose
The Word Problem Generator model (based on T5-small or similar sequence-to-sequence transformer) aims to generate educational word problems based on a given topic, keywords, and other parameters.

### 2.2. Input/Output Schemas
Refer to `ludora_backend/app/schemas/ai_models.py`:
-   **Input Schema:** `WordProblemInput`
    -   `topic: str`
    -   `keywords: List[str]`
    -   `prompt_prefix: str`
    -   `max_length: int`
-   **Output Schema:** `WordProblemOutput`
    -   `generated_problem_text: str`

### 2.3. Model Training (General Guidance)
-   **Data Needed:** A dataset of (prompt, word_problem) pairs. Prompts could be structured from topics, keywords, or even example problems.
-   **Suggested Libraries:** `transformers` (from Hugging Face) for fine-tuning T5-small or similar models.
-   **Fine-tuning T5-small:**
    -   Start with a pre-trained `t5-small` checkpoint.
    -   Format your training data into "prefix: input_text" for the encoder and "output_text" for the decoder. Example prefix: "generate word problem about [TOPIC] using keywords [KEYWORDS]: ".
    -   Use the `Seq2SeqTrainer` or a custom PyTorch training loop.
-   **Key Considerations:**
    -   **Prompt Engineering:** The structure of the input prompt is crucial for T5 performance.
    -   **Data Quality & Diversity:** Ensure a good variety of topics, problem structures, and relevant keywords in your training data.
    -   **Evaluation Metrics:** ROUGE, BLEU for text generation quality, plus human evaluation for educational relevance and correctness.

### 2.4. Exporting to ONNX
-   **General Steps:**
    -   Use `transformers.onnx` module for exporting Hugging Face models to ONNX. T5 is an encoder-decoder model, so you might need to export these parts, or use a script that handles the full `generate` method export if available.
    -   Example command (conceptual): `python -m transformers.onnx --model=your_fine_tuned_t5_small_model --feature=seq2seq-lm --framework=pt output_onnx_path/`
-   **Input/Output Names:**
    -   ONNX versions of transformer models have specific input names (e.g., `input_ids`, `attention_mask`, sometimes `decoder_input_ids`). The tokenizer will prepare these.
    -   The output will typically be sequence IDs (`output_ids` or similar).
    -   Ensure these match what `run_onnx_inference` is used with in the backend service.
-   **Tokenizer:** The exact same tokenizer used during training and export **must** be used in the backend for preprocessing and postprocessing. Save your fine-tuned tokenizer alongside the model: `tokenizer.save_pretrained("./your_tokenizer_dir/")`.

### 1.5. Quantization (General Guidance)
-   **Benefits:** Reduced model size, potentially faster inference.
-   **Tools:** ONNX Runtime quantization tools, `optimum.onnxruntime` for Hugging Face models.
-   **Considerations:** Can affect generation quality; test thoroughly. Dynamic quantization is often easier to apply for transformers.

### 1.6. Backend Integration Notes
-   **Service File:** `ludora_backend/app/services/ai_models/word_problem_generator.py`
-   **Model Path:** Service expects model at `ludora_backend/app/services/ai_models/onnx_placeholder_models/t5_small_word_problem.onnx`.
-   **Tokenizer Path/Name:** Service uses `TOKENIZER_NAME_OR_PATH = "t5-small"`. Update this if you use a custom fine-tuned tokenizer saved locally (e.g., point to the directory where you saved it).
-   **Preprocessing (`generate_ai_word_problem` function):**
    -   The current logic constructs a prompt and uses `tokenizer.encode_plus` to get `input_ids` and `attention_mask`.
    -   This needs to align with how your specific T5 ONNX model expects inputs (e.g., if `decoder_input_ids` are needed explicitly for the first step of generation).
    -   The placeholder currently feeds `input_ids` and `attention_mask` to `run_onnx_inference`.
-   **Postprocessing (`generate_ai_word_problem` function):**
    -   The current logic takes the output from `run_onnx_inference` (assumed to be token IDs) and uses `tokenizer.decode` to get text.
    -   This is generally correct, but ensure `skip_special_tokens=True` and other decoding parameters are appropriate.
    -   The actual ONNX model might involve a generate loop or specific handling for sequence generation not fully captured by the current simplified `run_onnx_inference` placeholder for generative tasks. The current service uses dummy output generation. This part will need significant updates for a real model.

### 1.7. Local Model Usage & Testing
-   Place your trained `.onnx` model and tokenizer files at the paths specified in `word_problem_generator.py`.
-   Ensure `transformers`, `sentencepiece`, and `onnxruntime` are installed.
-   The service currently generates dummy text. To test with a real model:
    1.  Comment out/remove the dummy output generation block.
    2.  Ensure the `input_feed` to `run_onnx_inference` matches your ONNX model's inputs.
    3.  Ensure the postprocessing correctly handles the output of `run_onnx_inference`.
-   Test the relevant API endpoint (e.g., `GET /api/v1/q/questions/generate?question_type=ai_word_problem&topic_id=...`) via integration tests or API tools. Update tests in `test_ai_word_problem_generator.py` and the question generation endpoint tests.

---
*(Further models can be documented here following a similar structure)*
