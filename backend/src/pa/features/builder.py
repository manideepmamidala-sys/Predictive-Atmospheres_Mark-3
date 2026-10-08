"""The only conversion of independent room attributes to ordered model features."""

from __future__ import annotations

from pa.features.schema import RoomInput

FEATURE_ORDER = (
    "length", "width", "height", "num_doors", "door_area", "num_windows",
    "window_area", "daylight_factor", "illuminance", "cct", "walkable_floor_area",
    "day_or_night", "space_type", "length_width_ratio", "floor_area",
    "wall_area", "volume", "door_wall_ratio", "window_wall_ratio", "walkable_floor_ratio",
)


def build_features(room: RoomInput) -> dict[str, float | int | str | None]:
    """Use supplied *total* opening areas once; do not impute missing fields."""
    floor = room.length * room.width
    wall = 2 * (room.length + room.width) * room.height
    values = room.model_dump(mode="json")
    values.update({
        "length_width_ratio": room.length / room.width,
        "floor_area": floor,
        "wall_area": wall,
        "volume": floor * room.height,
        "door_wall_ratio": room.door_area / wall if room.door_area is not None else None,
        "window_wall_ratio": room.window_area / wall if room.window_area is not None else None,
        "walkable_floor_ratio": (room.walkable_floor_area / floor
                                 if room.walkable_floor_area is not None else None),
    })
    return {name: values[name] for name in FEATURE_ORDER}
