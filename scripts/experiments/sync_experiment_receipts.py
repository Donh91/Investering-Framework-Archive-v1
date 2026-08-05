#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def fetch(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=60) as response:
        return json.loads(response.read())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest-url", required=True)
    ap.add_argument("--receipt-root", type=Path, required=True)
    ap.add_argument("--sync-output", type=Path, required=True)
    ap.add_argument("--allow-unavailable", action="store_true")
    args = ap.parse_args()
    try:
        manifest = fetch(args.manifest_url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        if args.allow_unavailable:
            print(json.dumps({"status": "UNAVAILABLE", "error": str(exc)}, sort_keys=True))
            return
        raise
    if manifest.get("contract") != "EXPERIMENT_EXECUTION_RECEIPT_MANIFEST_v1":
        raise SystemExit("invalid_receipt_manifest_contract")
    imported = mismatches = 0
    for item in manifest.get("receipts", []):
        receipt = fetch(item["raw_url"])
        if sha256(receipt) != item["sha256"]:
            mismatches += 1
            continue
        path = args.receipt_root / f"{receipt['receipt_id']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(canonical(receipt))
            imported += 1
    summary = {
        "contract": "EXPERIMENT_RECEIPT_SYNC_v1",
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_manifest_sha256": sha256(manifest),
        "source_receipt_count": len(manifest.get("receipts", [])),
        "imported": imported,
        "hash_mismatches": mismatches,
        "status": "FAIL" if mismatches else "PASS",
        "authority": "AUDIT_SYNC_ONLY",
    }
    args.sync_output.parent.mkdir(parents=True, exist_ok=True)
    args.sync_output.write_bytes(canonical(summary))
    print(json.dumps(summary, sort_keys=True))
    if mismatches:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
