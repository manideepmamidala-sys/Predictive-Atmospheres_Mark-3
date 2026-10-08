"""Structured public errors without raw tracebacks."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from pa.modeling.artifact import ArtifactUnavailable


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def invalid_request(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [{"loc": [str(part) for part in error["loc"]], "message": error["msg"]}
                   for error in exc.errors()]
        return JSONResponse(status_code=422, content={"error": {
            "code": "invalid_request", "message": "Request validation failed", "details": details,
        }})

    @app.exception_handler(ArtifactUnavailable)
    async def unavailable(_: Request, exc: ArtifactUnavailable) -> JSONResponse:
        return JSONResponse(status_code=503, content={"error": {
            "code": "model_unavailable", "message": str(exc), "details": None,
        }})

    @app.exception_handler(ValueError)
    async def invalid_value(_: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"error": {
            "code": "invalid_value", "message": str(exc), "details": None,
        }})
