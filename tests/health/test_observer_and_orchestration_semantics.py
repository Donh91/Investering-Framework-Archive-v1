from pathlib import Path


def text(name: str) -> str:
    return (Path('.github/workflows') / name).read_text(encoding='utf-8')


def test_health_observer_does_not_fail_because_observed_fleet_is_red():
    workflow = text('automation-production-health.yml')
    assert 'Record observed fleet status without failing the observer' in workflow
    assert 'Enforce production health result after durable publication' not in workflow
    assert 'run: exit 2' not in workflow
    assert 'LATEST_AUTOMATION_HEALTH.json' in workflow
    assert 'git show "origin/main:$path"' in workflow


def test_observability_and_remediation_schedule_order():
    health = text('automation-production-health.yml')
    remediation = text('remediation-maturation.yml')
    dashboard = text('operations-dashboard.yml')
    assert "cron: '30 5 * * *'" in health and "cron: '30 17 * * *'" in health
    assert "cron: '45 5 * * *'" in remediation and "cron: '45 17 * * *'" in remediation
    assert "cron: '0 6 * * *'" in dashboard and "cron: '0 18 * * *'" in dashboard
    for workflow in (health, remediation, dashboard):
        assert "timezone: 'Europe/Copenhagen'" in workflow
        assert 'group: framework-main-writer' in workflow
        assert "ref: main" in workflow


def test_codex_ready_queue_is_visible_but_not_self_merging():
    workflow = text('remediation-maturation.yml')
    assert 'issues: write' in workflow
    assert 'CODEX READY REMEDIATION QUEUE' in workflow
    assert 'LATEST_CODEX_READY_TASKS.json' in workflow
    assert 'merge pull request' not in workflow.lower()
    assert 'automatic_code_write' not in workflow
