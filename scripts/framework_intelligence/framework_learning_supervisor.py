#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
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


def iso_week(now: datetime):
    y, w, _ = now.isocalendar()
    return int(y), int(w)


def candidate_maps(registry, admission, adjudication):
    amap = {str(x.get("candidate_id")): x for x in (admission or {}).get("candidates", []) if isinstance(x, dict) and x.get("candidate_id")}
    jmap = {str(x.get("candidate_id")): x for x in (adjudication or {}).get("candidate_actions", []) if isinstance(x, dict) and x.get("candidate_id")}
    return amap, jmap


def derive_families(registry, admission, adjudication):
    amap, jmap = candidate_maps(registry, admission, adjudication)
    grouped = defaultdict(list)
    for c in (registry or {}).get("candidates", []):
        if not isinstance(c, dict) or not c.get("candidate_id"):
            continue
        cid = str(c["candidate_id"])
        ar = amap.get(cid, {})
        key = str(ar.get("semantic_fingerprint") or c.get("semantic_fingerprint") or cid)
        grouped[key].append((c, ar, jmap.get(cid, {})))

    out = []
    for key, rows in grouped.items():
        lifecycle = Counter()
        actions = Counter()
        admission_states = Counter()
        titles = set()
        matured = observations = 0
        dup = 0
        candidate_ids = []
        for c, ar, jr in rows:
            cid = str(c.get("candidate_id"))
            candidate_ids.append(cid)
            titles.add(str(c.get("title") or ""))
            lifecycle[str(c.get("state") or jr.get("lifecycle_state") or "UNKNOWN")] += 1
            actions[str(jr.get("selected_action") or "UNKNOWN")] += 1
            ast = str(ar.get("status") or c.get("scientific_admission_status") or "UNKNOWN")
            admission_states[ast] += 1
            if ast == "SEMANTIC_DUPLICATE_KEEP_SHADOW":
                dup += 1
            matured += int(c.get("matured_outcome_count") or jr.get("matured_outcome_count") or 0)
            observations += int(c.get("observation_count") or 0)

        if actions.get("RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW") and actions.get("RUN_FAILURE_AND_RETIREMENT_REVIEW"):
            status = "CONTESTED"
        elif actions.get("RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW"):
            status = "SUPPORTED_NEEDS_INCREMENTAL_VALUE"
        elif actions.get("RUN_FAILURE_AND_RETIREMENT_REVIEW"):
            status = "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW"
        elif actions.get("KEEP_SHADOW_INCONCLUSIVE"):
            status = "INCONCLUSIVE_KEEP_FROZEN"
        elif all(x == "SEMANTIC_DUPLICATE_KEEP_SHADOW" for x in admission_states for _ in range(admission_states[x])):
            status = "ARCHIVE_DUPLICATE"
        elif admission_states.get("TARGET_UNIT_QUARANTINED"):
            status = "KEEP_QUARANTINED"
        elif admission_states.get("WAITING_FOR_MAPPING"):
            status = "WAIT_FOR_MAPPING"
        else:
            status = "WAIT_FOR_MORE_PROSPECTIVE_EVIDENCE"

        out.append({
            "semantic_identity": key,
            "candidate_ids": sorted(candidate_ids),
            "titles": sorted(t for t in titles if t),
            "family_status": status,
            "candidate_count": len(rows),
            "semantic_duplicate_count": dup,
            "duplicate_adjusted_candidate_count": max(0, len(rows) - dup),
            "matured_outcome_count": matured,
            "observation_count": observations,
            "lifecycle_counts": dict(sorted(lifecycle.items())),
            "adjudication_action_counts": dict(sorted(actions.items())),
            "scientific_admission_counts": dict(sorted(admission_states.items())),
        })
    out.sort(key=lambda x: (x["family_status"], -x["matured_outcome_count"], x["semantic_identity"]))
    return out


def classify_delta(prev, curr):
    if prev is None:
        return "NEW"
    old, new = prev.get("family_status"), curr.get("family_status")
    if old == new:
        if curr.get("matured_outcome_count", 0) > prev.get("matured_outcome_count", 0):
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
    if old == "SUPPORTED_NEEDS_INCREMENTAL_VALUE" and new != old:
        return "WEAKENED"
    return "UNRESOLVED"


def specialist_route(family):
    title = " ".join(family.get("titles") or []).upper()
    if "RANGE" in title:
        return "RANGE_LAB_ANALYST"
    if "ETHBTC" in title or "ROTATION" in title or "ALTSEASON" in title or "BREADTH" in title:
        return "ROTATION_ANALYST"
    if "FUNDING" in title or "OPEN INTEREST" in title or " OI " in f" {title} " or "LIQUID" in title:
        return "LEVERAGE_MICROSTRUCTURE_ANALYST"
    if "SEQUENCE" in title or "REGIME" in title:
        return "SEQUENCE_REGIME_ANALYST"
    return "EXPERIMENT_FAMILY_CURATOR"


def build_queue(families, phase1, unconsumed, staleness):
    queue = []
    for f in families:
        state = f["family_status"]
        if state == "CONTESTED":
            queue.append({"priority": 1, "state": "DELEGATE_SPECIALIST", "specialist": "CONTRADICTION_ANALYST", "compute_tier": "CHEAP_SPECIALIST", "semantic_identity": f["semantic_identity"], "reason": "material family contains conflicting mature evidence"})
        elif state == "SUPPORTED_NEEDS_INCREMENTAL_VALUE":
            queue.append({"priority": 2, "state": "DELEGATE_DETERMINISTIC", "specialist": specialist_route(f), "compute_tier": "DETERMINISTIC_FIRST", "semantic_identity": f["semantic_identity"], "reason": "supportive learning requires incremental-value and replication review before any method implication"})
        elif state == "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW":
            queue.append({"priority": 2, "state": "PROPOSE_EXPERIMENT", "specialist": "EXPERIMENT_FAMILY_CURATOR", "compute_tier": "DETERMINISTIC_FIRST", "semantic_identity": f["semantic_identity"], "reason": "negative evidence requires bounded regime/failure review; parent remains frozen"})
    for row in unconsumed:
        queue.append({"priority": 1 if row["severity"] == "HIGH" else 3, "state": "DELEGATE_DETERMINISTIC", "specialist": "INFORMATION_UTILIZATION_ANALYST", "compute_tier": "DETERMINISTIC_FIRST", "semantic_identity": None, "reason": row["reason"], "source": row["source"]})
    for row in staleness:
        if row["status"] == "METHOD_AUDIT_DUE":
            queue.append({"priority": 1, "state": "REQUEST_METHOD_AUDIT", "specialist": "METHODOLOGY_AUDITOR", "compute_tier": "SOL_OR_TERRA_IF_DETERMINISTIC_REVIEW_INSUFFICIENT", "semantic_identity": None, "reason": row["trigger"]})
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
    year, week = iso_week(now)
    out_root = root / args.output_root

    paths = {
        "registry": root / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json",
        "admission": root / "research/experiment_lifecycle/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json",
        "adjudication": root / "research/experiment_lifecycle/weekly_adjudication/LATEST.json",
        "compounding_state": root / "00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/STATE.json",
        "next_best": root / "00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1/NEXT_BEST_EXPERIMENT.json",
        "phase1": root / "research/framework_intelligence/phase1/LATEST.json",
        "automation_health": root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
        "architecture_health": root / "research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json",
    }
    src = {k: load_json(v, {}) for k, v in paths.items()}
    families = derive_families(src["registry"], src["admission"], src["adjudication"])

    previous = load_json(out_root / "LATEST_LEARNING_MEMORY.json", {}) or {}
    previous_map = {x.get("semantic_identity"): x for x in previous.get("families", []) if isinstance(x, dict)}
    memory_rows = []
    deltas = []
    for f in families:
        old = previous_map.get(f["semantic_identity"])
        delta = classify_delta(old, f)
        row = dict(f)
        row["first_seen_iso_week"] = (old or {}).get("first_seen_iso_week", f"{year}-W{week:02d}")
        row["last_seen_iso_week"] = f"{year}-W{week:02d}"
        row["negative_memory"] = f["family_status"] == "NEGATIVE_EVIDENCE_NEEDS_FAILURE_REVIEW"
        row["reopen_condition"] = "materially new regime, data, mechanism or implementation" if row["negative_memory"] else None
        memory_rows.append(row)
        if delta != "UNCHANGED":
            deltas.append({"semantic_identity": f["semantic_identity"], "change": delta, "from": (old or {}).get("family_status"), "to": f["family_status"], "matured_outcome_count": f["matured_outcome_count"], "titles": f["titles"][:3]})

    phase1 = src["phase1"] or {}
    unconsumed = []
    for c in phase1.get("contradictions", []) or []:
        unconsumed.append({"source": "research/framework_intelligence/phase1/LATEST.json", "expected_consumer": "MASTER_MONDAY", "severity": "HIGH", "status": "UNUSED_HIGH_VALUE", "reason": str(c), "route": "INFORMATION_UTILIZATION_ANALYST"})
    if phase1 and phase1.get("would_offer_to_master_monday") and not phase1.get("live_consumed"):
        unconsumed.append({"source": "research/framework_intelligence/phase1/LATEST.json", "expected_consumer": "MASTER_MONDAY_PHASE2_PLUS", "severity": "MEDIUM", "status": "INTENTIONALLY_UNUSED_PHASE1", "reason": "consultation context is available but correctly firewalled during Phase 1", "route": "OBSERVE"})

    staleness = []
    if any(x["severity"] == "HIGH" for x in unconsumed):
        staleness.append({"method": "MASTER_MONDAY_INFORMATION_BINDING", "status": "METHOD_AUDIT_DUE", "trigger": "high-value evidence exists but weekly package/consumer binding is inconsistent", "automatic_change_allowed": False})
    else:
        staleness.append({"method": "MASTER_MONDAY_INFORMATION_BINDING", "status": "MONITOR", "trigger": "no high-severity utilization defect in current snapshot", "automatic_change_allowed": False})

    queue = build_queue(memory_rows, phase1, unconsumed, staleness)
    counts = Counter(x["change"] for x in deltas)
    range_context = [x for x in memory_rows if any("RANGE" in t.upper() for t in x.get("titles", [])) and x["family_status"] in {"SUPPORTED_NEEDS_INCREMENTAL_VALUE", "CONTESTED"}]
    negative = [x for x in memory_rows if x.get("negative_memory")]

    provenance = {k: {"path": str(v.relative_to(root)), "available": v.exists(), "sha256": sha256(v)} for k, v in paths.items()}
    memory = {
        "contract": "FRAMEWORK_LEARNING_MEMORY_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL", "generated_at_utc": now.isoformat().replace("+00:00", "Z"), "iso_year": year, "iso_week": week,
        "families": memory_rows, "family_count": len(memory_rows), "scientific_status": {"forecast_skill": "UNPROVEN", "automatic_promotion": False}, "provenance": provenance,
    }
    delta_doc = {
        "contract": "WEEKLY_LEARNING_DELTA_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL", "generated_at_utc": memory["generated_at_utc"], "iso_year": year, "iso_week": week,
        "changes": deltas, "change_counts": dict(sorted(counts.items())), "negative_memory_count": len(negative), "semantic_family_count": len(memory_rows),
    }
    packet = {
        "contract": "MASTER_MONDAY_LEARNING_PACKET_v1", "authority": "ADVISORY_ONLY", "generated_at_utc": memory["generated_at_utc"], "iso_year": year, "iso_week": week,
        "live_consumption_allowed": False, "current_phase_gate": "PHASE1_SHADOW_UNLESS_SEPARATELY_PROMOTED",
        "strengthened": [x for x in deltas if x["change"] == "STRENGTHENED"][:5],
        "weakened": [x for x in deltas if x["change"] == "WEAKENED"][:5],
        "new_learning": [x for x in deltas if x["change"] == "NEW"][:5],
        "negative_findings": [{"semantic_identity": x["semantic_identity"], "titles": x["titles"][:2], "reopen_condition": x["reopen_condition"]} for x in negative[:5]],
        "contradictions": phase1.get("contradictions", []) or [],
        "range_context": [{"semantic_identity": x["semantic_identity"], "titles": x["titles"][:2], "matured_outcome_count": x["matured_outcome_count"], "status": x["family_status"]} for x in range_context[:5]],
        "method_improvement_candidates": [x for x in staleness if x["status"] == "METHOD_AUDIT_DUE"],
        "scientific_status": "FORECAST_SKILL_UNPROVEN",
    }
    supervisor = {
        "contract": "FRAMEWORK_LEARNING_SUPERVISOR_STATE_v1", "authority": "ORCHESTRATION_ONLY", "generated_at_utc": memory["generated_at_utc"], "iso_year": year, "iso_week": week,
        "family_count": len(memory_rows), "material_delta_count": len(deltas), "unconsumed_information_count": len(unconsumed), "method_audit_due_count": sum(1 for x in staleness if x["status"] == "METHOD_AUDIT_DUE"),
        "delegation_queue_count": len(queue), "next_best_existing_experiment": src["next_best"],
        "compute_policy": "DETERMINISTIC_FIRST_CHEAPEST_SUFFICIENT_ESCALATION", "canonical_effect": False, "portfolio_execution": False, "master_monday_live_influence": False,
    }

    docs = {
        "LATEST_LEARNING_MEMORY.json": memory,
        "LATEST_WEEKLY_LEARNING_DELTA.json": delta_doc,
        "LATEST_MASTER_MONDAY_LEARNING_PACKET.json": packet,
        "LATEST_UNCONSUMED_INFORMATION.json": {"contract": "UNCONSUMED_INFORMATION_REGISTER_v1", "generated_at_utc": memory["generated_at_utc"], "items": unconsumed},
        "LATEST_METHOD_STALENESS_REGISTER.json": {"contract": "METHOD_STALENESS_REGISTER_v1", "generated_at_utc": memory["generated_at_utc"], "items": staleness},
        "LATEST_SUPERVISOR_STATE.json": supervisor,
        "LATEST_DELEGATION_QUEUE.json": {"contract": "FRAMEWORK_LEARNING_DELEGATION_QUEUE_v1", "authority": "PROPOSAL_ONLY", "generated_at_utc": memory["generated_at_utc"], "items": queue},
    }
    for name, value in docs.items():
        write_json(out_root / name, value)
    snapshot = out_root / "snapshots" / str(year) / f"W{week:02d}" / now.strftime("%Y%m%dT%H%M%SZ")
    for name, value in docs.items():
        write_json(snapshot / name, value)
    print(json.dumps({"status": "PASS", "outputs": list(docs), "queue_count": len(queue), "material_delta_count": len(deltas)}))


if __name__ == "__main__":
    main()
