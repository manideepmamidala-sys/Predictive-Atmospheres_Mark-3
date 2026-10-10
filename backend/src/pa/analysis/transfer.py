"""Known-room relative rating transfer to held-out participants."""

from __future__ import annotations

import numpy as np
from scipy.stats import spearmanr

SEED = 2718
NULL_DRAWS = 1000


def _centered_profiles(rows: list[dict], *, training_people: set[str],
                       rng: np.random.Generator | None = None) -> dict[str, float]:
    by_person: dict[str, list[dict]] = {}
    for row in rows:
        if row["participant_id"] in training_people:
            by_person.setdefault(row["participant_id"], []).append(row)
    values: dict[str, list[float]] = {}
    for person_rows in by_person.values():
        center = float(np.mean([row["value"] for row in person_rows]))
        labels = [row["room_id"] for row in person_rows]
        if rng is not None:
            labels = list(rng.permutation(labels))
        for room, row in zip(labels, person_rows, strict=True):
            values.setdefault(room, []).append(float(row["value"] - center))
    return {room: float(np.mean(samples)) for room, samples in values.items()}


def _fold(rows: list[dict], held_out: str,
          rng: np.random.Generator | None = None) -> dict:
    people = {row["participant_id"] for row in rows}
    train_people = people - {held_out}
    profile = _centered_profiles(rows, training_people=train_people, rng=rng)
    held = [row for row in rows if row["participant_id"] == held_out and
            row["room_id"] in profile]
    if len(held) < 3:
        return {"participant_id": held_out, "status": "unavailable_insufficient_known_rooms",
                "known_rooms": len(held), "training_people": sorted(train_people)}
    center = float(np.mean([row["value"] for row in held]))
    truth = np.asarray([row["value"] - center for row in held], dtype=float)
    predicted = np.asarray([profile[row["room_id"]] for row in held], dtype=float)
    rho = None
    if np.var(truth) > 1e-12 and np.var(predicted) > 1e-12:
        rho = float(spearmanr(truth, predicted).statistic)
    return {"participant_id": held_out, "status": "descriptive_relative",
            "known_rooms": len(held), "room_ids": [row["room_id"] for row in held],
            "training_people": sorted(train_people), "mae": float(np.mean(abs(predicted - truth))),
            "zero_baseline_mae": float(np.mean(abs(truth))), "spearman_rho": rho,
            "prediction": predicted.tolist(), "centered_observed": truth.tolist(),
            "held_out_observed_center": center}


def evaluate_relative_transfer(rows: list[dict], *, draws: int = NULL_DRAWS,
                               seed: int = SEED) -> dict:
    if draws < 0:
        raise ValueError("negative null draw count")
    people = sorted({row["participant_id"] for row in rows})
    rooms = sorted({row["room_id"] for row in rows})
    base = {"trials": len(rows), "participants": len(people), "rooms": len(rooms),
            "null_draws": draws, "estimand": "known-room relative profile; held-out observed mean used only for centering"}
    if len(people) < 4 or len(rooms) < 4:
        return {**base, "status": "unavailable_insufficient_groups"}
    if any(not np.isfinite(row["value"]) for row in rows):
        return {**base, "status": "unavailable_nonfinite_rating"}
    folds = [_fold(rows, person) for person in people]
    eligible = [fold for fold in folds if fold["status"] == "descriptive_relative"]
    if not eligible:
        return {**base, "status": "unavailable_no_eligible_folds", "folds": folds}
    observed = float(np.mean([fold["mae"] for fold in eligible]))
    rng = np.random.default_rng(seed)
    null = []
    for _ in range(draws):
        null_folds = [_fold(rows, person, rng) for person in people]
        null.append(float(np.mean([fold["mae"] for fold in null_folds
                                   if fold["status"] == "descriptive_relative"])))
    return {**base, "status": "descriptive_relative", "folds": folds,
            "observed_mean_mae": observed,
            "zero_baseline_mean_mae": float(np.mean([fold["zero_baseline_mae"]
                                                      for fold in eligible])),
            "null_mean_mae": null, "seed": seed,
            "null_note": "training room labels shuffled within person; frozen held-out outcomes; no calibrated population p-value"}
