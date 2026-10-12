#!/usr/bin/env python3
"""Non-executing Research Lab REA mission/evidence gate. No provider/network/model calls."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

MISSION = "RL-REA-CUSTOM-FIT-007"
MODEL_TASK = "RESEARCH_LAB_SOL_ANALYSIS"
PACKET_CONTRACT = "RESEARCH_LAB_SOL_MISSION_PACKET_v1"
TRIAL_CONTRACT = "REA_CUSTOM_FIT_TECHNICAL_TRIAL_V1"
WAIT = "WAITING_PREDECESSOR"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path) -> dict:
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError("JSON_OBJECT_REQUIRED")
    return result


def blocked(reason: str, **data: object) -> dict:
    return {"mission_id": MISSION, "authority": "RESEARCH_ONLY", "state": "BLOCKED", "reason": reason, **data}


def inspect_release(queue: dict, packet: dict) -> dict:
    """Diagnose queue state, never release a mission or spend an API dollar."""
    if queue.get("contract") != "RESEARCH_LAB_SOL_QUEUE_v1":
        return blocked("QUEUE_CONTRACT_INVALID")
    if packet.get("contract") != PACKET_CONTRACT or packet.get("mission_id") != MISSION:
        return blocked("PACKET_IDENTITY_INVALID")
    if packet.get("task") != MODEL_TASK or queue.get("task_name") != MODEL_TASK:
        return blocked("MODEL_TASK_BINDING_INVALID")
    if queue.get("max_active_missions") != 1 or queue.get("trigger_issue") != 1476:
        return blocked("EXISTING_DISPATCH_CONTRACT_DRIFT")
    for obj in (queue.get("authority"), packet.get("authority")):
        if not isinstance(obj, dict) or not obj or any(value is not False for value in obj.values()):
            return blocked("AUTHORITY_NOT_ZERO")
    missions = queue.get("missions")
    if not isinstance(missions, list):
        return blocked("MISSION_LIST_INVALID")
    ids = [x.get("mission_id") for x in missions if isinstance(x, dict)]
    if len(ids) != len(set(ids)):
        return blocked("DUPLICATE_MISSION_IDS")
    selected = [x for x in missions if isinstance(x, dict) and x.get("mission_id") == MISSION]
    active = [x.get("mission_id") for x in missions if isinstance(x, dict) and x.get("state") == "ACTIVE_RELEASED"]
    if len(selected) != 1 or len(active) != 1:
        return blocked("ONE_ACTIVE_ONE_WAITING_INVARIANT_FAILED", active=active)
    if queue.get("active_mission") != active[0]:
        return blocked("ACTIVE_MISSION_POINTER_CONFLICT", active=active)
    if selected[0].get("state") != WAIT:
        return blocked("MISSION_MUST_REMAIN_WAITING_UNTIL_OWNER_RELEASE", active=active)
    if selected[0].get("mission_packet") != "06_RESEARCH_LAB/mission_packets/2026-10-12__RL-REA-CUSTOM-FIT-007__sol-api.json":
        return blocked("MISSION_PACKET_PATH_MISMATCH")
    if packet.get("status") != "DESIGN_FROZEN_WAITING_PREDECESSOR_M6":
        return blocked("DESIGN_FREEZE_DRIFT")
    return {
        "mission_id": MISSION,
        "authority": "RESEARCH_ONLY",
        "state": "QUEUED_NOT_RELEASED",
        "active_predecessor": active[0],
        "api_call_permitted": False,
        "automatic_release_permitted": False,
        "requires_owner_budget_and_head_refresh": True,
        "note": "Queue evidence is not evidence of a model call, REA success or alpha."
    }


def inspect_technical_trial(trial: dict, target_bytes: bytes) -> dict:
    """Conservative on-disk technical fact gate, *not* an economic signal validator."""
    if trial.get("contract") != TRIAL_CONTRACT:
        return blocked("TRIAL_CONTRACT_INVALID")
    if trial.get("mission_id") != MISSION or trial.get("authority") != "RESEARCH_ONLY":
        return blocked("TRIAL_AUTHORITY_OR_IDENTITY_INVALID")
    s = trial.get("source")
    if not isinstance(s, dict) or s.get("rights_confirmed") is not True or s.get("sha256") != sha(target_bytes):
        return blocked("SOURCE_HASH_OR_RIGHTS_UNVERIFIED")
    safety = trial.get("safety")
    if not isinstance(safety, dict) or any(safety.get(x) is not True for x in ("no_secrets_in_payload", "authorized_capture", "real_process_ownership_guard")):
        return blocked("SAFETY_OR_HOST_GUARD_UNVERIFIED")
    if trial.get("host_status") == "HOST_CAPABILITY_GATED":
        return {"mission_id":MISSION,"authority":"RESEARCH_ONLY","state":"HOST_CAPABILITY_GATED","incremental_fact_count":0,"economic_edge":"NOT_ASSESSED"}
    if trial.get("host_status") != "RUN_COMPLETED":
        return blocked("HOST_OR_RUN_UNVERIFIED")
    baseline = trial.get("baseline")
    treatment = trial.get("rea")
    if not isinstance(baseline, dict) or not isinstance(treatment, dict):
        return blocked("BASELINE_OR_TREATMENT_MISSING")
    if baseline.get("source_sha256") != sha(target_bytes) or treatment.get("source_sha256") != sha(target_bytes):
        return blocked("UNEQUAL_SOURCE_CLOCK_OR_BYTES")
    if baseline.get("preregistered_before_rea") is not True:
        return blocked("BASELINE_NOT_FROZEN_BEFORE_TREATMENT")
    prior = baseline.get("fact_ids")
    findings = treatment.get("findings")
    if not isinstance(prior, list) or not all(isinstance(x, str) and x for x in prior):
        return blocked("BASELINE_FACTS_INVALID")
    if not isinstance(findings, list):
        return blocked("TREATMENT_FACTS_INVALID")
    valid = []
    seen = set(prior)
    original = target_bytes.decode("utf-8", errors="replace")
    for finding in findings:
        if not isinstance(finding, dict):
            return blocked("FINDING_RECORD_INVALID")
        fid = finding.get("fact_id")
        if not isinstance(fid, str) or not fid or fid in seen:
            continue
        # These are a necessary floor, not independent scientific acceptance.
        anchor = finding.get("source_anchor_exact")
        if not isinstance(anchor, str) or len(anchor) < 8 or anchor not in original:
            continue
        if finding.get("independent_source_review") is not True:
            continue
        if finding.get("actionable_owner_confirmed") is not True:
            continue
        seen.add(fid)
        valid.append(fid)
    return {
        "mission_id": MISSION,
        "authority": "RESEARCH_ONLY",
        "state": "SOURCE_ANCHORED_NOVELTY_CANDIDATE" if valid else "NO_INCREMENTAL_VERIFIED_FACT",
        "incremental_fact_count": len(valid),
        "incremental_fact_ids": valid,
        "economic_edge": "NOT_ASSESSED",
        "production_promotion_allowed": False,
        "independent_code_owner_approval_still_required": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    q = sub.add_parser("queue")
    q.add_argument("--queue", type=Path, required=True)
    q.add_argument("--packet", type=Path, required=True)
    t = sub.add_parser("trial")
    t.add_argument("--trial", type=Path, required=True)
    t.add_argument("--target", type=Path, required=True)
    args = ap.parse_args()
    if args.command == "queue":
        out = inspect_release(load(args.queue), load(args.packet))
    else:
        out = inspect_technical_trial(load(args.trial), args.target.read_bytes())
    print(json.dumps(out, sort_keys=True, indent=2))
    if out["state"] == "BLOCKED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
