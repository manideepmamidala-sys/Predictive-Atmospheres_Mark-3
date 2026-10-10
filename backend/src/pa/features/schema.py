"""Physical room inputs; unavailable supplied attributes stay optional."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class DayNight(str, Enum):
    DAY = "Day"
    NIGHT = "Night"


class SpaceType(str, Enum):
    GENERAL = "General"
    BEDROOM = "Bedroom"
    LIVING_ROOM = "Living Room"
    WORKPLACE = "Workplace"
    CLASSROOM = "Classroom"
    CAFETERIA = "Cafeteria"


class RoomInput(BaseModel):
    """Independent variables only; missing optional observations are not zeros."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)

    length: float = Field(gt=0, le=100, allow_inf_nan=False)
    width: float = Field(gt=0, le=100, allow_inf_nan=False)
    height: float = Field(gt=0, le=30, allow_inf_nan=False)
    num_doors: int | None = Field(default=None, ge=0, le=100)
    door_area: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    num_windows: int | None = Field(default=None, ge=0, le=100)
    window_area: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    daylight_factor: float | None = Field(default=None, ge=0, le=100, allow_inf_nan=False)
    illuminance: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    cct: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    walkable_floor_area: float | None = Field(default=None, ge=0, allow_inf_nan=False)
    day_or_night: DayNight | None = None
    space_type: SpaceType | None = None

    @field_validator("num_doors", "num_windows", mode="before")
    @classmethod
    def parse_integer_count(cls, value: object) -> object:
        if isinstance(value, float) and value.is_integer():
            return int(value)
        return value

    @model_validator(mode="after")
    def check_physical(self) -> RoomInput:
        floor = self.length * self.width
        wall = 2 * (self.length + self.width) * self.height
        if self.walkable_floor_area is not None and self.walkable_floor_area > floor + 1e-7:
            raise ValueError("walkable floor area exceeds geometric floor area")
        for label, count, area in (("door", self.num_doors, self.door_area),
                                   ("window", self.num_windows, self.window_area)):
            if count == 0 and area is not None and area > 0:
                raise ValueError(f"{label} area is positive but count is zero")
            if count is not None and count > 0 and area == 0:
                raise ValueError(f"{label} count is positive but total area is zero")
        opening_area = sum(area or 0 for area in (self.door_area, self.window_area))
        if opening_area > wall + 1e-7:
            raise ValueError("total opening area exceeds wall area")
        return self


INDEPENDENT_FIELDS = tuple(RoomInput.model_fields)
NUMERIC_FIELDS = tuple(name for name in INDEPENDENT_FIELDS
                       if name not in ("day_or_night", "space_type"))
COUNT_FIELDS = ("num_doors", "num_windows")
REQUIRED_STUDIO_FIELDS = INDEPENDENT_FIELDS


def validate_studio_room(room: RoomInput) -> RoomInput:
    """The E3 deployable model uses every independent input, without imputation."""
    missing = [name for name in REQUIRED_STUDIO_FIELDS if getattr(room, name) is None]
    if missing:
        raise ValueError("studio room requires complete E3 inputs: " + ", ".join(missing))
    return room


class NumericRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    minimum: float = Field(allow_inf_nan=False)
    maximum: float = Field(allow_inf_nan=False)

    @model_validator(mode="after")
    def ordered(self) -> NumericRange:
        if self.minimum > self.maximum:
            raise ValueError("minimum exceeds maximum")
        return self


class StudioConstraints(BaseModel):
    """Search controls refer only to independent room inputs."""
    model_config = ConfigDict(extra="forbid")

    base_room: RoomInput | None = None
    locked_fields: list[str] = Field(default_factory=list)
    allowed_ranges: dict[str, NumericRange] = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_fields(self) -> StudioConstraints:
        unknown_locks = set(self.locked_fields) - set(INDEPENDENT_FIELDS)
        unknown_ranges = set(self.allowed_ranges) - set(NUMERIC_FIELDS)
        if unknown_locks or unknown_ranges:
            raise ValueError("unknown independent room fields: " +
                             ", ".join(sorted(unknown_locks | unknown_ranges)))
        if len(self.locked_fields) != len(set(self.locked_fields)):
            raise ValueError("locked_fields contains duplicates")
        if self.locked_fields and self.base_room is None:
            raise ValueError("base_room is required when fields are locked")
        if self.base_room is not None:
            validate_studio_room(self.base_room)
        return self
