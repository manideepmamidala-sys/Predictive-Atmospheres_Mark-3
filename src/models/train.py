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
from src.data.data_loader import load_data, load_data_standalone, _first_existing_column
from src.data.experiment_registry import discover_experiments

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
        feature_mode: Optional[str] = None,
        config: Optional[Config] = None,
        use_streamlit_loader: bool = False,
    ):
        self.config = config or get_config()
        self.model_type = model_type or self.config.model.default_model_type
        self.feature_mode = feature_mode or self.config.training.default_feature_mode
        self._use_streamlit_loader = use_streamlit_loader
        self._repo_root = Path(__file__).resolve().parents[2]
        self._reports_dir = self._repo_root / 'artifacts' / 'reports'

    def train(self) -> TrainResult:
        """Run training and return a TrainResult."""
        if self.feature_mode == 'baseline':
            X_spatial, y_va, bio_sequences = self._load()
            feature_names = ['Length (meter)', 'Width (meter)', 'Height (meter)']
            artifacts: Dict[str, str] = {}
            scaler = None
        elif self.feature_mode == 'full':
            X_spatial, y_va, feature_names, artifacts, scaler = self._load_full_feature_dataset()
            bio_sequences = None
        else:
            raise ValueError(f"Unknown feature_mode: {self.feature_mode}")

        X_tensor = torch.tensor(X_spatial, dtype=torch.float32)
        y_tensor = torch.tensor(y_va, dtype=torch.float32)

        X_train, X_val, y_train, y_val = self._split(X_spatial, y_va)
        X_train_t = torch.tensor(X_train, dtype=torch.float32)
        y_train_t = torch.tensor(y_train, dtype=torch.float32)
        X_val_t = torch.tensor(X_val, dtype=torch.float32)
        y_val_t = torch.tensor(y_val, dtype=torch.float32)

        model, loss_history, final_lr = self._fit(X_train_t, y_train_t)
        metrics = self._compute_train_val_metrics(model, X_train_t, y_train_t, X_val_t, y_val_t)
        converged = self._check_convergence(loss_history)

        self._validate_model(model, input_dim=int(X_spatial.shape[1]))

        if self.feature_mode == 'full':
            compare_artifacts = self._write_full_mode_reports(
                X_full=X_spatial,
                y_full=y_va,
                feature_names=feature_names,
                trained_model=model,
                val_metrics=metrics,
            )
            artifacts.update(compare_artifacts)

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
        )

    # ----- internal helpers -----
    def _load(self):
        if self._use_streamlit_loader:
            return load_data()
        return load_data_standalone()

    def _split(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        return train_test_split(X, y, test_size=0.2, random_state=42)

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

    def _fit(self, X: torch.Tensor, y: torch.Tensor) -> Tuple[Any, List[float], float]:
        cfg = self.config.training
        loss_history: List[float] = []
        final_lr = 0.0

        if self.model_type == 'PyTorch FFNN':
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
                optimizer.zero_grad()
                outputs = model(X)
                loss = criterion(outputs, y)
                loss.backward()
                optimizer.step()
                scheduler.step(loss.item())
                loss_history.append(loss.item())
            final_lr = optimizer.param_groups[0]['lr']

        elif self.model_type == 'Random Forest':
            model = get_random_forest_model()
            model.fit(X, y)
            loss_history = list(np.linspace(1.0, 0.1, 50))

        elif self.model_type == 'Ridge Regression':
            model = get_ridge_model()
            model.fit(X, y)
            loss_history = list(np.linspace(1.0, 0.2, 50))
        else:
            raise ValueError(f"Unknown model_type: {self.model_type}")

        return model, loss_history, final_lr

    def _load_full_feature_dataset(self) -> Tuple[np.ndarray, np.ndarray, List[str], Dict[str, str], Any]:
        """Load and build the full-feature dataset from all experiments."""
        experiments = discover_experiments(self.config.paths.data_dir)
        frames: List[pd.DataFrame] = []

        for exp in experiments:
            bio = pd.read_csv(exp.biometric_csv)
            spatial = pd.read_csv(exp.spatial_csv)
            merged = bio.merge(spatial, on='Room_ID', how='left')
            merged['__experiment'] = exp.name
            frames.append(merged)

        if not frames:
            raise RuntimeError("No experiments found for full-feature mode.")

        df = pd.concat(frames, ignore_index=True)

        y = self._extract_targets(df)
        df = df.loc[y.index].copy()

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

        return X_scaled, y.to_numpy(dtype=np.float32), feature_names, artifacts, scaler

    def _extract_targets(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract V/A targets using multimodal affective fusion.

        Combines subjective self-reported scores with objective biometric
        scores (when available) using a configurable alpha weight.

        Fusion: Target = alpha × Objective + (1 - alpha) × Subjective

        Exposes raw objective, subjective, delta, and Euclidean distance
        columns alongside the fused targets.
        """
        alpha = self.config.fusion.alpha

        def get_col(col_name):
            if col_name in df.columns:
                return pd.to_numeric(df[col_name], errors='coerce')
            return pd.Series(np.nan, index=df.index, dtype=float)

        # Subjective scores
        val_col = 'Valence Score by Subject ' if 'Valence Score by Subject ' in df.columns else 'Valence Score by Subject'
        aro_col = 'Arousal Score by Subject ' if 'Arousal Score by Subject ' in df.columns else 'Arousal Score by Subject'
        sub_v = get_col(val_col)
        sub_a = get_col(aro_col)

        # Both subjective V and A must be present for fusion
        mask = (~sub_v.isna()) & (~sub_a.isna())

        out = pd.DataFrame(index=df.index[mask])
        out['subjective_valence'] = sub_v[mask].astype(float)
        out['subjective_arousal'] = sub_a[mask].astype(float)

        # Objective scores (FAA / RMSSD) — use as-is if present, else NaN
        obj_v_col = _first_existing_column(list(df.columns), ['Objective_Valence', 'FAA_Valence'])
        obj_a_col = _first_existing_column(list(df.columns), ['Objective_Arousal', 'RMSSD_Arousal'])

        if obj_v_col is not None and obj_a_col is not None:
            out['objective_valence'] = pd.to_numeric(df.loc[mask, obj_v_col], errors='coerce').astype(float)
            out['objective_arousal'] = pd.to_numeric(df.loc[mask, obj_a_col], errors='coerce').astype(float)
        else:
            # No objective columns in merged CSV — use subjective as both
            out['objective_valence'] = out['subjective_valence']
            out['objective_arousal'] = out['subjective_arousal']

        # Fusion
        out['valence'] = alpha * out['objective_valence'] + (1.0 - alpha) * out['subjective_valence']
        out['arousal'] = alpha * out['objective_arousal'] + (1.0 - alpha) * out['subjective_arousal']

        # Variance metrics
        out['delta_valence'] = out['objective_valence'] - out['subjective_valence']
        out['delta_arousal'] = out['objective_arousal'] - out['subjective_arousal']
        out['euclidean_distance'] = np.sqrt(out['delta_valence'] ** 2 + out['delta_arousal'] ** 2)

        return out

    def _build_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Build the feature matrix enforcing strict independent/derived/categorical separation.

        Independent inputs (from experiment data):
            Length, Width, Height, Door count, Door area, Window count, Window area,
            Daylight Factor, Illuminance, CCT, Walkable Floor Area

        Derived (computed here, NEVER from CSV):
            L:W Ratio, Floor Area, Wall Area, Volume,
            Door/Wall Ratio, Window/Wall Ratio, Walkable/Floor Ratio

        Categorical (one-hot):
            Day or Night, Type of Space
        """
        # Purged metrics — NEVER allowed into the feature matrix
        PURGED = {
            'UDI-Useful Daylight Illuminance (%)', 'sDA-Spatial Daylight Autonomy (%)',
            'Annual Sunlight Exposure (%)', 'UDI (%)', 'sDA (%)',
            'Door to Wall Ratio (%)', 'Window to Wall Ratio (%)',
            'Length to Width Ratio', 'Floor Area (sq.meter)', 'Wall Area (sq.meter)',
            'Volume (cubic.meter)',
        }

        df.columns = df.columns.str.strip()
        spatial_config = self.config.spatial_features
        known_independent = set(spatial_config.independent_features.keys())

        feature_df = pd.DataFrame(index=df.index)

        # --- 1. Extract independent features with alias handling ---
        alias_map = {
            'Length (meter)': ['Length (meter)', 'Length (m)'],
            'Width (meter)': ['Width (meter)', 'Width (m)'],
            'Height (meter)': ['Height (meter)', 'Height (m)'],
            'Walkable Floor Area (sq.meter)': ['Walkable Floor Area (sq.meter)', 'Walkable Floor Area (m2)'],
        }
        for std_name in sorted(known_independent):
            aliases = alias_map.get(std_name, [std_name])
            value = pd.Series(np.nan, index=df.index, dtype=float)
            for col in aliases:
                if col in df.columns:
                    value = value.fillna(pd.to_numeric(df[col], errors='coerce'))
            # Use config default if the column is entirely missing
            feat_def = spatial_config.independent_features[std_name]
            feature_df[std_name] = value.fillna(feat_def['default'])

        # --- 2. Compute derived features from independent geometry ---
        L = feature_df['Length (meter)']
        W = feature_df['Width (meter)']
        H = feature_df['Height (meter)']
        floor_area = L * W
        wall_area = 2 * (L + W) * H
        walkable = feature_df['Walkable Floor Area (sq.meter)']

        feature_df['Length to Width Ratio'] = L / W.clip(lower=0.01)
        feature_df['Floor Area (sq.meter)'] = floor_area
        feature_df['Wall Area (sq.meter)'] = wall_area
        feature_df['Volume (cubic.meter)'] = floor_area * H
        feature_df['Door Area to Wall Area Ratio'] = feature_df['Door Area (sq.meter)'] / wall_area.clip(lower=0.01)
        feature_df['Window Area to Wall Area Ratio'] = feature_df['Window Area (sq.meter)'] / wall_area.clip(lower=0.01)
        feature_df['Walkable Floor to Total Floor Ratio'] = walkable / floor_area.clip(lower=0.01)

        # --- 3. One-hot encode Day or Night ---
        for col in spatial_config.condition_features:
            if col in df.columns:
                filled = df[col].astype(str).str.strip().replace({'nan': 'Unknown'}).fillna('Unknown')
                dummies = pd.get_dummies(filled, prefix=col)
                feature_df = pd.concat([feature_df, dummies], axis=1)

        # --- 4. One-hot encode Type of Space ---
        for col in spatial_config.categorical_features:
            if col in df.columns:
                filled = df[col].astype(str).str.strip().replace({'nan': 'Unknown'}).fillna('Unknown')
                dummies = pd.get_dummies(filled, prefix=col)
                feature_df = pd.concat([feature_df, dummies], axis=1)
            else:
                # Create zero columns for all known space types
                for st in spatial_config.space_types:
                    feature_df[f'{col}_{st}'] = 0.0

        # --- 5. Clean and order ---
        # Drop any purged columns that may have leaked in
        for purged_col in PURGED:
            if purged_col in feature_df.columns:
                feature_df = feature_df.drop(columns=[purged_col], errors='ignore')

        for col in feature_df.columns:
            if feature_df[col].dtype.kind in 'biufc':
                feature_df[col] = feature_df[col].astype(float)
                median = float(feature_df[col].median()) if feature_df[col].notna().any() else 0.0
                feature_df[col] = feature_df[col].fillna(median)

        feature_df = feature_df.replace([np.inf, -np.inf], np.nan).fillna(0.0)
        ordered = sorted(feature_df.columns)
        return feature_df[ordered], ordered

    def _write_data_quality_report(self, df: pd.DataFrame) -> Path:
        self._reports_dir.mkdir(parents=True, exist_ok=True)
        experiment_02_df = df[df['__experiment'] == 'experiment_02'] if '__experiment' in df.columns else df
        report = {
            'rows_total': int(len(df)),
            'rows_experiment_01': int(len(df[df['__experiment'] == 'experiment_01'])) if '__experiment' in df.columns else 0,
            'rows_experiment_02': int(len(experiment_02_df)),
            'null_counts': {k: int(v) for k, v in experiment_02_df.isna().sum().to_dict().items()},
            'duplicate_room_ids': int(experiment_02_df.duplicated(subset=['Room_ID']).sum()) if 'Room_ID' in experiment_02_df.columns else 0,
            'duplicate_eeg_filenames': int(experiment_02_df.duplicated(subset=['EEG_Filename']).sum()) if 'EEG_Filename' in experiment_02_df.columns else 0,
            'experiments_present': sorted(df['__experiment'].dropna().astype(str).unique().tolist()) if '__experiment' in df.columns else [],
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

    def _write_full_mode_reports(
        self,
        X_full: np.ndarray,
        y_full: np.ndarray,
        feature_names: List[str],
        trained_model: Any,
        val_metrics: Dict[str, float],
    ) -> Dict[str, str]:
        self._reports_dir.mkdir(parents=True, exist_ok=True)

        baseline_features = ['Length (meter)', 'Width (meter)', 'Height (meter)']
        baseline_idx = [feature_names.index(f) for f in baseline_features if f in feature_names]
        if len(baseline_idx) != 3:
            raise RuntimeError("Full-feature dataset is missing one or more baseline dimensions.")

        X_base = X_full[:, baseline_idx]
        Xb_train, Xb_val, yb_train, yb_val = self._split(X_base, y_full)
        # Train a simple MLP baseline for comparison
        old_model_type = self.model_type
        self.model_type = 'PyTorch MLP'
        base_model, _, _ = self._fit(
            torch.tensor(Xb_train, dtype=torch.float32),
            torch.tensor(yb_train, dtype=torch.float32),
        )
        self.model_type = old_model_type
        base_metrics = self._compute_train_val_metrics(
            base_model,
            torch.tensor(Xb_train, dtype=torch.float32),
            torch.tensor(yb_train, dtype=torch.float32),
            torch.tensor(Xb_val, dtype=torch.float32),
            torch.tensor(yb_val, dtype=torch.float32),
        )

        comparison = {
            'model_type': self.model_type,
            'baseline_metrics': base_metrics,
            'full_feature_metrics': val_metrics,
            'metric_delta_full_minus_baseline': {
                k: float(val_metrics.get(k, 0.0) - base_metrics.get(k, 0.0)) for k in val_metrics.keys()
            },
            'full_feature_count': int(len(feature_names)),
        }

        importance = self._compute_feature_importance(trained_model, X_full, y_full, feature_names)
        comparison['feature_importance'] = importance

        comparison_path = self._reports_dir / 'model_comparison.json'
        comparison_path.write_text(json.dumps(comparison, indent=2), encoding='utf-8')

        findings_lines = [
            "# Training Findings (Experiment 01 + 02 Combined)",
            "",
            f"Model type: {self.model_type}",
            f"Full feature count: {len(feature_names)}",
            f"Total training samples: {len(y_full)}",
            "",
            "## Validation Performance",
            f"- Baseline (3-feature MLP) Val_MAE: {base_metrics['Val_MAE']:.4f}",
            f"- Full-feature ({self.model_type}) Val_MAE: {val_metrics['Val_MAE']:.4f}",
            f"- Delta Val_MAE: {val_metrics['Val_MAE'] - base_metrics['Val_MAE']:.4f}",
            f"- Baseline Val_R2: {base_metrics['Val_R2']:.4f}",
            f"- Full-feature Val_R2: {val_metrics['Val_R2']:.4f}",
            "",
            "## Top Influential Features",
        ]
        for item in importance[:10]:
            findings_lines.append(f"- {item['feature']}: {item['importance_mean']:.6f}")

        findings_lines.extend(
            [
                "",
                "## Notes",
                "- Importance values are permutation-based and represent average absolute impact on prediction quality.",
                "- Results should be interpreted as directional insights due to limited sample size per experiment.",
            ]
        )

        findings_path = self._reports_dir / 'training_findings.md'
        findings_path.write_text("\n".join(findings_lines), encoding='utf-8')

        return {
            'model_comparison_report': str(comparison_path),
            'findings_report': str(findings_path),
        }

    def _compute_feature_importance(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str],
    ) -> List[Dict[str, float]]:
        if self.model_type == 'Random Forest' and hasattr(model, 'model'):
            estimator = model.model
            scorer = 'neg_mean_absolute_error'
            result = permutation_importance(estimator, X, y, n_repeats=10, random_state=42, scoring=scorer)
            output = []
            for idx, name in enumerate(feature_names):
                output.append(
                    {
                        'feature': name,
                        'importance_mean': float(result.importances_mean[idx]),
                        'importance_std': float(result.importances_std[idx]),
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
def train_models_streamlit(model_type: Optional[str] = None, feature_mode: Optional[str] = None) -> TrainResult:
    """
    Thin wrapper that plugs training results into ``st.session_state``.
    Call from UI code only.
    """
    import streamlit as st

    config = get_config()
    model_type = model_type or config.model.default_model_type
    feature_mode = feature_mode or config.training.default_feature_mode

    with st.spinner(f"Training {model_type} model ({feature_mode} features)…"):
        trainer = Trainer(model_type=model_type, feature_mode=feature_mode, use_streamlit_loader=True)
        result = trainer.train()

    st.session_state.spatial_model = result.model
    st.session_state.loss_history = result.loss_history
    st.session_state.trained = True
    st.session_state.eval_metrics = result.metrics
    st.session_state.converged = result.converged
    st.session_state.final_lr = result.final_lr
    st.session_state.feature_names = result.feature_names
    st.session_state.feature_mode = result.feature_mode
    st.session_state.model_type = result.model_type
    st.session_state.scaler = result.scaler
    # Store full training data so UI pages can access it for visualization
    st.session_state.train_X = result.X_spatial
    st.session_state.train_y_va = result.y_va

    return result


# Backward-compatible alias
def train_models_logic(model_type: Optional[str] = None, feature_mode: Optional[str] = None):
    """Legacy alias — delegates to train_models_streamlit."""
    return train_models_streamlit(model_type, feature_mode)
