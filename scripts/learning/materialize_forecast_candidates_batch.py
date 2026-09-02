#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "api_agent"))
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from materialize_forecast_candidates import materialize_forecast_candidates  # noqa: E402
from forecast_ratification_contract import iso  # noqa: E402

UTC = timezone.utc
CENSUS_CONTRACT = "FORECAST_MATERIALIZATION_CENSUS_v1"

AUTHORITY = {
    "creates_truth": False,
    "portfolio_action": False,
    "framework_state_change": False,
    "model_weight_change": False,
    "canonical_promotion": False,
    "forecast_skill_authority": False,
}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(value: Any) -> str:
    return digest_bytes(canon(value))


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def reason_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(row.get("reason") or "UNKNOWN") for row in rows)
    return dict(sorted(counts.items()))


def run_batch(
    outputs_root: Path,
    pending_root: Path,
    census_output: Path,
    *,
    now: datetime | None = None,
) -> dict[str, Any]:
    now = (now or datetime.now(UTC)).astimezone(UTC)
    source_rows: list[dict[str, Any]] = []
    totals = {
        "source_output_count": 0,
        "paired_source_count": 0,
        "missing_receipt_count": 0,
        "created_candidate_count": 0,
        "existing_candidate_count": 0,
        "legacy_censored_candidate_count": 0,
        "source_temporal_censored_candidate_count": 0,
    }

    for output_path in sorted(outputs_root.rglob("DAILY_DIRECTOR_OUTPUT.json")) if outputs_root.exists() else []:
        totals["source_output_count"] += 1
        receipt_path = output_path.with_name("DAILY_DIRECTOR_RECEIPT.json")
        output_bytes = output_path.read_bytes()
        row: dict[str, Any] = {
            "output_path": output_path.as_posix(),
            "output_file_sha256": digest_bytes(output_bytes),
            "receipt_path": receipt_path.as_posix(),
            "receipt_file_sha256": None,
            "source_output_sha256": None,
            "source_receipt_created_unix": None,
            "materialization_status": None,
            "created_count": 0,
            "existing_candidate_count": 0,
            "legacy_censored_count": 0,
            "legacy_censored_reason_counts": {},
            "source_temporal_censored_count": 0,
            "source_temporal_censored_reason_counts": {},
            "created_paths": [],
        }
        if not receipt_path.exists():
            totals["missing_receipt_count"] += 1
            row["materialization_status"] = "SOURCE_RECEIPT_MISSING"
            source_rows.append(row)
            continue

        receipt_bytes = receipt_path.read_bytes()
        row["receipt_file_sha256"] = digest_bytes(receipt_bytes)
        output = json.loads(output_bytes)
        receipt = json.loads(receipt_bytes)
        row["source_output_sha256"] = receipt.get("output_hash")
        row["source_receipt_created_unix"] = receipt.get("created_unix")
        result = materialize_forecast_candidates(output, receipt, pending_root, now)
        totals["paired_source_count"] += 1
        totals["created_candidate_count"] += int(result.get("created_count") or 0)
        totals["existing_candidate_count"] += int(result.get("existing_candidate_count") or 0)
        totals["legacy_censored_candidate_count"] += int(result.get("legacy_censored_count") or 0)
        totals["source_temporal_censored_candidate_count"] += int(result.get("source_temporal_censored_count") or 0)
        row.update({
            "materialization_status": result.get("status"),
            "created_count": int(result.get("created_count") or 0),
            "existing_candidate_count": int(result.get("existing_candidate_count") or 0),
            "legacy_censored_count": int(result.get("legacy_censored_count") or 0),
            "legacy_censored_reason_counts": reason_counts(result.get("legacy_censored") or []),
            "source_temporal_censored_count": int(result.get("source_temporal_censored_count") or 0),
            "source_temporal_censored_reason_counts": reason_counts(result.get("source_temporal_censored") or []),
            "created_paths": list(result.get("paths") or []),
        })
        source_rows.append(row)

    census: dict[str, Any] = {
        "contract": CENSUS_CONTRACT,
        "generated_at_utc": iso(now),
        "outputs_root": outputs_root.as_posix(),
        "pending_root": pending_root.as_posix(),
        "outcome_data_read": False,
        "historical_forecast_rewrite_performed": False,
        "historical_outcome_rewrite_performed": False,
        "totals": totals,
        "sources": source_rows,
        "authority": AUTHORITY,
    }
    census["census_sha256"] = digest(census)
    census_output.parent.mkdir(parents=True, exist_ok=True)
    payload = canon(census)
    census_output.write_bytes(payload)
    if census_output.read_bytes() != payload:
        raise RuntimeError("FORECAST_MATERIALIZATION_CENSUS_READBACK_MISMATCH")
    return census


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outputs-root", type=Path, required=True)
    ap.add_argument("--pending-root", type=Path, required=True)
    ap.add_argument("--census-output", type=Path, required=True)
    args = ap.parse_args()
    census = run_batch(args.outputs_root, args.pending_root, args.census_output)
    print(json.dumps({"status": "PASS", **census["totals"], "census_sha256": census["census_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
