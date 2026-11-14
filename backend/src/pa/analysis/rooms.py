"""Lighting, function, E1 comfort and aggregate participant products R6–R9."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy.stats import spearmanr

from pa.analysis.catalogue import counts, product
from pa.io.metadata import ParticipantSummary


def room_products(source: dict, spatial: list[dict], cohort: ParticipantSummary) -> dict:
    by_room = {row["room_id"]: row for row in spatial}
    trials = source["trials"]
    output = {}

    lighting = []
    for row in trials:
        if row["experiment"] not in (2, 3):
            continue
        room = by_room[row["room_id"]]
        for axis in ("valence", "arousal"):
            value = row["subjective"][axis]
            if value is not None and room["illuminance"] is not None:
                lighting.append({"kind": "observed_rating", "experiment": row["experiment"],
                                 "participant_id": row["participant_id"],
                                 "room_id": row["room_id"], "axis": axis,
                                 "illuminance": room["illuminance"], "cct": room["cct"],
                                 "day_or_night": room["day_or_night"], "rating": value,
                                 "paired_day_minus_night": None})
    for experiment in (2,):  # E3 has no Night rooms.
        people = sorted({row["participant_id"] for row in trials
                         if row["experiment"] == experiment})
        for person in people:
            own = [row for row in trials if row["experiment"] == experiment and
                   row["participant_id"] == person]
            for axis in ("valence", "arousal"):
                day = [row["subjective"][axis] for row in own
                       if by_room[row["room_id"]]["day_or_night"] == "Day" and
                       row["subjective"][axis] is not None]
                night = [row["subjective"][axis] for row in own
                         if by_room[row["room_id"]]["day_or_night"] == "Night" and
                         row["subjective"][axis] is not None]
                if day and night:
                    lighting.append({"kind": "within_person_day_minus_night", "experiment": 2,
                                     "participant_id": person, "room_id": None, "axis": axis,
                                     "illuminance": None, "cct": None,
                                     "day_or_night": "paired_summary", "rating": None,
                                     "paired_day_minus_night": float(np.mean(day)-np.mean(night))})
    output["R6"] = product("R6", question="How do recorded lighting conditions relate to signed ratings?",
        takeaway=("E2 within-person Day minus Night mean reports: " + "; ".join(
            f"{axis} {np.mean([row['paired_day_minus_night'] for row in lighting if row['kind'] == 'within_person_day_minus_night' and row['axis'] == axis]):+.2f}"
            for axis in ("valence", "arousal")) +
            ". E3 has no Night rooms, so that contrast is unavailable there."),
        method="Observed room illuminance/CCT against source ratings; E2 within-person mean Day minus mean Night using each person's rated rooms.",
        rows=lighting, x="illuminance", y="rating", series="axis", facet="experiment",
        chart_type="scatter", x_label="Room illuminance", y_label="Signed report",
        sample=counts([row for row in trials if row["experiment"] in (2, 3)]), source=source,
        caveats=["E2 lighting, geometry and other room choices co-vary; differences are not causal effects.",
                 "Rows marked within_person_day_minus_night preserve paired E2 contrasts; E3 has no Night support.",
                 "Repeated participants and ten rooms prevent trial-level independent uncertainty."],
        units={"illuminance": "lux", "cct": "K", "rating": "signed −1 to 1",
               "paired_day_minus_night": "signed source scale"})

    function = []
    for space_type in sorted({row["space_type"] for row in spatial
                              if row["experiment"] == 3 and row["space_type"] is not None}):
        room_ids = {row["room_id"] for row in spatial if row["experiment"] == 3 and
                    row["space_type"] == space_type}
        own = [row for row in trials if row["experiment"] == 3 and row["room_id"] in room_ids]
        for axis in ("valence", "arousal"):
            values = [row["subjective"][axis] for row in own if
                      row["subjective"][axis] is not None]
            function.append({"kind": "function_mean", "space_type": space_type, "axis": axis,
                             "mean_rating": float(np.mean(values)) if values else None,
                             "trials": len(values),
                             "participants": len({row["participant_id"] for row in own if
                                                  row["subjective"][axis] is not None}),
                             "rooms": len(room_ids), "experiment": 3,
                             "participant_id": None, "room_id": None})
    function_dots = []
    for row in trials:
        if row["experiment"] != 3:
            continue
        for axis in ("valence", "arousal"):
            if row["subjective"][axis] is not None:
                function_dots.append({"kind": "observed_trial", "space_type": by_room[row["room_id"]]["space_type"],
                                      "axis": axis, "mean_rating": row["subjective"][axis],
                                      "trials": 1, "participants": 1, "rooms": 1,
                                      "experiment": 3, "participant_id": row["participant_id"],
                                      "room_id": row["room_id"]})
    output["R7"] = product("R7", question="How do reports differ among the recorded E3 room functions?",
        takeaway=(f"{len({row['space_type'] for row in function})} E3 function labels each cover two designed rooms; observed mean valence "
                  f"ranges from {min(row['mean_rating'] for row in function if row['axis'] == 'valence'):.2f} "
                  f"to {max(row['mean_rating'] for row in function if row['axis'] == 'valence'):.2f}."),
        method="Show each source E3 rating as an observed dot and the type mean as a separately labeled dot; retain room and person counts on each mean row.",
        rows=function + function_dots, x="space_type", y="mean_rating", series="kind",
        facet="axis", chart_type="scatter", x_label="Recorded function",
        y_label="Observed report / function mean",
        sample=counts([row for row in trials if row["experiment"] == 3]),
        source=source, caveats=["Dots from the same participant or room are dependent; function_mean rows have the independent room/person denominators.",
                                "Two room designs per function cannot isolate function from other attributes.",
                                "E1/E2 lack function labels and are not pooled."],
        units={"mean_rating": "signed source scale −1 to 1"})

    comfort = []
    for row in trials:
        if row["experiment"] != 1 or row["comfort"] is None:
            continue
        room = by_room[row["room_id"]]
        floor = float(room["length"] * room["width"])
        comfort.append({"participant_id": row["participant_id"], "room_id": row["room_id"],
                        "comfort": row["comfort"], "floor_area": floor,
                        "volume": floor * float(room["height"]),
                        "length": room["length"], "width": room["width"],
                        "height": room["height"]})
    values = np.asarray([[row["floor_area"], row["comfort"]] for row in comfort])
    rho = (float(spearmanr(values[:, 0], values[:, 1]).statistic)
           if len(values) >= 4 and np.var(values[:, 0]) > 1e-12 and
           np.var(values[:, 1]) > 1e-12 else None)
    output["R8"] = product("R8", question="How does E1's separate comfort response relate to room form?",
        takeaway=f"E1 comfort versus geometric floor area has descriptive trial-level Spearman ρ {rho:.2f}."
                 if rho is not None else "E1 comfort–form correlation is unavailable.",
        method="Each E1 source comfort rating against recorded length × width; report Spearman as descriptive only.",
        rows=comfort, x="floor_area", y="comfort", series="participant_id",
        chart_type="scatter", x_label="Geometric floor area", y_label="E1 comfort",
        sample=counts([row for row in trials if row["experiment"] == 1]), source=source,
        caveats=["E1 comfort is not valence or arousal and never enters the fused target.",
                 "Repeated people and rooms make trial-level correlation exploratory."],
        units={"floor_area": "m²", "volume": "m³",
               "height": "m", "comfort": "transformed source scale −1 to 1"})

    by_experiment = defaultdict(list)
    for row in trials:
        if row["experiment"] in (2, 3):
            by_experiment[row["experiment"]].append(row)
    aggregate = []
    for experiment, own in sorted(by_experiment.items()):
        sleep_known = experiment == 3
        for axis in ("valence", "arousal"):
            observed = [row["subjective"][axis] for row in own if
                        row["subjective"][axis] is not None]
            aggregate.append({
                "experiment": experiment, "axis": axis,
                "participants": len({row["participant_id"] for row in own}),
                "rating_trials": len(observed),
                "mean_rating": float(np.mean(observed)) if observed else None,
                "sleep_trials": cohort.e3_sleep_trials if sleep_known else None,
                "sleep_hours_mean": cohort.e3_sleep_hours_mean if sleep_known else None,
                "sleep_hours_min": cohort.e3_sleep_hours_min if sleep_known else None,
                "sleep_hours_max": cohort.e3_sleep_hours_max if sleep_known else None})
    output["R9"] = product("R9", question="Who took part, and how were reports distributed per experiment?",
        takeaway=(f"{cohort.participants} participants ({cohort.occupation}), aged "
                  f"{cohort.age_min:g}–{cohort.age_max:g}; E3 sleep was reported on "
                  f"{cohort.e3_sleep_trials} trials (mean {cohort.e3_sleep_hours_mean:g} h). "
                  "Characteristics are published in aggregate only."),
        method=("Experiment-level participant counts and mean signed reports per axis, with the "
                "cohort-level E3 sleep summary; no per-person characteristic or sleep value is published."),
        rows=aggregate, x="experiment", y="mean_rating", series="axis",
        chart_type="bar", x_label="Experiment", y_label="Mean signed report",
        sample=counts([row for row in trials if row["experiment"] in (2, 3)]), source=source,
        caveats=["E2 sleep was not recorded; its sleep fields are null, not zero.",
                 "Per-person age, gender and sleep are withheld for participant privacy.",
                 "Small overlapping cohorts cannot support demographic or sleep effect claims."],
        units={"sleep_hours_mean": "hours", "sleep_hours_min": "hours", "sleep_hours_max": "hours",
               "mean_rating": "signed source scale −1 to 1"})
    return output
