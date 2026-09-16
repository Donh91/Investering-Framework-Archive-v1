from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_path(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def build_consumer_receipt(
    repo_root: Path,
    manifest_path: Path,
    consumer: str,
    declared_consumed_evidence: list[str],
    *,
    consumed_at_utc: str | None = None,
    max_manifest_age_seconds: int | None = None,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    now = consumed_at_utc or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    now_dt = parse_time(now)
    declared = list(dict.fromkeys(str(name) for name in declared_consumed_evidence if str(name)))
    manifest_sha256 = sha256_path(manifest_path)

    if not manifest:
        return {
            "contract": "CONSUMER_RECEIPT_v1",
            "consumer": consumer,
            "status": "UNAVAILABLE",
            "consumption_state": "UNKNOWN",
            "consumed_at_utc": now,
            "manifest_path": str(manifest_path),
            "manifest_sha256": manifest_sha256,
            "manifest_generated_at_utc": None,
            "manifest_age_seconds": None,
            "manifest_freshness_status": "UNKNOWN",
            "max_manifest_age_seconds": max_manifest_age_seconds,
            "expected_evidence": [],
            "declared_consumed_evidence": declared,
            "verified_evidence": {},
            "missing_expected_evidence": [],
            "unavailable_expected_evidence": [],
            "stale_declared_evidence": [],
            "unexpected_declared_evidence": declared,
            "reason": "HANDOFF_MANIFEST_UNAVAILABLE",
        }

    manifest_generated = manifest.get("generated_at_utc")
    manifest_dt = parse_time(manifest_generated)
    manifest_age_seconds: float | None = None
    manifest_freshness_status = "NOT_ENFORCED"
    freshness_reason: str | None = None
    if max_manifest_age_seconds is not None:
        if now_dt is None or manifest_dt is None:
            manifest_freshness_status = "UNKNOWN"
            freshness_reason = "HANDOFF_MANIFEST_FRESHNESS_UNKNOWN"
        else:
            manifest_age_seconds = round((now_dt - manifest_dt).total_seconds(), 3)
            if manifest_age_seconds < 0:
                manifest_freshness_status = "UNKNOWN"
                freshness_reason = "HANDOFF_MANIFEST_FROM_FUTURE"
            elif manifest_age_seconds > max_manifest_age_seconds:
                manifest_freshness_status = "STALE"
                freshness_reason = "HANDOFF_MANIFEST_STALE"
            else:
                manifest_freshness_status = "PASS"

    consumers = manifest.get("consumers") if isinstance(manifest.get("consumers"), dict) else {}
    expected_raw = consumers.get(consumer)
    if not isinstance(expected_raw, list):
        return {
            "contract": "CONSUMER_RECEIPT_v1",
            "consumer": consumer,
            "status": "UNAVAILABLE",
            "consumption_state": "UNKNOWN",
            "consumed_at_utc": now,
            "manifest_path": str(manifest_path.relative_to(repo_root)) if manifest_path.is_relative_to(repo_root) else str(manifest_path),
            "manifest_sha256": manifest_sha256,
            "manifest_generated_at_utc": manifest_generated,
            "manifest_age_seconds": manifest_age_seconds,
            "manifest_freshness_status": manifest_freshness_status,
            "max_manifest_age_seconds": max_manifest_age_seconds,
            "expected_evidence": [],
            "declared_consumed_evidence": declared,
            "verified_evidence": {},
            "missing_expected_evidence": [],
            "unavailable_expected_evidence": [],
            "stale_declared_evidence": [],
            "unexpected_declared_evidence": declared,
            "reason": "CONSUMER_NOT_REGISTERED",
        }

    expected = list(dict.fromkeys(str(name) for name in expected_raw if str(name)))
    evidence = manifest.get("evidence") if isinstance(manifest.get("evidence"), dict) else {}
    expected_set = set(expected)
    declared_set = set(declared)
    verified: dict[str, dict[str, Any]] = {}
    stale: list[str] = []
    declared_without_ref: list[str] = []

    for name in declared:
        ref = evidence.get(name)
        if not isinstance(ref, dict):
            declared_without_ref.append(name)
            continue
        rel = ref.get("path")
        declared_sha = ref.get("sha256")
        if not isinstance(rel, str) or not isinstance(declared_sha, str):
            declared_without_ref.append(name)
            continue
        actual_sha = sha256_path(repo_root / rel)
        if actual_sha != declared_sha:
            stale.append(name)
            continue
        verified[name] = {"path": rel, "sha256": declared_sha}

    missing_expected = [name for name in expected if name not in declared_set]
    unavailable_expected = [name for name in expected if not isinstance(evidence.get(name), dict)]
    unexpected = [name for name in declared if name not in expected_set]
    unverified_declared = sorted(set(stale + declared_without_ref))

    reasons: list[str] = []
    if missing_expected:
        reasons.append("EXPECTED_EVIDENCE_NOT_DECLARED")
    if unavailable_expected:
        reasons.append("EXPECTED_EVIDENCE_UNAVAILABLE")
    if unexpected:
        reasons.append("UNEXPECTED_EVIDENCE_DECLARED")
    if unverified_declared:
        reasons.append("DECLARED_EVIDENCE_NOT_BYTE_VERIFIED")
    if freshness_reason:
        reasons.append(freshness_reason)

    status = "PASS" if not reasons else "PARTIAL"
    consumption_state = "VERIFIED" if status == "PASS" else "DEGRADED"

    return {
        "contract": "CONSUMER_RECEIPT_v1",
        "consumer": consumer,
        "status": status,
        "consumption_state": consumption_state,
        "consumed_at_utc": now,
        "manifest_path": str(manifest_path.relative_to(repo_root)) if manifest_path.is_relative_to(repo_root) else str(manifest_path),
        "manifest_sha256": manifest_sha256,
        "manifest_generated_at_utc": manifest_generated,
        "manifest_age_seconds": manifest_age_seconds,
        "manifest_freshness_status": manifest_freshness_status,
        "max_manifest_age_seconds": max_manifest_age_seconds,
        "expected_evidence": expected,
        "declared_consumed_evidence": declared,
        "verified_evidence": verified,
        "missing_expected_evidence": missing_expected,
        "unavailable_expected_evidence": unavailable_expected,
        "stale_declared_evidence": unverified_declared,
        "unexpected_declared_evidence": unexpected,
        "reasons": reasons,
        "semantics": "PRODUCER_SUCCESS_IS_NOT_SYSTEM_SUCCESS_WITHOUT_VERIFIED_CONSUMER_RECEIPT",
    }


def stamp_target(
    repo_root: Path,
    manifest_path: Path,
    consumer: str,
    target: Path,
    declared: list[str],
    self_hash_field: str | None,
    max_manifest_age_seconds: int | None = None,
) -> dict[str, Any]:
    value = load_json(target)
    if value is None:
        raise SystemExit("TARGET_JSON_UNAVAILABLE")
    if self_hash_field:
        value.pop(self_hash_field, None)
    receipt = build_consumer_receipt(
        repo_root,
        manifest_path,
        consumer,
        declared,
        max_manifest_age_seconds=max_manifest_age_seconds,
    )
    value["consumer_receipt"] = receipt
    if self_hash_field:
        value[self_hash_field] = hashlib.sha256(canonical(value)).hexdigest()
    target.write_bytes(canonical(value))
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--consumer", required=True)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--declared", action="append", default=[])
    parser.add_argument("--self-hash-field")
    parser.add_argument("--max-manifest-age-seconds", type=int)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    target = args.target if args.target.is_absolute() else root / args.target
    receipt = stamp_target(
        root,
        manifest,
        args.consumer,
        target,
        args.declared,
        args.self_hash_field,
        args.max_manifest_age_seconds,
    )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
