#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "research/dataset_registry/DATASET_REGISTRY_v1.json"
POLICY = ROOT / "research/programs/MARKET_ANTICIPATION_RESEARCH_PROGRAM_v1/DATASET_STORAGE_POLICY_v1.md"
ALLOWED = {"T0_GIT_METADATA", "T1_GIT_COMPACT_CANONICAL", "T2_ACTIONS_ARTIFACT", "T3_DURABLE_BULK", "T4_EXTERNAL_LICENSED"}


def main() -> int:
    failures: list[str] = []
    if not POLICY.is_file():
        failures.append("missing storage policy")
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ids: set[str] = set()
    for row in data.get("datasets", []):
        dataset_id = row.get("dataset_id")
        if not dataset_id or dataset_id in ids:
            failures.append(f"invalid or duplicate dataset_id: {dataset_id}")
        ids.add(dataset_id)
        for field in ("raw_storage_class", "normalized_storage_class", "metadata_storage_class", "durable_target"):
            if row.get(field) not in ALLOWED:
                failures.append(f"{dataset_id}: invalid {field}")
        if row.get("metadata_storage_class") != "T0_GIT_METADATA":
            failures.append(f"{dataset_id}: metadata must remain T0")
        if row.get("raw_storage_class") in {"T0_GIT_METADATA", "T1_GIT_COMPACT_CANONICAL"}:
            failures.append(f"{dataset_id}: raw bulk data may not default to Git")
        if row.get("enumeration_authorized") is not False:
            failures.append(f"{dataset_id}: enumeration must remain false")
        if not row.get("partitioning") or not row.get("preferred_format"):
            failures.append(f"{dataset_id}: missing partitioning or format")
        if not isinstance(row.get("retention_days"), int) or row["retention_days"] <= 0:
            failures.append(f"{dataset_id}: invalid retention")
    authority = data.get("authority", {})
    if any(authority.get(k) is not False for k in ("framework_state_change", "model_weight_change", "portfolio_action")):
        failures.append("registry authority must remain closed")
    print(json.dumps({"status": "PASS" if not failures else "FAIL", "datasets": len(ids), "failures": failures}, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
