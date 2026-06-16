import torch
import numpy as np

class ModelAdapter:
    def __init__(self, model, framework):
        self.model = model
        self.framework = framework

    def predict(self, X, batch=False, return_array=False):
        """Unified inference method."""
        if self.framework == 'pytorch':
            # Handle PyTorch inference
            self.model.eval()
            if not isinstance(X, torch.Tensor):
                X = torch.tensor(X, dtype=torch.float32)
            with torch.no_grad():
                out = self.model(X)
                if isinstance(out, dict):
                    out = out['affective_space']
                out = out.detach().cpu().numpy()
                
        elif self.framework == 'sklearn':
            # Handle scikit-learn inference
            if hasattr(X, 'numpy'):
                X = X.numpy()
            out = self.model.predict(X)
        else:
            raise ValueError(f"Unknown framework: {self.framework}")
            
        if out.ndim == 1:
            out = out.reshape(1, -1)
            
        if return_array:
            return out
            
        if batch:
            return [(float(out[i, 0]), float(out[i, 1])) for i in range(len(out))]
        return (float(out[0, 0]), float(out[0, 1]))

    def predict_mc_dropout(self, input_data: np.ndarray, n_passes: int = 50):
        if self.framework != 'pytorch':
            val, aro = self.predict(input_data, batch=False)
            return ((val, aro), 0.0, 100.0)
            
        import torch
        self.model.eval()
        dropout_modules = []
        for m in self.model.modules():
            if m.__class__.__name__.startswith('Dropout'):
                dropout_modules.append(m)
                m.train()

        with torch.no_grad():
            input_tensor = torch.tensor(input_data, dtype=torch.float32)
            predictions = []
            for _ in range(n_passes):
                output = self.model(input_tensor)
                va = output['affective_space'] if isinstance(output, dict) else output
                predictions.append(va.detach().cpu().numpy())

        predictions = np.stack(predictions)
        mean_pred = predictions.mean(axis=0)[0]
        std_dev = predictions.std(axis=0).mean()
        
        for m in dropout_modules:
            m.eval()
        
        confidence_score = max(0.0, min(100.0, (1.0 / (1.0 + float(std_dev))) * 100.0))
        return (float(mean_pred[0]), float(mean_pred[1])), float(std_dev), confidence_score
