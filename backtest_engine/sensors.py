from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable


SENSOR_ROLES = {
    "CORE_TRANSITION_SIGNAL",
    "CONFIRMATION_VETO",
    "RISK_CONTEXT",
    "DESCRIPTIVE_CONTEXT",
    "SOURCE_QA",
    "EXPERIMENTAL",
}

AUTHORITY_LEVELS = {
    "PERMIT_AND_VETO",
    "VETO_ONLY",
    "CONTEXT_ONLY",
    "QA_ONLY",
    "NO_AUTHORITY",
}

LIFECYCLE_STATES = {"CORE", "RETAINED", "SHADOW", "EXPERIMENTAL", "RETIRED"}


@dataclass(frozen=True)
class SensorDefinition:
    sensor_id: str
    cluster_id: str
    role: str
    authority: str
    lifecycle: str
    direct_required: bool
    owner_method_id: str | None
    fallback_policy: str
    decision_uses: tuple[str, ...]

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.sensor_id:
            errors.append("sensor_id is required")
        if not self.cluster_id:
            errors.append("cluster_id is required")
        if self.role not in SENSOR_ROLES:
            errors.append(f"unsupported role: {self.role}")
        if self.authority not in AUTHORITY_LEVELS:
            errors.append(f"unsupported authority: {self.authority}")
        if self.lifecycle not in LIFECYCLE_STATES:
            errors.append(f"unsupported lifecycle: {self.lifecycle}")
        if self.direct_required and not self.owner_method_id:
            errors.append("direct-required sensors need an owner_method_id")
        if self.authority in {"PERMIT_AND_VETO", "VETO_ONLY"} and self.role not in {
            "CORE_TRANSITION_SIGNAL", "CONFIRMATION_VETO", "RISK_CONTEXT"
        }:
            errors.append("permit/veto authority requires a signal, confirmation or risk role")
        if not self.fallback_policy:
            errors.append("fallback_policy is required")
        return errors


def validate_sensor_registry(rows: Iterable[SensorDefinition]) -> dict[str, object]:
    errors: list[dict[str, object]] = []
    seen: set[str] = set()
    clusters: dict[str, list[str]] = defaultdict(list)
    role_counts: dict[str, int] = defaultdict(int)
    lifecycle_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        if row.sensor_id in seen:
            errors.append({"sensor_id": row.sensor_id, "errors": ["duplicate sensor_id"]})
        seen.add(row.sensor_id)
        clusters[row.cluster_id].append(row.sensor_id)
        role_counts[row.role] += 1
        lifecycle_counts[row.lifecycle] += 1
        row_errors = row.validate()
        if row_errors:
            errors.append({"sensor_id": row.sensor_id, "errors": row_errors})
    return {
        "status": "PASS" if not errors else "FAIL",
        "sensor_count": len(seen),
        "dependency_cluster_count": len(clusters),
        "clusters": {key: sorted(value) for key, value in sorted(clusters.items())},
        "role_counts": dict(sorted(role_counts.items())),
        "lifecycle_counts": dict(sorted(lifecycle_counts.items())),
        "errors": errors,
    }


def cluster_aware_evidence_count(sensor_ids: Iterable[str], registry: dict[str, SensorDefinition]) -> dict[str, object]:
    raw: list[str] = []
    clusters: dict[str, list[str]] = defaultdict(list)
    unknown: list[str] = []
    for sensor_id in sensor_ids:
        raw.append(sensor_id)
        sensor = registry.get(sensor_id)
        if sensor is None:
            unknown.append(sensor_id)
            continue
        clusters[sensor.cluster_id].append(sensor_id)
    return {
        "raw_sensor_count": len(raw),
        "independent_cluster_count": len(clusters),
        "clusters": {key: sorted(value) for key, value in sorted(clusters.items())},
        "unknown_sensor_ids": sorted(unknown),
    }
