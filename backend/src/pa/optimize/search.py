"""Seeded candidate search over independent room inputs only."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from pydantic import ValidationError

from pa.features.schema import RoomInput
from pa.features.support import StudiedSupport, SupportResult
from pa.modeling.artifact import LoadedArtifact
from pa.modeling.predict import Prediction, predict_room
from pa.scoring.neuro_score import AffectPoint
from pa.signals.common import decisions


@dataclass(frozen=True)
class Candidate:
    room: RoomInput
    prediction: Prediction
    support: SupportResult


@dataclass(frozen=True)
class SearchResult:
    status: str
    candidates: tuple[Candidate, ...]
    samples_evaluated: int
    reason: str | None


def _identity(room: RoomInput) -> tuple:
    return tuple(sorted(room.model_dump(mode="json").items()))


def _sample_room(rng: np.random.Generator, support: StudiedSupport,
                 eligible: list[RoomInput]) -> RoomInput | None:
    sampled: dict = {}
    for field in RoomInput.model_fields:
        values = [getattr(room, field) for room in eligible if getattr(room, field) is not None]
        if not values:
            continue
        if field in ("day_or_night", "space_type", "num_doors", "num_windows"):
            sampled[field] = values[int(rng.integers(len(values)))]
        elif field in ("length", "width", "height", "door_area", "window_area",
                       "daylight_factor", "illuminance", "cct", "walkable_floor_area"):
            sampled[field] = float(rng.uniform(min(values), max(values)))
    try:
        return RoomInput.model_validate(sampled)
    except ValidationError:
        return None


def search(artifact: LoadedArtifact | None, support: StudiedSupport, target: AffectPoint,
           *, space_type: str | None = None, day_or_night: str | None = None,
           budget: int | None = None, n_candidates: int | None = None,
           seed: int | None = None) -> SearchResult:
    cfg = decisions()["optimizer"]
    budget = cfg["default_budget"] if budget is None else budget
    n_candidates = cfg["default_candidates"] if n_candidates is None else n_candidates
    seed = decisions()["modeling"]["random_seed"] if seed is None else seed
    if not 1 <= budget <= cfg["max_budget"] or not 1 <= n_candidates <= cfg["max_candidates"]:
        raise ValueError("search budget or candidate count outside configured bounds")
    if artifact is None:
        return SearchResult("unavailable", (), 0, "model artifact unavailable")
    eligible = [room for room in support.rooms
                if (space_type is None or room.space_type == space_type) and
                   (day_or_night is None or room.day_or_night == day_or_night)]
    if not eligible:
        return SearchResult("empty", (), 0, "no studied room has the requested categories")
    rng = np.random.default_rng(seed)
    seen: set[tuple] = set()
    candidates: list[Candidate] = []
    evaluated = 0
    # Include known feasible independent configurations; subsequent draws explore nearby space.
    initial = eligible.copy()
    rng.shuffle(initial)
    for attempt in range(budget):
        room = initial.pop() if initial else _sample_room(rng, support, eligible)
        if room is None:
            continue
        key = _identity(room)
        if key in seen:
            continue
        seen.add(key)
        evidence = support.assess(room)
        if evidence.status != "supported":
            continue
        evaluated += 1
        predicted = predict_room(artifact, room, target)
        candidates.append(Candidate(room, predicted, evidence))
    candidates.sort(key=lambda candidate: (-candidate.prediction.neuro_score,
                                           _identity(candidate.room)))
    if not candidates:
        return SearchResult("empty", (), evaluated, "no valid supported distinct candidates")
    return SearchResult("ok", tuple(candidates[:n_candidates]), evaluated, None)
