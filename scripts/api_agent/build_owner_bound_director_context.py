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
        if value.get("contract") in {"DAILY_RAW_CAPTURE_INDEX_v1", "DAILY_RAW_CAPTURE_INDEX_v2"}:
            rows.append((path, value))
    rows.sort(key=lambda item: item[1].get("captured_at_utc", ""))
    return rows


def compact_owner(owner: dict[str, Any]) -> dict[str, Any]:
    summaries = []
    for item in owner.get("files", []):
        if item.get("summary"):
            summaries.append({"path": item.get("path"), "summary": item["summary"], "sha256": item.get("sha256")})
    return {
        "owner_id": owner.get("owner_id"),
        "status": owner.get("status", "UNKNOWN"),
        "collector_exit_code": owner.get("collector_exit_code"),
        "file_count": owner.get("file_count", 0),
        "summaries": summaries,
    }


def owner_status_map(capture: dict[str, Any] | None) -> dict[str, str]:
    if not capture:
        return {}
    return {str(o.get("owner_id")): str(o.get("status", "UNKNOWN")) for o in capture.get("owners", [])}


def numeric_deltas(latest: Any, previous: Any, prefix: str = "") -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if isinstance(latest, dict):
        previous = previous if isinstance(previous, dict) else {}
        for key in sorted(latest):
            out.extend(numeric_deltas(latest[key], previous.get(key), f"{prefix}.{key}" if prefix else key))
    elif isinstance(latest, (int, float)) and not isinstance(latest, bool):
        row: dict[str, Any] = {"metric": prefix, "latest": latest, "previous": previous if isinstance(previous, (int, float)) and not isinstance(previous, bool) else None}
        if row["previous"] is not None:
            row["absolute_change"] = latest - row["previous"]
            row["percentage_change"] = round((latest / row["previous"] - 1.0) * 100.0, 8) if row["previous"] else None
        out.append(row)
    return out


def build_context(rows: list[tuple[Path, dict[str, Any]]]) -> dict[str, Any]:
    if not rows:
        raise ValueError("no_daily_capture_indexes")
    latest_path, latest = rows[-1]
    previous_path, previous = rows[-2] if len(rows) > 1 else (None, None)
    latest_status = owner_status_map(latest)
    previous_status = owner_status_map(previous)
    transitions = [{
        "owner_id": owner_id,
        "previous_status": previous_status.get(owner_id, "UNKNOWN"),
        "latest_status": latest_status.get(owner_id, "UNKNOWN"),
        "changed": previous_status.get(owner_id) != latest_status.get(owner_id),
    } for owner_id in sorted(set(latest_status) | set(previous_status))]
    pass_count = sum(v == "PASS" for v in latest_status.values())
    latest_metrics = latest.get("market_metrics", {})
    previous_metrics = previous.get("market_metrics", {}) if previous else {}
    deltas = numeric_deltas(latest_metrics, previous_metrics)
    comparable = sum(row.get("previous") is not None for row in deltas)

    context = {
        "contract": "OWNER_BOUND_DAILY_DIRECTOR_CONTEXT_v2",
        "authority": "SHADOW_ONLY",
        "canonical_data_ping": False,
        "latest_capture": {
            "path": str(latest_path), "captured_at_utc": latest.get("captured_at_utc"), "run_id": latest.get("run_id"),
            "status": latest.get("status"), "owners": [compact_owner(o) for o in latest.get("owners", [])], "market_metrics": latest_metrics,
        },
        "previous_capture": None if previous is None else {
            "path": str(previous_path), "captured_at_utc": previous.get("captured_at_utc"), "run_id": previous.get("run_id"),
            "status": previous.get("status"), "market_metrics": previous_metrics,
        },
        "owner_status_transitions": transitions,
        "metric_deltas": deltas,
        "coverage": {
            "owner_count": len(latest_status), "pass_count": pass_count,
            "pass_ratio": round(pass_count / len(latest_status), 4) if latest_status else 0.0,
            "latest_numeric_metrics": len(deltas), "comparable_numeric_metrics": comparable,
        },
        "limitations": [
            "Only explicitly materialized compact metrics may be compared.",
            "Missing metrics remain unknown and may not be inferred.",
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
    print(json.dumps({"status": "PASS", "captures_found": len(rows), "context_hash": context["context_hash"], "comparable_metrics": context["coverage"]["comparable_numeric_metrics"]}, sort_keys=True))


if __name__ == "__main__":
    main()
