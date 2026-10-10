"""Shared strict catalogue envelope for source-computed research figures."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime

from pa.config import ROOT
from pa.results.schemas import CATALOGUE_ROUTES, CatalogueProduct


def provenance(method_version: str, approved_spec_sha256: str) -> dict:
    return {"method_version": method_version,
            "approved_spec_sha256": approved_spec_sha256,
            "source_manifest_sha256": hashlib.sha256(
                (ROOT / "data/MANIFEST.sha256").read_bytes()).hexdigest(),
            "generated_at_utc": datetime.now(UTC).isoformat(timespec="seconds")}


def counts(rows: list[dict], *, id_key: str = "id") -> dict[str, int]:
    return {"trials": len(rows),
            "participants": len({row["participant_id"] for row in rows
                                 if row.get("participant_id") is not None}),
            "rooms": len({row["room_id"] for row in rows if row.get("room_id") is not None})}


def product(identifier: str, *, question: str, takeaway: str, method: str,
            rows: list[dict], x: str, y: str, chart_type: str,
            x_label: str, y_label: str, sample: dict[str, int],
            source: dict, caveats: list[str], units: dict[str, str] | None = None,
            series: str | None = None, facet: str | None = None,
            availability_reason: str | None = None,
            methods_evidence: dict | None = None) -> CatalogueProduct:
    if identifier not in CATALOGUE_ROUTES:
        raise ValueError(f"unsupported product ID {identifier}")
    output = {"schema_version": "1.0.0", "id": identifier,
              "route": CATALOGUE_ROUTES[identifier],
              "status": "available" if rows and not availability_reason else "unavailable",
              "question": question, "takeaway": takeaway, "method": method,
              "caveats": caveats, "counts": sample, "units": units or {},
              "provenance": provenance(source["method_version"],
                                       source["approved_spec_sha256"]),
              "availability_reason": availability_reason or (
                  "No eligible source observations for this prespecified analysis."
                  if not rows else None),
              "chart": {"type": chart_type, "rows": rows, "x": x, "y": y,
                        "series": series, "facet": facet, "x_label": x_label,
                        "y_label": y_label, "x_unit": (units or {}).get(x),
                        "y_unit": (units or {}).get(y)}}
    if methods_evidence is not None:
        output["methods_evidence"] = methods_evidence
    return CatalogueProduct.model_validate(output)
