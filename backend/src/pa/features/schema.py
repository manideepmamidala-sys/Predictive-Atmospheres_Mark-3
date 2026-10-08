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
