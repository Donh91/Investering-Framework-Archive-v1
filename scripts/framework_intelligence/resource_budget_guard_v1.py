#!/usr/bin/env python3
"""No-network resource advisory inside the EXISTING Framework Learning Supervisor.

This stage cannot query account billing with a repository GITHUB_TOKEN. A verified
billing snapshot may be supplied by an authorized existing owner. A missing or
stale snapshot is UNKNOWN, never a fabricated live quota. No AI/API/cloud calls.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

POLICY = "00_FMOS/framework_strategist/RESOURCE_CONSERVATION_POLICY_v1.json"
PRODUCTION = "research/framework_learning/resource_budget/LATEST.json"
DRYRUN = "runtime/framework-learning-supervisor/resource_budget/LATEST.json"
CONTRACT = "FRAMEWORK_RESOURCE_BUDGET_ADVISORY_v1"


def utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC_Z_REQUIRED")
    instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if instant.utcoffset().total_seconds() != 0:
        raise ValueError("UTC_ONLY")
    return instant.astimezone(timezone.utc)


def strict_read(path: Path, limit: int = 100000) -> dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise ValueError("SOURCE_NOT_SAFE")
    def reject_constant(value: str) -> None:
        raise ValueError("NONFINITE_NUMBER:" + value)
    def finite_float(value: str) -> float:
        x = float(value)
        if not math.isfinite(x):
            raise ValueError("NONFINITE_FLOAT")
        return x
    result = json.loads(path.read_bytes(), parse_constant=reject_constant,
                        parse_float=finite_float)
    if not isinstance(result, dict):
        raise ValueError("INVALID_OBJECT")
    return result


def assess(root: Path, *, now: datetime, snapshot: Path | None = None) -> dict:
    if now.tzinfo is None:
        raise ValueError("NAIVE_CLOCK")
    now = now.astimezone(timezone.utc)
    root = root.resolve()
    policy = strict_read(root / POLICY)
    if policy.get("contract") != "RESOURCE_CONSERVATION_OWNER_POLICY_v1":
        raise ValueError("INVALID_POLICY")
    if (policy.get("codex_cloud_default") != "DISABLED_PASSIVE"
            or policy.get("automatic_spend_authority") is not False
            or policy.get("new_workflows_or_agent_schedules") is not False):
        raise ValueError("AUTHORITY_BOUNDARY_BROKEN")

    actions_critical = now < utc(policy["actions_critical_until_utc"])
    codex_critical = now < utc(policy["codex_cloud_critical_until_utc"])
    snapshot_status = "MISSING"
    actions_usage = None
    codex_remaining_pct = None
    if snapshot is not None:
        try:
            candidate = snapshot.resolve()
            # The snapshot must be an explicitly supplied ordinary file in root.
            if snapshot.is_symlink() or root not in candidate.parents:
                raise ValueError("UNSAFE_SNAPSHOT_PATH")
            evidence = strict_read(candidate)
            if evidence.get("contract") != "RESOURCE_USAGE_SNAPSHOT_v1":
                raise ValueError("BAD_SNAPSHOT_CONTRACT")
            at = utc(evidence["as_of_utc"])
            age = (now - at).total_seconds()
            if age < -900 or age > 24 * 3600:
                snapshot_status = "STALE_OR_FUTURE"
            elif evidence.get("source_type") == "GITHUB_BILLING_DIRECT":
                # This local JSON is self-declared. Without an authenticated
                # provider fetch/receipt, it MUST NOT count as provider-verified
                # billing, even if its source_type string says it does.
                snapshot_status = "UNAUTHENTICATED_BILLING_CLAIM"
            elif evidence.get("source_type") != "OWNER_SCREENSHOT":
                snapshot_status = "SOURCE_UNVERIFIED"
            else:
                gb = evidence.get("github_actions", {})
                cb = evidence.get("codex", {})
                used = gb.get("used_minutes")
                included = gb.get("included_minutes")
                remaining = cb.get("remaining_pct")
                # bool, invalid data, missing fields and overflow are unknown.
                def valid(n):
                    return type(n) in (int, float) and math.isfinite(n)
                if (not valid(used) or not valid(included) or included <= 0
                        or used < 0 or not valid(remaining) or not 0 <= remaining <= 100):
                    snapshot_status = "INVALID_VALUES"
                else:
                    actions_usage = {"fraction_used": round(used / included, 4),
                                     "source_type": evidence["source_type"],
                                     "as_of_utc": evidence["as_of_utc"]}
                    codex_remaining_pct = remaining
                    snapshot_status = "CURRENT_OWNER_REPORTED"
        except (OSError, ValueError, TypeError, KeyError, OverflowError):
            snapshot_status = "INVALID_OR_UNREADABLE"

    actions_state = "UNKNOWN"
    if actions_usage is not None:
        frac = actions_usage["fraction_used"]
        actions_state = "CRITICAL" if frac >= .90 else ("CONSERVE" if frac >= .75 else "NORMAL")
    if actions_critical:
        actions_state = "CRITICAL"

    codex_state = "UNKNOWN"
    if codex_remaining_pct is not None:
        codex_state = ("CRITICAL" if codex_remaining_pct <= 30
                       else "CONSERVE" if codex_remaining_pct <= 50 else "NORMAL")
    if codex_critical:
        codex_state = "CRITICAL"

    state = ("CRITICAL" if "CRITICAL" in (actions_state, codex_state)
             else "CONSERVE" if "CONSERVE" in (actions_state, codex_state)
             else "UNKNOWN" if "UNKNOWN" in (actions_state, codex_state)
             else "NORMAL")
    return {
        "contract": CONTRACT,
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "status": state,
        "github_actions": {"status": actions_state, "usage": actions_usage,
                           "owner_declared_emergency": actions_critical},
        "codex_cloud": {"status": codex_state,
                        "remaining_pct": codex_remaining_pct,
                        "owner_declared_emergency": codex_critical,
                        "passive_execution": "NOT_AUTHORIZED"},
        "snapshot_status": snapshot_status,
        "billing_hard_stop_verified": False,
        "scope": "READ_ONLY_RESOURCE_ADVISORY_NOT_PROVIDER_BILLING_CONTROL",
        "expensive_work": "EXPLICIT_BOUNDED_OWNER_TASK_ONLY",
        "unknown_usage": "NO_NEW_PASSIVE_CLOUD_OR_UNVERIFIED_SPENDING",
        "authority": {"automatic_dispatch": False, "automatic_spend": False,
                      "automatic_merge": False, "new_schedule": False,
                      "ci_bypass": False, "trading": False},
        "next_owner": "EXISTING_SUPERVISOR_AND_FRAMEWORK_STRATEGIST",
        "required_billing_followup": ("Read actual account Actions budgets/usage "
                                       "and Codex weekly usage from authorized owner surfaces."),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", default=".")
    p.add_argument("--output", default=PRODUCTION)
    p.add_argument("--snapshot", default=None)
    p.add_argument("--as-of-utc", default=None)
    args = p.parse_args()
    root = Path(args.repo_root).resolve()
    output = root / args.output
    target = output.resolve()
    allow = {(root / PRODUCTION).resolve(), (root / DRYRUN).resolve()}
    if (target not in allow or target != output.absolute()
            or output.is_symlink() or root not in target.parents):
        raise ValueError("INVALID_OUTPUT_PATH")
    snap = Path(args.snapshot) if args.snapshot else None
    if snap is not None and not snap.is_absolute():
        snap = root / snap
    now = utc(args.as_of_utc) if args.as_of_utc else datetime.now(timezone.utc)
    report = assess(root, now=now, snapshot=snap)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name("." + output.name + "." + str(os.getpid()) + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(report, file, indent=2, sort_keys=True)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    print(json.dumps({"contract": CONTRACT, "status": report["status"],
                      "snapshot_status": report["snapshot_status"]}, sort_keys=True))


if __name__ == "__main__":
    main()
