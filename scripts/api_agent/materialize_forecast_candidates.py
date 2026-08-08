from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def existing_candidates(root: Path) -> dict[str, Path]:
    found: dict[str, Path] = {}
    for path in root.rglob("*.json") if root.exists() else []:
        try:
            value = load(path)
        except Exception:
            continue
        candidate_id = value.get("candidate_id")
        if isinstance(candidate_id, str) and candidate_id:
            found.setdefault(candidate_id, path)
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--pending-root", type=Path, required=True)
    parser.add_argument("--materialization-receipt", type=Path)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    created: list[dict[str, str]] = []
    duplicate_skipped: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    output = load(args.output)
    source_receipt = load(args.receipt)
    known = existing_candidates(args.pending_root)

    try:
        for index, candidate in enumerate(output.get("forecast_candidates", []), 1):
            candidate_id = hashlib.sha256(canon({"receipt": source_receipt.get("output_hash"), "index": index, "candidate": candidate})).hexdigest()[:24]
            if candidate_id in known:
                duplicate_skipped.append({"candidate_id": candidate_id, "existing_path": str(known[candidate_id])})
                continue
            material = {
                "contract": "FORECAST_CANDIDATE_v2",
                "authority": "UNRATIFIED_RESEARCH_ONLY",
                "candidate_id": candidate_id,
                "observed_at_utc": now.isoformat().replace("+00:00", "Z"),
                "created_at_utc": now.isoformat().replace("+00:00", "Z"),
                "model": source_receipt.get("model"),
                "task": source_receipt.get("task"),
                "prompt_sha256": source_receipt.get("prompt_hash"),
                "context_sha256": source_receipt.get("context_hash"),
                "source_output_sha256": source_receipt.get("output_hash"),
                "candidate": candidate,
                "ratification_status": "PENDING",
                "self_promotion_allowed": False,
            }
            path = args.pending_root / f"{now:%Y/%m/%d}" / f"{candidate_id}.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(canon(material))
            readback = load(path)
            if readback != material:
                raise RuntimeError(f"readback_mismatch:{path}")
            created.append({"candidate_id": candidate_id, "path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
            known[candidate_id] = path
    except Exception as exc:
        errors.append({"error": type(exc).__name__, "detail": str(exc)[:400]})

    receipt = {
        "contract": "MATERIALIZATION_RECEIPT_v1",
        "status": "PASS" if not errors else "FAILED",
        "created_at_utc": now.isoformat().replace("+00:00", "Z"),
        "source_output_sha256": source_receipt.get("output_hash"),
        "created": created,
        "duplicate_skipped": duplicate_skipped,
        "errors": errors,
    }
    receipt["receipt_sha256"] = hashlib.sha256(canon(receipt)).hexdigest()
    receipt_path = args.materialization_receipt or (args.pending_root / "LATEST_MATERIALIZATION_RECEIPT.json")
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_bytes(canon(receipt))
    if load(receipt_path) != receipt:
        raise SystemExit("MATERIALIZATION_RECEIPT_READBACK_FAILED")
    print(json.dumps(receipt, sort_keys=True))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
