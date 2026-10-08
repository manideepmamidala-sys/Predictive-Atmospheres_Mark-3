from fastapi.testclient import TestClient

from pa.api.app import app


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
