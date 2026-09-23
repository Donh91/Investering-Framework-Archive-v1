from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

RELATIONSHIP_CLASSES = {
    "CORRELATED",
    "NONLINEARLY_DEPENDENT",
    "REDUNDANT",
    "UNIQUE",
    "SYNERGISTIC",
    "REGIME_DEPENDENT",
    "UNSTABLE",
    "DATA_BLOCKED",
}
PRESENTATION_ROLES = {"PRIMARY", "VALIDATION", "AUDIT_ONLY", "DATA_BLOCKED", "UNRESOLVED"}
HISTORICAL_SOURCE = "06_RESEARCH_LAB/audit_summaries/2026-07-22__public-repo-methods-closed-lab-audit__shadow.md"


def historical_rows(audit_text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    nonlinear_markers = (
        "ETH/BTC 20-day momentum versus ETH/BTC 14-day volatility",
        "Spearman correlation: approximately 0.10",
        "Distance correlation: approximately 0.41",
        "stable across eight subsamples",
    )
    if all(marker in audit_text for marker in nonlinear_markers):
        rows.append({
            "relationship_id": "HIST_ETHBTC_MOMENTUM_VOLATILITY",
            "sensor_or_test_ids": ["ETHBTC_20D_MOMENTUM", "ETHBTC_14D_VOLATILITY"],
            "relationship_classes": ["NONLINEARLY_DEPENDENT"],
            "evidence_class": "HISTORICAL_PROXY_AUDIT",
            "sample_status": {"aligned_daily_rows": 2886, "subsamples": 8},
            "current_prospective_validation": False,
            "presentation_role": "AUDIT_ONLY",
            "source_refs": [HISTORICAL_SOURCE],
        })
    synergy_markers = (
        "BTC 20-day momentum",
        "ETH relative participation proxy",
        "AUC around 0.72",
        "performance weakened in the 2022-2024 subperiod",
    )
    if all(marker in audit_text for marker in synergy_markers):
        rows.append({
            "relationship_id": "HIST_BTC_MOMENTUM_ETH_PARTICIPATION_SURVIVAL",
            "sensor_or_test_ids": ["BTC_20D_MOMENTUM", "ETH_RELATIVE_PARTICIPATION_PROXY"],
            "relationship_classes": ["SYNERGISTIC", "REGIME_DEPENDENT"],
            "evidence_class": "HISTORICAL_PROXY_AUDIT",
            "sample_status": {"aligned_daily_rows": 2886, "sequence_episodes": 124},
            "current_prospective_validation": False,
            "presentation_role": "AUDIT_ONLY",
            "source_refs": [HISTORICAL_SOURCE],
        })
    return rows


def prospective_row(candidate: dict[str, Any]) -> dict[str, Any]:
    state = str(candidate.get("state") or "UNKNOWN")
    admission = str(candidate.get("scientific_admission_status") or "UNKNOWN")
    classes: list[str] = []
    if admission == "SEMANTIC_DUPLICATE_KEEP_SHADOW":
        classes = ["REDUNDANT"]
        role = "AUDIT_ONLY"
    elif state in {"WAITING_FOR_DATA", "WAITING_FOR_MAPPING"}:
        classes = ["DATA_BLOCKED"]
        role = "DATA_BLOCKED"
    else:
        role = "UNRESOLVED"
    return {
        "relationship_id": str(candidate.get("candidate_id")),
        "sensor_or_test_ids": [str(candidate.get("title") or candidate.get("candidate_id"))],
        "relationship_classes": classes,
        "evidence_class": "PROSPECTIVE_CURRENT",
        "sample_status": {
            "state": state,
            "scientific_admission_status": admission,
            "observation_count": int(candidate.get("observation_count") or 0),
            "matured_outcome_count": int(candidate.get("matured_outcome_count") or 0),
        },
        "current_prospective_validation": bool(candidate.get("matured_outcome_count", 0)),
        "presentation_role": role,
        "source_refs": [
            f"research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json#{candidate.get('candidate_id')}"
        ],
        "semantic_fingerprint": candidate.get("semantic_fingerprint"),
    }


def build_readout(registry: dict[str, Any], audit_text: str) -> dict[str, Any]:
    candidates = registry.get("candidates") if isinstance(registry.get("candidates"), list) else []
    sensor_candidates = [
        candidate for candidate in candidates
        if isinstance(candidate, dict) and candidate.get("kind") == "SENSOR_COMBINATION"
    ]
    prospective = sorted(
        (prospective_row(candidate) for candidate in sensor_candidates),
        key=lambda row: row["relationship_id"],
    )
    groups: dict[str, list[str]] = {}
    for row in prospective:
        fp = row.get("semantic_fingerprint")
        if isinstance(fp, str) and fp:
            groups.setdefault(fp, []).append(row["relationship_id"])
    duplicate_groups = [
        {"semantic_fingerprint": fp, "candidate_ids": sorted(ids), "presentation_rule": "COUNT_ONCE_MAXIMUM"}
        for fp, ids in sorted(groups.items())
        if len(ids) > 1
    ]
    historical = historical_rows(audit_text)
    all_rows = historical + prospective
    for row in all_rows:
        if any(value not in RELATIONSHIP_CLASSES for value in row["relationship_classes"]):
            raise ValueError("non-canonical relationship class")
        if row["presentation_role"] not in PRESENTATION_ROLES:
            raise ValueError("non-canonical presentation role")

    return {
        "contract": "SENSOR_RELATIONSHIP_COMPRESSION_READOUT_v1",
        "generated_from_registry_at_utc": registry.get("generated_at_utc"),
        "authority": {
            "research_only": True,
            "binding": False,
            "canonical_market_state": False,
            "market_gate_change": False,
            "model_weight_change": False,
            "portfolio_action": False,
            "automatic_sensor_promotion": False,
            "automatic_sensor_retirement": False,
        },
        "canonical_relationship_vocabulary": sorted(RELATIONSHIP_CLASSES),
        "presentation_roles": sorted(PRESENTATION_ROLES),
        "historical_rows": historical,
        "prospective_rows": prospective,
        "semantic_duplicate_groups": duplicate_groups,
        "rules": {
            "low_linear_correlation_implies_unique": False,
            "historical_proxy_counts_as_current_validation": False,
            "aligned_sensor_count_adds_conviction": False,
            "unresolved_relationships_fail_closed": True,
            "presentation_roles_are_weights": False,
        },
        "source_refs": [
            "01_CORE_FRAMEWORK/governance/2026-07-22__sensor-relationship-and-incremental-value-standard__canonical.md",
            HISTORICAL_SOURCE,
            "research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"))
    parser.add_argument("--historical-audit", type=Path, default=Path(HISTORICAL_SOURCE))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    result = build_readout(registry, args.historical_audit.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "prospective_rows": len(result["prospective_rows"]), "historical_rows": len(result["historical_rows"])}, sort_keys=True))


if __name__ == "__main__":
    main()
