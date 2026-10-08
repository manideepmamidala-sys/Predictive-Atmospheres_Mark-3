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
                                          metrics=[]))
    write_products(products, tmp_path)
    bundle = json.loads((tmp_path / "bundle.json").read_text())
    signals_export = json.loads((tmp_path / "signals.json").read_text())
    assert bundle["trials"][0]["comfort"] == 0.2
    assert bundle["trials"][0]["fused"] is None
    assert signals_export["trials"][0]["id"] == bundle["trials"][0]["id"]
    assert len(signals_export["trials"][0]["eeg"]["raw"]) == 100
    assert bundle["trials"][0]["eeg"] is None
    assert bundle["people"][0]["mean_valence"] is None
    assert bundle["model"]["status"] == "unavailable"
