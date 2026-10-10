"""Crossed person/room rating descriptions and fixed rater partitions."""

from __future__ import annotations

from itertools import combinations

import numpy as np
from scipy.stats import gaussian_kde, spearmanr

from pa.analysis.catalogue import counts, product

SEED = 2718
NULL_DRAWS = 1000


def _design(people: np.ndarray, rooms: np.ndarray, *, with_room: bool) -> np.ndarray:
    person_names = sorted(set(people))
    columns = [np.ones(len(people))]
    columns.extend((people == person).astype(float) for person in person_names[1:])
    if with_room:
        room_names = sorted(set(rooms))
        columns.extend((rooms == room).astype(float) for room in room_names[1:])
    return np.column_stack(columns)


def _sse(y: np.ndarray, design: np.ndarray) -> float:
    fitted = design @ np.linalg.lstsq(design, y, rcond=None)[0]
    return float(np.sum((y - fitted) ** 2))


def crossed_additive(rows: list[dict], *, draws: int = NULL_DRAWS,
                     seed: int = SEED) -> dict:
    """Room incremental share after person effects; shuffle labels within people."""
    if draws < 0:
        raise ValueError("negative null draw count")
    people = np.asarray([str(row["participant_id"]) for row in rows])
    rooms = np.asarray([str(row["room_id"]) for row in rows])
    y = np.asarray([row["value"] for row in rows], dtype=float)
    base = {"trials": len(rows), "participants": len(set(people)),
            "rooms": len(set(rooms)), "null_draws": draws,
            "interpretation": "room share conditional on observed people and rooms"}
    if len(rows) < 4 or len(set(people)) < 2 or len(set(rooms)) < 3:
        return {**base, "status": "unavailable_insufficient_groups"}
    if not np.isfinite(y).all() or np.var(y) < 1e-12:
        return {**base, "status": "unavailable_nonfinite_or_constant_rating"}
    total = float(np.sum((y - np.mean(y)) ** 2))
    person_sse = _sse(y, _design(people, rooms, with_room=False))
    full_sse = _sse(y, _design(people, rooms, with_room=True))
    observed = max(0.0, (person_sse - full_sse) / total)
    rng = np.random.default_rng(seed)
    null = []
    person_indices = [np.flatnonzero(people == person) for person in sorted(set(people))]
    for _ in range(draws):
        permuted_rooms = rooms.copy()
        for indices in person_indices:
            permuted_rooms[indices] = rng.permutation(permuted_rooms[indices])
        null_sse = _sse(y, _design(people, permuted_rooms, with_room=True))
        null.append(max(0.0, (person_sse - null_sse) / total))
    return {**base, "status": "descriptive", "room_incremental_share": observed,
            "residual_share": full_sse / total, "person_only_residual_share": person_sse / total,
            "person_share": 1 - person_sse / total,
            "null_room_share": null, "seed": seed,
            "null_note": "descriptive room-label-within-person permutation; no population p-value"}


def rater_partitions(rows: list[dict]) -> dict:
    """Enumerate ten unordered 2/3 or 3/3 person partitions once each."""
    people = sorted({str(row["participant_id"]) for row in rows})
    rooms = sorted({str(row["room_id"]) for row in rows})
    result = {"participants": len(people), "rooms": len(rooms), "partitions": []}
    if len(people) not in (5, 6) or len(rooms) < 3:
        return {**result, "status": "unavailable_unsupported_rater_count"}
    half = 2 if len(people) == 5 else 3
    for group_a in combinations(people, half):
        if len(people) == 6 and people[0] not in group_a:
            continue  # each 3/3 split has a mirror
        group_b = tuple(person for person in people if person not in group_a)
        def room_profile(group: tuple[str, ...]) -> dict[str, float]:
            return {room: float(np.mean([row["value"] for row in rows
                                         if row["room_id"] == room and
                                         row["participant_id"] in group]))
                    for room in rooms if any(row["room_id"] == room and
                                            row["participant_id"] in group for row in rows)}
        a, b = room_profile(group_a), room_profile(group_b)
        shared = sorted(set(a) & set(b))
        rho = None
        if len(shared) >= 3:
            av = np.asarray([a[room] for room in shared])
            bv = np.asarray([b[room] for room in shared])
            if np.var(av) > 1e-12 and np.var(bv) > 1e-12:
                rho = float(spearmanr(av, bv).statistic)
        result["partitions"].append({"group_a": group_a, "group_b": group_b,
                                      "shared_rooms": len(shared), "spearman_rho": rho,
                                      "status": "descriptive" if rho is not None else
                                      "unavailable_constant_or_few_rooms"})
    assert len(result["partitions"]) == 10
    result["status"] = "descriptive"
    return result


def _bootstrap_room_means(rows: list[dict], *, draws: int = 2000,
                          seed: int = SEED) -> dict[str, tuple[float | None, float | None]]:
    """Resample whole observed participant rating vectors, not trial rows."""
    people = sorted({row["participant_id"] for row in rows})
    rooms = sorted({row["room_id"] for row in rows})
    if len(people) < 4:
        return {room: (None, None) for room in rooms}
    vectors = {person: {row["room_id"]: row["value"] for row in rows
                        if row["participant_id"] == person} for person in people}
    rng = np.random.default_rng(seed)
    samples = {room: [] for room in rooms}
    for _ in range(draws):
        sampled = rng.choice(people, size=len(people), replace=True)
        for room in rooms:
            values = [vectors[person][room] for person in sampled if room in vectors[person]]
            if values:
                samples[room].append(float(np.mean(values)))
    return {room: tuple(float(value) for value in np.quantile(samples[room], [0.025, 0.975]))
            if samples[room] else (None, None) for room in rooms}


def rating_products(source: dict, rating_analysis: dict) -> dict:
    """Five separate E2/E3 self-report products with participant-aware descriptions."""
    trials = [row for row in source["trials"] if row["experiment"] in (2, 3)]
    sample = counts(trials)
    analyses = [item for item in rating_analysis["analyses"] if item["experiment"] in (2, 3)]
    output = {}
    variance = []
    for item in analyses:
        stats = item["crossed_additive"]
        variance.append({"experiment": item["experiment"], "axis": item["axis"],
                         "person_share": stats.get("person_share", 1-stats["person_only_residual_share"]
                         if stats.get("person_only_residual_share") is not None else None),
                         "room_share": stats.get("room_incremental_share"),
                         "residual_share": stats.get("residual_share"),
                         "person_only_residual_share": stats.get("person_only_residual_share"),
                         "null_median_room_share": float(np.median(stats["null_room_share"]))
                         if stats.get("null_room_share") else None,
                         "trials": stats["trials"], "participants": stats["participants"],
                         "rooms": stats["rooms"], "status": stats["status"]})
    output["R1"] = product("R1", question="How much rating variation follows rooms after accounting for people?",
        takeaway=("Observed incremental room shares after person effects: "
                  + "; ".join(f"E{row['experiment']} {row['axis']} {row['room_share']:.2f}"
                              for row in variance if row["room_share"] is not None) +
                  ". These are descriptive fractions, not causal effects."),
        method="Crossed additive person+room least squares; 1,000 seeded room-label-within-person negative-control draws per experiment and axis.",
        rows=variance, x="axis", y="room_share", series="experiment", chart_type="bar",
        x_label="Reported axis", y_label="Incremental room share", sample=sample, source=source,
        caveats=["The pilot has only ten rooms per experiment; the null is descriptive, not a population p-value.",
                 "E2 and E3 rating elicitation differs and remains separate."],
        units={"room_share": "fraction of total observed rating variation"})

    ranking = []
    for item in analyses:
        rows = item["source_rows"]
        intervals = _bootstrap_room_means(rows, seed=SEED)
        for room in sorted({row["room_id"] for row in rows}):
            values = [row["value"] for row in rows if row["room_id"] == room]
            lo, hi = intervals[room]
            ranking.append({"experiment": item["experiment"], "axis": item["axis"],
                            "room_id": room, "mean_rating": float(np.mean(values)),
                            "participants": len(values), "interval_low": lo,
                            "interval_high": hi, "bootstrap_draws": 2000 if lo is not None else 0})
    ranking.sort(key=lambda row: (row["experiment"], row["axis"], -row["mean_rating"]))
    output["R2"] = product("R2", question="Which rooms received higher or lower signed ratings?",
        takeaway=("Observed room-mean ranges: " + "; ".join(
            f"E{experiment} {axis} {min(row['mean_rating'] for row in ranking if row['experiment'] == experiment and row['axis'] == axis):.2f} to "
            f"{max(row['mean_rating'] for row in ranking if row['experiment'] == experiment and row['axis'] == axis):.2f}"
            for experiment in (2, 3) for axis in ("valence", "arousal")) +
            "; participant-resampled intervals stay within each source experiment."),
        method="Mean observed transformed score per room; 2,000 seeded participant-vector bootstrap draws when at least four people contribute.",
        rows=ranking, x="room_id", y="mean_rating", series="axis", facet="experiment",
        chart_type="bar", x_label="Room", y_label="Mean signed rating", sample=sample,
        source=source, caveats=["Intervals condition on the observed rooms and participants; no causal ranking follows.",
                                "A negative score expresses source rating direction, not a validated emotion diagnosis."],
        units={"mean_rating": "signed source scale −1 to 1"})

    positions = []
    for experiment in (2, 3):
        own = [row for row in trials if row["experiment"] == experiment and
               all(row["subjective"][axis] is not None for axis in ("valence", "arousal"))]
        values = np.asarray([[row["subjective"]["valence"], row["subjective"]["arousal"]]
                             for row in own], dtype=float).T
        kde = (gaussian_kde(values) if values.shape[1] >= 4 and
               np.linalg.matrix_rank(np.cov(values)) == 2 else None)
        if kde is not None:
            grid = np.linspace(-1, 1, 21)
            x_mesh, y_mesh = np.meshgrid(grid, grid)
            density = kde(np.vstack([x_mesh.ravel(), y_mesh.ravel()]))
            positions.extend({"experiment": experiment, "kind": "density_grid",
                              "valence": float(x), "arousal": float(y),
                              "density": float(z), "participant_id": None, "room_id": None}
                             for x, y, z in zip(x_mesh.ravel(), y_mesh.ravel(), density,
                                                strict=True))
        positions.extend({"experiment": experiment, "kind": "source_position",
                          "valence": row["subjective"]["valence"],
                          "arousal": row["subjective"]["arousal"],
                          "density": None, "participant_id": row["participant_id"],
                          "room_id": row["room_id"]} for row in own)
        if own:
            positions.append({"experiment": experiment, "kind": "target_vector",
                              "valence": float(np.mean(values[0])),
                              "arousal": float(np.mean(values[1])), "density": None,
                              "participant_id": None, "room_id": None,
                              "source_valence": 0.0, "source_arousal": 0.0,
                              "target_valence": float(np.mean(values[0])),
                              "target_arousal": float(np.mean(values[1]))})
    output["R3"] = product("R3", question="Where do reported experiences lie on the signed affect plane?",
        takeaway=(f"E2 has {sum(row['experiment'] == 2 and row['kind'] == 'source_position' for row in positions)} "
                  f"reported positions; E3 has {sum(row['experiment'] == 3 and row['kind'] == 'source_position' for row in positions)}. "
                  "Their densities are smoothed separately."),
        method="Source transformed signed valence/arousal points; Gaussian KDE on a fixed 21×21 grid within each experiment when covariance is nonsingular.",
        rows=positions, x="valence", y="arousal", series="density", facet="experiment",
        chart_type="heatmap", x_label="Reported valence", y_label="Reported arousal",
        sample=sample, source=source,
        caveats=["Density is descriptive smoothing of dependent participant/room observations.",
                 "Rows marked source_position preserve the observed points; density_grid rows supply the field.",
                 "E2 and E3 elicitation and scales must be read separately."],
        units={"valence": "signed −1 to 1", "arousal": "signed −1 to 1", "density": "relative density"})

    agreement = []
    for item in analyses:
        for index, part in enumerate(item["rater_partitions"].get("partitions", []), 1):
            agreement.append({"kind": "unique_partition", "experiment": item["experiment"], "axis": item["axis"],
                              "partition": f"Split {index:02d}", "group_a": ", ".join(part["group_a"]),
                              "group_b": ", ".join(part["group_b"]),
                              "shared_rooms": part["shared_rooms"],
                              "spearman_rho": part["spearman_rho"], "status": part["status"]})
        people = sorted({row["participant_id"] for row in item["source_rows"]})
        for first, second in combinations(people, 2):
            a = {row["room_id"]: row["value"] for row in item["source_rows"]
                 if row["participant_id"] == first}
            b = {row["room_id"]: row["value"] for row in item["source_rows"]
                 if row["participant_id"] == second}
            shared = sorted(set(a) & set(b))
            av, bv = np.asarray([a[room] for room in shared]), np.asarray([b[room] for room in shared])
            rho = (float(spearmanr(av, bv).statistic) if len(shared) >= 3 and
                   np.var(av) > 1e-12 and np.var(bv) > 1e-12 else None)
            agreement.append({"kind": "person_pair", "experiment": item["experiment"],
                              "axis": item["axis"], "partition": first + " × " + second,
                              "group_a": first, "group_b": second,
                              "shared_rooms": len(shared), "spearman_rho": rho,
                              "status": "descriptive" if rho is not None else
                              "unavailable_constant_or_few_rooms"})
    output["R4"] = product("R4", question="Do groups of raters rank the same rooms similarly?",
        takeaway=("Median rank agreement across ten overlapping unique splits: " + "; ".join(
            f"E{item['experiment']} {item['axis']} "
            f"{np.median([part['spearman_rho'] for part in item['rater_partitions']['partitions'] if part['spearman_rho'] is not None]):.2f}"
            for item in analyses) + "."),
        method="E2 two-versus-three and E3 three-versus-three participant partitions plus pairwise participant room-profile comparisons; Spearman correlation of shared-room ranks.",
        rows=agreement, x="partition", y="spearman_rho", series="axis", facet="experiment",
        chart_type="bar", x_label="Unique participant split", y_label="Room-rank agreement",
        sample=sample, source=source,
        caveats=["Rows distinguish unique_partition from person_pair; both reuse people and rooms.",
                 "Partitions overlap heavily and are not ten independent studies.",
                 "Constant or fewer than three shared-room profiles yield null correlation."],
        units={"spearman_rho": "Spearman ρ"})

    style = []
    for item in analyses:
        by_person = {person: [row["value"] for row in item["source_rows"]
                              if row["participant_id"] == person]
                     for person in sorted({row["participant_id"] for row in item["source_rows"]})}
        for person, values in by_person.items():
            style.append({"experiment": item["experiment"], "axis": item["axis"],
                          "participant_id": person, "mean_rating": float(np.mean(values)),
                          "rating_sd": float(np.std(values, ddof=1)) if len(values) > 1 else None,
                          "range": float(max(values)-min(values)), "trials": len(values)})
    output["R5"] = product("R5", question="How do participants use the signed rating scales?",
        takeaway=(f"Across {len({(row['experiment'], row['participant_id']) for row in style})} "
                  "participant-by-experiment profiles, observed within-person rating ranges "
                  f"span {min(row['range'] for row in style):.2f}–"
                  f"{max(row['range'] for row in style):.2f} source-scale units."),
        method="Observed per-person mean, sample standard deviation and range for each experiment/axis.",
        rows=style, x="participant_id", y="mean_rating", series="axis",
        facet="experiment", chart_type="scatter", x_label="Participant",
        y_label="Mean signed rating", sample=sample, source=source,
        caveats=["Few rooms per person cannot identify stable personal response style.",
                 "Scale use is not comparable across E2/E3 elicitation without calibration."],
        units={"mean_rating": "signed source scale −1 to 1", "rating_sd": "source scale"})
    return output
