import json

import numpy as np
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from pa.features.schema import RoomInput
from pa.modeling.artifact import ArtifactUnavailable, build_metadata, load_artifact, save_artifact
from pa.modeling.predict import feature_frame, predict_room
from pa.scoring.neuro_score import AffectPoint


def test_synthetic_fitted_artifact_roundtrip_and_schema_guard(tmp_path):
    rooms = [RoomInput(length=4, width=3, height=2.8),
             RoomInput(length=5, width=4, height=3),
             RoomInput(length=6, width=5, height=3.2)]
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
