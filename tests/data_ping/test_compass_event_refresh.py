import unittest
from datetime import datetime, timedelta, timezone

from scripts.data_ping.compass_event_refresh import evaluate, heat_state


NOW = datetime(2026, 9, 18, 16, 0, tzinfo=timezone.utc)


def auto_state(*, source_sha="new-source", breadth=0.60, ethbtc=0.031, validation="PASS", fresh_minutes=10):
    fresh=(NOW-timedelta(minutes=fresh_minutes)).isoformat().replace("+00:00","Z")
    return {
        "packet_sha256": source_sha,
        "packet_generated_at_utc": fresh,
        "validation_status": validation,
        "decision_context_status": "PASS",
        "blockers": [],
        "normalized_state": {
            "live_market": {"btc_usdt": 80000.0, "eth_usdt": 2500.0, "ethbtc": ethbtc},
            "breadth": {"aggregate": {"advance_ratio": breadth}},
            "entry_signal_reference": {"state": "WAIT"},
        },
        "deltas_since_prior_auto_packet": {
            "btc_usdt": {"pct": 0.2},
            "eth_usdt": {"pct": 0.3},
            "ethbtc": {"pct": 0.1},
        },
        "source_health": {
            "hourly_market": {
                "freshness": {
                    "status": "PASS",
                    "pointer_freshness": {"status": "PASS", "timestamp": fresh, "max_age_seconds": 10800},
                    "retrieval_freshness": {"status": "PASS", "timestamp": fresh, "max_age_seconds": 10800},
                    "session_coverage_freshness": {"status": "PASS", "timestamp": fresh, "max_age_seconds": 10800},
                    "source_observation_freshness": {"status": "PASS", "timestamp": fresh, "max_age_seconds": 10800},
                }
            }
        },
    }


def entry(*, temp="NORMAL", btc=1.0, eth=1.5, median=1.0):
    return {
        "execution_temperature": temp,
        "market_snapshot": {
            "btc_return_24h_pct": btc,
            "eth_return_24h_pct": eth,
            "median_return_24h_pct": median,
        },
    }


def cn_package(*, risk="NORMAL", risk_class="UNKNOWN", distribution="NONE", direction="NO_EDGE"):
    return {
        "market_state": "Structured test context.",
        "base_case_this_week": "Narrative context only.",
        "base_case_2_3_weeks": "Narrative context only.",
        "base_case_4_8_weeks": "Narrative context only.",
        "decision_projection": {
            "contract": "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1",
            "next_1_3d": {"direction": direction, "summary": "Structured test lane."},
            "next_5_7d": {"direction": direction, "summary": "Structured test lane."},
            "weeks_4_8": {
                "state": "UNCLEAR",
                "warning": "NONE",
                "direction": "NO_EDGE",
                "action_posture": "HOLD",
                "summary": "Structured test lane.",
                "through_date": None,
                "horizon_days": None,
                "eta": "UNKNOWN",
                "confidence": "LOW",
            },
            "protection": {
                "pullback_risk_state": risk,
                "pullback_class": risk_class,
                "distribution_risk": distribution,
                "eta_window": "UNKNOWN",
                "confidence_quality": "HIGH" if risk in {"HIGH", "CONFIRMED"} else "MEDIUM",
                "drivers": ["Structured test protection state."],
                "invalidation": "Later structured evidence must explicitly change this state.",
            },
        },
    }

def compass(*, source_sha="old-source", action="HOLD_WAIT", data_status="OK", issued_at=None, protection=None):
    out = {
        "issued_at_utc": issued_at or (NOW-timedelta(hours=6)).isoformat().replace("+00:00","Z"),
        "source_bindings": {"auto_market_state": {"packet_sha256": source_sha}},
        "data_status": data_status,
        "action_now": action,
        "market_now": {"directional_state": "NEUTRAL", "regime": "HOLD_WAIT"},
        "capitalization_ladder": [
            {"segment": "BTC", "status": "HOLD", "action": "HOLD"},
            {"segment": "ETH", "status": "HOLD", "action": "HOLD"},
            {"segment": "LARGE_CAPS", "status": "WAIT", "action": "WAIT"},
            {"segment": "MID_CAPS", "status": "WAIT", "action": "WAIT"},
            {"segment": "SMALL_CAPS", "status": "WAIT", "action": "WAIT"},
            {"segment": "MICROCAPS", "status": "HARD_WAIT", "action": "HARD_WAIT"},
        ],
    }
    if protection is not None:
        out["protection_tracker"] = protection
    return out


def decision(**kwargs):
    a=kwargs.pop("auto", auto_state())
    return evaluate(
        auto_state=a,
        auto_pointer={"packet_sha256": a["packet_sha256"]},
        latest_compass=kwargs.pop("latest", compass()),
        entry_latest=kwargs.pop("entry_latest", entry()),
        prior_state=kwargs.pop("prior_state", {"last_heat_state": "NORMAL"}),
        cn_package=cn_package(),
        cn_binding={"status": "PASS"},
        now=NOW,
    )


class CompassEventRefreshTests(unittest.TestCase):
    def test_same_source_never_dispatches(self):
        a=auto_state(source_sha="same")
        out=decision(auto=a, latest=compass(source_sha="same"), entry_latest=entry(temp="HOT", btc=9))
        self.assertFalse(out["dispatch"])
        self.assertFalse(out["upstream_refresh_required"])
        self.assertEqual(out["reason"], "LATEST_COMPASS_ALREADY_BINDS_CURRENT_OWNER_PACKET")

    def test_stale_owner_evidence_requests_upstream_recovery_before_same_source_noop(self):
        a=auto_state(source_sha="same", fresh_minutes=240)
        out=decision(auto=a, latest=compass(source_sha="same"))
        self.assertFalse(out["dispatch"])
        self.assertTrue(out["upstream_refresh_required"])
        self.assertEqual(out["reason"], "UPSTREAM_OWNER_FRESHNESS_STALE")
        self.assertTrue(out["owner_freshness_reasons"])

    def test_action_change_dispatches(self):
        out=decision(latest=compass(action="PREPARE"))
        self.assertTrue(out["dispatch"])
        self.assertIn("ACTION_STATE_CHANGED", out["cause_codes"])

    def test_hot_episode_enters_once(self):
        out=decision(entry_latest=entry(temp="HOT", btc=9), prior_state={"last_heat_state": "NORMAL"})
        self.assertTrue(out["dispatch"])
        self.assertIn("MARKET_HEAT_ENTERED", out["cause_codes"])

        second=decision(
            entry_latest=entry(temp="HOT", btc=9),
            prior_state={"last_heat_state": "HOT_UPSIDE_REASSESSMENT"},
        )
        self.assertFalse(second["dispatch"])

    def test_symmetric_downside_heat_is_reassessment_only(self):
        state, detail=heat_state(entry(temp="NORMAL", btc=-8.2, eth=-4, median=-2))
        self.assertEqual(state, "HOT_DOWNSIDE_REASSESSMENT")
        self.assertEqual(
            detail["downside_semantics"],
            "SYMMETRIC_REUSE_OF_EXISTING_HEAT_MAGNITUDES_EVENT_ONLY",
        )
        out=decision(
            entry_latest=entry(temp="NORMAL", btc=-8.2, eth=-4, median=-2),
            prior_state={"last_heat_state": "NORMAL"},
        )
        self.assertTrue(out["dispatch"])
        self.assertIn("MARKET_HEAT_ENTERED", out["cause_codes"])

    def test_heat_does_not_dispatch_from_degraded_evidence(self):
        a=auto_state(validation="FAIL")
        latest=compass(data_status="DEGRADED", action="HOLD_WAIT_DATA_DEGRADED")
        latest["market_now"]={"directional_state":"UNAVAILABLE","regime":"DATA_DEGRADED"}
        latest["capitalization_ladder"]=[
            {"segment":seg,"status":"UNAVAILABLE"}
            for seg in ["BTC","ETH","LARGE_CAPS","MID_CAPS","SMALL_CAPS","MICROCAPS"]
        ]
        out=decision(
            auto=a,
            latest=latest,
            entry_latest=entry(temp="HOT", btc=9),
            prior_state={"last_heat_state": "NORMAL"},
        )
        self.assertFalse(out["dispatch"])
        self.assertNotIn("MARKET_HEAT_ENTERED", out.get("cause_codes", []))

    def test_degraded_owner_health_dispatches_fail_closed_update(self):
        a=auto_state(validation="FAIL")
        out=decision(auto=a)
        self.assertTrue(out["dispatch"])
        self.assertIn("DATA_HEALTH_CHANGED", out["cause_codes"])
        self.assertEqual(out["current_data_status"], "DEGRADED")

    def test_nonprotective_market_change_inside_cooldown_is_suppressed(self):
        latest=compass(issued_at=(NOW-timedelta(minutes=30)).isoformat().replace("+00:00","Z"))
        latest["market_now"]={"directional_state":"MIXED","regime":"HOLD_WAIT"}
        out=decision(
            latest=latest,
            prior_state={
                "last_heat_state": "NORMAL",
                "last_requested_source_sha": "previous-request",
                "last_request_at_utc": (NOW-timedelta(hours=1)).isoformat().replace("+00:00","Z"),
            },
        )
        self.assertFalse(out["dispatch"])
        self.assertEqual(out["reason"], "COOLDOWN_ACTIVE")
        self.assertIn("MARKET_STATE_CHANGED", out["suppressed_cause_codes"])

    def test_data_health_degradation_bypasses_cooldown(self):
        a=auto_state(validation="FAIL")
        out=decision(
            auto=a,
            latest=compass(issued_at=(NOW-timedelta(minutes=30)).isoformat().replace("+00:00","Z")),
            prior_state={
                "last_heat_state": "NORMAL",
                "last_requested_source_sha": "previous-request",
                "last_request_at_utc": (NOW-timedelta(hours=1)).isoformat().replace("+00:00","Z"),
            },
        )
        self.assertTrue(out["dispatch"])
        self.assertTrue(out["protective_bypass"])
        self.assertIn("DATA_HEALTH_CHANGED", out["cause_codes"])

    def test_downside_heat_bypasses_cooldown(self):
        out=decision(
            latest=compass(issued_at=(NOW-timedelta(minutes=30)).isoformat().replace("+00:00","Z")),
            entry_latest=entry(temp="NORMAL", btc=-8.5, eth=-5, median=-2),
            prior_state={
                "last_heat_state": "NORMAL",
                "last_requested_source_sha": "previous-request",
                "last_request_at_utc": (NOW-timedelta(hours=1)).isoformat().replace("+00:00","Z"),
            },
        )
        self.assertTrue(out["dispatch"])
        self.assertTrue(out["protective_bypass"])
        self.assertIn("MARKET_HEAT_ENTERED", out["cause_codes"])

    def test_request_in_flight_suppresses_duplicate_risk_on_dispatch(self):
        out=decision(
            latest=(lambda x: (x.update({"market_now":{"directional_state":"MIXED","regime":"HOLD_WAIT"}}) or x))(compass()),
            prior_state={
                "last_heat_state": "NORMAL",
                "last_requested_source_sha": "new-source",
                "last_request_at_utc": (NOW-timedelta(minutes=5)).isoformat().replace("+00:00","Z"),
            },
        )
        self.assertFalse(out["dispatch"])
        self.assertEqual(out["reason"], "REQUEST_IN_FLIGHT")
        self.assertIn("MARKET_STATE_CHANGED", out["suppressed_cause_codes"])

    def test_nonprotective_event_defers_to_imminent_scheduled_slot(self):
        near=datetime(2026, 9, 18, 18, 0, tzinfo=timezone.utc)  # 20:00 CPH, 17m before fixed slot
        a=auto_state()
        out=evaluate(
            auto_state=a,
            auto_pointer={"packet_sha256": a["packet_sha256"]},
            latest_compass=(lambda x: (x.update({"market_now":{"directional_state":"MIXED","regime":"HOLD_WAIT"}}) or x))(compass()),
            entry_latest=entry(),
            prior_state={"last_heat_state": "NORMAL"},
            cn_package=cn_package(),
            cn_binding={"status": "PASS"},
            now=near,
        )
        self.assertFalse(out["dispatch"])
        self.assertEqual(out["reason"], "SCHEDULED_SLOT_IMMINENT")
        self.assertIn("MARKET_STATE_CHANGED", out["suppressed_cause_codes"])
        self.assertLessEqual(out["seconds_to_next_scheduled_compass"], 30*60)

    def test_protective_event_does_not_wait_for_imminent_slot(self):
        near=datetime(2026, 9, 18, 18, 0, tzinfo=timezone.utc)
        a=auto_state(validation="FAIL")
        out=evaluate(
            auto_state=a,
            auto_pointer={"packet_sha256": a["packet_sha256"]},
            latest_compass=compass(),
            entry_latest=entry(),
            prior_state={"last_heat_state": "NORMAL"},
            cn_package=cn_package(),
            cn_binding={"status": "PASS"},
            now=near,
        )
        self.assertTrue(out["dispatch"])
        self.assertTrue(out["protective_bypass"])

    def test_protection_escalation_bypasses_cooldown(self):
        a=auto_state()
        latest=compass(
            protection={
                "pullback_risk_state": "NORMAL",
                "pullback_class": "UNKNOWN",
                "distribution_risk": "NONE",
                "eta_window": "UNKNOWN",
                "confidence_quality": "MEDIUM",
                "reentry_state": "INACTIVE",
                "last_material_change_at": (NOW-timedelta(hours=6)).isoformat().replace("+00:00","Z"),
            }
        )
        out=evaluate(
            auto_state=a,
            auto_pointer={"packet_sha256": a["packet_sha256"]},
            latest_compass=latest,
            entry_latest=entry(),
            prior_state={
                "last_heat_state": "NORMAL",
                "last_requested_source_sha": "previous-request",
                "last_request_at_utc": (NOW-timedelta(hours=1)).isoformat().replace("+00:00","Z"),
            },
            cn_package=cn_package(risk="HIGH", risk_class="DISTRIBUTION", distribution="CONFIRMED", direction="DOWN"),
            cn_binding={"status": "PASS"},
            now=NOW,
        )
        self.assertTrue(out["dispatch"])
        self.assertTrue(out["protective_bypass"])
        self.assertIn("PROTECTION_STATE_CHANGED", out["cause_codes"])
        self.assertEqual(out["current_protection_tracker"]["pullback_risk_state"], "HIGH")

    def test_reentry_watch_persists_without_ungoverned_confirmation(self):
        a=auto_state()
        latest=compass(
            protection={
                "pullback_risk_state": "NORMAL",
                "pullback_class": "UNKNOWN",
                "distribution_risk": "NONE",
                "eta_window": "UNKNOWN",
                "confidence_quality": "MEDIUM",
                "reentry_state": "WAIT_FOR_RECLAIM",
                "last_material_change_at": (NOW-timedelta(hours=6)).isoformat().replace("+00:00","Z"),
            }
        )
        out=evaluate(
            auto_state=a,
            auto_pointer={"packet_sha256": a["packet_sha256"]},
            latest_compass=latest,
            entry_latest=entry(),
            prior_state={"last_heat_state": "NORMAL"},
            cn_package=cn_package(),
            cn_binding={"status": "PASS"},
            now=NOW,
        )
        self.assertFalse(out["dispatch"])
        self.assertEqual(out["current_protection_tracker"]["reentry_state"], "WAIT_FOR_RECLAIM")
        self.assertFalse(out["current_protection_tracker"]["authority"]["portfolio_execution"])

    def test_unbound_request_retries_after_timeout(self):
        out=decision(
            latest=(lambda x: (x.update({"market_now":{"directional_state":"MIXED","regime":"HOLD_WAIT"}}) or x))(compass()),
            prior_state={
                "last_heat_state": "NORMAL",
                "last_requested_source_sha": "new-source",
                "last_request_at_utc": (NOW-timedelta(minutes=30)).isoformat().replace("+00:00","Z"),
            },
        )
        self.assertTrue(out["dispatch"])
        self.assertIn("PRIOR_REQUEST_NOT_BOUND_RETRY", out["cause_codes"])
        self.assertIn("MARKET_STATE_CHANGED", out["cause_codes"])


if __name__ == "__main__":
    unittest.main()
