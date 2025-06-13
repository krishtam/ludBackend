import onnxruntime
import numpy as np # Common for pre/post-processing
from typing import Any, Dict, List

# Placeholder for where models might be stored, e.g., a dedicated 'onnx_models' directory
# This would need to be configured properly, perhaps via settings.
# For now, assume models are passed by path.
# MODEL_DIRECTORY = "path/to/your/onnx_models"

def load_onnx_model(model_path: str) -> onnxruntime.InferenceSession:
    """
    Loads an ONNX model using ONNX Runtime.

    Args:
        model_path (str): The file path to the ONNX model.

    Returns:
        onnxruntime.InferenceSession: The loaded inference session.

    Raises:
        Exception: If the model cannot be loaded.
    """
    try:
        # Specify CPUExecutionProvider to ensure it runs on CPU
        # This is a good default if GPU support is not guaranteed or configured.
        session = onnxruntime.InferenceSession(model_path, providers=['CPUExecutionProvider'])
        print(f"ONNX model loaded successfully from {model_path}")
        return session
    except Exception as e:
        print(f"Error loading ONNX model from {model_path}: {e}")
        # Consider re-raising or handling more gracefully depending on application needs
        raise

def run_onnx_inference(session: onnxruntime.InferenceSession, input_data: Dict[str, np.ndarray]) -> List[Any]:
    """
    Runs inference on a loaded ONNX model.

    Args:
        session (onnxruntime.InferenceSession): The ONNX inference session.
        input_data (Dict[str, np.ndarray]): A dictionary where keys are input names
                                           and values are numpy arrays.

    Returns:
        List[Any]: A list of outputs from the model.

    Raises:
        Exception: If inference fails.
    """
    try:
        input_feed = {name: data for name, data in input_data.items()}
        output_names = [output.name for output in session.get_outputs()]

        result = session.run(output_names, input_feed)
        print(f"ONNX inference successful. Output names: {output_names}")
        return result
    except Exception as e:
        print(f"Error during ONNX inference: {e}")
        # Consider re-raising or handling
        raise

# Example Usage (commented out as per subtask instructions)
# if __name__ == '__main__':
#     # This is just for demonstration. You'd need a sample ONNX model.
#     # Create a dummy ONNX model file for testing this utility if possible,
#     # or just ensure the functions are syntactically correct.
#     # For example, a simple linear model: y = 2x.
#     #
#     # try:
#     #     # Dummy model path - replace with a real model for actual testing
#     #     dummy_model_path = "dummy_model.onnx"
#     #
#     #     # Create a dummy ONNX file for testing (simplified)
#     #     # Note: This requires 'onnx' library to be installed (pip install onnx)
#     #     # It's not added to requirements.txt as this is example code.
#     #     import onnx
#     #     from onnx import helper
#     #     from onnx import TensorProto
#     #
#     #     X = helper.make_tensor_value_info('input_float', TensorProto.FLOAT, [None, 1])
#     #     Y = helper.make_tensor_value_info('output_float', TensorProto.FLOAT, [None, 1])
#     #     node_def = helper.make_node('Mul', ['input_float', 'two_constant'], ['output_float'])
#     #     two_tensor = helper.make_tensor('two_constant', TensorProto.FLOAT, [1], [2.0])
#     #     graph_def = helper.make_graph([node_def], 'simple-model', [X], [Y], [two_tensor])
#     #     model_def = helper.make_model(graph_def, producer_name='onnx-example')
#     #     onnx.save(model_def, dummy_model_path)
#     #
#     #     sess = load_onnx_model(dummy_model_path)
#     #     sample_input = np.array([[1.0], [2.0], [3.0]], dtype=np.float32)
#     #     outputs = run_onnx_inference(sess, {'input_float': sample_input})
#     #     print(f"Dummy model output: {outputs[0]}") # Should be [[2.0], [4.0], [6.0]]
#     #
#     #     # Clean up the dummy model file
#     #     import os
#     #     os.remove(dummy_model_path)
#     #
#     # except ImportError:
#     #     print("The 'onnx' library is required to run the ONNX model creation example. Please install it.")
#     # except Exception as e:
#     #     print(f"Error in example usage: {e}")
#     pass
