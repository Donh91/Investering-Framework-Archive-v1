from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.health.build_operations_dashboard import build_dashboard, parse_time, render_markdown


def finalize_dashboard(data: dict) -> dict:
    existing = {(row.get("priority"), row.get("system")) for row in data.get("required_actions", [])}
    for name, system in data.get("systems", {}).items():
        if system.get("status") != "UNKNOWN" or ("P1", name) in existing:
            continue
        reason = system.get("reason") or system.get("input_error") or "REQUIRED_INPUT_UNAVAILABLE"
        data.setdefault("required_actions", []).append({
            "priority": "P1",
            "system": name,
            "reason": reason,
        })
    data["required_actions"] = sorted(
        data.get("required_actions", []),
        key=lambda row: (row.get("priority", "P9"), row.get("system", "")),
    )
    data.pop("dashboard_sha256", None)
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
    data["dashboard_sha256"] = hashlib.sha256(canonical).hexdigest()
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--md-output", type=Path, required=True)
    parser.add_argument("--reference-time")
    args = parser.parse_args()
    reference = parse_time(args.reference_time) if args.reference_time else None
    result = finalize_dashboard(build_dashboard(args.repo_root, reference))
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.md_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    args.md_output.write_text(render_markdown(result), encoding="utf-8")
    print(json.dumps({"status": result["overall_status"], "required_actions": len(result["required_actions"])}, sort_keys=True))


if __name__ == "__main__":
    main()
