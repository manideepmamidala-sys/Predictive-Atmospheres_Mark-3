"""Local research commands. Processing commands are explicit, never import side effects."""

from __future__ import annotations

import json
from dataclasses import asdict

import typer

from pa.affect.analysis import write_analysis
from pa.affect.run import write_affect
from pa.config import RESULTS
from pa.features.schema import RoomInput
from pa.features.support import load_studied_support
from pa.io.audit import write_audit
from pa.io.manifest import verify_sources
from pa.modeling.artifact import ArtifactUnavailable, load_artifact
from pa.modeling.predict import predict_room
from pa.modeling.train import write_model_evaluation
from pa.optimize.search import search
from pa.results.build import write_research_exports
from pa.results.review import write_review_panels
from pa.scoring.neuro_score import AffectPoint
from pa.signals.run import write_signals

app = typer.Typer(no_args_is_help=True)


@app.callback()
def main() -> None:
    """Predictive Atmospheres research commands."""


@app.command("verify-data")
def verify_data() -> None:
    """Check inventoried source evidence against immutable recorded hashes."""
    errors = verify_sources()
    if errors:
        for issue in errors:
            typer.echo(f"{issue.path}: {issue.reason}", err=True)
        raise typer.Exit(code=1)
    typer.echo("Source inventory verified")


@app.command()
def audit() -> None:
    """Export observed acquisition inventory and conditional rate scenarios."""
    result = write_audit()
    typer.echo(f"Audited {result['summary']['recordings']} recordings")


@app.command()
def signals() -> None:
    """Process original recordings after the independent scientific checkpoint passes."""
    try:
        result = write_signals()
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Processed {len(result['trials'])} conditional-rate trials")


@app.command()
def affect() -> None:
    """Construct explicit descriptive affect cohorts from gated signal evidence."""
    try:
        result = write_affect()
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Constructed affect availability for {len(result['trials'])} trials")


@app.command()
def analyze() -> None:
    """Export crossed-design descriptive analyses without trial-iid inference."""
    try:
        result = write_analysis()
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Analyzed {sum(row['trials'] for row in result['experiments'])} trials")


@app.command()
def train() -> None:
    """Run untouched grouped evaluation, then independently fit the full-data artifact."""
    try:
        result = write_model_evaluation()
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Model status: {result['status']}; eligible trials: {result['cohort']['rows']}")


@app.command()
def export() -> None:
    """Validate and write six public research products and their browser bundle."""
    try:
        manifest = write_research_exports()
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Exported {len(manifest['products'])} validated research files")


@app.command()
def openapi() -> None:
    """Write generated API and shared physical-input contracts."""
    from pa.api.app import app as api_app

    destination = RESULTS / "openapi.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(api_app.openapi(), indent=2, sort_keys=True) + "\n")
    (RESULTS / "room-input.schema.json").write_text(
        json.dumps(RoomInput.model_json_schema(), indent=2, sort_keys=True) + "\n")
    typer.echo("Generated versioned OpenAPI and room-input contracts")


@app.command()
def pipeline() -> None:
    """Regenerate audited evidence, scientific products, artifact and contracts."""
    verify_data()
    audit()
    signals()
    signal_review()
    affect()
    analyze()
    train()
    export()
    openapi()


@app.command("signal-review")
def signal_review() -> None:
    """Render deterministic representative raw/cleaned/QC plots for manual inspection."""
    try:
        panels = write_review_panels()
    except (RuntimeError, FileNotFoundError, ValueError) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"Rendered {len(panels)} representative signal review panels")


@app.command()
def predict(room_json: str, target_valence: float, target_arousal: float) -> None:
    """Predict from a trusted fitted artifact and independent room JSON."""
    try:
        room = RoomInput.model_validate_json(room_json)
        target = AffectPoint(valence=target_valence, arousal=target_arousal)
        artifact = load_artifact()
        result = predict_room(artifact, room, target)
    except (ValueError, ArtifactUnavailable) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps({"model_status": artifact.metadata["model_status"],
                           "prediction": asdict(result)}, allow_nan=False))


@app.command()
def optimize(target_valence: float, target_arousal: float,
             budget: int | None = None, n_candidates: int | None = None,
             seed: int | None = None, space_type: str | None = None,
             day_or_night: str | None = None) -> None:
    """Search declared room support from the trusted model and a user target."""
    try:
        target = AffectPoint(valence=target_valence, arousal=target_arousal)
        artifact = load_artifact()
        outcome = search(artifact, load_studied_support(), target, space_type=space_type,
                         day_or_night=day_or_night, budget=budget,
                         n_candidates=n_candidates, seed=seed)
    except (ValueError, ArtifactUnavailable) as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(json.dumps({"model_status": artifact.metadata["model_status"],
                           "status": outcome.status,
                           "samples_evaluated": outcome.samples_evaluated,
                           "reason": outcome.reason,
                           "candidates": [{"room": item.room.model_dump(mode="json"),
                                           "prediction": asdict(item.prediction),
                                           "support": asdict(item.support)}
                                          for item in outcome.candidates]}, allow_nan=False))


if __name__ == "__main__":
    app()
