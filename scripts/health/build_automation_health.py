from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow-root", type=Path, required=True)
    ap.add_argument("--json-output", type=Path, required=True)
    ap.add_argument("--md-output", type=Path, required=True)
    args = ap.parse_args()

    rows = []
    blockers = []
    for path in sorted(list(args.workflow_root.glob("*.yml")) + list(args.workflow_root.glob("*.yaml"))):
        text = path.read_text(errors="ignore")
        writes = "contents: write" in text and "git push" in text
        scheduled = "schedule:" in text
        uses_openai = "OPENAI_API_KEY" in text or "api_gateway.py" in text
        uses_cfgi = "CFGI_API_KEY" in text or "cfgi_" in text.lower()
        writer_group = None
        match = re.search(r"(?m)^\s*group:\s*([^\n#]+)", text)
        if match:
            writer_group = match.group(1).strip()
        has_abort = "git rebase --abort" in text
        has_readback = "merge-base --is-ancestor" in text
        has_quiet_guard = "git diff --cached --quiet" in text
        risks = []
        if writes and writer_group != "framework-main-writer":
            risks.append("NON_GLOBAL_WRITER_LOCK")
        if writes and not has_abort:
            risks.append("NO_REBASE_ABORT")
        if writes and not has_readback:
            risks.append("NO_MAIN_READBACK")
        if writes and not has_quiet_guard:
            risks.append("NO_EMPTY_COMMIT_GUARD")
        blockers.extend(f"{path.name}:{risk}" for risk in risks)
        rows.append({
            "workflow": path.name,
            "scheduled": scheduled,
            "writes_main": writes,
            "writer_group": writer_group,
            "openai_enabled": uses_openai,
            "cfgi_enabled": uses_cfgi,
            "risks": risks,
        })

    status = "GREEN" if not blockers else "AMBER"
    result = {
        "contract": "AUTOMATION_HEALTH_INVENTORY_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": status,
        "workflow_count": len(rows),
        "writer_count": sum(row["writes_main"] for row in rows),
        "openai_workflow_count": sum(row["openai_enabled"] for row in rows),
        "cfgi_workflow_count": sum(row["cfgi_enabled"] for row in rows),
        "blockers": sorted(set(blockers)),
        "workflows": rows,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    lines = ["# Automation Health", f"Status: **{status}**", f"Workflows: {len(rows)}", f"Writers: {result['writer_count']}", f"OpenAI-enabled: {result['openai_workflow_count']}", f"CFGI-enabled: {result['cfgi_workflow_count']}", "", "## Findings"]
    lines += [f"- {item}" for item in result["blockers"]] or ["- None"]
    args.md_output.write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": status, "blockers": len(result["blockers"])}, sort_keys=True))


if __name__ == "__main__":
    main()
