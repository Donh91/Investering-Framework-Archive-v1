from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))
from api_agent.api_gateway import PRICES_PER_MILLION, estimate_cost
from lib.evidence_io import cost_receipt_identity, created_utc, finite_nonnegative, json_evidence_paths, load_evidence

# Owner approval: normal USD40, account-wide exceptional ceiling USD45.
# Legacy caller-specific smaller caps/reserves remain binding; this code never
# grants a paid POST or lowers a lane's independent ceiling.
OWNER_GLOBAL_TARGET_USD = 40.0
OWNER_GLOBAL_HARD_STOP_USD = 45.0
OWNER_GLOBAL_RESERVE_USD = 4.0  # Routine paths retain existing protected headroom.
OWNER_SINGLE_REQUEST_CAP_USD = 3.0
# Exact unresolved native POSTs. Missing/removed rows must never silently
# become zero risk. This immutable floor may only change with separately
# reviewed provider-settlement evidence, NEVER by editing a JSON ledger alone.
UNRESOLVED_NATIVE_POST_FLOOR_USD = {
    "41870364609": 3.0,
    "41949497953": 3.0,
}
CANONICAL_LIABILITY_LEDGER = SCRIPTS_ROOT.parent / (
    "research/api_agent/coordination/API_PENDING_BILLING_RISK_V1.json"
)


def pending_risk(path: Path) -> tuple[float, float, int]:
    """Conservative persistent upper risk, never a provider invoice or retry permit.

    Unknown POSTs remain reserved across UTC month rollover until independent
    settlement evidence is admitted in the original governed source.
    """
    value = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(value, dict)
            or value.get("contract") != "API_PENDING_BILLING_RISK_V1"
            or value.get("no_retry_original_ids") is not True
            or value.get("requires_reconciliation_before_releasing_reserve") is not True
            or not isinstance(value.get("unresolved"), list)):
        raise ValueError("LIABILITY_LEDGER_CONTRACT_INVALID")
    low, high, seen = 0.0, 0.0, set()
    for row in value["unresolved"]:
        if not isinstance(row, dict):
            raise ValueError("LIABILITY_ROW_NOT_OBJECT")
        rid = row.get("run_id")
        month = row.get("created_month_utc")
        lo, hi = row.get("lower_usd"), row.get("upper_usd")
        src = row.get("source")
        if (not isinstance(rid, str) or not rid.isdecimal()
                or rid in seen or len(rid) > 19
                or not isinstance(month, str) or len(month) != 7
                or month[4] != "-" or not month[:4].isdigit()
                or not month[5:].isdigit() or not 1 <= int(month[5:]) <= 12
                or row.get("status") != "POST_OUTCOME_UNKNOWN"
                or not finite_nonnegative(lo) or not finite_nonnegative(hi)
                or float(lo) > float(hi) or float(hi) <= 0
                or float(hi) > OWNER_SINGLE_REQUEST_CAP_USD
                or not isinstance(src, str)
                or src != ("https://github.com/Donh91/"
                           "Investering-Framework-Archive-v1/actions/runs/" + rid)
                or not isinstance(row.get("basis"), str)
                or len(row["basis"].strip()) < 30):
            raise ValueError("LIABILITY_ROW_UNBOUNDED_OR_UNVERIFIED")
        seen.add(rid)
        low += float(lo)
        high += float(hi)
    missing = set(UNRESOLVED_NATIVE_POST_FLOOR_USD) - seen
    if missing:
        raise ValueError("KNOWN_UNSETTLED_NATIVE_POST_MISSING")
    for row in value["unresolved"]:
        floor = UNRESOLVED_NATIVE_POST_FLOOR_USD.get(row["run_id"])
        if floor is not None and float(row["upper_usd"]) < floor:
            raise ValueError("KNOWN_UNSETTLED_NATIVE_POST_UNDER_RESERVED")
    if not math.isfinite(high) or high > OWNER_GLOBAL_HARD_STOP_USD:
        raise ValueError("LIABILITY_TOTAL_INVALID")
    return low, high, len(seen)


def model_quote(args: argparse.Namespace) -> tuple[float, dict | None]:
    """No-network, no-POST price preview against CURRENT approved model/route.

    A new Sol version needs an actual verified price and original-owner registry
    update. A model name supplied by a chat/comment does not authorize billing.
    """
    fields = (args.model, args.task, args.effort, args.owner_work_id,
              args.input_token_upper, args.output_token_upper)
    if all(v is None for v in fields):
        return float(args.new_request_upper_usd), None
    if any(v is None for v in fields):
        raise ValueError("INCOMPLETE_OWNER_MODEL_APPROVAL")
    if (not isinstance(args.owner_work_id, str)
            or not 9 <= len(args.owner_work_id) <= 110
            or not all(x.isalnum() or x in "_-." for x in args.owner_work_id)
            or args.effort != "max"):
        raise ValueError("MAX_APPROVAL_ID_OR_EFFORT_INVALID")
    root = SCRIPTS_ROOT.parent
    registry = json.loads((root / "research/api_agent/API_TASK_REGISTRY_v1.json").read_text())
    routing = json.loads((root / "research/api_agent/CAPABILITY_ROUTING_POLICY_v1.json").read_text())
    task = registry.get("tasks", {}).get(args.task)
    model = args.model
    approved_model = routing.get("pricing_snapshot", {}).get("verified_latest_model_ids", {}).get("sol")
    price = routing.get("models", {}).get(model, {}).get("price_per_million")
    if (not isinstance(task, dict) or task.get("model") != model
            or task.get("reasoning_effort") != args.effort
            or task.get("advisory_only") is not True
            or task.get("automatic_code_write") is not False
            or task.get("automatic_merge") is not False
            or model != approved_model or model not in PRICES_PER_MILLION
            or price != PRICES_PER_MILLION[model]):
        raise ValueError("MAX_MODEL_NOT_CURRENTLY_PRICED_AND_ADMITTED")
    input_bound, output_bound = args.input_token_upper, args.output_token_upper
    if (type(input_bound) is not int or type(output_bound) is not int
            or not 0 <= input_bound <= 500_000
            or not 1 <= output_bound <= 100_000):
        raise ValueError("MAX_TOKEN_BOUND_INVALID")
    quoted = (input_bound * price["input"] + output_bound * price["output"]) / 1_000_000
    required = max(quoted, float(args.new_request_upper_usd))
    if not math.isfinite(required) or required > OWNER_SINGLE_REQUEST_CAP_USD:
        raise ValueError("MAX_SINGLE_REQUEST_CEILING_EXCEEDED")
    return required, {"model": model, "effort": args.effort, "task": args.task,
                      "work_id": args.owner_work_id,
                      "token_price_upper_usd": round(quoted, 8),
                      "status": "QUOTE_ONLY_NATIVE_OWNER_CLAIM_REQUIRED"}


def parse_created(value: dict) -> datetime | None:
    return created_utc(value)


def effective_cost(value: dict) -> tuple[float | None, bool, str | None]:
    recorded = value.get("estimated_cost_usd")
    if not finite_nonnegative(recorded):
        return None, False, "INVALID_COST_OR_TIMESTAMP"
    model = value.get("model")
    has_usage = "input_tokens" in value or "output_tokens" in value
    is_api_receipt = value.get("contract") == "API_AGENT_RECEIPT_v3"
    if is_api_receipt and (model in PRICES_PER_MILLION or has_usage):
        if model not in PRICES_PER_MILLION:
            return None, False, "UNKNOWN_MODEL_FOR_USAGE_RECEIPT"
        input_tokens = value.get("input_tokens")
        output_tokens = value.get("output_tokens")
        if isinstance(input_tokens, bool) or isinstance(output_tokens, bool) or not isinstance(input_tokens, int) or not isinstance(output_tokens, int) or input_tokens < 0 or output_tokens < 0:
            return None, False, "INVALID_TOKEN_USAGE"
        normalized = estimate_cost(str(model), input_tokens, output_tokens)
        return normalized, abs(float(recorded) - normalized) > 1e-12, None
    return float(recorded), False, None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt-root", type=Path, required=True)
    parser.add_argument("--hard-stop-usd", type=float, required=True)
    parser.add_argument("--reserve-usd", type=float, default=0.25)
    parser.add_argument("--pending-ledger-root", type=Path)
    parser.add_argument("--liability-ledger", type=Path, default=CANONICAL_LIABILITY_LEDGER)
    parser.add_argument("--new-request-upper-usd", type=float, default=0.0)
    parser.add_argument("--model")
    parser.add_argument("--task")
    parser.add_argument("--effort")
    parser.add_argument("--owner-work-id")
    parser.add_argument("--input-token-upper", type=int)
    parser.add_argument("--output-token-upper", type=int)
    args = parser.parse_args()
    if (not finite_nonnegative(args.hard_stop_usd)
            or not finite_nonnegative(args.reserve_usd)
            or not finite_nonnegative(args.new_request_upper_usd)
            or args.new_request_upper_usd > OWNER_SINGLE_REQUEST_CAP_USD):
        parser.error("caps/reserves must be finite nonnegative; one request <= USD3")

    now = datetime.now(timezone.utc)
    total = 0.0
    receipts = 0
    repriced_api_receipts = 0
    errors = []
    missing_optional_roots = []
    roots = [(args.receipt_root, False)]
    if args.pending_ledger_root:
        roots.append((args.pending_ledger_root, True))

    seen: dict[tuple, tuple] = {}
    for root, optional in roots:
        if optional and not root.exists():
            missing_optional_roots.append(str(root))
            continue
        if not root.is_dir():
            errors.append({"path": str(root), "reason": "RECEIPT_ROOT_UNAVAILABLE"})
            continue
        paths, scan_errors = json_evidence_paths(root)
        errors.extend(scan_errors)
        for path in paths:
            evidence = load_evidence(path)
            if evidence.state != "USABLE":
                errors.append({"path": str(path), "reason": evidence.reason})
                continue
            value = evidence.value
            if not isinstance(value, dict):
                errors.append({"path": str(path), "reason": "RECEIPT_OBJECT_REQUIRED"})
                continue
            if "estimated_cost_usd" not in value:
                if value.get("task") or "RECEIPT" in str(value.get("contract", "")):
                    errors.append({"path": str(path), "reason": "COST_FIELD_MISSING"})
                continue
            created = parse_created(value)
            cost, repriced, cost_error = effective_cost(value)
            if created is None or cost_error is not None or cost is None:
                errors.append({"path": str(path), "reason": cost_error or "INVALID_COST_OR_TIMESTAMP"})
                continue
            recorded = value.get("estimated_cost_usd")
            try:
                identity = cost_receipt_identity(value, path, created)
            except ValueError:
                errors.append({'path': str(path), 'reason': 'COST_IDENTITY_INVALID'})
                continue
            accounting = (recorded, cost, created.year, created.month)
            if identity in seen:
                if seen[identity] != accounting:
                    errors.append({"path": str(path), "reason": "CONFLICTING_DUPLICATE_COST"})
                continue
            seen[identity] = accounting
            if (created.year, created.month) == (now.year, now.month):
                total += cost
                receipts += 1
                repriced_api_receipts += int(repriced)

    if not math.isfinite(total):
        errors.append({"path": str(args.receipt_root), "reason": "COST_TOTAL_NONFINITE"})
        total = None
    pending_low, pending_high, pending_count = 0.0, 0.0, 0
    try:
        pending_low, pending_high, pending_count = pending_risk(args.liability_ledger)
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        errors.append({"path": str(args.liability_ledger),
                       "reason": "LIABILITY_EVIDENCE_UNAVAILABLE:" + str(exc)[:100]})
    quoted = None
    new_upper = float(args.new_request_upper_usd)
    try:
        new_upper, quoted = model_quote(args)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as exc:
        errors.append({"path": "MAX_MODEL_QUOTE",
                       "reason": "MODEL_APPROVAL_BLOCKED:" + str(exc)[:100]})
    if new_upper > OWNER_SINGLE_REQUEST_CAP_USD:
        errors.append({"path": "MAX_NEW_REQUEST", "reason": "MAX_SINGLE_REQUEST_CEILING_EXCEEDED"})
    # OWNER_APPROVED 45 is a tolerance, not a bearer capability. No native
    # caller-specific exceptional authorization has been merged yet.
    # A naked --hard-stop-usd 45 --reserve-usd 0 is NOT an owner claim.
    # Fail closed here until a separately reviewed exact-work-id, source-HEAD,
    # actual-event proof is bound to the existing paid caller.
    if args.hard_stop_usd > OWNER_GLOBAL_TARGET_USD:
        errors.append({"path": "OWNER_EXCEPTIONAL_CAP",
                       "reason": "EXCEPTIONAL_45_NATIVE_SOURCE_CAPABILITY_REQUIRED"})
    effective_hard_stop = min(args.hard_stop_usd, OWNER_GLOBAL_HARD_STOP_USD)
    # Only an explicitly reviewed 45-cap caller can use the exceptional
    # USD5 tolerance; normal callers must retain USD4 minimum headroom.
    effective_reserve = (max(args.reserve_usd, OWNER_GLOBAL_RESERVE_USD)
                         if args.hard_stop_usd == OWNER_GLOBAL_TARGET_USD
                         else args.reserve_usd)
    exposure_lower = total + pending_low if total is not None else None
    exposure_upper = total + pending_high + new_upper if total is not None else None
    remaining = effective_hard_stop - exposure_upper if exposure_upper is not None else None
    owner_remaining = OWNER_GLOBAL_HARD_STOP_USD - exposure_upper if exposure_upper is not None else None
    normal_remaining = OWNER_GLOBAL_TARGET_USD - exposure_upper if exposure_upper is not None else None
    status = ("BLOCKED" if errors or remaining is None or owner_remaining is None
              or remaining < effective_reserve or owner_remaining < 0 else "PASS")
    result = {
        "status": status,
        "month": now.strftime("%Y-%m"),
        "receipts": receipts,
        "repriced_api_receipts": repriced_api_receipts,
        "cost_basis": "CURRENT_GATEWAY_PRICING_FOR_TOKENIZED_OPENAI_RECEIPTS_ELSE_RECORDED_COST",
        "spent_usd": round(total, 8) if total is not None else None,
        "remaining_usd": round(remaining, 8) if remaining is not None else None,
        "requested_hard_stop_usd": args.hard_stop_usd,
        "effective_hard_stop_usd": effective_hard_stop,
        "owner_global_hard_stop_usd": OWNER_GLOBAL_HARD_STOP_USD,
        "owner_global_reserve_usd": OWNER_GLOBAL_RESERVE_USD,
        "owner_normal_target_usd": OWNER_GLOBAL_TARGET_USD,
        "pending_liability_count": pending_count,
        "pending_liability_lower_usd": round(pending_low, 8),
        "pending_liability_upper_usd": round(pending_high, 8),
        "new_request_reserved_upper_usd": round(new_upper, 8),
        "exposure_range_min_usd": round(exposure_lower, 8) if exposure_lower is not None else None,
        "exposure_range_max_usd": round(exposure_upper, 8) if exposure_upper is not None else None,
        "normal_remaining_usd": round(normal_remaining, 8) if normal_remaining is not None else None,
        "approval_quote": quoted,
        "owner_global_remaining_usd_after_risk": round(owner_remaining, 8) if owner_remaining is not None else None,
        "owner_remaining_usd": round(owner_remaining, 8) if owner_remaining is not None else None,
        "reserve_usd": effective_reserve,
        "malformed_cost_receipts": [e["path"] for e in errors],
        "cost_evidence_errors": errors,
        "missing_optional_roots": missing_optional_roots,
        "fail_closed": True,
    }
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    if status != "PASS":
        raise SystemExit("monthly_api_cost_guard_blocked")


if __name__ == "__main__":
    main()
