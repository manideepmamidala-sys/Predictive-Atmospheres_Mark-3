"""Small versioned FastAPI surface over trusted pre-fitted local artifacts."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware

from pa.api.errors import install_error_handlers
from pa.api.schemas import (
    ErrorResponse,
    HealthResponse,
    MetaResponse,
    OptimizeCandidate,
    OptimizeRequest,
    OptimizeResponse,
    PredictRequest,
    PredictResponse,
)
from pa.config import ROOT, SCHEMA_VERSION
from pa.features.support import load_studied_support
from pa.modeling.artifact import ArtifactUnavailable, LoadedArtifact, load_artifact, source_hash
from pa.modeling.predict import predict_room
from pa.optimize.search import search


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        app.state.artifact = load_artifact()
        app.state.reason = None
    except ArtifactUnavailable as exc:
        app.state.artifact = None
        app.state.reason = str(exc)
    app.state.support = load_studied_support()
    yield


app = FastAPI(title="Predictive Atmospheres Research API", version="1.0.0", lifespan=lifespan)
origins = [origin.strip() for origin in os.environ.get("PA_CORS_ORIGINS", "http://localhost:5173").split(",")
           if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"],
                   allow_headers=["Content-Type"])
install_error_handlers(app)


def _artifact(request: Request) -> LoadedArtifact:
    artifact = request.app.state.artifact
    if artifact is None:
        raise ArtifactUnavailable(request.app.state.reason or "model artifact unavailable")
    return artifact


@app.get("/v1/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    artifact = request.app.state.artifact
    return HealthResponse(schema_version=SCHEMA_VERSION, status="alive", ready=artifact is not None,
                          model_status=artifact.metadata.get("model_status", "unavailable") if artifact else "unavailable",
                          reason=request.app.state.reason)


@app.get("/v1/meta", response_model=MetaResponse)
def metadata(request: Request) -> MetaResponse:
    artifact = request.app.state.artifact
    meta = artifact.metadata if artifact else {}
    return MetaResponse(schema_version=SCHEMA_VERSION,
                        data_manifest_sha256=source_hash(ROOT / "data/MANIFEST.sha256"),
                        artifact_version=meta.get("artifact_version"),
                        model_status=meta.get("model_status", "unavailable"),
                        ready=artifact is not None,
                        limitations=meta.get("limitations", [request.app.state.reason or "model artifact unavailable"]))


@app.post("/v1/predict", response_model=PredictResponse,
          responses={422: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
async def predict(payload: PredictRequest, request: Request) -> PredictResponse:
    artifact = _artifact(request)
    prediction = await run_in_threadpool(predict_room, artifact, payload.room, payload.target)
    support = request.app.state.support.assess(payload.room)
    return PredictResponse(schema_version=SCHEMA_VERSION, status="ok",
                           model_status=artifact.metadata["model_status"],
                           prediction=asdict(prediction), support=asdict(support),
                           limitations=artifact.metadata.get("limitations", []))


@app.post("/v1/optimize", response_model=OptimizeResponse,
          responses={422: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
async def optimize(payload: OptimizeRequest, request: Request) -> OptimizeResponse:
    artifact = _artifact(request)
    outcome = await run_in_threadpool(search, artifact, request.app.state.support, payload.target,
                                      space_type=payload.space_type, day_or_night=payload.day_or_night,
                                      budget=payload.budget, n_candidates=payload.n_candidates,
                                      seed=payload.seed)
    candidates = [OptimizeCandidate(room=item.room, prediction=asdict(item.prediction),
                                    support=asdict(item.support)) for item in outcome.candidates]
    return OptimizeResponse(schema_version=SCHEMA_VERSION, status=outcome.status,
                            model_status=artifact.metadata["model_status"], candidates=candidates,
                            samples_evaluated=outcome.samples_evaluated, reason=outcome.reason,
                            limitations=artifact.metadata.get("limitations", []))
