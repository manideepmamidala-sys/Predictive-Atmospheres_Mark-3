"""Transfer, controls, generalization, importance and training products P1–P5."""

from __future__ import annotations

import numpy as np

from pa.analysis.catalogue import counts, product


def _null_summary(values: list[float], observed: float | None) -> dict:
    finite = np.asarray([value for value in values if value is not None and
                         np.isfinite(value)], dtype=float)
    if not len(finite):
        return {"draws": 0, "observed": observed, "null_median": None,
                "null_low": None, "null_high": None}
    return {"draws": len(finite), "observed": observed,
            "null_median": float(np.median(finite)),
            "null_low": float(np.quantile(finite, 0.025)),
            "null_high": float(np.quantile(finite, 0.975))}


def _null_histogram(values: list[float], observed: float | None, *,
                    experiment: int, axis: str, analysis: str, metric: str) -> list[dict]:
    """Export the actual draw distribution on a fixed, labelled control-specific grid."""
    summary = _null_summary(values, observed)
    finite = np.asarray([value for value in values if value is not None and
                         np.isfinite(value)], dtype=float)
    if not len(finite):
        return []
    low, high = float(np.min(finite)), float(np.max(finite))
    if low == high:
        low -= 0.5
        high += 0.5
    edges = np.linspace(low, high, 21)
    hist, _ = np.histogram(finite, bins=edges)
    control = f"E{experiment} {axis}: {analysis.replace('_', ' ')}"
    return [{"experiment": experiment, "axis": axis, "analysis": analysis,
             "control": control, "metric": metric, "bin_left": float(edges[i]),
             "bin_center": float((edges[i] + edges[i + 1]) / 2),
             "bin_right": float(edges[i + 1]), "draw_count": int(count),
             **summary}
            for i, count in enumerate(hist)]


def prediction_products(source: dict, ratings: dict, evaluation: dict,
                        report_comparator: dict, null: dict, learning: dict) -> dict:
    cohort_ids = set(evaluation["cohort"]["ids"])
    cohort = [row for row in source["trials"] if row["id"] in cohort_ids]
    sample = counts(cohort)
    output = {}

    transfer = []
    for analysis in ratings["analyses"]:
        if analysis["experiment"] not in (2, 3):
            continue
        result = analysis["known_room_relative_transfer"]
        for fold in result.get("folds", []):
            transfer.append({"experiment": analysis["experiment"], "axis": analysis["axis"],
                             "participant_id": fold["participant_id"],
                             "status": fold["status"], "known_rooms": fold["known_rooms"],
                             "mae": fold.get("mae"), "zero_baseline_mae": fold.get("zero_baseline_mae"),
                             "spearman_rho": fold.get("spearman_rho"),
                             "held_out_observed_center": fold.get("held_out_observed_center")})
    output["P1"] = product("P1", question="Can other people's ratings describe a known room's relative response for a held-out person?",
        takeaway=("Relative known-room MAE versus zero-profile baseline: " + "; ".join(
            f"E{item['experiment']} {item['axis']} "
            f"{item['known_room_relative_transfer']['observed_mean_mae']:.3f} vs "
            f"{item['known_room_relative_transfer']['zero_baseline_mean_mae']:.3f}"
            for item in ratings["analyses"] if item["experiment"] in (2, 3)) + "."),
        method="Leave-one-person-out; center training people's observed ratings, predict their known-room mean profile, center held-out ratings using that person's observed mean only for relative evaluation.",
        rows=transfer, x="participant_id", y="mae", series="axis", facet="experiment",
        chart_type="bar", x_label="Held-out participant", y_label="Relative-profile MAE",
        sample=counts([row for row in source["trials"] if row["experiment"] in (2, 3)]),
        source=source,
        caveats=["The held-out person's own observed mean is used to center evaluation outcomes; this is not absolute prediction for an unobserved person.",
                 "Rooms are already known from training people; results do not test unseen rooms."],
        units={"mae": "signed source scale", "spearman_rho": "Spearman ρ"})

    null_rows = []
    for analysis in ratings["analyses"]:
        if analysis["experiment"] not in (2, 3):
            continue
        e, axis = analysis["experiment"], analysis["axis"]
        crossed = analysis["crossed_additive"]
        null_rows.extend(_null_histogram(
            crossed.get("null_room_share", []), crossed.get("room_incremental_share"),
            experiment=e, axis=axis, analysis="room_label_within_person_room_share",
            metric="room_share"))
        relative = analysis["known_room_relative_transfer"]
        null_rows.extend(_null_histogram(
            relative.get("null_mean_mae", []), relative.get("observed_mean_mae"),
            experiment=e, axis=axis, analysis="known_room_relative_transfer",
            metric="mean_mae"))
    spatial_values = null.get("null_mean_mae", [])
    null_rows.extend(_null_histogram(
        spatial_values, null.get("observed", {}).get("mean_mae"),
        experiment=3, axis="fused_valence_arousal_mean",
        analysis="unseen_room_whole_attribute_shuffle_full_refit", metric="mean_mae"))
    reason = None if (null.get("status") == "complete" and len(spatial_values) == 1000 and
                     len(null_rows) == 9 * 20 and
                     all(row["draws"] == 1000 for row in null_rows)) else (
        "One or more prespecified 1,000-draw controls are incomplete; publication is withheld.")
    output["P2"] = product("P2", question="How do observed results compare with prespecified shuffled controls?",
        takeaway=(f"The observed E3 fused room MAE is {null['observed']['mean_mae']:.3f} "
                  f"versus {float(np.median(spatial_values)):.3f} across 1,000 full-refit shuffled controls; "
                  "eight separate rating/transfer controls are shown on their own scales."
                  if reason is None else
                  "The prespecified shuffled-control comparison is awaiting all 1,000 draws per control."),
        method="For ratings and transfer, 1,000 within-training-person room-label draws; for spatial prediction, 1,000 whole training-room attribute shuffles with frozen outer folds and full inner refit.",
        rows=null_rows if reason is None else [], x="bin_center", y="draw_count",
        facet="control", chart_type="bar", x_label="Shuffled control statistic",
        y_label="Draw count", sample=counts([row for row in source["trials"]
                                            if row["experiment"] in (2, 3)]),
        source=source, availability_reason=reason,
        caveats=["Metrics differ across analyses: room share versus MAE, so compare each only with its own null range.",
                 "Draws overlap in rooms/people and do not provide independent population inference.",
                 "The spatial model control uses only 23 complete E3 trials; the displayed count is the broader E2/E3 rating source context.",
                 "The full draw arrays and exact folds remain in versioned source analysis files."],
        units={"observed": "see metric per row", "bin_center": "see metric per row",
               "draw_count": "full-refit or label-shuffle draws"})

    curve = []
    for point in learning.get("points", []):
        k = point["training_room_count"]
        curve.append({"kind": "learning_curve", "training_room_count": k,
                      "candidate": "inner_selected", "mean_mae": point["mean_mae"],
                      "evaluated_subsets": point["evaluated_subsets"],
                      "requested_subsets": len(point["subsets"]),
                      "experiment": 3, "outer_group": None,
                      "target_type": evaluation["target_type"],
                      "error_unit": "constructed-coordinate units",
                      "trials": evaluation["cohort"]["rows"],
                      "participants": evaluation["cohort"]["participants"],
                      "rooms": evaluation["cohort"]["rooms"], "held_out_trials": None})
        curve.append({"kind": "learning_curve", "training_room_count": k,
                      "candidate": "dummy_median", "mean_mae": point["baseline_median_mae"],
                      "evaluated_subsets": point["evaluated_subsets"],
                      "requested_subsets": len(point["subsets"]),
                      "experiment": 3, "outer_group": None,
                      "target_type": evaluation["target_type"],
                      "error_unit": "constructed-coordinate units",
                      "trials": evaluation["cohort"]["rows"],
                      "participants": evaluation["cohort"]["participants"],
                      "rooms": evaluation["cohort"]["rooms"], "held_out_trials": None})
    for fold in evaluation["evaluation"]["room"]["folds"]:
        if fold["status"] == "evaluated":
            curve.append({"kind": "held_out_room_fold", "training_room_count": None,
                          "candidate": fold["selection"]["name"],
                          "mean_mae": fold["mean_mae"], "evaluated_subsets": 1,
                          "requested_subsets": 1, "experiment": 3,
                          "outer_group": fold["group"],
                          "target_type": evaluation["target_type"],
                          "error_unit": "constructed-coordinate units",
                          "trials": evaluation["cohort"]["rows"],
                          "participants": evaluation["cohort"]["participants"],
                          "rooms": evaluation["cohort"]["rooms"],
                          "held_out_trials": len(fold["test_indices"])})
    for comparator in report_comparator["experiments"]:
        room_eval = comparator.get("evaluation", {}).get("room", {})
        curve.append({"kind": "self_report_only_comparator", "training_room_count": None,
                      "candidate": "E" + str(comparator["experiment"]) + " self-report",
                      "mean_mae": room_eval.get("mean_mae"),
                      "evaluated_subsets": len(room_eval.get("folds", [])),
                      "requested_subsets": len(room_eval.get("folds", [])),
                      "experiment": comparator["experiment"], "outer_group": None,
                      "target_type": comparator["target_type"],
                      "error_unit": "signed source rating scale",
                      "trials": comparator["rows"],
                      "participants": comparator["participants"],
                      "rooms": comparator["rooms"], "held_out_trials": None})
    curve_reason = (None if learning.get("status") == "descriptive" and
                    sum(len(point["subsets"]) for point in learning.get("points", [])) == 455
                    else "The prespecified 455 unique training-room subsets were not all computed.")
    output["P3"] = product("P3", question="How accurately do room attributes predict a new E3 room, and what changes with training-room count?",
        takeaway=(f"E3 fused held-out-room MAE is {evaluation['evaluation']['room']['aggregate']['mean_metrics']['mean_mae']:.3f} "
                  f"versus median baseline {evaluation['evaluation']['room']['aggregate']['mean_metrics']['baseline_median_mae']:.3f}; "
                  "the final fitted Studio model is baseline-only."),
        method="Leave-one-E3-room-out nested grouped selection; k=4–9 unique room-subset learning curve with up to 100 subsets per k, compared with the training-median baseline.",
        rows=curve if curve_reason is None else [], x="training_room_count", y="mean_mae",
        series="candidate", chart_type="line", x_label="Distinct training rooms",
        y_label="Mean absolute error (see row target)", sample=sample,
        source=source, availability_reason=curve_reason,
        caveats=["Overlapping room subsets create descriptive variability, not independent replications.",
                 "Caption counts describe the primary E3 fused cohort; self-report-only E2/E3 rows carry their own trial/person/room counts, target type and error unit in the data table.",
                 "Self-report-only comparator rows use signed source reports, are research-only, and are not Studio alternatives.",
                 "No observed improvement over a fixed median baseline and no calibrated error radius."],
        units={"mean_mae": "row-specific error unit (constructed coordinate or signed source rating)",
               "trials": "source trials", "participants": "source people", "rooms": "source rooms"})

    selection = evaluation.get("final_selection") or {}
    candidate = (selection.get("candidate") or {}).get("name")
    importance_reason = ("The fitted E3 model selected a constant dummy baseline; it has no spatial "
                         "feature attribution to estimate. Publishing nonzero importance would invent a learned effect."
                         if candidate and candidate.startswith("dummy_") else
                         "Feature importance has not been validated for this fitted model.")
    output["P4"] = product("P4", question="Which room inputs matter to the fitted predictor?",
        takeaway=importance_reason, method="Exploratory model-specific feature importance would be shown only beside grouped performance and only for a nonconstant fitted model.",
        rows=[], x="feature", y="importance", chart_type="bar",
        x_label="Independent room input", y_label="Exploratory importance",
        sample=sample, source=source, availability_reason=importance_reason,
        caveats=["A constant baseline has no feature-level explanation.",
                 "No causal feature effect can be read from small grouped predictive comparisons."],
        units={"importance": "unavailable"})

    stages = [("reviewed_trial_ledger", 160),
              ("E3_source_trials", sum(row["experiment"] == 3 for row in source["trials"])),
              ("E3_complete_raw_components_and_reports", evaluation["cohort"]["rows"]),
              ("independent_E3_room_groups", evaluation["cohort"]["rooms"]),
              ("fitted_artifact_training_trials", evaluation["cohort"]["rows"])]
    diagram = [{"stage": name, "order": index, "count": count,
                "unit": "rooms" if "groups" in name else "trials",
                "scope": "E3-only full independent attributes" if index >= 2 else "source"}
               for index, (name, count) in enumerate(stages, 1)]
    output["P5"] = product("P5", question="How was the deployable fused model trained without using held-out outcomes?",
        takeaway=(f"Only {evaluation['cohort']['rows']} complete E3 trials across "
                  f"{evaluation['cohort']['rooms']} rooms and "
                  f"{evaluation['cohort']['participants']} people enter the Studio fit; "
                  f"the selected model is {candidate or 'unavailable'}."),
        method="Source eligibility → reviewed physiology → raw complete E3 cohort → grouped inner selection → full-data population calibration and fitted pipeline.",
        rows=diagram, x="stage", y="count", chart_type="bar",
        x_label="Training stage", y_label="Observed count", sample=sample, source=source,
        caveats=["The room-group row uses rooms; all other count rows use trials.",
                 "Calibration, imputation and encoding are fitted within each evaluation training partition.",
                 "The fitted full-data artifact is scoped to source E3 rooms; deployment beyond their support is experimental."],
        units={"count": "row-specific unit"})
    return output
