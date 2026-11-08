#!/usr/bin/env python3
"""Deterministic, source-only observer for original Alpha Precision Harvest L01-L08.

This observer is NOT a research executor, dispatcher, agent, scientific reviewer,
GitHub biller, workflow trigger, or merge authority. It emits a no-churn, value-free
owner-handoff snapshot to an already scheduled governance workflow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "04_RESEARCH_LAB/external_specialist_dissection/2026-11-07__ALPHA_RESEARCH_PRECISION_PARALLEL_LANES_v1.json"
DEFAULT_ROUTING = ROOT / "04_RESEARCH_LAB/external_specialist_dissection/alpha_precision_20261107/OWNER_ROUTING_V1.json"
DEFAULT_BUDGET = ROOT / "research/framework_learning/resource_budget/LATEST.json"
DEFAULT_OUTPUT = ROOT / "00_ARCHIVE_CONTROL/research_governance_v1/alpha_precision_harvest_v1/STATE.json"
VALID_STATUSES = {"PLANNED", "RUNNING", "COMPLETE_VERIFIED", "FAILED_EVIDENCED", "BLOCKED", "NOT_EXECUTED"}
PRIVATE_FIELDS = {"run_evidence", "source_urls", "original_alpha_pr", "original_pr_head_sha"}

def _hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def observe(manifest: dict, routes: dict, budget: dict) -> dict:
    if manifest.get("contract") != "RESEARCH_PARALLEL_LANES_V1":
        raise ValueError("invalid research contract")
    if routes.get("contract") != "ALPHA_PRECISION_EXISTING_OWNER_ROUTING_V1":
        raise ValueError("invalid existing-owner routing contract")
    if not (manifest.get("approved_execution") is True
            and manifest.get("no_new_scheduler") is True
            and manifest.get("no_new_agent_identity") is True
            and manifest.get("no_trading_authority") is True
            and routes.get("automatic_execution_authorized") is False
            and routes.get("no_new_scheduler") is True
            and routes.get("no_model_spend") is True):
        raise ValueError("research or owner authority is not fail-closed")
    lanes = manifest.get("lanes")
    bindings = routes.get("lanes")
    if not isinstance(lanes, list) or not isinstance(bindings, list) or len(lanes) != 8 or len(bindings) != 8:
        raise ValueError("expected exactly eight bound original lanes")
    ids = [lane.get("id") for lane in lanes]
    route_ids = [lane.get("id") for lane in bindings]
    if len(set(ids)) != 8 or len(set(route_ids)) != 8 or set(ids) != set(route_ids):
        raise ValueError("lane/owner routing mismatch")
    by_id = {row["id"]: row for row in bindings}
    public_budget = budget.get("github_actions", {})
    budget_attested = (
        budget.get("billing_hard_stop_verified") is True
        and isinstance(public_budget, dict)
        and public_budget.get("status") == "VERIFIED"
        and public_budget.get("usage") is not None
    )
    decisions = []
    for lane in lanes:
        lid, status, kind = lane["id"], lane.get("status"), lane.get("executor_kind")
        if status not in VALID_STATUSES or kind not in {"READ_ONLY_TOOL", "GITHUB_JOB", "EXISTING_AI_AGENT"}:
            raise ValueError("invalid original lane status or executor")
        r = by_id[lid]
        if not (r.get("owner_class") and r.get("activation_evidence")
                and r.get("next_owner_action") and r.get("gate_family")):
            raise ValueError("incomplete existing owner route")
        if status == "BLOCKED":
            gate = "OWNER_BLOCKED_WAIT_OBJECTIVE_REENTRY"
        elif status == "FAILED_EVIDENCED":
            gate = "OWNER_REPAIR_FROM_NATIVE_FAILURE"
        elif status == "COMPLETE_VERIFIED":
            gate = "VERIFY_NATIVE_RECEIPT_AND_SCIENCE_INDEPENDENTLY"
        elif status == "RUNNING":
            gate = "ORIGINAL_OWNER_RESEARCH_IN_PROGRESS_NO_JOB_ATTESTED"
        elif kind == "GITHUB_JOB" and not budget_attested:
            gate = "GITHUB_ACTIONS_ACCOUNT_USAGE_UNKNOWN_NO_JOB_DISPATCH"
        elif kind == "GITHUB_JOB":
            gate = "ORIGINAL_OWNER_MUST_AUTHORIZE_EXACT_JOB_AND_SOURCE"
        elif kind == "EXISTING_AI_AGENT":
            gate = "ORIGINAL_OWNER_MUST_PROVE_EXISTING_AGENT_RUN_AUTHORITY"
        else:
            gate = "PUBLIC_SOURCE_AND_FIRST_KNOWN_REQUIRED"
        decisions.append({
            "id": lid, "observed_lane_status": status, "owner_class": r["owner_class"],
            "evidence_needed": r["activation_evidence"], "next_owner_action": r["next_owner_action"],
            "action_gate": gate, "automatic_dispatch": False,
            "science_admitted": False, "actual_job_observed_by_this_observer": False,
        })
    substantive = {
        "contract": "ALPHA_PRECISION_ORIGINAL_OWNER_OBSERVATION_V1",
        "authority": "READ_ONLY_HANDOFF_NOT_EXECUTOR",
        "mission_id": manifest["mission_id"],
        "original_research_owner": routes["research_owner"],
        "scientific_owner": routes["science_owner"],
        "supervisor_owner": routes["supervisor_owner"],
        "source_eligibility": manifest.get("source_eligibility", "UNKNOWN"),
        "source_preflight": manifest.get("serial_preflight", {}).get("status", "UNKNOWN"),
        "github_actions_account_usage": "VERIFIED" if budget_attested else "UNKNOWN_OR_UNATTESTED",
        "lanes": decisions,
        "observed_source_fingerprint": _hash({"manifest": manifest, "routes": routes, "budget_gate": budget_attested}),
        "permitted_automatic_actions": ["READ_EXISTING_PUBLIC_MANIFEST", "WRITE_DEDUPED_OBSERVATION"],
        "paid_api_authorized": False,
        "github_job_dispatch_authorized": False,
        "independent_scientific_promotion": False,
        "portfolio_or_trade_authority": False,
    }
    substantive["fingerprint"] = _hash(substantive)
    return substantive

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--routing", type=Path, default=DEFAULT_ROUTING)
    parser.add_argument("--budget", type=Path, default=DEFAULT_BUDGET)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    a = parser.parse_args()
    def load(p: Path) -> dict:
        return json.loads(p.read_text(encoding="utf-8"))
    report = observe(load(a.manifest), load(a.routing), load(a.budget))
    body = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    a.output.parent.mkdir(parents=True, exist_ok=True)
    changed = not a.output.exists() or a.output.read_text(encoding="utf-8") != body
    if changed:
        a.output.write_text(body, encoding="utf-8")
    print(json.dumps({"contract": report["contract"], "changed": changed,
                      "fingerprint": report["fingerprint"],
                      "github_job_dispatch_authorized": False,
                      "lanes_observed": len(report["lanes"])}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
