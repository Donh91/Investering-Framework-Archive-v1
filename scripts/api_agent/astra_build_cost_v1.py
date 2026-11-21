"""BUILD_v1 mission-specific budget/repair *preflight*, no paid authority.

This is an additional, fail-closed cap; it never widens the existing global
USD3 ordinary request, USD4 protected reserve, owner ledger, or native claim.
A BUILD stage is a separately reviewed one-shot owner mission. Two stages
are permitted only when stage one has a genuine independently verified
test-failure receipt, never as a retry after an uncertain paid POST.
"""
from __future__ import annotations

import re

from scripts.api_agent.api_gateway import estimate_cost

MAX_REQUEST_BYTES = 600_000
INPUT_OVERHEAD_TOKENS = 20_000
MAX_STAGE_USD = 5.0
MAX_MISSION_USD = 10.0
MAX_STAGES = 2
MAX_PROGRAM_USD = 30.0
PROTECTED_BUILD_RESERVE_USD = 10.0
PROGRAM_MISSIONS = frozenset({"M1", "M2", "M3"})
MODEL = "gpt-6.2-astra"
EFFORT = "max"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
OWNER_STAGE = re.compile(r"ASTRA-BUILD-(M[123])-20261121-S([12])\Z")

class BudgetHold(ValueError):
    pass

def require(ok, code):
    if not ok:
        raise BudgetHold(code)

def exact_stage_id(work_id, mission, stage):
    require(mission in PROGRAM_MISSIONS, "BUILD_MISSION")
    require(type(stage) is int and stage in (1, 2), "BUILD_STAGE")
    require(work_id == f"ASTRA-BUILD-{mission}-20261121-S{stage}",
            "STAGE_WORK_ID")
    return work_id

def quote(*, work_id, mission, stage, model, reasoning_effort,
          request_bytes, max_output_tokens, prior=None):
    exact_stage_id(work_id, mission, stage)
    require(model == MODEL and reasoning_effort == EFFORT, "MODEL_OR_EFFORT")
    require(type(request_bytes) is int and 0 < request_bytes <= MAX_REQUEST_BYTES,
            "INPUT_600KB")
    require(type(max_output_tokens) is int and 4_096 <= max_output_tokens <= 128_000,
            "OUTPUT_TOKENS")
    if stage == 1:
        require(prior is None, "UNEXPECTED_PRIOR")
    else:
        require(isinstance(prior, dict) and set(prior) ==
                {"work_id", "stage", "status", "sandbox_receipt_sha256",
                 "native_run_id", "attempt_terminal"},
                "PRIOR_SCHEMA")
        require(prior.get("work_id") == f"ASTRA-BUILD-{mission}-20261121-S1"
                and prior.get("stage") == 1
                and prior.get("status") == "VERIFIED_SANDBOX_TEST_FAILURE"
                and isinstance(prior.get("sandbox_receipt_sha256"), str)
                and HEX64.fullmatch(prior["sandbox_receipt_sha256"])
                and isinstance(prior.get("native_run_id"), int)
                and prior["native_run_id"] > 0
                and prior.get("attempt_terminal") is True,
                "PRIOR_FAILED_NATIVE_SANDBOX_REQUIRED")
    # request bytes as tokens + overhead is a deliberate conservative bound
    # as in the existing one-shot owner mission runner. The generic gateway
    # applies official long-context/cache-write tier pricing, not this module.
    input_upper = request_bytes + INPUT_OVERHEAD_TOKENS
    upper = estimate_cost(model, input_upper, max_output_tokens)
    require(type(upper) in (int, float) and 0 < upper <= MAX_STAGE_USD,
            "STAGE_OVER_USD5")
    return {"contract": "ASTRA_BUILD_BUDGET_PREFLIGHT_v1",
            "work_id": work_id, "mission": mission, "stage": stage,
            "model": model, "reasoning_effort": reasoning_effort,
            "request_bytes": request_bytes, "input_token_upper": input_upper,
            "max_output_tokens": max_output_tokens,
            "worst_case_usd": round(upper, 6),
            "hard_request_cap_usd": MAX_STAGE_USD,
            "hard_mission_cap_usd": MAX_MISSION_USD,
            "program_max_usd": MAX_PROGRAM_USD,
            "protected_build_reserve_usd": PROTECTED_BUILD_RESERVE_USD,
            "stage_two_requires_native_failed_sandbox": stage == 2,
            "normal_global_usd3_cap_unmodified": True,
            "independent_global_guard_required": True,
            "paid_post_permitted": False,
            "retry_authorized": False}

def validate_program_reservations(rows):
    """The caller supplies an authenticated native ledger subset, not model text."""
    require(isinstance(rows, list) and len(rows) <= 6, "BUILD_LEDGER_SHAPE")
    seen = set()
    per = {k: 0.0 for k in PROGRAM_MISSIONS}
    total = 0.0
    for row in rows:
        require(isinstance(row, dict)
                and set(row) == {"work_id", "upper_usd", "status"}, "BUILD_ROW")
        work_id, upper = row["work_id"], row["upper_usd"]
        m = OWNER_STAGE.fullmatch(str(work_id))
        require(m is not None and work_id not in seen, "BUILD_WORK_ID")
        require(type(upper) in (int, float) and 0 < upper <= MAX_STAGE_USD,
                "BUILD_ROW_USD5")
        require(row["status"] in ("OWNER_RESERVED_PREHTTP",
                                  "CONSUMED_PENDING_INVOICE",
                                  "CONSUMED_SETTLED_OWNER_PROVIDER_EVIDENCE"),
                "BUILD_ROW_STATUS")
        seen.add(work_id)
        per[m.group(1)] += upper
        total += upper
    require(all(cost <= MAX_MISSION_USD for cost in per.values()),
            "BUILD_MISSION_USD10")
    require(total <= MAX_PROGRAM_USD, "BUILD_PROGRAM_USD30")
    return {"max_program_usd": MAX_PROGRAM_USD, "current_reserved_upper_usd": total,
            "protected_build_reserve_usd": PROTECTED_BUILD_RESERVE_USD,
            "stage_count": len(rows), "per_mission": per,
            "global_budget_and_provider_settlement_unverified": True,
            "paid_authority": False}
