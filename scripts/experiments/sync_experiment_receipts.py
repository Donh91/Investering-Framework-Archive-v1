#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

CONTRACT = "EXPERIMENT_RECEIPT_SYNC_v1"
HEALTHY_STATES = {"HEALTHY_NEW_DATA", "HEALTHY_NO_CHANGE"}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def fetch(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read())


def parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path: Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text())
    except Exception:
        return None
    return value if isinstance(value, dict) else None


def prior_success_utc(previous: dict[str, Any] | None) -> str | None:
    if not isinstance(previous, dict):
        return None
    explicit = previous.get("last_successful_sync_utc")
    if isinstance(explicit, str) and explicit:
        return explicit
    if previous.get("sync_state") in HEALTHY_STATES or previous.get("status") == "PASS":
        generated = previous.get("generated_at_utc")
        if isinstance(generated, str) and generated:
            return generated
    return None


def classify_sync_state(
    *,
    imported: int,
    hash_mismatches: int,
    fetch_failures: int,
    source_age_hours: float,
    max_source_age_hours: float,
) -> tuple[str, str]:
    if hash_mismatches or fetch_failures:
        return "FAILED", "FAIL"
    if source_age_hours > max_source_age_hours:
        return "STALE", "DEGRADED"
    if imported:
        return "HEALTHY_NEW_DATA", "PASS"
    return "HEALTHY_NO_CHANGE", "PASS"


def unavailable_summary(
    *,
    now: datetime,
    previous: dict[str, Any] | None,
    error_class: str,
) -> dict[str, Any]:
    return {
        "contract": CONTRACT,
        "generated_at_utc": iso(now),
        "sync_state": "UNAVAILABLE",
        "status": "DEGRADED",
        "source_reachable": False,
        "source_manifest_valid": False,
        "source_manifest_sha256": None,
        "source_manifest_generated_at_utc": None,
        "source_manifest_age_hours": None,
        "source_manifest_changed": None,
        "source_receipt_count": None,
        "imported": 0,
        "already_present_verified": 0,
        "hash_mismatches": 0,
        "fetch_failures": 1,
        "last_successful_sync_utc": prior_success_utc(previous),
        "failure_class": error_class,
        "authority": "AUDIT_SYNC_ONLY",
    }


def write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(summary))


def sync_receipts(
    manifest: dict[str, Any],
    receipt_root: Path,
    *,
    fetcher: Callable[[str], dict[str, Any]] = fetch,
) -> tuple[int, int, int, int]:
    imported = hash_mismatches = fetch_failures = already_present_verified = 0
    for item in manifest.get("receipts", []):
        if not isinstance(item, dict):
            fetch_failures += 1
            continue
        receipt_id = item.get("receipt_id")
        expected_sha = item.get("sha256")
        raw_url = item.get("raw_url")
        if not isinstance(receipt_id, str) or not receipt_id or not isinstance(expected_sha, str) or not raw_url:
            fetch_failures += 1
            continue
        path = receipt_root / f"{receipt_id}.json"
        if path.exists():
            existing = load(path)
            if existing is not None and sha256(existing) == expected_sha:
                already_present_verified += 1
            else:
                hash_mismatches += 1
            continue
        try:
            receipt = fetcher(str(raw_url))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError):
            fetch_failures += 1
            continue
        if sha256(receipt) != expected_sha:
            hash_mismatches += 1
            continue
        if receipt.get("receipt_id") != receipt_id:
            hash_mismatches += 1
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical(receipt))
        imported += 1
    return imported, hash_mismatches, fetch_failures, already_present_verified


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest-url", required=True)
    ap.add_argument("--receipt-root", type=Path, required=True)
    ap.add_argument("--sync-output", type=Path, required=True)
    ap.add_argument("--allow-unavailable", action="store_true")
    ap.add_argument("--max-source-age-hours", type=float, default=24.0)
    ap.add_argument("--now-utc")
    args = ap.parse_args()

    now = parse_utc(args.now_utc) if args.now_utc else datetime.now(timezone.utc)
    previous = load(args.sync_output)

    try:
        manifest = fetch(args.manifest_url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError) as exc:
        summary = unavailable_summary(now=now, previous=previous, error_class=type(exc).__name__)
        write_summary(args.sync_output, summary)
        print(json.dumps(summary, sort_keys=True))
        if args.allow_unavailable:
            return
        raise SystemExit(2)

    manifest_sha = sha256(manifest)
    previous_sha = previous.get("source_manifest_sha256") if isinstance(previous, dict) else None
    generated_raw = manifest.get("generated_at_utc")
    receipts = manifest.get("receipts")
    declared_count = manifest.get("receipt_count")
    manifest_valid = (
        manifest.get("contract") == "EXPERIMENT_EXECUTION_RECEIPT_MANIFEST_v1"
        and isinstance(generated_raw, str)
        and isinstance(receipts, list)
        and (declared_count is None or declared_count == len(receipts))
    )
    if not manifest_valid:
        summary = {
            **unavailable_summary(now=now, previous=previous, error_class="INVALID_RECEIPT_MANIFEST"),
            "sync_state": "FAILED",
            "status": "FAIL",
            "source_reachable": True,
            "source_manifest_sha256": manifest_sha,
            "source_manifest_valid": False,
            "fetch_failures": 0,
        }
        write_summary(args.sync_output, summary)
        print(json.dumps(summary, sort_keys=True))
        raise SystemExit(2)

    try:
        source_generated = parse_utc(generated_raw)
    except (TypeError, ValueError):
        summary = {
            **unavailable_summary(now=now, previous=previous, error_class="INVALID_MANIFEST_TIMESTAMP"),
            "sync_state": "FAILED",
            "status": "FAIL",
            "source_reachable": True,
            "source_manifest_sha256": manifest_sha,
            "source_manifest_valid": False,
            "fetch_failures": 0,
        }
        write_summary(args.sync_output, summary)
        print(json.dumps(summary, sort_keys=True))
        raise SystemExit(2)

    source_age_hours = max(0.0, (now - source_generated).total_seconds() / 3600.0)

    imported, mismatches, fetch_failures, already_present = sync_receipts(
        manifest,
        args.receipt_root,
    )
    sync_state, status = classify_sync_state(
        imported=imported,
        hash_mismatches=mismatches,
        fetch_failures=fetch_failures,
        source_age_hours=source_age_hours,
        max_source_age_hours=args.max_source_age_hours,
    )
    summary = {
        "contract": CONTRACT,
        "generated_at_utc": iso(now),
        "sync_state": sync_state,
        "status": status,
        "source_reachable": True,
        "source_manifest_valid": True,
        "source_manifest_sha256": manifest_sha,
        "source_manifest_generated_at_utc": generated_raw,
        "source_manifest_age_hours": round(source_age_hours, 6) if source_age_hours != float("inf") else None,
        "source_manifest_changed": previous_sha != manifest_sha if previous_sha else None,
        "source_receipt_count": len(receipts),
        "imported": imported,
        "already_present_verified": already_present,
        "hash_mismatches": mismatches,
        "fetch_failures": fetch_failures,
        "last_successful_sync_utc": iso(now) if sync_state in HEALTHY_STATES else prior_success_utc(previous),
        "max_source_age_hours": args.max_source_age_hours,
        "authority": "AUDIT_SYNC_ONLY",
    }
    write_summary(args.sync_output, summary)
    print(json.dumps(summary, sort_keys=True))
    if sync_state == "FAILED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
