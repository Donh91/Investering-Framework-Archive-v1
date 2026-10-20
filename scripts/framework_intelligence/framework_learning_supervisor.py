#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path, default: Any = None):
    if not path.exists():
        return default
    return json.loads(path.read_text())


def write_json(path: Path, value: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def read_strategist_advisory(root: Path, now: datetime, *,
                            strategist_path: str = "research/framework_learning/strategist/LATEST.json") -> dict[str, Any]:
    """Verify advisory source bytes and authority, without dispatch authority.

    The initial producer may observe a prior brief. Finalization reuses these
    same checks after the current Strategist, without rerunning its inputs.
    """
    allowed = {"research/framework_learning/strategist/LATEST.json",
               "runtime/framework-learning-supervisor/strategist/LATEST.json"}
    if strategist_path not in allowed:
        raise ValueError("STRATEGIST_PATH_NOT_ALLOWLISTED")
    rel = strategist_path
    path = root / rel
    empty = {"status": "UNAVAILABLE", "reference": rel, "proposal_ids": [],
             "attention_codes": [], "grok_review_candidate_count": 0,
             "automatic_routing": False, "source_sha256": None}
    try:
        if (path.is_symlink() or not path.is_file() or path.resolve() != path.absolute()):
            return empty
        raw = path.read_bytes()
        if len(raw) > 2_000_000:
            return {**empty, "status": "INVALID"}
        packet = json.loads(raw)
        if (not isinstance(packet, dict) or
                packet.get("contract") != "FRAMEWORK_STRATEGIST_BRIEF_v1" or
                packet.get("owner") != "EXISTING_FRAMEWORK_LEARNING_SUPERVISOR"):
            return {**empty, "status": "INVALID"}
        authority = packet.get("authority")
        prohibited = ("canonical_effect", "portfolio_execution", "autonomous_grok_request",
                      "autonomous_api_payment", "autonomous_merge", "new_queue")
        if (not isinstance(authority, dict) or any(authority.get(key) is not False for key in prohibited)):
            return {**empty, "status": "AUTHORITY_VIOLATION"}
        generated = packet.get("generated_at_utc")
        if not isinstance(generated, str) or not generated.endswith("Z"):
            return {**empty, "status": "INVALID"}
        stamp = datetime.fromisoformat(generated.replace("Z", "+00:00"))
        elapsed = (now - stamp).total_seconds()
        if elapsed < -900 or elapsed > 48 * 3600:
            return {**empty, "status": "STALE"}
        if packet.get("input_status") != "CURRENT":
            return {**empty, "status": "DEGRADED"}
        receipts = packet.get("source_receipts")
        if not isinstance(receipts, dict) or not receipts:
            return {**empty, "status": "INVALID"}
        # The producer's receipt paths are untrusted input; a malicious
        # previous advisory must not induce arbitrary local file reads.
        expected = {
            "strategic_intent": "00_FMOS/framework_strategist/STRATEGIC_INTENT_v1.json",
            "learning_memory": "research/framework_learning/LATEST_LEARNING_MEMORY.json",
            "weekly_delta": "research/framework_learning/LATEST_WEEKLY_LEARNING_DELTA.json",
            "self_improvement": "research/framework_learning/LATEST_SELF_IMPROVEMENT_V1.json",
            "health": "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
            "unconsumed": "research/framework_learning/LATEST_UNCONSUMED_INFORMATION.json",
            "staleness": "research/framework_learning/LATEST_METHOD_STALENESS_REGISTER.json",
            "weekly_forensics": "research/framework_learning/weekly_forensics/LATEST.json",
            "resource_budget": "research/framework_learning/resource_budget/LATEST.json",
        }
        optional = {"weekly_forensics", "resource_budget"}
        if set(receipts) != set(expected):
            return {**empty, "status": "INVALID"}
        for name, relative in expected.items():
            value = receipts[name]
            if not isinstance(value, dict) or value.get("path") != relative:
                return {**empty, "status": "INVALID"}
            if name in optional and value.get("status") != "CURRENT":
                # Explicitly optional, never used for a finding in this state.
                continue
            if value.get("status") != "CURRENT":
                return {**empty, "status": "SOURCE_MOVED"}
            original = root / relative
            if (not original.is_file() or original.is_symlink()
                    or original.resolve() != original.absolute()
                    or root.resolve() not in original.resolve().parents):
                return {**empty, "status": "SOURCE_MOVED"}
            if hashlib.sha256(original.read_bytes()).hexdigest() != value.get("sha256"):
                return {**empty, "status": "SOURCE_MOVED"}
        proposals = packet.get("proposals")
        if (not isinstance(proposals, list) or len(proposals) > 3
                or any(not isinstance(p, dict) or p.get("dispatch_allowed") is not False
                       or p.get("automatic_grok_call") is not False
                       or p.get("automatic_market_change") is not False
                       for p in proposals)):
            return {**empty, "status": "AUTHORITY_VIOLATION"}
        if any(not isinstance(p.get("id"), str) or not isinstance(p.get("code"), str)
               for p in proposals):
            return {**empty, "status": "INVALID"}
        return {"status": "ADVISORY_PREVIOUS_EVIDENCE", "reference": rel,
                "source_generated_at_utc": generated,
                "proposal_ids": [p["id"] for p in proposals],
                "attention_codes": [p["code"] for p in proposals],
                "grok_review_candidate_count": sum(
                    p.get("routing") == "GROK_REVIEW_CANDIDATE" for p in proposals),
                "automatic_routing": False,
                "source_sha256": hashlib.sha256(raw).hexdigest()}
    except (OSError, ValueError, TypeError, UnicodeDecodeError):
        return {**empty, "status": "INVALID"}


def finalize_strategist_advisory(root: Path, output_root: str, now: datetime) -> dict[str, Any]:
    """Consume the current brief after producers finish, without regenerating inputs.

    Only the existing live Supervisor state is finalized. Earlier snapshots stay
    immutable producer-stage observations. Source hashes and authority are still
    checked by the same reader; SOURCE_MOVED is never converted into acceptance.
    """
    root = root.resolve()
    if output_root not in {"research/framework_learning", "runtime/framework-learning-supervisor"}:
        raise ValueError("SUPERVISOR_OUTPUT_NOT_ALLOWLISTED")
    target = root / output_root / "LATEST_SUPERVISOR_STATE.json"
    if (target.is_symlink() or not target.is_file()
            or target.resolve() != target.absolute()
            or len(target.read_bytes()) > 2_000_000):
        raise ValueError("SUPERVISOR_STATE_UNTRUSTED")
    original_state = target.read_bytes()
    state = json.loads(original_state)
    if (not isinstance(state, dict)
            or state.get("contract") != "FRAMEWORK_LEARNING_SUPERVISOR_STATE_v1"
            or state.get("authority") != "ORCHESTRATION_ONLY"
            or any(state.get(k) is not False for k in
                   ("canonical_effect", "portfolio_execution", "master_monday_live_influence"))):
        raise ValueError("SUPERVISOR_STATE_AUTHORITY_INVALID")
    generated = state.get("generated_at_utc")
    if not isinstance(generated, str) or not generated.endswith("Z"):
        raise ValueError("SUPERVISOR_STATE_TIME_INVALID")
    stamp = datetime.fromisoformat(generated.replace("Z", "+00:00"))
    age = (now - stamp).total_seconds()
    if age < 0 or age > 15 * 60:
        raise ValueError("SUPERVISOR_STATE_NOT_CURRENT_RUN")
    advisory = read_strategist_advisory(
        root, now, strategist_path=output_root + "/strategist/LATEST.json")
    if advisory["status"] == "ADVISORY_PREVIOUS_EVIDENCE":
        produced = datetime.fromisoformat(advisory["source_generated_at_utc"].replace("Z", "+00:00"))
        if produced < stamp or produced > now:
            advisory.update(status="PRODUCER_NOT_CURRENT_RUN", proposal_ids=[],
                            attention_codes=[], grok_review_candidate_count=0,
                            source_sha256=None)
        else:
            advisory["status"] = "ADVISORY_CURRENT_EVIDENCE"
    advisory["consumption_phase"] = "POST_PRODUCER_SOURCE_VERIFICATION"
    advisory["verified_at_utc"] = now.isoformat().replace("+00:00", "Z")
    state["strategist_advisory"] = advisory
    # A failed source/authority check publishes its honest rejection, not a
    # retained accepted proposal from the earlier producer stage.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent,
                                         prefix=".supervisor-finalize-", delete=False) as file:
            temporary = Path(file.name)
            json.dump(state, file, indent=2, sort_keys=True)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        if target.read_bytes() != original_state:
            raise ValueError("SUPERVISOR_STATE_MOVED_DURING_FINALIZATION")
        temporary.replace(target)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return advisory


def week_id(now: datetime):
    y, w, _ = now.isocalendar()
    return int(y), int(w), f"{int(y)}-W{int(w):02d}"


def admit_cross_domain_shadow_weekly(snapshot, expected_week):
    """Consume *reviewed main* Shadow Registry only, as optional advisory.

    A weekly PR candidate is NOT an accepted/merged source. Missing or stale
    report remains pending, never converted into profitable strategy evidence.
    This function cannot enqueue paid calls, orders or canonical signals.
    """
    pending = {
        "status": "PENDING_REVIEWED_WEEKLY_SNAPSHOT",
        "week": expected_week,
        "authority": "ADVISORY_ONLY",
        "automatic_model_calls": False,
        "portfolio_execution": False,
        "reason": "NO_CURRENT_REVIEWED_CROSS_DOMAIN_SHADOW_RECEIPT",
        "lanes": [],
    }
    if not isinstance(snapshot, dict) or snapshot.get("contract") != "SHADOW_WEEKLY_RELEVANCE_SNAPSHOT_v1":
        return pending
    if snapshot.get("authority") != "RESEARCH_ONLY_NON_CANONICAL" or snapshot.get("portfolio_execution") is not False:
        return {**pending, "reason": "INVALID_REGISTRY_AUTHORITY"}
    if snapshot.get("week") != expected_week:
        return {**pending, "reason": "WEEKLY_REVIEW_NOT_MERGED_OR_STALE"}
    review = snapshot.get("cross_domain_review")
    if not isinstance(review, dict) or review.get("contract") != "SHADOW_CROSS_DOMAIN_WEEKLY_REVIEW_v1":
        return {**pending, "reason": "CROSS_DOMAIN_REVIEW_NOT_IN_MERGED_SNAPSHOT"}
    cost = review.get("cost_and_execution")
    if (review.get("week") != expected_week or
        review.get("authority") != "RESEARCH_ONLY_NON_CANONICAL" or
        not isinstance(cost, dict) or
        any(cost.get(x) != 0 for x in (
            "external_llm_calls", "incremental_paid_api_usd",
            "incremental_provider_calls", "new_schedulers"
        )) or
        any(cost.get(x) is not False for x in (
            "automatic_execution", "automatic_market_rule_change",
            "automatic_model_promotion", "wallet_signing"
        ))):
        return {**pending, "reason": "INVALID_COST_OR_AUTHORITY_BOUNDARY"}
    lanes = review.get("lanes")
    if not isinstance(lanes, list) or [r.get("lane_id") for r in lanes if isinstance(r, dict)] != [
        "COMPASS", "AUTO_TRADING", "ALPHA_LAB"
    ] or len(lanes) != 3:
        return {**pending, "reason": "INVALID_CROSS_DOMAIN_LANES"}
    if any(r.get("scientific_edge") != "UNPROVEN" or
           r.get("paper_or_live_trading_authorized") is not False for r in lanes):
        return {**pending, "reason": "UNAPPROVED_TRADING_OR_EDGE_PROMOTION"}
    # Only compact source status/owner/research task; never expose payload,
    # holdings, addresses, market data or inferred trader identity.
    return {
        "status": "WEEKLY_RESEARCH_ADVISORY_ONLY",
        "week": expected_week,
        "authority": "ADVISORY_ONLY",
        "automatic_model_calls": False,
        "portfolio_execution": False,
        "reason": "OWNER_REVIEW_AND_INDEPENDENT_ACCEPTANCE_REQUIRED",
        "lanes": [
            {
                "lane_id": row["lane_id"],
                "source_status": row.get("source_status"),
                "scientific_edge": "UNPROVEN",
                "owner": row.get("owner"),
                "next_review_question": row.get("review_question"),
            }
            for row in lanes
        ],
    }


def normalize_compounding_families(state):
    if not state:
        return []
    if state.get("contract") != "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1":
        raise RuntimeError("unexpected Compounding Learning state contract")
    if state.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        raise RuntimeError("Compounding Learning authority mismatch")
    rows = []
    for family in state.get("hypothesis_families", []) or []:
        if not isinstance(family, dict) or not family.get("semantic_identity"):
            continue
        rows.append({
            "semantic_identity": str(family["semantic_identity"]),
            "titles": list(family.get("titles") or []),
            "kinds": list(family.get("kinds") or []),
            "candidate_ids": list(family.get("candidate_ids") or []),
            "family_status": str(family.get("current_evidence_status") or "UNKNOWN"),
            "matured_outcome_count": int(family.get("matured_outcome_count_total") or 0),
            "observation_count": int(family.get("observation_count_total") or 0),
            "supporting_evidence_refs": list(family.get("supporting_evidence_refs") or []),
            "contradicting_evidence_refs": list(family.get("contradicting_evidence_refs") or []),
            "inconclusive_evidence_refs": list(family.get("inconclusive_evidence_refs") or []),
            "known_regime_dependence": list(family.get("known_regime_dependence") or ["UNSPECIFIED"]),
            "redundancy_collinearity_warning": bool(family.get("redundancy_collinearity_warning")),
            "confidence_class": family.get("confidence_class"),
            "unresolved_uncertainty": family.get("unresolved_uncertainty"),
            "material_evidence": bool(family.get("material_evidence")),
            "material_evidence_fingerprint": family.get("material_evidence_fingerprint"),
            "source_evidence_fingerprint": family.get("evidence_fingerprint"),
        })
    return rows


def classify_delta(previous, current):
    if previous is None:
        return "NEW"
    old, new = previous.get("family_status"), current.get("family_status")
    if old == new:
        if current.get("matured_outcome_count", 0) > previous.get("matured_outcome_count", 0):
            if new == "SUPPORTED_NEEDS_INCREMENTAL_VALUE":
                return "STRENGTHENED"
            if new == "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW":
                return "FALSIFIED_OR_NEGATIVE"
        return "UNCHANGED"
    if new == "CONTESTED":
        return "CONTESTED"
    if new == "SUPPORTED_NEEDS_INCREMENTAL_VALUE":
        return "STRENGTHENED"
    if new == "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW":
        return "FALSIFIED_OR_NEGATIVE"
    if old == "SUPPORTED_NEEDS_INCREMENTAL_VALUE":
        return "WEAKENED"
    return "UNRESOLVED"


def specialist_route(family):
    text = " ".join(family.get("titles") or []).upper()
    kinds = {str(x).upper() for x in family.get("kinds") or []}
    if "RANGE" in text:
        return "RANGE_LAB_ANALYST"
    if any(x in text for x in ("ETHBTC", "ROTATION", "ALTSEASON", "BREADTH", "DOMINANCE")):
        return "ROTATION_ANALYST"
    if any(x in text for x in ("FUNDING", "OPEN INTEREST", "LIQUIDATION", "TAKER", "DEPTH")):
        return "LEVERAGE_MICROSTRUCTURE_ANALYST"
    if "SEQUENCE_TEST" in kinds or "SEQUENCE" in text or "REGIME" in text:
        return "SEQUENCE_REGIME_ANALYST"
    return "EXPERIMENT_FAMILY_CURATOR"


def build_queue(families, unconsumed, staleness):
    queue = []
    for family in families:
        status = family["family_status"]
        if status == "CONTESTED":
            queue.append({"priority": 1, "state": "DELEGATE_SPECIALIST", "specialist": "CONTRADICTION_ANALYST", "compute_tier": "CHEAP_SPECIALIST", "semantic_identity": family["semantic_identity"], "reason": "Compounding Learning reports contested mature evidence"})
        elif status == "SUPPORTED_NEEDS_INCREMENTAL_VALUE":
            queue.append({"priority": 2, "state": "DELEGATE_DETERMINISTIC", "specialist": specialist_route(family), "compute_tier": "DETERMINISTIC_FIRST", "semantic_identity": family["semantic_identity"], "reason": "supportive family needs incremental-value / replication review, not promotion"})
        elif status == "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW":
            queue.append({"priority": 2, "state": "PROPOSE_EXPERIMENT", "specialist": "EXPERIMENT_FAMILY_CURATOR", "compute_tier": "DETERMINISTIC_FIRST", "semantic_identity": family["semantic_identity"], "reason": "negative family needs bounded failure/regime review; frozen parent preserved"})
    for item in unconsumed:
        queue.append({"priority": 1 if item["severity"] == "HIGH" else 3, "state": "DELEGATE_DETERMINISTIC", "specialist": "INFORMATION_UTILIZATION_ANALYST", "compute_tier": "DETERMINISTIC_FIRST", "semantic_identity": None, "reason": item["reason"], "source": item["source"]})
    for item in staleness:
        if item["status"] == "METHOD_AUDIT_DUE":
            queue.append({"priority": 1, "state": "REQUEST_METHOD_AUDIT", "specialist": "METHODOLOGY_AUDITOR", "compute_tier": "GPT6_SOL_SENIOR_IF_DETERMINISTIC_REVIEW_INSUFFICIENT", "api_task": "SENIOR_REPAIR_AUDIT", "authority": "PROPOSAL_ONLY", "semantic_identity": None, "reason": item["trigger"]})
    queue.sort(key=lambda x: (x["priority"], x["specialist"], x.get("semantic_identity") or ""))
    return queue[:25]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--output-root", default="research/framework_learning")
    ap.add_argument("--as-of-utc")
    ap.add_argument("--finalize-strategist", action="store_true")
    args = ap.parse_args()

    root = Path(args.repo_root)
    now = datetime.fromisoformat(args.as_of_utc.replace("Z", "+00:00")) if args.as_of_utc else datetime.now(timezone.utc)
    if args.finalize_strategist:
        print(json.dumps(finalize_strategist_advisory(root, args.output_root, now), sort_keys=True))
        return
    year, week, week_label = week_id(now)
    out_root = root / args.output_root

    paths = {
        "compounding_state": root / "00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/STATE.json",
        "compounding_backlog": root / "00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/LEARNING_BACKLOG.json",
        "next_best": root / "00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/NEXT_BEST_EXPERIMENT.json",
        "phase1": root / "research/framework_intelligence/phase1/LATEST.json",
        "automation_health": root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
        "architecture_health": root / "research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json",
        "weekly_forensics": root / "research/framework_learning/weekly_forensics/LATEST.json",
        "weekly_forensics_replay": root / "research/framework_learning/weekly_forensics/replay/LATEST_REPLAY_BASELINE.json",
        "automation_orchestration": root / "research/framework_learning/automation_orchestration/LATEST_PLAN.json",
        "shadow_registry_weekly": root / "04_MARKET_LEARNING/shadow_registry/LATEST.json",
    }
    src = {name: load_json(path, {}) or {} for name, path in paths.items()}
    families = normalize_compounding_families(src["compounding_state"])

    previous = load_json(out_root / "LATEST_LEARNING_MEMORY.json", {}) or {}
    previous_map = {x.get("semantic_identity"): x for x in previous.get("families", []) if isinstance(x, dict)}
    memory_rows, deltas = [], []
    for family in families:
        old = previous_map.get(family["semantic_identity"])
        change = classify_delta(old, family)
        row = dict(family)
        row["first_seen_iso_week"] = (old or {}).get("first_seen_iso_week", week_label)
        row["last_seen_iso_week"] = week_label
        row["negative_memory"] = family["family_status"] == "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW"
        row["reopen_condition"] = "materially new regime, data, mechanism or implementation" if row["negative_memory"] else None
        memory_rows.append(row)
        if change != "UNCHANGED":
            deltas.append({"semantic_identity": family["semantic_identity"], "change": change, "from": (old or {}).get("family_status"), "to": family["family_status"], "matured_outcome_count": family["matured_outcome_count"], "titles": family["titles"][:3]})

    phase1 = src["phase1"]
    unconsumed = []
    for contradiction in phase1.get("contradictions", []) or []:
        unconsumed.append({"source": "research/framework_intelligence/phase1/LATEST.json", "expected_consumer": "MASTER_MONDAY", "severity": "HIGH", "status": "UNUSED_HIGH_VALUE", "reason": str(contradiction), "route": "INFORMATION_UTILIZATION_ANALYST"})
    if phase1 and phase1.get("would_offer_to_master_monday") and not phase1.get("live_consumed"):
        unconsumed.append({"source": "research/framework_intelligence/phase1/LATEST.json", "expected_consumer": "MASTER_MONDAY_PHASE2_PLUS", "severity": "MEDIUM", "status": "INTENTIONALLY_UNUSED_PHASE1", "reason": "consultation context exists but is correctly firewalled in Phase 1", "route": "OBSERVE"})

    staleness = [{
        "method": "MASTER_MONDAY_INFORMATION_BINDING",
        "status": "METHOD_AUDIT_DUE" if any(x["severity"] == "HIGH" for x in unconsumed) else "MONITOR",
        "trigger": "high-value evidence exists but weekly consumer binding is inconsistent" if any(x["severity"] == "HIGH" for x in unconsumed) else "no high-severity utilization defect in current snapshot",
        "automatic_change_allowed": False,
    }]

    queue = build_queue(memory_rows, unconsumed, staleness)
    negative = [x for x in memory_rows if x["negative_memory"]]
    ranges = [x for x in memory_rows if any("RANGE" in t.upper() for t in x["titles"]) and x["family_status"] in {"SUPPORTED_NEEDS_INCREMENTAL_VALUE", "CONTESTED"}]
    change_counts = Counter(x["change"] for x in deltas)
    provenance = {name: {"path": str(path.relative_to(root)), "available": path.exists(), "sha256": sha256(path)} for name, path in paths.items()}

    replay = src.get("weekly_forensics_replay") or {}
    replay_summary = {"available": replay.get("contract") == "WEEKLY_FORENSICS_REPLAY_BASELINE_v1", "weeks_materialized": replay.get("weeks_materialized"), "anti_hindsight": replay.get("anti_hindsight"), "authority": replay.get("authority")}

    generated = now.isoformat().replace("+00:00", "Z")
    memory = {
        "contract": "FRAMEWORK_LEARNING_MEMORY_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL", "generated_at_utc": generated, "iso_year": year, "iso_week": week,
        "semantic_family_owner": "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1", "families": memory_rows, "family_count": len(memory_rows),
        "scientific_status": {"forecast_skill": "UNPROVEN", "automatic_promotion": False}, "weekly_forensics_replay_baseline": replay_summary, "provenance": provenance,
    }
    delta_doc = {
        "contract": "WEEKLY_LEARNING_DELTA_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL", "generated_at_utc": generated, "iso_year": year, "iso_week": week,
        "changes": deltas, "change_counts": dict(sorted(change_counts.items())), "negative_memory_count": len(negative), "semantic_family_count": len(memory_rows),
        "source_compounding_delta": src["compounding_state"].get("learning_delta"),
    }
    # No new cron/API job: existing Framework Learning Supervisor already runs
    # daily and Monday. A weekly snapshot becomes visible ONLY after PR merge.
    shadow_weekly_advisory = admit_cross_domain_shadow_weekly(
        src.get("shadow_registry_weekly"), week_label
    )
    packet = {
        "contract": "MASTER_MONDAY_LEARNING_PACKET_v1", "authority": "ADVISORY_ONLY", "generated_at_utc": generated, "iso_year": year, "iso_week": week,
        "live_consumption_allowed": False, "current_phase_gate": "PHASE1_SHADOW_UNLESS_SEPARATELY_PROMOTED",
        "strengthened": [x for x in deltas if x["change"] == "STRENGTHENED"][:5],
        "weakened": [x for x in deltas if x["change"] == "WEAKENED"][:5],
        "new_learning": [x for x in deltas if x["change"] == "NEW"][:5],
        "negative_findings": [{"semantic_identity": x["semantic_identity"], "titles": x["titles"][:2], "reopen_condition": x["reopen_condition"]} for x in negative[:5]],
        "contradictions": phase1.get("contradictions", []) or [],
        "range_context": [{"semantic_identity": x["semantic_identity"], "titles": x["titles"][:2], "matured_outcome_count": x["matured_outcome_count"], "status": x["family_status"]} for x in ranges[:5]],
        "method_improvement_candidates": [x for x in staleness if x["status"] == "METHOD_AUDIT_DUE"],
        "cross_domain_shadow_weekly": shadow_weekly_advisory,
        "scientific_status": "FORECAST_SKILL_UNPROVEN",
        "weekly_forensics_delta": src["weekly_forensics"].get("master_monday_delta") if src["weekly_forensics"].get("contract") == "WEEKLY_FORENSICS_PACK_v1" and src["weekly_forensics"].get("mode") == "FINAL" else None,
        "weekly_forensics_authority": "ADVISORY_ONLY",
    }
    orchestration = src.get("automation_orchestration") or {}
    orchestration_summary = orchestration.get("routing_summary") if orchestration.get("contract") == "AUTOMATION_INTELLIGENT_ORCHESTRATION_PLAN_v1" else None
    supervisor = {
        "contract": "FRAMEWORK_LEARNING_SUPERVISOR_STATE_v1", "authority": "ORCHESTRATION_ONLY", "generated_at_utc": generated, "iso_year": year, "iso_week": week,
        "semantic_family_owner": "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1", "family_count": len(memory_rows), "material_delta_count": len(deltas),
        "unconsumed_information_count": len(unconsumed), "method_audit_due_count": sum(1 for x in staleness if x["status"] == "METHOD_AUDIT_DUE"), "delegation_queue_count": len(queue),
        "cross_domain_shadow_weekly": shadow_weekly_advisory,
        "next_best_existing_experiment": src["next_best"], "compounding_learning_backlog_reference": "00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/LEARNING_BACKLOG.json",
        "compute_policy": "DETERMINISTIC_FIRST_LUNA_FOR_ROUTINE_GPT6_1_SOL_FOR_DIFFICULT_ASTRA_FOR_AGENTIC_EXTREME", "automation_orchestration": orchestration_summary, "canonical_effect": False, "portfolio_execution": False, "master_monday_live_influence": False,
        "strategist_advisory": read_strategist_advisory(root, now),
    }
    docs = {
        "LATEST_LEARNING_MEMORY.json": memory,
        "LATEST_WEEKLY_LEARNING_DELTA.json": delta_doc,
        "LATEST_MASTER_MONDAY_LEARNING_PACKET.json": packet,
        "LATEST_UNCONSUMED_INFORMATION.json": {"contract": "UNCONSUMED_INFORMATION_REGISTER_v1", "generated_at_utc": generated, "items": unconsumed},
        "LATEST_METHOD_STALENESS_REGISTER.json": {"contract": "METHOD_STALENESS_REGISTER_v1", "generated_at_utc": generated, "items": staleness},
        "LATEST_SUPERVISOR_STATE.json": supervisor,
        "LATEST_DELEGATION_QUEUE.json": {"contract": "FRAMEWORK_LEARNING_DELEGATION_QUEUE_v1", "authority": "PROPOSAL_ONLY", "generated_at_utc": generated, "items": queue},
    }
    for name, value in docs.items():
        write_json(out_root / name, value)
    snapshot = out_root / "snapshots" / str(year) / f"W{week:02d}" / now.strftime("%Y%m%dT%H%M%SZ")
    for name, value in docs.items():
        write_json(snapshot / name, value)
    print(json.dumps({"status": "PASS", "family_count": len(memory_rows), "material_delta_count": len(deltas), "queue_count": len(queue)}))


if __name__ == "__main__":
    main()
