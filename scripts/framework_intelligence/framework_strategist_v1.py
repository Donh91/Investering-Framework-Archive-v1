#!/usr/bin/env python3
"""Read-only strategic synthesis owned by the existing Framework Learning Supervisor.

No model calls, external requests, repo discovery, repairs, merges, GitHub comments,
portfolio actions, threshold changes or independent queue/schedule. All observations
remain proposals backed by allowlisted owner receipts; UNKNOWN is not positive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "FRAMEWORK_STRATEGIST_BRIEF_v1"
INTENT_PATH = "00_FMOS/framework_strategist/STRATEGIC_INTENT_v1.json"
OUTPUT_PATH = "research/framework_learning/strategist/LATEST.json"
# Path + authoritative exact contract + maximum accepted age, in hours.
SOURCES = {
    "learning_memory": ("research/framework_learning/LATEST_LEARNING_MEMORY.json",
                        "FRAMEWORK_LEARNING_MEMORY_v1", 48),
    "weekly_delta": ("research/framework_learning/LATEST_WEEKLY_LEARNING_DELTA.json",
                     "WEEKLY_LEARNING_DELTA_v1", 48),
    "self_improvement": ("research/framework_learning/LATEST_SELF_IMPROVEMENT_V1.json",
                         "SELF_IMPROVEMENT_ADVISORY_v1", 48),
    "health": ("research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
               "AUTOMATION_PRODUCTION_HEALTH_v2_1", 48),
    "unconsumed": ("research/framework_learning/LATEST_UNCONSUMED_INFORMATION.json",
                   "UNCONSUMED_INFORMATION_REGISTER_v1", 48),
    "staleness": ("research/framework_learning/LATEST_METHOD_STALENESS_REGISTER.json",
                 "METHOD_STALENESS_REGISTER_v1", 48),
    "weekly_forensics": ("research/framework_learning/weekly_forensics/LATEST.json",
                         "WEEKLY_FORENSICS_PACK_v1", 14 * 24),
}
REQUIRED = set(SOURCES) - {"weekly_forensics"}
ALLOWED_ROUTES = {"SUPERVISOR_ATTENTION", "EXISTING_SOURCE_OWNER", "GROK_REVIEW_CANDIDATE"}
SEVERITY = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}


def _stamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("non_utc_source_timestamp")
    date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if date.tzinfo is None:
        raise ValueError("missing_timezone")
    return date.astimezone(timezone.utc)


def _digest(obj: Any) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _read_receipt(root: Path, path: str, contract: str,
                  now: datetime, max_age_hours: int) -> tuple[dict[str, Any] | None, dict]:
    source = root / path
    receipt = {"path": path, "contract": contract, "status": "MISSING",
               "sha256": None, "source_generated_at_utc": None}
    try:
        if not source.is_file() or source.is_symlink():
            return None, receipt
        raw = source.read_bytes()
        if len(raw) > 5_000_000:
            receipt["status"] = "OVERSIZED"
            return None, receipt
        receipt["sha256"] = hashlib.sha256(raw).hexdigest()
        data = json.loads(raw)
        if not isinstance(data, dict) or data.get("contract") != contract:
            receipt["status"] = "WRONG_CONTRACT"
            return None, receipt
        generated = _stamp(data.get("generated_at_utc"))
        receipt["source_generated_at_utc"] = generated.isoformat().replace("+00:00", "Z")
        age = (now - generated).total_seconds() / 3600
        if age < -0.25:
            receipt["status"] = "FUTURE_DATED"
            return None, receipt
        if age > max_age_hours:
            receipt["status"] = "STALE"
            return None, receipt
        receipt["status"] = "CURRENT"
        return data, receipt
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        receipt["status"] = "INVALID"
        return None, receipt


def _observation(code: str, severity: str, goal: str, owner: str,
                 evidence: list[str], question: str, *,
                 routing: str = "SUPERVISOR_ATTENTION",
                 scientific: str = "NOT_ASSESSED", context: str = "") -> dict:
    if severity not in SEVERITY or routing not in ALLOWED_ROUTES:
        raise ValueError("unknown_signal_route")
    evidence = sorted(set(evidence))
    if not evidence:
        raise ValueError("missing_provenance")
    identity = _digest({"code": code, "goal": goal, "evidence": evidence})[:24]
    return {"id": identity, "code": code, "severity": severity, "goal_id": goal,
            "owner": owner, "evidence_sources": evidence, "question": question,
            "interpretation": context, "scientific_status": scientific,
            "routing": routing, "authority": "PROPOSAL_ONLY", "dispatch_allowed": False,
            "automatic_code_write": False, "automatic_grok_call": False,
            "automatic_market_change": False}


def _valid_rows(data: dict, field: str) -> list[dict]:
    rows = data.get(field)
    if not isinstance(rows, list):
        raise ValueError("malformed_" + field)
    if len(rows) > 10000 or any(not isinstance(x, dict) for x in rows):
        raise ValueError("malformed_" + field)
    return rows


def _safe_write(root: Path, output: Path, result: dict) -> None:
    base, target = root.resolve(), output.resolve()
    if base not in target.parents:
        raise ValueError("output_not_in_repository")
    forbidden = [INTENT_PATH, *[x[0] for x in SOURCES.values()]]
    if target in {(root / p).resolve() for p in forbidden}:
        raise ValueError("output_overwrites_source")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name("." + output.name + "." + str(os.getpid()) + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8") as file:
            json.dump(result, file, sort_keys=True, indent=2)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)


def build(root: Path, output: Path, *, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("naive_clock")
    now = now.astimezone(timezone.utc)
    root = root.resolve()
    output = output.resolve()
    # Validate output BEFORE reading sources or touching any data.
    if root not in output.parents or output in {
        (root / path).resolve() for path in [INTENT_PATH, *[v[0] for v in SOURCES.values()]]
    }:
        raise ValueError("invalid_output_path")
    intent, intent_receipt = _read_receipt(root, INTENT_PATH, "FRAMEWORK_STRATEGIC_INTENT_v1",
                                           now, 24 * 365 * 3)
    if intent is None:
        raise ValueError("owner_intent_unavailable:" + intent_receipt["status"])
    if intent.get("authority") != "OWNER_INTENT_READ_ONLY":
        raise ValueError("intent_authority_violation")
    goals = intent.get("goals")
    if not isinstance(goals, list) or len(goals) < 3 or len(goals) > 12:
        raise ValueError("invalid_goals")
    goal_ids = [g.get("id") for g in goals if isinstance(g, dict)]
    if len(goal_ids) != len(goals) or any(not isinstance(x, str) or not x for x in goal_ids):
        raise ValueError("invalid_goal_identity")
    if len(set(goal_ids)) != len(goal_ids):
        raise ValueError("duplicate_goal_identity")

    docs: dict[str, dict | None] = {}
    receipts: dict[str, dict] = {"strategic_intent": intent_receipt}
    for name, (path, contract, age) in SOURCES.items():
        docs[name], receipts[name] = _read_receipt(root, path, contract, now, age)
    incomplete = sorted(n for n in REQUIRED if docs[n] is None)
    observations: list[dict] = []
    verified_names = {n for n, doc in docs.items() if doc is not None}

    # False-green and integrity: only authority-bound, not self-classified AI prose.
    health = docs["health"]
    evolution = docs["self_improvement"]
    if health is not None and evolution is not None:
        health_status = health.get("status")
        verdict = evolution.get("operational_verdict")
        # The producer and derived classifier must agree on severe state.
        if health_status == "RED" or verdict == "NEEDS_DIAGNOSIS":
            observations.append(_observation(
                "OPERATIONAL_INTEGRITY_ATTENTION", "HIGH", "RELIABILITY", "#1156",
                ["health", "self_improvement"],
                "Ask existing #1156 to check root-cause and production evidence before declaring recovery.",
                context="Operational degradation is observed; not proof of any fixed root cause."))
        elif health_status == "AMBER" or verdict == "ADVISORY_DEGRADED":
            observations.append(_observation(
                "OPERATIONAL_WARNING_REVIEW", "MEDIUM", "RELIABILITY", "#1156",
                ["health", "self_improvement"],
                "Which current AMBER findings are substantive, and which are expected controls?",
                context="A cautionary operations state is not automatically a critical incident."))
        if (verdict == "NO_RED_HEALTH_INCIDENTS" and health_status != "GREEN") or (
                health_status == "GREEN" and verdict in {"NEEDS_DIAGNOSIS", "INSUFFICIENT_EVIDENCE"}):
            observations.append(_observation(
                "SOURCE_CONTRADICTION", "HIGH", "RELIABILITY", "#1156",
                ["health", "self_improvement"],
                "Reconcile inconsistent authoritative and derived health before downstream reuse.",
                routing="GROK_REVIEW_CANDIDATE",
                context="Cross-source conflict; independent reviewer must inspect exact receipts."))
    if evolution is not None:
        score = evolution.get("scoreboard")
        if isinstance(score, dict) and score.get("DOCUMENTED_IMPROVEMENT") == 0:
            observations.append(_observation(
                "NO_DOCUMENTED_IMPROVEMENT_ADMISSION", "INFO", "RESEARCH_RIGOR", "#1157",
                ["self_improvement"],
                "What independent, preregistered held-out evidence is still needed to admit a real improvement?",
                context="Zero validated by this admission surface, NOT zero actual historical progress."))

    # Explicit high-severity consumer gaps; INTENTIONALLY_UNUSED is NOT a defect.
    unused = docs["unconsumed"]
    if unused is not None:
        rows = _valid_rows(unused, "items")
        high = [x for x in rows if x.get("severity") == "HIGH" and
                x.get("status") == "UNUSED_HIGH_VALUE"]
        if high:
            observations.append(_observation(
                "HIGH_VALUE_EVIDENCE_NOT_CONSUMED", "HIGH", "EFFICIENCY",
                "Framework Learning Supervisor", ["unconsumed"],
                "Which verified source-owner handoff should consume these existing high-value records?",
                context=f"{len(high)} existing explicit unused-information records; no new queue created."))

    stale = docs["staleness"]
    if stale is not None:
        items = _valid_rows(stale, "items")
        due = [x for x in items if x.get("status") == "METHOD_AUDIT_DUE"]
        if due:
            observations.append(_observation(
                "METHOD_REVIEW_DUE", "MEDIUM", "EFFICIENCY", "Framework Learning Supervisor",
                ["staleness"], "Route the existing methodology audit rather than minting another method owner.",
                context=f"{len(due)} pre-existing method audits due, not proof of obsolescence."))

    # A WEEKLY delta is NOT a 4-week trend; use only explicit distinct family changes.
    delta = docs["weekly_delta"]
    if delta is not None:
        changes = _valid_rows(delta, "changes")
        statuses: dict[str, set[str]] = {}
        for row in changes:
            sid, direction = row.get("semantic_identity"), row.get("change")
            if isinstance(sid, str) and sid and isinstance(direction, str):
                statuses.setdefault(sid, set()).add(direction)
        negative = sum(bool(states & {"WEAKENED", "FALSIFIED_OR_NEGATIVE", "CONTESTED"})
                       for states in statuses.values())
        positive = sum("STRENGTHENED" in states for states in statuses.values())
        if negative >= 2:
            observations.append(_observation(
                "WEEKLY_RESEARCH_WEAKENING", "MEDIUM", "RESEARCH_RIGOR", "#1157",
                ["weekly_delta"],
                "Check whether these distinct research-family changes survived source-root and outcome validation.",
                context=f"{negative} distinct negative/contested family identities in one weekly delta, NOT a multiweek decline.",
                scientific="UNVERIFIED_RESEARCH_DIRECTION"))
        if positive >= 2:
            observations.append(_observation(
                "WEEKLY_RESEARCH_STRENGTHENING", "INFO", "RESEARCH_RIGOR", "#1157",
                ["weekly_delta"],
                "Audit incremental value against independent baseline; do not label this investment improvement.",
                context=f"{positive} distinct strengthened families in one weekly delta; may share original roots.",
                scientific="UNVERIFIED_RESEARCH_DIRECTION"))

    # Use explicit weekly finding owners; not freeform model-selected instructions.
    forensics = docs["weekly_forensics"]
    if forensics is not None:
        findings = _valid_rows(forensics, "findings")
        serious = [f for f in findings if f.get("severity") == "HIGH" and
                   f.get("route") not in {"WAIT_FOR_EVIDENCE", "NO_ACTION"}]
        if serious:
            observations.append(_observation(
                "UNRESOLVED_WEEKLY_RESEARCH_BLOCKERS", "HIGH", "RESEARCH_RIGOR",
                "Weekly Forensics / existing domain owners", ["weekly_forensics"],
                "Ask source owners to verify whether these existing high-severity weekly blockers remain open.",
                context=f"{len(serious)} historical weekly findings; may already be resolved since the source timestamp."))

    # Missing sources are never replaced with legacy or imagination.
    if incomplete:
        observations.append(_observation(
            "STRATEGIC_SOURCE_GAP", "HIGH", "RELIABILITY", "Framework Learning Supervisor",
            [f"missing:{name}" for name in incomplete],
            "Restore fresh, contract-correct owner receipts before making strategic claims.",
            context="Required strategic inputs unavailable; absence is UNKNOWN, not health."))

    # This is a proposal-only lens; no fabricated Alpha Lab/Task2/Compass outcome progress.
    priority = sorted(observations, key=lambda x: (SEVERITY[x["severity"]], x["code"], x["id"]))
    accepted = priority[:3]
    for row in accepted:
        row["evidence_bindings"] = [
            {"name": key, **receipts[key]} for key in row["evidence_sources"] if key in receipts
        ]
        row["grok_bridge_state"] = ("CANDIDATE_NOT_DISPATCHED" if
                                    row["routing"] == "GROK_REVIEW_CANDIDATE" else "NOT_REQUESTED")
    evidence_status = "DEGRADED" if incomplete or any(r["status"] != "CURRENT" for r in receipts.values()) else "CURRENT"
    result = {
        "contract": CONTRACT,
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "authority": {"type": "ADVISORY_ONLY", "canonical_effect": False,
                      "scientific_promotion": False, "portfolio_execution": False,
                      "autonomous_grok_request": False, "autonomous_api_payment": False,
                      "autonomous_merge": False, "new_queue": False},
        "owner": "EXISTING_FRAMEWORK_LEARNING_SUPERVISOR",
        "intent_contract": intent["contract"],
        "intent_sha256": intent_receipt["sha256"],
        "source_receipts": receipts,
        "input_status": evidence_status,
        "incomplete_required_inputs": incomplete,
        "covered_source_count": len(verified_names),
        "goal_alignment": [
            {"goal_id": g["id"], "status": "OUTCOME_NOT_INDEPENDENTLY_EVALUATED",
             "evidence_requirement": g.get("evidence_requirement"),
             "owner_issue": g.get("owner_issue")} for g in goals
        ],
        "observations_total": len(observations),
        "proposals": accepted,
        "suppressed_by_max_three": max(0, len(observations) - len(accepted)),
        "longitudinal_claim": "NO_VERIFIED_MULTI_WEEK_TREND_IN_THIS_READOUT",
        "next_step": "ADVISORY_HANDOFF_TO_EXISTING_SUPERVISOR; GROK_ONLY_VIA_EXISTING_VERIFIED_BRIDGE",
    }
    _safe_write(root, output, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output", default=OUTPUT_PATH)
    parser.add_argument("--as-of-utc")
    args = parser.parse_args()
    now = _stamp(args.as_of_utc) if args.as_of_utc else None
    result = build(Path(args.repo_root), Path(args.repo_root) / args.output, now=now)
    print(json.dumps({"contract": result["contract"],
                      "input_status": result["input_status"],
                      "proposal_count": len(result["proposals"])}, sort_keys=True))


if __name__ == "__main__":
    main()
