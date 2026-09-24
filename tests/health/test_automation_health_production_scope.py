from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).parents[2] / "scripts" / "health" / "build_automation_health_runtime.py"
spec = importlib.util.spec_from_file_location("automation_health_runtime", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def _scheduled_row() -> dict:
    return {
        "workflow": "scheduled.yml",
        "path": ".github/workflows/scheduled.yml",
        "scheduled": True,
        "manual": True,
        "cron_count": 1,
        "cron_expressions": ["0 1 * * *"],
        "schedule_timezone": "UTC",
        "writes_main": False,
        "writer_group": None,
        "openai_enabled": False,
        "cfgi_enabled": False,
        "permissions": [],
        "lifecycle_state": "ACTIVE",
        "lifecycle_reason": None,
        "expected_exit_code": None,
        "lifecycle_since": None,
        "static_risks": [],
    }


def test_scheduled_health_ignores_task_branch_push_failures(monkeypatch) -> None:
    def fake_api(url: str, token: str) -> dict:
        if url.endswith("/Investering-Framework-Archive-v1"):
            return {"default_branch": "main"}
        if "/actions/workflows?" in url:
            return {"workflows": [{"id": 42, "path": ".github/workflows/scheduled.yml", "name": "Scheduled", "state": "active", "html_url": "https://example.invalid/workflow"}]}
        if "event=schedule" in url:
            return {"workflow_runs": [{"id": 100, "event": "schedule", "head_branch": "main", "status": "completed", "conclusion": "success", "created_at": "2026-08-29T01:00:00Z", "updated_at": "2026-08-29T01:01:00Z"}]}
        if "branch=main" in url:
            return {"workflow_runs": [
                {"id": 102, "event": "push", "head_branch": "agent/task-noise", "status": "completed", "conclusion": "failure", "created_at": "2026-08-29T03:00:00Z", "updated_at": "2026-08-29T03:00:00Z"},
                {"id": 101, "event": "push", "head_branch": "agent/task-noise", "status": "completed", "conclusion": "failure", "created_at": "2026-08-29T02:00:00Z", "updated_at": "2026-08-29T02:00:00Z"},
                {"id": 100, "event": "schedule", "head_branch": "main", "status": "completed", "conclusion": "success", "created_at": "2026-08-29T01:00:00Z", "updated_at": "2026-08-29T01:01:00Z"},
            ]}
        raise AssertionError(url)

    monkeypatch.setattr(module.base, "api_json", fake_api)
    live = module.live_workflows("Donh91/Investering-Framework-Archive-v1", "token", {"scheduled.yml"})["scheduled.yml"]
    assert live["latest_run"]["id"] == 100
    assert live["failure_streak"] == 0
    assert live["recent_failure_count"] == 0
    assert live["success_streak"] == 1

    row = _scheduled_row(); row["live"] = live
    status, findings = module.classify(row, datetime(2026, 8, 29, 4, tzinfo=timezone.utc))
    assert status == "GREEN"
    assert "LATEST_RUN_FAILED" not in findings
    assert "REPEATED_CONSECUTIVE_FAILURES" not in findings


def test_non_scheduled_pr_gate_rejections_are_amber_not_production_red(monkeypatch) -> None:
    def fake_api(url: str, token: str) -> dict:
        if url.endswith("/Investering-Framework-Archive-v1"):
            return {"default_branch": "main"}
        if "/actions/workflows?" in url:
            return {"workflows": [{"id": 43, "path": ".github/workflows/gate.yml", "name": "Gate", "state": "active", "html_url": "https://example.invalid/gate"}]}
        if "/runs?per_page=10" in url:
            return {"workflow_runs": [
                {"id": 202, "event": "pull_request", "head_branch": "agent/task-bad", "status": "completed", "conclusion": "failure", "created_at": "2026-08-29T03:00:00Z", "updated_at": "2026-08-29T03:00:00Z"},
                {"id": 201, "event": "pull_request", "head_branch": "agent/task-bad", "status": "completed", "conclusion": "failure", "created_at": "2026-08-29T02:00:00Z", "updated_at": "2026-08-29T02:00:00Z"},
            ]}
        raise AssertionError(url)

    monkeypatch.setattr(module.base, "api_json", fake_api)
    live = module.live_workflows("Donh91/Investering-Framework-Archive-v1", "token", set())["gate.yml"]
    assert live["failure_streak"] == 0
    assert live["recent_failure_count"] == 0
    assert live["pr_gate_rejection_streak"] == 2
    assert live["recent_pr_gate_rejection_count"] == 2

    row = _scheduled_row(); row["workflow"] = "gate.yml"; row["scheduled"] = False; row["cron_expressions"] = []; row["live"] = live
    status, findings = module.classify(row, datetime(2026, 8, 29, 4, tzinfo=timezone.utc))
    assert status == "AMBER"
    assert "PR_GATE_REJECTION" in findings
    assert "REPEATED_PR_GATE_REJECTIONS" in findings
    assert "LATEST_RUN_FAILED" not in findings
    assert "REPEATED_CONSECUTIVE_FAILURES" not in findings


def test_scheduled_cancellation_is_amber_not_execution_failure(monkeypatch) -> None:
    cancelled = {"id": 301, "event": "schedule", "head_branch": "main", "status": "completed", "conclusion": "cancelled", "created_at": "2026-08-29T01:00:00Z", "updated_at": "2026-08-29T01:00:02Z"}
    def fake_api(url: str, token: str) -> dict:
        if url.endswith("/Investering-Framework-Archive-v1"): return {"default_branch": "main"}
        if "/actions/workflows?" in url: return {"workflows": [{"id": 44, "path": ".github/workflows/scheduled.yml", "name": "Scheduled", "state": "active", "html_url": "https://example.invalid/scheduled"}]}
        if "event=schedule" in url: return {"workflow_runs": [cancelled]}
        if "branch=main" in url: return {"workflow_runs": [cancelled]}
        raise AssertionError(url)

    monkeypatch.setattr(module.base, "api_json", fake_api)
    live = module.live_workflows("Donh91/Investering-Framework-Archive-v1", "token", {"scheduled.yml"})["scheduled.yml"]
    assert live["recent_failure_count"] == 0
    assert live["failure_streak"] == 0
    assert live["recent_cancellation_count"] == 1
    assert live["cancellation_streak"] == 1

    row = _scheduled_row(); row["live"] = live
    status, findings = module.classify(row, datetime(2026, 8, 29, 2, tzinfo=timezone.utc))
    assert status == "AMBER"
    assert "LATEST_RUN_CANCELLED" in findings
    assert "LATEST_RUN_FAILED" not in findings
    assert "REPEATED_CONSECUTIVE_FAILURES" not in findings


def test_scheduled_execution_failure_remains_red(monkeypatch) -> None:
    failure = {"id": 401, "event": "schedule", "head_branch": "main", "status": "completed", "conclusion": "failure", "created_at": "2026-08-29T01:00:00Z", "updated_at": "2026-08-29T01:02:00Z"}
    def fake_api(url: str, token: str) -> dict:
        if url.endswith("/Investering-Framework-Archive-v1"): return {"default_branch": "main"}
        if "/actions/workflows?" in url: return {"workflows": [{"id": 45, "path": ".github/workflows/scheduled.yml", "name": "Scheduled", "state": "active", "html_url": "https://example.invalid/scheduled"}]}
        if "event=schedule" in url: return {"workflow_runs": [failure]}
        if "branch=main" in url: return {"workflow_runs": [failure]}
        raise AssertionError(url)

    monkeypatch.setattr(module.base, "api_json", fake_api)
    live = module.live_workflows("Donh91/Investering-Framework-Archive-v1", "token", {"scheduled.yml"})["scheduled.yml"]
    assert live["recent_failure_count"] == 1
    assert live["failure_streak"] == 1
    assert live["recent_cancellation_count"] == 0

    row = _scheduled_row(); row["live"] = live
    status, findings = module.classify(row, datetime(2026, 8, 29, 2, tzinfo=timezone.utc))
    assert status == "RED"
    assert "LATEST_RUN_FAILED" in findings
    assert "LATEST_RUN_CANCELLED" not in findings


def test_in_progress_rerun_preserves_previous_success_in_streak(monkeypatch) -> None:
    latest = {
        "id": 500,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "status": "in_progress",
        "conclusion": None,
        "run_attempt": 2,
        "created_at": "2026-09-24T06:58:00Z",
        "updated_at": "2026-09-24T06:58:30Z",
    }
    older_failures = [
        {
            "id": run_id,
            "event": "workflow_dispatch",
            "head_branch": "main",
            "status": "completed",
            "conclusion": "failure",
            "run_attempt": 1,
            "created_at": created_at,
            "updated_at": created_at,
        }
        for run_id, created_at in (
            (499, "2026-09-18T18:33:34Z"),
            (498, "2026-09-18T18:20:00Z"),
            (497, "2026-09-18T18:10:00Z"),
        )
    ]
    previous_success = dict(
        latest,
        status="completed",
        conclusion="success",
        run_attempt=1,
        updated_at="2026-09-18T19:12:08Z",
    )

    def fake_api(url: str, token: str) -> dict:
        if url.endswith("/Investering-Framework-Archive-v1"):
            return {"default_branch": "main"}
        if "/actions/workflows?" in url:
            return {"workflows": [{"id": 46, "path": ".github/workflows/manual.yml", "name": "Manual", "state": "active", "html_url": "https://example.invalid/manual"}]}
        if "/actions/workflows/46/runs?per_page=10" in url:
            return {"workflow_runs": [latest, *older_failures]}
        if "/actions/runs/500/attempts/1" in url:
            return previous_success
        raise AssertionError(url)

    monkeypatch.setattr(module.base, "api_json", fake_api)
    live = module.live_workflows(
        "Donh91/Investering-Framework-Archive-v1", "token", set()
    )["manual.yml"]

    assert live["latest_run"]["status"] == "in_progress"
    assert live["latest_run"]["run_attempt"] == 2
    assert live["recent_conclusions"][:4] == ["success", "failure", "failure", "failure"]
    assert live["success_streak"] == 1
    assert live["failure_streak"] == 0

    row = _scheduled_row()
    row["workflow"] = "manual.yml"
    row["scheduled"] = False
    row["cron_expressions"] = []
    row["live"] = live
    status, findings = module.classify(
        row, datetime(2026, 9, 24, 7, tzinfo=timezone.utc)
    )
    assert status == "GREEN"
    assert "REPEATED_CONSECUTIVE_FAILURES" not in findings


def test_in_progress_rerun_preserves_previous_failure_in_streak(monkeypatch) -> None:
    latest = {
        "id": 600,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "status": "in_progress",
        "conclusion": None,
        "run_attempt": 2,
        "created_at": "2026-09-24T06:58:00Z",
        "updated_at": "2026-09-24T06:58:30Z",
    }
    older_failure = {
        "id": 599,
        "event": "workflow_dispatch",
        "head_branch": "main",
        "status": "completed",
        "conclusion": "failure",
        "run_attempt": 1,
        "created_at": "2026-09-23T06:00:00Z",
        "updated_at": "2026-09-23T06:01:00Z",
    }
    previous_failure = dict(
        latest,
        status="completed",
        conclusion="failure",
        run_attempt=1,
        updated_at="2026-09-24T06:50:00Z",
    )

    def fake_api(url: str, token: str) -> dict:
        if url.endswith("/Investering-Framework-Archive-v1"):
            return {"default_branch": "main"}
        if "/actions/workflows?" in url:
            return {"workflows": [{"id": 47, "path": ".github/workflows/manual.yml", "name": "Manual", "state": "active", "html_url": "https://example.invalid/manual"}]}
        if "/actions/workflows/47/runs?per_page=10" in url:
            return {"workflow_runs": [latest, older_failure]}
        if "/actions/runs/600/attempts/1" in url:
            return previous_failure
        raise AssertionError(url)

    monkeypatch.setattr(module.base, "api_json", fake_api)
    live = module.live_workflows(
        "Donh91/Investering-Framework-Archive-v1", "token", set()
    )["manual.yml"]

    assert live["recent_conclusions"][:2] == ["failure", "failure"]
    assert live["success_streak"] == 0
    assert live["failure_streak"] == 2

    row = _scheduled_row()
    row["workflow"] = "manual.yml"
    row["scheduled"] = False
    row["cron_expressions"] = []
    row["live"] = live
    status, findings = module.classify(
        row, datetime(2026, 9, 24, 7, tzinfo=timezone.utc)
    )
    assert status == "RED"
    assert "REPEATED_CONSECUTIVE_FAILURES" in findings


def test_empty_registry_is_one_global_degradation(monkeypatch) -> None:
    def fake_api(url: str, token: str) -> dict:
        if url.endswith("/Investering-Framework-Archive-v1"): return {"default_branch": "main"}
        if "/actions/workflows?" in url: return {"workflows": []}
        raise AssertionError(url)

    monkeypatch.setattr(module.base, "api_json", fake_api)
    try:
        module.live_workflows("Donh91/Investering-Framework-Archive-v1", "token", {"scheduled.yml"})
    except ValueError as exc:
        assert "EMPTY_WORKFLOW_REGISTRY_RESPONSE" in str(exc)
    else:
        raise AssertionError("empty registry must fail as global API degradation")

    assert module.API_DEGRADED is True
    row = _scheduled_row(); row["live"] = None
    status, findings = module.classify(row, datetime(2026, 8, 29, 4, tzinfo=timezone.utc))
    assert status == "GREEN"
    assert "WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE" not in findings
    assert "NO_RUN_HISTORY" not in findings


def test_slow_cycle_workflow_preserves_only_stale_exit_code() -> None:
    text = (Path(__file__).parents[2] / ".github" / "workflows" / "daily-slow-cycle-shadow.yml").read_text()
    assert "collector_rc=$?" in text
    assert '"$collector_rc" -ne 0' in text
    assert '"$collector_rc" -ne 3' in text
    assert 'exit "$collector_rc"' in text


def test_current_shadow_registry_is_branch_only_not_direct_main() -> None:
    path = Path(__file__).parents[2] / ".github" / "workflows" / "shadow-registry-weekly.yml"
    row = module.workflow_static(path)
    assert row["write_target_class"] == "BRANCH_ONLY"
    assert row["writes_main"] is False
    assert not module.MAIN_WRITER_RISKS.intersection(row["static_risks"])


def test_current_automation_health_writer_remains_direct_main() -> None:
    path = Path(__file__).parents[2] / ".github" / "workflows" / "automation-production-health.yml"
    row = module.workflow_static(path)
    assert row["write_target_class"] == "DIRECT_MAIN"
    assert row["writes_main"] is True


def test_contents_write_without_git_push_is_not_a_main_writer(tmp_path: Path) -> None:
    path = tmp_path / "permission-only.yml"
    path.write_text("""name: Permission Only
on:
  workflow_dispatch:
permissions:
  contents: write
jobs:
  x:
    steps:
      - run: echo no-push
""")
    row = module.workflow_static(path)
    assert row["write_target_class"] == "WRITE_PERMISSION_NO_PUSH"
    assert row["writes_main"] is False


def test_explicit_non_main_ref_is_branch_only(tmp_path: Path) -> None:
    path = tmp_path / "branch-only.yml"
    path.write_text("""name: Branch Only
on:
  workflow_dispatch:
permissions:
  contents: write
jobs:
  x:
    steps:
      - run: git push origin HEAD:automation/test-proof
""")
    row = module.workflow_static(path)
    assert row["write_target_class"] == "BRANCH_ONLY"
    assert row["writes_main"] is False
    assert not module.MAIN_WRITER_RISKS.intersection(row["static_risks"])


def test_tag_push_is_not_a_main_writer(tmp_path: Path) -> None:
    path = tmp_path / "tag.yml"
    path.write_text("""name: Tag
on:
  workflow_dispatch:
permissions:
  contents: write
jobs:
  x:
    steps:
      - run: git push origin refs/tags/v1
""")
    row = module.workflow_static(path)
    assert row["write_target_class"] == "TAG_OR_OTHER_REF"
    assert row["writes_main"] is False


def test_unresolved_dynamic_push_target_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "dynamic.yml"
    path.write_text("""name: Dynamic
on:
  workflow_dispatch:
permissions:
  contents: write
jobs:
  x:
    steps:
      - run: git push origin "$TARGET_BRANCH"
""")
    row = module.workflow_static(path)
    assert row["write_target_class"] == "DYNAMIC_TARGET_UNKNOWN"
    assert row["writes_main"] is False
    row["live"] = {
        "state": "active",
        "latest_run": {"status": "completed", "event": "workflow_dispatch", "conclusion": "success", "created_at": "2026-09-02T18:00:00Z"},
        "recent_failure_count": 0,
        "recent_cancellation_count": 0,
        "recent_pr_gate_rejection_count": 0,
        "success_streak": 1,
        "failure_streak": 0,
        "cancellation_streak": 0,
        "pr_gate_rejection_streak": 0,
    }
    status, findings = module.classify(row, datetime(2026, 9, 2, 19, tzinfo=timezone.utc))
    assert status == "RED"
    assert "WRITE_TARGET_UNKNOWN" in findings


def test_current_repository_has_no_unresolved_write_targets() -> None:
    workflow_root = Path(__file__).parents[2] / ".github" / "workflows"
    unknown = []
    for path in sorted(list(workflow_root.glob("*.yml")) + list(workflow_root.glob("*.yaml"))):
        row = module.workflow_static(path)
        if row["write_target_class"] == "DYNAMIC_TARGET_UNKNOWN":
            unknown.append(path.name)
    assert unknown == [], f"unresolved repository write targets: {unknown}"
