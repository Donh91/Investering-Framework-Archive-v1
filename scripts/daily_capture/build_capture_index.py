from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OWNER_DIRS = {
    "fred_macro": "fred-owner-output",
    "binance_spot": "binance-spot-owner-output",
    "binance_microstructure": "binance-spot-microstructure-output",
    "okx_swap": "okx-swap-owner-output",
    "top100_breadth": "top100-breadth-owner-output",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compact_json_summary(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {}
    wanted = {
        "status", "run_id", "snapshot_id", "retrieval_timestamp_utc",
        "retrieval_timestamp", "freeze_timestamp_utc", "as_of_utc",
        "rows", "row_count", "constituent_count", "membership_hash",
        "capture_integrity", "freshness_status", "source", "venue",
    }
    if isinstance(data, dict):
        return {k: data[k] for k in wanted if k in data}
    return {}


def owner_record(root: Path, owner_id: str, relative_dir: str, exit_codes: dict[str, int]) -> dict[str, Any]:
    directory = root / relative_dir
    files: list[dict[str, Any]] = []
    if directory.exists():
        for path in sorted(p for p in directory.rglob("*") if p.is_file()):
            item: dict[str, Any] = {
                "path": str(path.relative_to(root)),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            if path.suffix.lower() == ".json":
                summary = compact_json_summary(path)
                if summary:
                    item["summary"] = summary
            files.append(item)
    code = int(exit_codes.get(owner_id, 999))
    return {
        "owner_id": owner_id,
        "collector_exit_code": code,
        "status": "PASS" if code == 0 and files else "FAIL" if code != 0 else "EMPTY",
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--status-file", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--trigger", required=True)
    args = parser.parse_args()

    exit_codes = json.loads(args.status_file.read_text())
    captured_at = datetime.now(timezone.utc).replace(microsecond=0)
    owners = [owner_record(args.root, key, value, exit_codes) for key, value in OWNER_DIRS.items()]
    passed = sum(owner["status"] == "PASS" for owner in owners)
    overall = "COMPLETE" if passed == len(owners) else "PARTIAL" if passed else "FAILED"

    packet = {
        "contract": "DAILY_RAW_CAPTURE_INDEX_v1",
        "authority": "SHADOW_OBSERVATION_ONLY",
        "run_id": args.run_id,
        "captured_at_utc": captured_at.isoformat().replace("+00:00", "Z"),
        "trigger": args.trigger,
        "status": overall,
        "owners_passed": passed,
        "owners_planned": len(owners),
        "owners": owners,
        "artifact_retention_days": 7,
        "canonical_data_ping": False,
        "framework_state_change": False,
        "portfolio_action": False,
        "weekly_calibration_eligible": passed >= 3,
    }

    day_dir = args.output_root / captured_at.strftime("%Y/%m/%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    output = day_dir / f"{captured_at.strftime('%H%M%S')}_{args.run_id}.json"
    output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")

    latest = args.output_root / "LATEST.json"
    latest.write_text(json.dumps({
        "contract": "DAILY_RAW_CAPTURE_LATEST_POINTER_v1",
        "path": str(output.relative_to(args.output_root.parent)),
        "run_id": args.run_id,
        "captured_at_utc": packet["captured_at_utc"],
        "status": overall,
    }, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
