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


def parse_created(value: dict) -> datetime | None:
    return created_utc(value)


def task_of(value: dict) -> str | None:
    task = value.get("task")
    if task:
        return str(task)
    if value.get("contract") == "RESEARCH_AUTOMATION_COST_RECEIPT_v1":
        return "RESEARCH_AUTOMATION"
    return None


def effective_cost(value: dict) -> tuple[float | None, bool, str | None]:
    recorded = value.get("estimated_cost_usd")
    if not finite_nonnegative(recorded):
        return None, False, "INVALID_COST_OR_TIMESTAMP"
    model = value.get("model")
    has_usage = "input_tokens" in value or "output_tokens" in value
    if model in PRICES_PER_MILLION or has_usage:
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
    parser.add_argument("--task", required=True)
    parser.add_argument("--cap-usd", type=float, required=True)
    parser.add_argument("--reserve-usd", type=float, default=0.1)
    args = parser.parse_args()
    if not finite_nonnegative(args.cap_usd) or not finite_nonnegative(args.reserve_usd):
        parser.error("cap and reserve must be finite nonnegative amounts")

    now = datetime.now(timezone.utc)
    spent = 0.0
    receipts = 0
    repriced_api_receipts = 0
    seen: dict[tuple, tuple] = {}
    errors = []
    if not args.receipt_root.is_dir():
        errors.append({"path": str(args.receipt_root), "reason": "RECEIPT_ROOT_UNAVAILABLE"})
    else:
        paths, scan_errors = json_evidence_paths(args.receipt_root)
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
            if task_of(value) != args.task:
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
                spent += cost
                receipts += 1
                repriced_api_receipts += int(repriced)
    if not math.isfinite(spent):
        errors.append({"path": str(args.receipt_root), "reason": "COST_TOTAL_NONFINITE"})
        spent = None
    remaining = args.cap_usd - spent if spent is not None else None
    status = "PASS" if not errors and remaining is not None and remaining > args.reserve_usd else "BLOCKED"
    print(json.dumps({
        "status": status,
        "task": args.task,
        "month": now.strftime("%Y-%m"),
        "receipts": receipts,
        "repriced_api_receipts": repriced_api_receipts,
        "cost_basis": "CURRENT_GATEWAY_PRICING_FOR_TOKENIZED_OPENAI_RECEIPTS_ELSE_RECORDED_COST",
        "spent_usd": round(spent, 8) if spent is not None else None,
        "cap_usd": args.cap_usd,
        "remaining_usd": round(remaining, 8) if remaining is not None else None,
        "reserve_usd": args.reserve_usd,
        "cost_evidence_errors": errors,
        "fail_closed": True,
    }, sort_keys=True, allow_nan=False))
    if status != "PASS":
        raise SystemExit("api_lane_budget_blocked")


if __name__ == "__main__":
    main()
