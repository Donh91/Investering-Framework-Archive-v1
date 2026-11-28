"""Offline C2 diagnostic for the existing API Agent; never selects or invokes a model."""
from collections import defaultdict
from decimal import Decimal
import json
import re


AUTHORITY = {"routing_override": False, "budget_authority": False,
             "paid_call": False, "scientific_promotion": False}


def policy_diagnostics(routing, registry, shared):
    if (routing.get("contract"), registry.get("contract"), shared.get("contract")) != (
        "CAPABILITY_ROUTING_POLICY_v1", "API_TASK_REGISTRY_v1", "SOL_MAX_SHARED_MODEL_POLICY_V1"
    ):
        raise ValueError("unexpected_policy_contract")
    models, tasks = routing.get("models"), registry.get("tasks")
    required = shared.get("required_new_max_model")
    if (not isinstance(models, dict) or not models or not isinstance(tasks, dict)
            or not isinstance(required, str) or not required.strip()
            or "RESEARCH_LAB_SOL_ANALYSIS" not in tasks
            or any(not isinstance(task, str) or not isinstance(cfg, dict)
                   or not isinstance(cfg.get("model"), str) or not cfg["model"].strip()
                   for task, cfg in tasks.items())):
        raise ValueError("invalid_policy_shape")
    return {
        "authority": dict(AUTHORITY),
        "registry_task_count": len(tasks),
        "registry_models_missing_from_router": sorted(
            [task, cfg["model"]] for task, cfg in tasks.items() if cfg["model"] not in models
        ),
        "new_owner_bound_sol_max": required,
        "new_sol_max_listed_in_general_router": required in models,
        "legacy_registry_research_model": tasks["RESEARCH_LAB_SOL_ANALYSIS"]["model"],
        "interpretation": "SCOPE_RECONCILIATION_REQUIRED_NOT_RUNTIME_FAILURE_PROOF",
    }


def receipt_census(receipts):
    """Descriptive recorded estimates by exact task/model/effort, not resolved-work costs.

    Caller must authenticate and bound the source cohort separately. Missing receipts
    cannot be detected here. Exact duplicate rows count once; overlapping response IDs
    with different rows invalidate the census rather than silently double-counting.
    """
    seen, groups = {}, defaultdict(lambda: {"receipts": 0, "gateway_pass": 0,
                                            "attempts": 0, "cost": Decimal(0)})
    duplicates = 0
    for row in receipts:
        if not isinstance(row, dict) or row.get("contract") != "API_AGENT_RECEIPT_v3":
            raise ValueError("unexpected_receipt_contract")
        key = tuple(row.get(k) for k in ("task", "model", "reasoning_effort"))
        if any(not isinstance(v, str) or not v.strip() for v in key):
            raise ValueError("missing_cohort_identity")
        ids, attempts = row.get("response_ids"), row.get("attempt_count")
        if (not isinstance(ids, list) or not ids or any(not isinstance(x, str) or not x.strip() for x in ids)
                or len(set(ids)) != len(ids) or type(attempts) is not int or attempts != len(ids)
                or row.get("response_id") != ids[-1]):
            raise ValueError("invalid_attempt_identity")
        if not isinstance(row.get("output_hash"), str) or not re.fullmatch(r"[0-9a-f]{64}", row["output_hash"]):
            raise ValueError("invalid_output_hash")
        for k in ("input_tokens", "output_tokens", "created_unix"):
            if type(row.get(k)) is not int or row[k] < 0:
                raise ValueError("invalid_usage_or_clock")
        raw = row.get("estimated_cost_usd")
        if type(raw) not in (int, float):
            raise ValueError("invalid_recorded_cost")
        cost = Decimal(str(raw))
        if not cost.is_finite() or cost < 0:
            raise ValueError("invalid_recorded_cost")
        if row.get("status") not in ("PASS", "COST_EXCEEDED", "API_OUTPUT_INVALID"):
            raise ValueError("unknown_gateway_status")
        identity = json.dumps(row, sort_keys=True, separators=(",", ":"), allow_nan=False)
        overlaps = [seen[x] for x in ids if x in seen]
        if overlaps:
            if len(overlaps) == len(ids) and all(x == identity for x in overlaps):
                duplicates += 1
                continue
            raise ValueError("conflicting_response_identity")
        seen.update({x: identity for x in ids})
        g = groups[key]
        g["receipts"] += 1
        g["gateway_pass"] += int(row["status"] == "PASS")
        g["attempts"] += attempts
        g["cost"] += cost
    result = []
    for (task, model, effort), g in sorted(groups.items()):
        result.append({"task": task, "model": model, "reasoning_effort": effort,
                       "receipt_count": g["receipts"], "gateway_pass_count": g["gateway_pass"],
                       "attempt_count": g["attempts"], "recorded_estimate_usd": str(g["cost"]),
                       "estimate_per_gateway_pass_usd": str(g["cost"] / g["gateway_pass"]) if g["gateway_pass"] else None,
                       "cost_per_independently_resolved_work_usd": None})
    return {"authority": dict(AUTHORITY), "duplicate_rows": duplicates, "cohorts": result,
            "coverage": "CALLER_SUPPLIED_NOT_PROVEN_COMPLETE",
            "cost_basis": "RECORDED_GATEWAY_ESTIMATE_NOT_PROVIDER_INVOICE",
            "resolution_evidence": "UNAVAILABLE_NO_INDEPENDENT_WORK_ID_JOIN",
            "routing_recommendation": None}
