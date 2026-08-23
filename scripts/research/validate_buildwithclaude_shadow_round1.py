#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
ROUND = ROOT / "06_RESEARCH_LAB" / "buildwithclaude_shadow_round1_v1"
PROTOCOLS = ROOT / "06_RESEARCH_LAB" / "protocols"

EXPECTED_IDS = {
    "BWC-R1-C1-PROPERTY-INVARIANTS",
    "BWC-R1-C2-MUTATION",
    "BWC-R1-C3-SESSION-TELEMETRY",
    "BWC-R1-C4-GUARDRAILS",
}

EXPECTED_COMPLEXITY_KEYS = {
    "maintenance",
    "dependencies",
    "api_or_token_cost",
    "latency",
    "source_fragility",
    "security_privacy",
    "governance_burden",
    "correlated_failure_risk",
}

REQUIRED_FILES = [
    ROUND / "ROUND_CONTRACT.md",
    ROUND / "ROUND1_CANDIDATES.json",
    PROTOCOLS / "SHADOW_IDEA_ADMISSION_RULE_v1.md",
    PROTOCOLS / "SHADOW_IDEA_ADMISSION_TEMPLATE_v1.json",
    ROOT / "scripts/research/shadow_property_invariant_probe.py",
    ROOT / "scripts/research/shadow_mutation_probe.py",
    ROOT / "scripts/research/shadow_session_telemetry.py",
    ROOT / "scripts/research/shadow_guardrail_probe.py",
    ROOT / ".github/workflows/buildwithclaude-shadow-round1.yml",
]


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def nonempty_list(obj: Any) -> bool:
    return isinstance(obj, list) and bool(obj) and all(str(x).strip() for x in obj)


def main() -> int:
    failures: List[str] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            failures.append(f"missing required file: {path.relative_to(ROOT)}")

    if failures:
        print(json.dumps({"status": "FAIL", "failures": failures}, indent=2, sort_keys=True))
        return 1

    spec = load_json(ROUND / "ROUND1_CANDIDATES.json")
    template = load_json(PROTOCOLS / "SHADOW_IDEA_ADMISSION_TEMPLATE_v1.json")

    if spec.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        failures.append("round authority must be RESEARCH_ONLY_NON_CANONICAL")
    for key in (
        "canonical_effect",
        "portfolio_execution",
        "paid_data_authorized",
        "external_provider_calls_authorized",
    ):
        if spec.get(key) is not False:
            failures.append(f"round {key} must be false")

    candidates = spec.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 4:
        failures.append("round must contain exactly four candidates")
        candidates = candidates if isinstance(candidates, list) else []

    ids = [str(c.get("id")) for c in candidates if isinstance(c, dict)]
    if set(ids) != EXPECTED_IDS or len(ids) != len(set(ids)):
        failures.append(f"candidate ids mismatch or duplicate: {ids}")

    for candidate in candidates:
        if not isinstance(candidate, dict):
            failures.append("candidate entry must be an object")
            continue
        cid = candidate.get("id", "UNKNOWN")
        if candidate.get("classification") != "SHADOW_CANDIDATE":
            failures.append(f"{cid}: classification must remain SHADOW_CANDIDATE")
        for field in ("problem_to_solve", "existing_capability_overlap", "promotion_gate"):
            if not str(candidate.get(field, "")).strip():
                failures.append(f"{cid}: missing {field}")
        for field in ("success_criteria", "failure_criteria", "rollback_criteria"):
            if not nonempty_list(candidate.get(field)):
                failures.append(f"{cid}: {field} must be non-empty")
        tax = candidate.get("complexity_tax")
        if not isinstance(tax, dict):
            failures.append(f"{cid}: complexity_tax missing")
        else:
            missing = EXPECTED_COMPLEXITY_KEYS - set(tax)
            if missing:
                failures.append(f"{cid}: complexity_tax missing {sorted(missing)}")
            for key in EXPECTED_COMPLEXITY_KEYS:
                if key in tax and not str(tax.get(key, "")).strip():
                    failures.append(f"{cid}: complexity_tax {key} empty")

    decision = spec.get("decision")
    if not isinstance(decision, dict):
        failures.append("round decision missing")
    else:
        if decision.get("classification") != "SHADOW_TESTING":
            failures.append("round decision classification must be SHADOW_TESTING")
        if decision.get("review_required_before_any_promotion") is not True:
            failures.append("review_required_before_any_promotion must be true")
        if decision.get("market_decision_authority_permitted") is not False:
            failures.append("market_decision_authority_permitted must be false")
        if decision.get("measurably_better_after_complexity_tax") is not None:
            failures.append("complexity-tax verdict must remain null before evidence")

    allowed = set(template.get("allowed_classifications") or [])
    required_classes = {
        "ARCHIVE_ONLY",
        "SHADOW_CANDIDATE",
        "SHADOW_TESTING",
        "FORWARD_TEST",
        "OPERATIONAL_HELPER",
        "CANONICAL_CANDIDATE",
        "CANONICAL",
        "RETIRED",
    }
    if allowed != required_classes:
        failures.append("admission template classifications mismatch")
    if template.get("default_state") != "SHADOW_CANDIDATE":
        failures.append("admission template default_state must be SHADOW_CANDIDATE")
    template_decision = template.get("decision") or {}
    if template_decision.get("review_required_before_canonical_promotion") is not True:
        failures.append("admission template must require canonical review")

    report = {
        "contract": "BUILDWITHCLAUDE_SHADOW_ROUND1_STATIC_VALIDATION_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "candidate_count": len(candidates),
        "candidate_ids": sorted(ids),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
