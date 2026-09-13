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
    args = parser.parse_args()
    if not finite_nonnegative(args.hard_stop_usd) or not finite_nonnegative(args.reserve_usd):
        parser.error("hard stop and reserve must be finite nonnegative amounts")

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
    remaining = args.hard_stop_usd - total if total is not None else None
    status = "BLOCKED" if errors or remaining is None or remaining <= args.reserve_usd else "PASS"
    result = {
        "status": status,
        "month": now.strftime("%Y-%m"),
        "receipts": receipts,
        "repriced_api_receipts": repriced_api_receipts,
        "cost_basis": "CURRENT_GATEWAY_PRICING_FOR_TOKENIZED_OPENAI_RECEIPTS_ELSE_RECORDED_COST",
        "spent_usd": round(total, 8) if total is not None else None,
        "remaining_usd": round(remaining, 8) if remaining is not None else None,
        "reserve_usd": args.reserve_usd,
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
