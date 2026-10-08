from pa.affect.analysis import analyze_affect, group_summary, room_level_association


def test_crossed_summary_counts_and_missing_values():
    rows = [
        {"experiment": 2, "participant_id": "P1", "room_id": "R1", "score": 0.1},
        {"experiment": 2, "participant_id": "P2", "room_id": "R1", "score": None},
        {"experiment": 2, "participant_id": "P1", "room_id": "R2", "score": 0.5},
    ]
    room = group_summary(rows, "room_id", ("score",))
    assert room[0]["trials"] == 2 and room[0]["participants"] == 2
    assert room[0]["n_score"] == 1 and room[0]["mean_score"] == 0.1
    assert room[0]["interval_status"] == "not_estimated_crossed_dependence"


def test_room_level_association_has_no_trial_iid_interval_or_p_value():
    rows = [{"experiment": 3, "participant_id": person, "room_id": f"R{room}",
             "light": float(room), "valence": float(room) / 2}
            for room in range(3) for person in ("P1", "P2")]
    result = room_level_association(rows, "light", "valence", experiment=3)
    assert result["n_rooms"] == 3 and result["pearson_r"] == 1
    assert result["interval"] is None and result["p_value"] is None
    unavailable = room_level_association(rows[:2], "light", "valence", experiment=3)
    assert unavailable["status"] == "unavailable_insufficient_rooms"


def test_analysis_never_pools_partial_fusion_into_complete_summary():
    rows = []
    for person, cohort in (("P1", "complete_fusion"), ("P2", "partial_modality_fusion")):
        rows.append({"id": f"E3:{person}:R1", "experiment": 3, "participant_id": person,
                     "room_id": "R1", "construction": {
                         "cohort": cohort, "subjective": {"valence": 0.2, "arousal": 0.1},
                         "fused": {"valence": 0.4, "arousal": 0.3}}})
    detail = {"method_version": "synthetic", "trials": rows, "cohorts": [],
              "objective_subjective_disagreement": []}
    spatial = [{"room_id": "R1", "experiment": 3, "illuminance": 300}]
    result = analyze_affect(detail, spatial)
    assert result["experiments"][0]["n_complete_fused_valence"] == 1
    assert result["experiments"][0]["n_partial_fused_valence"] == 1
    assert result["interval_status"].startswith("unavailable")
