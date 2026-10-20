#!/usr/bin/env python3
"""Fail-closed month-wide CAS liability admission for existing Strategist lane.

Only the existing GitHub workflow writes the ledger to main. This module never
calls GitHub, models, or any API. Every successful claim permanently consumes
its maximum estimated liability (not the optimistic actual-cost estimate).
Concurrent different fingerprints contend on ONE GitHub Contents API blob SHA.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

from scripts.api_agent.api_gateway import PRICES_PER_MILLION, estimate_cost

CONTRACT = "FRAMEWORK_STRATEGIST_MONTHLY_LIABILITY_v1"
TASK = "FRAMEWORK_STRATEGIST_SEMANTIC"
MODEL = "gpt-6.1-sol"
CAP_USD = 0.75
RESERVE_USD = 0.05
OVERHEAD_TOKENS = 8192  # conservative protocol/context wrapper budget
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
            + "\n").encode("utf-8")


def max_liability(root: Path, runtime: Path) -> float:
    """Maximum possible bill for this model's bounded request, not a forecast."""
    registry = json.loads((root / "research/api_agent/API_TASK_REGISTRY_v1.json").read_text())
    policy = json.loads((root / "research/api_agent/API_INTELLIGENCE_POLICY_v2.json").read_text())
    cfg = registry["tasks"][TASK]
    if (cfg["model"] != MODEL or cfg["max_attempts"] != 1
            or cfg["max_output_tokens"] != 5400
            or policy["monthly_hard_stop_usd"] != 40
            or policy["global_reserve_usd"] != 4
            or policy["lane_caps_usd"][TASK] != CAP_USD
            or MODEL not in PRICES_PER_MILLION):
        raise ValueError("budget_policy_or_pricing_drift")
    instruction = cfg["governed_instruction"].encode("utf-8")
    prompt = (runtime / "prompt.txt").read_bytes()
    context = (runtime / "context.json").read_bytes()
    if len(context) > 12_001 or len(prompt) > 10_000:
        raise ValueError("unbounded_model_inputs")
    input_ceiling = len(instruction) + len(prompt) + len(context) + OVERHEAD_TOKENS
    estimate = estimate_cost(MODEL, input_ceiling, cfg["max_output_tokens"])
    if not math.isfinite(estimate) or estimate <= 0 or estimate > 0.15:
        raise ValueError("unknown_or_excessive_model_liability")
    return math.ceil(estimate * 1_000_000) / 1_000_000


def claim_month(ledger: dict, *, month: str, fingerprint: str, run_id: str,
                liability_usd: float) -> dict:
    """Pure CAS payload constructor: no optimistic spent-only admission."""
    if not re.fullmatch(r"20[0-9]{2}-(0[1-9]|1[0-2])", month):
        raise ValueError("invalid_month")
    if not HEX64.fullmatch(fingerprint) or not re.fullmatch(r"[0-9]{1,20}", run_id):
        raise ValueError("invalid_claim_identity")
    if (not isinstance(liability_usd, float) or not math.isfinite(liability_usd)
            or liability_usd <= 0 or liability_usd > 0.15):
        raise ValueError("invalid_max_liability")
    if not ledger:
        entries = {}
    else:
        if (ledger.get("contract") != CONTRACT or ledger.get("month") != month
                or ledger.get("task") != TASK
                or ledger.get("cap_usd") != CAP_USD
                or ledger.get("reserve_usd") != RESERVE_USD
                or not isinstance(ledger.get("entries"), dict)):
            raise ValueError("untrusted_existing_monthly_ledger")
        entries = ledger["entries"]
    total = 0.0
    for key, row in entries.items():
        if (not isinstance(key, str) or not HEX64.fullmatch(key)
                or not isinstance(row, dict)
                or not re.fullmatch(r"[0-9]{1,20}", str(row.get("github_run_id", "")))
                or type(row.get("max_liability_usd")) not in (int, float)
                or not math.isfinite(row["max_liability_usd"])
                or row["max_liability_usd"] <= 0 or row["max_liability_usd"] > 0.15):
            raise ValueError("untrusted_existing_liability")
        total += row["max_liability_usd"]
    if fingerprint in entries:
        raise ValueError("already_claimed_no_second_payment")
    if round(total + liability_usd + RESERVE_USD, 6) > CAP_USD:
        raise ValueError("monthly_budget_insufficient_for_worst_case")
    return {"contract": CONTRACT, "month": month, "task": TASK,
            "cap_usd": CAP_USD, "reserve_usd": RESERVE_USD,
            "entries": {**entries, fingerprint: {
                "github_run_id": run_id,
                "max_liability_usd": liability_usd,
                "disposition": "CLAIMED_CONSERVATIVELY_NEVER_AUTO_REFUNDED"}}}


def prepare_payload(root: Path, runtime: Path, remote_get: dict,
                    *, month: str, run_id: str) -> dict:
    now = datetime.now(timezone.utc).strftime("%Y-%m")
    if month != now:
        raise ValueError("crossed_utc_month_boundary")
    plan = json.loads((runtime / "plan.json").read_text())
    fingerprint = plan.get("material_fingerprint")
    if (plan.get("run_allowed") is not True or not isinstance(fingerprint, str)
            or not HEX64.fullmatch(fingerprint) or plan.get("max_api_calls") != 1):
        raise ValueError("unqualified_strategist_attempt")
    # GH REST Contents response, or {} ONLY after verified HTTP 404. Parsing an
    # arbitrary exception as empty ledger would be fail-open, so workflow must
    # pass --confirmed-absent on the explicit 404 path.
    old_sha = None
    if remote_get:
        old_sha = remote_get.get("sha")
        if not isinstance(old_sha, str) or not HEX40.fullmatch(old_sha):
            raise ValueError("invalid_remote_git_blob_sha")
        data = base64.b64decode(remote_get["content"], validate=False)
        if hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() != old_sha:
            raise ValueError("remote_ledger_content_sha_mismatch")
        ledger = json.loads(data)
    else:
        ledger = {}
    liability = max_liability(root, runtime)
    updated = claim_month(ledger, month=month, fingerprint=fingerprint,
                          run_id=run_id, liability_usd=liability)
    rel = "research/framework_learning/strategist/semantic/reservations/monthly/" + month + ".json"
    body = {"message": f"budget(strategist): claim monthly maximum liability {fingerprint[:12]}",
            "branch": "main", "content": base64.b64encode(canonical(updated)).decode("ascii")}
    if old_sha is not None:
        body["sha"] = old_sha  # CAS: concurrent DISTINCT fingerprints conflict
    return {"path": rel, "request": body, "liability_usd": liability}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--runtime-dir", type=Path, required=True)
    ap.add_argument("--remote-get", type=Path, required=True)
    ap.add_argument("--month", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--confirmed-absent", action="store_true")
    a = ap.parse_args()
    remote = json.loads(a.remote_get.read_text())
    if not remote and not a.confirmed_absent:
        raise SystemExit("remote_ledger_absence_not_authoritative")
    request = prepare_payload(a.repo_root, a.runtime_dir, remote,
                              month=a.month, run_id=a.run_id)
    print(json.dumps(request, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
