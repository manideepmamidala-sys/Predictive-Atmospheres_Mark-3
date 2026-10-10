import json
from dataclasses import asdict

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from pa.api.app import app
from pa.cli import app as cli
from pa.config import MODEL, RESULTS
from pa.features.schema import RoomInput
from pa.features.support import load_studied_support
from pa.io.metadata import load_rooms
from pa.modeling.artifact import ArtifactUnavailable, load_artifact
from pa.modeling.predict import predict_room
from pa.optimize.search import search
from pa.scoring.neuro_score import AffectPoint
from pa.signals.common import decisions


def test_fitted_artifact_direct_cli_api_and_reloaded_prediction_parity():
    if not (MODEL / "model.joblib").is_file():
        pytest.skip("no fitted artifact; synthetic parity is tested separately")
    queue = RESULTS / "qc_review.json"
    if decisions()["version"].startswith("1.2.") and queue.is_file() and \
            json.loads(queue.read_text()).get("owner_verdict") == "pending":
        with pytest.raises(ArtifactUnavailable, match="incompatible model metadata"):
            load_artifact()
        with TestClient(app) as client:
            assert client.get("/v1/health").json()["ready"] is False
        return
    source = next(row for row in load_rooms() if row["experiment"] == 3)
    room = RoomInput.model_validate({name: source[name] for name in RoomInput.model_fields})
    target = AffectPoint(valence=0.1, arousal=-0.1)
    artifact = load_artifact()
    evidence = json.loads((RESULTS / "model_evaluation.json").read_text())
    assert artifact.metadata["model_status"] == evidence["status"]
    selected = artifact.metadata["training_scope"]["final_selection"]["candidate"]
    assert selected == evidence["final_selection"]["candidate"]
    direct = predict_room(artifact, room, target)
    restored = predict_room(load_artifact(), room, target)
    assert restored == direct
    cli_result = CliRunner().invoke(cli, ["predict", "--", room.model_dump_json(), "0.1", "-0.1"])
    assert cli_result.exit_code == 0, cli_result.output
    cli_payload = json.loads(cli_result.stdout)
    support = load_studied_support()
    heights = [observed.height for observed in support.rooms]
    allowed_ranges = {"height": {"minimum": min(heights), "maximum": max(heights)}}
    options = {"requested_score": 65, "base_room": room,
               "locked_fields": ["space_type"], "allowed_ranges": allowed_ranges,
               "space_type": room.space_type, "day_or_night": room.day_or_night,
               "budget": 20, "n_candidates": 2, "seed": 2718}
    direct_generation = search(artifact, support, target, **options)
    assert direct_generation.status == "ok" and len(direct_generation.candidates) == 2
    cli_generation = CliRunner().invoke(cli, [
        "optimize", "--requested-score", "65", "--base-room-json", room.model_dump_json(),
        "--locked-fields-json", '["space_type"]', "--allowed-ranges-json",
        json.dumps(allowed_ranges), "--space-type", room.space_type,
        "--day-or-night", room.day_or_night, "--budget", "20", "--n-candidates", "2",
        "--seed", "2718", "--", "0.1", "-0.1"])
    assert cli_generation.exit_code == 0, cli_generation.output
    cli_candidates = json.loads(cli_generation.stdout)["candidates"]
    with TestClient(app) as client:
        assert client.get("/v1/health").json()["ready"]
        response = client.post("/v1/predict", json={"room": room.model_dump(mode="json"),
                                                    "target": target.model_dump()})
        assert response.status_code == 200, response.text
        api_payload = response.json()
        optimized = client.post("/v1/optimize", json={
            "target": target.model_dump(), **{key: value for key, value in options.items()
                                             if key != "base_room"},
            "base_room": room.model_dump(mode="json")})
        assert optimized.status_code == 200 and optimized.json()["status"] == "ok"
        api_candidates = optimized.json()["candidates"]
        empty = client.post("/v1/optimize", json={"target": target.model_dump(),
                                                  "space_type": "General", "budget": 20})
        assert empty.status_code == 200 and empty.json()["status"] == "empty"
    assert cli_payload["prediction"] == api_payload["prediction"] == asdict(direct)
    expected_candidates = [{"room": item.room.model_dump(mode="json"),
                            "prediction": asdict(item.prediction),
                            "support": asdict(item.support),
                            "requested_score": item.requested_score,
                            "achieved_score": item.achieved_score,
                            "absolute_difference": item.absolute_difference}
                           for item in direct_generation.candidates]
    assert len(cli_candidates) == len(api_candidates) == len(expected_candidates) == 2
    assert cli_candidates == api_candidates == expected_candidates
    assert api_payload["model_status"] == artifact.metadata["model_status"]
    if selected["name"].startswith("dummy_"):
        distinct = next(observed for observed in support.rooms if observed != room)
        other_prediction = predict_room(artifact, distinct, target)
        assert (other_prediction.raw_valence, other_prediction.raw_arousal,
                other_prediction.neuro_score) == (direct.raw_valence, direct.raw_arousal,
                                                  direct.neuro_score)
        assert all(item.prediction.neuro_score == direct.neuro_score
                   for item in direct_generation.candidates)
