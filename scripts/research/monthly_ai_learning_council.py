#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()).hexdigest()


def count_json(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for p in root.rglob("*.json") if p.is_file())


def compact_experiment_registry(registry: dict[str, Any], limit: int = 100) -> dict[str, Any]:
    rows = []
    states: dict[str, int] = {}
    for row in registry.get("candidates", []):
        if not isinstance(row, dict):
            continue
        state = str(row.get("state") or "UNKNOWN")
        states[state] = states.get(state, 0) + 1
        matured = int(row.get("matured_outcome_count", 0) or 0)
        if matured > 0 or state.startswith("MATURED"):
            rows.append({
                "candidate_id": row.get("candidate_id"),
                "title": row.get("title"),
                "kind": row.get("kind"),
                "state": state,
                "matured_outcome_count": matured,
                "scientific_admission_status": row.get("scientific_admission_status"),
            })
    rows.sort(key=lambda x: (-int(x.get("matured_outcome_count", 0)), str(x.get("candidate_id"))))
    return {
        "contract": registry.get("contract"),
        "candidate_count": len([x for x in registry.get("candidates", []) if isinstance(x, dict)]),
        "state_counts": states,
        "matured_candidates": rows[:limit],
    }


def build_context(repo_root: Path, now: datetime) -> dict[str, Any]:
    policy = read_json(repo_root / "research/monthly_learning_council/MONTHLY_AI_LEARNING_COUNCIL_POLICY_v1.json", {}) or {}
    prior = read_json(repo_root / "research/monthly_learning_council/STATE.json", {}) or {}
    lifecycle = read_json(repo_root / "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json", {}) or {}
    adjudication = read_json(repo_root / "research/experiment_lifecycle/weekly_adjudication/LATEST.json", {}) or {}
    shadow = read_json(repo_root / "04_MARKET_LEARNING/shadow_registry/LATEST.json", {}) or {}
    shared = read_json(repo_root / "06_RESEARCH_LAB/shared_row_model_tournament_v1/weekly/LATEST.json", {}) or {}
    action_compass = read_json(repo_root / "research/framework_memory/action_compass_calibration/LATEST_EXIT_WARNING_CALIBRATION.json", {}) or {}
    architecture = read_json(repo_root / "research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json", {}) or {}
    automation = read_json(repo_root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json", {}) or {}

    forecast_n = count_json(repo_root / "research/framework_memory/forecast_memory")
    outcome_n = count_json(repo_root / "research/framework_memory/outcome_memory")
    escalation = [x for x in adjudication.get("escalation_queue", []) if isinstance(x, dict)]
    escalation_limit = int(policy.get("max_escalation_candidates_in_context", 25) or 25)
    escalation = escalation[:escalation_limit]
    escalation_fp = digest(escalation)

    month_key = now.strftime("%Y-%m")
    monthly_day = int(policy.get("monthly_review_day", 3) or 3)
    monthly_due = now.day >= monthly_day and prior.get("last_completed_month") != month_key
    matured_delta = max(0, outcome_n - int(prior.get("last_matured_outcomes_total", 0) or 0))
    maturation_trigger = matured_delta >= int(policy.get("matured_outcome_delta_trigger", 25) or 25)
    escalation_trigger = bool(escalation) and escalation_fp != str(prior.get("last_escalation_fingerprint") or "")
    milestone_due = maturation_trigger or escalation_trigger
    run_review = monthly_due or milestone_due
    quarterly = monthly_due and now.month in set(policy.get("quarterly_review_months", [1, 4, 7, 10]))
    review_kind = "QUARTERLY_ARCHITECTURE" if quarterly else "MONTHLY" if monthly_due else "EVIDENCE_MILESTONE" if milestone_due else "NO_REVIEW"

    context = {
        "contract": "MONTHLY_AI_LEARNING_COUNCIL_FROZEN_CONTEXT_v1",
        "generated_at_utc": now.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "review_kind": review_kind,
        "eligibility": {
            "run_review": run_review,
            "monthly_due": monthly_due,
            "milestone_due": milestone_due,
            "maturation_trigger": maturation_trigger,
            "escalation_trigger": escalation_trigger,
            "matured_outcome_delta": matured_delta,
            "month_key": month_key,
        },
        "evidence_census": {
            "forecast_json_count": forecast_n,
            "outcome_json_count": outcome_n,
            "experiment_registry": compact_experiment_registry(lifecycle),
            "weekly_adjudication_summary": adjudication.get("summary"),
            "weekly_escalation_queue": escalation,
            "shadow_registry_summary": shadow.get("summary"),
            "shared_row_snapshot": {
                "contract": shared.get("contract"),
                "status": shared.get("status"),
                "relevance_state": shared.get("relevance_state"),
                "summary": shared.get("summary"),
            },
            "action_compass_calibration": action_compass,
            "architecture_health": architecture.get("summary", architecture),
            "automation_health": automation.get("summary", automation),
        },
        "prior_council_state": {
            "last_completed_month": prior.get("last_completed_month"),
            "last_review_at_utc": prior.get("last_review_at_utc"),
            "last_review_kind": prior.get("last_review_kind"),
            "last_matured_outcomes_total": prior.get("last_matured_outcomes_total", 0),
            "last_escalation_fingerprint": prior.get("last_escalation_fingerprint", ""),
        },
        "deterministic_markers": {
            "current_escalation_fingerprint": escalation_fp,
            "minimum_matured_outcomes_for_learning_claim": int(policy.get("minimum_matured_outcomes_for_learning_claim", 25) or 25),
        },
        "firewall": {
            "canonical_effect": False,
            "portfolio_execution": False,
            "automatic_threshold_change": False,
            "automatic_weight_change": False,
            "automatic_market_rule_change": False,
            "automatic_canonical_promotion": False,
        },
    }
    context["freeze_sha256"] = digest(context)
    return context


def analyst_prompt(review_kind: str) -> str:
    quarterly = " In quarterly mode, also test whether complexity should be removed, sensors retired, and simple models outperform full-stack variants." if review_kind == "QUARTERLY_ARCHITECTURE" else ""
    return (
        "Act as the primary scientist for a frozen monthly learning audit. Use only supplied evidence. Distinguish prospective matured evidence from immature, duplicate, descriptive, replay, or merely interesting evidence. "
        "Ask what was actually learned, what was challenged, what remains unlearned, what is redundant, and which bounded prospective research question has highest information value. "
        "Do not call small-N patterns learned. Do not modify an existing test after seeing outcomes; changed ideas must become new preregistered hypotheses. "
        "Put only testable research-only hypotheses in hypotheses, each phrased with its falsification condition. forecast_candidates must be empty. "
        "Never recommend portfolio action, threshold/weight/rule changes, or canonical promotion." + quarterly
    )


def adversarial_prompt() -> str:
    return (
        "Act as an independent adversarial scientist. The context includes a frozen evidence package and the first analyst's output. Try to falsify the analyst rather than agree. "
        "Look for hindsight leakage, multiple testing, dependence, semantic duplicates, regime coincidence, weak baselines, selection bias, survivorship, revision drift, small-N theatre, and complexity without incremental value. "
        "Preserve matured-versus-immature boundaries. In hypotheses, return only bounded research hypotheses that still deserve prospective testing after your critique; return an empty list if none survive. "
        "forecast_candidates must be empty. Do not change market rules, thresholds, weights, canonical state, or portfolio action."
    )


def blocked_ai(reason: str) -> dict[str, Any]:
    return {"status": "BLOCKED", "summary": "AI review unavailable; deterministic council remains valid.", "evidence_for": [], "evidence_against": [], "uncertainties": [reason], "hypotheses": [], "forecast_candidates": []}


def choose_primary_action(context: dict[str, Any], adversarial: dict[str, Any]) -> tuple[str, str, str, list[dict[str, Any]]]:
    escalations = context.get("evidence_census", {}).get("weekly_escalation_queue", []) or []
    if escalations:
        first = escalations[0]
        cid = str(first.get("candidate_id") or "UNSPECIFIED_CANDIDATE")
        selected = str(first.get("selected_action") or "")
        if selected == "RUN_INCREMENTAL_VALUE_AND_ADVERSARIAL_REVIEW":
            return "RUN_INCREMENTAL_VALUE_TEST", cid, "Matured supportive evidence requires incremental-value review before any promotion.", []
        if selected == "RUN_FAILURE_AND_RETIREMENT_REVIEW":
            return "RUN_REDUNDANCY_CONFIRMATION", cid, "Negative matured evidence requires failure/redundancy review before retirement.", []
    hypotheses = adversarial.get("hypotheses", []) if adversarial.get("status") in {"READY", "DEGRADED"} else []
    queue = []
    for text in hypotheses:
        clean = " ".join(str(text).split())[:1200]
        if not clean:
            continue
        hid = "MLC-HYP-" + hashlib.sha256(clean.encode()).hexdigest()[:16]
        queue.append({"candidate_id": hid, "hypothesis": clean, "action": "RESEARCH_NEW_HYPOTHESIS", "authority": "RESEARCH_ONLY_NON_CANONICAL", "canonical_effect": False})
    if queue:
        first = queue[0]
        return "RESEARCH_NEW_HYPOTHESIS", first["candidate_id"], first["hypothesis"], queue
    return "CONTINUE_OBSERVING", "MONTHLY_AI_LEARNING_COUNCIL", "No evidence-backed escalation or surviving AI research hypothesis justified a new bounded research item.", []


def deterministic_claims(context: dict[str, Any], floor: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    learned, challenged = [], []
    rows = context.get("evidence_census", {}).get("experiment_registry", {}).get("matured_candidates", []) or []
    for row in rows:
        n = int(row.get("matured_outcome_count", 0) or 0)
        if n < floor:
            continue
        state = str(row.get("state") or "")
        compact = {"candidate_id": row.get("candidate_id"), "title": row.get("title"), "matured_outcome_count": n, "state": state}
        if state == "MATURED_SUPPORTED":
            learned.append(compact)
        elif state == "MATURED_NOT_SUPPORTED":
            challenged.append(compact)
    return learned, challenged


def finalize(repo_root: Path, runtime_root: Path, now: datetime) -> dict[str, Any]:
    context = read_json(runtime_root / "context.json", {}) or {}
    analyst = read_json(runtime_root / "analyst/output.json", None) or blocked_ai("ANALYST_OUTPUT_UNAVAILABLE")
    adversarial = read_json(runtime_root / "adversarial/output.json", None) or blocked_ai("ADVERSARIAL_OUTPUT_UNAVAILABLE")
    policy = read_json(repo_root / "research/monthly_learning_council/MONTHLY_AI_LEARNING_COUNCIL_POLICY_v1.json", {}) or {}
    prior = read_json(repo_root / "research/monthly_learning_council/STATE.json", {}) or {}
    floor = int(policy.get("minimum_matured_outcomes_for_learning_claim", 25) or 25)
    learned, challenged = deterministic_claims(context, floor)
    action, target, reason, candidate_queue = choose_primary_action(context, adversarial)
    max_candidates = int(policy.get("max_ai_research_candidates", 5) or 5)
    candidate_queue = candidate_queue[:max_candidates]
    now_text = now.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    eligibility = context.get("eligibility", {})
    state = {
        "contract": "MONTHLY_AI_LEARNING_COUNCIL_STATE_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "status": "REVIEW_COMPLETE",
        "primary_action": action,
        "target": target,
        "reason": reason,
        "evidence_fingerprint": context.get("freeze_sha256", ""),
        "last_completed_month": eligibility.get("month_key") if eligibility.get("monthly_due") else prior.get("last_completed_month"),
        "last_review_at_utc": now_text,
        "last_review_kind": context.get("review_kind"),
        "last_matured_outcomes_total": context.get("evidence_census", {}).get("outcome_json_count", 0),
        "last_escalation_fingerprint": context.get("deterministic_markers", {}).get("current_escalation_fingerprint", ""),
        "candidate_queue": candidate_queue,
        "learning_claims": learned,
        "challenged_claims": challenged,
        "ai_review_status": {"analyst": analyst.get("status"), "adversarial": adversarial.get("status")},
        "canonical_effect": False,
        "portfolio_execution": False,
        "paid_data_authorized": False,
        "deep_research_authorized": False,
        "external_provider_calls_authorized": False,
    }
    report = {
        "contract": "MONTHLY_AI_LEARNING_COUNCIL_REPORT_v1",
        "generated_at_utc": now_text,
        "review_kind": context.get("review_kind"),
        "freeze_sha256": context.get("freeze_sha256"),
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "deterministic": {"learning_claims": learned, "challenged_claims": challenged, "primary_action": action, "target": target, "candidate_queue": candidate_queue},
        "ai": {"analyst": analyst, "adversarial": adversarial},
        "eligibility": eligibility,
        "firewall": context.get("firewall"),
        "canonical_effect": False,
        "portfolio_execution": False,
    }
    root = repo_root / "research/monthly_learning_council"
    write_json(root / "STATE.json", state)
    write_json(root / "LATEST.json", report)
    stamp = now.astimezone(UTC).strftime("%Y/%m/%d/%H%M%S")
    write_json(root / "history" / stamp / "CONTEXT.json", context)
    write_json(root / "history" / stamp / "REPORT.json", report)
    for row in candidate_queue:
        write_json(root / "research_candidates" / f"{row['candidate_id']}.json", row)
    return state


def prepare(repo_root: Path, runtime_root: Path, now: datetime) -> dict[str, Any]:
    context = build_context(repo_root, now)
    runtime_root.mkdir(parents=True, exist_ok=True)
    write_json(runtime_root / "context.json", context)
    (runtime_root / "analyst_prompt.txt").write_text(analyst_prompt(context["review_kind"]) + "\n", encoding="utf-8")
    eligibility = dict(context["eligibility"])
    eligibility["review_kind"] = context["review_kind"]
    eligibility["freeze_sha256"] = context["freeze_sha256"]
    write_json(runtime_root / "eligibility.json", eligibility)
    return eligibility


def prepare_adversarial(runtime_root: Path) -> None:
    context = read_json(runtime_root / "context.json", {}) or {}
    analyst = read_json(runtime_root / "analyst/output.json", None) or blocked_ai("ANALYST_OUTPUT_UNAVAILABLE")
    combined = {"contract": "MONTHLY_AI_LEARNING_COUNCIL_ADVERSARIAL_CONTEXT_v1", "frozen_context": context, "analyst_output": analyst, "freeze_sha256": context.get("freeze_sha256")}
    write_json(runtime_root / "adversarial_context.json", combined)
    (runtime_root / "adversarial_prompt.txt").write_text(adversarial_prompt() + "\n", encoding="utf-8")


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now(UTC)
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--runtime-root", type=Path, required=True)
    p.add_argument("--now")
    p = sub.add_parser("prepare-adversarial")
    p.add_argument("--runtime-root", type=Path, required=True)
    p = sub.add_parser("finalize")
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--runtime-root", type=Path, required=True)
    p.add_argument("--now")
    args = ap.parse_args()
    if args.cmd == "prepare":
        print(json.dumps(prepare(args.repo_root, args.runtime_root, parse_now(args.now)), sort_keys=True))
    elif args.cmd == "prepare-adversarial":
        prepare_adversarial(args.runtime_root)
        print("ADVERSARIAL_CONTEXT_READY")
    else:
        print(json.dumps(finalize(args.repo_root, args.runtime_root, parse_now(args.now)), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
