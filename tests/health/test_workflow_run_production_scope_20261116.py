"""P0 original-owner health-scoping adversarial regressions, synthetic runs only."""
from __future__ import annotations
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).parents[2] / "scripts/health/build_automation_health_runtime.py"
spec = importlib.util.spec_from_file_location("test_runtime_health_scope", MODULE_PATH)
assert spec and spec.loader
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)

def run(i, kind, conclusion, minute, branch="main"):
    return {"id": i, "event": kind, "head_branch": branch, "status": "completed",
            "conclusion": conclusion, "run_attempt": 1,
            "created_at": f"2026-11-16T10:{minute:02d}:00Z",
            "updated_at": f"2026-11-16T10:{minute:02d}:30Z"}

def live(monkeypatch, runs, scheduled=None):
    if scheduled is None:
        scheduled = [r for r in runs if r["event"] == "schedule"]
    def api(url, token):
        if url.endswith("/Investering-Framework-Archive-v1"):
            return {"default_branch": "main"}
        if "/actions/workflows?" in url:
            return {"workflows": [{"id": 42, "name": "Cycle Navigator Internal Precision",
                "path": ".github/workflows/cycle-navigator-internal-precision.yml", "state": "active"}]}
        if "event=schedule" in url:
            return {"workflow_runs": scheduled}
        if "branch=main" in url:
            return {"workflow_runs": runs}
        raise AssertionError(url)
    monkeypatch.setattr(health.base, "api_json", api)
    return health.live_workflows(
        "Donh91/Investering-Framework-Archive-v1", "token",
        {"cycle-navigator-internal-precision.yml"}
    )["cycle-navigator-internal-precision.yml"]

def test_two_failed_workflow_run_events_are_visible_and_red(monkeypatch):
    items = [run(103,"workflow_run","failure",30),run(102,"workflow_run","failure",20),
             run(101,"schedule","success",10)]
    x = live(monkeypatch,items)
    assert x["latest_run"]["id"] == 103
    assert x["failure_streak"] == 2 and x["recent_failure_count"] == 2
    assert "workflow_run" in x["production_scope"]
    row = {"workflow": "cycle-navigator-internal-precision.yml",
           "path": ".github/workflows/cycle-navigator-internal-precision.yml",
           "scheduled": True, "manual": True, "cron_count": 1,
           "cron_expressions": ["15 10 * * 1"], "schedule_timezone": "Europe/Copenhagen",
           "writes_main": False, "writer_group": None, "openai_enabled": False,
           "cfgi_enabled": False, "permissions": [], "lifecycle_state": "ACTIVE",
           "lifecycle_reason": None, "expected_exit_code": None, "lifecycle_since": None,
           "static_risks": [], "live": x}
    status, findings = health.classify(row,datetime(2026,11,16,12,tzinfo=timezone.utc))
    assert status == "RED" and "LATEST_RUN_FAILED" in findings

def test_later_skipped_upstream_dependency_does_not_hide_failure(monkeypatch):
    items = [run(104,"workflow_run","skipped",40),run(103,"workflow_run","failure",30),
             run(102,"workflow_run","failure",20),run(101,"schedule","success",10)]
    x = live(monkeypatch,items)
    assert x["latest_run"]["id"] == 103
    assert x["failure_streak"] == 2
    assert x["recent_failure_count"] == 2
    assert "skipped" not in x["recent_conclusions"]

def test_real_success_resets_streak_without_erasing_history(monkeypatch):
    items = [run(105,"workflow_run","success",50),run(104,"workflow_run","skipped",40),
             run(103,"workflow_run","failure",30),run(102,"workflow_run","failure",20)]
    x = live(monkeypatch,items,scheduled=[])
    assert x["latest_run"]["id"] == 105
    assert x["failure_streak"] == 0 and x["success_streak"] == 1
    assert x["recent_failure_count"] == 2

def test_pr_and_task_branch_failure_excluded_from_production(monkeypatch):
    items = [run(109,"workflow_run","failure",55,"agent/task-test"),
             run(108,"pull_request","failure",50),run(107,"workflow_run","success",40)]
    x = live(monkeypatch,items,scheduled=[])
    assert x["latest_run"]["id"] == 107
    assert x["failure_streak"] == 0 and x["recent_failure_count"] == 0

def test_skipped_schedule_remains_visible_but_workflow_run_skipped_excluded(monkeypatch):
    items = [run(107,"workflow_run","skipped",50),run(106,"schedule","skipped",40),
             run(105,"workflow_run","failure",20)]
    x = live(monkeypatch,items)
    assert x["latest_run"]["id"] == 106
    assert x["recent_conclusions"] == ["skipped","failure"]
    assert x["recent_failure_count"] == 1
