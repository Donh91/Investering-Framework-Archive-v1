#!/usr/bin/env python3
"""Validate the Analysis-to-Action Translation Audit control package."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]


def load(name: str):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> int:
    checks = 0
    owner = load("OWNER_BINDING_AND_PROPOSITION_v1.json")
    schema_v1 = load("TRANSLATION_ROW_SCHEMA_v1.json")
    schema_v2 = load("TRANSLATION_ROW_SCHEMA_v2_PROSPECTIVE.json")
    rows = load("SOURCE_ROWS_W28_W31_v1.json")
    capture_v1 = load("PROSPECTIVE_CAPTURE_CONTRACT_v1.json")
    capture_v2 = load("PROSPECTIVE_CAPTURE_CONTRACT_v2.json")
    definitions = load("AATA_PROSPECTIVE_DEFINITIONS_v1.json")
    audit_receipt = load(
        "blind_audits/2026-07-31__claude-stage1-data-blocked/"
        "AATA_CLAUDE_STAGE1_AUDIT_RECEIPT_v1.json"
    )

    checks += 1
    if owner["new_active_test"] or owner["new_engine"] or owner["new_score"]:
        fail("AATA must not create an active test, engine or score")

    checks += 1
    if owner["economic_execution_allowed"] or owner["final_holdout_opened"]:
        fail("Economic execution and final holdout must remain locked")

    checks += 1
    row_ids = [row["row_id"] for row in rows["rows"]]
    if len(row_ids) != len(set(row_ids)) or len(row_ids) != 4:
        fail("Expected four unique W28-W31 source rows")

    checks += 1
    weeks = [row["week"] for row in rows["rows"]]
    if weeks != ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]:
        fail("Week order or coverage changed")

    checks += 1
    for row in rows["rows"]:
        required = set(schema_v1["required"])
        if not required.issubset(row):
            fail(f"Missing schema fields in {row['row_id']}")
        if row["temporal_status"].startswith("BLOCKED") and row["outcome"]["status"] != "HISTORICAL_CONTEXT_ONLY":
            fail(f"Blocked row counted beyond context: {row['row_id']}")
        if any(row["authority"].values()):
            fail(f"Forbidden authority in {row['row_id']}")
        for key in ("master_monday_path", "forecast_ledger_path"):
            path = row["source"].get(key)
            if path and not (REPO / path).exists():
                fail(f"Referenced owner path missing: {path}")

    checks += 1
    w30 = next(row for row in rows["rows"] if row["week"] == "2026-W30")
    if w30["outcome"]["status"] != "OWNER_AUDIT_IMPORTED_ECONOMIC_RESCORING_LOCKED":
        fail("W30 owner audit boundary changed")
    if w30["outcome"]["existing_owner_audit"]["leadership"] != "MISS":
        fail("W30 owner leadership label changed")

    checks += 1
    w31 = next(row for row in rows["rows"] if row["week"] == "2026-W31")
    if w31["outcome"]["status"] != "PENDING_HORIZON_MATURITY_AND_OWNER_JOIN":
        fail("W31 must remain pending")
    if any(w31["outcome"][key] is not None for key in (
        "analysis_result",
        "price_translation_result",
        "action_policy_result",
        "timing_result",
        "utility_metrics",
    )):
        fail("W31 cannot be scored during Stage 1 remediation")

    checks += 1
    required_blocks = set(capture_v1["required_separation"])
    if required_blocks != {"analysis_block", "operational_translation_block"}:
        fail("Historical v1 separation changed")

    checks += 1
    if any(capture_v1["authority"].values()):
        fail("Historical capture contract has forbidden authority")

    checks += 1
    if rows["summary"]["new_economic_scores"] != 0:
        fail("No new economic scores allowed")

    checks += 1
    if definitions["effective_from_week"] != "2026-W32" or definitions["retroactive_application"] is not False:
        fail("Prospective definitions must begin at W32 without retroactive application")

    checks += 1
    expected_dimensions = {"RELATIVE_STRENGTH", "ABSOLUTE_PERFORMANCE", "ROTATION"}
    if set(definitions["leadership"]["dimensions"]) != expected_dimensions:
        fail("Leadership dimensions changed")
    if definitions["leadership"]["missing_rule"] != "BLOCKED":
        fail("Undefined leadership must fail closed")

    checks += 1
    action = definitions["action_policy"]
    if action["primary_counterfactual"] != "FIRST_VALID_PERMISSION":
        fail("Primary action counterfactual changed")
    if action["null_counterfactual"] != "SOURCE_ANALYSIS_WITH_NO_ACTION":
        fail("Null action counterfactual changed")
    if action["missing_benchmark_rule"] != "BLOCKED":
        fail("Missing action benchmark must fail closed")

    checks += 1
    cluster = definitions["dependency_clusters"]["known_seed_cluster"]
    if cluster["cluster_id"] != "ETHBTC_DEPENDENCY_CLUSTER" or cluster["maximum_divergence_count"] != 1:
        fail("ETHBTC dependency de-duplication changed")

    checks += 1
    review = definitions["interim_review"]
    if review["trigger_valid_rows"] != 6 or review["mandatory"] is not True:
        fail("Six-row interim review must remain mandatory")

    checks += 1
    if capture_v2["effective_from_week"] != "2026-W32":
        fail("Capture v2 effective week changed")
    if capture_v2["does_not_rewrite"] != ["2026-W28", "2026-W29", "2026-W30", "2026-W31"]:
        fail("Historical non-rewrite boundary changed")
    if any(capture_v2["authority"].values()):
        fail("Capture v2 has forbidden authority")

    checks += 1
    required_action_fields = {
        "btc_permission",
        "alt_permission",
        "primary_counterfactual",
        "null_counterfactual",
    }
    if not required_action_fields.issubset(
        set(capture_v2["required_separation"]["action_block"]["required"])
    ):
        fail("Capture v2 does not separate permissions and baselines")

    checks += 1
    if schema_v2["$id"] != "ANALYSIS_TO_ACTION_TRANSLATION_ROW_SCHEMA_v2_PROSPECTIVE":
        fail("Prospective schema identity changed")
    if schema_v2["properties"]["week"]["pattern"] != r"^\d{4}-W(0[1-9]|[1-4][0-9]|5[0-3])$":
        fail("Prospective week pattern changed")

    checks += 1
    authority_props = schema_v2["properties"]["authority"]["properties"]
    if any(value.get("const") is not False for value in authority_props.values()):
        fail("Prospective schema authority must remain false")

    checks += 1
    if audit_receipt["verdict"] != "DATA_BLOCKED":
        fail("Claude Stage 1 aggregate verdict must remain DATA_BLOCKED")
    if audit_receipt["governance_ruling"]["stage_2_allowed"] is not False:
        fail("Stage 2 must remain blocked")
    if audit_receipt["governance_ruling"]["new_economic_scores"] != 0:
        fail("Audit receipt cannot claim economic scores")

    result = {
        "status": "PASS",
        "checks": checks,
        "rows": len(rows["rows"]),
        "claude_stage1_verdict": audit_receipt["verdict"],
        "stage_2_allowed": False,
        "new_economic_scores": 0,
        "final_holdout_opened": False,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        raise
