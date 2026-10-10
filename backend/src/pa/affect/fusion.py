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
    eeg_arousal: float | None
    eeg_arousal_scope: str
    physiology_scope: str


def construct_affect(components: dict[str, float | None],
                     subjective: dict[str, float | None],
                     alpha: float | None = None) -> AffectConstruction:
    """Missing axes remain missing; partial objective never enters full cohort."""
    alpha = decisions()["affect"]["primary_alpha"] if alpha is None else alpha
    if not 0 <= alpha <= 1:
        raise ValueError("alpha outside [0,1]")
    valence = components.get("faa")
    alpha_component = components.get("alpha_suppression")
    engagement = components.get("engagement")
    heart_rate = components.get("heart_rate_bpm")
    eeg_arousal = (0.5 * (alpha_component + engagement)
                   if alpha_component is not None and engagement is not None else None)
    if eeg_arousal is not None:
        eeg_scope = "composite"
    elif alpha_component is not None:
        eeg_scope = "alpha_suppression_only"
    elif engagement is not None:
        eeg_scope = "engagement_only"
    else:
        eeg_scope = "unavailable"
    if eeg_arousal is not None and heart_rate is not None:
        arousal = 0.5 * eeg_arousal + 0.5 * heart_rate
        physiology_scope = "complete" if valence is not None else "partial_arousal_only"
    elif eeg_arousal is not None:
        arousal = eeg_arousal
        physiology_scope = "partial_EEG"
    elif heart_rate is not None:
        arousal = heart_rate
        physiology_scope = "partial_HR"
    else:
        arousal = None
        physiology_scope = "partial_axis" if valence is not None else "unavailable"
    objective = {"valence": valence, "arousal": arousal}
    fused = {axis: (alpha * objective[axis] + (1 - alpha) * subjective[axis]
                    if objective[axis] is not None and subjective.get(axis) is not None else None)
             for axis in ("valence", "arousal")}
    available = tuple(name for name in ("faa", "alpha_suppression", "engagement",
                                      "heart_rate_bpm", "rmssd_ms")
                      if components.get(name) is not None)
    full_objective = all(components.get(name) is not None for name in
                         ("faa", "alpha_suppression", "engagement", "heart_rate_bpm"))
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
                              available, cohort, alpha, eeg_arousal, eeg_scope,
                              physiology_scope)
