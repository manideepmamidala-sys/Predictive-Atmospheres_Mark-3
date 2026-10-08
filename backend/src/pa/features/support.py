"""Empirical support is separate from physical input validity."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pa.features.schema import RoomInput
from pa.io.metadata import load_rooms

SUPPORT_COLUMNS = ("length", "width", "height", "num_doors", "door_area",
                   "num_windows", "window_area",
                   "daylight_factor", "illuminance", "cct", "walkable_floor_area")


@dataclass(frozen=True)
class SupportResult:
    status: str
    nearest_room_id: str | None
    standardized_distance: float | None
    threshold: float | None
    reason: str | None = None


class StudiedSupport:
    """Complete-case observed neighborhood calibrated by leave-one-room distances."""

    def __init__(self, records: list[tuple[str, RoomInput]]):
        eligible = [(room_id, room) for room_id, room in records
                    if all(getattr(room, name) is not None for name in SUPPORT_COLUMNS)]
        if len(eligible) < 3:
            raise ValueError("at least three complete studied rooms required")
        self.ids = [room_id for room_id, _ in eligible]
        self.rooms = [room for _, room in eligible]
        self.matrix = np.array([[float(getattr(room, name)) for name in SUPPORT_COLUMNS]
                                for _, room in eligible])
        self.minimum = self.matrix.min(axis=0)
        self.maximum = self.matrix.max(axis=0)
        self.scale = np.maximum(self.maximum - self.minimum, 1e-12)
        scaled = (self.matrix - self.minimum) / self.scale
        distances = np.linalg.norm(scaled[:, None, :] - scaled[None, :, :], axis=2)
        np.fill_diagonal(distances, np.inf)
        self.threshold = float(np.quantile(np.min(distances, axis=1), 0.95))

    def assess(self, candidate: RoomInput) -> SupportResult:
        if any(getattr(candidate, name) is None for name in SUPPORT_COLUMNS):
            return SupportResult("unavailable", None, None, self.threshold, "missing support attributes")
        vector = np.array([float(getattr(candidate, name)) for name in SUPPORT_COLUMNS])
        if np.any(vector < self.minimum) or np.any(vector > self.maximum):
            return SupportResult("outside_range", None, None, self.threshold,
                                 "outside observed complete-room marginal range")
        categories = {(room.day_or_night, room.space_type) for room in self.rooms}
        if (candidate.day_or_night, candidate.space_type) not in categories:
            return SupportResult("unseen_category", None, None, self.threshold,
                                 "categorical combination was not observed")
        distances = np.linalg.norm((self.matrix - vector) / self.scale, axis=1)
        index = int(np.argmin(distances))
        nearest = float(distances[index])
        return SupportResult("supported" if nearest <= self.threshold else "sparse",
                             self.ids[index], nearest, self.threshold,
                             None if nearest <= self.threshold else "outside observed neighborhood")


def load_studied_support() -> StudiedSupport:
    """Use original Experiment 3 full-attribute rooms for empirical support."""
    records = [(source["room_id"], RoomInput.model_validate({
        key: value for key, value in source.items() if key not in ("experiment", "room_id")
    })) for source in load_rooms() if source["experiment"] == 3]
    return StudiedSupport(records)
