#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

HISTORY_CONTRACT = "AUTOMATION_HEALTH_RUN_STATUS_v1"
RESOLUTION_CONTRACT = "SOURCE_QA_INCIDENT_RESOLUTION_v1"


def canonical_hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def write_new_json(path: Path, value: dict[str, Any]) -> bool:
    body = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path.exists():
        if path.read_text(encoding="utf-8") == body:
            return False
        raise ValueError(f"IMMUTABLE_EVIDENCE_CONFLICT:{path.as_posix()}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return True


def record_status(repo_root: Path, run_id: int, run_attempt: int) -> Path:
    health_path = repo_root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
    health = read_json(health_path)
    if not health or not health.get("generated_at_utc"):
        raise ValueError("AUTOMATION_HEALTH_UNAVAILABLE")
    receipt: dict[str, Any] = {
        "contract": HISTORY_CONTRACT,
        "run_id": run_id,
        "run_attempt": run_attempt,
        "generated_at_utc": health.get("generated_at_utc"),
        "status": health.get("status"),
        "red_count": int(health.get("red_count") or 0),
        "amber_count": int(health.get("amber_count") or 0),
        "source_path": "research/architecture_health/LATEST_AUTOMATION_HEALTH.json",
        "source_sha256": hashlib.sha256(health_path.read_bytes()).hexdigest(),
    }
    receipt["receipt_sha256"] = canonical_hash({k: v for k, v in receipt.items() if k != "receipt_sha256"})
    out = repo_root / "research/architecture_health/history" / f"{run_id}-attempt-{run_attempt}.json"
    write_new_json(out, receipt)
    return out


def valid_history(path: Path) -> dict[str, Any] | None:
    data = read_json(path)
    if data.get("contract") != HISTORY_CONTRACT:
        return None
    declared = str(data.get("receipt_sha256") or "")
    actual = canonical_hash({k: v for k, v in data.items() if k != "receipt_sha256"})
    if not declared or declared != actual:
        return None
    return data


def resolved_incidents(repo_root: Path) -> set[str]:
    root = repo_root / "09_SOURCE_QA/incidents/resolutions"
    resolved: set[str] = set()
    for path in sorted(root.glob("*.json")) if root.exists() else []:
        data = read_json(path)
        if data.get("contract") == RESOLUTION_CONTRACT and data.get("incident_path"):
            resolved.add(str(data["incident_path"]))
    return resolved


def resolve_recovered(repo_root: Path, run_id: int) -> list[str]:
    history_root = repo_root / "research/architecture_health/history"
    rows: list[dict[str, Any]] = []
    for path in sorted(history_root.glob("*.json")) if history_root.exists() else []:
        data = valid_history(path)
        if data:
            rows.append(data)
    rows.sort(key=lambda x: (str(x.get("generated_at_utc") or ""), int(x.get("run_id") or 0), int(x.get("run_attempt") or 0)))
    if len(rows) < 2:
        return []
    recent = rows[-2:]
    if any(int(row.get("red_count") or 0) != 0 for row in recent):
        return []
    incident_root = repo_root / "09_SOURCE_QA/incidents"
    already = resolved_incidents(repo_root)
    created: list[str] = []
    resolved_at = str(recent[-1].get("generated_at_utc") or "")
    for incident in sorted(incident_root.glob("INCIDENT_automation-production-health-*.md")) if incident_root.exists() else []:
        rel = incident.relative_to(repo_root).as_posix()
        if rel in already:
            continue
        receipt = {
            "contract": RESOLUTION_CONTRACT,
            "incident_path": rel,
            "owner": "automation-production-health",
            "successful_run_id": run_id,
            "successful_run_conclusion": "success",
            "resolved_at_utc": resolved_at,
        }
        out = incident_root / "resolutions" / f"{incident.stem}.json"
        if write_new_json(out, receipt):
            created.append(out.relative_to(repo_root).as_posix())
    return created


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    rec = sub.add_parser("record")
    rec.add_argument("--repo-root", type=Path, default=Path("."))
    rec.add_argument("--run-id", type=int, required=True)
    rec.add_argument("--run-attempt", type=int, required=True)
    res = sub.add_parser("resolve")
    res.add_argument("--repo-root", type=Path, default=Path("."))
    res.add_argument("--run-id", type=int, required=True)
    args = parser.parse_args()
    if args.command == "record":
        path = record_status(args.repo_root, args.run_id, args.run_attempt)
        print(json.dumps({"status": "RECORDED", "path": path.relative_to(args.repo_root).as_posix()}, sort_keys=True))
    else:
        created = resolve_recovered(args.repo_root, args.run_id)
        print(json.dumps({"status": "RESOLVED" if created else "NOOP", "created": created}, sort_keys=True))


if __name__ == "__main__":
    main()
