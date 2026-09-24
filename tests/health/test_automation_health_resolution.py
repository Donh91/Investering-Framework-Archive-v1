from __future__ import annotations

import json
from pathlib import Path

from scripts.health.automation_health_resolution import record_status, resolve_recovered


def write_health(root: Path, generated: str, red: int, amber: int = 0):
    path = root / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({
        "generated_at_utc": generated,
        "status": "AMBER" if amber else "GREEN",
        "red_count": red,
        "amber_count": amber,
    }) + "\n")


def test_two_zero_red_runs_resolve_health_incidents_without_mutation(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# old red\n")
    original = incident.read_bytes()

    write_health(tmp_path, "2026-09-24T10:00:00Z", 0, 1)
    record_status(tmp_path, 10, 1)
    assert resolve_recovered(tmp_path, 10) == []

    write_health(tmp_path, "2026-09-24T18:00:00Z", 0, 2)
    record_status(tmp_path, 11, 1)
    created = resolve_recovered(tmp_path, 11)
    assert len(created) == 1
    assert incident.read_bytes() == original
    receipt = json.loads((tmp_path / created[0]).read_text())
    assert receipt["incident_path"].endswith("INCIDENT_automation-production-health-1.md")
    assert receipt["successful_run_id"] == 11


def test_recent_red_run_blocks_resolution(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# old red\n")
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0)
    record_status(tmp_path, 10, 1)
    write_health(tmp_path, "2026-09-24T18:00:00Z", 1)
    record_status(tmp_path, 11, 1)
    assert resolve_recovered(tmp_path, 11) == []


def test_two_attempts_of_same_run_do_not_count_as_two_recovery_runs(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# old red\n")
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0, 1)
    record_status(tmp_path, 10, 1)
    write_health(tmp_path, "2026-09-24T10:05:00Z", 0, 1)
    record_status(tmp_path, 10, 2)
    assert resolve_recovered(tmp_path, 10) == []


def test_resolution_requires_current_run_to_be_latest_recovery_evidence(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# old red\n")
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0)
    record_status(tmp_path, 10, 1)
    write_health(tmp_path, "2026-09-24T18:00:00Z", 0)
    record_status(tmp_path, 11, 1)
    assert resolve_recovered(tmp_path, 10) == []
    created = resolve_recovered(tmp_path, 11)
    assert len(created) == 1
