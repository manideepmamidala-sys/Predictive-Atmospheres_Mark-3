"""Cached null draws require identical effective input and dependency provenance."""

import json

import pytest

from pa.modeling.cohort_guard import current_input_guard, verify_or_create_null_guard


def test_effective_cohort_guard_rejects_changed_content(tmp_path):
    current = current_input_guard()
    assert (current["cohort_trials"], current["room_groups"],
            current["participant_groups"]) == (23, 10, 4)
    path = tmp_path / "guard.json"
    path.write_text(json.dumps({**current, "effective_cohort_sha256": "0" * 64}))
    with pytest.raises(RuntimeError, match="effective input/dependency guard changed"):
        verify_or_create_null_guard(path)
