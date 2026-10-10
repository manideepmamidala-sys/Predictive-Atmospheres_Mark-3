"""Reconstruct saved outer-fold predictions without rerunning model selection."""

from __future__ import annotations

import numpy as np

from pa.modeling.evaluate import group_mae, make_estimator
from pa.modeling.targets import PopulationCalibrator
from pa.modeling.train import Cohort


def outer_prediction_evidence(cohort: Cohort, evaluation: dict) -> dict:
    """Refit recorded selections on their training rows; verify stored fold scores."""
    evidence = {}
    for question, groups in (("room", cohort.room_groups), ("subject", cohort.subject_groups)):
        folds = []
        for record in evaluation[question]["folds"]:
            if record["status"] != "evaluated":
                folds.append({"group": record["group"], "status": record["status"],
                              "reason": record.get("reason"),
                              "test_trial_ids": [cohort.ids[i] for i in record["test_indices"]]})
                continue
            train = np.asarray(record["train_indices"], dtype=int)
            test = np.asarray(record["test_indices"], dtype=int)
            calibration = PopulationCalibrator.fit(cohort.raw.iloc[train])
            y_train = calibration.fused(cohort.raw.iloc[train], cohort.reports[train])
            y_test = calibration.fused(cohort.raw.iloc[test], cohort.reports[test])
            predictions = {}
            for name, spec in (("selected", record["selection"]),
                               ("dummy_median", {"name": "dummy_median"}),
                               ("dummy_mean", {"name": "dummy_mean"})):
                estimator = make_estimator(spec)
                estimator.fit(cohort.X.iloc[train], y_train)
                predicted = np.asarray(estimator.predict(cohort.X.iloc[test]), dtype=float)
                valence, arousal, mean = group_mae(predicted, y_test, groups[test])
                expected = (record["mean_mae"] if name == "selected" else
                            record["baselines"][name]["mean_mae"])
                if not np.isclose(mean, expected, atol=1e-12, rtol=1e-12):
                    raise ValueError(f"outer prediction evidence disagrees with saved {question}/{record['group']}/{name}")
                if name == "selected" and (not np.isclose(valence, record["valence_mae"], atol=1e-12,
                                                        rtol=1e-12) or
                                           not np.isclose(arousal, record["arousal_mae"], atol=1e-12,
                                                          rtol=1e-12)):
                    raise ValueError("outer prediction axis MAE disagrees with saved fold")
                predictions[name] = {"coordinates": predicted.tolist(),
                                     "valence_mae": valence, "arousal_mae": arousal,
                                     "mean_mae": mean}
            folds.append({"group": record["group"], "status": "evaluated",
                          "train_trial_ids": [cohort.ids[i] for i in train],
                          "test_trial_ids": [cohort.ids[i] for i in test],
                          "train_group_ids": sorted({str(value) for value in groups[train]}),
                          "test_group_ids": sorted({str(value) for value in groups[test]}),
                          "observed_fused_coordinates": y_test.tolist(),
                          "selected_candidate": record["selection"],
                          "predictions": predictions,
                          "outer_training_calibrator": {"centers": calibration.centers,
                                                        "scales": calibration.scales}})
        evidence[question] = {"folds": folds, "target_type": "E3_complete_fusion_population_calibrated",
                              "calibration_rule": "fit on outer-training raw components only"}
    return evidence
