"""Raw acquisition CSV reader; no assumed sample rate or signal unit."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from pa.config import DATA
from pa.io.metadata import Trial

HEADER = ("Counter", "Channel1", "Channel2", "Channel3")


@dataclass(frozen=True)
class Recording:
    counter: NDArray[np.int64]
    right_forehead: NDArray[np.float64]
    left_forehead: NDArray[np.float64]
    wrist_ecg: NDArray[np.float64]

    @property
    def samples(self) -> int:
        return len(self.counter)


def recording_path(trial: Trial, raw_dir: Path = DATA / "raw") -> Path:
    filename = Path(trial.eeg_filename)
    if filename.name != trial.eeg_filename or filename.suffix.lower() != ".csv":
        raise ValueError("unsafe or invalid recording filename")
    return raw_dir / f"experiment_{trial.experiment:02d}" / filename


def read_recording(path: Path) -> Recording:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        header = tuple(next(csv.reader(handle)))
    if header != HEADER:
        raise ValueError(f"unexpected raw header in {path}: {header}")
    matrix = np.loadtxt(path, delimiter=",", skiprows=1, dtype=np.float64, ndmin=2)
    if matrix.shape[1] != 4 or not np.isfinite(matrix).all():
        raise ValueError(f"invalid numeric recording in {path}")
    counter = matrix[:, 0]
    if not np.equal(counter, np.floor(counter)).all() or np.any((counter < 0) | (counter > 255)):
        raise ValueError(f"invalid counter values in {path}")
    return Recording(counter.astype(np.int64), matrix[:, 1], matrix[:, 2], matrix[:, 3])
