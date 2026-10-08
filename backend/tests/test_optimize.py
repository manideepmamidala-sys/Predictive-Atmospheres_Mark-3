import numpy as np
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
