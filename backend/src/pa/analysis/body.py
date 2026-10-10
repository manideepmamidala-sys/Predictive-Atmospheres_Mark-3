"""Reviewed signal, component agreement and affect-density products B1–B8."""

from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy import signal
from scipy.stats import gaussian_kde

from pa.analysis.catalogue import counts, product
from pa.io.metadata import Trial
from pa.io.recordings import read_recording, recording_path
from pa.signals.common import decisions


def _comparison(validity: dict, experiment: int, left: str, right: str) -> dict | None:
    return next((row for row in validity["comparisons"] if row["experiment"] == experiment
                 and row["left"] == left and row["right"] == right), None)


def _spectral_rows(metadata: list[Trial], signals: list[dict], reviews: dict) -> list[dict]:
    """Median first accepted-epoch PSD per reviewed channel and experiment."""
    by_id = {row["trial_id"]: row for row in reviews["trials"]}
    by_signal = {row["id"]: row for row in signals}
    cfg = decisions()["eeg"]
    epoch_size = round(float(cfg["epoch_s"]) * 500)
    nperseg = round(float(cfg["welch_segment_s"]) * 500)
    noverlap = round(nperseg * float(cfg["welch_overlap_fraction"]))
    sos = signal.butter(cfg["filter_order"], cfg["filter_hz"], btype="bandpass",
                        fs=500, output="sos")
    psds: dict[tuple[int, str, float], list[float]] = defaultdict(list)
    for trial in metadata:
        trial_id = f"E{trial.experiment}:{trial.subject_id}:{trial.room_id}"
        source = by_signal[trial_id]
        review = by_id[trial_id]["reviewed_eligibility"]
        available = [name for name in ("right", "left") if review[f"eeg_{name}"]]
        if not available:
            continue
        raw = read_recording(recording_path(trial))
        for channel in available:
            channel_qc = source["eeg"]["channel_qc"][channel]
            rejected = {item["index"] for item in channel_qc["rejected_epochs"]}
            first = next((index for index in range(channel_qc["total_epochs"])
                          if index not in rejected), None)
            if first is None:
                continue
            vector = raw.right_forehead if channel == "right" else raw.left_forehead
            epoch = vector[first * epoch_size:(first+1) * epoch_size]
            if len(epoch) != epoch_size:
                continue
            cleaned = signal.sosfiltfilt(sos, epoch)
            frequencies, density = signal.welch(cleaned, fs=500, window="hann",
                                                nperseg=nperseg, noverlap=noverlap)
            for hz, value in zip(frequencies, density, strict=True):
                if 1 <= hz <= 45:
                    psds[(trial.experiment, channel, float(hz))].append(float(value))
    return [{"kind": "accepted_epoch_spectrum", "experiment": experiment,
             "channel": channel, "frequency_hz": hz,
             "median_psd": float(np.median(values)), "trials": len(values),
             "band": None, "median_band_power": None}
            for (experiment, channel, hz), values in sorted(psds.items())]


def _density_rows(trials: list[dict]) -> list[dict]:
    rows = []
    for experiment in (2, 3):
        complete = [row for row in trials if row["experiment"] == experiment and
                    row["construction"]["cohort"] == "complete_fusion"]
        for component, key in (("physiology-derived", "objective"),
                               ("self-reported", "subjective"), ("fused", "fused")):
            positions = np.asarray([[row["construction"][key]["valence"],
                                     row["construction"][key]["arousal"]]
                                    for row in complete], dtype=float)
            if len(positions) < 4 or np.linalg.matrix_rank(np.cov(positions.T)) != 2:
                continue
            estimator = gaussian_kde(positions.T)
            grid = np.linspace(-1, 1, 21)
            x_mesh, y_mesh = np.meshgrid(grid, grid)
            density = estimator(np.vstack([x_mesh.ravel(), y_mesh.ravel()]))
            rows.extend({"experiment": experiment, "component": component,
                         "kind": "density_grid", "valence": float(x),
                         "arousal": float(y), "density": float(z),
                         "participant_id": None, "room_id": None,
                         "source_valence": None, "source_arousal": None,
                         "target_valence": None, "target_arousal": None}
                        for x, y, z in zip(x_mesh.ravel(), y_mesh.ravel(), density,
                                           strict=True))
            rows.extend({"experiment": experiment, "component": component,
                         "kind": "source_position", "valence": float(pair[0]),
                         "arousal": float(pair[1]), "density": None,
                         "participant_id": row["participant_id"], "room_id": row["room_id"],
                         "source_valence": None, "source_arousal": None,
                         "target_valence": None, "target_arousal": None}
                        for row, pair in zip(complete, positions, strict=True))
            mean = np.mean(positions, axis=0)
            rows.append({"experiment": experiment, "component": component,
                         "kind": "target_vector", "valence": float(mean[0]),
                         "arousal": float(mean[1]), "density": None,
                         "participant_id": None, "room_id": None,
                         "source_valence": 0.0, "source_arousal": 0.0,
                         "target_valence": float(mean[0]), "target_arousal": float(mean[1])})
    return rows


def body_products(source: dict, signal_detail: dict, review: dict, validity: dict,
                  metadata: list[Trial]) -> dict:
    trials = source["trials"]
    sample = counts(trials)
    output = {}
    qc_rows = []
    for experiment in (1, 2, 3):
        own = [row for row in review["trials"] if row["experiment"] == experiment]
        for key in ("timebase", "eeg_right", "eeg_left", "eeg_bilateral", "ecg_hr", "ecg_rmssd"):
            qc_rows.append({"experiment": experiment, "branch": key,
                            "eligible_trials": sum(bool(row["reviewed_eligibility"][key])
                                                   for row in own), "total_trials": len(own),
                            "ineligible_trials": sum(not row["reviewed_eligibility"][key]
                                                     for row in own)})
    output["B1"] = product("B1", question="Which signals passed reviewed quality and timebase checks?",
        takeaway=("Among 160 reviewed source trials, "
                  f"{sum(row['reviewed_eligibility']['timebase'] for row in review['trials'])} pass the conditional timebase, "
                  f"{sum(row['reviewed_eligibility']['eeg_bilateral'] for row in review['trials'])} retain bilateral EEG, "
                  f"{sum(row['reviewed_eligibility']['ecg_hr'] for row in review['trials'])} retain HR and "
                  f"{sum(row['reviewed_eligibility']['ecg_rmssd'] for row in review['trials'])} retain RMSSD."),
        method="Count CP-B reviewed component-specific eligibility independently per experiment; no rejected component is replaced with zero.",
        rows=qc_rows, x="branch", y="eligible_trials", series="experiment",
        chart_type="bar", x_label="Quality branch", y_label="Eligible trials",
        sample=sample, source=source,
        caveats=["Review inspected selected signal panels and all machine evidence; it was AI-assisted, not a personal owner signoff.",
                 "Sample rate, units and reference remain conditionally unconfirmed."],
        units={"eligible_trials": "trials"})

    spectral = _spectral_rows(metadata, signal_detail["trials"], review)
    for row in signal_detail["trials"]:
        state = next(item["reviewed_eligibility"] for item in review["trials"]
                     if item["trial_id"] == row["id"])
        for channel in ("right", "left"):
            if not state[f"eeg_{channel}"]:
                continue
            powers = row["eeg"]["channel_qc"][channel]["powers"]
            for band, power in powers.items():
                if power is not None:
                    spectral.append({"kind": "reviewed_band_power", "experiment": row["experiment"],
                                     "channel": channel, "frequency_hz": None,
                                     "median_psd": None, "trials": 1, "band": band,
                                     "median_band_power": power})
    output["B2"] = product("B2", question="What spectral and band-balance evidence remains after EEG review?",
        takeaway=(f"{sum(row['reviewed_eligibility']['eeg_right'] for row in review['trials'])} right and "
                  f"{sum(row['reviewed_eligibility']['eeg_left'] for row in review['trials'])} left channel-trials "
                  "remain eligible for accepted-epoch spectral description."),
        method="One first accepted 4-second epoch per reviewed channel/trial, 1–45 Hz Welch PSD with approved 1–45 Hz filter; band rows preserve QC median accepted-epoch powers.",
        rows=spectral, x="frequency_hz", y="median_psd", series="channel",
        facet="experiment", chart_type="line", x_label="Frequency",
        y_label="Median accepted-epoch PSD",
        sample=counts([row for row in trials if any(
            item["trial_id"] == row["id"] and (
                item["reviewed_eligibility"]["eeg_right"] or
                item["reviewed_eligibility"]["eeg_left"])
            for item in review["trials"])]), source=source,
        caveats=["Squared raw amplitudes have unverified units and reference; PSD is not source-calibrated power.",
                 "Only first accepted epoch per reviewed channel contributes to the plotted spectral curve; band rows use all accepted epochs.",
                 "Rows marked reviewed_band_power encode band balance separately."],
        units={"frequency_hz": "Hz", "median_psd": "unverified amplitude²/Hz",
               "median_band_power": "unverified amplitude²"})

    cardiac = []
    for row in trials:
        hr = row["heart_rate_bpm"]
        rmssd = row["rmssd_ms"]
        if hr is not None or rmssd is not None:
            normalized_rmssd = row["normalized_components"]["rmssd_ms"]
            cardiac.append({"kind": "reviewed_trial", "experiment": row["experiment"],
                            "participant_id": row["participant_id"], "room_id": row["room_id"],
                            "heart_rate_bpm": hr, "rmssd_ms": rmssd,
                            "negative_log_rmssd_sensitivity": -normalized_rmssd
                            if normalized_rmssd is not None else None,
                            "time_s": None, "trace_amplitude": None})
    signal_by_id = {row["id"]: row for row in signal_detail["trials"]}
    for experiment in (1, 2, 3):
        example = next((row for row in trials if row["experiment"] == experiment and
                        row["heart_rate_bpm"] is not None), None)
        if example is None:
            continue
        trace = signal_by_id[example["id"]]["ecg_trace"]
        clean = trace["cleaned"]
        rate = trace["sample_rate_hz"]
        if rate:
            cardiac.extend({"kind": "reviewed_trace_example", "experiment": experiment,
                            "participant_id": example["participant_id"],
                            "room_id": example["room_id"], "heart_rate_bpm": None,
                            "rmssd_ms": None, "negative_log_rmssd_sensitivity": None,
                            "time_s": float(index / rate + trace["window_start_s"]),
                            "trace_amplitude": float(clean[index])}
                           for index in range(0, min(len(clean), 1000), 5))
    output["B3"] = product("B3", question="What valid heart-rate and RMSSD evidence is available?",
        takeaway=f"Reviewed HR is available in {sum(row['heart_rate_bpm'] is not None for row in trials)} trials; RMSSD in {sum(row['rmssd_ms'] is not None for row in trials)}.",
        method="Only reviewed valid HR/RMSSD; negative calibrated log-RMSSD is a separate descriptive sensitivity, never a required fused component.",
        rows=cardiac, x="heart_rate_bpm", y="rmssd_ms", series="experiment",
        chart_type="scatter", x_label="Heart rate", y_label="RMSSD",
        sample=counts([row for row in trials if row["heart_rate_bpm"] is not None or
                       row["rmssd_ms"] is not None]), source=source,
        caveats=["HR and RMSSD have distinct coverage gates; null is not zero.",
                 "Wrist ECG morphology and units are unconfirmed; trace-example rows are short cleaned display samples."],
        units={"heart_rate_bpm": "beats/min", "rmssd_ms": "ms",
               "time_s": "s", "trace_amplitude": "unverified raw amplitude"})

    cortical = []
    for row in trials:
        if row["experiment"] not in (2, 3) or row["subjective"]["arousal"] is None:
            continue
        for candidate, value in (("eeg_composite", row["construction"]["eeg_arousal"]),
                                 ("alpha_suppression", row["normalized_components"]["alpha_suppression"]),
                                 ("engagement", row["normalized_components"]["engagement"])):
            if value is not None:
                cortical.append({"experiment": row["experiment"],
                                 "participant_id": row["participant_id"],
                                 "room_id": row["room_id"], "candidate": candidate,
                                 "candidate_value": value,
                                 "report_arousal": row["subjective"]["arousal"]})
    summaries = []
    for experiment in (2, 3):
        for candidate in ("eeg_composite", "alpha_suppression", "engagement"):
            item = _comparison(validity, experiment, candidate, "report_arousal")
            if item:
                summaries.append(f"E{experiment} {candidate}: {item['trials']} trials/"
                                 f"{item['participants']} people, mean person ρ "
                                 f"{item['equal_participant_mean_rho']:.2f}"
                                 if item["equal_participant_mean_rho"] is not None else
                                 f"E{experiment} {candidate}: unavailable")
    contributing_ids = {(row["experiment"], row["participant_id"], row["room_id"])
                        for row in cortical}
    output["B4"] = product("B4", question="Do cortical candidates agree with reported arousal?",
        takeaway="; ".join(summaries),
        method="Compare normalized alpha suppression, engagement and their equal EEG composite with original signed arousal separately by experiment; participant-level Spearman summaries.",
        rows=cortical, x="candidate_value", y="report_arousal", series="candidate",
        facet="experiment", chart_type="scatter", x_label="Cortical candidate",
        y_label="Reported arousal",
        sample=counts([row for row in trials if (row["experiment"], row["participant_id"],
                                                  row["room_id"]) in contributing_ids]),
        source=source,
        caveats=["Three candidate rows may describe the same source trial; counts use unique trials.",
                 "Within-person correlations and participant resampling retain repeated-room dependence.",
                 "These approximate forehead features are not validated arousal measurements."],
        units={"candidate_value": "signed descriptive coordinate",
               "report_arousal": "signed source scale −1 to 1"})

    relationships = (("B5", "eeg_composite", "heart_rate", "eeg_arousal", "heart_rate_bpm",
                      "Do cortical arousal and heart rate move together?"),
                     ("B6", "faa", "report_valence", "faa", "subjective_valence",
                      "Does forehead alpha asymmetry agree with reported valence?"))
    for identifier, left_name, right_name, x_key, y_key, question in relationships:
        points = []
        for row in trials:
            if row["experiment"] not in (2, 3):
                continue
            x = row["construction"]["eeg_arousal"] if x_key == "eeg_arousal" else row["faa"]
            y = (row["subjective"]["arousal"] if y_key == "subjective_arousal" else
                 row["subjective"]["valence"] if y_key == "subjective_valence" else
                 row["heart_rate_bpm"])
            if x is not None and y is not None:
                points.append({"experiment": row["experiment"],
                               "participant_id": row["participant_id"],
                               "room_id": row["room_id"], x_key: x, y_key: y})
        comparison = [_comparison(validity, experiment, left_name, right_name)
                      for experiment in (2, 3)]
        summaries = []
        for experiment, entry in zip((2, 3), comparison, strict=True):
            plotted = [row for row in points if row["experiment"] == experiment]
            if identifier == "B5":
                display = (f"E{experiment}: {len(plotted)} plotted raw-HR pairs from "
                           f"{len({row['participant_id'] for row in plotted})} people; ")
                if entry and entry["equal_participant_mean_rho"] is not None:
                    summaries.append(display + f"{entry['trials']} calibrated-HR correlation "
                                     f"pairs from {entry['participants']} people, equal-person "
                                     f"mean ρ {entry['equal_participant_mean_rho']:.2f}")
                else:
                    summaries.append(display + "calibrated-HR correlation unavailable")
            else:
                summaries.append(f"E{experiment}: {entry['trials']} paired trials, "
                                 f"{entry['participants']} people, equal-person mean ρ "
                                 f"{entry['equal_participant_mean_rho']:.2f}"
                                 if entry and entry["equal_participant_mean_rho"] is not None else
                                 f"E{experiment}: correlation unavailable")
        summary = "; ".join(summaries)
        method = ("Scatter reviewed EEG arousal against raw heart rate in beats/min. "
                  "Within-person Spearman uses calibrated normalized heart rate with at least "
                  "three variable pairs per contributing person; the equal-person summary "
                  "uses that smaller cohort, with 2,000 participant-vector bootstrap draws "
                  "only when at least four people contribute."
                  if identifier == "B5" else
                  "Reviewed eligible paired components; participant-level Spearman and "
                  "equal-person descriptive summary, 2,000 participant-vector bootstrap "
                  "draws only with ≥4 contributors.")
        caveats = ["The plotted trials repeat rooms/people; relationship summaries use participants as units.",
                   "Acquisition and construct uncertainty limit physiological interpretation.",
                   "E2/E3 correlations are separate; absent interval reflects fewer than four contributing people."]
        if identifier == "B5":
            caveats.append("Raw heart-rate pairs can remain visible when within-person calibration "
                           "is unavailable; those pairs do not enter the correlation cohort.")
        output[identifier] = product(identifier, question=question, takeaway=summary,
            method=method,
            rows=points, x=x_key, y=y_key, series="participant_id", facet="experiment",
            chart_type="scatter", x_label=left_name.replace("_", " "),
            y_label=right_name.replace("_", " "), sample=counts(points), source=source,
            caveats=caveats,
            units={x_key: "signed descriptive coordinate" if x_key == "eeg_arousal"
                   else "unverified log alpha ratio",
                   y_key: "beats/min" if y_key == "heart_rate_bpm" else "signed source scale"})

    divergence = []
    for experiment, entries in validity["divergence"].items():
        divergence.extend({"experiment": int(experiment), **item} for item in entries)
    disagreement = []
    contributing = []
    for row in trials:
        if row["experiment"] not in (2, 3):
            continue
        paired = False
        for axis in ("valence", "arousal"):
            report = row["construction"]["subjective"][axis]
            physiology = row["construction"]["objective"][axis]
            if report is None or physiology is None:
                continue
            paired = True
            disagreement.append({"kind": "physiology_vs_report", "experiment": row["experiment"],
                                 "participant_id": row["participant_id"], "room_id": row["room_id"],
                                 "axis": axis, "cohort": row["construction"]["cohort"],
                                 "reported_axis": report, "physiology_axis": physiology,
                                 "objective_minus_subjective": physiology-report,
                                 "eeg_robust_z": None, "heart_rate_robust_z": None})
        if paired:
            contributing.append(row)
    disagreement.extend({"kind": "eeg_hr_divergence", "experiment": row["experiment"],
                         "participant_id": row["participant_id"], "room_id": row["room_id"],
                         "axis": "arousal", "cohort": None, "reported_axis": None,
                         "physiology_axis": None, "objective_minus_subjective": None,
                         "eeg_robust_z": row["eeg_robust_z"],
                         "heart_rate_robust_z": row["heart_rate_robust_z"]}
                        for row in divergence)
    output["B7"] = product("B7", question="Where do physiology-derived and reported coordinates disagree?",
        takeaway=(f"{len(contributing)} trials have at least one paired physiology/report axis; "
                  f"{len(divergence)} also meet the separate EEG-versus-HR robust-z divergence rule."),
        method="Paired signed physiology-minus-report axes are plotted by trial and cohort; five prespecified opposite-sign EEG/HR robust-z candidates remain separately labeled rows.",
        rows=disagreement, x="reported_axis", y="physiology_axis", series="axis",
        facet="experiment", chart_type="scatter", x_label="Self-reported axis",
        y_label="Physiology-derived axis", sample=counts(contributing), source=source,
        caveats=["Cohort and axis determine availability; partial points are not complete fusion.",
                 "Opposite signs do not establish stress, masking, privacy effects or causality.",
                 "Rows distinguish physiology_vs_report from eeg_hr_divergence."],
        units={"reported_axis": "signed −1 to 1", "physiology_axis": "signed −1 to 1",
               "objective_minus_subjective": "signed coordinate difference",
               "eeg_robust_z": "robust standard units", "heart_rate_robust_z": "robust standard units"})

    density = _density_rows(trials)
    complete = [row for row in trials if row["construction"]["cohort"] == "complete_fusion"]
    output["B8"] = product("B8", question="How do physiology-derived, reported and fused coordinates differ?",
        takeaway=(f"Matched physiology-derived, reported and fused positions use "
                  f"{sum(row['experiment'] == 2 for row in complete)} E2 and "
                  f"{sum(row['experiment'] == 3 for row in complete)} E3 complete-fusion trials."),
        method="For each experiment and component, Gaussian KDE on a 21×21 fixed signed plane; observed points and mean origin-to-centroid target vectors retained in separate row kinds.",
        rows=density, x="valence", y="arousal", series="density", facet="component",
        chart_type="heatmap", x_label="Signed valence", y_label="Signed arousal",
        sample=counts(complete), source=source,
        caveats=["Density smooths dependent pilot observations and is not a population distribution.",
                 "Only complete-fusion trials enter a matched three-component comparison.",
                 "Rows have kind density_grid, source_position or target_vector; experiment is always retained."],
        units={"valence": "signed −1 to 1", "arousal": "signed −1 to 1",
               "density": "relative density"})
    return output
