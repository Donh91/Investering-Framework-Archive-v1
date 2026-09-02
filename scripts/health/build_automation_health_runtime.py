from __future__ import annotations

"""Runtime corrections for Automation Production Health.

This is intentionally a thin compatibility layer over build_automation_health.py.
It keeps the existing report contract and static analysis while correcting three
runtime-observability semantics:

1. scheduled workflow health is derived only from production-eligible runs on
   the repository default branch (schedule/workflow_dispatch), so task-branch
   pushes cannot make production look RED;
2. an empty GitHub Actions workflow registry is treated as one global API
   degradation instead of 100+ independent missing-workflow observations;
3. repository writes are classified by push target, so reviewed-PR branches are
   not mislabeled as direct-main writers and unresolved dynamic targets fail
   closed instead of being assumed safe.
"""

import importlib.util
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote

BASE_PATH = Path(__file__).with_name("build_automation_health.py")
spec = importlib.util.spec_from_file_location("automation_health_base", BASE_PATH)
assert spec and spec.loader
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)

ORIGINAL_CLASSIFY = base.classify
ORIGINAL_WORKFLOW_STATIC = base.workflow_static
API_DEGRADED = False
PRODUCTION_EVENTS = {"schedule", "workflow_dispatch"}
MAIN_WRITER_RISKS = {
    "NON_GLOBAL_WRITER_LOCK",
    "NO_REBASE_ABORT",
    "NO_MAIN_READBACK",
    "NO_EMPTY_COMMIT_GUARD",
}
WRITE_TARGET_CLASSES = {
    "DIRECT_MAIN",
    "BRANCH_ONLY",
    "TAG_OR_OTHER_REF",
    "WRITE_PERMISSION_NO_PUSH",
    "DYNAMIC_TARGET_UNKNOWN",
    "NO_REPO_WRITE",
}


def _push_fragments(text: str) -> list[str]:
    """Return shell fragments following each git-push invocation.

    The bounded parser stops at shell command separators. It is intentionally
    conservative: anything that cannot be resolved to main, a proven branch or
    a tag remains DYNAMIC_TARGET_UNKNOWN.
    """
    return [
        match.group(1).strip()
        for match in re.finditer(r"\bgit\s+push\b([^;&|\n]*)", text)
    ]


def _has_proven_branch_output(text: str, variable: str) -> bool:
    """Recognize a deterministic non-main branch carried through GITHUB_OUTPUT.

    This covers the reviewed-PR writer pattern used by Shadow Registry without
    treating arbitrary shell variables as safe. A variable target is branch-only
    only when the workflow contains all three links: a non-main namespace
    assignment, publication of that value as the `branch` step output, and an
    env binding from `steps.<id>.outputs.branch` into the pushed variable.
    """
    env_pattern = (
        rf"(?m)^\s*{re.escape(variable)}:\s*"
        rf"\$\{{\{{\s*steps\.[^.]+\.outputs\.branch\s*\}}\}}\s*$"
    )
    if not re.search(env_pattern, text):
        return False

    assignment = re.search(
        r"(?m)^\s*branch\s*=\s*['\"]([^'\"]+)['\"]\s*$", text
    )
    if not assignment:
        return False
    value = assignment.group(1).strip()
    if value in {"main", "refs/heads/main"} or value.startswith("main/"):
        return False
    if not re.match(
        r"^(?:automation|agent|ops|fix|research|chore|feature|remediation)/",
        value,
    ):
        return False

    return bool(
        re.search(
            r"echo\s+['\"]branch=\$branch['\"]\s*>>\s*['\"]?\$GITHUB_OUTPUT",
            text,
        )
    )


def _classify_push_fragment(fragment: str, text: str) -> str:
    clean = fragment.replace("\\\n", " ").strip()

    if re.search(
        r"(?:^|\s)\+?(?:HEAD:)?(?:refs/heads/)?main(?:\s|$)", clean
    ):
        return "DIRECT_MAIN"

    if "--tags" in clean or "refs/tags/" in clean:
        return "TAG_OR_OTHER_REF"

    explicit_ref = re.search(
        r"(?:^|\s)\+?HEAD:(?:refs/heads/)?([A-Za-z0-9._/-]+)(?:\s|$)",
        clean,
    )
    if explicit_ref:
        return "DIRECT_MAIN" if explicit_ref.group(1) == "main" else "BRANCH_ONLY"

    variables = re.findall(
        r"['\"]?\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))['\"]?",
        clean,
    )
    for braced, plain in variables:
        variable = braced or plain
        if _has_proven_branch_output(text, variable):
            return "BRANCH_ONLY"
    if variables:
        return "DYNAMIC_TARGET_UNKNOWN"

    tokens = [
        token.strip("'\"")
        for token in re.findall(r'(?:"[^"]+"|\'[^\']+\'|\S+)', clean)
    ]
    non_options = [token for token in tokens if not token.startswith("-")]
    if non_options:
        target = non_options[-1]
        if target == "main" or target.endswith(":main") or target.endswith(
            ":refs/heads/main"
        ):
            return "DIRECT_MAIN"
        if target.startswith("refs/heads/") or "/" in target:
            return "BRANCH_ONLY"

    return "DYNAMIC_TARGET_UNKNOWN"


def classify_write_target(text: str) -> str:
    if "contents: write" not in text:
        return "NO_REPO_WRITE"

    pushes = _push_fragments(text)
    if not pushes:
        return "WRITE_PERMISSION_NO_PUSH"

    classes = [_classify_push_fragment(fragment, text) for fragment in pushes]
    if "DIRECT_MAIN" in classes:
        return "DIRECT_MAIN"
    if "DYNAMIC_TARGET_UNKNOWN" in classes:
        return "DYNAMIC_TARGET_UNKNOWN"
    if "BRANCH_ONLY" in classes:
        return "BRANCH_ONLY"
    return "TAG_OR_OTHER_REF"


def workflow_static(path: Path) -> dict[str, Any]:
    """Refine the base static row with repository write-target semantics."""
    row = ORIGINAL_WORKFLOW_STATIC(path)
    text = path.read_text(errors="ignore")
    write_target_class = classify_write_target(text)
    assert write_target_class in WRITE_TARGET_CLASSES

    row["write_target_class"] = write_target_class
    row["writes_main"] = write_target_class == "DIRECT_MAIN"

    if write_target_class != "DIRECT_MAIN":
        row["static_risks"] = [
            risk
            for risk in row.get("static_risks", [])
            if risk not in MAIN_WRITER_RISKS
        ]

    if write_target_class == "DYNAMIC_TARGET_UNKNOWN":
        row.setdefault("static_risks", []).append("WRITE_TARGET_UNKNOWN")

    row["static_risks"] = sorted(set(row.get("static_risks", [])))
    return row


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
    """Apply runtime health semantics and fail closed on unresolved write targets."""
    candidate = row
    if API_DEGRADED:
        # Preserve static and lifecycle findings, but do not infer NO_RUN_HISTORY,
        # LATEST_RUN_FAILED or missing registration from an unavailable global API.
        candidate = dict(row)
        candidate["scheduled"] = False
        candidate["live"] = {
            "state": "active",
            "latest_run": None,
            "recent_failure_count": 0,
            "recent_completed_count": 0,
            "success_streak": 0,
            "failure_streak": 0,
        }

    status, findings = ORIGINAL_CLASSIFY(candidate, now)
    if row.get("write_target_class") == "DYNAMIC_TARGET_UNKNOWN":
        findings = sorted(set(findings) | {"WRITE_TARGET_UNKNOWN"})
        status = "RED"
    return status, findings


def main() -> None:
    base.workflow_static = workflow_static
    base.live_workflows = live_workflows
    base.classify = classify
    base.main()


if __name__ == "__main__":
    main()
