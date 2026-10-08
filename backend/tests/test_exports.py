import pytest
from pydantic import ValidationError

from pa.results.schemas import Position, TraceRecord


def test_export_rejects_nonfinite_numbers_and_preserves_explicit_null():
    with pytest.raises(ValidationError):
        Position(valence=float("nan"), arousal=0)
    trace = TraceRecord(sample_rate_hz=None, unit="unverified raw amplitude", raw=[0.1])
    assert trace.model_dump()["sample_rate_hz"] is None


def test_six_products_write_one_valid_bundle(tmp_path):
    import json

    from pa.results.export import write_products
    from pa.results.schemas import (
        AffectExport,
        ModelExport,
        ModelRecord,
        PeopleExport,
        Provenance,
        RoomsExport,
        SignalsExport,
        StudyExport,
        StudyRecord,
    )

    provenance = Provenance(source="synthetic test fixture", method="contract exercise")
    products = {
        "study": StudyExport(provenance=provenance, study=StudyRecord(
            title="Synthetic", abstract="Contract fixture", experiments=[])),
        "rooms": RoomsExport(provenance=provenance, rooms=[]),
        "signals": SignalsExport(provenance=provenance, trials=[]),
        "affect": AffectExport(provenance=provenance, sensitivity=[]),
        "people": PeopleExport(provenance=provenance, people=[]),
        "model": ModelExport(provenance=provenance, model=ModelRecord(
            status="unavailable", explanation="fixture", metrics=[])),
    }
    manifest = write_products(products, tmp_path)
    bundle = json.loads((tmp_path / "bundle.json").read_text())
    assert bundle["study"]["title"] == "Synthetic"
    assert set(manifest["products"]) == {*products, "bundle"}
    assert bundle["rooms"] == [] and bundle["model"]["status"] == "unavailable"


def test_trace_windows_are_bounded_and_mark_qc_exclusion():
    import numpy as np

    from pa.results.traces import browser_trace, ecg_window, eeg_window
    from pa.signals.ecg import process_ecg
    from pa.signals.eeg import process_eeg

    fs = 500
    t = np.arange(fs * 12) / fs
    counter = np.arange(len(t)) % 256
    healthy = np.sin(2 * np.pi * 10 * t)
    eeg = process_eeg(healthy, healthy, counter, fs)
    trace = eeg_window(healthy, eeg, fs)
    assert len(trace.raw) == len(trace.cleaned) == fs * 4
    display = browser_trace(trace.model_dump(mode="json"))
    assert display["source_sample_rate_hz"] == fs
    assert display["sample_rate_hz"] == 100
    assert len(display["raw"]) == len(display["cleaned"]) == 400
    assert len(display["raw"]) / display["sample_rate_hz"] == 4
    clipped = np.clip(100 * healthy, -1, 1)
    rejected = eeg_window(clipped, process_eeg(clipped, clipped, counter, fs), fs)
    assert rejected.cleaned == [] and rejected.rejected_segments == [(0, 4)]
    flat_ecg = np.zeros(len(t))
    ecg = ecg_window(flat_ecg, process_ecg(flat_ecg, fs, counter), fs)
    assert len(ecg.raw) == fs * 4 and ecg.cleaned == []
    assert ecg.rejected_segments


def test_browser_products_keep_unavailable_science_explicit(tmp_path):
    import json

    from pa.affect.run import construct_affect_detail
    from pa.io.metadata import Trial
    from pa.results.build import build_products
    from pa.results.export import write_products
    from pa.results.schemas import ModelRecord

    trial = Trial(1, "P1", "R1", "fixture.csv", 60, 0.2, None, None, None,
                  "synthetic_test_fixture")
    signal = {"id": "E1:P1:R1", "experiment": 1, "participant_id": "P1", "room_id": "R1",
              "sample_count": 30000, "primary_rate_hz": 500,
              "rate_status": "conditional_unconfirmed",
              "eeg_trace": {"sample_rate_hz": 500, "unit": "unverified raw amplitude",
                            "raw": [0.1] * 500, "cleaned": [], "rejected_segments": []},
              "ecg_trace": None,
              "eeg": {"valid": False, "reasons": ["insufficient_valid_epochs"],
                      "forehead_log_alpha_asymmetry": None, "log_beta_alpha_ratio": None},
              "ecg": {"valid_hr": False, "valid_rmssd": False, "reasons": ["no_qrs_quality"],
                      "heart_rate_bpm": None, "rmssd_ms": None}}
    spatial = [{"room_id": "R1", "experiment": 1, "space_type": None,
                "day_or_night": None, "illuminance": None, "cct": None,
                "length": 4, "width": 3, "height": 3}]
    affect = construct_affect_detail([trial], [signal])
    products = build_products([trial], spatial, [signal], affect,
                              ModelRecord(status="unavailable", explanation="No valid model fixture",
                                          metrics=[]),
                              demographics={"P1": {"age": 26, "gender": "Female"}})
    write_products(products, tmp_path)
    bundle = json.loads((tmp_path / "bundle.json").read_text())
    signals_export = json.loads((tmp_path / "signals.json").read_text())
    assert bundle["trials"][0]["comfort"] == 0.2
    assert bundle["trials"][0]["fused"] is None
    assert signals_export["trials"][0]["id"] == bundle["trials"][0]["id"]
    assert len(signals_export["trials"][0]["eeg"]["raw"]) == 100
    assert bundle["trials"][0]["eeg"] is None
    assert bundle["people"][0]["mean_valence"] is None
    assert bundle["people"][0]["age"] == 26
    assert bundle["people"][0]["gender"] == "Female"
    assert bundle["people"][0]["by_experiment"] == [{
        "experiment": 1, "trials": 1, "valid_fused": 0,
        "mean_valence": None, "mean_arousal": None,
        "sleep_hours": None, "sleep_min_hours": None,
        "sleep_max_hours": None, "sleep_observations": 0}]
    assert all(row["n"] == 0 for row in bundle["disagreement"])
    assert bundle["model"]["status"] == "unavailable"


def test_source_demographics_and_sleep_are_preserved_by_experiment():
    from pa.io.metadata import load_demographics, load_trials

    demographics = load_demographics()
    trials = load_trials()
    assert demographics["Subj_B"] == {"age": 26.0, "gender": "Female"}
    assert {trial.subject_id for trial in trials} <= demographics.keys()
    assert sum(trial.sleep_hours is not None for trial in trials if trial.experiment == 3) == 60
    assert all(trial.sleep_hours is None for trial in trials if trial.experiment in (1, 2))


@pytest.mark.parametrize("rows", [
    "Subject_ID,age,gender,occupation\nP1,20,Female,\nP1,21,Female,\n",
    "Subject_ID,age,gender,occupation\nP1,-2,Female,\n",
])
def test_demographic_reader_rejects_ambiguous_or_invalid_rows(tmp_path, rows):
    from pa.io.metadata import load_demographics

    (tmp_path / "Subject Data.csv").write_text(rows)
    with pytest.raises(ValueError):
        load_demographics(tmp_path)


def test_generated_participant_summaries_and_disagreement_match_source_scope():
    import json

    from pa.config import RESULTS

    bundle = json.loads((RESULTS / "bundle.json").read_text())
    detail = json.loads((RESULTS / "affect_detail.json").read_text())["trials"]
    people = {person["id"]: person for person in bundle["people"]}
    for participant_id, person in people.items():
        for scope in person["by_experiment"]:
            rows = [row for row in detail if row["participant_id"] == participant_id
                    and row["experiment"] == scope["experiment"]]
            assert scope["trials"] == len(rows)
            assert scope["valid_fused"] == sum(row["construction"]["cohort"] ==
                                                "complete_fusion" for row in rows)
            assert scope["sleep_observations"] == (len(rows) if scope["experiment"] == 3 else 0)
    subj_m_e1 = next(item for item in people["Subj_M"]["by_experiment"]
                     if item["experiment"] == 1)
    assert (subj_m_e1["trials"], subj_m_e1["valid_fused"],
            subj_m_e1["mean_valence"]) == (10, 0, None)
    for summary in bundle["disagreement"]:
        rows = [row for row in detail if row["experiment"] == summary["experiment"]
                and row["construction"]["cohort"] == summary["cohort"]
                and (summary["participant_id"] is None or
                     row["participant_id"] == summary["participant_id"])]
        pairs = [row["objective_minus_subjective"][summary["axis"]] for row in rows
                 if row["objective_minus_subjective"][summary["axis"]] is not None]
        assert summary["n"] == len(pairs)
        assert summary["mean_objective_minus_subjective"] == pytest.approx(
            sum(pairs) / len(pairs)) if pairs else summary[
                "mean_objective_minus_subjective"] is None
    assert all(item["n"] == 0 for item in bundle["sensitivity"]
               if item["participant_id"] == "Subj_B" and item["experiment"] == 3)
