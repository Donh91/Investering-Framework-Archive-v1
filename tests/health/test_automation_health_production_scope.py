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
            return {
                "workflows": [
                    {
                        "id": 42,
                        "path": ".github/workflows/scheduled.yml",
                        "name": "Scheduled",
                        "state": "active",
                        "html_url": "https://example.invalid/workflow",
                    }
                ]
            }
        if "event=schedule" in url:
            return {
                "workflow_runs": [
                    {
                        "id": 100,
                        "event": "schedule",
                        "head_branch": "main",
                        "status": "completed",
                        "conclusion": "success",
                        "created_at": "2026-08-29T01:00:00Z",
                        "updated_at": "2026-08-29T01:01:00Z",
                    }
                ]
            }
        if "branch=main" in url:
            return {
                "workflow_runs": [
                    {
                        "id": 102,
                        "event": "push",
                        "head_branch": "agent/task-noise",
                        "status": "completed",
                        "conclusion": "failure",
                        "created_at": "2026-08-29T03:00:00Z",
                        "updated_at": "2026-08-29T03:00:00Z",
                    },
                    {
                        "id": 101,
                        "event": "push",
                        "head_branch": "agent/task-noise",
                        "status": "completed",
                        "conclusion": "failure",
                        "created_at": "2026-08-29T02:00:00Z",
                        "updated_at": "2026-08-29T02:00:00Z",
                    },
                    {
                        "id": 100,
                        "event": "schedule",
                        "head_branch": "main",
                        "status": "completed",
                        "conclusion": "success",
                        "created_at": "2026-08-29T01:00:00Z",
                        "updated_at": "2026-08-29T01:01:00Z",
                    },
                ]
            }
        raise AssertionError(url)

    monkeypatch.setattr(module.base, "api_json", fake_api)
    live = module.live_workflows(
        "Donh91/Investering-Framework-Archive-v1",
        "token",
        {"scheduled.yml"},
    )["scheduled.yml"]

    assert live["latest_run"]["id"] == 100
    assert live["failure_streak"] == 0
    assert live["recent_failure_count"] == 0
    assert live["success_streak"] == 1

    row = _scheduled_row()
    row["live"] = live
    status, findings = module.classify(
        row, datetime(2026, 8, 29, 4, tzinfo=timezone.utc)
    )
    assert status == "GREEN"
    assert "LATEST_RUN_FAILED" not in findings
    assert "REPEATED_CONSECUTIVE_FAILURES" not in findings


def test_non_scheduled_gate_still_counts_branch_failures(monkeypatch) -> None:
    def fake_api(url: str, token: str) -> dict:
        if url.endswith("/Investering-Framework-Archive-v1"):
            return {"default_branch": "main"}
        if "/actions/workflows?" in url:
            return {
                "workflows": [
                    {
                        "id": 43,
                        "path": ".github/workflows/gate.yml",
                        "name": "Gate",
                        "state": "active",
                        "html_url": "https://example.invalid/gate",
                    }
                ]
            }
        if "/runs?per_page=10" in url:
            return {
                "workflow_runs": [
                    {
                        "id": 202,
                        "event": "pull_request",
                        "head_branch": "agent/task-bad",
                        "status": "completed",
                        "conclusion": "failure",
                        "created_at": "2026-08-29T03:00:00Z",
                        "updated_at": "2026-08-29T03:00:00Z",
                    },
                    {
                        "id": 201,
                        "event": "pull_request",
                        "head_branch": "agent/task-bad",
                        "status": "completed",
                        "conclusion": "failure",
                        "created_at": "2026-08-29T02:00:00Z",
                        "updated_at": "2026-08-29T02:00:00Z",
                    },
                ]
            }
        raise AssertionError(url)

    monkeypatch.setattr(module.base, "api_json", fake_api)
    live = module.live_workflows(
        "Donh91/Investering-Framework-Archive-v1", "token", set()
    )["gate.yml"]
    assert live["failure_streak"] == 2

    row = _scheduled_row()
    row["workflow"] = "gate.yml"
    row["scheduled"] = False
    row["cron_expressions"] = []
    row["live"] = live
    status, findings = module.classify(
        row, datetime(2026, 8, 29, 4, tzinfo=timezone.utc)
    )
    assert status == "RED"
    assert "REPEATED_CONSECUTIVE_FAILURES" in findings


def test_empty_registry_is_one_global_degradation(monkeypatch) -> None:
    def fake_api(url: str, token: str) -> dict:
        if url.endswith("/Investering-Framework-Archive-v1"):
            return {"default_branch": "main"}
        if "/actions/workflows?" in url:
            return {"workflows": []}
        raise AssertionError(url)

    monkeypatch.setattr(module.base, "api_json", fake_api)
    try:
        module.live_workflows(
            "Donh91/Investering-Framework-Archive-v1", "token", {"scheduled.yml"}
        )
    except ValueError as exc:
        assert "EMPTY_WORKFLOW_REGISTRY_RESPONSE" in str(exc)
    else:
        raise AssertionError("empty registry must fail as global API degradation")

    assert module.API_DEGRADED is True
    row = _scheduled_row()
    row["live"] = None
    status, findings = module.classify(
        row, datetime(2026, 8, 29, 4, tzinfo=timezone.utc)
    )
    assert status == "GREEN"
    assert "WORKFLOW_NOT_REGISTERED_OR_API_UNAVAILABLE" not in findings
    assert "NO_RUN_HISTORY" not in findings


def test_slow_cycle_workflow_preserves_only_stale_exit_code() -> None:
    text = (
        Path(__file__).parents[2]
        / ".github"
        / "workflows"
        / "daily-slow-cycle-shadow.yml"
    ).read_text()
    assert "collector_rc=$?" in text
    assert '"$collector_rc" -ne 0' in text
    assert '"$collector_rc" -ne 3' in text
    assert 'exit "$collector_rc"' in text


def test_current_shadow_registry_is_branch_only_not_direct_main() -> None:
    path = (
        Path(__file__).parents[2]
        / ".github"
        / "workflows"
        / "shadow-registry-weekly.yml"
    )
    row = module.workflow_static(path)
    assert row["write_target_class"] == "BRANCH_ONLY"
    assert row["writes_main"] is False
    assert not module.MAIN_WRITER_RISKS.intersection(row["static_risks"])


def test_current_automation_health_writer_remains_direct_main() -> None:
    path = (
        Path(__file__).parents[2]
        / ".github"
        / "workflows"
        / "automation-production-health.yml"
    )
    row = module.workflow_static(path)
    assert row["write_target_class"] == "DIRECT_MAIN"
    assert row["writes_main"] is True


def test_contents_write_without_git_push_is_not_a_main_writer(tmp_path: Path) -> None:
    path = tmp_path / "permission-only.yml"
    path.write_text(
        """name: Permission Only
on:
  workflow_dispatch:
permissions:
  contents: write
jobs:
  x:
    steps:
      - run: echo no-push
"""
    )
    row = module.workflow_static(path)
    assert row["write_target_class"] == "WRITE_PERMISSION_NO_PUSH"
    assert row["writes_main"] is False


def test_explicit_non_main_ref_is_branch_only(tmp_path: Path) -> None:
    path = tmp_path / "branch-only.yml"
    path.write_text(
        """name: Branch Only
on:
  workflow_dispatch:
permissions:
  contents: write
jobs:
  x:
    steps:
      - run: git push origin HEAD:automation/test-proof
"""
    )
    row = module.workflow_static(path)
    assert row["write_target_class"] == "BRANCH_ONLY"
    assert row["writes_main"] is False
    assert not module.MAIN_WRITER_RISKS.intersection(row["static_risks"])


def test_tag_push_is_not_a_main_writer(tmp_path: Path) -> None:
    path = tmp_path / "tag.yml"
    path.write_text(
        """name: Tag
on:
  workflow_dispatch:
permissions:
  contents: write
jobs:
  x:
    steps:
      - run: git push origin refs/tags/v1
"""
    )
    row = module.workflow_static(path)
    assert row["write_target_class"] == "TAG_OR_OTHER_REF"
    assert row["writes_main"] is False


def test_unresolved_dynamic_push_target_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "dynamic.yml"
    path.write_text(
        """name: Dynamic
on:
  workflow_dispatch:
permissions:
  contents: write
jobs:
  x:
    steps:
      - run: git push origin "$TARGET_BRANCH"
"""
    )
    row = module.workflow_static(path)
    assert row["write_target_class"] == "DYNAMIC_TARGET_UNKNOWN"
    assert row["writes_main"] is False
    row["live"] = {
        "state": "active",
        "latest_run": {
            "status": "completed",
            "conclusion": "success",
            "created_at": "2026-09-02T18:00:00Z",
        },
        "recent_failure_count": 0,
        "success_streak": 1,
        "failure_streak": 0,
    }
    status, findings = module.classify(
        row, datetime(2026, 9, 2, 19, tzinfo=timezone.utc)
    )
    assert status == "RED"
    assert "WRITE_TARGET_UNKNOWN" in findings
