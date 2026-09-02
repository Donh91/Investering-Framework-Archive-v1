from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from forecast_ratification_contract import (  # noqa: E402
    SOURCE_FRESHNESS_CONTRACT_V1,
    SOURCE_FRESHNESS_CUTOVER_COMMIT_SHA,
    SOURCE_OUTPUT_MAX_AGE_MINUTES,
    iso,
)

TARGET_MODES = {"PCT_MOVE", "ABSOLUTE_VALUE", "ABSOLUTE_RANGE"}
LEGACY_TARGET_UNIT_REASON = "LEGACY_V1_TARGET_UNIT_AMBIGUOUS"
UTC = timezone.utc


def canon(v):
    return (json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(v) -> str:
    return hashlib.sha256(canon(v)).hexdigest()


def load_json(path: Path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def existing_candidate_ids(pending_root: Path) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    if not pending_root.exists():
        return found
    for path in sorted(pending_root.rglob("*.json")):
        row = load_json(path)
        if not isinstance(row, dict):
            continue
        candidate_id = str(row.get("candidate_id") or "").strip()
        if not candidate_id:
            continue
        found.setdefault(candidate_id, []).append(str(path))
    return found


def is_legacy_target_unit_ambiguous(candidate: dict) -> bool:
    return candidate.get("target_mode") is None and "threshold" in candidate


def receipt_created_at(receipt: dict) -> datetime:
    raw = receipt.get("created_unix")
    if not isinstance(raw, (int, float)) or isinstance(raw, bool):
        raise ValueError("SOURCE_RECEIPT_CREATED_UNIX_REQUIRED")
    return datetime.fromtimestamp(float(raw), tz=UTC)


def materialize_forecast_candidates(out: dict, receipt: dict, pending_root: Path, now: datetime | None = None) -> dict:
    now = (now or datetime.now(UTC)).astimezone(UTC)
    existing = existing_candidate_ids(pending_root)
    created: list[str] = []
    already_present: list[str] = []
    legacy_censored: list[dict] = []
    source_temporal_censored: list[dict] = []

    source_at: datetime | None = None
    source_age_seconds: float | None = None
    source_error: str | None = None
    try:
        source_at = receipt_created_at(receipt)
        source_age_seconds = (now - source_at).total_seconds()
        if source_age_seconds < 0:
            source_error = "SOURCE_OUTPUT_TIMESTAMP_AFTER_MATERIALIZATION"
        elif source_age_seconds > SOURCE_OUTPUT_MAX_AGE_MINUTES * 60:
            source_error = "SOURCE_OUTPUT_STALE_AT_CANDIDATE_MATERIALIZATION"
    except Exception as exc:
        source_error = str(exc)

    for i, candidate in enumerate(out.get("forecast_candidates", []), 1):
        if candidate.get("target_mode") not in TARGET_MODES:
            if is_legacy_target_unit_ambiguous(candidate):
                legacy_censored.append({
                    "index": i,
                    "metric_path": candidate.get("metric_path"),
                    "direction": candidate.get("direction"),
                    "reason": LEGACY_TARGET_UNIT_REASON,
                })
                continue
            raise SystemExit("FORECAST_CANDIDATE_TARGET_MODE_REQUIRED")

        candidate_id = hashlib.sha256(
            canon({"receipt": receipt.get("output_hash"), "index": i, "candidate": candidate})
        ).hexdigest()[:24]
        if candidate_id in existing:
            already_present.append(candidate_id)
            continue

        if source_error is not None or source_at is None or source_age_seconds is None:
            source_temporal_censored.append({
                "candidate_id": candidate_id,
                "index": i,
                "metric_path": candidate.get("metric_path"),
                "direction": candidate.get("direction"),
                "reason": source_error or "SOURCE_TEMPORAL_PROVENANCE_UNAVAILABLE",
                "source_output_max_age_minutes": SOURCE_OUTPUT_MAX_AGE_MINUTES,
            })
            continue

        material = {
            "contract": "FORECAST_CANDIDATE_v1",
            "authority": "UNRATIFIED_RESEARCH_ONLY",
            "candidate_id": candidate_id,
            "created_at_utc": iso(now),
            "model": receipt.get("model"),
            "task": receipt.get("task"),
            "prompt_sha256": receipt.get("prompt_hash"),
            "context_sha256": receipt.get("context_hash"),
            "source_output_sha256": receipt.get("output_hash"),
            "source_receipt_sha256": digest(receipt),
            "source_freshness_contract": SOURCE_FRESHNESS_CONTRACT_V1,
            "source_freshness_cutover_commit_sha": SOURCE_FRESHNESS_CUTOVER_COMMIT_SHA,
            "source_output_created_at_utc": iso(source_at),
            "source_output_age_at_materialization_seconds": source_age_seconds,
            "source_output_max_age_minutes": SOURCE_OUTPUT_MAX_AGE_MINUTES,
            "candidate": candidate,
            "ratification_status": "PENDING",
            "self_promotion_allowed": False,
        }
        path = pending_root / f"{now:%Y/%m/%d}" / f"{candidate_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = canon(material)
        path.write_bytes(payload)
        if path.read_bytes() != payload:
            raise RuntimeError("forecast_candidate_readback_mismatch")
        existing[candidate_id] = [str(path)]
        created.append(str(path))

    return {
        "status": "PASS",
        "candidate_count": len(created),
        "created_count": len(created),
        "existing_candidate_count": len(already_present),
        "existing_candidate_ids": sorted(already_present),
        "legacy_censored_count": len(legacy_censored),
        "legacy_censored": legacy_censored,
        "source_temporal_censored_count": len(source_temporal_censored),
        "source_temporal_censored": source_temporal_censored,
        "source_output_max_age_minutes": SOURCE_OUTPUT_MAX_AGE_MINUTES,
        "source_freshness_cutover_commit_sha": SOURCE_FRESHNESS_CUTOVER_COMMIT_SHA,
        "legacy_rewrite_performed": False,
        "legacy_rescore_performed": False,
        "paths": created,
        "idempotent_across_pending_tree": True,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--pending-root", type=Path, required=True)
    a = ap.parse_args()
    out = json.loads(a.output.read_text())
    receipt = json.loads(a.receipt.read_text())
    print(json.dumps(materialize_forecast_candidates(out, receipt, a.pending_root), sort_keys=True))


if __name__ == "__main__":
    main()
