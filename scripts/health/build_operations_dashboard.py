from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

UTC = timezone.utc
SEVERITY = {"GREEN": 0, "AMBER": 1, "UNKNOWN": 1, "RED": 2}


def parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "MISSING"
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None, "INVALID_JSON"
    return (value, None) if isinstance(value, dict) else (None, "INVALID_SHAPE")


def sha256_path(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() and path.is_file() else None


def first_time(obj: dict[str, Any] | None, keys: Iterable[str]) -> datetime | None:
    if not obj:
        return None
    for key in keys:
        stamp = parse_time(obj.get(key))
        if stamp:
            return stamp
    return None


def normalized_status(value: Any) -> str:
    candidate = str(value or "UNKNOWN").upper()
    if candidate in {"GREEN", "AMBER", "RED"}:
        return candidate
    if candidate in {"PASS", "READY", "COMPLETE", "DURABLE_PASS", "SUCCESS"}:
        return "GREEN"
    if candidate in {"PARTIAL", "DEGRADED", "PENDING", "SKIPPED_NO_DELTA", "UNKNOWN"}:
        return "AMBER"
    if candidate in {"FAIL", "FAILED", "BLOCKED", "SOURCE_UNAVAILABLE"}:
        return "RED"
    return "UNKNOWN"


def combine_status(*values: str) -> str:
    return max(values, key=lambda value: SEVERITY.get(value, 1))


def freshness(timestamp: datetime | None, reference: datetime, green_hours: float, red_hours: float) -> tuple[str, str, float | None]:
    if timestamp is None:
        return "UNKNOWN", "TIMESTAMP_UNAVAILABLE", None
    age = round(max(0.0, (reference - timestamp).total_seconds() / 3600.0), 3)
    if age <= green_hours:
        return "GREEN", "FRESH", age
    if age <= red_hours:
        return "AMBER", "DELAYED", age
    return "RED", "STALE", age


def pointer_entry(repo_root: Path, pointer: Any) -> dict[str, Any]:
    if not isinstance(pointer, dict):
        return {"path": None, "declared_sha256": None, "actual_sha256": None, "hash_status": "UNKNOWN"}
    rel = pointer.get("path") if isinstance(pointer.get("path"), str) else None
    actual = sha256_path(repo_root / rel) if rel else None
    declared = pointer.get("sha256") if isinstance(pointer.get("sha256"), str) else None
    if actual is None:
        state = "MISSING"
    elif declared is None:
        state = "UNDECLARED"
    else:
        state = "MATCH" if actual == declared else "MISMATCH"
    return {"path": rel, "declared_sha256": declared, "actual_sha256": actual, "hash_status": state}


def pointer_object(repo_root: Path, pointer: dict[str, Any]) -> dict[str, Any] | None:
    if not pointer.get("path"):
        return None
    value, _ = read_json(repo_root / pointer["path"])
    return value


def hash_status(pointer: dict[str, Any]) -> str:
    if pointer["hash_status"] == "MATCH":
        return "GREEN"
    if pointer["hash_status"] == "MISMATCH":
        return "RED"
    return "AMBER"


def collect_api_usage(repo_root: Path, reference: datetime) -> dict[str, Any]:
    root = repo_root / "research/api_agent/receipts"
    month = reference.strftime("%Y-%m")
    count = input_tokens = output_tokens = 0
    cost = 0.0
    latest: tuple[datetime, Path, dict[str, Any]] | None = None
    for path in root.rglob("*.json") if root.exists() else []:
        data, error = read_json(path)
        if error or data is None:
            continue
        stamp = first_time(data, ("completed_at_utc", "created_at_utc", "generated_at_utc", "timestamp_utc"))
        if stamp and (latest is None or stamp > latest[0]):
            latest = (stamp, path, data)
        if not stamp or stamp.strftime("%Y-%m") != month:
            continue
        count += 1
        try:
            cost += float(data.get("cost_usd", data.get("estimated_cost_usd", 0)) or 0)
        except (TypeError, ValueError):
            pass
        usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
        for key, target in (("input_tokens", "input"), ("output_tokens", "output")):
            try:
                value = int(usage.get(key, data.get(key, 0)) or 0)
            except (TypeError, ValueError):
                value = 0
            if target == "input":
                input_tokens += value
            else:
                output_tokens += value
    latest_row = None
    if latest:
        latest_row = {
            "path": str(latest[1].relative_to(repo_root)),
            "completed_at_utc": latest[0].isoformat().replace("+00:00", "Z"),
            "status": latest[2].get("status"),
            "model": latest[2].get("model"),
            "task_id": latest[2].get("task_id"),
            "cost_usd": latest[2].get("cost_usd", latest[2].get("estimated_cost_usd")),
        }
    return {"month": month, "receipt_count": count, "cost_usd": round(cost, 6), "input_tokens": input_tokens, "output_tokens": output_tokens, "latest": latest_row}


def build_dashboard(repo_root: Path, reference: datetime | None = None) -> dict[str, Any]:
    reference = reference or datetime.now(UTC)
    handoff, handoff_error = read_json(repo_root / "LATEST_HANDOFF.json")
    automation, automation_error = read_json(repo_root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json")
    architecture, architecture_error = read_json(repo_root / "research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json")
    pointers = handoff.get("pointers", {}) if handoff else {}

    capture_pointer = pointer_entry(repo_root, pointers.get("latest_capture") if isinstance(pointers, dict) else None)
    director_pointer = pointer_entry(repo_root, pointers.get("latest_director_output") if isinstance(pointers, dict) else None)
    weekly_pointer = pointer_entry(repo_root, pointers.get("latest_weekly_output") if isinstance(pointers, dict) else None)
    capture = pointer_object(repo_root, capture_pointer)
    director = pointer_object(repo_root, director_pointer)
    weekly = pointer_object(repo_root, weekly_pointer)

    capture_time = first_time(capture, ("captured_at_utc", "snapshot_utc", "generated_at_utc", "created_at_utc"))
    director_time = first_time(director, ("completed_at_utc", "generated_at_utc", "created_at_utc", "captured_at_utc"))
    weekly_time = first_time(weekly, ("completed_at_utc", "generated_at_utc", "created_at_utc", "freeze_recorded_at_utc"))
    capture_fresh, capture_reason, capture_age = freshness(capture_time, reference, 8, 16)
    director_fresh, director_reason, director_age = freshness(director_time, reference, 12, 30)
    weekly_fresh, weekly_reason, weekly_age = freshness(weekly_time, reference, 24 * 8, 24 * 15)

    director_semantic = normalized_status(director.get("status") if director else None)
    if director and str(director.get("status", "")).upper() == "SKIPPED_NO_DELTA":
        director_semantic = "GREEN"
        director_reason = "EXPECTED_SKIP_NO_COMPARABLE_DELTA"

    systems = {
        "daily_capture": {"status": combine_status(capture_fresh, hash_status(capture_pointer)), "reason": capture_reason, "age_hours": capture_age, "timestamp_utc": capture_time.isoformat().replace("+00:00", "Z") if capture_time else None, "pointer": capture_pointer},
        "openai_daily_director": {"status": combine_status(director_fresh, hash_status(director_pointer), director_semantic), "reason": director_reason, "age_hours": director_age, "timestamp_utc": director_time.isoformat().replace("+00:00", "Z") if director_time else None, "semantic_status": director.get("status") if director else None, "pointer": director_pointer},
        "weekly_output": {"status": combine_status(weekly_fresh, hash_status(weekly_pointer)), "reason": weekly_reason, "age_hours": weekly_age, "timestamp_utc": weekly_time.isoformat().replace("+00:00", "Z") if weekly_time else None, "pointer": weekly_pointer},
        "automation_health": {"status": normalized_status(automation.get("status") if automation else None), "generated_at_utc": automation.get("generated_at_utc") if automation else None, "red_count": automation.get("red_count") if automation else None, "amber_count": automation.get("amber_count") if automation else None, "blockers": automation.get("blockers", []) if automation else [], "input_error": automation_error},
        "architecture_health": {"status": normalized_status(architecture.get("status") if architecture else None), "generated_at_utc": architecture.get("generated_at_utc") if architecture else None, "blockers": architecture.get("blockers", []) if architecture else [], "input_error": architecture_error},
    }

    actions: list[dict[str, Any]] = []
    for name, system in systems.items():
        status = system["status"]
        reason = system.get("reason") or system.get("input_error") or system.get("blockers") or "REQUIRED_INPUT_UNAVAILABLE"
        if status == "RED":
            actions.append({"priority": "P0", "system": name, "reason": reason})
        elif status in {"AMBER", "UNKNOWN"}:
            actions.append({"priority": "P1", "system": name, "reason": reason})
    actions.sort(key=lambda row: (row["priority"], row["system"]))

    overall = "GREEN"
    for system in systems.values():
        overall = combine_status(overall, system["status"])

    dashboard = {
        "contract": "OPERATIONS_DASHBOARD_v1",
        "authority": "OPERATIONAL_OBSERVABILITY_ONLY",
        "generated_at_utc": reference.isoformat().replace("+00:00", "Z"),
        "overall_status": overall,
        "source_status": {"latest_handoff": handoff_error or "PASS", "automation_health": automation_error or "PASS", "architecture_health": architecture_error or "PASS"},
        "systems": systems,
        "agent_activity": {
            "openai_api": collect_api_usage(repo_root, reference),
            "pending_forecast_candidates": len(handoff.get("pending_forecast_candidates", [])) if handoff else 0,
            "codex": {"status": "UNKNOWN", "reason": "NO_DEDICATED_CODEX_DELIVERY_RECEIPT_DISCOVERED_BY_V1"},
        },
        "incidents": {"open_count": len(handoff.get("open_incidents", [])) if handoff else 0, "paths": handoff.get("open_incidents", []) if handoff else []},
        "required_actions": actions,
    }
    canonical = json.dumps(dashboard, sort_keys=True, separators=(",", ":")).encode("utf-8")
    dashboard["dashboard_sha256"] = hashlib.sha256(canonical).hexdigest()
    return dashboard


def render_markdown(data: dict[str, Any]) -> str:
    lines = ["# Operations Dashboard", "", f"Overall: **{data['overall_status']}**", f"Generated: `{data['generated_at_utc']}`", "", "## Systems", "", "| System | Status | Detail | Age hours |", "|---|---:|---|---:|"]
    for name, system in data["systems"].items():
        detail = system.get("reason") or system.get("semantic_status") or "-"
        age = system.get("age_hours")
        lines.append(f"| `{name}` | **{system['status']}** | {detail} | {age if age is not None else '-'} |")
    usage = data["agent_activity"]["openai_api"]
    lines += ["", "## AI activity", "", f"- OpenAI receipts this month: **{usage['receipt_count']}**", f"- OpenAI cost this month: **${usage['cost_usd']:.6f}**", f"- Pending forecast candidates: **{data['agent_activity']['pending_forecast_candidates']}**", f"- Codex attribution: **{data['agent_activity']['codex']['status']}**", "", "## Incidents", "", f"Open incident references: **{data['incidents']['open_count']}**", "", "## Required actions", ""]
    lines.extend(f"- **{row['priority']}** `{row['system']}` - {row['reason']}" for row in data["required_actions"]) if data["required_actions"] else lines.append("- None")
    lines += ["", f"Dashboard SHA-256: `{data['dashboard_sha256']}`", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--md-output", type=Path, required=True)
    parser.add_argument("--reference-time")
    args = parser.parse_args()
    result = build_dashboard(args.repo_root, parse_time(args.reference_time) if args.reference_time else None)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.md_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    args.md_output.write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"status": result["overall_status"], "required_actions": len(result["required_actions"])}, sort_keys=True))


if __name__ == "__main__":
    main()
