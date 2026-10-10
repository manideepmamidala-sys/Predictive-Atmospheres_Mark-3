"""Map saved source-derived evidence into strictly validated browser products."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from pa.affect.analysis import analyze_affect
from pa.analysis.body import body_products
from pa.analysis.catalogue import counts as catalogue_counts
from pa.analysis.catalogue import product as catalogue_product
from pa.analysis.prediction import prediction_products
from pa.analysis.ratings import rating_products
from pa.analysis.rooms import room_products
from pa.analysis.study import study_products
from pa.config import RESULTS, ROOT
from pa.io.checkpoint import require_science_checkpoint
from pa.io.metadata import Trial, load_demographics, load_rooms, load_trials
from pa.results.export import write_catalogue_products, write_products
from pa.results.schemas import (
    AffectExport,
    DisagreementRecord,
    ExperimentRecord,
    ModelExport,
    ModelRecord,
    ModelSummary,
    PeopleExport,
    PersonExperimentRecord,
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
                   affect_detail: dict, model_record: ModelRecord,
                   demographics: dict[str, dict] | None = None) -> dict:
    """Require one anchored record per source trial; no synthetic null replacements."""
    signal_by_id = {row["id"]: row for row in signal_rows}
    affect_by_id = {row["id"]: row for row in affect_detail["trials"]}
    expected_ids = {f"E{trial.experiment}:{trial.subject_id}:{trial.room_id}" for trial in trials}
    if (set(signal_by_id) != expected_ids or set(affect_by_id) != expected_ids or
            len(signal_by_id) != len(signal_rows) or
            len(affect_by_id) != len(affect_detail["trials"])):
        raise ValueError("export trial/source identity mismatch")
    manifest_hash = hashlib.sha256((ROOT / "data/MANIFEST.sha256").read_bytes()).hexdigest()
    spec_hash = hashlib.sha256((ROOT / decisions()["approved_spec_path"]).read_bytes()).hexdigest()
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
        reviewed = affect.get("reviewed_eligibility") or {
            "timebase": True, "eeg_right": eeg["valid"], "eeg_left": eeg["valid"],
            "eeg_bilateral": eeg["valid"], "ecg_hr": ecg["valid_hr"],
            "ecg_rmssd": ecg["valid_rmssd"]}
        exported_trials.append(TrialRecord(
            id=identity, experiment=trial.experiment, participant_id=trial.subject_id,
            room_id=trial.room_id, eeg_valid=reviewed["eeg_bilateral"],
            ecg_valid=reviewed["ecg_hr"] and reviewed["ecg_rmssd"],
            ecg_hr_valid=reviewed["ecg_hr"], ecg_rmssd_valid=reviewed["ecg_rmssd"],
            reviewed_eligibility=reviewed,
            reasons=list(dict.fromkeys([*eeg["reasons"], *ecg["reasons"]])),
            eeg=browser_trace(signal["eeg_trace"]),
            ecg=browser_trace(signal["ecg_trace"]),
            eeg_band_power=({"alpha_right": eeg["alpha_right"], "alpha_left": eeg["alpha_left"],
                             "beta_right": eeg["beta_right"], "beta_left": eeg["beta_left"]}
                            if reviewed["eeg_bilateral"] else None),
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
    complete_by_person_experiment: dict[tuple[str, int], list[Position]] = defaultdict(list)
    for row in exported_trials:
        if row.cohort == "complete_fusion" and row.fused is not None:
            complete_by_room[row.room_id].append(row.fused)
            complete_by_person[row.participant_id].append(row.fused)
            complete_by_person_experiment[(row.participant_id, row.experiment)].append(row.fused)
    rooms = []
    for room in spatial:
        points = complete_by_room[room["room_id"]]
        rooms.append(RoomRecord(
            id=room["room_id"], experiment=room["experiment"],
            space_type=room["space_type"], lighting=room["day_or_night"],
            illuminance_lux=room["illuminance"], cct_kelvin=room["cct"],
            dimensions={name: room[name] for name in ("length", "width", "height")},
            independent_attributes={name: room.get(name) for name in (
                "length", "width", "height", "num_doors", "door_area", "num_windows",
                "window_area", "daylight_factor", "illuminance", "cct",
                "walkable_floor_area", "day_or_night", "space_type")},
            mean_affect=Position(valence=_mean([point.valence for point in points]),
                                 arousal=_mean([point.arousal for point in points])) if points else None,
            n_affect=len(points)))
    people = []
    for person in sorted({trial.subject_id for trial in trials}):
        own = [trial for trial in trials if trial.subject_id == person]
        points = complete_by_person[person]
        by_experiment = []
        for experiment in sorted({trial.experiment for trial in own}):
            subset = [trial for trial in own if trial.experiment == experiment]
            subset_points = complete_by_person_experiment[(person, experiment)]
            sleep = [trial.sleep_hours for trial in subset if trial.sleep_hours is not None]
            by_experiment.append(PersonExperimentRecord(
                experiment=experiment, trials=len(subset), valid_fused=len(subset_points),
                mean_valence=_mean([point.valence for point in subset_points]),
                mean_arousal=_mean([point.arousal for point in subset_points]),
                sleep_hours=_mean(sleep), sleep_min_hours=min(sleep) if sleep else None,
                sleep_max_hours=max(sleep) if sleep else None,
                sleep_observations=len(sleep)))
        source = (demographics or {}).get(person, {})
        people.append(PersonRecord(
            id=person, experiments=sorted({trial.experiment for trial in own}),
            trials=len(own), valid_fused=len(points),
            mean_valence=_mean([point.valence for point in points]),
            mean_arousal=_mean([point.arousal for point in points]),
            age=source.get("age"), gender=source.get("gender"),
            by_experiment=by_experiment))
    sensitivity = []
    for experiment in (2, 3):
        experiment_rows = [row for row in affect_detail["trials"] if row["experiment"] == experiment]
        for person in [None, *sorted({row["participant_id"] for row in experiment_rows})]:
            scoped = [row for row in experiment_rows if person is None or row["participant_id"] == person]
            for alpha in decisions()["affect"]["alpha_sensitivity"]:
                points = [_position(row["alpha_sensitivity"][str(alpha)]["fused"])
                          for row in scoped if row["alpha_sensitivity"][str(alpha)]["cohort"] == "complete_fusion"]
                points = [point for point in points if point is not None]
                sensitivity.append(SensitivityRecord(
                    experiment=experiment, participant_id=person, alpha=alpha, n=len(points),
                    mean_valence=_mean([point.valence for point in points]),
                    mean_arousal=_mean([point.arousal for point in points])))
    disagreement = []
    for experiment in (1, 2, 3):
        experiment_rows = [row for row in affect_detail["trials"] if row["experiment"] == experiment]
        for person in [None, *sorted({row["participant_id"] for row in experiment_rows})]:
            scoped = [row for row in experiment_rows if person is None or row["participant_id"] == person]
            for cohort in ("complete_fusion", "partial_modality_fusion", "partial_axis_overlap"):
                for axis in ("valence", "arousal"):
                    paired = [row["objective_minus_subjective"][axis] for row in scoped
                              if row["construction"]["cohort"] == cohort and
                              row["objective_minus_subjective"][axis] is not None]
                    disagreement.append(DisagreementRecord(
                        experiment=experiment, participant_id=person, cohort=cohort,
                        axis=axis, n=len(paired),
                        mean_objective_minus_subjective=_mean(paired)))
    analysis = analyze_affect(affect_detail, spatial)
    return {
        "study": StudyExport(provenance=provenance, study=study),
        "rooms": RoomsExport(provenance=provenance, rooms=rooms),
        "signals": SignalsExport(provenance=provenance, trials=exported_trials),
        "affect": AffectExport(provenance=provenance, sensitivity=sensitivity,
                               disagreement=disagreement,
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
    metadata_path = ROOT / "artifacts/model/metadata.json"
    metadata = json.loads(metadata_path.read_text()) if metadata_path.is_file() else {}
    selection = evaluation.get("final_selection") or {}
    model.summary = ModelSummary(
        cohort_trials=evaluation["cohort"]["rows"],
        cohort_participants=evaluation["cohort"]["participants"],
        cohort_rooms=evaluation["cohort"]["rooms"],
        exclusions=evaluation["cohort"]["exclusions"],
        selection_status=selection.get("status"),
        selected_candidate=selection.get("candidate"),
        preprocessing=[
            "Numeric inputs: training-fold median imputation, missingness indicators and standard scaling.",
            "Categorical inputs: training-fold most-frequent imputation and one-hot encoding; unseen categories ignored.",
            "Constructed affect targets: training-fold population median/MAD component calibration, then tanh mapping.",
        ],
        provenance={key: metadata[key] for key in (
            "dataset_manifest_sha256", "analysis_spec_sha256", "code_tree_sha256",
            "decisions_sha256", "model_sha256", "uv_lock_sha256") if key in metadata},
        participant_baseline_fallback=(
            "Held-out-participant outer folds use a fixed training-median baseline when fewer than four "
            "participant groups remain for inner selection; this is recorded as unavailable selection, "
            "while eligible held-out errors are still evaluated."),
        evidence_links={"evaluation": "artifacts/results/model_evaluation.json",
                        "metadata": "artifacts/model/metadata.json",
                        "model_card": "docs/model_card.md"},
    )
    trial_rows = load_trials()
    demographics = load_demographics()
    unknown = {trial.subject_id for trial in trial_rows} - demographics.keys()
    if unknown:
        raise ValueError(f"missing demographic metadata for supplied trial IDs: {sorted(unknown)}")
    products = build_products(trial_rows, load_rooms(), signals["trials"], affect, model,
                              demographics=demographics)
    manifest = write_products(products, destination)
    catalogue = build_catalogue_products(affect, signals, load_rooms(), trial_rows,
                                         demographics, evaluation)
    manifest["analysis_catalogue"] = write_catalogue_products(
        catalogue, destination / "analysis")
    return manifest


def build_catalogue_products(affect: dict, signals: dict, spatial: list[dict],
                             trials: list[Trial], demographics: dict[str, dict],
                             evaluation: dict) -> dict:
    """Compute all twenty-eight figure products from reviewed, versioned analyses."""
    def saved(name: str) -> dict:
        path = RESULTS / name
        if not path.is_file():
            raise FileNotFoundError(f"required research analysis missing: {path}")
        result = json.loads(path.read_text())
        approved = (result.get("approved_spec_sha256") or
                    result.get("source_fingerprint", {}).get(
                        "docs/specs/analysis-v1.2-draft.md"))
        if approved != affect["approved_spec_sha256"]:
            raise ValueError(f"research analysis spec mismatch: {name}")
        return result

    ratings = saved("rating_research.json")
    validity = saved("validity.json")
    comparator = saved("self_report_comparator.json")
    null = saved("model_null.json")
    learning = saved("model_learning_curve.json")
    review = saved("qc_review.json")
    products = {}
    for family in (study_products(affect, spatial, demographics),
                   rating_products(affect, ratings),
                   room_products(affect, spatial, trials, demographics),
                   body_products(affect, signals, review, validity, trials),
                   prediction_products(affect, ratings, evaluation, comparator, null, learning)):
        overlap = set(products) & set(family)
        if overlap:
            raise ValueError(f"duplicate catalogue product IDs: {sorted(overlap)}")
        products.update(family)
    methods = []
    for experiment in (1, 2, 3):
        own = [row for row in affect["trials"] if row["experiment"] == experiment]
        methods.append({"experiment": experiment, "source_trials": len(own),
                        "participants": len({row["participant_id"] for row in own}),
                        "rooms": len({row["room_id"] for row in own}),
                        "rating_question": "comfort (separate)" if experiment == 1 else
                        "signed valence/arousal (different elicitation by experiment)",
                        "complete_descriptive_fusion": sum(row["construction"]["cohort"] ==
                                                           "complete_fusion" for row in own),
                        "reviewed_timebase": sum(row["reviewed_eligibility"]["timebase"]
                                                 for row in own),
                        "reviewed_HR": sum(row["reviewed_eligibility"]["ecg_hr"]
                                           for row in own)})
    products["Methods"] = catalogue_product(
        "Methods", question="What source and analysis rules support these figures?",
        takeaway="Three source experiments are described separately; reviewed physiology, descriptive mapping and fold-fitted E3 prediction have different eligibility.",
        method="Source-trial accounting plus approved v1.2 methods: conditional 500 Hz signal processing, delegated CP-B quality review, robust within-person descriptive calibration, E3 fold-contained population calibration, grouped evaluation and descriptive controls.",
        rows=methods, x="experiment", y="source_trials", chart_type="table",
        x_label="Experiment", y_label="Anchored source trials",
        sample=catalogue_counts(affect["trials"]), source=affect,
        caveats=["Acquisition rate/reference and absolute units remain unconfirmed.",
                 "Neither constructed coordinates nor pilot associations validate a clinical emotion measure.",
                 "E2/E3 rating protocols differ; no pooled deployed model or population p-value is claimed.",
                 "All 160 source trials remain accounted for even when a component is invalid or unavailable."],
        units={"source_trials": "trials"})
    return products
