"""Within-person descriptive component calibration; prohibited for held-out targets."""

from __future__ import annotations

import math
from collections import defaultdict

import numpy as np

from pa.modeling.targets import COMPONENTS
from pa.signals.common import decisions


def _transform_raw(name: str, value: float | None) -> float | None:
    if value is None or not math.isfinite(value):
        return None
    if name == "rmssd_ms":
        return math.log(value) if value > 0 else None
    return value


def descriptive_components(rows: list[dict]) -> tuple[list[dict], dict]:
    """Calibrate only observed valid components within each person.

    Output components are tanh robust z scores. The returned diagnostics retain
    uncalibratable components; no zero/neutral fallback is inserted.
    """
    cfg = decisions()["affect"]
    grouped: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["experiment"]), str(row["participant_id"]))].append(row)
    calibrations = {}
    for (experiment, participant), participant_rows in grouped.items():
        key = f"E{experiment}:{participant}"
        calibrations[key] = {}
        for component in (*COMPONENTS, "rmssd_ms"):
            values = [_transform_raw(component, row.get(component)) for row in participant_rows]
            finite = np.asarray([value for value in values if value is not None], dtype=float)
            if len(finite) < cfg["min_descriptive_trials_per_participant"]:
                calibrations[key][component] = {"status": "insufficient_distinct_trials",
                                                "observed": len(finite),
                                                "distinct": len(np.unique(finite))}
                continue
            center = float(np.median(finite))
            scale = float(np.median(np.abs(finite - center)) * cfg["robust_scale_mad_factor"])
            if scale <= 0:
                calibrations[key][component] = {"status": "zero_robust_scale",
                                                "observed": len(finite)}
                continue
            calibrations[key][component] = {"status": "calibrated", "observed": len(finite),
                                            "center": center, "scale": scale}
    output = []
    for row in rows:
        person = f"E{int(row['experiment'])}:{row['participant_id']}"
        components = {}
        for name in (*COMPONENTS, "rmssd_ms"):
            calibration = calibrations[person][name]
            value = _transform_raw(name, row.get(name))
            components[name] = (float(np.tanh((value - calibration["center"]) /
                                               calibration["scale"]))
                                if value is not None and calibration["status"] == "calibrated"
                                else None)
        output.append(components)
    return output, calibrations
