import unittest
from datetime import datetime, timedelta, timezone

from scripts.data_ping.compass_event_refresh import _ladder_materially_changed, _missing_scheduled_freeze, _public_refresh_message, evaluate, heat_state


NOW = datetime(2026, 9, 18, 16, 0, tzinfo=timezone.utc)


def auto_state(*, source_sha="new-source", breadth=0.60, ethbtc=0.031, validation="PASS", fresh_minutes=10, observation_open="2026-09-18T15:00:00Z", predecessor_observation="2026-09-18T14:00:00Z", deltas=None):
    fresh=(NOW-timedelta(minutes=fresh_minutes)).isoformat().replace("+00:00","Z")
    return {
        "packet_sha256": source_sha,
        "packet_generated_at_utc": fresh,
        "validation_status": validation,
        "decision_context_status": "PASS",
        "blockers": [],
        "normalized_state": {
            "live_market": {"btc_usdt": 80000.0, "eth_usdt": 2500.0, "ethbtc": ethbtc, "observation_open_utc": observation_open},
            "breadth": {"aggregate": {"advance_ratio": breadth}},
            "entry_signal_reference": {"state": "WAIT"},
        },
        "predecessor": {
            "status": "AVAILABLE",
            "market_observation_open_utc": predecessor_observation,
        },
        "deltas_since_prior_auto_packet": deltas if deltas is not None else {
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
        "market_now": {"directional_state": "BULLISH", "regime": "HOLD_WAIT"},
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
    def test_schema_only_unavailable_rung_is_not_material(self):
        previous = [
            {"segment": "BTC", "status": "HOLD"},
            {"segment": "ETH", "status": "HOLD"},
            {"segment": "MICROCAPS", "status": "HARD_WAIT"},
        ]
        current = previous + [{"segment": "MEMES", "status": "UNAVAILABLE"}]
        self.assertFalse(_ladder_materially_changed(previous, current))
        promoted = previous + [{"segment": "MEMES", "status": "PREPARE"}]
        self.assertTrue(_ladder_materially_changed(previous, promoted))

    def test_missed_morning_freeze_triggers_current_time_recovery_not_sell(self):
        zeros = {k: {"pct": 0.0} for k in ("btc_usdt", "eth_usdt", "ethbtc")}
        a = auto_state(
            observation_open="2026-09-18T15:00:00Z",
            predecessor_observation="2026-09-18T15:00:00Z",
            deltas=zeros,
        )
        latest = compass(
            issued_at=(NOW - timedelta(hours=14)).isoformat().replace("+00:00", "Z")
        )
        result = decision(auto=a, latest=latest)
        self.assertTrue(result["dispatch"])
        self.assertIn("SCHEDULED_FREEZE_MISSING", result["cause_codes"])
        self.assertEqual(result["missing_scheduled_freeze"], "MORNING")
        self.assertFalse(result["authority"]["portfolio_execution"])
        self.assertFalse(result["authority"]["forecast_change"])

    def test_latest_issue_after_slot_does_not_trigger_recovery(self):
        a = auto_state(
            observation_open="2026-09-18T15:00:00Z",
            predecessor_observation="2026-09-18T15:00:00Z",
            deltas={k: {"pct": 0.0} for k in ("btc_usdt", "eth_usdt", "ethbtc")},
        )
        result = decision(auto=a, latest=compass(
            issued_at=(NOW - timedelta(hours=6)).isoformat().replace("+00:00", "Z")
        ))
        self.assertFalse(result["dispatch"])
        self.assertIsNone(result["missing_scheduled_freeze"])
        self.assertEqual(result["reason"], "NO_MATERIAL_CHANGE")

    def test_missed_freeze_respects_existing_inflight_request(self):
        old = (NOW-timedelta(hours=14)).isoformat().replace("+00:00","Z")
        result = decision(latest=compass(issued_at=old), prior_state={
            "last_heat_state": "NORMAL",
            "last_requested_source_sha": "new-source",
            "last_request_at_utc": (NOW - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        })
        self.assertFalse(result["dispatch"])
        self.assertEqual(result["reason"], "REQUEST_IN_FLIGHT")
        self.assertIn("SCHEDULED_FREEZE_MISSING", result["suppressed_cause_codes"])

    def test_missed_freeze_grace_and_dst_boundary(self):
        issue = "2026-03-29T06:16:00Z"  # 08:16 Europe/Copenhagen CEST
        self.assertIsNone(_missing_scheduled_freeze(
            datetime(2026, 3, 29, 6, 59, tzinfo=timezone.utc), issue))
        self.assertEqual(_missing_scheduled_freeze(
            datetime(2026, 3, 29, 7, 3, tzinfo=timezone.utc), issue), "MORNING")
        self.assertIsNone(_missing_scheduled_freeze(
            datetime(2026, 3, 29, 7, 3, tzinfo=timezone.utc),
            "2026-03-29T06:17:00Z"
        ))
        # After transition to CET, 08:17 local is 07:17 UTC.
        self.assertEqual(_missing_scheduled_freeze(
            datetime(2026, 10, 25, 8, 3, tzinfo=timezone.utc),
            "2026-10-25T07:16:00Z"), "MORNING")
        self.assertIsNone(_missing_scheduled_freeze(
            datetime(2026, 10, 25, 7, 59, tzinfo=timezone.utc),
            "2026-10-25T07:16:00Z"))

    def test_previous_evening_miss_survives_midnight(self):
        # Oct 11 02:55 CPH is Oct 11 00:55Z: yesterday's 20:17 slot
        # was missed, even though today's 08:17 slot is not due.
        now = datetime(2026, 10, 11, 0, 55, tzinfo=timezone.utc)
        morning_only = "2026-10-10T06:20:00Z"
        self.assertEqual(
            _missing_scheduled_freeze(now, morning_only), "PREVIOUS_EVENING")
        # Genuine late evening/current-time issue supersedes missed slot.
        self.assertIsNone(_missing_scheduled_freeze(
            now, "2026-10-10T22:35:49Z"))
        # A short delay before the 20:17+45m grace should not alarm.
        before_grace = datetime(2026, 10, 10, 18, 45, tzinfo=timezone.utc)
        self.assertIsNone(_missing_scheduled_freeze(before_grace, morning_only))

    def test_missed_publication_message_is_not_fake_market_move(self):
        text = _public_refresh_message(["SCHEDULED_FREEZE_MISSING"])
        self.assertIn("Scheduled Compass update missed", text)
        self.assertIn("does not indicate a new market move", text)
        self.assertNotIn("Material market move or decision-state", text)
        retry = _public_refresh_message(["PRIOR_REQUEST_NOT_BOUND_RETRY", "SCHEDULED_FREEZE_MISSING"])
        self.assertEqual(retry, text)
        mixed = _public_refresh_message(["SCHEDULED_FREEZE_MISSING", "MARKET_STATE_CHANGED"])
        self.assertNotEqual(mixed, text)
        market = _public_refresh_message(["MARKET_STATE_CHANGED"])
        self.assertIn("reassessment", market)
        protective = _public_refresh_message(["PROTECTION_STATE_CHANGED"])
        self.assertIn("Protection or re-entry", protective)

    def test_no_recovery_without_verifiable_original_issue_time(self):
        self.assertIsNone(_missing_scheduled_freeze(NOW, None))
        self.assertIsNone(_missing_scheduled_freeze(NOW, "not-utc"))
        self.assertIsNone(_missing_scheduled_freeze(NOW, "2099-01-01T00:00:00Z"))

    def test_same_fresh_source_does_not_hide_missed_scheduled_publication(self):
        # As-of clocks are internally consistent: this SAME immutable packet
        # existed BEFORE the 08:17 CPH slot, is still fresh at 09:05 CPH,
        # but the last issued forecast was 08:16 CPH. A missed publication
        # is a different event from new market-data materiality.
        a = auto_state(source_sha="same")
        src = "2026-09-18T06:14:00Z"
        a["packet_generated_at_utc"] = src
        for status in a["source_health"]["hourly_market"]["freshness"].values():
            if isinstance(status, dict):
                status["timestamp"] = src
        a["normalized_state"]["live_market"]["observation_open_utc"] = "2026-09-18T06:00:00Z"
        a["predecessor"]["market_observation_open_utc"] = "2026-09-18T05:00:00Z"
        kw = dict(auto_state=a, auto_pointer={"packet_sha256": "same"},
                  latest_compass=compass(source_sha="same",
                                        issued_at="2026-09-18T06:16:00Z"),
                  entry_latest=entry(), prior_state={"last_heat_state": "NORMAL"},
                  cn_package=cn_package(), cn_binding={"status": "PASS"})
        before_grace = evaluate(**kw, now=datetime(2026, 9, 18, 7, 0, tzinfo=timezone.utc))
        self.assertFalse(before_grace["dispatch"])
        self.assertEqual(before_grace["reason"], "LATEST_COMPASS_ALREADY_BINDS_CURRENT_OWNER_PACKET")
        missed = evaluate(**kw, now=datetime(2026, 9, 18, 7, 5, tzinfo=timezone.utc))
        self.assertTrue(missed["dispatch"])
        self.assertEqual(missed["missing_scheduled_freeze"], "MORNING")
        self.assertIn("SCHEDULED_FREEZE_MISSING", missed["cause_codes"])
        self.assertFalse(missed["authority"]["portfolio_execution"])
        self.assertFalse(missed["authority"]["forecast_change"])

    def test_same_source_missed_slot_tracks_inflight_and_retries_after_20m(self):
        # Temporal replay: source 08:14 CPH, issued 08:16, 08:17 scheduled
        # slot missing, 09:05 current-time refresh request never bound.
        a = auto_state(source_sha="same")
        original = "2026-09-18T06:14:00Z"
        a["packet_generated_at_utc"] = original
        for value in a["source_health"]["hourly_market"]["freshness"].values():
            if isinstance(value, dict):
                value["timestamp"] = original
        a["normalized_state"]["live_market"]["observation_open_utc"] = "2026-09-18T06:00:00Z"
        a["predecessor"]["market_observation_open_utc"] = "2026-09-18T05:00:00Z"
        kw = dict(
            auto_state=a,
            auto_pointer={"packet_sha256": "same"},
            latest_compass=compass(source_sha="same", issued_at="2026-09-18T06:16:00Z"),
            entry_latest=entry(),
            prior_state={
                "last_heat_state": "NORMAL",
                "last_requested_source_sha": "same",
                "last_request_at_utc": "2026-09-18T07:05:00Z",
            },
            cn_package=cn_package(), cn_binding={"status": "PASS"},
        )
        in_flight = evaluate(**kw, now=datetime(2026, 9, 18, 7, 15, tzinfo=timezone.utc))
        self.assertFalse(in_flight["dispatch"])
        self.assertEqual(in_flight["reason"], "REQUEST_IN_FLIGHT")
        self.assertIn("SCHEDULED_FREEZE_MISSING", in_flight["suppressed_cause_codes"])

        retry = evaluate(**kw, now=datetime(2026, 9, 18, 7, 25, tzinfo=timezone.utc))
        self.assertTrue(retry["dispatch"])
        self.assertEqual(retry["reason"], "MATERIAL_REASSESSMENT_REQUIRED")
        self.assertIn("PRIOR_REQUEST_NOT_BOUND_RETRY", retry["cause_codes"])
        self.assertIn("SCHEDULED_FREEZE_MISSING", retry["cause_codes"])
        self.assertFalse(retry["authority"]["portfolio_execution"])
        self.assertIn("Scheduled Compass update missed",
                      _public_refresh_message(retry["cause_codes"]))

        # Requests for other source identities cannot create false same-SHA
        # retry evidence against the unchanged current packet.
        unrelated = dict(kw, prior_state={
            "last_heat_state": "NORMAL",
            "last_requested_source_sha": "different-source",
            "last_request_at_utc": "2026-09-18T07:05:00Z",
        })
        fresh = evaluate(**unrelated, now=datetime(2026, 9, 18, 7, 25, tzinfo=timezone.utc))
        self.assertNotIn("PRIOR_REQUEST_NOT_BOUND_RETRY", fresh.get("cause_codes", []))

    def test_persistent_downside_heat_does_not_duplicate_missed_slot_recovery(self):
        # Accepted same-source recovery at 09:05 CPH; a persistent HOT
        # downside episode is NOT a new protection deterioration.
        a = auto_state(source_sha="same")
        original = "2026-09-18T06:14:00Z"
        a["packet_generated_at_utc"] = original
        for value in a["source_health"]["hourly_market"]["freshness"].values():
            if isinstance(value, dict):
                value["timestamp"] = original
        a["normalized_state"]["live_market"]["observation_open_utc"] = "2026-09-18T06:00:00Z"
        a["predecessor"]["market_observation_open_utc"] = "2026-09-18T05:00:00Z"
        prior = {
            "last_heat_state": "HOT_DOWNSIDE_REASSESSMENT",
            "last_requested_source_sha": "same",
            "last_request_at_utc": "2026-09-18T07:05:00Z",
        }
        kw = dict(
            auto_state=a, auto_pointer={"packet_sha256": "same"},
            latest_compass=compass(source_sha="same", issued_at="2026-09-18T06:16:00Z"),
            entry_latest=entry(temp="NORMAL", btc=-8.5, eth=-5, median=-2),
            prior_state=prior, cn_package=cn_package(), cn_binding={"status": "PASS"},
        )
        in_flight = evaluate(**kw, now=datetime(2026, 9, 18, 7, 10, tzinfo=timezone.utc))
        self.assertFalse(in_flight["dispatch"])
        self.assertEqual(in_flight["reason"], "REQUEST_IN_FLIGHT")
        self.assertFalse(in_flight["protective_bypass"])
        self.assertIn("SCHEDULED_FREEZE_MISSING", in_flight["suppressed_cause_codes"])

        retry = evaluate(**kw, now=datetime(2026, 9, 18, 7, 26, tzinfo=timezone.utc))
        self.assertTrue(retry["dispatch"])
        self.assertIn("PRIOR_REQUEST_NOT_BOUND_RETRY", retry["cause_codes"])
        self.assertIn("SCHEDULED_FREEZE_MISSING", retry["cause_codes"])
        self.assertFalse(retry["protective_bypass"])

        # A genuinely NEW downside episode still bypasses the in-flight
        # cooldown so urgent protective reassessment remains possible.
        newly_hot = evaluate(
            **dict(kw, prior_state=dict(prior, last_heat_state="NORMAL")),
            now=datetime(2026, 9, 18, 7, 10, tzinfo=timezone.utc),
        )
        self.assertTrue(newly_hot["dispatch"])
        self.assertTrue(newly_hot["protective_bypass"])
        self.assertIn("MARKET_HEAT_ENTERED", newly_hot["cause_codes"])

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

    def test_action_change_dispatches_without_masquerading_as_market_change(self):
        out=decision(latest=compass(action="PREPARE"))
        self.assertTrue(out["dispatch"])
        self.assertIn("ACTION_STATE_CHANGED", out["cause_codes"])
        self.assertNotIn("MARKET_STATE_CHANGED", out["cause_codes"])

    def test_repeated_same_price_observation_does_not_emit_market_state_change(self):
        zeros = {
            "btc_usdt": {"pct": 0.0},
            "eth_usdt": {"pct": 0.0},
            "ethbtc": {"pct": 0.0},
        }
        a=auto_state(
            observation_open="2026-09-18T15:00:00Z",
            predecessor_observation="2026-09-18T15:00:00Z",
            deltas=zeros,
        )
        latest=compass()
        out=decision(auto=a, latest=latest)
        self.assertFalse(out["dispatch"])
        self.assertEqual(out["reason"], "NO_MATERIAL_CHANGE")
        self.assertEqual(
            out["current_market_state"]["directional_state"],
            "UNCHANGED_NO_NEW_OBSERVATION",
        )
        self.assertFalse(out["current_market_state"]["new_price_observation"])
        self.assertNotIn("MARKET_STATE_CHANGED", out.get("cause_codes", []))

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


    def _source_continuity_case(self, *, now=None, original_minutes_old=165,
                                current_open=None, prior_open=None,
                                source_sha="new-source", original_sha="old-source"):
        now = now or datetime(2026, 10, 22, 12, 0, tzinfo=timezone.utc)
        old_clock = now - timedelta(minutes=original_minutes_old)
        new_clock = now - timedelta(minutes=5)
        origin = old_clock.isoformat().replace("+00:00", "Z")
        actual = new_clock.isoformat().replace("+00:00", "Z")
        prev_obs = prior_open or (now - timedelta(hours=4)).replace(
            minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z")
        next_obs = current_open or (now - timedelta(hours=1)).replace(
            minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z")
        a = auto_state(source_sha=source_sha, observation_open=next_obs,
                       predecessor_observation=prev_obs,
                       deltas={k: {"pct": 0} for k in ("btc_usdt", "eth_usdt", "ethbtc")})
        a["packet_generated_at_utc"] = actual
        for row in a["source_health"]["hourly_market"]["freshness"].values():
            if isinstance(row, dict):
                row["timestamp"] = actual
        latest = compass(source_sha=original_sha, issued_at=(
            now - timedelta(hours=2)).isoformat().replace("+00:00", "Z"))
        latest["market_now"]["market_observation_open_utc"] = prev_obs
        latest["source_bindings"]["auto_market_state"]["freshness"] = {
            "status": "PASS",
            "checks": [{"lane": lane, "timestamp": origin, "status": "PASS",
                        "max_age_seconds": 10800}
                       for lane in ("pointer_freshness", "retrieval_freshness",
                                    "session_coverage_freshness",
                                    "source_observation_freshness", "auto_market_state_packet")],
        }
        return dict(auto_state=a, auto_pointer={"packet_sha256": source_sha},
                    latest_compass=latest, entry_latest=entry(),
                    prior_state={"last_heat_state": "NORMAL"},
                    cn_package=cn_package(), cn_binding={"status": "PASS"}, now=now)

    def test_temporary_source_continuity_new_verified_hour(self):
        out = evaluate(**self._source_continuity_case())
        self.assertTrue(out["dispatch"])
        self.assertIn("OFFICIAL_SOURCE_REFRESH_DUE", out["cause_codes"])
        self.assertEqual(out["temporary_source_continuity"]["expires_local_date"], "2026-11-01")
        self.assertFalse(out["authority"]["forecast_change"])
        self.assertFalse(out["authority"]["portfolio_execution"])
        self.assertIn("does not imply a material market move",
                      _public_refresh_message(["OFFICIAL_SOURCE_REFRESH_DUE"]))

    def test_temporary_source_continuity_requires_new_source_and_hour(self):
        kw = self._source_continuity_case()
        kw["auto_state"]["normalized_state"]["live_market"]["observation_open_utc"] = (
            kw["latest_compass"]["market_now"]["market_observation_open_utc"])
        self.assertNotIn("OFFICIAL_SOURCE_REFRESH_DUE",
                         evaluate(**kw).get("cause_codes", []))
        same = self._source_continuity_case(source_sha="same", original_sha="same")
        self.assertFalse(evaluate(**same)["dispatch"])
        self.assertEqual(evaluate(**same)["reason"], "LATEST_COMPASS_ALREADY_BINDS_CURRENT_OWNER_PACKET")

    def test_temporary_source_continuity_never_rewrites_invalid_clock(self):
        for change in ("missing", "failed", "future", "no_approaching_expiry"):
            with self.subTest(change=change):
                kw = self._source_continuity_case()
                checks = kw["latest_compass"]["source_bindings"]["auto_market_state"]["freshness"]
                if change == "missing":
                    checks.pop("checks")
                elif change == "failed":
                    checks["checks"][0]["status"] = "FAIL"
                elif change == "future":
                    checks["checks"][0]["timestamp"] = "2099-01-01T00:00:00Z"
                else:
                    for row in checks["checks"]:
                        row["max_age_seconds"] = 18000
                self.assertNotIn("OFFICIAL_SOURCE_REFRESH_DUE",
                                 evaluate(**kw).get("cause_codes", []))

    def test_temporary_source_continuity_expires_november_first(self):
        nov = datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc)
        out = evaluate(**self._source_continuity_case(now=nov))
        self.assertNotIn("OFFICIAL_SOURCE_REFRESH_DUE", out.get("cause_codes", []))
        self.assertFalse(out["temporary_source_continuity"]["active"])

    def test_temporary_source_continuity_respects_inflight_dedupe(self):
        kw = self._source_continuity_case()
        kw["prior_state"] = {
            "last_heat_state": "NORMAL",
            "last_requested_source_sha": "new-source",
            "last_request_at_utc": (kw["now"] - timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
        }
        out = evaluate(**kw)
        self.assertFalse(out["dispatch"])
        self.assertEqual(out["reason"], "REQUEST_IN_FLIGHT")
        self.assertIn("OFFICIAL_SOURCE_REFRESH_DUE", out["suppressed_cause_codes"])

    def test_temporary_source_continuity_rejects_degraded_required_lane(self):
        kw = self._source_continuity_case()
        kw["cn_binding"] = {"status": "FAIL"}
        out = evaluate(**kw)
        self.assertNotIn("OFFICIAL_SOURCE_REFRESH_DUE", out.get("cause_codes", []))

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
