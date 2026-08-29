from __future__ import annotations

"""Runtime corrections for Automation Production Health.

This is intentionally a thin compatibility layer over build_automation_health.py.
It keeps the existing report contract and static analysis while correcting two
runtime-observability semantics:

1. scheduled workflow health is derived only from production-eligible runs on
   the repository default branch (schedule/workflow_dispatch), so task-branch
   pushes cannot make production look RED;
2. an empty GitHub Actions workflow registry is treated as one global API
   degradation instead of 100+ independent missing-workflow observations.
"""

import importlib.util
from pathlib import Path
from typing import Any
from urllib.parse import quote

BASE_PATH = Path(__file__).with_name("build_automation_health.py")
spec = importlib.util.spec_from_file_location("automation_health_base", BASE_PATH)
assert spec and spec.loader
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

ORIGINAL_CLASSIFY = base.classify
API_DEGRADED = False
PRODUCTION_EVENTS = {"schedule", "workflow_dispatch"}


def _run_view(run: dict[str, Any] | None) -> dict[str, Any] | None:
    if not run:
        return None
    return {
        "id": run.get("id"),
        "event": run.get("event"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "created_at": run.get("created_at"),
        "updated_at": run.get("updated_at"),
        "run_attempt": run.get("run_attempt"),
        "html_url": run.get("html_url"),
        "head_sha": run.get("head_sha"),
    }


def live_workflows(
    repo: str,
    token: str,
    scheduled_workflows: set[str] | None = None,
) -> dict[str, dict[str, Any]]:
    """Return live state with scheduled workflows scoped to production runs."""
    global API_DEGRADED
    API_DEGRADED = False

    owner, name = repo.split("/", 1)
    api_base = f"https://api.github.com/repos/{owner}/{name}"
    repo_meta = base.api_json(api_base, token)
    default_branch = str(repo_meta.get("default_branch") or "main")
    branch_q = quote(default_branch, safe="")

    workflows: list[dict[str, Any]] = []
    page = 1
    while True:
        page_workflows = base.api_json(
            f"{api_base}/actions/workflows?per_page=100&page={page}", token
        ).get("workflows", [])
        workflows.extend(page_workflows)
        if len(page_workflows) < 100:
            break
        page += 1

    if not workflows:
        API_DEGRADED = True
        raise ValueError("EMPTY_WORKFLOW_REGISTRY_RESPONSE")

    result: dict[str, dict[str, Any]] = {}
    scheduled_set = scheduled_workflows or set()

    for workflow in workflows:
        wid = workflow["id"]
        workflow_name = Path(workflow["path"]).name
        is_scheduled = workflow_name in scheduled_set

        if is_scheduled:
            # The branch query prevents task-branch / PR pushes from becoming
            # production-health evidence. Event filtering also excludes any
            # historical push/PR run that happened on main under an older
            # trigger definition.
            runs = base.api_json(
                f"{api_base}/actions/workflows/{wid}/runs?branch={branch_q}&per_page=20",
                token,
            ).get("workflow_runs", [])
            production_runs = [
                run
                for run in runs
                if run.get("head_branch") == default_branch
                and run.get("event") in PRODUCTION_EVENTS
            ]
            scheduled_runs = base.api_json(
                f"{api_base}/actions/workflows/{wid}/runs?event=schedule&branch={branch_q}&per_page=1",
                token,
            ).get("workflow_runs", [])
            latest_scheduled = scheduled_runs[0] if scheduled_runs else None
            if latest_scheduled and not any(
                run.get("id") == latest_scheduled.get("id") for run in production_runs
            ):
                production_runs.append(latest_scheduled)
                production_runs.sort(
                    key=lambda run: str(run.get("created_at") or ""), reverse=True
                )
        else:
            production_runs = base.api_json(
                f"{api_base}/actions/workflows/{wid}/runs?per_page=10", token
            ).get("workflow_runs", [])
            latest_scheduled = next(
                (run for run in production_runs if run.get("event") == "schedule"),
                None,
            )

        latest = production_runs[0] if production_runs else None
        recent_completed = [
            run for run in production_runs if run.get("status") == "completed"
        ]
        conclusions = [run.get("conclusion") for run in recent_completed]
        recent_failures = [
            run
            for run in recent_completed
            if run.get("conclusion") not in base.GOOD_CONCLUSIONS
        ]

        result[workflow_name] = {
            "workflow_id": wid,
            "name": workflow.get("name"),
            "state": workflow.get("state"),
            "html_url": workflow.get("html_url"),
            "production_scope": (
                f"default_branch:{default_branch};events:schedule,workflow_dispatch"
                if is_scheduled
                else "all_registered_runs"
            ),
            "latest_run": _run_view(latest),
            "latest_scheduled_run": _run_view(latest_scheduled),
            "recent_completed_count": len(recent_completed),
            "recent_failure_count": len(recent_failures),
            "recent_conclusions": conclusions[:5],
            "success_streak": base.leading_streak(conclusions, True),
            "failure_streak": base.leading_streak(conclusions, False),
        }

    return result


def classify(row: dict[str, Any], now: Any) -> tuple[str, list[str]]:
    """Suppress per-workflow live inferences during a global API degradation."""
    if not API_DEGRADED:
        return ORIGINAL_CLASSIFY(row, now)

    # Preserve static and lifecycle findings, but do not infer NO_RUN_HISTORY,
    # LATEST_RUN_FAILED or missing registration from an unavailable global API.
    degraded = dict(row)
    degraded["scheduled"] = False
    degraded["live"] = {
        "state": "active",
        "latest_run": None,
        "recent_failure_count": 0,
        "recent_completed_count": 0,
        "success_streak": 0,
        "failure_streak": 0,
    }
    return ORIGINAL_CLASSIFY(degraded, now)


def main() -> None:
    base.live_workflows = live_workflows
    base.classify = classify
    base.main()


if __name__ == "__main__":
    main()
