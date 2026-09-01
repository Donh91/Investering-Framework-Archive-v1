#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CONTRACT = "POLYMARKET_EXPECTATIONS_OFFLINE_PARSER_v0_2"
AUTHORITY = {
    "binding": False,
    "canonical_acceptance": False,
    "state_change": False,
    "portfolio_action": False,
    "automatic_promotion": False,
}
NETWORK_COLLECTION = "DISABLED_UNTIL_DURABLE_STORAGE_AND_DERIVED_USE_CONTRACT_IS_EXPLICIT"
RESEARCH_ACCESS = "OFFICIAL_OPEN_APIS_DOCUMENTED_FOR_RESEARCH"


class ProbeError(ValueError):
    pass


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _point(row: Any) -> tuple[float, float] | None:
    if not isinstance(row, dict):
        return None
    timestamp = row.get("t", row.get("timestamp"))
    price = row.get("p", row.get("price"))
    try:
        return float(timestamp), float(price)
    except (TypeError, ValueError):
        return None


def summarize_prices_history(raw: bytes) -> dict[str, Any]:
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProbeError("invalid_json") from exc
    rows = doc.get("history") if isinstance(doc, dict) else doc
    if not isinstance(rows, list):
        raise ProbeError("history_not_list")
    points = [point for row in rows if (point := _point(row)) is not None]
    if not points:
        raise ProbeError("no_valid_history_points")
    points.sort(key=lambda item: item[0])
    probabilities = [value for _, value in points]
    if any(value < 0 or value > 1 for value in probabilities):
        raise ProbeError("probability_out_of_range")
    return {
        "contract": CONTRACT,
        "source": "POLYMARKET",
        "research_access": RESEARCH_ACCESS,
        "network_collection": NETWORK_COLLECTION,
        "payload_sha256": sha256(raw),
        "payload_bytes": len(raw),
        "row_count": len(points),
        "earliest_timestamp": points[0][0],
        "latest_timestamp": points[-1][0],
        "min_probability": min(probabilities),
        "max_probability": max(probabilities),
        "raw_persisted": False,
        "authority": AUTHORITY,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline-only Polymarket history parser.")
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    raw = args.input.read_bytes()
    print(json.dumps(summarize_prices_history(raw), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
