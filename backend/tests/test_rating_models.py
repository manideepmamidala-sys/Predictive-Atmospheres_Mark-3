import numpy as np

from pa.analysis.ratings import crossed_additive, rater_partitions
from pa.analysis.transfer import _centered_profiles, evaluate_relative_transfer


def _rows(n_people=5):
    return [{"participant_id": f"P{p}", "room_id": f"R{r}",
             "value": float(0.1 * p + np.sin(r / 2) + 0.02 * p * r)}
            for p in range(n_people) for r in range(10)]


def test_crossed_room_signal_exceeds_shuffled_control_and_partitions_are_unique():
    rows = _rows()
    result = crossed_additive(rows, draws=20)
    assert result["status"] == "descriptive"
    assert result["room_incremental_share"] > np.median(result["null_room_share"])
    partitions = rater_partitions(rows)
    assert len(partitions["partitions"]) == 10
    assert len({tuple(item["group_a"]) for item in partitions["partitions"]}) == 10
    assert len(rater_partitions(_rows(6))["partitions"]) == 10


def test_transfer_uses_only_training_people_for_profile_and_observed_center_is_relative():
    rows = _rows()
    people = {f"P{i}" for i in range(1, 5)}
    profile = _centered_profiles(rows, training_people=people)
    changed = [dict(row, value=row["value"] + 1000 * int(row["room_id"][1:]))
               if row["participant_id"] == "P0" else row for row in rows]
    assert _centered_profiles(changed, training_people=people) == profile
    result = evaluate_relative_transfer(rows, draws=20)
    assert result["status"] == "descriptive_relative"
    assert len(result["folds"]) == 5
    assert len(result["null_mean_mae"]) == 20
    assert all(abs(sum(fold["centered_observed"])) < 1e-10 for fold in result["folds"])
