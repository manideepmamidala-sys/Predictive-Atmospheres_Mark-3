"""
Model Training Module
=====================
Pure-Python training logic — NO Streamlit dependency.

Supports:
  - SpatialFFNN (extended room features → V/A) — DEFAULT
  - SpatialMLP (basic room dims → V/A) — LEGACY
  - scikit-learn alternatives (RandomForest, Ridge)
  - Config-driven hyperparameters
  - Standalone and Streamlit modes

Usage (standalone):
    from src.models.train import Trainer
    trainer = Trainer()
    result = trainer.train()

Usage (Streamlit — via wrapper):
    from src.models.train import train_models_streamlit
    train_models_streamlit()
"""
import logging
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.config import get_config, Config
from src.models.architectures import SpatialMLP, SpatialFFNN
from src.models.sklearn_models import get_random_forest_model, get_ridge_model
from src.models.adapter import ModelAdapter

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Training result container
# ---------------------------------------------------------------------------
@dataclass
class TrainResult:
    """Immutable result of a training run."""
    model: Any
    loss_history: List[float]
    metrics: Dict[str, float]
    converged: bool
    final_lr: float
    model_type: str
    X_spatial: np.ndarray
    y_va: np.ndarray
    feature_mode: str = 'full'
    feature_names: List[str] = field(default_factory=list)
    artifacts: Dict[str, str] = field(default_factory=dict)
    biometric_sequences: Any = None
    scaler: Any = None
    val_loss_history: List[float] = field(default_factory=list)
    parity_df: Optional[pd.DataFrame] = None


# ---------------------------------------------------------------------------
# Evaluation metrics
# ---------------------------------------------------------------------------
def compute_evaluation_metrics(
    model: Any,
    X_tensor: torch.Tensor,
    y_tensor: torch.Tensor,
) -> Dict[str, float]:
    """
    Compute regression metrics: MSE, MAE, R², per-dimension MAE.

    Works with both PyTorch and sklearn-wrapper models.
    """
    # Use unified prediction if available
    if hasattr(model, 'predict'):
        predictions = model.predict(X_tensor, return_array=True)
    else:
        # Fallback for raw PyTorch models
        if hasattr(model, 'eval'):
            model.eval()

        with torch.no_grad():
            raw_output = model(X_tensor)
            if isinstance(raw_output, dict):
                raw_output = raw_output.get('affective_space', raw_output)
            predictions = raw_output.detach().cpu().numpy()

        if hasattr(model, 'train') and callable(getattr(model, 'train')):
            model.train()

    targets = y_tensor.numpy()

    mse = float(np.mean((predictions - targets) ** 2))
    mae = float(np.mean(np.abs(predictions - targets)))

    ss_res = np.sum((targets - predictions) ** 2)
    ss_tot = np.sum((targets - np.mean(targets, axis=0)) ** 2)
    r2 = float(1 - (ss_res / (ss_tot + 1e-6)))

    v_mae = float(np.mean(np.abs(predictions[:, 0] - targets[:, 0])))
    a_mae = float(np.mean(np.abs(predictions[:, 1] - targets[:, 1])))

    return {
        'MSE': mse,
        'MAE': mae,
        'R²': r2,
        'Valence_MAE': v_mae,
        'Arousal_MAE': a_mae,
    }


# ---------------------------------------------------------------------------
# Core trainer (no UI dependency)
# ---------------------------------------------------------------------------
class Trainer:
    """
    Standalone model trainer — usable from CLI, tests, or Streamlit.

    Example::

        trainer = Trainer(model_type='PyTorch FFNN')
        result = trainer.train()
        print(result.metrics)
    """

    def __init__(
        self,
        model_type: Optional[str] = None,
        config: Optional[Config] = None,
        use_streamlit_loader: bool = False,
    ):
        self.config = config or get_config()
        self.model_type = model_type or self.config.model.default_model_type
        self.feature_mode = 'full'
        self._use_streamlit_loader = use_streamlit_loader
        self._repo_root = Path(__file__).resolve().parents[2]
        self._reports_dir = self._repo_root / 'artifacts' / 'reports'

    def train(self) -> TrainResult:
        """Run training and return a TrainResult."""
        X_spatial, y_va, feature_names, artifacts, scaler = self._load_data()

        self.feature_mode = 'full'
        bio_sequences = None

        X_tensor = torch.tensor(X_spatial, dtype=torch.float32)
        y_tensor = torch.tensor(y_va, dtype=torch.float32)

        X_train, X_val, y_train, y_val = self._split(X_spatial, y_va)
        X_train_t = torch.tensor(X_train, dtype=torch.float32)
        y_train_t = torch.tensor(y_train, dtype=torch.float32)
        X_val_t = torch.tensor(X_val, dtype=torch.float32)
        y_val_t = torch.tensor(y_val, dtype=torch.float32)

        model, loss_history, val_loss_history, final_lr = self._fit(X_train_t, y_train_t, X_val_t, y_val_t)
        metrics = self._compute_train_val_metrics(model, X_train_t, y_train_t, X_val_t, y_val_t)
        converged = self._check_convergence(loss_history)

        self._validate_model(model, input_dim=int(X_spatial.shape[1]))

        # Generate Parity Plot Data
        val_preds = model.predict(X_val_t, return_array=True)

        parity_df = pd.DataFrame({
            'Actual_Valence': y_val[:, 0],
            'Predicted_Valence': val_preds[:, 0],
            'Actual_Arousal': y_val[:, 1],
            'Predicted_Arousal': val_preds[:, 1],
        })



        return TrainResult(
            model=model,
            loss_history=loss_history,
            metrics=metrics,
            converged=converged,
            final_lr=final_lr,
            model_type=self.model_type,
            X_spatial=X_spatial,
            y_va=y_va,
            feature_mode=self.feature_mode,
            feature_names=feature_names,
            artifacts=artifacts,
            biometric_sequences=bio_sequences,
            scaler=scaler,
            val_loss_history=val_loss_history,
            parity_df=parity_df,
        )

    # ----- internal helpers -----
    def _split(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        cfg = self.config.training
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=cfg.val_split, random_state=cfg.split_random_state
        )
        return (X_train, X_val, y_train, y_val)

    def _compute_train_val_metrics(
        self,
        model: Any,
        X_train: torch.Tensor,
        y_train: torch.Tensor,
        X_val: torch.Tensor,
        y_val: torch.Tensor,
    ) -> Dict[str, float]:
        train_metrics = compute_evaluation_metrics(model, X_train, y_train)
        val_metrics = compute_evaluation_metrics(model, X_val, y_val)

        def rmse(mse: float) -> float:
            return float(np.sqrt(max(mse, 0.0)))

        return {
            'Train_MAE': train_metrics['MAE'],
            'Train_RMSE': rmse(train_metrics['MSE']),
            'Train_R2': train_metrics['R²'],
            'Train_Valence_MAE': train_metrics['Valence_MAE'],
            'Train_Arousal_MAE': train_metrics['Arousal_MAE'],
            'Val_MAE': val_metrics['MAE'],
            'Val_RMSE': rmse(val_metrics['MSE']),
            'Val_R2': val_metrics['R²'],
            'Val_Valence_MAE': val_metrics['Valence_MAE'],
            'Val_Arousal_MAE': val_metrics['Arousal_MAE'],
        }

    def _fit(self, X: torch.Tensor, y: torch.Tensor, X_val: torch.Tensor, y_val: torch.Tensor) -> Tuple[Any, List[float], List[float], float]:
        cfg = self.config.training
        loss_history: List[float] = []
        val_loss_history: List[float] = []
        final_lr = 0.0

        if self.model_type is None or self.model_type == 'Random Forest':
            self.model_type = 'Random Forest'
            from sklearn.metrics import mean_squared_error
            import joblib
            model = get_random_forest_model()
            model.fit(X, y)
            train_mse = mean_squared_error(y, model.predict(X))
            val_mse = mean_squared_error(y_val, model.predict(X_val))
            loss_history = [float(train_mse)]
            val_loss_history = [float(val_mse)]
            
            model_path = self._repo_root / 'artifacts' / 'models' / 'random_forest.joblib'
            model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, model_path)

        elif self.model_type == 'Ridge Regression':
            from sklearn.metrics import mean_squared_error
            model = get_ridge_model()
            model.fit(X, y)
            train_mse = mean_squared_error(y, model.predict(X))
            val_mse = mean_squared_error(y_val, model.predict(X_val))
            loss_history = [float(train_mse)]
            val_loss_history = [float(val_mse)]

        elif self.model_type == 'PyTorch FFNN':
            model = SpatialFFNN(input_dim=int(X.shape[1]))
            optimizer = optim.Adam(model.parameters(), lr=cfg.learning_rate, weight_decay=1e-4)
            criterion = nn.MSELoss()
            scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode='min',
                factor=cfg.lr_scheduler_factor,
                patience=cfg.lr_scheduler_patience,
            )
            for _epoch in range(cfg.epochs):
                model.train()
                optimizer.zero_grad()
                outputs = model(X)
                loss = criterion(outputs, y)
                loss.backward()
                optimizer.step()
                scheduler.step(loss.item())
                loss_history.append(loss.item())
                
                model.eval()
                with torch.no_grad():
                    val_outputs = model(X_val)
                    val_loss = criterion(val_outputs, y_val)
                    val_loss_history.append(val_loss.item())
                    
            final_lr = optimizer.param_groups[0]['lr']

        elif self.model_type == 'PyTorch MLP':
            model = SpatialMLP(input_dim=int(X.shape[1]))
            optimizer = optim.Adam(model.parameters(), lr=cfg.learning_rate)
            criterion = nn.MSELoss()
            scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                mode='min',
                factor=cfg.lr_scheduler_factor,
                patience=cfg.lr_scheduler_patience,
            )
            for _epoch in range(cfg.epochs):
                model.train()
                optimizer.zero_grad()
                outputs = model(X)
                loss = criterion(outputs, y)
                loss.backward()
                optimizer.step()
                scheduler.step(loss.item())
                loss_history.append(loss.item())
                
                model.eval()
                with torch.no_grad():
                    val_outputs = model(X_val)
                    val_loss = criterion(val_outputs, y_val)
                    val_loss_history.append(val_loss.item())

            final_lr = optimizer.param_groups[0]['lr']
        else:
            raise ValueError(f"Unknown model_type: {self.model_type}")

        if self.model_type in ['PyTorch FFNN', 'PyTorch MLP']:
            adapter = ModelAdapter(model, framework='pytorch')
        else:
            adapter = ModelAdapter(model, framework='sklearn')

        return adapter, loss_history, val_loss_history, final_lr

    def _load_data(self) -> Tuple[np.ndarray, np.ndarray, List[str], Dict[str, str], Any]:
        """Load and build the full-feature dataset from fusion_analysis.parquet."""
        df = pd.read_parquet(self._repo_root / 'data' / 'processed' / 'fusion_analysis.parquet')
        df.fillna(0.0, inplace=True)
        
        y = df[['fused_valence', 'fused_arousal']].to_numpy(dtype=np.float32)

        # Build feature set
        x_df, feature_names = self._build_features(df)

        # Apply StandardScaler for heterogeneous feature ranges
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(x_df.to_numpy(dtype=np.float32))

        quality_path = self._write_data_quality_report(df)
        schema_path = self._write_feature_schema_report(feature_names, x_df)

        artifacts = {
            'data_quality_report': str(quality_path),
            'feature_schema_report': str(schema_path),
        }

        logger.info(f"Full-feature dataset: {X_scaled.shape[0]} rows, {X_scaled.shape[1]} features")
        logger.info(f"Features: {feature_names}")

        import typing
        return typing.cast(Tuple[np.ndarray, np.ndarray, List[str], Dict[str, str], Any], (X_scaled, y, feature_names, artifacts, scaler))

    def _build_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Build the feature matrix enforcing strict independent/derived/categorical separation."""
        feature_df = pd.DataFrame(index=df.index)

        # 11 Independent spatial features
        numeric_cols = [
            "Length_m", "Width_m", "Height_m", "Num_Doors", "Door_Area_m2", 
            "Num_Windows", "Window_Area_m2", "Daylight_Factor_pct", "Illuminance_lux", 
            "CCT_K", "Walkable_Floor_Area_m2"
        ]
        
        for col in numeric_cols:
            if col in df.columns:
                feature_df[col] = df[col]
            else:
                feature_df[col] = 0.0

        # One-hot encode Day/Night
        feature_df['Day_or_Night_Day'] = df.get('Day_or_Night_Day', 0.0)
        feature_df['Day_or_Night_Night'] = df.get('Day_or_Night_Night', 0.0)

        # One-hot encode Space Type
        space_types = ["Bedroom", "Living Room", "Workplace", "Classroom", "Cafeteria"]
        for st in space_types:
            col_name = f'Type_of_Space_{st}'
            feature_df[col_name] = df.get(col_name, 0.0)

        # Compute Derived Features
        feature_df['Length_to_Width_Ratio'] = feature_df['Length_m'] / (feature_df['Width_m'] + 1e-9)
        feature_df['Floor_Area_m2'] = feature_df['Length_m'] * feature_df['Width_m']
        feature_df['Wall_Area_m2'] = 2 * (feature_df['Length_m'] + feature_df['Width_m']) * feature_df['Height_m']
        feature_df['Volume_m3'] = feature_df['Length_m'] * feature_df['Width_m'] * feature_df['Height_m']
        feature_df['Door_to_Wall_Ratio'] = feature_df['Door_Area_m2'] / (feature_df['Wall_Area_m2'] + 1e-9)
        feature_df['Window_to_Wall_Ratio'] = feature_df['Window_Area_m2'] / (feature_df['Wall_Area_m2'] + 1e-9)
        feature_df['Walkable_to_Floor_Ratio'] = feature_df['Walkable_Floor_Area_m2'] / (feature_df['Floor_Area_m2'] + 1e-9)

        ordered = [
            'Length_m', 'Width_m', 'Height_m', 'Num_Doors', 'Door_Area_m2',
            'Num_Windows', 'Window_Area_m2', 'Daylight_Factor_pct', 'Illuminance_lux',
            'CCT_K', 'Walkable_Floor_Area_m2',
            'Day_or_Night_Day', 'Day_or_Night_Night',
            'Type_of_Space_Bedroom', 'Type_of_Space_Living Room', 'Type_of_Space_Workplace',
            'Type_of_Space_Classroom', 'Type_of_Space_Cafeteria',
            'Length_to_Width_Ratio', 'Floor_Area_m2', 'Wall_Area_m2', 'Volume_m3',
            'Door_to_Wall_Ratio', 'Window_to_Wall_Ratio', 'Walkable_to_Floor_Ratio'
        ]
        return feature_df[ordered], ordered

    def _write_data_quality_report(self, df: pd.DataFrame) -> Path:
        self._reports_dir.mkdir(parents=True, exist_ok=True)
        report = {
            'rows_total': int(len(df)),
            'null_counts': {k: int(v) for k, v in df.isna().sum().to_dict().items()},
        }
        out = self._reports_dir / 'data_quality_report.json'
        out.write_text(json.dumps(report, indent=2), encoding='utf-8')
        return out

    def _write_feature_schema_report(self, feature_names: List[str], x_df: pd.DataFrame) -> Path:
        self._reports_dir.mkdir(parents=True, exist_ok=True)
        schema = {
            'feature_count': len(feature_names),
            'features': feature_names,
            'dtypes': {c: str(t) for c, t in x_df.dtypes.items()},
        }
        out = self._reports_dir / 'feature_schema.json'
        out.write_text(json.dumps(schema, indent=2), encoding='utf-8')
        return out


    def _compute_feature_importance(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str],
    ) -> List[Dict[str, Any]]:
        if self.model_type == 'Random Forest':
            estimator = model.model
            scorer = 'neg_mean_absolute_error'
            result = permutation_importance(estimator, X, y, n_repeats=10, random_state=42, scoring=scorer)  # type: ignore
            output = []
            for idx, name in enumerate(feature_names):
                output.append(
                    {
                        'feature': name,
                        'importance_mean': float(result['importances_mean'][idx]),
                        'importance_std': float(result['importances_std'][idx]),
                    }
                )
            output.sort(key=lambda x: x['importance_mean'], reverse=True)
            return output

        # Lightweight fallback for non-RF models.
        baseline = np.mean(np.abs(self._predict(model, X) - y))
        impacts = []
        for i, name in enumerate(feature_names):
            X_perm = X.copy()
            rng = np.random.default_rng(42 + i)
            rng.shuffle(X_perm[:, i])
            mae = np.mean(np.abs(self._predict(model, X_perm) - y))
            impacts.append({'feature': name, 'importance_mean': float(mae - baseline), 'importance_std': 0.0})
        impacts.sort(key=lambda x: x['importance_mean'], reverse=True)
        return impacts

    @staticmethod
    def _predict(model: Any, X: np.ndarray) -> np.ndarray:
        if hasattr(model, 'predict'):
            return model.predict(X, return_array=True)
        # Fallback
        model.eval()
        with torch.no_grad():
            out = model(torch.tensor(X, dtype=torch.float32))
            if isinstance(out, dict):
                out = out['affective_space']
            return out.detach().cpu().numpy()

    def _check_convergence(self, loss_history: List[float]) -> bool:
        cfg = self.config.training
        window = cfg.convergence_window
        if len(loss_history) > window:
            recent_change = abs(loss_history[-1] - loss_history[-window])
            return recent_change < cfg.convergence_threshold
        return False

    def _validate_model(self, model: Any, input_dim: int = 3) -> None:
        """Sanity-check model outputs."""
        probe = torch.zeros((2, input_dim), dtype=torch.float32)
        if input_dim >= 3:
            probe[0, 0] = 10.0
            probe[0, 1] = 8.0
            probe[0, 2] = 3.5
            probe[1, 0] = 5.0
            probe[1, 1] = 4.0
            probe[1, 2] = 2.8
        
        if hasattr(model, 'predict'):
            out = model.predict(probe, return_array=True).flatten()
        else:
            with torch.no_grad():
                model.eval()
                out = model(probe)
                if isinstance(out, dict):
                    out = out['affective_space']
                out = out.detach().cpu().numpy().flatten()

        if np.any(np.isnan(out)) or np.any(np.isinf(out)):
            raise RuntimeError(f"Model diverged: {out}")
        for val in out:
            if not (-2.0 <= val <= 2.0):
                raise RuntimeError(f"Output out of range: {out}")


# ---------------------------------------------------------------------------
# Streamlit convenience wrapper (thin layer)
# ---------------------------------------------------------------------------
def train_models_streamlit(model_type: Optional[str] = None) -> TrainResult:
    """
    Thin wrapper that plugs training results into ``st.session_state``.
    Call from UI code only.
    """
    import streamlit as st

    config = get_config()
    model_type = model_type or config.model.default_model_type

    with st.spinner(f"Training {model_type} model (full features)…"):
        trainer = Trainer(model_type=model_type, use_streamlit_loader=True)
        result = trainer.train()

    st.session_state.spatial_model = result.model
    st.session_state.loss_history = result.loss_history
    st.session_state.val_loss_history = result.val_loss_history
    st.session_state.parity_df = result.parity_df
    st.session_state.trained = True
    st.session_state.eval_metrics = result.metrics
    st.session_state.converged = result.converged
    st.session_state.final_lr = result.final_lr
    st.session_state.feature_names = result.feature_names
    st.session_state.model_type = result.model_type
    st.session_state.scaler = result.scaler
    # Store full training data so UI pages can access it for visualization
    st.session_state.train_X = result.X_spatial
    st.session_state.train_y_va = result.y_va

    return result


# Backward-compatible alias
def train_models_logic(model_type: Optional[str] = None):
    """Legacy alias — delegates to train_models_streamlit."""
    return train_models_streamlit(model_type)
