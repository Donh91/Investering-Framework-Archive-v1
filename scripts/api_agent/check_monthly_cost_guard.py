from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))
from api_agent.api_gateway import PRICES_PER_MILLION, estimate_cost
from api_agent import astra_mission_reservations_v1 as astra_missions
from api_agent import opaque_api_reservations_v1 as opaque_reservations
from lib.evidence_io import cost_receipt_identity, created_utc, finite_nonnegative, json_evidence_paths, load_evidence

# Owner explicit interactive approval 2026-11-13: account-wide USD50 per month
# with protected USD4 headroom. Existing caller-specific USD40 or lower caps
# and original per-task USD3 single-request limits remain binding.
# Legacy caller-specific smaller caps/reserves remain binding; this code never
# grants a paid POST or lowers a lane's independent ceiling.
OWNER_GLOBAL_TARGET_USD = 50.0
OWNER_GLOBAL_HARD_STOP_USD = 100.0  # Owner decision 2026-11-18; caller caps unchanged.
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
# Exact reviewed source evidence for consumed owner reservations. No inferred per-run USD.
OWNER_CONSUMED_ASTRA_EVIDENCE = {
    "ASTRA-HIGH-TASK2-SCIENTIFIC-20261113-ONE": {
        "owner_issue": 1596,
        "owner_trigger_comment_id": None,
        "owner_event": "workflow_dispatch",
        "owner_actor": "Donh91",
        "claim_comment_id": 6851822851,
        "run_id": "43419077122",
        "run_conclusion": "success",
        "artifact_id": "14033562358",
        "output_sha256": "d244b7f8a6293792fabbd7694bd9f85893f7c724ec7b6458af8c99acbef07709",
        "archive_pr": 2126,
        "completion_comment_id": 6852191726,
        "input_tokens": 17037,
        "output_tokens": 15497,
        "estimated_text_model_usd": 0.94522
    },
    "ASTRA-HIGH-TASK2-ALL-CN-HISTORICAL-20261113-ONE": {
        "owner_issue": 1596,
        "owner_trigger_comment_id": 6854781097,
        "owner_event": "issue_comment",
        "owner_actor": "Donh91",
        "claim_comment_id": 6854798355,
        "run_id": "43436726016",
        "run_conclusion": "success",
        "artifact_id": "14045101056",
        "output_sha256": "34c77a52cae0f45c78169d84d48506fcc096b11c5ca36e744d3965cca2c56eee",
        "archive_pr": 2126,
        "completion_comment_id": 6855239533,
        "input_tokens": 131489,
        "output_tokens": 38738,
        "estimated_text_model_usd": 3.25179
    },
    "ASTRA-HIGH-TASK2-PUBLIC-W46W47-20261116-ONE": {
        "owner_issue": 1596,
        "owner_trigger_comment_id": 6915834169,
        "owner_event": "issue_comment",
        "owner_actor": "Donh91",
        "claim_comment_id": 6915851510,
        "run_id": "43862850019",
        "run_conclusion": "success",
        "artifact_id": "14224547889",
        "output_sha256": "981ce1be3655a031810aba7c7f79044ed923b0c608d509ce54fa3bd9f3bce864",
        "archive_pr": 2195,
        "completion_comment_id": 6925700892,
        "input_tokens": 21561,
        "output_tokens": 12931,
        "estimated_text_model_usd": 0.86216
    },
    "ASTRA-HIGH-S1-VNEXT-ARCHITECTURE-20261116-ONE": {
        "owner_issue": 1156,
        "owner_trigger_comment_id": 6928271522,
        "owner_event": "issue_comment",
        "owner_actor": "Donh91",
        "claim_comment_id": 6928295238,
        "run_id": "43949496515",
        "run_conclusion": "success",
        "artifact_id": "14268215043",
        "output_sha256": "b20e7e940c2cdbb6f6dd4339193eb5295d2be41d4dde6bf9f37cb929c8506785",
        "archive_pr": 2204,
        "completion_comment_id": 6929489944,
        "input_tokens": 49007,
        "output_tokens": 18488,
        "estimated_text_model_usd": 1.41447
    },
    "ASTRA-HIGH-COMPASS-TOTAL-AUDIT-20261116-ONE": {
        "owner_issue": 1827,
        "owner_trigger_comment_id": 6928297034,
        "owner_event": "issue_comment",
        "owner_actor": "Donh91",
        "claim_comment_id": 6928319885,
        "run_id": "43949672635",
        "run_conclusion": "success",
        "artifact_id": "14267453073",
        "output_sha256": "cf072b3cf7f674e94522a85c7660bad309cd67c57dcb08f2b2ca35e7bffacc45",
        "archive_pr": 2204,
        "completion_comment_id": 6929491796,
        "input_tokens": 66483,
        "output_tokens": 19945,
        "estimated_text_model_usd": 1.66208
    },
    "ASTRA-HIGH-COMPASS-EDGE-SCIENCE-20261116-ONE": {
        "owner_issue": 1596,
        "owner_trigger_comment_id": 6928297698,
        "owner_event": "issue_comment",
        "owner_actor": "Donh91",
        "claim_comment_id": 6928325484,
        "run_id": "43949678137",
        "run_conclusion": "success",
        "artifact_id": "14268300941",
        "output_sha256": "201c1c6d5e50a67e49d10d406ffc49a436138fb47f7e6649116455fff3161b88",
        "archive_pr": 2204,
        "completion_comment_id": None,
        "input_tokens": 43877,
        "output_tokens": 19021,
        "estimated_text_model_usd": 1.38982
    },
    "ASTRA-HIGH-COMPASS-EARLY-WARNING-CYCLE-20261116-ONE": {
        "owner_issue": 1553,
        "owner_trigger_comment_id": 6928298418,
        "owner_event": "issue_comment",
        "owner_actor": "Donh91",
        "claim_comment_id": 6928316089,
        "run_id": "43949682325",
        "run_conclusion": "success",
        "artifact_id": "14266287659",
        "output_sha256": "c62b860b2359ef08b2a11573028767779a8ee8a08dcac9c0e16cd3793d0bb496",
        "archive_pr": 2204,
        "completion_comment_id": 6929493777,
        "input_tokens": 35520,
        "output_tokens": 11194,
        "estimated_text_model_usd": 0.9149
    },
    "ASTRA-HIGH-ALPHA-LAB-PAPER-EDGE-20261116-ONE": {
        "owner_issue": 1340,
        "owner_trigger_comment_id": 6928299330,
        "owner_event": "issue_comment",
        "owner_actor": "Donh91",
        "claim_comment_id": 6928321540,
        "run_id": "43949688570",
        "run_conclusion": "success",
        "artifact_id": "14268125488",
        "output_sha256": "a3c5880525057846dadf80ee90ac40cbfe6a59e8144c398f3323a3a49184a16b",
        "archive_pr": 2204,
        "completion_comment_id": 6929494783,
        "input_tokens": 31078,
        "output_tokens": 18424,
        "estimated_text_model_usd": 1.23198
    },
    "ASTRA-HIGH-MAEVE-TASK2-PREP-20261117-ONE": {
        "owner_issue": 937,
        "owner_trigger_comment_id": 6944827288,
        "owner_event": "issue_comment",
        "owner_actor": "Donh91",
        "claim_comment_id": 6944866063,
        "run_id": "44061041475",
        "run_conclusion": "success",
        "artifact_id": "14319116037",
        "output_sha256": "10bce9dc190b0a55065e971d6f71e04ae186799cba71170f2634e4b5f807d597",
        "archive_pr": 2204,
        "completion_comment_id": None,
        "input_tokens": 29614,
        "output_tokens": 12825,
        "estimated_text_model_usd": 0.93739
    }
}
OWNER_ASTRA_PROVIDER_PERIOD_SETTLEMENT = {
    "contract": "OWNER_ASTRA_PROVIDER_PERIOD_SETTLEMENT_20261118_V1",
    "source": "owner OpenAI usage dashboard + CSV export 2026-11-18",
    "screenshot_sha256": "db712eea88dc77b74e48ee2bd682d76c5aca51996a1d449794f13082a815f41b",
    "usage_csv_sha256": "0b5764bd0e7268425a3682c599a66bfa672b90c73086f7f7b75476d3b75fedf5",
    "observed_period_start": "2026-11-12",
    "observed_period_end": "2026-11-18",
    "capture_local": "2026-11-18 12:08 Europe/Copenhagen",
    "provider_period_spend_usd": 5.41,
    "settled_total_usd": 5.41,
    "amount_scope": "displayed aggregate for wider period; no per-request or per-model USD allocation; not a final invoice",
    "usage_model": "gpt-6-astra",
    "usage_by_day_utc": {
        "2026-11-13": [
            2,
            148526,
            54235
        ],
        "2026-11-16": [
            6,
            247526,
            100003
        ],
        "2026-11-17": [
            1,
            29614,
            12825
        ]
    },
    "usage_columns": [
        "requests",
        "input_tokens",
        "output_tokens"
    ],
    "native_estimated_total_usd": 12.60981,
    "accounting": "Count once in November upper exposure, conservatively max of observed wider-period dollars and native summed text estimates; no exact per-work billing claim. Native estimates are outside primary guard receipt root; any overlap remains conservative.",
    "no_replay": True
}
# No never-triggered entry in the nine-row census. Any future release needs a reviewed pin.
OWNER_NEVER_TRIGGERED_EVIDENCE: dict = {}
CONSUMED_STATUS = "CONSUMED_SETTLED_OWNER_PROVIDER_EVIDENCE"
RELEASED_STATUS = "RELEASED_NEVER_TRIGGERED"
ACTIVE_RESERVATION_STATUS = "OWNER_RESERVED_PREHTTP"
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
    if not isinstance(reservations, list) or len(reservations) > 10:
        raise ValueError("OWNER_RESERVATION_LEDGER_INVALID")
    reserved_work_ids = set()
    consumed_ids = set()
    active_count = 0
    for reservation in reservations:
        if (not isinstance(reservation, dict)
                or reservation.get("created_month_utc") != "2026-11"
                or reservation.get("status") not in (ACTIVE_RESERVATION_STATUS, CONSUMED_STATUS, RELEASED_STATUS)
                or reservation.get("lower_usd") != 0
                or reservation.get("source") != ("https://github.com/Donh91/Investering-Framework-Archive-v1/issues/" + str(OWNER_ASTRA_PROGRAM_WORK.get(reservation.get("work_id"), 1596)))
                or reservation.get("one_paid_post_max") != 1):
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
        status = reservation["status"]
        if status == CONSUMED_STATUS:
            if (work not in OWNER_CONSUMED_ASTRA_EVIDENCE
                    or reservation.get("native_settlement_evidence") != OWNER_CONSUMED_ASTRA_EVIDENCE[work]
                    or reservation.get("settlement_group") != OWNER_ASTRA_PROVIDER_PERIOD_SETTLEMENT["contract"]
                    or reservation.get("reconciliation_required") is not False
                    or reservation.get("no_retry") is not True):
                raise ValueError("ASTRA_CONSUMED_EVIDENCE_INVALID")
            consumed_ids.add(work)
        elif status == RELEASED_STATUS:
            if (work not in OWNER_NEVER_TRIGGERED_EVIDENCE
                    or reservation.get("native_settlement_evidence") != OWNER_NEVER_TRIGGERED_EVIDENCE[work]
                    or reservation.get("reconciliation_required") is not False
                    or reservation.get("no_retry") is not True):
                raise ValueError("ASTRA_NEVER_TRIGGERED_EVIDENCE_INVALID")
        else:
            if (work in OWNER_CONSUMED_ASTRA_EVIDENCE or work in OWNER_NEVER_TRIGGERED_EVIDENCE
                    or reservation.get("reconciliation_required") is not True):
                raise ValueError("ASTRA_ACTIVE_RESERVATION_INVALID")
            active_count += 1
            high += float(allowed[work])
    reservation_count = active_count
    if settlement_bound or consumed_ids or "owner_astra_provider_period_settlement" in value:
        if (consumed_ids != set(OWNER_CONSUMED_ASTRA_EVIDENCE)
                or value.get("owner_astra_provider_period_settlement") != OWNER_ASTRA_PROVIDER_PERIOD_SETTLEMENT):
            raise ValueError("ASTRA_PROVIDER_GROUP_EVIDENCE_INVALID")
    # Generic owner Astra missions (#1156): a separate append-only ledger key, each row bound to a reviewed mission.
    mission_high, mission_count, _ = astra_missions.mission_reservations(value, reserved_work_ids)
    high += mission_high
    reservation_count += mission_count
    # No exception offset: opaque liabilities count in full for all callers.
    opaque_high, opaque_count = opaque_reservations.pending_upper(value)
    high += opaque_high
    reservation_count += opaque_count
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


def settled_owner_cost_upper(path: Path, now: datetime) -> float:
    """One historical group provision; callers must first validate pending_risk."""
    value = json.loads(path.read_text(encoding="utf-8"))
    evidence = value.get("owner_astra_provider_period_settlement")
    _, provision = astra_missions.settlement_summary(value)
    upper = float(provision.get(now.strftime("%Y-%m"), 0))
    if evidence is not None:
        if evidence != OWNER_ASTRA_PROVIDER_PERIOD_SETTLEMENT:
            raise ValueError("ASTRA_PROVIDER_GROUP_EVIDENCE_INVALID")
        if (now.year, now.month) == (2026, 11):
            upper += max(evidence["provider_period_spend_usd"], evidence["native_estimated_total_usd"])
    return upper


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
    parser.add_argument("--owner-astra-mission-id")
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
    settled_owner_upper = 0.0
    settled_astra_count = 0
    try:
        pending_low, pending_high, pending_count = pending_risk(args.liability_ledger)
        settled_owner_upper = settled_owner_cost_upper(args.liability_ledger, now)
        settled_astra_count = len(astra_missions.settlement_summary(json.loads(args.liability_ledger.read_text(encoding="utf-8")))[0])
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
    historical_pr_audit = False
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
                         and r.get("status") == ACTIVE_RESERVATION_STATUS
                         and r.get("one_paid_post_max") == 1
                         and r.get("source") ==
                           "https://github.com/Donh91/Investering-Framework-Archive-v1/issues/" +
                           str(OWNER_ASTRA_PROGRAM_WORK[approved_astra_id])]
                if len(exact) != 1:
                    # The existing MAEVE PR preflight is a read-only check of the
                    # original packet. It must report an explicit consumed state,
                    # never PASS for a retired paid route. Actual issue-comment
                    # launches and local invocations remain blocked.
                    consumed = [r for r in lr.get("owner_reservations", [])
                                if r.get("work_id") == approved_astra_id
                                and r.get("status") == CONSUMED_STATUS
                                and r.get("native_settlement_evidence") == OWNER_CONSUMED_ASTRA_EVIDENCE.get(approved_astra_id)]
                    historical_pr_audit = (
                        not exact and len(consumed) == 1
                        and approved_astra_id == "ASTRA-HIGH-MAEVE-TASK2-PREP-20261117-ONE"
                        and args.liability_ledger.resolve() == CANONICAL_LIABILITY_LEDGER.resolve()
                        and os.environ.get("GITHUB_ACTIONS") == "true"
                        and os.environ.get("GITHUB_EVENT_NAME") == "pull_request"
                        and re.fullmatch(r"refs/pull/[0-9]+/merge", os.environ.get("GITHUB_REF", "")) is not None)
                    if not historical_pr_audit:
                        raise ValueError("DISTINCT_OWNER_ASTRA_RESERVATION_REQUIRED")
            except (OSError, ValueError, TypeError, KeyError):
                errors.append({"path": "OWNER_ASTRA_PROGRAM",
                               "reason": "DISTINCT_OWNER_ASTRA_RESERVATION_REQUIRED"})
    # Generic owner Astra mission (#1156): same exceptional shape, bound to exactly one mission reservation row.
    mission_id = args.owner_astra_mission_id
    mission_ok = False
    if mission_id is not None:
        try:
            if (approved_astra_id is not None or args.hard_stop_usd != OWNER_GLOBAL_HARD_STOP_USD
                    or args.reserve_usd < OWNER_GLOBAL_RESERVE_USD or new_upper != 0.0):
                raise ValueError("MISSION_EXCEPTION_SHAPE_INVALID")
            lr = json.loads(args.liability_ledger.read_text(encoding="utf-8"))
            exact = [r for r in lr.get(astra_missions.KEY, []) if isinstance(r, dict) and r.get("work_id") == mission_id]
            if (len(exact) != 1 or exact[0].get("status") != astra_missions.RESERVED
                    or astra_missions.mission_max_usd(mission_id) != exact[0].get("upper_usd")):
                raise ValueError("DISTINCT_OWNER_ASTRA_MISSION_RESERVATION_REQUIRED")
            mission_ok = True
        except (OSError, ValueError, TypeError, KeyError, AttributeError):
            errors.append({"path": "OWNER_ASTRA_MISSION",
                           "reason": "DISTINCT_OWNER_ASTRA_MISSION_RESERVATION_REQUIRED"})
    exceptional = exceptional or mission_ok
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
                and row.get("status") == ACTIVE_RESERVATION_STATUS
            ) + sum(float(row.get("upper_usd", 0)) for row in valid.get(astra_missions.KEY, [])
                    if row.get("status") != astra_missions.SETTLED)
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
    exposure_upper = total + pending_high + settled_owner_upper + new_upper if total is not None else None
    remaining = (effective_hard_stop - exposure_upper + normal_exception_hold
                 if exposure_upper is not None else None)
    owner_remaining = OWNER_GLOBAL_HARD_STOP_USD - exposure_upper if exposure_upper is not None else None
    normal_remaining = (OWNER_GLOBAL_TARGET_USD - exposure_upper + normal_exception_hold
                        if exposure_upper is not None else None)
    status = ("BLOCKED" if errors or remaining is None or owner_remaining is None
              or remaining <= effective_reserve  # the reserve is never spendable, as in the lane guard
              or owner_remaining < OWNER_GLOBAL_RESERVE_USD else "PASS")
    if status == "PASS" and historical_pr_audit:
        status = "CONSUMED_NO_POST"
    result = {
        "status": status,
        "historical_pr_audit_only": historical_pr_audit,
        "paid_authority": False,
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
        "settled_owner_cost_upper_usd": round(settled_owner_upper, 8),
        "settled_astra_mission_count": settled_astra_count,
        "pending_liability_count": pending_count,
        "pending_liability_lower_usd": round(pending_low, 8),
        "pending_liability_upper_usd": round(pending_high, 8),
        "new_request_reserved_upper_usd": round(new_upper, 8),
        "exposure_range_min_usd": round(exposure_lower, 8) if exposure_lower is not None else None,
        "exposure_range_max_usd": round(exposure_upper, 8) if exposure_upper is not None else None,
        "normal_remaining_usd": round(normal_remaining, 8) if normal_remaining is not None else None,
        "approval_quote": quoted,
        "owner_astra_mission_id": mission_id if mission_ok else None,
        "owner_global_remaining_usd_after_risk": round(owner_remaining, 8) if owner_remaining is not None else None,
        "owner_remaining_usd": round(owner_remaining, 8) if owner_remaining is not None else None,
        "reserve_usd": effective_reserve,
        "malformed_cost_receipts": [e["path"] for e in errors],
        "cost_evidence_errors": errors,
        "missing_optional_roots": missing_optional_roots,
        "fail_closed": True,
    }
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    if status not in ("PASS", "CONSUMED_NO_POST"):
        raise SystemExit("monthly_api_cost_guard_blocked")


if __name__ == "__main__":
    main()
