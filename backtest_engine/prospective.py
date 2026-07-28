from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from typing import Iterable, Mapping

ALLOWED_RECEIPT_KINDS = {
    "FREEZE",
    "DENIAL",
    "TRIGGER",
    "SUPERSESSION",
    "CLOSEOUT",
    "NO_ACTION",
}

REQUIRED_FIELDS = {
    "schema_version",
    "receipt_kind",
    "event_id",
    "policy_family",
    "rule_version",
    "knowledge_at_utc",
    "decision_at_utc",
    "execution_at_utc",
    "label_end_utc",
    "captured_at_utc",
    "state_before",
    "state_after",
    "action_permission",
    "source_artifact_ids",
    "source_hashes",
    "transaction_cost_contract",
    "overlap_cluster_key",
    "owner_registry_version",
    "source_authority_status",
    "rule_frozen_before_outcome",
    "holdout_touched",
}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timezone-aware UTC timestamp required")
    return parsed


def canonical_json(payload: Mapping) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def content_sha256(payload: Mapping) -> str:
    material = dict(payload)
    material.pop("receipt_sha256", None)
    return hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()


def validate_receipt(
    receipt: Mapping,
    *,
    policy_families: Iterable[str] | None = None,
    max_capture_delay_seconds: int = 1800,
) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_FIELDS - set(receipt)
    if missing:
        return [f"missing required fields: {sorted(missing)}"]

    if receipt["schema_version"] != "PROSPECTIVE_DECISION_RECEIPT_v1":
        errors.append("unsupported schema_version")
    if receipt["receipt_kind"] not in ALLOWED_RECEIPT_KINDS:
        errors.append("invalid receipt_kind")
    if policy_families is not None and receipt["policy_family"] not in set(policy_families):
        errors.append("unknown policy_family")

    try:
        knowledge = _parse_utc(str(receipt["knowledge_at_utc"]))
        decision = _parse_utc(str(receipt["decision_at_utc"]))
        execution = _parse_utc(str(receipt["execution_at_utc"]))
        label_end = _parse_utc(str(receipt["label_end_utc"]))
        captured = _parse_utc(str(receipt["captured_at_utc"]))
    except (TypeError, ValueError) as exc:
        errors.append(str(exc))
        return errors

    if not knowledge <= decision <= execution < label_end:
        errors.append("temporal order violation")
    capture_delay = (captured - decision).total_seconds()
    if capture_delay < 0:
        errors.append("captured_at precedes decision_at")
    if capture_delay > max_capture_delay_seconds:
        errors.append("capture delay exceeds frozen maximum")
    if captured >= label_end:
        errors.append("receipt captured after label horizon")

    source_ids = receipt["source_artifact_ids"]
    source_hashes = receipt["source_hashes"]
    if not isinstance(source_ids, list) or not source_ids:
        errors.append("source_artifact_ids must be a non-empty list")
    if not isinstance(source_hashes, list) or not source_hashes:
        errors.append("source_hashes must be a non-empty list")
    if isinstance(source_ids, list) and isinstance(source_hashes, list) and len(source_ids) != len(source_hashes):
        errors.append("source_artifact_ids and source_hashes length mismatch")
    if isinstance(source_hashes, list):
        for value in source_hashes:
            if not SHA256_RE.fullmatch(str(value)):
                errors.append("source_hashes must contain lowercase SHA-256 values")
                break

    if receipt["action_permission"] == "NONE":
        if not receipt.get("no_action_reason"):
            errors.append("NONE action requires no_action_reason")
        if execution != decision:
            errors.append("NONE action requires execution_at == decision_at")

    if not receipt["transaction_cost_contract"]:
        errors.append("transaction_cost_contract required")
    if not receipt["overlap_cluster_key"]:
        errors.append("overlap_cluster_key required")
    if not receipt["owner_registry_version"]:
        errors.append("owner_registry_version required")
    if receipt["source_authority_status"] not in {
        "OWNER",
        "APPROVED_DIRECT_CHALLENGER",
        "MIXED_APPROVED",
        "NOT_APPLICABLE",
    }:
        errors.append("source authority is not policy-scoreable")
    if receipt["rule_frozen_before_outcome"] is not True:
        errors.append("rule must be frozen before outcome")
    if receipt["holdout_touched"] is not False:
        errors.append("holdout_touched must be false")

    supplied_hash = receipt.get("receipt_sha256")
    if supplied_hash is not None and supplied_hash != content_sha256(receipt):
        errors.append("receipt_sha256 mismatch")
    return errors


def finalize_receipt(receipt: Mapping) -> dict:
    output = dict(receipt)
    output["receipt_sha256"] = content_sha256(output)
    if not output.get("receipt_id"):
        date = str(output["decision_at_utc"])[:10].replace("-", "")
        output["receipt_id"] = f"PDR-{date}-{output['receipt_sha256'][:12]}"
        output["receipt_sha256"] = content_sha256(output)
    return output


def classify_receipt(receipt: Mapping, *, policy_families: Iterable[str]) -> str:
    return "A_FULLY_REPLAYABLE" if not validate_receipt(receipt, policy_families=policy_families) else "INVALID_OR_NON_A"


def summarize_accumulation(
    receipts: Iterable[Mapping],
    *,
    policy_families: Iterable[str],
    preferred_rows_per_family: int = 5,
) -> dict:
    families = tuple(policy_families)
    counts = Counter()
    clusters: dict[str, set[str]] = defaultdict(set)
    invalid: list[str] = []
    for receipt in receipts:
        family = str(receipt.get("policy_family", "UNKNOWN"))
        receipt_id = str(receipt.get("receipt_id", receipt.get("event_id", "UNKNOWN")))
        errors = validate_receipt(receipt, policy_families=families)
        if errors:
            invalid.append(receipt_id)
            continue
        counts[family] += 1
        clusters[family].add(str(receipt["overlap_cluster_key"]))

    per_family = {}
    for family in families:
        a_rows = counts[family]
        unique_clusters = len(clusters[family])
        per_family[family] = {
            "A_rows": a_rows,
            "unique_overlap_clusters": unique_clusters,
            "preferred_rows": preferred_rows_per_family,
            "economic_ranking_ready": a_rows >= preferred_rows_per_family and unique_clusters >= preferred_rows_per_family,
        }
    return {
        "status": "PASS" if not invalid else "PARTIAL",
        "valid_A_rows": sum(counts.values()),
        "invalid_receipts": invalid,
        "per_policy_family": per_family,
        "actual_policy_replay_unlocked": any(v["economic_ranking_ready"] for v in per_family.values()),
    }
