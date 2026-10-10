import pytest
from pydantic import ValidationError

from pa.features.builder import FEATURE_ORDER, build_features
from pa.features.schema import RoomInput, StudioConstraints, validate_studio_room
from pa.io.metadata import load_rooms


def test_total_opening_area_and_missingness():
    room = RoomInput(length=5, width=4, height=3, num_doors=2, door_area=4,
                     num_windows=1, window_area=2)
    features = build_features(room)
    assert tuple(features) == FEATURE_ORDER
    assert features["door_wall_ratio"] == pytest.approx(4 / 54)
    assert features["window_wall_ratio"] == pytest.approx(2 / 54)
    assert features["cct"] is None
    assert build_features(RoomInput(length=5, width=4, height=3))["volume"] == 60


def test_invalid_physics_and_derived_input_rejected():
    for bad in ({"length": 0}, {"length": float("inf")},
                {"walkable_floor_area": 100}, {"num_doors": 0, "door_area": 2},
                {"volume": 60}, {"space_type": "Castle"}):
        with pytest.raises(ValidationError):
            RoomInput.model_validate({"length": 5, "width": 4, "height": 3, **bad})


def test_supplied_rooms_validate_without_imputation():
    for source in load_rooms():
        room = RoomInput.model_validate({k: v for k, v in source.items()
                                         if k not in ("experiment", "room_id")})
        assert build_features(room)["floor_area"] > 0


def test_studied_support_separates_observed_from_physical():
    from pa.features.support import StudiedSupport

    records = [(source["room_id"], RoomInput.model_validate({k: v for k, v in source.items()
               if k not in ("experiment", "room_id")})) for source in load_rooms()
               if source["experiment"] == 3]
    support = StudiedSupport(records)
    exact = support.assess(records[0][1])
    assert exact.status == "supported" and exact.standardized_distance == 0
    physical_but_unstudied = RoomInput(length=50, width=50, height=10, num_doors=1,
                                      door_area=2, num_windows=1, window_area=2,
                                      daylight_factor=1, illuminance=300, cct=5500,
                                      walkable_floor_area=20, day_or_night="Day",
                                      space_type="Bedroom")
    outside = support.assess(physical_but_unstudied)
    assert outside.status == "outside_range" and outside.nearest_room_id is not None


def test_studied_support_checks_both_opening_counts_and_missingness():
    from pa.features.support import load_studied_support

    support = load_studied_support()
    base = support.rooms[0]
    assert support.assess(base).status == "supported"
    for count in ("num_doors", "num_windows"):
        absent = base.model_copy(update={count: None})
        assert support.assess(absent).status == "unavailable"
        outside = base.model_copy(update={count: 99})
        assert support.assess(outside).status == "outside_range"


def test_support_numeric_nearest_is_separate_from_observed_category():
    from pa.features.support import load_studied_support

    support = load_studied_support()
    numeric_room = support.rooms[support.ids.index("Rm_023")]
    classroom = numeric_room.model_copy(update={"space_type": "Classroom"})
    assessed = support.assess(classroom)
    assert assessed.status == "supported"
    assert assessed.nearest_room_id == "Rm_023"
    assert assessed.standardized_distance == 0
    unseen = numeric_room.model_copy(update={"space_type": "General"})
    assessed_unseen = support.assess(unseen)
    assert assessed_unseen.status == "unseen_category"
    assert assessed_unseen.nearest_room_id == "Rm_023"
    assert "numeric only" in assessed_unseen.reason


def test_studio_requires_all_independent_inputs_and_valid_constraints():
    from pa.features.support import load_studied_support

    room = load_studied_support().rooms[0]
    assert validate_studio_room(room) is room
    with pytest.raises(ValueError, match="complete E3 inputs"):
        validate_studio_room(room.model_copy(update={"cct": None}))
    for bad in ({"locked_fields": ["length"]},
                {"base_room": room, "locked_fields": ["volume"]},
                {"allowed_ranges": {"space_type": {"minimum": 1, "maximum": 2}}},
                {"allowed_ranges": {"length": {"minimum": 6, "maximum": 4}}}):
        with pytest.raises(ValidationError):
            StudioConstraints.model_validate(bad)
