"""Preserve investigator-supplied signed ratings without physiological substitution."""

from __future__ import annotations

from pa.io.metadata import Trial


def subjective_axes(trial: Trial) -> dict[str, float | None]:
    """Experiment 1 comfort is not a valence/arousal axis."""
    return {"valence": trial.self_valence, "arousal": trial.self_arousal}


def comfort_score(trial: Trial) -> float | None:
    return trial.comfort
