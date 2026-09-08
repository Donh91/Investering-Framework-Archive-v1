#!/usr/bin/env python3
"""Forward-only graduation monitor for the native zero-manual-feed chain.

A cycle counts only when Native Handlekompas itself was started by workflow_run,
completed successfully, materialized a valid hash-bound pointer, and consumed the
latest Auto Market State with zero manual input. Duplicate source packets do not
advance the streak. Invalid natural cycles reset the consecutive streak.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "ZERO_MANUAL_FEED_GRADUATION_STATE_v1"
TARGET_STREAK = 3
DEFAULT_STATE = Path("02_DATA_PING/operational_handoffs/zero_manual_feed_graduation/STATE.json")
HANDLE_POINTER = Path("04_MARKET_LEARNING/handlekompas/LATEST.json")
AUTO_POINTER = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"json_object_required:{path}")
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def initial_state() -> dict[str, Any]:
    return {
        "contract": CONTRACT,
        "target_consecutive_natural_cycles": TARGET_STREAK,
        "consecutive_valid_natural_cycles": 0,
        "last_counted_source_packet_sha256": None,
        "last_upstream_run_id": None,
        "last_evaluated_at_utc": None,
        "last_cycle_status": "NOT_YET_OBSERVED",
        "graduated": False,
        "history": [],
        "authority": {
            "portfolio_execution": False,
            "market_threshold_change": False,
            "canonical_market_state_change": False,
            "owner_switch": False,
            "purpose": "OPERATIONAL_GRADUATION_EVIDENCE_ONLY",
        },
    }


def validate_cycle(repo: Path) -> tuple[bool, str, str | None]:
    hp = repo / HANDLE_POINTER
    ap = repo / AUTO_POINTER
    if not hp.exists():
        return False, "HANDLEKOMPAS_POINTER_MISSING", None
    if not ap.exists():
        return False, "AUTO_MARKET_STATE_POINTER_MISSING", None
    handle_pointer = read_json(hp)
    auto_pointer = read_json(ap)
    handle_path = handle_pointer.get("handlekompas_path")
    auto_path = auto_pointer.get("packet_path")
    if not isinstance(handle_path, str) or not isinstance(auto_path, str):
        return False, "POINTER_TARGET_MISSING", None
    handle = read_json(repo / handle_path)
    auto = read_json(repo / auto_path)
    source_sha = handle.get("source", {}).get("packet_sha256") if isinstance(handle.get("source"), dict) else None
    if not isinstance(source_sha, str) or not source_sha:
        return False, "HANDLEKOMPAS_SOURCE_SHA_MISSING", None
    if handle_pointer.get("source_packet_sha256") != source_sha:
        return False, "HANDLEKOMPAS_POINTER_SOURCE_SHA_MISMATCH", source_sha
    if auto_pointer.get("packet_sha256") != auto.get("packet_sha256"):
        return False, "AUTO_MARKET_STATE_POINTER_HASH_MISMATCH", source_sha
    if source_sha != auto_pointer.get("packet_sha256"):
        return False, "HANDLEKOMPAS_NOT_BOUND_TO_LATEST_AUTO_STATE", source_sha
    if handle.get("manual_market_data_required") is not False:
        return False, "HANDLEKOMPAS_MANUAL_DATA_REQUIRED", source_sha
    if float(auto.get("manual_input_residual_pct", 100.0)) != 0.0:
        return False, "AUTO_STATE_MANUAL_INPUT_RESIDUAL_NONZERO", source_sha
    authority = handle.get("authority") if isinstance(handle.get("authority"), dict) else {}
    if authority.get("portfolio_execution") is not False or authority.get("market_threshold_change") is not False:
        return False, "HANDLEKOMPAS_AUTHORITY_BOUNDARY_INVALID", source_sha
    return True, "VALID_NATURAL_CYCLE", source_sha


def evaluate(repo: Path, state_path: Path, *, upstream_event: str, upstream_conclusion: str, upstream_run_id: str) -> dict[str, Any]:
    path = repo / state_path
    state = read_json(path) if path.exists() else initial_state()
    now = utc_now()
    natural = upstream_event == "workflow_run"
    success = upstream_conclusion == "success"
    valid = False
    reason = "NON_NATURAL_HANDLEKOMPAS_TRIGGER"
    source_sha: str | None = None
    if natural and success:
        valid, reason, source_sha = validate_cycle(repo)
    elif natural and not success:
        reason = "NATURAL_HANDLEKOMPAS_RUN_NOT_SUCCESSFUL"

    previous_sha = state.get("last_counted_source_packet_sha256")
    duplicate = bool(valid and source_sha == previous_sha)
    if natural:
        if valid and not duplicate:
            state["consecutive_valid_natural_cycles"] = int(state.get("consecutive_valid_natural_cycles", 0)) + 1
            state["last_counted_source_packet_sha256"] = source_sha
            cycle_status = "COUNTED"
        elif valid and duplicate:
            cycle_status = "DUPLICATE_SOURCE_NOT_COUNTED"
        else:
            state["consecutive_valid_natural_cycles"] = 0
            cycle_status = "RESET_INVALID_NATURAL_CYCLE"
    else:
        cycle_status = "IGNORED_NON_NATURAL_TRIGGER"

    streak = int(state.get("consecutive_valid_natural_cycles", 0))
    state["graduated"] = streak >= int(state.get("target_consecutive_natural_cycles", TARGET_STREAK))
    state["last_upstream_run_id"] = str(upstream_run_id)
    state["last_evaluated_at_utc"] = now
    state["last_cycle_status"] = cycle_status
    history = list(state.get("history") or [])
    history.append({
        "evaluated_at_utc": now,
        "upstream_run_id": str(upstream_run_id),
        "upstream_event": upstream_event,
        "upstream_conclusion": upstream_conclusion,
        "source_packet_sha256": source_sha,
        "valid": valid,
        "reason": "DUPLICATE_SOURCE_PACKET" if duplicate else reason,
        "cycle_status": cycle_status,
        "streak_after": streak,
    })
    state["history"] = history[-12:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    return state


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--state-path", type=Path, default=DEFAULT_STATE)
    ap.add_argument("--upstream-event", required=True)
    ap.add_argument("--upstream-conclusion", required=True)
    ap.add_argument("--upstream-run-id", required=True)
    args = ap.parse_args()
    state = evaluate(args.repo_root, args.state_path, upstream_event=args.upstream_event, upstream_conclusion=args.upstream_conclusion, upstream_run_id=args.upstream_run_id)
    print(json.dumps({
        "status": state["last_cycle_status"],
        "streak": state["consecutive_valid_natural_cycles"],
        "target": state["target_consecutive_natural_cycles"],
        "graduated": state["graduated"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
