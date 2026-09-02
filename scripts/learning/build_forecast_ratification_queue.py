#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from forecast_candidate_grouping import classified_candidate_groups_with_quarantine  # noqa: E402
from forecast_ratification_contract import (  # noqa: E402
    CUTOVER_COMMIT_SHA,
    DECISION_SLA_MINUTES,
    RATIFICATION_QUEUE_V1,
    RATIFICATION_TERMINAL_V1,
    SOURCE_FRESHNESS_CUTOVER_COMMIT_SHA,
    SOURCE_OUTPUT_MAX_AGE_MINUTES,
    decision_deadline,
    iso,
    parse_dt,
    validate_source_temporal_provenance,
)

UTC = timezone.utc


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def terminal_ids(root: Path) -> set[str]:
    result: set[str] = set()
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        try:
            value = read(path)
        except Exception:
            continue
        if value.get("contract") != RATIFICATION_TERMINAL_V1:
            continue
        cid = str(value.get("candidate_id") or "")
        if cid:
            result.add(cid)
    return result


def build_queue(pending_root: Path, terminal_root: Path, now: datetime) -> dict[str, Any]:
    groups, grouping_quarantines = classified_candidate_groups_with_quarantine(pending_root)
    terminal = terminal_ids(terminal_root)
    rows: list[dict[str, Any]] = []
    quarantines = list(grouping_quarantines)
    counts = {
        "distinct_candidate_ids": len(groups),
        "terminal_candidates": 0,
        "legacy_pre_cutover": 0,
        "legacy_identical_duplicate_ids": 0,
        "legacy_divergent_duplicate_ids": 0,
        "quarantined_candidate_ids": len({str(row.get("candidate_id") or "") for row in grouping_quarantines if row.get("candidate_id")}),
        "post_cutover_duplicate_quarantine_ids": len({str(row.get("candidate_id")) for row in grouping_quarantines if str(row.get("error") or "").startswith("POST_CUTOVER_DUPLICATE_CANDIDATE_ID")}),
        "source_temporal_quarantine_ids": 0,
        "expired_without_terminal": 0,
        "decision_required": 0,
    }

    for cid, group in sorted(groups.items()):
        if cid in terminal:
            counts["terminal_candidates"] += 1
            continue
        classification = group["classification"]
        if classification.startswith("LEGACY_PRE_CUTOVER"):
            counts["legacy_pre_cutover"] += 1
            if classification == "LEGACY_PRE_CUTOVER_IDENTICAL_DUPLICATE":
                counts["legacy_identical_duplicate_ids"] += 1
            elif classification == "LEGACY_PRE_CUTOVER_DIVERGENT_DUPLICATE":
                counts["legacy_divergent_duplicate_ids"] += 1
            continue

        candidate = group["candidate"]
        try:
            validate_source_temporal_provenance(candidate)
        except Exception as exc:
            counts["source_temporal_quarantine_ids"] += 1
            quarantines.append({
                "candidate_id": cid,
                "paths": [path.as_posix() for path in group["paths"]],
                "error": f"SOURCE_TEMPORAL_PROVENANCE:{exc}",
            })
            continue

        created = parse_dt(str(candidate["created_at_utc"]))
        deadline = decision_deadline(str(candidate["created_at_utc"]))
        if now > deadline:
            counts["expired_without_terminal"] += 1
            continue
        payload = candidate.get("candidate") or {}
        rows.append({
            "candidate_id": cid,
            "candidate_sha256": digest(candidate),
            "created_at_utc": iso(created),
            "decision_deadline_utc": iso(deadline),
            "candidate_paths": [path.as_posix() for path in group["paths"]],
            "candidate_group_classification": classification,
            "model": candidate.get("model"),
            "task": candidate.get("task"),
            "source_output_created_at_utc": candidate.get("source_output_created_at_utc"),
            "source_output_age_at_materialization_seconds": candidate.get("source_output_age_at_materialization_seconds"),
            "source_output_max_age_minutes": candidate.get("source_output_max_age_minutes"),
            "source_receipt_sha256": candidate.get("source_receipt_sha256"),
            "metric_path": payload.get("metric_path"),
            "direction": payload.get("direction"),
            "target_mode": payload.get("target_mode"),
            "threshold_pct": payload.get("threshold_pct"),
            "target_value": payload.get("target_value"),
            "range_low": payload.get("range_low"),
            "range_high": payload.get("range_high"),
            "horizon_days": payload.get("horizon_days"),
            "rationale": payload.get("rationale"),
            "decision_options": ["RATIFY", "REJECT"],
            "outcome_data_included": False,
        })
    counts["decision_required"] = len(rows)
    counts["quarantined_candidate_ids"] = len({str(row.get("candidate_id") or "") for row in quarantines if row.get("candidate_id")})
    return {
        "contract": RATIFICATION_QUEUE_V1,
        "generated_at_utc": iso(now),
        "prospective_cutover_commit_sha": CUTOVER_COMMIT_SHA,
        "source_freshness_cutover_commit_sha": SOURCE_FRESHNESS_CUTOVER_COMMIT_SHA,
        "decision_sla_minutes": DECISION_SLA_MINUTES,
        "source_output_max_age_minutes": SOURCE_OUTPUT_MAX_AGE_MINUTES,
        "outcome_data_included": False,
        "outcome_paths_read": [],
        "self_promotion_allowed": False,
        "legacy_duplicate_policy": "PRE_CUTOVER_MULTI_PATH_IDS_ARE_ARCHIVE_ONLY_POST_CUTOVER_MULTI_PATH_IDS_ARE_QUARANTINED_AND_NEVER_OWNER_VISIBLE",
        "quarantine_policy": "STRUCTURALLY_INVALID_POST_CUTOVER_DUPLICATE_OR_SOURCE_TEMPORALLY_INVALID_IDS_ARE_EXCLUDED_FROM_OWNER_QUEUE_WITHOUT_BLOCKING_OTHER_CANDIDATES",
        "source_temporal_policy": "POST_SOURCE_FRESHNESS_CUTOVER_OWNER_QUEUE_REQUIRES_RECEIPT_TIME_RECEIPT_HASH_AND_BOUND_SOURCE_AGE",
        "counts": counts,
        "quarantines": [{
            "candidate_id": row.get("candidate_id"),
            "error": row.get("error"),
            "paths": row.get("paths") or ([row.get("path")] if row.get("path") else []),
            "owner_decision_allowed": False,
        } for row in quarantines],
        "candidates": rows,
        "authority": {
            "portfolio_action": False,
            "framework_state_change": False,
            "model_weight_change": False,
            "canonical_promotion": False,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pending-root", type=Path, required=True)
    ap.add_argument("--terminal-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--now-utc")
    args = ap.parse_args()
    now = parse_dt(args.now_utc) if args.now_utc else datetime.now(UTC)
    queue = build_queue(args.pending_root, args.terminal_root, now)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canon(queue))
    print(json.dumps({"status": "PASS", **queue["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
