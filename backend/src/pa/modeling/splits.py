"""Group-disjoint fold membership and deterministic candidate ranking."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from sklearn.model_selection import GroupKFold, LeaveOneGroupOut

from pa.signals.common import decisions


def outer_splits(groups: NDArray) -> list[tuple[NDArray, NDArray]]:
    if len(np.unique(groups)) < 2:
        return []
    return list(LeaveOneGroupOut().split(np.zeros(len(groups)), groups=groups))


def inner_splits(groups: NDArray) -> list[tuple[NDArray, NDArray]]:
    cfg = decisions()["modeling"]
    if len(np.unique(groups)) < cfg["min_training_groups_for_inner_cv"]:
        return []
    return list(GroupKFold(n_splits=cfg["inner_splits"]).split(
        np.zeros(len(groups)), groups=groups))


def candidate_specs() -> list[dict]:
    return decisions()["modeling"]["candidates"]


def choose_candidate(scores: dict[str, float]) -> str:
    """Candidate config key order is frozen simplicity order; near ties prefer earlier."""
    cfg = decisions()["modeling"]
    finite = [score for score in scores.values() if np.isfinite(score)]
    if not finite:
        raise ValueError("no eligible model candidate")
    minimum = min(finite)
    for key in (candidate_key(spec) for spec in candidate_specs()):
        score = scores.get(key, float("inf"))
        if np.isfinite(score) and score <= minimum + cfg["tie_tolerance_mae"]:
            return key
    raise ValueError("no configured eligible model candidate")


def candidate_key(spec: dict) -> str:
    return ":".join(f"{name}={value}" for name, value in sorted(spec.items()))
