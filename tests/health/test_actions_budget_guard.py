from datetime import datetime, timezone

from scripts.health.build_actions_budget_guard import evaluate

UTC = timezone.utc


def snapshot(used, allowance=3000, *, observed="2026-09-20T12:00:00Z", reset="2026-10-01", stop=False):
    return {
        "contract": "GITHUB_ACTIONS_USAGE_SNAPSHOT_v1",
        "source_type": "TEST",
        "source_ref": "fixture",
        "observed_at_utc": observed,
        "cycle_start_date_utc": "2026-09-01",
        "reset_date_utc": reset,
        "included_minutes": allowance,
        "used_minutes": used,
        "stop_usage": stop,
        "freshness_max_hours": 720,
    }


def test_90_percent_enters_critical():
    state = evaluate(snapshot(2700), datetime(2026, 9, 20, 12, tzinfo=UTC))
    assert state["state"] == "CRITICAL"


def test_80_percent_enters_conserve_when_projection_not_materially_critical():
    state = evaluate(snapshot(2400, observed="2026-09-29T12:00:00Z"), datetime(2026, 9, 29, 12, tzinfo=UTC))
    assert state["state"] == "CONSERVE"


def test_elevated_threshold():
    state = evaluate(snapshot(2000, observed="2026-09-29T12:00:00Z"), datetime(2026, 9, 29, 12, tzinfo=UTC))
    assert state["state"] == "ELEVATED"


def test_normal_threshold():
    state = evaluate(snapshot(1200, observed="2026-09-29T12:00:00Z"), datetime(2026, 9, 29, 12, tzinfo=UTC))
    assert state["state"] == "NORMAL"


def test_hard_stop_marks_protected_blocked():
    state = evaluate(snapshot(3000, observed="2026-09-29T16:08:11Z", stop=True), datetime(2026, 9, 30, 12, tzinfo=UTC))
    assert state["state"] == "CRITICAL"
    assert state["protected_a_blocked"] is True


def test_stale_snapshot_is_unknown():
    s = snapshot(1800, observed="2026-09-10T00:00:00Z")
    s["freshness_max_hours"] = 48
    state = evaluate(s, datetime(2026, 9, 20, 0, tzinfo=UTC))
    assert state["state"] == "UNKNOWN"
    assert state["snapshot_status"] == "STALE_USAGE_SNAPSHOT"


def test_pre_reset_snapshot_becomes_unknown_after_reset():
    state = evaluate(snapshot(3000, observed="2026-09-29T16:08:11Z", stop=True), datetime(2026, 10, 1, 0, 1, tzinfo=UTC))
    assert state["state"] == "UNKNOWN"
    assert state["snapshot_status"] == "SNAPSHOT_PRE_RESET"


def test_invalid_snapshot_never_fabricates_usage():
    state = evaluate({"contract": "WRONG"}, datetime(2026, 9, 30, 12, tzinfo=UTC))
    assert state["state"] == "UNKNOWN"
    assert state["usage_pct"] is None
