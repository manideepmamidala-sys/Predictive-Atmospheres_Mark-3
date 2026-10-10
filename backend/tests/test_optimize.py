import numpy as np
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from pa.features.schema import RoomInput
from pa.features.support import StudiedSupport
from pa.modeling.artifact import LoadedArtifact
from pa.modeling.predict import feature_frame
from pa.optimize.search import search
from pa.scoring.neuro_score import AffectPoint


class TwoLevelModel:
    def predict(self, frame):
        # At target (1, 1), length 4 produces about 64.5 and others produce 95.
        return np.array([[0.29, 0.29] if length == 4 else [0.9, 0.9]
                         for length in frame["length"]])


def fixture():
    rooms = [RoomInput(length=4+i, width=3+i, height=3, num_doors=1, door_area=2,
                       num_windows=1, window_area=2, daylight_factor=2,
                       illuminance=300+100*i, cct=5000,
                       walkable_floor_area=8+i, day_or_night="Day", space_type="Bedroom")
             for i in range(4)]
    support = StudiedSupport([(f"R{i}", room) for i, room in enumerate(rooms)])
    model = Pipeline([("select", ColumnTransformer([
        ("numeric", SimpleImputer(), ["length", "width", "height"]),
    ])), ("model", DummyRegressor(strategy="mean"))])
    model.fit(feature_frame(rooms), np.array([[0.2, 0.3]] * len(rooms)))
    return LoadedArtifact(model, {"model_status": "synthetic_test"}), support


def test_seeded_search_is_distinct_physical_and_supported():
    artifact, support = fixture()
    target = AffectPoint(valence=0, arousal=0)
    first = search(artifact, support, target, budget=20, n_candidates=3, seed=7)
    second = search(artifact, support, target, budget=20, n_candidates=3, seed=7)
    assert first == second and first.status == "ok"
    assert len({str(item.room) for item in first.candidates}) == len(first.candidates)
    assert all(item.support.status == "supported" for item in first.candidates)


def test_unavailable_and_impossible_categories_are_explicit():
    artifact, support = fixture()
    target = AffectPoint(valence=0, arousal=0)
    assert search(None, support, target).status == "unavailable"
    assert search(artifact, support, target, space_type="Castle").status == "empty"


def test_requested_score_ranks_closest_and_keeps_locked_base_dimensions():
    _, support = fixture()
    artifact = LoadedArtifact(TwoLevelModel(), {"model_status": "synthetic_test"})
    target = AffectPoint(valence=1, arousal=1)
    result = search(artifact, support, target, requested_score=65, budget=20,
                    n_candidates=4, seed=2718)
    assert result.status == "ok"
    assert result.candidates[0].room.length == 4
    assert result.candidates[0].achieved_score == pytest.approx(64.5, abs=0.1)
    assert result.candidates[0].absolute_difference < result.candidates[1].absolute_difference
    assert result.candidates[0].support.nearest_room_id == "R0"

    base = support.rooms[0]
    locked = search(artifact, support, target, requested_score=65, base_room=base,
                    locked_fields=["length", "width", "height", "space_type"],
                    budget=30, seed=7)
    assert locked.status == "ok"
    assert all((item.room.length, item.room.width, item.room.height, item.room.space_type) ==
               (base.length, base.width, base.height, base.space_type)
               for item in locked.candidates)


def test_constraints_are_never_relaxed_and_empty_is_reasoned():
    artifact, support = fixture()
    target = AffectPoint(valence=0, arousal=0)
    base = support.rooms[0]
    impossible = search(artifact, support, target, base_room=base, locked_fields=["length"],
                        allowed_ranges={"length": {"minimum": 6, "maximum": 7}}, budget=20)
    assert impossible.status == "empty" and not impossible.candidates
    assert "locks or allowed ranges" in impossible.reason
    constrained = search(artifact, support, target,
                         allowed_ranges={"length": {"minimum": 4, "maximum": 4}},
                         budget=40)
    assert constrained.status == "ok"
    assert all(item.room.length == 4 for item in constrained.candidates)
    closed = support.rooms[0].model_copy(update={"num_doors": 0, "door_area": 0.0})
    varied = StudiedSupport([("closed", closed)] +
                            [(f"R{i}", room) for i, room in enumerate(support.rooms[1:])])
    incoherent = search(artifact, varied, target, base_room=closed,
                        locked_fields=["num_doors"],
                        allowed_ranges={"door_area": {"minimum": 2, "maximum": 2}},
                        budget=30)
    assert incoherent.status == "empty"
    assert "physically valid" in incoherent.reason
    with pytest.raises(ValueError, match="0–100"):
        search(artifact, support, target, requested_score=101)


def test_equal_scores_break_ties_by_support_then_stable_room_order():
    artifact, support = fixture()
    near = support.rooms[0].model_copy(update={"length": 4.1})
    result = search(artifact, support, AffectPoint(valence=0, arousal=0),
                    requested_score=65, base_room=near, budget=5, n_candidates=5, seed=9)
    assert [item.room.length for item in result.candidates] == [4, 5, 6, 7, 4.1]
    assert all(item.support.standardized_distance == 0 for item in result.candidates[:4])
    assert result.candidates[-1].support.standardized_distance > 0


def test_requested_score_endpoints_and_all_fields_locked():
    artifact, support = fixture()
    room = support.rooms[0]
    target = AffectPoint(valence=0, arousal=0)
    for requested in (0, 100):
        result = search(artifact, support, target, requested_score=requested,
                        base_room=room, locked_fields=list(RoomInput.model_fields), budget=20)
        assert result.status == "ok"
        assert len(result.candidates) == 1
        assert result.samples_evaluated == 1
        candidate = result.candidates[0]
        assert candidate.room == room
        assert candidate.requested_score == requested
        assert candidate.achieved_score == pytest.approx(100 * candidate.prediction.neuro_score)
        assert candidate.absolute_difference == pytest.approx(abs(candidate.achieved_score - requested))
