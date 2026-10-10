"""Bounded, seeded search for the closest requested Neuro-Score."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from pydantic import ValidationError

from pa.features.schema import (
    COUNT_FIELDS,
    INDEPENDENT_FIELDS,
    NUMERIC_FIELDS,
    RoomInput,
    StudioConstraints,
    validate_studio_room,
)
from pa.features.support import StudiedSupport, SupportResult
from pa.modeling.artifact import LoadedArtifact
from pa.modeling.predict import Prediction, predict_room
from pa.scoring.neuro_score import AffectPoint, score_percentage
from pa.signals.common import decisions


@dataclass(frozen=True)
class Candidate:
    room: RoomInput
    prediction: Prediction
    support: SupportResult
    requested_score: float
    achieved_score: float
    absolute_difference: float


@dataclass(frozen=True)
class SearchResult:
    status: str
    candidates: tuple[Candidate, ...]
    samples_evaluated: int
    reason: str | None


def _identity(room: RoomInput) -> tuple:
    return tuple(getattr(room, field) for field in INDEPENDENT_FIELDS)


def _within_constraints(room: RoomInput, constraints: StudioConstraints,
                        space_type: str | None, day_or_night: str | None) -> bool:
    if space_type is not None and room.space_type != space_type:
        return False
    if day_or_night is not None and room.day_or_night != day_or_night:
        return False
    base = constraints.base_room
    if base is not None and any(getattr(room, name) != getattr(base, name)
                                for name in constraints.locked_fields):
        return False
    return all(bounds.minimum <= getattr(room, name) <= bounds.maximum
               for name, bounds in constraints.allowed_ranges.items())


def _bounds(eligible: list[RoomInput], constraints: StudioConstraints) -> dict[str, tuple[float, float]] | None:
    result = {}
    for name in NUMERIC_FIELDS:
        values = [float(getattr(room, name)) for room in eligible
                  if getattr(room, name) is not None]
        if not values:
            return None
        lower, upper = min(values), max(values)
        allowed = constraints.allowed_ranges.get(name)
        if allowed is not None:
            lower, upper = max(lower, allowed.minimum), min(upper, allowed.maximum)
        if name in constraints.locked_fields:
            locked = float(getattr(constraints.base_room, name))
            lower, upper = max(lower, locked), min(upper, locked)
        if lower > upper or (name in COUNT_FIELDS and not any(
                lower <= value <= upper for value in values)):
            return None
        result[name] = (lower, upper)
    return result


def _sample_room(rng: np.random.Generator, eligible: list[RoomInput],
                 constraints: StudioConstraints,
                 bounds: dict[str, tuple[float, float]]) -> RoomInput | None:
    values = {}
    exemplar = eligible[int(rng.integers(len(eligible)))]
    for name in INDEPENDENT_FIELDS:
        if name in constraints.locked_fields:
            values[name] = getattr(constraints.base_room, name)
        elif name in ("day_or_night", "space_type"):
            values[name] = getattr(exemplar, name)
        elif name in COUNT_FIELDS:
            choices = sorted({getattr(room, name) for room in eligible
                              if bounds[name][0] <= getattr(room, name) <= bounds[name][1]})
            values[name] = choices[int(rng.integers(len(choices)))]
        else:
            lower, upper = bounds[name]
            values[name] = float(rng.uniform(lower, upper)) if lower < upper else lower
    try:
        return RoomInput.model_validate(values)
    except ValidationError:
        return None


def search(artifact: LoadedArtifact | None, support: StudiedSupport, target: AffectPoint,
           *, requested_score: float = 100.0, base_room: RoomInput | None = None,
           locked_fields: list[str] | None = None,
           allowed_ranges: dict | None = None,
           space_type: str | None = None, day_or_night: str | None = None,
           budget: int | None = None, n_candidates: int | None = None,
           seed: int | None = None) -> SearchResult:
    cfg = decisions()["optimizer"]
    budget = cfg["default_budget"] if budget is None else budget
    n_candidates = cfg["default_candidates"] if n_candidates is None else n_candidates
    seed = decisions()["modeling"]["random_seed"] if seed is None else seed
    if not 1 <= budget <= cfg["max_budget"] or not 1 <= n_candidates <= cfg["max_candidates"]:
        raise ValueError("search budget or candidate count outside configured bounds")
    if not np.isfinite(requested_score) or not 0 <= requested_score <= 100:
        raise ValueError("requested_score must be on the 0–100 scale")
    constraints = StudioConstraints.model_validate({
        "base_room": base_room, "locked_fields": locked_fields or [],
        "allowed_ranges": allowed_ranges or {},
    })
    if artifact is None:
        return SearchResult("unavailable", (), 0, "model artifact unavailable")
    eligible = [room for room in support.rooms
                if (space_type is None or room.space_type == space_type)
                and (day_or_night is None or room.day_or_night == day_or_night)]
    if not eligible:
        return SearchResult("empty", (), 0, "no studied room has the requested categories")
    bounds = _bounds(eligible, constraints)
    if bounds is None:
        return SearchResult("empty", (), 0, "locks or allowed ranges exclude observed support")

    rng = np.random.default_rng(seed)
    base = constraints.base_room
    initial = ([base] if base is not None and _within_constraints(
        base, constraints, space_type, day_or_night) else [])
    initial += [room for room in sorted(eligible, key=_identity)
                if _within_constraints(room, constraints, space_type, day_or_night)]
    seen: set[tuple] = set()
    candidates: list[Candidate] = []
    evaluated = 0
    for attempt in range(budget):
        room = initial[attempt] if attempt < len(initial) else _sample_room(
            rng, eligible, constraints, bounds)
        if room is None or not _within_constraints(room, constraints, space_type, day_or_night):
            continue
        validate_studio_room(room)
        key = _identity(room)
        if key in seen:
            continue
        seen.add(key)
        evidence = support.assess(room)
        if evidence.status != "supported":
            continue
        predicted = predict_room(artifact, room, target)
        achieved = score_percentage(predicted.neuro_score)
        candidates.append(Candidate(room, predicted, evidence, requested_score,
                                    achieved, abs(achieved - requested_score)))
        evaluated += 1
    candidates.sort(key=lambda candidate: (candidate.absolute_difference,
                                           candidate.support.standardized_distance,
                                           _identity(candidate.room)))
    if not candidates:
        return SearchResult("empty", (), evaluated,
                            "no physically valid, supported candidate was found within this "
                            "search budget under the supplied locks and ranges")
    return SearchResult("ok", tuple(candidates[:n_candidates]), evaluated, None)
