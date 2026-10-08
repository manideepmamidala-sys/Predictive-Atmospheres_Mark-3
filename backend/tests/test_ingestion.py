from pa.io.metadata import load_rooms, load_trials
from pa.io.recordings import read_recording, recording_path


def test_original_ratings_and_missingness():
    trials = load_trials()
    rooms = load_rooms()
    assert len(trials) == 160 and len(rooms) == 30
    assert len({t.subject_id for t in trials}) == 10
    assert trials[0].comfort == 0.4 and trials[0].self_valence is None
    assert trials[0].sleep_hours is None
    assert next(t for t in trials if t.experiment == 2).sleep_hours is None
    assert next(t for t in trials if t.experiment == 3).self_valence == 0.85
    assert rooms[0]["cct"] is None and rooms[0]["num_doors"] is None
    assert next(r for r in rooms if r["experiment"] == 2)["walkable_floor_area"] is None


def test_raw_recording_uses_header_and_counter():
    trial = load_trials()[0]
    recording = read_recording(recording_path(trial))
    assert recording.samples > 0
    assert recording.counter.min() >= 0
