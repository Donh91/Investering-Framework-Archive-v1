#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

CONTRACT = "FORECAST_SKILL_ADMISSION_v1"


def load_optional(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text())


def gate(name: str, status: str, passed: bool, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"gate": name, "status": status, "passed": passed, "details": details or {}}


def build(
    settlement: dict[str, Any] | None,
    replication: dict[str, Any] | None,
    evidence_class: dict[str, Any] | None,
    power: dict[str, Any] | None,
    calibration: dict[str, Any] | None,
    min_effective_n: float,
) -> dict[str, Any]:
    gates = []

    if settlement is None:
        gates.append(gate("SETTLEMENT_TIMING", "MISSING_INPUT", False))
    else:
        scoped = settlement.get("contract") == "MODEL_CALIBRATION_SETTLEMENT_ELIGIBILITY_v1" and settlement.get("eligibility_scope") == "SETTLEMENT_TIMING_ONLY"
        count = int(settlement.get("settlement_eligible_count") or settlement.get("scientific_scored_count") or 0)
        no_skill_authority = settlement.get("scientific_skill_authority") is False
        passed = scoped and no_skill_authority and count > 0
        gates.append(gate("SETTLEMENT_TIMING", "PASS" if passed else "BLOCKED", passed, {"settlement_eligible_count": count, "scope_explicit": scoped, "scientific_skill_authority_false": no_skill_authority}))

    if evidence_class is None:
        gates.append(gate("EVIDENCE_CLASS_SEPARATION", "MISSING_INPUT", False))
    else:
        passed = (
            evidence_class.get("contract") == "FORECAST_EVIDENCE_CLASS_BOUNDARY_AUDIT_v1"
            and evidence_class.get("status") == "PASS"
            and evidence_class.get("cross_evidence_class_pooling_allowed") is False
            and evidence_class.get("forecast_skill_authority") is False
        )
        gates.append(gate("EVIDENCE_CLASS_SEPARATION", "PASS" if passed else "BLOCKED", passed, {"cross_class_pooling_allowed": evidence_class.get("cross_evidence_class_pooling_allowed"), "violation_count": len(evidence_class.get("violations") or [])}))

    if replication is None:
        gates.append(gate("INDEPENDENT_REPLICATION", "MISSING_INPUT", False))
    else:
        passed = replication.get("contract") == "FORECAST_REPLICATION_ELIGIBILITY_v1" and replication.get("status") == "PASS" and replication.get("scientific_skill_authority") is False
        gates.append(gate("INDEPENDENT_REPLICATION", "PASS" if passed else str(replication.get("status") or "BLOCKED"), passed, {
            "independently_assessed_forecast_count": replication.get("independently_assessed_forecast_count"),
            "disagreement_rate": replication.get("disagreement_rate"),
            "max_disagreement_rate": replication.get("max_disagreement_rate"),
        }))

    # Effective-N remains a separate methodological owner. Raw row count is not
    # substituted for effective N, because dependence/redundancy can materially
    # reduce power.
    if power is None:
        gates.append(gate("EFFECTIVE_N", "NOT_ASSESSED_NO_CANONICAL_POWER_AUDIT", False, {"minimum_effective_n": min_effective_n}))
    else:
        effective_n = power.get("effective_n")
        passed = power.get("contract") == "FORECAST_EFFECTIVE_N_AUDIT_v1" and power.get("status") == "PASS" and isinstance(effective_n, (int, float)) and float(effective_n) >= min_effective_n
        gates.append(gate("EFFECTIVE_N", "PASS" if passed else str(power.get("status") or "BLOCKED"), passed, {"effective_n": effective_n, "minimum_effective_n": min_effective_n, "method": power.get("method")}))

    if calibration is None:
        gates.append(gate("CALIBRATION_BASELINE", "NOT_ASSESSED_NO_PREREGISTERED_CALIBRATION_AUDIT", False))
    else:
        passed = calibration.get("contract") == "FORECAST_CALIBRATION_AUDIT_v1" and calibration.get("status") == "PASS" and calibration.get("prospective_only") is True
        gates.append(gate("CALIBRATION_BASELINE", "PASS" if passed else str(calibration.get("status") or "BLOCKED"), passed, {"prospective_only": calibration.get("prospective_only"), "baseline": calibration.get("baseline")}))

    all_pass = bool(gates) and all(item["passed"] for item in gates)
    status = "ELIGIBLE_FOR_PREREGISTERED_SKILL_ANALYSIS" if all_pass else "BLOCKED"
    blockers = [item["gate"] + ":" + item["status"] for item in gates if not item["passed"]]
    return {
        "contract": CONTRACT,
        "status": status,
        "forecast_skill_established": False,
        "skill_analysis_admission_only": True,
        "prospective_only": True,
        "cross_evidence_class_pooling_allowed": False,
        "historical_replay_can_increase_prospective_n": False,
        "minimum_effective_n": min_effective_n,
        "gates": gates,
        "blockers": blockers,
        "authority": {
            "forecast_skill_claim": False,
            "portfolio_action": False,
            "model_weight_change": False,
            "automatic_promotion": False,
            "canonical_promotion": False,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--settlement-eligibility", type=Path)
    ap.add_argument("--replication-eligibility", type=Path)
    ap.add_argument("--evidence-class-audit", type=Path)
    ap.add_argument("--power-audit", type=Path)
    ap.add_argument("--calibration-audit", type=Path)
    ap.add_argument("--min-effective-n", type=float, default=20.0)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = build(
        load_optional(args.settlement_eligibility),
        load_optional(args.replication_eligibility),
        load_optional(args.evidence_class_audit),
        load_optional(args.power_audit),
        load_optional(args.calibration_audit),
        args.min_effective_n,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "forecast_skill_established": False, "blockers": result["blockers"]}, sort_keys=True))


if __name__ == "__main__":
    main()
