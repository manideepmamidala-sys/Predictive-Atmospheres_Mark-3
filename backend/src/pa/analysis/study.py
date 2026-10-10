"""Study exposure, eligibility, room profiles and participant products S1–S5."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.stats import spearmanr

from pa.analysis.catalogue import counts, product

ROOM_NUMERIC = ("length", "width", "height", "num_doors", "door_area",
                "num_windows", "window_area", "daylight_factor", "illuminance", "cct",
                "walkable_floor_area")
COMMON_NUMERIC = tuple(name for name in ROOM_NUMERIC if name != "walkable_floor_area")
ROOM_UNITS = {"length": "m", "width": "m", "height": "m", "num_doors": "count",
              "door_area": "m²", "num_windows": "count", "window_area": "m²",
              "daylight_factor": "%", "illuminance": "lux", "cct": "K",
              "walkable_floor_area": "m²"}


def study_products(source: dict, spatial: list[dict], demographics: dict[str, dict]) -> dict:
    trials = source["trials"]
    sample = counts(trials)
    outcome = {}
    exposure = [{"experiment": row["experiment"], "participant_id": row["participant_id"],
                 "room_id": row["room_id"], "id": row["id"], "exposed": 1,
                 "cohort": row["construction"]["cohort"]} for row in trials]
    outcome["S1"] = product("S1", question="Which participant viewed which room?",
        takeaway=f"The source contains {len(exposure)} anchored exposures across three separate experiments.",
        method="One cell per source participant–room trial; color denotes recorded exposure.",
        rows=exposure, x="room_id", y="participant_id", series="exposed", chart_type="heatmap",
        x_label="Room", y_label="Participant", sample=sample, source=source,
        caveats=["People and rooms repeat; trials are not independent replicates.",
                 "The experiments use different rating questions."], units={"exposed": "trial"})

    stages = [("anchored_source", lambda row: True),
              ("reviewed_timebase", lambda row: row["reviewed_eligibility"]["timebase"]),
              ("reviewed_bilateral_EEG", lambda row: row["reviewed_eligibility"]["eeg_bilateral"]),
              ("reviewed_HR", lambda row: row["reviewed_eligibility"]["ecg_hr"]),
              ("reviewed_RMSSD", lambda row: row["reviewed_eligibility"]["ecg_rmssd"]),
              ("descriptive_complete_fusion", lambda row: row["construction"]["cohort"] == "complete_fusion"),
              ("raw_E3_model_candidate", lambda row: row["experiment"] == 3 and
               all(row.get(field) is not None for field in
                   ("faa", "alpha_suppression", "engagement", "heart_rate_bpm")) and
               all(row["subjective"][axis] is not None for axis in ("valence", "arousal")))]
    eligibility = []
    for experiment in (1, 2, 3):
        subset = [row for row in trials if row["experiment"] == experiment]
        for name, condition in stages:
            eligibility.append({"experiment": experiment, "branch": name,
                                "trials": sum(bool(condition(row)) for row in subset),
                                "participants": len({row["participant_id"] for row in subset
                                                     if condition(row)}),
                                "rooms": len({row["room_id"] for row in subset
                                              if condition(row)})})
    outcome["S2"] = product("S2", question="Which analyses have eligible source observations?",
        takeaway=(f"Across 160 trials, {sum(row['reviewed_eligibility']['eeg_bilateral'] for row in trials)} "
                  f"retain bilateral EEG and {sum(row['reviewed_eligibility']['ecg_hr'] for row in trials)} "
                  "retain HR; E3 has "
                  f"{next(row['trials'] for row in eligibility if row['experiment'] == 3 and row['branch'] == 'raw_E3_model_candidate')} raw model candidates "
                  "versus "
                  f"{next(row['trials'] for row in eligibility if row['experiment'] == 3 and row['branch'] == 'descriptive_complete_fusion')} descriptive complete-fusion trials. "
                  "These are overlapping branches."),
        method="Count every source trial independently under each prespecified eligibility condition.",
        rows=eligibility, x="branch", y="trials", facet="experiment", chart_type="bar",
        x_label="Analysis branch", y_label="Eligible trials", sample=sample, source=source,
        caveats=["A trial may contribute to multiple branches.",
                 "Descriptive fusion requires within-person calibration; raw model eligibility uses fold-fitted population calibration.",
                 "Human-readable QC decisions are agent-delegated, with uncertain evidence excluded."],
        units={"trials": "trial count"})

    room_profiles = []
    for experiment in (1, 2, 3):
        scope = [row for row in spatial if row["experiment"] == experiment]
        for feature in ROOM_NUMERIC:
            available = [float(row[feature]) for row in scope if row.get(feature) is not None]
            if not available:
                continue
            lo, hi = min(available), max(available)
            for room in scope:
                if room.get(feature) is not None:
                    value = float(room[feature])
                    room_profiles.append({"experiment": experiment, "room_id": room["room_id"],
                                          "attribute": feature, "value": value,
                                          "unit": ROOM_UNITS[feature],
                                          "normalized_value": (value-lo)/(hi-lo) if hi > lo else 0.5,
                                          "space_type": room.get("space_type"),
                                          "lighting": room.get("day_or_night")})
    outcome["S3"] = product("S3", question="How do recorded room attributes vary?",
        takeaway=f"Profiles cover {len(spatial)} source rooms; each line is scaled within its experiment and attribute.",
        method="Observed room attributes min–max scaled separately by experiment and attribute for parallel profiles; raw values retained per row.",
        rows=room_profiles, x="attribute", y="normalized_value", series="room_id",
        facet="experiment", chart_type="line", x_label="Room attribute",
        y_label="Within-experiment profile",
        sample={"trials": 0, "participants": 0, "rooms": len(spatial)}, source=source,
        caveats=["The normalized profile is descriptive, not a causal feature effect.",
                 "E1/E2 lack some E3-only independent attributes."],
        units={"normalized_value": "unit interval"})

    correlations = []
    for experiment in (1, 2, 3):
        scope = [row for row in spatial if row["experiment"] == experiment]
        for left in COMMON_NUMERIC:
            for right in COMMON_NUMERIC:
                pairs = [(float(row[left]), float(row[right])) for row in scope
                         if row.get(left) is not None and row.get(right) is not None]
                if len(pairs) < 4:
                    continue
                x, y = np.asarray(pairs).T
                rho = (float(spearmanr(x, y).statistic)
                       if np.var(x) > 1e-12 and np.var(y) > 1e-12 else None)
                correlations.append({"experiment": experiment, "attribute_x": left,
                                     "attribute_y": right, "spearman_rho": rho,
                                     "rooms": len(pairs)})
    # Heatmap cells with undefined correlation are shown as absent, not zero.
    outcome["S4"] = product("S4", question="Which measured room attributes co-vary?",
        takeaway=("Each experiment has ten designed rooms; "
                  + ", ".join(f"E{experiment} has {sum(row['experiment'] == experiment and row['attribute_x'] < row['attribute_y'] and row['spearman_rho'] is not None for row in correlations)} estimable attribute pairs"
                              for experiment in (1, 2, 3)) + "."),
        method="Pairwise Spearman correlations on observed rooms within each experiment; constant columns return null.",
        rows=correlations, x="attribute_x", y="attribute_y", series="spearman_rho",
        facet="experiment", chart_type="heatmap", x_label="Room attribute",
        y_label="Room attribute",
        sample={"trials": 0, "participants": 0, "rooms": len(spatial)}, source=source,
        caveats=["Ten designed rooms per experiment constrain precision.",
                 "Co-variation among design choices does not identify an effect on people."],
        units={"spearman_rho": "Spearman ρ"})

    per_person = defaultdict(list)
    for row in trials:
        per_person[(row["experiment"], row["participant_id"])].append(row)
    people = []
    for (experiment, participant), own in sorted(per_person.items()):
        details = demographics.get(participant, {})
        people.append({"experiment": experiment, "participant_id": participant,
                       "age": details.get("age"), "gender": details.get("gender"),
                       "trial_count": len(own),
                       "room_count": len({row["room_id"] for row in own}),
                       "complete_fusion_count": sum(row["construction"]["cohort"] ==
                                                    "complete_fusion" for row in own)})
    outcome["S5"] = product("S5", question="Who contributed to each experiment?",
        takeaway=f"{len({row['participant_id'] for row in trials})} source people contributed, with repeated exposure across experiments.",
        method="One observed dot per participant and experiment, from source demographic and trial metadata.",
        rows=people, x="age", y="trial_count", series="experiment", chart_type="scatter",
        x_label="Age", y_label="Source trials", sample=sample, source=source,
        caveats=["Age/gender are descriptive; small cells do not support subgroup inference.",
                 "The same participant may appear in more than one experiment."],
        units={"age": "years", "trial_count": "trials"})
    return outcome
