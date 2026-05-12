"""
run_pipeline.py — Execute Phase 1 + Phase 2 of the Predictive Atmospheres backend.

Usage:
    python run_pipeline.py

Outputs:
    data/processed/fusion_analysis.parquet
"""

import logging
import sys
from pathlib import Path

# Ensure the project root is on sys.path so `src` is importable
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("run_pipeline")


def main() -> None:
    logger.info("=" * 60)
    logger.info("PHASE 1 — Multi-Experiment Data Ingestion")
    logger.info("=" * 60)

    from src.data.data_loader import load_and_merge
    merged_df = load_and_merge()

    logger.info("")
    logger.info("Merged DataFrame summary:")
    logger.info("  Rows    : %d", len(merged_df))
    logger.info("  Columns : %d", len(merged_df.columns))
    logger.info("  Columns : %s", list(merged_df.columns))

    logger.info("")
    logger.info("=" * 60)
    logger.info("PHASE 2 — Affective Fusion Target Calculation")
    logger.info("=" * 60)

    from src.data.emotion_engine import run_fusion_pipeline
    fusion_df = run_fusion_pipeline(merged_df)

    logger.info("")
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE — fusion_analysis.parquet summary")
    logger.info("=" * 60)
    logger.info("  Rows    : %d", len(fusion_df))
    logger.info("  Columns (%d):", len(fusion_df.columns))
    for col in fusion_df.columns:
        logger.info("    • %s", col)

    # Verify no NaN in the critical target columns
    target_cols = ["fused_valence", "fused_arousal",
                   "objective_valence", "objective_arousal"]
    logger.info("")
    logger.info("NaN audit on target columns:")
    all_clean = True
    for col in target_cols:
        if col in fusion_df.columns:
            n_nan = fusion_df[col].isna().sum()
            status = "✓ CLEAN" if n_nan == 0 else f"✗ {n_nan} NaN"
            logger.info("  %-30s %s", col, status)
            if n_nan > 0:
                all_clean = False
        else:
            logger.warning("  %-30s MISSING COLUMN", col)
            all_clean = False

    if all_clean:
        logger.info("")
        logger.info("✅  All target columns are NaN-free.  Pipeline verified.")
    else:
        logger.warning("")
        logger.warning("⚠️   Some target columns contain NaN values — review logs above.")

    # Final stdout summary (required by deliverable spec)
    print("\n" + "=" * 60)
    print("DELIVERABLE SUMMARY")
    print("=" * 60)
    print(f"Row count : {len(fusion_df)}")
    print(f"Columns   : {list(fusion_df.columns)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
