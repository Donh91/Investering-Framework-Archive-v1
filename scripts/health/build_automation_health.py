from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UTC = timezone.utc
WRITER_GROUP = "framework-main-writer"
GOOD_CONCLUSIONS = {"success", "neutral", "skipped"}
LIFECYCLE_STATES = {"ACTIVE", "EXPECTED_BLOCK", "PENDING_FIRST_EXPECTED_RUN", "RETIRED"}


def utc_now() -> datetime:
    return datetime.now(UTC)


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


def api_json(url: str, token: str) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "investering-framework-health-auditor",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def _directive(text: str, key: str) -> str | None:
    match = re.search(rf"(?mi)^\s*#\s*{re.escape(key)}:\s*([^\n#]+?)\s*$", text)
    return match.group(1).strip() if match else None


def workflow_static(path: Path) -> dict[str, Any]:
    text = path.read_text(errors="ignore")
    writes = "contents: write" in text and "git push" in text
    scheduled = "schedule:" in text
    manual = "workflow_dispatch:" in text
    uses_openai = "OPENAI_API_KEY" in text or "api_gateway.py" in text
    uses_cfgi = "CFGI_API_KEY" in text or "cfgi_" in text.lower()
    writer_group = None
    match = re.search(r"(?m)^\s*group:\s*([^\n#]+)", text)
    if match:
        writer_group = match.group(1).strip().strip("'\"")
    cron_count = len(re.findall(r"(?m)^\s*-\s*cron:\s*", text))
    permissions = sorted(set(re.findall(r"(?m)^\s{2}([a-z-]+):\s*(read|write|none)\s*$", text)))

    lifecycle_raw = (_directive(text, "framework-lifecycle") or "ACTIVE").upper()
    lifecycle_state = lifecycle_raw if lifecycle_raw in LIFECYCLE_STATES else "INVALID"
    lifecycle_reason = _directive(text, "framework-lifecycle-reason")
    expected_exit_raw = _directive(text, "framework-expected-exit")
    expected_exit = None
    if expected_exit_raw is not None:
        try:
            expected_exit = int(expected_exit_raw)
        except ValueError:
            expected_exit = None

    risks: list[str] = []
    if lifecycle_state == "INVALID":
        risks.append("INVALID_LIFECYCLE_STATE")
    if writes and writer_group != WRITER_GROUP:
        risks.append("NON_GLOBAL_WRITER_LOCK")
    if writes and "git rebase --abort" not in text:
        risks.append("NO_REBASE_ABORT")
    if writes and "merge-base --is-ancestor" not in text and "git show origin/main:" not in text:
        risks.append("NO_MAIN_READBACK")
    if writes and "git diff --cached --quiet" not in text:
        risks.append("NO_EMPTY_COMMIT_GUARD")
    if "pull_request_target:" in text and ("contents: write" in text or "secrets." in text):
        risks.append("PR_TARGET_WITH_WRITE_OR_SECRET")
    if scheduled and "timezone:" not in text:
        risks.append("SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE")
    if "actions/upload-artifact@" in text and "retention-days:" not in text:
        risks.append("ARTIFACT_RETENTION_UNBOUNDED")

    if lifecycle_state == "EXPECTED_BLOCK":
        if scheduled:
            risks.append("EXPECTED_BLOCK_HAS_SCHEDULE")
        if not lifecycle_reason:
            risks.append("EXPECTED_BLOCK_REASON_MISSING")
        if expected_exit != 78:
            risks.append("EXPECTED_BLOCK_EXIT_CODE_INVALID")
        if "exit 78" not in text:
            risks.append("EXPECTED_BLOCK_EXIT_CONTRACT_MISSING")
    elif lifecycle_state == "PENDING_FIRST_EXPECTED_RUN" and not scheduled:
        risks.append("PENDING_FIRST_RUN_NOT_SCHEDULED")
    elif lifecycle_state == "RETIRED" and scheduled:
        risks.append("RETIRED_WORKFLOW_STILL_SCHEDULED")

    return {
        "workflow": path.name,
        "path": str(path),
        "scheduled": scheduled,
        "manual": manual,
        "cron_count": cron_count,
        "writes_main": writes,
        "writer_group": writer_group,
        "openai_enabled": uses_openai,
        "cfgi_enabled": uses_cfgi,
        "permissions": [{"scope": scope, "level": level} for scope, level in permissions],
        "lifecycle_state": lifecycle_state,
        "lifecycle_reason": lifecycle_reason,
        "expected_exit_code": expected_exit,
        "static_risks": risks,
    }


def leading_streak(conclusions: list[str | None], good: bool) -> int:
    count = 0
    for conclusion in conclusions:
        is_good = conclusion in GOOD_CONCLUSIONS
        if is_good != good:
            break
        count += 1
    return count


def live_workflows(repo: str, token: str) -> dict[str, dict[str, Any]]:
    owner, name = repo.split("/", 1)
    base = f"https://api.github.com/repos/{owner}/{name}"
    workflows = api_json(f"{base}/actions/workflows?per_page=100", token).get("workflows", [])
    result: dict[str, dict[str, Any]] = {}
    for workflow in workflows:
        wid = workflow["id"]
        runs = api_json(f"{base}/actions/workflows/{wid}/runs?per_page=10", token).get("workflow_runs", [])
        latest = runs[0] if runs else None
        recent_completed = [r for r in runs if r.get("status") == "completed"]
        conclusions = [r.get("conclusion") for r in recent_completed]
        recent_failures = [r for r in recent_completed if r.get("conclusion") not in GOOD_CONCLUSIONS]
        result[Path(workflow["path"]).name] = {
            "workflow_id": wid,
            "name": workflow.get("name"),
            "state": workflow.get("state"),
            "html_url": workflow.get("html_url"),
            "latest_run": None if not latest else {
                "id": latest.get("id"),
                "event": latest.get("event"),
                "status": latest.get("status"),
                "conclusion": latest.get("conclusion"),
                "created_at": latest.get("created_at"),
                "updated_at": latest.get("updated_at"),
                "run_attempt": latest.get("run_attempt"),
                "html_url": latest.get("html_url"),
                "head_sha": latest.get("head_sha"),
            },
            "recent_completed_count": len(recent_completed),
            "recent_failure_count": len(recent_failures),
            "recent_conclusions": conclusions[:5],
            "success_streak": leading_streak(conclusions, True),
            "failure_streak": leading_streak(conclusions, False),
        }
    return result


def classify(row: dict[str, Any], now: datetime) -> tuple[str, list[str]]:
    findings = list(row.get("static_risks", []))
    live = row.get("live") or {}
    latest = live.get("latest_run")
    lifecycle = row.get("lifecycle_state") or "ACTIVE"

    if not live:
        findings.append("WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE")
    elif live.get("state") != "active":
        findings.append("WORKFLOW_NOT_ACTIVE")

    if lifecycle == "EXPECTED_BLOCK":
        findings.append("EXPECTED_BLOCK")
        if latest and latest.get("status") == "completed" and latest.get("conclusion") in GOOD_CONCLUSIONS:
            findings.append("EXPECTED_BLOCK_UNEXPECTED_SUCCESS")
        elif latest and latest.get("status") in {"queued", "in_progress", "waiting", "requested", "pending"}:
            updated = parse_ts(latest.get("updated_at"))
            if updated and now - updated > timedelta(hours=2):
                findings.append("RUN_STUCK_OR_DELAYED")
    elif lifecycle == "RETIRED":
        findings.append("RETIRED_WORKFLOW_LOCAL_FILE_PRESENT")
    else:
        if row["scheduled"]:
            if not latest:
                if lifecycle == "PENDING_FIRST_EXPECTED_RUN":
                    findings.append("PENDING_FIRST_EXPECTED_RUN")
                else:
                    findings.append("NO_RUN_HISTORY")
            else:
                if lifecycle == "PENDING_FIRST_EXPECTED_RUN":
                    findings.append("PENDING_FIRST_RUN_ALREADY_RAN")
                created = parse_ts(latest.get("created_at"))
                if created:
                    age = now - created
                    threshold = timedelta(hours=36 if row["cron_count"] else 192)
                    if age > threshold:
                        findings.append("SCHEDULE_STALE")
                if latest.get("status") == "completed" and latest.get("conclusion") not in GOOD_CONCLUSIONS:
                    findings.append("LATEST_RUN_FAILED")
                elif latest.get("status") in {"queued", "in_progress", "waiting", "requested", "pending"}:
                    updated = parse_ts(latest.get("updated_at"))
                    if updated and now - updated > timedelta(hours=2):
                        findings.append("RUN_STUCK_OR_DELAYED")
        if live.get("failure_streak", 0) >= 2:
            findings.append("REPEATED_CONSECUTIVE_FAILURES")
        elif latest and latest.get("conclusion") in GOOD_CONCLUSIONS and live.get("recent_failure_count", 0) >= 2:
            findings.append("RECOVERING_AFTER_RECENT_FAILURES")

    critical = {
        "PR_TARGET_WITH_WRITE_OR_SECRET",
        "LATEST_RUN_FAILED",
        "REPEATED_CONSECUTIVE_FAILURES",
        "NON_GLOBAL_WRITER_LOCK",
        "NO_MAIN_READBACK",
        "INVALID_LIFECYCLE_STATE",
        "EXPECTED_BLOCK_HAS_SCHEDULE",
        "EXPECTED_BLOCK_REASON_MISSING",
        "EXPECTED_BLOCK_EXIT_CODE_INVALID",
        "EXPECTED_BLOCK_EXIT_CONTRACT_MISSING",
        "EXPECTED_BLOCK_UNEXPECTED_SUCCESS",
        "RETIRED_WORKFLOW_STILL_SCHEDULED",
    }
    status = "RED" if critical.intersection(findings) else ("AMBER" if findings else "GREEN")
    return status, sorted(set(findings))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow-root", type=Path, required=True)
    ap.add_argument("--json-output", type=Path, required=True)
    ap.add_argument("--md-output", type=Path, required=True)
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    args = ap.parse_args()

    now = utc_now()
    rows = [workflow_static(p) for p in sorted(list(args.workflow_root.glob("*.yml")) + list(args.workflow_root.glob("*.yaml")))]
    live: dict[str, dict[str, Any]] = {}
    api_error = None
    if args.repo and args.token:
        try:
            live = live_workflows(args.repo, args.token)
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ValueError) as exc:
            api_error = f"{type(exc).__name__}:{exc}"

    blockers: list[str] = []
    warnings: list[str] = []
    for row in rows:
        row["live"] = live.get(row["workflow"])
        row["status"], row["findings"] = classify(row, now)
        target = blockers if row["status"] == "RED" else warnings
        target.extend(f"{row['workflow']}:{item}" for item in row["findings"])

    orphaned = sorted(set(live) - {r["workflow"] for r in rows})
    if orphaned:
        warnings.extend(f"REGISTERED_WITHOUT_LOCAL_FILE:{name}" for name in orphaned)

    if any(r["status"] == "RED" for r in rows):
        overall = "RED"
    elif any(r["status"] == "AMBER" for r in rows) or api_error:
        overall = "AMBER"
    else:
        overall = "GREEN"

    result = {
        "contract": "AUTOMATION_PRODUCTION_HEALTH_v2_1",
        "lifecycle_semantics": "AUTOMATION_LIFECYCLE_v1",
        "generated_at_utc": now.isoformat().replace("+00:00", "Z"),
        "repository": args.repo,
        "status": overall,
        "api_error": api_error,
        "workflow_count": len(rows),
        "registered_workflow_count": len(live),
        "scheduled_workflow_count": sum(r["scheduled"] for r in rows),
        "writer_count": sum(r["writes_main"] for r in rows),
        "openai_workflow_count": sum(r["openai_enabled"] for r in rows),
        "cfgi_workflow_count": sum(r["cfgi_enabled"] for r in rows),
        "green_count": sum(r["status"] == "GREEN" for r in rows),
        "amber_count": sum(r["status"] == "AMBER" for r in rows),
        "red_count": sum(r["status"] == "RED" for r in rows),
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "orphaned_registered_workflows": orphaned,
        "workflows": rows,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")

    lines = [
        "# Automation Production Health",
        f"Status: **{overall}**",
        f"Generated: `{result['generated_at_utc']}`",
        f"Workflows: {len(rows)} local / {len(live)} registered",
        f"Scheduled: {result['scheduled_workflow_count']}",
        f"Writers: {result['writer_count']}",
        f"GREEN / AMBER / RED: {result['green_count']} / {result['amber_count']} / {result['red_count']}",
        "",
        "## Workflow matrix",
        "| Workflow | Lifecycle | Schedule | Writer | Last conclusion | Last run | Status | Findings |",
        "|---|---|---:|---:|---|---|---|---|",
    ]
    for row in rows:
        latest = (row.get("live") or {}).get("latest_run") or {}
        lines.append(
            f"| `{row['workflow']}` | `{row.get('lifecycle_state')}` | {'yes' if row['scheduled'] else 'no'} | {'yes' if row['writes_main'] else 'no'} | "
            f"{latest.get('conclusion') or latest.get('status') or 'none'} | {latest.get('created_at') or 'none'} | "
            f"**{row['status']}** | {', '.join(row['findings']) or 'None'} |"
        )
    lines += ["", "## Blockers"]
    lines += [f"- {item}" for item in result["blockers"]] or ["- None"]
    lines += ["", "## Warnings"]
    lines += [f"- {item}" for item in result["warnings"]] or ["- None"]
    if api_error:
        lines += ["", "## API degradation", f"- `{api_error}`"]
    args.md_output.write_text("\n".join(lines) + "\n")
    print(json.dumps({"status": overall, "blockers": len(result["blockers"]), "warnings": len(result["warnings"])}, sort_keys=True))

    if overall == "RED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
