import numpy as np
import torch
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

class SklearnModelWrapper:
    """Wrapper to make scikit-learn models interface similarly to PyTorch models."""
    def __init__(self, model):
        self.model = model

    def parameters(self):
        """Dummy generator to satisfy optimizers if called by accident."""
        yield torch.tensor([0.0], requires_grad=True)

    def fit(self, X, y):
        """Train the underlying scikit-learn model."""
        if hasattr(X, 'numpy'):
            X = X.numpy()
        else:
            X = np.array(X)
        if hasattr(y, 'numpy'):
            y = y.numpy()
        else:
            y = np.array(y)
        self.model.fit(X, y)

    def __call__(self, X_tensor):
        """Mock forward pass to return PyTorch tensors."""
        if hasattr(X_tensor, 'numpy'):
            X = X_tensor.numpy()
        else:
            X = np.array(X_tensor)
        
        preds = self.model.predict(X)
        return torch.tensor(preds, dtype=torch.float32)

    def eval(self):
        """Mock behavior for eval mode."""
        pass

    def train(self):
        """Mock behavior for train mode."""
        pass

def get_random_forest_model():
    base_rf = RandomForestRegressor(n_estimators=100, random_state=42)
    model = make_pipeline(StandardScaler(), MultiOutputRegressor(base_rf))
    return SklearnModelWrapper(model)

def get_ridge_model():
    base_ridge = Ridge(alpha=1.0)
    model = make_pipeline(StandardScaler(), MultiOutputRegressor(base_ridge))
    return SklearnModelWrapper(model)
