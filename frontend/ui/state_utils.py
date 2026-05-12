# Utility functions for Streamlit UI state handling

"""State utilities for extracting independent spatial features from
Streamlit's ``st.session_state``.

These helpers centralise the logic that collects only INDEPENDENT features.
Derived features (ratios, areas, volumes) are computed by the backend
in ``src.models.train._build_features`` and ``src.services.prediction_service``.

UDI, sDA, and ASE are permanently purged and never collected.
"""

from __future__ import annotations

from typing import Dict
import streamlit as st
from src.config import get_config


def get_current_features_from_state(config) -> Dict[str, float]:
    """Collect independent spatial features from ``st.session_state``.

    Derived features (L:W Ratio, Floor Area, Wall Area, Volume,
    Door/Wall Ratio, Window/Wall Ratio, Walkable/Floor Ratio) are
    NOT included — the backend computes them.
    """
    features: Dict[str, float] = {}

    # Core geometry
    features["Length_m"] = float(st.session_state.get("L", config.room.default_length))
    features["Width_m"] = float(st.session_state.get("W", config.room.default_width))
    features["Height_m"] = float(st.session_state.get("H", config.room.default_height))

    # Openings (independent only)
    features["Num_Doors"] = float(st.session_state.get("num_doors", 1.0))
    features["Door_Area_m2"] = float(st.session_state.get("door_area", 1.8))
    features["Num_Windows"] = float(st.session_state.get("num_windows", 2.0))
    features["Window_Area_m2"] = float(st.session_state.get("window_area", 5.0))

    # Daylight (UDI, sDA, ASE permanently purged)
    features["Daylight_Factor_pct"] = float(st.session_state.get("daylight_factor", 2.0))
    features["Illuminance_lux"] = float(st.session_state.get("illuminance", 300.0))
    features["CCT_K"] = float(st.session_state.get("cct", 4000.0))

    # Walkable Floor Area
    features["Walkable_Floor_Area_m2"] = float(st.session_state.get("walkable_floor", 60.0))

    # Experiment condition (Day/Night) – one-hot encoded
    is_day = st.session_state.get("is_day", True)
    feature_names = st.session_state.get("feature_names", [])
    for name in feature_names:
        if name.startswith("Day_or_Night_"):
            if name == "Day_or_Night_Day":
                features[name] = 1.0 if is_day else 0.0
            elif name == "Day_or_Night_Night":
                features[name] = 0.0 if is_day else 1.0
            else:
                features[name] = 0.0

    # Type of Space – one-hot encoded
    selected_space = st.session_state.get("space_type", "Living Room")
    for name in feature_names:
        if name.startswith("Type_of_Space_"):
            space_label = name.replace("Type_of_Space_", "")
            features[name] = 1.0 if space_label == selected_space else 0.0

    return features
