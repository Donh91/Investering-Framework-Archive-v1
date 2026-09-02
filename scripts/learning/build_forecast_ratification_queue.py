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

from forecast_ratification_contract import (  # noqa: E402
    CUTOVER_COMMIT_SHA,
    DECISION_SLA_MINUTES,
    RATIFICATION_QUEUE_V1,
    RATIFICATION_TERMINAL_V1,
    decision_deadline,
    is_post_cutover_candidate,
    iso,
    parse_dt,
)

UTC = timezone.utc


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def index_candidates(root: Path) -> dict[str, tuple[dict[str, Any], list[str]]]:
    found: dict[str, tuple[dict[str, Any], list[str]]] = {}
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        value = read(path)
        if value.get("contract") != "FORECAST_CANDIDATE_v1":
            continue
        cid = str(value.get("candidate_id") or "")
        if not cid:
            raise ValueError(f"CANDIDATE_ID_MISSING:{path}")
        if cid not in found:
            found[cid] = (value, [path.as_posix()])
            continue
        existing, paths = found[cid]
        if canon(existing) != canon(value):
            raise ValueError(f"DIVERGENT_DUPLICATE_CANDIDATE:{cid}")
        paths.append(path.as_posix())
    return found


def terminal_ids(root: Path) -> set[str]:
    result: set[str] = set()
    for path in sorted(root.rglob("*.json")) if root.exists() else []:
        value = read(path)
        if value.get("contract") != RATIFICATION_TERMINAL_V1:
            continue
        cid = str(value.get("candidate_id") or "")
        if cid:
            result.add(cid)
    return result


def build_queue(pending_root: Path, terminal_root: Path, now: datetime) -> dict[str, Any]:
    candidates = index_candidates(pending_root)
    terminal = terminal_ids(terminal_root)
    rows: list[dict[str, Any]] = []
    counts = {
        "distinct_candidates": len(candidates),
        "terminal_candidates": 0,
        "legacy_pre_cutover": 0,
        "expired_without_terminal": 0,
        "decision_required": 0,
    }

    for cid, (candidate, paths) in sorted(candidates.items()):
        if cid in terminal:
            counts["terminal_candidates"] += 1
            continue
        if not is_post_cutover_candidate(candidate):
            counts["legacy_pre_cutover"] += 1
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
            "candidate_paths": paths,
            "model": candidate.get("model"),
            "task": candidate.get("task"),
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
    return {
        "contract": RATIFICATION_QUEUE_V1,
        "generated_at_utc": iso(now),
        "prospective_cutover_commit_sha": CUTOVER_COMMIT_SHA,
        "decision_sla_minutes": DECISION_SLA_MINUTES,
        "outcome_data_included": False,
        "outcome_paths_read": [],
        "self_promotion_allowed": False,
        "counts": counts,
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
