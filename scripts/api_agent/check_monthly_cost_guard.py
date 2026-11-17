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

# Owner explicit interactive approval 2026-11-13: account-wide USD50 per month
# with protected USD4 headroom. Existing caller-specific USD40 or lower caps
# and original per-task USD3 single-request limits remain binding.
# Legacy caller-specific smaller caps/reserves remain binding; this code never
# grants a paid POST or lowers a lane's independent ceiling.
OWNER_GLOBAL_TARGET_USD = 50.0
OWNER_GLOBAL_HARD_STOP_USD = 100.0
OWNER_GLOBAL_RESERVE_USD = 4.0  # Routine paths retain existing protected headroom.
OWNER_SINGLE_REQUEST_CAP_USD = 3.0
# Previous source-bound liabilities were provider-reconciled against private
# evidence, without adding account billing amounts to the public Archive.
# A new unresolved POST must still carry a bounded live ledger row; releasing
# future reservations requires separate independent provider-settlement evidence.
UNRESOLVED_NATIVE_POST_FLOOR_USD = {}
PROVIDER_SETTLEMENT_EVIDENCE = {
    "repository": "Donh91/Investering-AI-Audit-Bridge",
    "commit_sha": "6a916cc41ef351926349736d0611d160f9ff700f",
    "path": "reports/claude/automated/2026/11/CLAUDE-API-BUDGET-PROVIDER-RECONCILIATION-20261115T001000Z/evidence/openai_platform_readback_20261115T0007CPH.png",
    "bytes": 451083,
    "git_blob_sha": "d7ceee216b98a7daf7852963ef4ecbf47ddad691",
    "sha256": "fb6ba8b50b356a9a48c05915578e77fc16cca3af08694436cc57f4f4335598c8",
    "source_contract_id": "OWNER_OPENAI_PLATFORM_BILLING_READBACK_v1",
    "captured_at_local": "2026-11-15T00:07 Europe/Copenhagen (minute precision)",
    "committed_at_utc": "2026-11-14T23:13:55Z",
    "schema": "image/png; owner recording frames manually reviewed",
    "completeness": "NOVEMBER_MTD_ACCOUNT_AGGREGATE_ONLY_NOT_PER_REQUEST",
    "coverage_assertion": "PUBLIC_ESTIMATED_RECEIPTS_AT_CAPTURE_EXCEEDED_PRIVATE_PROVIDER_ACCOUNT_TOTAL",
    "coverage_authority": "INDEPENDENT_CLAUDE_RECONCILIATION_6885728883",
    "coverage_scope": "NATIVE_POST_IDS_ONLY_ASTRA_RESERVATIONS_RETAINED",
}
SETTLED_NATIVE_POST_IDS = {"41870364609", "41949497953", "42204120988"}
# The consumed Nov 13 Astra one-shots have no receipt in the guard receipt root
# and were not visible in the private provider aggregate at capture. Their
# pre-HTTP reservations stay counted (and may not silently disappear from the
# canonical ledger) until per-model provider evidence settles them (WO-5).
SETTLED_ASTRA_WORK_IDS: set[str] = set()
RETAINED_ASTRA_RESERVATION_WORK_IDS = {
    "ASTRA-HIGH-TASK2-SCIENTIFIC-20261113-ONE",
    "ASTRA-HIGH-TASK2-ALL-CN-HISTORICAL-20261113-ONE",
    "ASTRA-HIGH-MAEVE-TASK2-PREP-20261117-ONE",
}
# Owner-present exceptional Astra program, audited under native high-impact PR.
# This is a research-only allocation, not a fallback/authority for other callers.
OWNER_ASTRA_PROGRAM_WORK = {
    "ASTRA-HIGH-S1-VNEXT-ARCHITECTURE-20261116-ONE": 1156,
    "ASTRA-HIGH-COMPASS-TOTAL-AUDIT-20261116-ONE": 1827,
    "ASTRA-HIGH-COMPASS-EDGE-SCIENCE-20261116-ONE": 1596,
    "ASTRA-HIGH-COMPASS-EARLY-WARNING-CYCLE-20261116-ONE": 1553,
    "ASTRA-HIGH-ALPHA-LAB-PAPER-EDGE-20261116-ONE": 1340,
    "ASTRA-HIGH-MAEVE-TASK2-PREP-20261117-ONE": 937,
}
MAEVE_WORK_ID = "ASTRA-HIGH-MAEVE-TASK2-PREP-20261117-ONE"
MAEVE_AUTHORIZATION = "OWNER_INTERACTIVE_2026-11-17_ASTRA_MAEVE_TASK2_PREP_V1_ONE"
MAEVE_MISSION_BLOB = "9c44bca23d8825c31afbdb1d62ae621285e9354a"
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
            or ("normal_budget_usd" in value and
                value["normal_budget_usd"] != OWNER_GLOBAL_TARGET_USD)
            or ("absolute_budget_usd" in value and
                value["absolute_budget_usd"] != OWNER_GLOBAL_HARD_STOP_USD)
            or value.get("contract") != "API_PENDING_BILLING_RISK_V1"
            or value.get("no_retry_original_ids") is not True
            or value.get("requires_reconciliation_before_releasing_reserve") is not True
            or not isinstance(value.get("unresolved"), list)):
        raise ValueError("LIABILITY_LEDGER_CONTRACT_INVALID")
    # Canonical released liabilities need immutable, private-source evidence;
    # test fixtures with future unknown POSTs may omit the settlement block.
    settlement_bound = path.resolve() == CANONICAL_LIABILITY_LEDGER.resolve() or "settled" in value
    if settlement_bound:
        if value.get("provider_settlement_evidence") != PROVIDER_SETTLEMENT_EVIDENCE:
            raise ValueError("PROVIDER_SETTLEMENT_EVIDENCE_INVALID")
        settled = value.get("settled")
        if not isinstance(settled, list) or len(settled) != len(SETTLED_NATIVE_POST_IDS) + len(SETTLED_ASTRA_WORK_IDS):
            raise ValueError("PROVIDER_SETTLED_SET_INVALID")
        post_ids, work_ids = set(), set()
        for entry in settled:
            if not isinstance(entry, dict) or entry.get("status") != "PROVIDER_PERIOD_RECONCILED" or entry.get("no_retry") is not True or any(k in entry for k in ("lower_usd", "upper_usd", "amount_usd", "billed_usd")):
                raise ValueError("PROVIDER_SETTLED_ROW_INVALID")
            if entry.get("kind") == "NATIVE_POST":
                post_ids.add(entry.get("run_id"))
            elif entry.get("kind") == "ASTRA_PREHTTP_RESERVATION":
                work_ids.add(entry.get("work_id"))
            else:
                raise ValueError("PROVIDER_SETTLED_KIND_INVALID")
        if post_ids != SETTLED_NATIVE_POST_IDS or work_ids != SETTLED_ASTRA_WORK_IDS:
            raise ValueError("PROVIDER_SETTLED_ID_SET_MISMATCH")
        if any(row.get("run_id") in post_ids for row in value["unresolved"]) or any(row.get("work_id") in work_ids for row in value.get("owner_reservations", [])):
            raise ValueError("PROVIDER_SETTLED_REINTRODUCED_PENDING")
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
    # The explicitly owner-authorized one-shot Astra liability is reserved
    # BEFORE HTTP, even if the API response is lost or the Actions artifact
    # eventually expires. It stays in the global monthly exposure until an
    # independently reviewed native settlement removes it.
    reservations = value.get("owner_reservations", [])
    if not isinstance(reservations, list) or len(reservations) > 9:
        raise ValueError("OWNER_RESERVATION_LEDGER_INVALID")
    reserved_work_ids = set()
    for reservation in reservations:
        if (not isinstance(reservation, dict)
                or reservation.get("created_month_utc") != "2026-11"
                or reservation.get("status") != "OWNER_RESERVED_PREHTTP"
                or reservation.get("lower_usd") != 0
                or reservation.get("source") != ("https://github.com/Donh91/Investering-Framework-Archive-v1/issues/" + str(OWNER_ASTRA_PROGRAM_WORK.get(reservation.get("work_id"), 1596)))
                or reservation.get("one_paid_post_max") != 1
                or reservation.get("reconciliation_required") is not True):
            raise ValueError("ASTRA_OWNER_RESERVATION_UNVERIFIED")
        work = reservation.get("work_id")
        if work in reserved_work_ids:
            raise ValueError("DUPLICATE_OWNER_RESERVATION")
        reserved_work_ids.add(work)
        allowed = {
            "ASTRA-HIGH-TASK2-SCIENTIFIC-20261113-ONE": 3,
            "ASTRA-HIGH-TASK2-ALL-CN-HISTORICAL-20261113-ONE": 10,
            "ASTRA-HIGH-TASK2-REALDATA-V2-20261113-ONE": 10,
            "ASTRA-HIGH-TASK2-PUBLIC-W46W47-20261116-ONE": 10,
            "ASTRA-HIGH-S1-VNEXT-ARCHITECTURE-20261116-ONE": 10,
            "ASTRA-HIGH-COMPASS-TOTAL-AUDIT-20261116-ONE": 10,
            "ASTRA-HIGH-COMPASS-EDGE-SCIENCE-20261116-ONE": 10,
            "ASTRA-HIGH-COMPASS-EARLY-WARNING-CYCLE-20261116-ONE": 10,
            "ASTRA-HIGH-ALPHA-LAB-PAPER-EDGE-20261116-ONE": 10,
            MAEVE_WORK_ID: 10,
        }
        if work == MAEVE_WORK_ID and (
            reservation.get("authorization_id") != MAEVE_AUTHORIZATION
            or reservation.get("mission") != "ASTRA_MAEVE_TASK2_PREP_V1"
            or reservation.get("mission_blob") != MAEVE_MISSION_BLOB
        ):
            raise ValueError("MAEVE_ONE_USE_AUTHORIZATION_INVALID")
        if work not in allowed or reservation.get("upper_usd") != allowed[work]:
            raise ValueError("UNKNOWN_OWNER_RESERVED_MODEL_OR_COST")
        high += float(allowed[work])
    reservation_count = len(reservations)
    if settlement_bound and not RETAINED_ASTRA_RESERVATION_WORK_IDS <= reserved_work_ids:
        raise ValueError("RETAINED_ASTRA_RESERVATION_MISSING")
    missing = set(UNRESOLVED_NATIVE_POST_FLOOR_USD) - seen
    if missing:
        raise ValueError("KNOWN_UNSETTLED_NATIVE_POST_MISSING")
    for row in value["unresolved"]:
        floor = UNRESOLVED_NATIVE_POST_FLOOR_USD.get(row["run_id"])
        if floor is not None and float(row["upper_usd"]) < floor:
            raise ValueError("KNOWN_UNSETTLED_NATIVE_POST_UNDER_RESERVED")
    if not math.isfinite(high) or high > OWNER_GLOBAL_HARD_STOP_USD:
        raise ValueError("LIABILITY_TOTAL_INVALID")
    return low, high, len(seen) + reservation_count


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
    parser.add_argument("--owner-astra-program-work-id")
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
    # New owner-authorized exceptional program applies ONLY to source-whitelisted
    # one-shot IDs in the canonical ledger. The native owner issue event + claim
    # is separately enforced by each runner, not by this quote-only guard.
    approved_astra_id = args.owner_astra_program_work_id
    exceptional = (approved_astra_id in OWNER_ASTRA_PROGRAM_WORK
                   and args.hard_stop_usd == 100.0
                   and args.reserve_usd >= 4.0
                   and new_upper == 0.0)
    if approved_astra_id is not None:
        if not exceptional:
            errors.append({"path": "OWNER_ASTRA_PROGRAM",
                           "reason": "WORK_ID_OR_EXCEPTION_CAP_INVALID"})
        else:
            try:
                lr = json.loads(args.liability_ledger.read_text(encoding="utf-8"))
                exact = [r for r in lr.get("owner_reservations", [])
                         if r.get("work_id") == approved_astra_id
                         and r.get("upper_usd") == 10
                         and r.get("one_paid_post_max") == 1
                         and r.get("source") ==
                           "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/" +
                           str(OWNER_ASTRA_PROGRAM_WORK[approved_astra_id])]
                if len(exact) != 1:
                    raise ValueError("DISTINCT_OWNER_ASTRA_RESERVATION_REQUIRED")
            except (OSError, ValueError, TypeError, KeyError):
                errors.append({"path": "OWNER_ASTRA_PROGRAM",
                               "reason": "DISTINCT_OWNER_ASTRA_RESERVATION_REQUIRED"})
    # Prior normal 40/4 callers keep their independent cap. The five owner
    # exceptional reservations cannot silently consume routine budget, but
    # DO count against the one global hard stop and its protected USD4.
    normal_exception_hold = 0.0
    if not exceptional:
        try:
            valid = json.loads(args.liability_ledger.read_text(encoding="utf-8"))
            normal_exception_hold = sum(
                float(row.get("upper_usd", 0))
                for row in valid.get("owner_reservations", [])
                if row.get("work_id") in OWNER_ASTRA_PROGRAM_WORK
            )
        except (OSError, ValueError, TypeError):
            errors.append({"path": "OWNER_ASTRA_PROGRAM",
                           "reason": "NORMAL_EXCEPTION_HOLD_UNREADABLE"})
    # USD50 is the total authenticated owner-approved monthly envelope, NOT
    # independent authority to purchase a model call. Existing paid runners
    # must still enforce original owner-event, model, one-POST and lane rules.
    # A local CLI preview with a matching number is never release consent.
    if args.hard_stop_usd > OWNER_GLOBAL_TARGET_USD and not exceptional:
        errors.append({"path": "OWNER_EXCEPTIONAL_CAP",
                       "reason": "OWNER_GLOBAL_50_USD_CAP_EXCEEDED"})
    effective_hard_stop = min(args.hard_stop_usd, OWNER_GLOBAL_HARD_STOP_USD)
    # Existing small lane caps (e.g. CN 9.4/0.1) retain their LOCAL
    # reserve; USD4 remains protected at the GLOBAL ACCOUNT envelope.
    # All normal prior USD40 and new USD50 callers keep at least USD4
    # in their own source-bound admission as before.
    effective_reserve = (max(args.reserve_usd, OWNER_GLOBAL_RESERVE_USD)
                         if args.hard_stop_usd >= 40.0 else args.reserve_usd)
    exposure_lower = total + pending_low if total is not None else None
    exposure_upper = total + pending_high + new_upper if total is not None else None
    remaining = (effective_hard_stop - exposure_upper + normal_exception_hold
                 if exposure_upper is not None else None)
    owner_remaining = OWNER_GLOBAL_HARD_STOP_USD - exposure_upper if exposure_upper is not None else None
    normal_remaining = (OWNER_GLOBAL_TARGET_USD - exposure_upper + normal_exception_hold
                        if exposure_upper is not None else None)
    status = ("BLOCKED" if errors or remaining is None or owner_remaining is None
              or remaining <= effective_reserve  # the reserve is never spendable, as in the lane guard
              or owner_remaining < OWNER_GLOBAL_RESERVE_USD else "PASS")
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
