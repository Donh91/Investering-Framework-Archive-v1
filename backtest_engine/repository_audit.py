from __future__ import annotations

import json
from pathlib import Path

from .prospective import summarize_accumulation
from .shadow_scoreboard import score_shadow_period
from .source_resilience import summarize_live_dual_source


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_prospective_repository(
    *,
    receipt_dir: Path,
    policy_registry_path: Path,
    source_ledger_path: Path,
    source_contract_path: Path,
    shadow_ledger_path: Path,
) -> dict:
    policy_registry = _read_json(policy_registry_path)
    families = tuple(policy_registry["families"].keys())
    receipts = [_read_json(path) for path in sorted(receipt_dir.glob("*.json"))]
    receipt_summary = summarize_accumulation(receipts, policy_families=families)

    source_ledger = _read_json(source_ledger_path)
    source_contract = _read_json(source_contract_path)
    source_summary = summarize_live_dual_source(source_ledger.get("rows", []), source_contract)

    shadow_ledger = _read_json(shadow_ledger_path)
    shadow_summary = score_shadow_period(shadow_ledger.get("runs", []))

    blocking = []
    if receipt_summary["invalid_receipts"]:
        blocking.append("INVALID_RECEIPTS")
    if shadow_summary["invalid_runs"]:
        blocking.append("INVALID_SHADOW_RUNS")

    return {
        "engineering_status": "PASS_ACTIVE" if not blocking else "FAIL",
        "blocking": blocking,
        "prospective_receipts": receipt_summary,
        "live_direct_ethbtc": source_summary,
        "shadow_dual_run": shadow_summary,
        "actual_policy_replay_unlocked": receipt_summary["actual_policy_replay_unlocked"],
        "final_holdout_opened": False,
        "canonical_state_change": "NONE",
        "portfolio_action": "NONE",
    }
