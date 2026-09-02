#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

from forecast_evidence_class import (  # noqa: E402
    AUTOMATED_EXPERIMENT,
    LEGACY_UNCLASSIFIED,
    OWNER_RATIFIED,
    EvidenceClassError,
    classify_forecast_evidence,
    evidence_class_authority,
    scientific_pool_compatibility_key,
)

AUDIT_CONTRACT = "FORECAST_EVIDENCE_CLASS_BOUNDARY_AUDIT_v1"


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def iter_forecasts(root: Path):
    if not root.exists():
        return
    for path in sorted(root.rglob("*.json")):
        try:
            value = json.loads(path.read_text())
        except Exception:
            continue
        if value.get("contract") == "FROZEN_FORECAST_v1":
            yield path, value


def audit_root(root: Path, expected_class: str, role: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    for path, record in iter_forecasts(root) or []:
        try:
            evidence_class = classify_forecast_evidence(record)
            pool_key = scientific_pool_compatibility_key(record)
            authority = evidence_class_authority(evidence_class)
        except EvidenceClassError as exc:
            rows.append({"path": path.as_posix(), "role": role, "evidence_class": "CONFLICT", "scientific_pool_compatibility_key": None})
            violations.append({"path": path.as_posix(), "role": role, "error": str(exc)})
            continue

        row = {
            "path": path.as_posix(),
            "role": role,
            "forecast_id": record.get("forecast_id"),
            "frozen_at_utc": record.get("frozen_at_utc"),
            "evidence_class": evidence_class,
            "scientific_pool_compatibility_key": pool_key,
            "authority": authority,
        }
        rows.append(row)

        # Historical rows may remain unclassified, but an explicitly classified
        # prospective record must never appear in the opposite evidence root.
        if evidence_class != LEGACY_UNCLASSIFIED and evidence_class != expected_class:
            violations.append({
                "path": path.as_posix(),
                "role": role,
                "error": "EVIDENCE_CLASS_ROOT_MISMATCH",
                "expected_class": expected_class,
                "actual_class": evidence_class,
            })
    return rows, violations


def build_audit(owner_root: Path, experiment_root: Path) -> dict[str, Any]:
    owner_rows, owner_violations = audit_root(owner_root, OWNER_RATIFIED, "API_AGENT_OWNER_RATIFICATION")
    experiment_rows, experiment_violations = audit_root(experiment_root, AUTOMATED_EXPERIMENT, "AUTOMATED_SCIENTIFIC_EXPERIMENT")
    rows = owner_rows + experiment_rows
    violations = owner_violations + experiment_violations
    counts: dict[str, int] = {}
    for row in rows:
        cls = str(row.get("evidence_class") or "UNKNOWN")
        counts[cls] = counts.get(cls, 0) + 1
    return {
        "contract": AUDIT_CONTRACT,
        "status": "FAIL" if violations else "PASS",
        "cross_evidence_class_pooling_allowed": False,
        "forecast_skill_authority": False,
        "legacy_unclassified_pooling_allowed": False,
        "owner_root": owner_root.as_posix(),
        "experiment_root": experiment_root.as_posix(),
        "record_count": len(rows),
        "evidence_class_counts": counts,
        "violations": violations,
        "records": rows,
        "authority": {
            "portfolio_action": False,
            "framework_state_change": False,
            "model_weight_change": False,
            "canonical_promotion": False,
            "forecast_skill_claim": False,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner-root", type=Path, required=True)
    ap.add_argument("--experiment-root", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    result = build_audit(args.owner_root, args.experiment_root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(canon(result))
    print(json.dumps({
        "status": result["status"],
        "record_count": result["record_count"],
        "evidence_class_counts": result["evidence_class_counts"],
        "violation_count": len(result["violations"]),
        "cross_evidence_class_pooling_allowed": False,
    }, sort_keys=True))
    if result["violations"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
