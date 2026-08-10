from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).parents[2] / "scripts" / "health" / "build_automation_health.py"
spec = importlib.util.spec_from_file_location("automation_health", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def write_workflow(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "test.yml"
    path.write_text(body)
    return path


def healthy_writer(tmp_path: Path) -> dict:
    path = write_workflow(
        tmp_path,
        """name: Test\non:\n  schedule:\n    - cron: '0 1 * * *'\n      timezone: 'Europe/Copenhagen'\npermissions:\n  contents: write\nconcurrency:\n  group: framework-main-writer\njobs:\n  x:\n    steps:\n      - run: |\n          git add out\n          if git diff --cached --quiet; then exit 0; fi\n          git rebase --abort || true\n          git push origin HEAD:main\n          git merge-base --is-ancestor HEAD origin/main\n""",
    )
    return module.workflow_static(path)


def expected_block(tmp_path: Path, scheduled: bool = False) -> dict:
    trigger = "  schedule:\n    - cron: '0 1 * * *'\n      timezone: 'Europe/Copenhagen'\n" if scheduled else "  workflow_dispatch:\n"
    path = write_workflow(
        tmp_path,
        "# framework-lifecycle: EXPECTED_BLOCK\n"
        "# framework-lifecycle-reason: TEST_FREEZE\n"
        "# framework-lifecycle-since: 2026-08-03T05:00:00Z\n"
        "# framework-expected-exit: 78\n"
        f"name: Test\non:\n{trigger}jobs:\n  x:\n    steps:\n      - run: |\n          echo TEST_FREEZE\n          exit 78\n",
    )
    return module.workflow_static(path)


def test_writer_without_global_lock_is_red(tmp_path: Path) -> None:
    path = write_workflow(
        tmp_path,
        """name: Test\non:\n  schedule:\n    - cron: '0 1 * * *'\npermissions:\n  contents: write\njobs:\n  x:\n    steps:\n      - run: git push origin HEAD:main\n""",
    )
    row = module.workflow_static(path)
    row["live"] = {
        "state": "active",
        "latest_run": {"status": "completed", "conclusion": "success", "created_at": "2026-08-03T00:00:00Z"},
        "recent_failure_count": 0,
        "success_streak": 1,
        "failure_streak": 0,
    }
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "RED"
    assert "NON_GLOBAL_WRITER_LOCK" in findings
    assert "NO_MAIN_READBACK" in findings


def test_healthy_writer_is_green(tmp_path: Path) -> None:
    row = healthy_writer(tmp_path)
    row["live"] = {
        "state": "active",
        "latest_run": {"status": "completed", "conclusion": "success", "created_at": "2026-08-03T06:00:00Z"},
        "recent_failure_count": 0,
        "success_streak": 3,
        "failure_streak": 0,
    }
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "GREEN"
    assert findings == []


def test_consecutive_failures_are_red(tmp_path: Path) -> None:
    path = write_workflow(tmp_path, "name: Test\non:\n  workflow_dispatch:\njobs:\n  x:\n    steps:\n      - run: echo ok\n")
    row = module.workflow_static(path)
    row["live"] = {
        "state": "active",
        "latest_run": {"status": "completed", "conclusion": "failure", "created_at": "2026-08-03T06:00:00Z"},
        "recent_failure_count": 2,
        "success_streak": 0,
        "failure_streak": 2,
    }
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "RED"
    assert "REPEATED_CONSECUTIVE_FAILURES" in findings
    assert "LATEST_RUN_FAILED" not in findings


def test_expected_block_does_not_turn_historical_failures_into_codex_failure(tmp_path: Path) -> None:
    row = expected_block(tmp_path)
    row["live"] = {
        "state": "active",
        "latest_run": {"status": "completed", "conclusion": "failure", "created_at": "2026-08-03T06:00:00Z"},
        "recent_failure_count": 5,
        "success_streak": 0,
        "failure_streak": 5,
    }
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "AMBER"
    assert "EXPECTED_BLOCK" in findings
    assert "REPEATED_CONSECUTIVE_FAILURES" not in findings
    assert "LATEST_RUN_FAILED" not in findings


def test_expected_block_with_schedule_is_red(tmp_path: Path) -> None:
    row = expected_block(tmp_path, scheduled=True)
    row["live"] = {"state": "active", "latest_run": None, "failure_streak": 0, "recent_failure_count": 0}
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "RED"
    assert "EXPECTED_BLOCK_HAS_SCHEDULE" in findings


def test_expected_block_historical_success_before_declaration_is_not_red(tmp_path: Path) -> None:
    row = expected_block(tmp_path)
    row["live"] = {
        "state": "active",
        "latest_run": {"status": "completed", "conclusion": "success", "created_at": "2026-08-03T04:00:00Z"},
        "recent_failure_count": 0,
        "success_streak": 1,
        "failure_streak": 0,
    }
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "AMBER"
    assert "EXPECTED_BLOCK_UNEXPECTED_SUCCESS" not in findings


def test_expected_block_unexpected_success_is_red(tmp_path: Path) -> None:
    row = expected_block(tmp_path)
    row["live"] = {
        "state": "active",
        "latest_run": {"status": "completed", "conclusion": "success", "created_at": "2026-08-03T06:00:00Z"},
        "recent_failure_count": 0,
        "success_streak": 1,
        "failure_streak": 0,
    }
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "RED"
    assert "EXPECTED_BLOCK_UNEXPECTED_SUCCESS" in findings


def test_pending_first_run_suppresses_no_history_but_remains_visible(tmp_path: Path) -> None:
    path = write_workflow(tmp_path, "# framework-lifecycle: PENDING_FIRST_EXPECTED_RUN\nname: Test\non:\n  schedule:\n    - cron: '0 1 * * *'\n      timezone: 'Europe/Copenhagen'\njobs:\n  x:\n    steps:\n      - run: echo ok\n")
    row = module.workflow_static(path)
    row["live"] = {"state": "active", "latest_run": None, "failure_streak": 0, "recent_failure_count": 0}
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "AMBER"
    assert "PENDING_FIRST_EXPECTED_RUN" in findings
    assert "NO_RUN_HISTORY" not in findings


def test_invalid_lifecycle_is_red(tmp_path: Path) -> None:
    path = write_workflow(tmp_path, "# framework-lifecycle: MAYBE\nname: Test\non:\n  workflow_dispatch:\njobs:\n  x:\n    steps:\n      - run: echo ok\n")
    row = module.workflow_static(path)
    row["live"] = {"state": "active", "latest_run": None, "failure_streak": 0, "recent_failure_count": 0}
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "RED"
    assert "INVALID_LIFECYCLE_STATE" in findings


def test_success_after_failures_is_amber_recovering(tmp_path: Path) -> None:
    row = healthy_writer(tmp_path)
    row["live"] = {
        "state": "active",
        "latest_run": {"status": "completed", "conclusion": "success", "created_at": "2026-08-03T06:00:00Z"},
        "recent_failure_count": 3,
        "success_streak": 1,
        "failure_streak": 0,
    }
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "AMBER"
    assert "RECOVERING_AFTER_RECENT_FAILURES" in findings


def test_scheduled_workflow_without_timezone_is_amber(tmp_path: Path) -> None:
    path = write_workflow(tmp_path, "name: Test\non:\n  schedule:\n    - cron: '0 1 * * *'\njobs:\n  x:\n    steps:\n      - run: echo ok\n")
    row = module.workflow_static(path)
    row["live"] = {
        "state": "active",
        "latest_run": {"status": "completed", "conclusion": "success", "created_at": "2026-08-03T06:00:00Z"},
        "recent_failure_count": 0,
        "success_streak": 1,
        "failure_streak": 0,
    }
    status, findings = module.classify(row, datetime(2026, 8, 3, 12, tzinfo=timezone.utc))
    assert status == "AMBER"
    assert "SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE" in findings


def test_leading_streaks() -> None:
    assert module.leading_streak(["success", "success", "failure"], True) == 2
    assert module.leading_streak(["failure", "failure", "success"], False) == 2
