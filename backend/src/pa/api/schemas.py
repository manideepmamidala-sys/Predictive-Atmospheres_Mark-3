"""Public v1 request and response contracts."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from pa.features.schema import DayNight, RoomInput, SpaceType
from pa.scoring.neuro_score import AffectPoint
from pa.signals.common import decisions

OPTIMIZER = decisions()["optimizer"]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    schema_version: str
    status: Literal["alive"]
    ready: bool
    model_status: str
    reason: str | None = None


class MetaResponse(BaseModel):
    schema_version: str
    data_manifest_sha256: str
    artifact_version: str | None
    model_status: str
    ready: bool
    limitations: list[str]


class PredictRequest(BaseModel):
    room: RoomInput
    target: AffectPoint


class PredictionPayload(BaseModel):
    valence: float
    arousal: float
    raw_valence: float
    raw_arousal: float
    projected: bool
    neuro_score: float


class SupportPayload(BaseModel):
    status: str
    nearest_room_id: str | None
    standardized_distance: float | None
    threshold: float | None
    reason: str | None = None


class PredictResponse(BaseModel):
    schema_version: str
    status: Literal["ok"]
    model_status: str
    prediction: PredictionPayload
    support: SupportPayload
    limitations: list[str]


class OptimizeRequest(BaseModel):
    target: AffectPoint
    space_type: SpaceType | None = None
    day_or_night: DayNight | None = None
    budget: int = Field(default=OPTIMIZER["default_budget"], ge=1, le=OPTIMIZER["max_budget"])
    n_candidates: int = Field(default=OPTIMIZER["default_candidates"], ge=1,
                              le=OPTIMIZER["max_candidates"])
    seed: int = decisions()["modeling"]["random_seed"]


class OptimizeCandidate(BaseModel):
    room: RoomInput
    prediction: PredictionPayload
    support: SupportPayload


class OptimizeResponse(BaseModel):
    schema_version: str
    status: Literal["ok", "empty"]
    model_status: str
    candidates: list[OptimizeCandidate]
    samples_evaluated: int
    reason: str | None
    limitations: list[str]
