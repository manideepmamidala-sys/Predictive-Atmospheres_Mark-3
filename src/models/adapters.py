"""
Model adapters for standardized predictions across PyTorch, Scikit-Learn, and ONNX.
"""
from abc import ABC, abstractmethod
from typing import Any, Tuple, Union, List
import numpy as np


class BaseModelAdapter(ABC):
    """
    Abstract interface for room emotional prediction models.
    """

    @abstractmethod
    def predict(self, input_data: np.ndarray, batch: bool = False) -> Union[Tuple[float, float], List[Tuple[float, float]]]:
        """
        Run model prediction.

        Args:
            input_data: Numpy array of input features (shape: 1xD or NxD)
            batch: Whether to return a batch of predictions

        Returns:
            Tuple of (valence, arousal) or List of such tuples.
        """
        pass

    @property
    def supports_gradients(self) -> bool:
        """Does this model support gradient-based optimization?"""
        return False


class PyTorchAdapter(BaseModelAdapter):
    def __init__(self, model: Any):
        self.model = model
        self.model.eval()

    def predict(self, input_data: np.ndarray, batch: bool = False) -> Union[Tuple[float, float], List[Tuple[float, float]]]:
        import torch

        with torch.no_grad():
            input_tensor = torch.tensor(input_data, dtype=torch.float32)
            output = self.model(input_tensor)

            if isinstance(output, dict):
                va = self._normalize_va_array(output['affective_space'])
            else:
                va = self._normalize_va_array(output)

            if batch:
                return [(float(va[i, 0]), float(va[i, 1])) for i in range(len(va))]
            return (float(va[0, 0]), float(va[0, 1]))

    def _normalize_va_array(self, raw_output: Any) -> np.ndarray:
        if hasattr(raw_output, 'detach') and hasattr(raw_output, 'cpu'):
            raw_output = raw_output.detach().cpu().numpy()
        else:
            raw_output = np.asarray(raw_output)

        if raw_output.ndim == 1:
            raw_output = raw_output.reshape(1, -1)
        return raw_output

    @property
    def supports_gradients(self) -> bool:
        return True

    def get_torch_model(self) -> Any:
        return self.model


class SKLearnAdapter(BaseModelAdapter):
    def __init__(self, model: Any):
        self.model = model

    def predict(self, input_data: np.ndarray, batch: bool = False) -> Union[Tuple[float, float], List[Tuple[float, float]]]:
        predictions = self.model.predict(input_data)
        if predictions.ndim == 1:
            predictions = predictions.reshape(1, -1)

        if batch:
            return [(float(predictions[i, 0]), float(predictions[i, 1])) for i in range(len(predictions))]
        return (float(predictions[0, 0]), float(predictions[0, 1]))



