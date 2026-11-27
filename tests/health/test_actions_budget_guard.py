from datetime import datetime, timezone

from scripts.health.build_actions_budget_guard import apply_owner_conservation, evaluate

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


def test_future_snapshot_never_looks_fresh():
    d = evaluate(snapshot(100, observed="2026-09-30T12:00:00Z"),
                 datetime(2026, 9, 29, tzinfo=UTC))
    assert d["state"] == "UNKNOWN"
    assert d["snapshot_status"] == "FUTURE_USAGE_SNAPSHOT"


def test_naive_timestamp_rejected():
    assert evaluate(snapshot(100, observed="2026-09-29T12:00:00"),
                    datetime(2026, 9, 29, 13, tzinfo=UTC))["state"] == "UNKNOWN"


def test_bad_numeric_values_fail_closed():
    now = datetime(2026, 9, 29, 13, tzinfo=UTC)
    for value in (True, "100", float("nan"), float("inf"), -1, 10**400):
        assert evaluate(snapshot(value), now)["state"] == "UNKNOWN"
    for value in (float("nan"), float("inf"), 0, -1, True):
        data = snapshot(100)
        data["freshness_max_hours"] = value
        assert evaluate(data, now)["state"] == "UNKNOWN"


def test_exhausted_allowance_does_not_assume_overage_permission_or_hard_stop():
    now = datetime(2026, 9, 29, 13, tzinfo=UTC)
    for stop in (None, "false"):
        d = evaluate(snapshot(3000, stop=stop), now)
        assert d["included_capacity_exhausted"] is True
        assert d["protected_a_blocked"] is None
        assert d["overage_authorization"] == "UNKNOWN"


def test_invalid_snapshot_is_not_echoed_to_public_output():
    d = evaluate({"contract": "WRONG", "secret": "private"}, datetime(2026, 9, 29, tzinfo=UTC))
    assert d["usage_snapshot"] == {}
    assert evaluate([], datetime(2026, 9, 29, tzinfo=UTC))["state"] == "UNKNOWN"


def test_owner_conservation_is_value_free_and_expires_without_inventing_recovery():
    now = datetime(2026, 11, 24, tzinfo=UTC)
    policy = {"contract": "RESOURCE_CONSERVATION_OWNER_POLICY_v1",
              "automatic_spend_authority": False,
              "new_workflows_or_agent_schedules": False,
              "never_bypass_required_ci": True,
              "actions_critical_until_utc": "2026-12-01T00:00:00Z"}
    d = apply_owner_conservation(evaluate({}, now), policy, now)
    assert d["state"] == "UNKNOWN"
    assert d["measured_budget_state"] == "UNKNOWN"
    assert d["effective_operating_state"] == "CRITICAL"
    assert d["snapshot_status"] == "INVALID_CONTRACT"
    assert d["protected_a_blocked"] is None
    assert d["usage_pct"] is None
    assert d["authority"]["workflow_disable"] is False
    reset = datetime(2026, 12, 1, tzinfo=UTC)
    assert apply_owner_conservation(evaluate({}, reset), policy, reset)["state"] == "UNKNOWN"
    policy["automatic_spend_authority"] = True
    assert apply_owner_conservation(evaluate({}, now), policy, now)["state"] == "UNKNOWN"


def test_owner_conservation_keeps_fresh_measurement_separate():
    now = datetime(2026, 9, 29, 13, tzinfo=UTC)
    measured = evaluate(snapshot(100, observed="2026-09-29T12:00:00Z"), now)
    assert measured["state"] == "NORMAL"
    policy = {"contract": "RESOURCE_CONSERVATION_OWNER_POLICY_v1",
              "automatic_spend_authority": False,
              "new_workflows_or_agent_schedules": False,
              "never_bypass_required_ci": True,
              "actions_critical_until_utc": "2026-12-01T00:00:00Z"}
    result = apply_owner_conservation(measured, policy, now)
    assert result["state"] == "CRITICAL"
    assert result["measured_budget_state"] == "NORMAL"
    assert result["effective_operating_state"] == "CRITICAL"
    assert result["usage_pct"] == measured["usage_pct"]
    assert measured["state"] == "NORMAL"
