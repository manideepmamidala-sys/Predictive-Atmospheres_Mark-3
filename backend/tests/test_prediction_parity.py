import json
from dataclasses import asdict

import numpy as np
import pytest
from fastapi.testclient import TestClient
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from typer.testing import CliRunner

from pa.api.app import app
from pa.cli import app as cli
from pa.features.schema import RoomInput
from pa.features.support import load_studied_support
from pa.modeling.artifact import LoadedArtifact
from pa.modeling.predict import feature_frame, predict_room
from pa.optimize.search import search
from pa.scoring.neuro_score import AffectPoint


def test_direct_cli_api_synthetic_prediction_parity(monkeypatch):
    common = {"num_doors": 1, "door_area": 2, "num_windows": 1, "window_area": 2,
              "daylight_factor": 2, "illuminance": 300, "cct": 5000,
              "walkable_floor_area": 8, "day_or_night": "Day", "space_type": "Bedroom"}
    training = [RoomInput(length=4, width=3, height=3, **common),
                RoomInput(length=6, width=5, height=3, **common)]
    pipeline = Pipeline([("select", ColumnTransformer([
        ("numbers", SimpleImputer(), ["length", "width", "height"]),
    ])), ("model", DummyRegressor(strategy="mean"))])
    pipeline.fit(feature_frame(training), np.array([[0.4, -0.2], [0.2, 0.2]]))
    artifact = LoadedArtifact(pipeline, {"model_status": "synthetic_test", "limitations": []})
    room = RoomInput(length=5, width=4, height=3, **common)
    target = AffectPoint(valence=0.1, arousal=-0.1)
    direct = predict_room(artifact, room, target)
    monkeypatch.setattr("pa.cli.load_artifact", lambda: artifact)
    result = CliRunner().invoke(cli, ["predict", "--", room.model_dump_json(), "0.1", "-0.1"])
    assert result.exit_code == 0, result.output
    from_cli = json.loads(result.stdout)["prediction"]
    with TestClient(app) as client:
        app.state.artifact = artifact
        app.state.reason = None
        response = client.post("/v1/predict", json={"room": room.model_dump(mode="json"),
                                                    "target": target.model_dump()})
        assert response.status_code == 200, response.text
        from_api = response.json()["prediction"]
    for name in ("valence", "arousal", "raw_valence", "raw_arousal", "neuro_score"):
        assert from_cli[name] == pytest.approx(getattr(direct, name))
        assert from_api[name] == pytest.approx(getattr(direct, name))


def test_direct_cli_api_closest_score_parity(monkeypatch):
    support = load_studied_support()
    room = support.rooms[0]
    model = Pipeline([("select", ColumnTransformer([
        ("numbers", SimpleImputer(), ["length", "width", "height"]),
    ])), ("model", DummyRegressor(strategy="mean"))])
    model.fit(feature_frame(support.rooms), np.array([[0.2, 0.3]] * len(support.rooms)))
    artifact = LoadedArtifact(model, {"model_status": "synthetic_test", "limitations": []})
    target = AffectPoint(valence=0.1, arousal=-0.1)
    kwargs = {"requested_score": 65, "base_room": room, "locked_fields": ["length"],
              "budget": 20, "n_candidates": 2, "seed": 7}
    direct = search(artifact, support, target, **kwargs)
    monkeypatch.setattr("pa.cli.load_artifact", lambda: artifact)
    monkeypatch.setattr("pa.cli.load_studied_support", lambda: support)
    cli_result = CliRunner().invoke(cli, ["optimize", "--requested-score", "65",
                                         "--base-room-json", room.model_dump_json(),
                                         "--locked-fields-json", '["length"]',
                                         "--budget", "20", "--n-candidates", "2", "--seed", "7",
                                         "--", "0.1", "-0.1"])
    assert cli_result.exit_code == 0, cli_result.output
    cli_candidates = json.loads(cli_result.stdout)["candidates"]
    with TestClient(app) as client:
        app.state.artifact = artifact
        app.state.support = support
        app.state.reason = None
        response = client.post("/v1/optimize", json={
            "target": target.model_dump(), "requested_score": 65,
            "base_room": room.model_dump(mode="json"), "locked_fields": ["length"],
            "budget": 20, "n_candidates": 2, "seed": 7})
        assert response.status_code == 200, response.text
        api_candidates = response.json()["candidates"]
    assert direct.candidates
    assert len(cli_candidates) == len(api_candidates) == len(direct.candidates)
    expected = [{"room": item.room.model_dump(mode="json"),
                 "prediction": asdict(item.prediction), "support": asdict(item.support),
                 "requested_score": item.requested_score,
                 "achieved_score": item.achieved_score,
                 "absolute_difference": item.absolute_difference}
                for item in direct.candidates]
    assert cli_candidates == api_candidates == expected
