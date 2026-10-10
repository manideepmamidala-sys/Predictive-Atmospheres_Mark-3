import json

import numpy as np
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from pa.features.schema import RoomInput
from pa.modeling import artifact
from pa.modeling.artifact import ArtifactUnavailable, build_metadata, load_artifact, save_artifact
from pa.modeling.predict import feature_frame, predict_room
from pa.scoring.neuro_score import AffectPoint


def test_synthetic_fitted_artifact_roundtrip_and_schema_guard(tmp_path):
    def room(length: float, width: float, height: float) -> RoomInput:
        return RoomInput(length=length, width=width, height=height, num_doors=1,
                         door_area=1.5, num_windows=1, window_area=2,
                         daylight_factor=2, illuminance=300, cct=5000,
                         walkable_floor_area=8, day_or_night="Day", space_type="Bedroom")

    rooms = [room(4, 3, 2.8), room(5, 4, 3), room(6, 5, 3.2)]
    X = feature_frame(rooms)
    # A synthetic fitted pipeline validates serialization mechanics independent of real study eligibility.
    pipeline = Pipeline([("select", ColumnTransformer([
        ("numbers", SimpleImputer(), ["length", "width", "height"]),
    ])), ("model", DummyRegressor(strategy="mean"))])
    pipeline.fit(X, np.array([[0.2, -0.1], [0.4, 0.3], [-0.2, 0.0]]))
    metadata = build_metadata(model_status="synthetic_test", training_scope={"synthetic": True},
                              metrics={}, limitations=["synthetic fixture only"])
    save_artifact(pipeline, metadata, tmp_path)
    restored = load_artifact(tmp_path)
    target = AffectPoint(valence=0, arousal=0)
    before = predict_room(restored, rooms[0], target)
    assert before.valence == pytest.approx(0.13333333333333333)
    assert before == predict_room(load_artifact(tmp_path), rooms[0], target)
    assert restored.metadata["model_sha256"]
    saved_metadata = (tmp_path / "metadata.json").read_text()
    (tmp_path / "model.joblib").write_bytes((tmp_path / "model.joblib").read_bytes() + b"corrupt")
    with pytest.raises(ArtifactUnavailable, match="model_sha256"):
        load_artifact(tmp_path)
    save_artifact(pipeline, metadata, tmp_path)
    assert (tmp_path / "metadata.json").read_text() == saved_metadata
    (tmp_path / "metadata.json").write_text(json.dumps({**metadata, "feature_order": ["bad"]}))
    with pytest.raises(ArtifactUnavailable, match="feature_order"):
        load_artifact(tmp_path)


def test_missing_artifact_is_unavailable(tmp_path):
    with pytest.raises(ArtifactUnavailable, match="missing"):
        load_artifact(tmp_path)


def test_revision_provenance_does_not_replace_content_compatibility(tmp_path, monkeypatch):
    pipeline = DummyRegressor().fit(np.array([[1], [2]]), np.array([[0, 0], [1, 1]]))
    monkeypatch.setattr(artifact, "current_code_revision", lambda: "revision-a")
    monkeypatch.setattr(artifact, "source_snapshot_status", lambda: "clean_committed_tree")
    metadata = build_metadata(model_status="synthetic_test", training_scope={}, metrics={},
                              limitations=[])
    save_artifact(pipeline, metadata, tmp_path)
    monkeypatch.setattr(artifact, "current_code_revision", lambda: "revision-b")
    monkeypatch.setattr(artifact, "source_snapshot_status", lambda: "uncommitted_changes")
    assert load_artifact(tmp_path).metadata["base_git_revision"] == "revision-a"
    assert build_metadata(model_status="synthetic_test", training_scope={}, metrics={},
                          limitations=[])["code_tree_sha256"] == metadata["code_tree_sha256"]
    path = tmp_path / "metadata.json"
    incompatible = json.loads(path.read_text())
    incompatible["code_tree_sha256"] = "incorrect-content-hash"
    path.write_text(json.dumps(incompatible))
    with pytest.raises(ArtifactUnavailable, match="code_tree_sha256"):
        load_artifact(tmp_path)


@pytest.mark.parametrize("document", ["[]", '"text"', "null", "{}",
                                      '{"model_status": 7, "limitations": []}'])
def test_malformed_metadata_is_unavailable(tmp_path, document):
    (tmp_path / "model.joblib").write_bytes(b"trusted-fixture-placeholder")
    (tmp_path / "metadata.json").write_text(document)
    with pytest.raises(ArtifactUnavailable, match="metadata"):
        load_artifact(tmp_path)


@pytest.mark.parametrize(("field", "invalid"), [
    ("artifact_version", []), ("artifact_version", None),
    ("artifact_version", ""), ("model_status", []),
    ("model_status", ""), ("limitations", "unavailable"),
    ("limitations", ["valid", 7]),
])
def test_consumed_metadata_fields_are_checked_before_artifact_is_ready(tmp_path, field, invalid):
    pipeline = DummyRegressor(strategy="mean").fit(np.array([[1], [2], [3]]),
                                                    np.array([[0, 0], [1, 1], [-1, -1]]))
    metadata = build_metadata(model_status="synthetic_test", training_scope={"synthetic": True},
                              metrics={}, limitations=[])
    save_artifact(pipeline, metadata, tmp_path)
    assert load_artifact(tmp_path).metadata["artifact_version"] == "1.0.0"
    path = tmp_path / "metadata.json"
    malformed = json.loads(path.read_text())
    malformed[field] = invalid
    path.write_text(json.dumps(malformed))
    with pytest.raises(ArtifactUnavailable, match=field):
        load_artifact(tmp_path)


@pytest.mark.parametrize("field", ["artifact_version", "model_status", "limitations"])
def test_missing_consumed_metadata_field_is_unavailable(tmp_path, field):
    pipeline = DummyRegressor().fit(np.array([[1], [2]]), np.array([[0, 0], [1, 1]]))
    save_artifact(pipeline, build_metadata(model_status="synthetic_test", training_scope={},
                                           metrics={}, limitations=[]), tmp_path)
    path = tmp_path / "metadata.json"
    malformed = json.loads(path.read_text())
    del malformed[field]
    path.write_text(json.dumps(malformed))
    with pytest.raises(ArtifactUnavailable, match=field):
        load_artifact(tmp_path)
