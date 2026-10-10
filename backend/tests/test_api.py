import importlib
import json

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sklearn.dummy import DummyRegressor

from pa.api.app import app
from pa.features.support import load_studied_support
from pa.modeling.artifact import LoadedArtifact


class ConstantFusedModel:
    def predict(self, frame):
        return np.tile(np.array([[0.2, -0.1]]), (len(frame), 1))


class InvalidFusedModel:
    def predict(self, frame):
        return np.array([[float("nan"), 0.0]])


def test_liveness_separate_from_missing_model():
    with TestClient(app) as client:
        health = client.get("/v1/health")
        assert health.status_code == 200 and health.json()["status"] == "alive"
        meta = client.get("/v1/meta")
        assert meta.status_code == 200 and meta.json()["schema_version"] == "1.0.0"
        if not health.json()["ready"]:
            unavailable = client.post("/v1/predict", json={"room": {"length": 5, "width": 4,
                    "height": 3}, "target": {"valence": 0, "arousal": 0}})
            assert unavailable.status_code == 503
            assert unavailable.json()["error"]["code"] == "model_unavailable"


def test_invalid_requests_are_structured():
    with TestClient(app) as client:
        bad = client.post("/v1/predict", json={"room": {"length": -1},
                                               "target": {"valence": 2, "arousal": 0}})
        assert bad.status_code == 422 and bad.json()["error"]["code"] == "invalid_request"
        too_many = client.post("/v1/optimize", json={"target": {"valence": 0, "arousal": 0},
                                                    "budget": 5001})
        assert too_many.status_code == 422


def test_studio_full_room_and_constraint_boundary():
    base = load_studied_support().rooms[0]
    room = base.model_dump(mode="json")
    target = {"valence": 0, "arousal": 0}
    with TestClient(app) as client:
        app.state.artifact = LoadedArtifact(ConstantFusedModel(),
                                            {"model_status": "synthetic_test", "limitations": []})
        app.state.reason = None
        partial = client.post("/v1/predict", json={"room": {"length": 5, "width": 4,
                              "height": 3}, "target": target})
        assert partial.status_code == 422
        assert partial.json()["error"]["code"] == "invalid_value"
        forward = client.post("/v1/predict", json={"room": room, "target": target})
        assert forward.status_code == 200, forward.text
        assert 0 <= forward.json()["prediction"]["neuro_score"] <= 1
        payload = {"target": target, "requested_score": 65, "base_room": room,
                   "locked_fields": ["length", "width"], "budget": 30}
        generated = client.post("/v1/optimize", json=payload)
        assert generated.status_code == 200, generated.text
        assert generated.json()["status"] == "ok"
        for candidate in generated.json()["candidates"]:
            assert candidate["room"]["length"] == room["length"]
            assert candidate["room"]["width"] == room["width"]
            assert candidate["achieved_score"] == pytest.approx(
                100 * candidate["prediction"]["neuro_score"])
            assert candidate["absolute_difference"] == pytest.approx(
                abs(candidate["achieved_score"] - 65))
        empty = client.post("/v1/optimize", json={**payload,
             "allowed_ranges": {"length": {"minimum": room["length"] + 1,
                                            "maximum": room["length"] + 2}}})
        assert empty.status_code == 200 and empty.json()["status"] == "empty"
        for invalid in ({**payload, "requested_score": 101},
                        {**payload, "locked_fields": ["volume"]},
                        {**payload, "base_room": None},
                        {**payload, "allowed_ranges": {"space_type": {
                            "minimum": 1, "maximum": 2}}}):
            response = client.post("/v1/optimize", json=invalid)
            assert response.status_code == 422, response.text
            assert response.json()["error"]["code"] == "invalid_request"


def test_invalid_loaded_model_output_is_structured_unavailable():
    room = load_studied_support().rooms[0]
    with TestClient(app) as client:
        app.state.artifact = LoadedArtifact(InvalidFusedModel(),
                                            {"model_status": "synthetic_test", "limitations": []})
        app.state.reason = None
        response = client.post("/v1/predict", json={"room": room.model_dump(mode="json"),
                                                    "target": {"valence": 0, "arousal": 0}})
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "model_unavailable"


def test_malformed_metadata_keeps_health_live_and_prediction_unavailable(tmp_path, monkeypatch):
    from pa.modeling.artifact import load_artifact

    (tmp_path / "model.joblib").write_bytes(b"trusted-fixture-placeholder")
    (tmp_path / "metadata.json").write_text("[]")
    api_module = importlib.import_module("pa.api.app")
    monkeypatch.setattr(api_module, "load_artifact", lambda: load_artifact(tmp_path))
    with TestClient(app) as client:
        health = client.get("/v1/health")
        assert health.status_code == 200
        assert health.json()["ready"] is False
        assert "metadata" in health.json()["reason"]
        response = client.post("/v1/predict", json={"room": {"length": 5, "width": 4,
                           "height": 3}, "target": {"valence": 0, "arousal": 0}})
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "model_unavailable"


@pytest.mark.parametrize(("field", "invalid"), [
    ("artifact_version", []), ("model_status", []),
    ("limitations", ["valid", 7]),
])
def test_invalid_consumed_metadata_keeps_all_public_routes_structured(
        tmp_path, monkeypatch, field, invalid):
    from pa.modeling.artifact import build_metadata, load_artifact, save_artifact

    pipeline = DummyRegressor().fit(np.array([[1], [2]]), np.array([[0, 0], [1, 1]]))
    save_artifact(pipeline, build_metadata(model_status="synthetic_test", training_scope={},
                                           metrics={}, limitations=[]), tmp_path)
    path = tmp_path / "metadata.json"
    metadata = json.loads(path.read_text())
    metadata[field] = invalid
    path.write_text(json.dumps(metadata))
    api_module = importlib.import_module("pa.api.app")
    monkeypatch.setattr(api_module, "load_artifact", lambda: load_artifact(tmp_path))
    with TestClient(app) as client:
        health = client.get("/v1/health")
        assert health.status_code == 200
        assert health.json()["ready"] is False
        assert field in health.json()["reason"]
        meta = client.get("/v1/meta")
        assert meta.status_code == 200
        assert meta.json()["ready"] is False
        assert meta.json()["artifact_version"] is None
        assert meta.json()["model_status"] == "unavailable"
        assert field in meta.json()["limitations"][0]
        for route, payload in (
                ("/v1/predict", {"room": {"length": 5, "width": 4, "height": 3},
                                 "target": {"valence": 0, "arousal": 0}}),
                ("/v1/optimize", {"target": {"valence": 0, "arousal": 0}})):
            response = client.post(route, json=payload)
            assert response.status_code == 503
            assert response.json()["error"]["code"] == "model_unavailable"
