from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def parse_ts(raw: Any) -> datetime | None:
    try:
        value = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return value.astimezone(timezone.utc)
    except Exception:
        return None


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


def metric_bearing_v2(value: dict[str, Any]) -> bool:
    return value.get("contract") == "DAILY_RAW_CAPTURE_INDEX_v2" and bool(value.get("market_metrics"))


def compact_owner(owner: dict[str, Any]) -> dict[str, Any]:
    summaries = []
    for item in owner.get("files", []):
        if item.get("summary"):
            summaries.append({"path": item.get("path"), "summary": item["summary"], "sha256": item.get("sha256")})
    return {"owner_id": owner.get("owner_id"), "status": owner.get("status", "UNKNOWN"), "collector_exit_code": owner.get("collector_exit_code"), "file_count": owner.get("file_count", 0), "summaries": summaries}


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
    predecessor: tuple[Path, dict[str, Any]] | None = None
    for candidate in reversed(rows[:-1]):
        if metric_bearing_v2(candidate[1]):
            predecessor = candidate
            break
    previous_path, previous = predecessor if predecessor else (None, None)
    latest_status = owner_status_map(latest)
    previous_status = owner_status_map(previous)
    transitions = [{"owner_id": owner_id, "previous_status": previous_status.get(owner_id, "UNKNOWN"), "latest_status": latest_status.get(owner_id, "UNKNOWN"), "changed": previous_status.get(owner_id) != latest_status.get(owner_id)} for owner_id in sorted(set(latest_status) | set(previous_status))]
    latest_metrics = latest.get("market_metrics", {})
    previous_metrics = previous.get("market_metrics", {}) if previous else {}
    deltas = numeric_deltas(latest_metrics, previous_metrics)
    comparable = sum(row.get("previous") is not None for row in deltas)
    latest_ts = parse_ts(latest.get("captured_at_utc"))
    previous_ts = parse_ts(previous.get("captured_at_utc")) if previous else None
    age_hours = round((latest_ts - previous_ts).total_seconds() / 3600, 3) if latest_ts and previous_ts else None
    delta_status = "DELTA_READY" if comparable > 0 else "DELTA_UNAVAILABLE"
    if age_hours is not None and age_hours > 48:
        delta_status = "DELTA_DEGRADED_STALE_PREDECESSOR"
    pass_count = sum(v == "PASS" for v in latest_status.values())
    context = {
        "contract": "OWNER_BOUND_DAILY_DIRECTOR_CONTEXT_v3",
        "authority": "SHADOW_ONLY",
        "canonical_data_ping": False,
        "latest_capture": {"path": str(latest_path), "captured_at_utc": latest.get("captured_at_utc"), "run_id": latest.get("run_id"), "status": latest.get("status"), "owners": [compact_owner(o) for o in latest.get("owners", [])], "market_metrics": latest_metrics},
        "previous_capture": None if previous is None else {"path": str(previous_path), "captured_at_utc": previous.get("captured_at_utc"), "run_id": previous.get("run_id"), "status": previous.get("status"), "market_metrics": previous_metrics},
        "predecessor_path": str(previous_path) if previous_path else None,
        "predecessor_sha256": sha256(previous) if previous else None,
        "predecessor_selection_rule": "latest_metric_bearing_v2",
        "predecessor_age_hours": age_hours,
        "delta_status": delta_status,
        "owner_status_transitions": transitions,
        "metric_deltas": deltas,
        "coverage": {"owner_count": len(latest_status), "pass_count": pass_count, "pass_ratio": round(pass_count / len(latest_status), 4) if latest_status else 0.0, "latest_numeric_metrics": len(deltas), "comparable_numeric_metrics": comparable},
        "limitations": ["Only explicitly materialized compact metrics may be compared.", "Missing metrics remain unknown and may not be inferred.", "This context cannot create canonical truth, framework state, model weights, or portfolio action."],
    }
    context["context_hash"] = sha256(context)
    return context


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    context = build_context(load_capture_indexes(args.capture_root))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(context))
    print(json.dumps({"status": context["delta_status"], "context_hash": context["context_hash"], "comparable_metrics": context["coverage"]["comparable_numeric_metrics"]}, sort_keys=True))


if __name__ == "__main__":
    main()
