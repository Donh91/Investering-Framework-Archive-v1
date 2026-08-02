from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_capture_indexes(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    rows: list[tuple[Path, dict[str, Any]]] = []
    for path in root.rglob("*.json"):
        try:
            value = json.loads(path.read_text())
        except Exception:
            continue
        if value.get("contract") == "DAILY_RAW_CAPTURE_INDEX_v1":
            rows.append((path, value))
    rows.sort(key=lambda item: item[1].get("captured_at_utc", ""))
    return rows


def compact_owner(owner: dict[str, Any]) -> dict[str, Any]:
    summaries: list[dict[str, Any]] = []
    for item in owner.get("files", []):
        summary = item.get("summary")
        if summary:
            summaries.append({
                "path": item.get("path"),
                "summary": summary,
                "sha256": item.get("sha256"),
            })
    return {
        "owner_id": owner.get("owner_id"),
        "status": owner.get("status", "UNKNOWN"),
        "collector_exit_code": owner.get("collector_exit_code"),
        "file_count": owner.get("file_count", 0),
        "total_bytes": owner.get("total_bytes", 0),
        "summaries": summaries,
    }


def owner_status_map(capture: dict[str, Any]) -> dict[str, str]:
    return {str(o.get("owner_id")): str(o.get("status", "UNKNOWN")) for o in capture.get("owners", [])}


def build_context(rows: list[tuple[Path, dict[str, Any]]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("no_daily_capture_indexes")
    latest_path, latest = rows[-1]
    previous_path, previous = rows[-2] if len(rows) > 1 else (None, None)
    latest_status = owner_status_map(latest)
    previous_status = owner_status_map(previous) if previous else {}
    transitions = []
    for owner_id in sorted(set(latest_status) | set(previous_status)):
        transitions.append({
            "owner_id": owner_id,
            "previous_status": previous_status.get(owner_id, "UNKNOWN"),
            "latest_status": latest_status.get(owner_id, "UNKNOWN"),
            "changed": previous_status.get(owner_id) != latest_status.get(owner_id),
        })
    pass_count = sum(1 for v in latest_status.values() if v == "PASS")
    context = {
        "contract": "OWNER_BOUND_DAILY_DIRECTOR_CONTEXT_v1",
        "authority": "SHADOW_ONLY",
        "canonical_data_ping": False,
        "latest_capture": {
            "path": str(latest_path),
            "captured_at_utc": latest.get("captured_at_utc"),
            "run_id": latest.get("run_id"),
            "capture_status": latest.get("capture_status"),
            "calibration_eligible": latest.get("calibration_eligible"),
            "owners": [compact_owner(o) for o in latest.get("owners", [])],
        },
        "previous_capture": None if previous is None else {
            "path": str(previous_path),
            "captured_at_utc": previous.get("captured_at_utc"),
            "run_id": previous.get("run_id"),
            "capture_status": previous.get("capture_status"),
        },
        "owner_status_transitions": transitions,
        "coverage": {
            "owner_count": len(latest_status),
            "pass_count": pass_count,
            "pass_ratio": round(pass_count / len(latest_status), 4) if latest_status else 0.0,
        },
        "limitations": [
            "Compact indexes preserve lineage and selected summaries, not every raw market value.",
            "No missing value may be inferred from file size, status, or neighboring captures.",
            "This context cannot create canonical truth, framework state, model weights, or portfolio action.",
        ],
    }
    context["context_hash"] = sha256(context)
    return context


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = load_capture_indexes(args.capture_root)
    context = build_context(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(context))
    print(json.dumps({"status": "PASS", "captures_found": len(rows), "context_hash": context["context_hash"]}, sort_keys=True))


if __name__ == "__main__":
    main()
