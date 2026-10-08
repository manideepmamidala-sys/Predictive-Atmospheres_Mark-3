"""Map saved source-derived evidence into strictly validated browser products."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from pa.affect.analysis import analyze_affect
from pa.config import RESULTS, ROOT
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import Trial, load_rooms, load_trials
from pa.results.export import write_products
from pa.results.schemas import (
    AffectExport,
    ExperimentRecord,
    ModelExport,
    ModelRecord,
    PeopleExport,
    PersonRecord,
    Position,
    Provenance,
    RoomRecord,
    RoomsExport,
    SensitivityRecord,
    SignalsExport,
    StudyExport,
    StudyRecord,
    TrialRecord,
)
from pa.results.traces import browser_trace
from pa.signals.common import decisions


def _position(axes: dict | None) -> Position | None:
    if axes is None or axes.get("valence") is None or axes.get("arousal") is None:
        return None
    return Position(valence=axes["valence"], arousal=axes["arousal"])


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def build_products(trials: list[Trial], spatial: list[dict], signal_rows: list[dict],
                   affect_detail: dict, model_record: ModelRecord) -> dict:
    """Require one anchored record per source trial; no synthetic null replacements."""
    signal_by_id = {row["id"]: row for row in signal_rows}
    affect_by_id = {row["id"]: row for row in affect_detail["trials"]}
    expected_ids = {f"E{trial.experiment}:{trial.subject_id}:{trial.room_id}" for trial in trials}
    if (set(signal_by_id) != expected_ids or set(affect_by_id) != expected_ids or
            len(signal_by_id) != len(signal_rows) or
            len(affect_by_id) != len(affect_detail["trials"])):
        raise ValueError("export trial/source identity mismatch")
    manifest_hash = hashlib.sha256((ROOT / "data/MANIFEST.sha256").read_bytes()).hexdigest()
    spec_hash = hashlib.sha256((ROOT / "docs/specs/analysis-v1.md").read_bytes()).hexdigest()
    provenance = Provenance(
        source="Original investigator-supplied CSV metadata and raw channel recordings",
        method=f"Analysis specification {decisions()['version']}; conditional primary 500 Hz scenario",
        manifest_sha256=manifest_hash, analysis_spec_sha256=spec_hash,
        limitations=["Acquisition sample rate, amplitude units and reference wiring are unconfirmed.",
                     "Constructed affect axes are hypotheses, not validated emotion measurements."])
    experiments = []
    for experiment in (1, 2, 3):
        subset = [trial for trial in trials if trial.experiment == experiment]
        experiments.append(ExperimentRecord(
            id=experiment, trials=len(subset),
            participants=len({trial.subject_id for trial in subset}),
            rooms=len({trial.room_id for trial in subset}),
            measured=["source ratings: comfort" if experiment == 1 else
                      "source ratings: signed valence and arousal",
                      "approximate bilateral-forehead channels", "owner-reported wrist ECG"]))
    study = StudyRecord(
        title="Predictive Atmospheres: retrospective pilot reanalysis",
        abstract="Original room-viewing trials are reanalyzed with explicit acquisition uncertainty, signal quality, missingness and grouped predictive evaluation.",
        experiments=experiments,
        protocol=["Barcelona room-viewing pilot; post-exposure original ratings.",
                  "Three experiment cohorts are described separately; room and participant observations repeat."],
        limitations=["No recorded baseline or confirmed exposure timing is available.",
                     "Room simulation attributes are not measured headset exposure.",
                     "Small crossed participant/room sample limits generalization and inference."])
    exported_trials = []
    for trial in trials:
        identity = f"E{trial.experiment}:{trial.subject_id}:{trial.room_id}"
        signal = signal_by_id[identity]
        affect = affect_by_id[identity]
        eeg, ecg = signal["eeg"], signal["ecg"]
        construction = affect["construction"]
        exported_trials.append(TrialRecord(
            id=identity, experiment=trial.experiment, participant_id=trial.subject_id,
            room_id=trial.room_id, eeg_valid=eeg["valid"],
            ecg_valid=ecg["valid_hr"] and ecg["valid_rmssd"],
            reasons=list(dict.fromkeys([*eeg["reasons"], *ecg["reasons"]])),
            eeg=browser_trace(signal["eeg_trace"]),
            ecg=browser_trace(signal["ecg_trace"]),
            eeg_band_power=({"alpha_right": eeg["alpha_right"], "alpha_left": eeg["alpha_left"],
                             "beta_right": eeg["beta_right"], "beta_left": eeg["beta_left"]}
                            if eeg["valid"] else None),
            faa=affect["faa"], heart_rate_bpm=affect["heart_rate_bpm"],
            rmssd_ms=affect["rmssd_ms"],
            subjective=_position(construction["subjective"]),
            objective=_position(construction["objective"]),
            fused=_position(construction["fused"]), alpha=construction["alpha"],
            comfort=trial.comfort, cohort=construction["cohort"],
            eeg_reasons=list(eeg["reasons"]), ecg_reasons=list(ecg["reasons"]),
            logged_duration_s=trial.logged_duration_s,
            sample_duration_s=signal["sample_count"] / signal["primary_rate_hz"],
            rate_status=signal["rate_status"],
            components=construction["components"],
            available_components=list(construction["available_components"]),
            axis_availability={axis: construction["fused"][axis] is not None
                               for axis in ("valence", "arousal")}))
    complete_by_room: dict[str, list[Position]] = defaultdict(list)
    complete_by_person: dict[str, list[Position]] = defaultdict(list)
    for row in exported_trials:
        if row.cohort == "complete_fusion" and row.fused is not None:
            complete_by_room[row.room_id].append(row.fused)
            complete_by_person[row.participant_id].append(row.fused)
    rooms = []
    for room in spatial:
        points = complete_by_room[room["room_id"]]
        rooms.append(RoomRecord(
            id=room["room_id"], experiment=room["experiment"],
            space_type=room["space_type"], lighting=room["day_or_night"],
            illuminance_lux=room["illuminance"], cct_kelvin=room["cct"],
            dimensions={name: room[name] for name in ("length", "width", "height")},
            mean_affect=Position(valence=_mean([point.valence for point in points]),
                                 arousal=_mean([point.arousal for point in points])) if points else None,
            n_affect=len(points)))
    people = []
    for person in sorted({trial.subject_id for trial in trials}):
        own = [trial for trial in trials if trial.subject_id == person]
        points = complete_by_person[person]
        people.append(PersonRecord(
            id=person, experiments=sorted({trial.experiment for trial in own}),
            trials=len(own), valid_fused=len(points),
            mean_valence=_mean([point.valence for point in points]),
            mean_arousal=_mean([point.arousal for point in points])))
    sensitivity = []
    for experiment in (2, 3):
        for alpha in decisions()["affect"]["alpha_sensitivity"]:
            points = [_position(row["alpha_sensitivity"][str(alpha)]["fused"])
                      for row in affect_detail["trials"] if row["experiment"] == experiment and
                      row["alpha_sensitivity"][str(alpha)]["cohort"] == "complete_fusion"]
            points = [point for point in points if point is not None]
            sensitivity.append(SensitivityRecord(
                experiment=experiment, alpha=alpha, n=len(points),
                mean_valence=_mean([point.valence for point in points]),
                mean_arousal=_mean([point.arousal for point in points])))
    analysis = analyze_affect(affect_detail, spatial)
    return {
        "study": StudyExport(provenance=provenance, study=study),
        "rooms": RoomsExport(provenance=provenance, rooms=rooms),
        "signals": SignalsExport(provenance=provenance, trials=exported_trials),
        "affect": AffectExport(provenance=provenance, sensitivity=sensitivity,
                               cohorts=dict(Counter(row.cohort for row in exported_trials)),
                               analysis=analysis),
        "people": PeopleExport(provenance=provenance, people=people),
        "model": ModelExport(provenance=provenance, model=model_record),
    }


def write_research_exports(destination: Path = RESULTS) -> dict:
    require_science_checkpoint()
    signals = json.loads((RESULTS / "signals_detail.json").read_text())
    affect = json.loads((RESULTS / "affect_detail.json").read_text())
    evaluation = json.loads((RESULTS / "model_evaluation.json").read_text())
    model = ModelRecord.model_validate(evaluation["model_record"])
    products = build_products(load_trials(), load_rooms(), signals["trials"], affect, model)
    return write_products(products, destination)
