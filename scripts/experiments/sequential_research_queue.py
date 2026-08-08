from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def decide(root: Path, queue: dict[str, Any]) -> dict[str, Any]:
    frozen = root / "research/experiments/pdlt_v1_1/discovery/FROZEN_MODEL_v1.json"
    pdlt_status = "DISCOVERY_FROZEN" if frozen.exists() else "BLOCKED_SAFE_PAID_RESUME_REQUIRED"

    latest_spar = root / "research/experiments/spar_v1/LATEST_REPORT.json"
    latest_frag = root / "research/experiments/spar_v1/LATEST_FRAGILITY_REPORT.json"
    latest_capture = read_json(root / "03_DAILY_CAPTURE_LOGS/captures/LATEST.json") or {}
    latest_capture_ts = parse_ts(latest_capture.get("captured_at_utc"))
    spar = read_json(latest_spar)
    frag = read_json(latest_frag)

    action = "WAIT"
    reason = "NO_RUNNABLE_STAGE"
    if spar is None:
        action = "RUN_SPAR_BASE"
        reason = "PDLT_IS_FROZEN_OR_SAFELY_BLOCKED_AND_SPAR_HAS_NOT_RUN"
    else:
        spar_max = parse_ts((spar.get("source") or {}).get("max_timestamp_utc"))
        stale_hours = None
        if latest_capture_ts and spar_max:
            stale_hours = (latest_capture_ts - spar_max).total_seconds() / 3600
        if spar.get("status") == "INSUFFICIENT_EVIDENCE" and stale_hours is not None and stale_hours >= 12:
            action = "RUN_SPAR_BASE"
            reason = "NEW_FREE_CAPTURE_DATA_AVAILABLE"
        elif spar.get("status") == "READY_FOR_ROBUSTNESS_REVIEW" and frag is None:
            action = "RUN_SPAR_FRAGILITY"
            reason = "SPAR_BASE_REACHED_PREREGISTERED_REVIEW_GATE"
        elif spar.get("status") == "READY_FOR_ROBUSTNESS_REVIEW" and frag and frag.get("status") == "INSUFFICIENT_EVIDENCE" and stale_hours is not None and stale_hours >= 12:
            action = "RUN_SPAR_BASE"
            reason = "REFRESH_BASE_BEFORE_NEXT_FRAGILITY_REVIEW"
        elif frag and frag.get("status") == "ROBUSTNESS_REVIEW_READY":
            action = "WAIT"
            reason = "ETF_TRANSMISSION_REMAINS_QUEUED_BUT_REQUIRES_VERIFIED_DATA_ADAPTER_BEFORE_EXECUTION"
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
