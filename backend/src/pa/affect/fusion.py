"""Explicit component, objective, self-report and fusion availability."""

from __future__ import annotations

from dataclasses import dataclass

from pa.signals.common import decisions


@dataclass(frozen=True)
class AffectConstruction:
    subjective: dict[str, float | None]
    objective: dict[str, float | None]
    fused: dict[str, float | None]
    components: dict[str, float | None]
    available_components: tuple[str, ...]
    cohort: str
    alpha: float


def construct_affect(components: dict[str, float | None],
                     subjective: dict[str, float | None],
                     alpha: float | None = None) -> AffectConstruction:
    """Missing axes remain missing; partial objective never enters full cohort."""
    alpha = decisions()["affect"]["primary_alpha"] if alpha is None else alpha
    if not 0 <= alpha <= 1:
        raise ValueError("alpha outside [0,1]")
    valence = components.get("faa")
    arousal_inputs = [components.get("beta_alpha"), components.get("heart_rate_bpm")]
    if components.get("rmssd_ms") is not None:
        arousal_inputs.append(-components["rmssd_ms"])
    arousal = sum(value for value in arousal_inputs if value is not None) / sum(
        value is not None for value in arousal_inputs) if any(
            value is not None for value in arousal_inputs) else None
    objective = {"valence": valence, "arousal": arousal}
    fused = {axis: (alpha * objective[axis] + (1 - alpha) * subjective[axis]
                    if objective[axis] is not None and subjective.get(axis) is not None else None)
             for axis in ("valence", "arousal")}
    available = tuple(name for name in ("faa", "beta_alpha", "heart_rate_bpm", "rmssd_ms")
                      if components.get(name) is not None)
    full_objective = len(available) == 4
    both_subjective = all(subjective.get(axis) is not None for axis in ("valence", "arousal"))
    both_fused = all(fused[axis] is not None for axis in ("valence", "arousal"))
    if full_objective and both_subjective and both_fused:
        cohort = "complete_fusion"
    elif both_fused:
        cohort = "partial_modality_fusion"
    elif any(value is not None for value in objective.values()) and any(
            value is not None for value in subjective.values()):
        cohort = "partial_axis_overlap"
    elif any(value is not None for value in objective.values()):
        cohort = "objective_only"
    elif any(value is not None for value in subjective.values()):
        cohort = "subjective_only"
    else:
        cohort = "unavailable"
    return AffectConstruction(dict(subjective), objective, fused, dict(components),
                              available, cohort, alpha)
