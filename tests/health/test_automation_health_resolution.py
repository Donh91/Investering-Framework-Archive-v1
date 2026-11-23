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
        "workflow_count": 178,
        "registered_workflow_count": 202,
        "scheduled_workflow_count": 41,
        "api_error": None,
        "warnings": [],
        "orphaned_registered_workflows": [],
        "workflows": [
            {"workflow": "cycle-navigator-autonomous-calibration-loop.yml", "findings": []},
            {"workflow": "situation-room-daily-static.yml", "findings": ["RECOVERING_AFTER_RECENT_FAILURES"] if amber else []},
        ],
    }) + "\n")


def test_record_status_preserves_compact_machine_verification_evidence(tmp_path):
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0, 1)
    path = record_status(tmp_path, 10, 1, "abc123")
    row = json.loads(path.read_text())
    assert row["head_sha"] == "abc123"
    assert row["workflow_count"] == 178
    assert row["registered_workflow_count"] == 202
    assert row["scheduled_workflow_count"] == 41
    assert row["api_error"] is None
    assert row["warnings"] == []
    assert row["findings"] == [
        "situation-room-daily-static.yml:RECOVERING_AFTER_RECENT_FAILURES"
    ]


def test_two_zero_red_runs_resolve_health_incidents_without_mutation(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# old red\n")
    original = incident.read_bytes()

    write_health(tmp_path, "2026-09-24T10:00:00Z", 0)
    record_status(tmp_path, 10, 1, "a" * 40, "schedule")
    assert resolve_recovered(tmp_path, 10) == []

    write_health(tmp_path, "2026-09-24T18:00:00Z", 0)
    record_status(tmp_path, 11, 1, "a" * 40, "schedule")
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
    record_status(tmp_path, 10, 1, "a" * 40, "schedule")
    write_health(tmp_path, "2026-09-24T18:00:00Z", 1)
    record_status(tmp_path, 11, 1, "a" * 40, "schedule")
    assert resolve_recovered(tmp_path, 11) == []


def test_two_attempts_of_same_run_do_not_count_as_two_recovery_runs(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# old red\n")
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0)
    record_status(tmp_path, 10, 1, "a" * 40, "schedule")
    write_health(tmp_path, "2026-09-24T10:05:00Z", 0)
    record_status(tmp_path, 10, 2, "a" * 40, "schedule")
    assert resolve_recovered(tmp_path, 10) == []


def test_resolution_requires_current_run_to_be_latest_recovery_evidence(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# old red\n")
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0)
    record_status(tmp_path, 10, 1, "a" * 40, "schedule")
    write_health(tmp_path, "2026-09-24T18:00:00Z", 0)
    record_status(tmp_path, 11, 1, "a" * 40, "schedule")
    assert resolve_recovered(tmp_path, 10) == []
    created = resolve_recovered(tmp_path, 11)
    assert len(created) == 1


def test_manual_success_is_not_automatic_recovery(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# real health error\n")
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0)
    record_status(tmp_path, 10, 1, "a" * 40, "workflow_dispatch")
    write_health(tmp_path, "2026-09-24T18:00:00Z", 0)
    record_status(tmp_path, 11, 1, "a" * 40, "workflow_dispatch")
    assert resolve_recovered(tmp_path, 11) == []


def test_amber_zero_red_does_not_close_incident(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# real health error\n")
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0, 1)
    record_status(tmp_path, 10, 1, "a" * 40, "schedule")
    write_health(tmp_path, "2026-09-24T18:00:00Z", 0)
    record_status(tmp_path, 11, 1, "a" * 40, "schedule")
    assert resolve_recovered(tmp_path, 11) == []


def test_incomplete_health_api_does_not_close_incident(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# real health error\n")
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0)
    report = tmp_path / "research/architecture_health/LATEST_AUTOMATION_HEALTH.json"
    raw = json.loads(report.read_text())
    raw["api_error"] = "UPSTREAM_SOURCE_UNAVAILABLE"
    report.write_text(json.dumps(raw) + "\n")
    record_status(tmp_path, 10, 1, "a" * 40, "schedule")
    write_health(tmp_path, "2026-09-24T18:00:00Z", 0)
    record_status(tmp_path, 11, 1, "a" * 40, "schedule")
    assert resolve_recovered(tmp_path, 11) == []


def test_unknown_legacy_event_and_sha_do_not_close_incident(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# real health error\n")
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0)
    record_status(tmp_path, 10, 1)
    write_health(tmp_path, "2026-09-24T18:00:00Z", 0)
    record_status(tmp_path, 11, 1, "a" * 40, "schedule")
    assert resolve_recovered(tmp_path, 11) == []


def test_prior_green_health_does_not_auto_close_new_incident(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-20-attempt-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# later RED incident\n")
    for run_id, moment in ((10, "10:00"), (11, "18:00")):
        write_health(tmp_path, f"2026-09-24T{moment}:00Z", 0)
        record_status(tmp_path, run_id, 1, "a" * 40, "schedule")
    assert resolve_recovered(tmp_path, 11) == []
    write_health(tmp_path, "2026-09-25T10:00:00Z", 0)
    record_status(tmp_path, 21, 1, "a" * 40, "schedule")
    assert resolve_recovered(tmp_path, 21) == []
    write_health(tmp_path, "2026-09-25T18:00:00Z", 0)
    record_status(tmp_path, 22, 1, "a" * 40, "schedule")
    produced = resolve_recovered(tmp_path, 22)
    assert len(produced) == 1
    receipt = json.loads((tmp_path / produced[0]).read_text())
    assert receipt["incident_origin_run_id"] == 20
    assert receipt["fleet_green_run_ids"] == [21, 22]
    assert receipt["original_consumer_verified"] is False


def test_unverifiable_incident_filename_does_not_get_auto_closed(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-unverified.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# unknown origin\n")
    for run_id, moment in ((10, "10:00"), (11, "18:00")):
        write_health(tmp_path, f"2026-09-24T{moment}:00Z", 0)
        record_status(tmp_path, run_id, 1, "a" * 40, "schedule")
    assert resolve_recovered(tmp_path, 11) == []


def test_fleet_receipt_never_claims_consumer_success(tmp_path):
    incident = tmp_path / "09_SOURCE_QA/incidents/INCIDENT_automation-production-health-1.md"
    incident.parent.mkdir(parents=True)
    incident.write_text("# old red\n")
    write_health(tmp_path, "2026-09-24T10:00:00Z", 0)
    record_status(tmp_path, 10, 1, "a" * 40, "schedule")
    write_health(tmp_path, "2026-09-24T18:00:00Z", 0)
    record_status(tmp_path, 11, 1, "a" * 40, "schedule")
    receipt = json.loads((tmp_path / resolve_recovered(tmp_path, 11)[0]).read_text())
    assert receipt["evidence_scope"] == "FLEET_HEALTH_ONLY"
    assert receipt["fleet_green_run_ids"] == [10, 11]
    assert receipt["original_consumer_verified"] is False
    assert receipt["data_source_first_known_verified"] is False
    assert receipt["incident_repaired_or_merged_by_this_receipt"] is False
