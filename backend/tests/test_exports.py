import pytest
from pydantic import ValidationError

from pa.results.schemas import (
    CATALOGUE_IDS,
    CATALOGUE_ROUTES,
    CatalogueIndex,
    CatalogueProduct,
    Position,
    TraceRecord,
)


def test_catalogue_contract_rejects_missing_ids_invalid_route_and_encoding():
    base = {
        "schema_version": "1.0.0", "id": "S1", "route": "/study",
        "status": "available", "question": "Which trials?", "takeaway": "One source trial.",
        "method": "Count source trials.", "caveats": [],
        "counts": {"trials": 1, "participants": 1, "rooms": 1}, "units": {},
        "provenance": {"method_version": "1.2.0", "approved_spec_sha256": "a" * 64,
                       "source_manifest_sha256": "b" * 64,
                       "generated_at_utc": "2026-10-10T00:00:00+00:00"},
        "availability_reason": None,
        "chart": {"type": "bar", "rows": [{"room_id": "R1", "trials": 1}],
                  "x": "room_id", "y": "trials", "x_label": "Room", "y_label": "Trials"},
    }
    assert CatalogueProduct.model_validate(base).id == "S1"
    with pytest.raises(ValidationError):
        CatalogueProduct.model_validate({**base, "route": "/body"})
    with pytest.raises(ValidationError):
        CatalogueProduct.model_validate({**base, "chart": {**base["chart"], "y": "missing"}})
    with pytest.raises(ValidationError):
        CatalogueIndex.model_validate({"schema_version": "1.0.0",
                                       "method_version": "1.2.0",
                                       "approved_spec_sha256": "a" * 64,
                                       "products": [{"id": "S1", "route": "/study",
                                                     "status": "available", "path": "S1.json"}]})


def test_catalogue_index_requires_published_absolute_product_paths():
    index = {"schema_version": "1.0.0", "method_version": "1.2.0",
             "approved_spec_sha256": "a" * 64,
             "products": [{"id": identifier, "route": CATALOGUE_ROUTES[identifier],
                           "status": "available",
                           "path": f"/research/analysis/{identifier}.json"}
                          for identifier in CATALOGUE_IDS]}
    assert len(CatalogueIndex.model_validate(index).products) == 28
    index["products"][0]["path"] = "S1.json"
    with pytest.raises(ValidationError, match="route/path mismatch"):
        CatalogueIndex.model_validate(index)


def test_null_histogram_preserves_every_draw_and_observed_marker():
    from pa.analysis.prediction import _null_histogram

    rows = _null_histogram([0.4] * 999 + [0.9], 0.5, experiment=3,
                           axis="fused_valence_arousal_mean", analysis="full_refit",
                           metric="mean_mae")
    assert len(rows) == 20
    assert sum(row["draw_count"] for row in rows) == 1000
    assert {row["observed"] for row in rows} == {0.5}
    assert {row["draws"] for row in rows} == {1000}
    assert rows[-1]["bin_right"] == 0.9


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


def test_reproduction_comparison_ignores_checkout_revision_but_detects_science_drift(tmp_path):
    import hashlib
    import json
    import subprocess
    import sys

    from pa.config import ROOT

    roots = [tmp_path / name for name in ("reference", "reproduction")]
    model_bytes = b"synthetic-model-bytes"
    model_sha256 = hashlib.sha256(model_bytes).hexdigest()
    for root, revision in zip(roots, ("revision-a", "revision-b")):
        results = root / "artifacts/results"
        model = root / "artifacts/model"
        results.mkdir(parents=True)
        model.mkdir(parents=True)
        (results / "study.json").write_text(json.dumps({"estimate": 1.0}))
        catalogue = results / "analysis"
        catalogue.mkdir()
        (catalogue / "index.json").write_text(json.dumps({"products": ["S1"]}))
        (catalogue / "S1.json").write_text(json.dumps({
            "provenance": {"generated_at_utc": revision, "approved_spec_sha256": "fixed"},
            "chart": {"rows": [{"estimate": 1.0}]},
        }))
        (results / "model_null.json").write_text(json.dumps({
            "started_at_utc": revision, "elapsed_wall_seconds": 1 if revision == "revision-a" else 2,
            "requested_draws": 1000, "draws": {"0": {"mean_mae": 0.4}},
        }))
        (results / "model_learning_curve.json").write_text(json.dumps({
            "elapsed_wall_seconds": 1 if revision == "revision-a" else 2,
            "folds": [{"mean_mae": 0.5}],
        }))
        (results / "model_null_checkpoint.json").write_text(json.dumps({"status": revision}))
        (model / "model.joblib").write_bytes(model_bytes)
        (model / "metadata.json").write_text(json.dumps({
            "base_git_revision": revision,
            "source_snapshot_status": "clean_committed_tree" if revision == "revision-a"
            else "uncommitted_changes",
            "code_tree_sha256": "scientific-content-hash",
            "model_sha256": model_sha256,
        }))

    def compare():
        return subprocess.run([sys.executable, str(ROOT / "scripts/compare_reproduction.py"),
                               *(str(root) for root in roots)], capture_output=True, text=True,
                              check=False)

    assert compare().returncode == 0
    reproduced_chart = roots[1] / "artifacts/results/analysis/S1.json"
    reproduced_chart.write_text(json.dumps({
        "provenance": {"generated_at_utc": "revision-b", "approved_spec_sha256": "fixed"},
        "chart": {"rows": [{"estimate": 2.0}]},
    }))
    changed_chart = compare()
    assert changed_chart.returncode != 0
    assert "analysis/S1.json.chart.rows[0].estimate" in changed_chart.stdout
    reproduced_chart.write_text(json.dumps({
        "provenance": {"generated_at_utc": "revision-b", "approved_spec_sha256": "fixed"},
        "chart": {"rows": [{"estimate": 1.0}]},
    }))
    reproduced_results = roots[1] / "artifacts/results/study.json"
    reproduced_results.write_text(json.dumps({"estimate": 2.0}))
    changed_result = compare()
    assert changed_result.returncode != 0
    assert "study.json.estimate" in changed_result.stdout
    reproduced_results.write_text(json.dumps({"estimate": 1.0}))
    (roots[1] / "artifacts/model/model.joblib").write_bytes(b"changed-model-bytes")
    changed_model = compare()
    assert changed_model.returncode != 0
    assert "model_sha256 does not match model.joblib" in changed_model.stdout
    (roots[1] / "artifacts/model/model.joblib").write_bytes(model_bytes)
    for root in roots:
        metadata_path = root / "artifacts/model/metadata.json"
        metadata = json.loads(metadata_path.read_text())
        metadata["approved_spec_sha256"] = "a" * 64
        metadata_path.write_text(json.dumps(metadata))
    incomplete_v12 = compare()
    assert incomplete_v12.returncode != 0
    assert "spatial null lacks the 1000 prescribed draws" in incomplete_v12.stdout
    assert "learning curve lacks the 455 room subsets" in incomplete_v12.stdout
    assert "analysis catalogue lacks 28 cards" in incomplete_v12.stdout
    assert "v1.2 reference product missing: artifacts/results/model_null_input.json" in incomplete_v12.stdout


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
    for item in bundle["sensitivity"]:
        scoped = [row for row in detail if row["experiment"] == item["experiment"] and
                  (item["participant_id"] is None or
                   row["participant_id"] == item["participant_id"])]
        assert item["n"] == sum(row["alpha_sensitivity"][format(item["alpha"], "g")]["cohort"] ==
                                "complete_fusion" for row in scoped)
    e3_b = [row for row in detail if row["experiment"] == 3 and
            row["participant_id"] == "Subj_B"]
    assert len(e3_b) == 10
    assert all(row["reviewed_eligibility"]["eeg_bilateral"] and
               row["reviewed_eligibility"]["ecg_hr"] for row in e3_b)
    assert all(item["n"] == 10 for item in bundle["sensitivity"]
               if item["participant_id"] == "Subj_B" and item["experiment"] == 3)
