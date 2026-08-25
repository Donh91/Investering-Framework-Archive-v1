from __future__ import annotations

import importlib.util
import json
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


def test_schedule_literal_inside_step_does_not_make_manual_gate_scheduled(tmp_path: Path) -> None:
    path = write_workflow(
        tmp_path,
        """name: Manual Gate
on:
  pull_request:
  workflow_dispatch:
jobs:
  gate:
    steps:
      - run: |
          python - <<'PY'
          source = "schedule:"
          assert "schedule:" not in source.replace("schedule:", "")
          PY
""",
    )
    row = module.workflow_static(path)
    assert row["scheduled"] is False
    assert "SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE" not in row["static_risks"]


def test_job_named_schedule_does_not_make_manual_workflow_scheduled(tmp_path: Path) -> None:
    path = write_workflow(
        tmp_path,
        """name: Manual Workflow
on:
  workflow_dispatch:
jobs:
  schedule:
    runs-on: ubuntu-latest
    steps:
      - run: echo manual
""",
    )
    row = module.workflow_static(path)
    assert row["scheduled"] is False
    assert "SCHEDULE_WITHOUT_EXPLICIT_TIMEZONE" not in row["static_risks"]


def test_leading_streaks() -> None:
    assert module.leading_streak(["success", "success", "failure"], True) == 2
    assert module.leading_streak(["failure", "failure", "success"], False) == 2


def test_retired_terminal_workflow_does_not_reopen_historical_failures(tmp_path: Path) -> None:
    path = write_workflow(
        tmp_path,
        "# framework-lifecycle: RETIRED\n"
        "# framework-lifecycle-reason: PROVIDER_TERMINAL_NO_RETRY\n"
        "# framework-lifecycle-since: 2026-08-21T09:30:00Z\n"
        "name: Test\non:\n  workflow_dispatch:\njobs:\n  x:\n    steps:\n      - run: echo terminal\n",
    )
    row = module.workflow_static(path)
    row["live"] = {
        "state": "active",
        "latest_run": {"status": "completed", "conclusion": "failure", "created_at": "2026-08-21T09:00:00Z"},
        "recent_failure_count": 5,
        "success_streak": 0,
        "failure_streak": 5,
    }
    status, findings = module.classify(row, datetime(2026, 8, 24, 12, tzinfo=timezone.utc))
    assert status == "AMBER"
    assert "RETIRED_WORKFLOW_LOCAL_FILE_PRESENT" in findings
    assert "REPEATED_CONSECUTIVE_FAILURES" not in findings
    assert "LATEST_RUN_FAILED" not in findings


def test_current_cfgi_terminal_contract_blocks_paid_redispatch() -> None:
    repo = Path(__file__).parents[2]
    enrichment_path = repo / ".github/workflows/historical-altseason-cfgi-enrichment.yml"
    enrichment = module.workflow_static(enrichment_path)
    enrichment_text = enrichment_path.read_text()
    terminal = json.loads(
        (repo / "00_ARCHIVE_CONTROL/research_runtime/CFGI_MARKET_PROVIDER_TERMINAL_RECEIPT.json").read_text()
    )
    audit = (repo / ".github/workflows/historical-altseason-cfgi-run-audit.yml").read_text()
    assert enrichment["lifecycle_state"] == "RETIRED"
    assert enrichment["scheduled"] is False
    assert terminal["status"] == "TERMINAL_PROVIDER_NO_HISTORICAL_ROWS"
    assert terminal["no_additional_paid_retry_authorized"] is True
    assert "TERMINAL_PROVIDER_STATE_NO_PAID_RETRY" in audit
    assert "terminal['no_additional_paid_retry_authorized'] is True" in audit
    assert "Fail closed to the ratified terminal provider state before secret access" in enrichment_text
    assert "steps.terminal.outputs.retired != 'true'" in enrichment_text
    assert "CFGI_RETIRED_NO_DISPATCH_PASS" in enrichment_text
    assert enrichment_text.index("Fail closed to the ratified terminal provider state before secret access") < enrichment_text.index("Verify CFGI secret only after provenance and budget gates pass")


def test_current_cfgi_terminal_audit_accepts_v2_paid_ledger() -> None:
    repo = Path(__file__).parents[2]
    audit = (repo / ".github/workflows/historical-altseason-cfgi-run-audit.yml").read_text()
    assert "HISTORICAL_ALTSEASON_CFGI_PAID_ATTEMPT_LEDGER_v2" in audit
    assert "ledger['cumulative_actual_credits_used']==10518" in audit
    assert "verified_prior_cumulative_actual_credits_used" in audit
