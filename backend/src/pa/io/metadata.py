"""Faithful readers for investigator-supplied, already-transformed metadata."""

from __future__ import annotations

import csv
import math
from dataclasses import asdict, dataclass
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
    sleep_hours: float | None
    rating_provenance: str

    def as_record(self) -> dict:
        return asdict(self)


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
                sleep_hours=_number(row.get("Sleep Hours", "")) if experiment == 3 else None,
                rating_provenance=("transformed_comfort_0_10" if experiment == 1 else
                                   "transformed_separate_axes_0_10" if experiment == 2 else
                                   "transformed_direction_intensity_0_10"),
            ))
    keys = [(trial.experiment, trial.subject_id, trial.room_id) for trial in trials]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate experiment/subject/room trial")
    return trials


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
