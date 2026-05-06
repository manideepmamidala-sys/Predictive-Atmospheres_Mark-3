"""Pydantic models for data validation."""

from __future__ import annotations

from typing import Any, Optional, List

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoomDimensions(BaseModel):
    """Validated room dimensions in meters."""
    length: float = Field(..., ge=2.0, le=50.0)
    width: float = Field(..., ge=2.0, le=50.0)
    height: float = Field(..., ge=2.5, le=10.0)


class SpatialInput(BaseModel):
    """Validated spatial input vector — independent features only.

    Derived features (L:W Ratio, Floor Area, Wall Area, Volume,
    Door/Wall Ratio, Window/Wall Ratio, Walkable/Floor Ratio)
    are computed by the backend and are NOT part of this schema.

    UDI, sDA, and ASE are permanently purged.
    """
    # Core geometry
    length: float = Field(..., ge=2.0, le=50.0, description="Room length in meters")
    width: float = Field(..., ge=2.0, le=50.0, description="Room width in meters")
    height: float = Field(..., ge=2.0, le=10.0, description="Room height in meters")

    # Openings
    num_doors: float = Field(1.0, ge=0.0, le=10.0, description="Number of doors")
    door_area: float = Field(1.8, ge=0.0, le=30.0, description="Total door area in m²")
    num_windows: float = Field(2.0, ge=0.0, le=30.0, description="Number of windows")
    window_area: float = Field(5.0, ge=0.0, le=250.0, description="Total window area in m²")

    # Daylight (UDI, sDA, ASE permanently purged)
    daylight_factor: float = Field(2.0, ge=0.0, le=20.0, description="Daylight factor (%)")
    illuminance: float = Field(300.0, ge=0.0, le=2000.0, description="Illuminance in lux")
    cct: float = Field(4000.0, ge=2000.0, le=10000.0, description="Correlated Color Temperature in Kelvin")

    # Floor
    walkable_floor_area: float = Field(60.0, ge=0.0, le=500.0, description="Walkable floor area in m²")

    # Categorical
    day_or_night: str = Field("Day", description="Experiment condition: 'Day' or 'Night'")
    space_type: str = Field("Living Room", description="Type of space: Bedroom, Living Room, Workplace, Classroom, Cafeteria")

    @field_validator('space_type')
    @classmethod
    def validate_space_type(cls, value: str) -> str:
        valid = {'Bedroom', 'Living Room', 'Workplace', 'Classroom', 'Cafeteria'}
        if value not in valid:
            raise ValueError(f"Invalid space type '{value}'. Must be one of: {valid}")
        return value

    @field_validator('day_or_night')
    @classmethod
    def validate_day_night(cls, value: str) -> str:
        if value not in ('Day', 'Night'):
            raise ValueError(f"day_or_night must be 'Day' or 'Night', got '{value}'")
        return value

    def to_feature_dict(self) -> dict:
        """Convert to the feature dictionary format expected by PredictionService."""
        return {
            'Length (meter)': self.length,
            'Width (meter)': self.width,
            'Height (meter)': self.height,
            'Number of Door': self.num_doors,
            'Door Area (sq.meter)': self.door_area,
            'Number of Windows': self.num_windows,
            'Window Area (sq.meter)': self.window_area,
            'Daylight Factor (%)': self.daylight_factor,
            'Illuminance (lux)': self.illuminance,
            'Correlated Color Temperature (Kelvin)': self.cct,
            'Walkable Floor Area (sq.meter)': self.walkable_floor_area,
        }


class EEGSignal(BaseModel):
    """Validated EEG signal metadata and samples."""
    model_config = ConfigDict(arbitrary_types_allowed=True)

    data: np.ndarray
    sample_rate: int = Field(256, ge=100, le=2000)
    channels: int = Field(1, ge=1, le=128)
    duration_sec: float = Field(..., gt=0.0, le=300.0)

    @field_validator('data')
    @classmethod
    def validate_data(cls, value: Any) -> np.ndarray:
        arr = np.asarray(value)
        if arr.ndim not in (1, 2):
            raise ValueError(f"Expected 1D or 2D signal array, got {arr.ndim}D")
        if not np.any(np.isfinite(arr)):
            raise ValueError("Signal contains no finite values")
        return arr
