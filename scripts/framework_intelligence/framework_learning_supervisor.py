#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
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


def week_id(now: datetime):
    y, w, _ = now.isocalendar()
    return int(y), int(w), f"{int(y)}-W{int(w):02d}"


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
            queue.append({"priority": 1, "state": "REQUEST_METHOD_AUDIT", "specialist": "METHODOLOGY_AUDITOR", "compute_tier": "SOL_OR_TERRA_IF_DETERMINISTIC_REVIEW_INSUFFICIENT", "semantic_identity": None, "reason": item["trigger"]})
    queue.sort(key=lambda x: (x["priority"], x["specialist"], x.get("semantic_identity") or ""))
    return queue[:25]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--output-root", default="research/framework_learning")
    ap.add_argument("--as-of-utc")
    args = ap.parse_args()

    root = Path(args.repo_root)
    now = datetime.fromisoformat(args.as_of_utc.replace("Z", "+00:00")) if args.as_of_utc else datetime.now(timezone.utc)
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

    generated = now.isoformat().replace("+00:00", "Z")
    memory = {
        "contract": "FRAMEWORK_LEARNING_MEMORY_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL", "generated_at_utc": generated, "iso_year": year, "iso_week": week,
        "semantic_family_owner": "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1", "families": memory_rows, "family_count": len(memory_rows),
        "scientific_status": {"forecast_skill": "UNPROVEN", "automatic_promotion": False}, "provenance": provenance,
    }
    delta_doc = {
        "contract": "WEEKLY_LEARNING_DELTA_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL", "generated_at_utc": generated, "iso_year": year, "iso_week": week,
        "changes": deltas, "change_counts": dict(sorted(change_counts.items())), "negative_memory_count": len(negative), "semantic_family_count": len(memory_rows),
        "source_compounding_delta": src["compounding_state"].get("learning_delta"),
    }
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
        "scientific_status": "FORECAST_SKILL_UNPROVEN",
        "weekly_forensics_delta": src["weekly_forensics"].get("master_monday_delta") if src["weekly_forensics"].get("contract") == "WEEKLY_FORENSICS_PACK_v1" and src["weekly_forensics"].get("mode") == "FINAL" else None,
        "weekly_forensics_authority": "ADVISORY_ONLY",
    }
    supervisor = {
        "contract": "FRAMEWORK_LEARNING_SUPERVISOR_STATE_v1", "authority": "ORCHESTRATION_ONLY", "generated_at_utc": generated, "iso_year": year, "iso_week": week,
        "semantic_family_owner": "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1", "family_count": len(memory_rows), "material_delta_count": len(deltas),
        "unconsumed_information_count": len(unconsumed), "method_audit_due_count": sum(1 for x in staleness if x["status"] == "METHOD_AUDIT_DUE"), "delegation_queue_count": len(queue),
        "next_best_existing_experiment": src["next_best"], "compounding_learning_backlog_reference": "00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/LEARNING_BACKLOG.json",
        "compute_policy": "DETERMINISTIC_FIRST_CHEAPEST_SUFFICIENT_ESCALATION", "canonical_effect": False, "portfolio_execution": False, "master_monday_live_influence": False,
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
