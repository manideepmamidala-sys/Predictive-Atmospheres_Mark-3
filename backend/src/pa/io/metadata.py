"""Faithful readers for investigator-supplied, already-transformed metadata."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

from pa.config import DATA

DURATION = "Time spent by the subject in the room (seconds)"
SPATIAL_COLUMNS = {
    "Length (meter)": "length",
    "Width (meter)": "width",
    "Height (meter)": "height",
    "Number of Door": "num_doors",
    "Door Area (sq.meter)": "door_area",
    "Number of Windows": "num_windows",
    "Window Area (sq.meter)": "window_area",
    "Daylight Factor (%)": "daylight_factor",
    "Illuminance (lux)": "illuminance",
    "Correlated Color Temperature (Kelvin)": "cct",
    "Walkable Floor Area (sq.meter)": "walkable_floor_area",
    "Day or Night": "day_or_night",
    "Type of Space": "space_type",
}


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return [
            {key.strip(): (value or "").strip() for key, value in row.items() if key is not None}
            for row in reader if any((value or "").strip() for value in row.values())
        ]


def _number(value: str) -> float | None:
    if not value:
        return None
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("metadata contains nonfinite number")
    return number


@dataclass(frozen=True)
class Trial:
    experiment: int
    subject_id: str
    room_id: str
    eeg_filename: str
    logged_duration_s: float
    comfort: float | None
    self_valence: float | None
    self_arousal: float | None
    rating_provenance: str

def load_trials(metadata_dir: Path = DATA / "metadata") -> list[Trial]:
    trials: list[Trial] = []
    for experiment in (1, 2, 3):
        path = metadata_dir / f"experiment_{experiment:02d}_biometric data.csv"
        for row in _rows(path):
            if not all(row.get(key) for key in ("Subject_ID", "Room_ID", "EEG_Filename")):
                raise ValueError(f"incomplete anchored trial in {path.name}: {row}")
            comfort = _number(row.get("Score by Subject", "")) if experiment == 1 else None
            valence = _number(row.get("Valence Score by Subject", "")) if experiment != 1 else None
            arousal = _number(row.get("Arousal Score by Subject", "")) if experiment != 1 else None
            duration = _number(row.get(DURATION, ""))
            if duration is None or duration <= 0:
                raise ValueError(f"invalid logged duration in {path.name}: {row}")
            for axis in (comfort, valence, arousal):
                if axis is not None and not -1 <= axis <= 1:
                    raise ValueError(f"rating outside transformed range in {path.name}: {row}")
            trials.append(Trial(
                experiment=experiment, subject_id=row["Subject_ID"], room_id=row["Room_ID"],
                eeg_filename=row["EEG_Filename"], logged_duration_s=duration,
                comfort=comfort, self_valence=valence, self_arousal=arousal,
                rating_provenance=("transformed_comfort_0_10" if experiment == 1 else
                                   "transformed_separate_axes_0_10" if experiment == 2 else
                                   "transformed_direction_intensity_0_10"),
            ))
    keys = [(trial.experiment, trial.subject_id, trial.room_id) for trial in trials]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate experiment/subject/room trial")
    return trials


SUMMARY_COUNTS = ("participants", "female", "male", "e3_sleep_trials")
SUMMARY_RANGES = (("age_min", "age_mean", "age_max"),
                  ("e3_sleep_hours_min", "e3_sleep_hours_mean", "e3_sleep_hours_max"))


@dataclass(frozen=True)
class ParticipantSummary:
    """Cohort-level participant description; per-person originals are withheld for privacy."""

    participants: int
    age_min: float
    age_max: float
    age_mean: float
    female: int
    male: int
    occupation: str
    e3_sleep_trials: int
    e3_sleep_hours_mean: float
    e3_sleep_hours_min: float
    e3_sleep_hours_max: float


def load_participant_summary(metadata_dir: Path = DATA / "metadata") -> ParticipantSummary:
    """Read the single aggregate cohort row; reject incomplete or inconsistent values."""
    rows = [row for row in _rows(metadata_dir / "participant_summary.csv") if row.get("scope") == "all"]
    if len(rows) != 1:
        raise ValueError("participant summary must contain exactly one 'all' scope row")
    row = rows[0]
    values: dict[str, float] = {}
    for key in (*SUMMARY_COUNTS, *(name for group in SUMMARY_RANGES for name in group)):
        number = _number(row.get(key, ""))
        if number is None or number < 0:
            raise ValueError(f"missing or negative participant summary value: {key}")
        values[key] = number
    if any(not values[key].is_integer() for key in SUMMARY_COUNTS):
        raise ValueError("participant summary counts must be whole numbers")
    if values["female"] + values["male"] > values["participants"]:
        raise ValueError("participant summary gender counts exceed participants")
    for low, mean, high in SUMMARY_RANGES:
        if not values[low] <= values[mean] <= values[high]:
            raise ValueError(f"participant summary range is inconsistent: {low}..{high}")
    if not row.get("occupation"):
        raise ValueError("missing participant summary occupation")
    return ParticipantSummary(
        occupation=row["occupation"],
        **{key: int(value) if key in SUMMARY_COUNTS else value for key, value in values.items()})


def load_rooms(metadata_dir: Path = DATA / "metadata") -> list[dict]:
    rooms: list[dict] = []
    for experiment in (1, 2, 3):
        path = metadata_dir / f"experiment_{experiment:02d}_spatial data.csv"
        for row in _rows(path):
            room_id = row.get("Room_ID")
            if not room_id:
                raise ValueError(f"spatial row without Room_ID in {path.name}")
            record: dict = {"experiment": experiment, "room_id": room_id}
            for original, normalized in SPATIAL_COLUMNS.items():
                raw = row.get(original, "")
                record[normalized] = raw if normalized in ("day_or_night", "space_type") and raw else (
                    None if normalized in ("day_or_night", "space_type") else _number(raw)
                )
            rooms.append(record)
    ids = [room["room_id"] for room in rooms]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate Room_ID in spatial metadata")
    return rooms
