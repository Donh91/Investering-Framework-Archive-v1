from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_packets(root: Path, iso_year: int, iso_week: int) -> list[tuple[Path, dict[str, Any]]]:
    packets: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(root.rglob("*.json")):
        if path.name == "LATEST.json" or "weekly" in path.parts:
            continue
        try:
            data = json.loads(path.read_text())
            stamp = datetime.fromisoformat(data["captured_at_utc"].replace("Z", "+00:00"))
        except Exception:
            continue
        y, w, _ = stamp.isocalendar()
        if y == iso_year and w == iso_week:
            packets.append((path, data))
    return packets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--iso-year", type=int)
    parser.add_argument("--iso-week", type=int)
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    current_year, current_week, _ = now.isocalendar()
    iso_year = args.iso_year or current_year
    iso_week = args.iso_week or current_week
    packets = load_packets(args.input_root, iso_year, iso_week)

    status_counts = Counter(packet.get("status", "UNKNOWN") for _, packet in packets)
    owner_status: dict[str, Counter[str]] = {}
    eligible = 0
    source_paths: list[str] = []
    for path, packet in packets:
        source_paths.append(str(path))
        eligible += int(bool(packet.get("weekly_calibration_eligible")))
        for owner in packet.get("owners", []):
            owner_status.setdefault(owner["owner_id"], Counter())[owner.get("status", "UNKNOWN")] += 1

    pack = {
        "contract": "WEEKLY_RAW_CALIBRATION_PACK_v1",
        "authority": "SHADOW_CALIBRATION_INPUT_ONLY",
        "iso_year": iso_year,
        "iso_week": iso_week,
        "generated_at_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "capture_count": len(packets),
        "eligible_capture_count": eligible,
        "capture_status_counts": dict(sorted(status_counts.items())),
        "owner_health": {key: dict(sorted(value.items())) for key, value in sorted(owner_status.items())},
        "source_capture_paths": source_paths,
        "raw_outcome_analysis": False,
        "forecast_evaluation_performed": False,
        "framework_state_change": False,
        "portfolio_action": False,
        "handoff_targets": [
            "RAW_WEEKLY_CALIBRATION",
            "FORECAST_LEDGER_EVALUATION",
            "MASTER_MONDAY_PREP",
            "SPECIALIST_WEEKLY_REVIEW",
        ],
        "readiness": "READY" if eligible >= 15 else "DEGRADED" if eligible else "BLOCKED",
    }

    week_dir = args.output_root / str(iso_year)
    week_dir.mkdir(parents=True, exist_ok=True)
    output = week_dir / f"W{iso_week:02d}.json"
    output.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n")
    pointer = args.output_root / "LATEST_WEEKLY_CALIBRATION.json"
    pointer.write_text(json.dumps({
        "contract": "LATEST_WEEKLY_CALIBRATION_POINTER_v1",
        "path": str(output.relative_to(args.output_root.parent)),
        "iso_year": iso_year,
        "iso_week": iso_week,
        "readiness": pack["readiness"],
        "capture_count": len(packets),
    }, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
