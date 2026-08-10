from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PATTERNS = ("SPAR-P1", "SPAR-P2", "SPAR-P3")


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def pattern_counts(report: dict[str, Any] | None) -> dict[str, int]:
    rows = (report or {}).get("patterns", [])
    found = {str(row.get("pattern_id")): int(row.get("matured_72h_count", 0)) for row in rows}
    return {pattern: found.get(pattern, 0) for pattern in PATTERNS}


def all_patterns_at_least(report: dict[str, Any] | None, threshold: int) -> bool:
    counts = pattern_counts(report)
    return all(counts[pattern] >= threshold for pattern in PATTERNS)


def decide(root: Path, queue: dict[str, Any]) -> dict[str, Any]:
    frozen = root / "research/experiments/pdlt_v1_1/discovery/FROZEN_MODEL_v1.json"
    pdlt_methods = root / "research/experiments/pdlt_v1_1/PDLT_METHODS_HARDENING_P2_2026-08-10.json"
    if frozen.exists():
        pdlt_status = "DISCOVERY_FROZEN"
    elif pdlt_methods.exists():
        pdlt_status = "BLOCKED_METHODS_REPAIR_REOPEN_GATES_REQUIRED"
    else:
        pdlt_status = "BLOCKED_SAFE_PAID_RESUME_REQUIRED"

    latest_spar = root / "research/experiments/spar_v1/LATEST_REPORT.json"
    latest_frag = root / "research/experiments/spar_v1/LATEST_FRAGILITY_REPORT.json"
    latest_capture = read_json(root / "03_DAILY_CAPTURE_LOGS/captures/LATEST.json") or {}
    latest_capture_ts = parse_ts(latest_capture.get("captured_at_utc"))
    spar = read_json(latest_spar)
    frag = read_json(latest_frag)

    action = "WAIT"
    reason = "NO_RUNNABLE_STAGE"
    counts = pattern_counts(spar)
    all_base_ready = all_patterns_at_least(spar, 5)
    all_fragility_ready = all_patterns_at_least(spar, 10)
    stale_hours = None
    if spar is not None:
        spar_max = parse_ts((spar.get("source") or {}).get("max_timestamp_utc"))
        if latest_capture_ts and spar_max:
            stale_hours = (latest_capture_ts - spar_max).total_seconds() / 3600

    if spar is None:
        action = "RUN_SPAR_BASE"
        reason = "PDLT_IS_FROZEN_OR_SAFELY_BLOCKED_AND_SPAR_HAS_NOT_RUN"
    elif frag and frag.get("status") == "ROBUSTNESS_REVIEW_READY":
        # Legacy pre-Phase-II fragility output must never open ETF execution.
        action = "WAIT"
        reason = "LEGACY_SPAP_FRAGILITY_READY_INVALID_AFTER_PHASE2_METHODS_REVIEW"
    elif frag and frag.get("status") == "METHODS_BLOCKED_PLACEBO_REGIME_NOT_FROZEN":
        if stale_hours is not None and stale_hours >= 12:
            action = "RUN_SPAR_BASE"
            reason = "REFRESH_BASE_WHILE_FRAGILITY_METHODS_REMAIN_BLOCKED"
        else:
            action = "WAIT"
            reason = "SPAR_FRAGILITY_METHODS_BLOCKED_PLACEBO_REGIME_NOT_FROZEN"
    elif all_base_ready and all_fragility_ready and (frag is None or frag.get("status") == "INSUFFICIENT_EVIDENCE"):
        action = "RUN_SPAR_FRAGILITY"
        reason = "ALL_SPAR_PATTERNS_REACHED_PREREGISTERED_10_EVENT_FRAGILITY_GATE"
    elif stale_hours is not None and stale_hours >= 12:
        action = "RUN_SPAR_BASE"
        reason = "NEW_FREE_CAPTURE_DATA_AVAILABLE"
    else:
        action = "WAIT"
        reason = "WAITING_FOR_MORE_FREE_PROSPECTIVE_EVIDENCE"

    return {
        "contract": "SEQUENTIAL_RESEARCH_QUEUE_STATE_v1",
        "authority": "SHADOW_RESEARCH_ONLY",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "queue_contract": queue.get("contract"),
        "pdlt_status": pdlt_status,
        "next_action": action,
        "reason": reason,
        "spar_matured_72h_by_pattern": counts,
        "spar_all_patterns_base_gate": all_base_ready,
        "spar_all_patterns_fragility_gate": all_fragility_ready,
        "spar_fragility_methods_gate": "PLACEBO_AND_REGIME_MECHANICS_NOT_FROZEN",
        "etf_execution_authorized": False,
        "budget_decision": {
            "new_cfgi_credits_authorized": 0,
            "new_openai_usd_authorized": 0.0,
            "paid_rerun_pdlt_authorized": False,
        },
        "one_active_execution_stage_only": True,
        "passive_maturation_may_overlap": True,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--queue", type=Path, required=True)
    p.add_argument("--repo-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    q = json.loads(a.queue.read_text())
    out = decide(a.repo_root, q)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
