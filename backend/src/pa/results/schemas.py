"""Validated browser research product contracts; finite values or explicit nulls."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from pa.config import SCHEMA_VERSION


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Provenance(StrictModel):
    source: str
    method: str
    generated_at: str | None = None
    limitations: list[str] = Field(default_factory=list)
    manifest_sha256: str | None = None
    analysis_spec_sha256: str | None = None


class Position(StrictModel):
    valence: float = Field(allow_inf_nan=False)
    arousal: float = Field(allow_inf_nan=False)


class ExperimentRecord(StrictModel):
    id: int
    trials: int = Field(ge=0)
    participants: int = Field(ge=0)
    rooms: int = Field(ge=0)
    measured: list[str] = Field(default_factory=list)


class StudyRecord(StrictModel):
    title: str
    abstract: str
    experiments: list[ExperimentRecord]
    protocol: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class RoomRecord(StrictModel):
    id: str
    experiment: int
    space_type: str | None = None
    lighting: str | None = None
    illuminance_lux: float | None = Field(default=None, allow_inf_nan=False)
    cct_kelvin: float | None = Field(default=None, allow_inf_nan=False)
    dimensions: dict[str, float | None]
    mean_affect: Position | None = None
    n_affect: int | None = Field(default=None, ge=0)


class TraceRecord(StrictModel):
    # Browser display rate may be lower than the conditional source analysis rate.
    sample_rate_hz: float | None = Field(default=None, allow_inf_nan=False)
    source_sample_rate_hz: float | None = Field(default=None, allow_inf_nan=False)
    unit: str
    channel: str | None = None
    window_start_s: float = Field(default=0, ge=0, allow_inf_nan=False)
    raw: list[float] = Field(default_factory=list)
    cleaned: list[float] = Field(default_factory=list)
    rejected_segments: list[tuple[float, float]] = Field(default_factory=list)


class TrialRecord(StrictModel):
    id: str
    experiment: int
    participant_id: str
    room_id: str
    eeg_valid: bool
    ecg_valid: bool
    reasons: list[str] = Field(default_factory=list)
    eeg: TraceRecord | None = None
    ecg: TraceRecord | None = None
    eeg_band_power: dict[str, float | None] | None = None
    faa: float | None = Field(default=None, allow_inf_nan=False)
    heart_rate_bpm: float | None = Field(default=None, allow_inf_nan=False)
    rmssd_ms: float | None = Field(default=None, allow_inf_nan=False)
    subjective: Position | None = None
    objective: Position | None = None
    fused: Position | None = None
    alpha: float | None = Field(default=None, allow_inf_nan=False)
    comfort: float | None = Field(default=None, allow_inf_nan=False)
    cohort: str | None = None
    eeg_reasons: list[str] = Field(default_factory=list)
    ecg_reasons: list[str] = Field(default_factory=list)
    logged_duration_s: float | None = Field(default=None, allow_inf_nan=False)
    sample_duration_s: float | None = Field(default=None, allow_inf_nan=False)
    rate_status: str | None = None
    components: dict[str, float | None] = Field(default_factory=dict)
    available_components: list[str] = Field(default_factory=list)
    axis_availability: dict[str, bool] = Field(default_factory=dict)


class SensitivityRecord(StrictModel):
    experiment: int | None = None
    participant_id: str | None = None
    alpha: float = Field(allow_inf_nan=False)
    n: int = Field(ge=0)
    mean_valence: float | None = Field(default=None, allow_inf_nan=False)
    mean_arousal: float | None = Field(default=None, allow_inf_nan=False)
    interval_valence: tuple[float, float] | None = None
    interval_arousal: tuple[float, float] | None = None


class PersonExperimentRecord(StrictModel):
    experiment: int
    trials: int = Field(ge=0)
    valid_fused: int = Field(ge=0)
    mean_valence: float | None = Field(default=None, allow_inf_nan=False)
    mean_arousal: float | None = Field(default=None, allow_inf_nan=False)
    sleep_hours: float | None = Field(default=None, allow_inf_nan=False)
    sleep_min_hours: float | None = Field(default=None, allow_inf_nan=False)
    sleep_max_hours: float | None = Field(default=None, allow_inf_nan=False)
    sleep_observations: int = Field(ge=0)


class PersonRecord(StrictModel):
    id: str
    experiments: list[int]
    trials: int = Field(ge=0)
    valid_fused: int = Field(ge=0)
    mean_valence: float | None = Field(default=None, allow_inf_nan=False)
    mean_arousal: float | None = Field(default=None, allow_inf_nan=False)
    age: float | None = Field(default=None, allow_inf_nan=False)
    gender: str | None = None
    sleep_hours: float | None = Field(default=None, allow_inf_nan=False)
    by_experiment: list[PersonExperimentRecord] = Field(default_factory=list)


class DisagreementRecord(StrictModel):
    experiment: int
    participant_id: str | None = None
    cohort: str
    axis: str
    n: int = Field(ge=0)
    mean_objective_minus_subjective: float | None = Field(default=None, allow_inf_nan=False)


class ModelSummary(StrictModel):
    cohort_trials: int = Field(ge=0)
    cohort_participants: int = Field(ge=0)
    cohort_rooms: int = Field(ge=0)
    exclusions: dict[str, int]
    selection_status: str | None = None
    selected_candidate: dict[str, str | int | float] | None = None
    preprocessing: list[str]
    provenance: dict[str, str]
    participant_baseline_fallback: str
    evidence_links: dict[str, str]


class MetricRecord(StrictModel):
    name: str
    value: float | None = Field(default=None, allow_inf_nan=False)
    unit: str | None = None
    interval: tuple[float, float] | None = None
    n: int | None = Field(default=None, ge=0)
    group: str | None = None


class ModelRecord(StrictModel):
    status: str
    explanation: str
    metrics: list[MetricRecord]
    limitations: list[str] = Field(default_factory=list)
    artifact_version: str | None = None
    summary: ModelSummary | None = None


class ExportBase(StrictModel):
    schema_version: str = SCHEMA_VERSION
    provenance: Provenance

    @field_validator("schema_version")
    @classmethod
    def known_schema(cls, value: str) -> str:
        if value != SCHEMA_VERSION:
            raise ValueError(f"unsupported research schema version: {value}")
        return value


class StudyExport(ExportBase):
    study: StudyRecord


class RoomsExport(ExportBase):
    rooms: list[RoomRecord]


class SignalsExport(ExportBase):
    trials: list[TrialRecord]


class AffectExport(ExportBase):
    sensitivity: list[SensitivityRecord]
    cohorts: dict[str, int] = Field(default_factory=dict)
    disagreement: list[DisagreementRecord] = Field(default_factory=list)
    analysis: dict = Field(default_factory=dict)


class PeopleExport(ExportBase):
    people: list[PersonRecord]


class ModelExport(ExportBase):
    model: ModelRecord


class ResearchBundle(ExportBase):
    study: StudyRecord
    rooms: list[RoomRecord]
    trials: list[TrialRecord]
    sensitivity: list[SensitivityRecord]
    disagreement: list[DisagreementRecord] = Field(default_factory=list)
    people: list[PersonRecord]
    model: ModelRecord
