import json

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
from pa.modeling.artifact import LoadedArtifact
from pa.modeling.predict import feature_frame, predict_room
from pa.scoring.neuro_score import AffectPoint


def test_direct_cli_api_synthetic_prediction_parity(monkeypatch):
    training = [RoomInput(length=4, width=3, height=3),
                RoomInput(length=6, width=5, height=3)]
    pipeline = Pipeline([("select", ColumnTransformer([
        ("numbers", SimpleImputer(), ["length", "width", "height"]),
    ])), ("model", DummyRegressor(strategy="mean"))])
    pipeline.fit(feature_frame(training), np.array([[0.4, -0.2], [0.2, 0.2]]))
    artifact = LoadedArtifact(pipeline, {"model_status": "synthetic_test", "limitations": []})
    room = RoomInput(length=5, width=4, height=3)
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
