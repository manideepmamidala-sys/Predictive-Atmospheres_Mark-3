"""
Legacy compatibility module.

This project previously exposed a large monolithic implementation in this file.
Core logic is now maintained in focused modules under `src.data` and `src.services`.

Kept only for backward compatibility with older imports.
"""
from src.data.emotion_engine import process_emotion_engine, calculate_stress_index
from src.data.preprocessing import analyze_eeg_bands

__all__ = [
    'process_emotion_engine',
    'calculate_stress_index',
    'analyze_eeg_bands',
]

