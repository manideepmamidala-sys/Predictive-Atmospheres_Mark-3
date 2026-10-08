import json

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from pa.api.app import app
from pa.cli import app as cli
from pa.config import MODEL
from pa.features.schema import RoomInput
from pa.io.metadata import load_rooms
from pa.modeling.artifact import load_artifact
from pa.modeling.predict import predict_room
from pa.scoring.neuro_score import AffectPoint


def test_fitted_artifact_direct_cli_api_and_reloaded_prediction_parity():
    if not (MODEL / "model.joblib").is_file():
        pytest.skip("no fitted artifact; synthetic parity is tested separately")
    source = next(row for row in load_rooms() if row["experiment"] == 3)
    room = RoomInput.model_validate({name: source[name] for name in RoomInput.model_fields})
    target = AffectPoint(valence=0.1, arousal=-0.1)
    direct = predict_room(load_artifact(), room, target)
    restored = predict_room(load_artifact(), room, target)
    assert restored == direct
    cli_result = CliRunner().invoke(cli, ["predict", "--", room.model_dump_json(), "0.1", "-0.1"])
    assert cli_result.exit_code == 0, cli_result.output
    cli_payload = json.loads(cli_result.stdout)
    with TestClient(app) as client:
        assert client.get("/v1/health").json()["ready"]
        response = client.post("/v1/predict", json={"room": room.model_dump(mode="json"),
                                                    "target": target.model_dump()})
        assert response.status_code == 200, response.text
        api_payload = response.json()
        optimized = client.post("/v1/optimize", json={"target": target.model_dump(),
                                                      "budget": 20, "n_candidates": 2,
                                                      "seed": 2718})
        assert optimized.status_code == 200 and optimized.json()["status"] == "ok"
        assert len(optimized.json()["candidates"]) == 2
        empty = client.post("/v1/optimize", json={"target": target.model_dump(),
                                                  "space_type": "General", "budget": 20})
        assert empty.status_code == 200 and empty.json()["status"] == "empty"
    for field in ("valence", "arousal", "raw_valence", "raw_arousal", "neuro_score"):
        assert cli_payload["prediction"][field] == pytest.approx(getattr(direct, field))
        assert api_payload["prediction"][field] == pytest.approx(getattr(direct, field))
    assert api_payload["model_status"] == "not_better_than_baseline"
