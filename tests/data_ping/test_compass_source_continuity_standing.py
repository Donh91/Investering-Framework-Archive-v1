"""P-1a: standing source-continuity re-issue (Bridge FABLE52-SHIPPABLE T5).

Each test marked FAILS_ON_BASE fails against compass_event_refresh.py blob
43f4f625 (continuity hard-stopped 2026-11-01) and passes with the patch.
Tests marked INVARIANT must pass on both: they pin the rule that a refresh is
admitted only from a genuinely newer completed hour, never by extending a clock.
"""
import unittest
from datetime import date, datetime, timedelta, timezone
from unittest import mock

from scripts.data_ping import compass_event_refresh as cer
from tests.data_ping import test_compass_event_refresh as base_tests  # module import: do not re-collect its TestCase

# 2026-11-11 12:30Z = 13:30 Copenhagen: after the morning slot, with a Compass
# issued after that slot, so SCHEDULED_FREEZE_MISSING cannot explain a dispatch.
NOV = datetime(2026, 11, 11, 12, 30, tzinfo=timezone.utc)


def case(**kw):
    """Continuity fixture with NO other material cause.

    The shared fixture's prior Compass direction differs from the freshly
    derived one, which would add MARKET_STATE_CHANGED and hide what this file
    tests. Align the prior direction with the derived one so that the only
    possible cause is the source-continuity rule.
    """
    built = base_tests.CompassEventRefreshTests._source_continuity_case(None, **kw)
    probe = cer.evaluate(**built)
    current = (probe.get("current_market_state") or {}).get("directional_state")
    if current:
        built["latest_compass"]["market_now"]["directional_state"] = current
    return built


class StandingSourceContinuityTests(unittest.TestCase):
    def test_refresh_admitted_after_november_first(self):  # FAILS_ON_BASE
        out = cer.evaluate(**case(now=NOV))
        self.assertTrue(out["temporary_source_continuity"]["active"])
        self.assertTrue(out["dispatch"])
        self.assertEqual(out["cause_codes"], ["OFFICIAL_SOURCE_REFRESH_DUE"])
        self.assertIsNone(out["missing_scheduled_freeze"])
        # Without the rule the same evidence is NO_MATERIAL_CHANGE (the 1 Nov regression).
        with mock.patch.object(cer, "SOURCE_CONTINUITY_END", date(2026, 11, 1)):
            bounded = cer.evaluate(**case(now=NOV))
        self.assertFalse(bounded["dispatch"])
        self.assertEqual(bounded["reason"], "NO_MATERIAL_CHANGE")
        self.assertFalse(out["authority"]["forecast_change"])
        self.assertFalse(out["authority"]["portfolio_execution"])

    def test_refresh_admitted_when_original_clock_already_expired(self):  # FAILS_ON_BASE
        # Mirrors 2026-11-11 11:00Z -> 15:08Z: expired 90 min ago, newer hour exists.
        out = cer.evaluate(**case(now=NOV, original_minutes_old=270))
        self.assertTrue(out["dispatch"])
        self.assertIn("OFFICIAL_SOURCE_REFRESH_DUE", out["cause_codes"])
        expiry = cer.parse_utc(out["temporary_source_continuity"]["expiry_at_utc"])
        self.assertEqual(expiry, NOV - timedelta(minutes=90))  # original clock, not extended

    def test_refresh_is_not_blocked_by_nonprotective_cooldown(self):  # FAILS_ON_BASE
        kw = case(now=NOV)
        kw["prior_state"] = {
            "last_heat_state": "NORMAL",
            "last_requested_source_sha": "old-source",
            "last_request_at_utc": (NOV - timedelta(minutes=150)).isoformat().replace("+00:00", "Z"),
        }
        out = cer.evaluate(**kw)
        self.assertLess(out["last_request_age_seconds"], cer.NON_PROTECTIVE_COOLDOWN_SECONDS)
        self.assertFalse(out["protective_bypass"])
        self.assertTrue(out["dispatch"])
        self.assertEqual(out["reason"], "MATERIAL_REASSESSMENT_REQUIRED")

    def test_output_states_standing_policy(self):  # FAILS_ON_BASE
        out = cer.evaluate(**case(now=NOV))
        self.assertIsNone(out["temporary_source_continuity"]["expires_local_date"])
        self.assertEqual(out["temporary_source_continuity"]["policy"], "STANDING_UNTIL_REBOUNDED")

    def test_same_observation_hour_never_admits_refresh(self):  # INVARIANT
        kw = case(now=NOV, original_minutes_old=270)
        kw["auto_state"]["normalized_state"]["live_market"]["observation_open_utc"] = (
            kw["latest_compass"]["market_now"]["market_observation_open_utc"])
        out = cer.evaluate(**kw)
        self.assertNotIn("OFFICIAL_SOURCE_REFRESH_DUE", out.get("cause_codes", []))
        self.assertFalse(out["temporary_source_continuity"]["refresh_admitted"])

    def test_same_source_packet_never_admits_refresh(self):  # INVARIANT
        out = cer.evaluate(**case(now=NOV, source_sha="same", original_sha="same"))
        self.assertFalse(out["dispatch"])
        self.assertEqual(out["reason"], "LATEST_COMPASS_ALREADY_BINDS_CURRENT_OWNER_PACKET")

    def test_far_from_expiry_does_not_refresh(self):  # INVARIANT
        out = cer.evaluate(**case(now=NOV, original_minutes_old=60))
        self.assertNotIn("OFFICIAL_SOURCE_REFRESH_DUE", out.get("cause_codes", []))

    def test_degraded_lane_never_admits_refresh(self):  # INVARIANT
        kw = case(now=NOV)
        kw["cn_binding"] = {"status": "FAIL"}
        self.assertNotIn("OFFICIAL_SOURCE_REFRESH_DUE", cer.evaluate(**kw).get("cause_codes", []))

    def test_stale_hourly_requests_upstream_instead_of_refresh(self):  # INVARIANT
        kw = case(now=NOV)
        kw["hourly_pointer"] = {}  # unverified pointer must fail closed
        out = cer.evaluate(**kw)
        self.assertFalse(out["dispatch"])
        self.assertTrue(out["upstream_refresh_required"])

    def test_inactive_before_window_start(self):  # INVARIANT
        early = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
        out = cer.evaluate(**case(now=early))
        self.assertFalse(out["temporary_source_continuity"]["active"])
        self.assertNotIn("OFFICIAL_SOURCE_REFRESH_DUE", out.get("cause_codes", []))

    def test_rollback_rebounding_the_end_date_restores_expiry(self):  # ROLLBACK
        with mock.patch.object(cer, "SOURCE_CONTINUITY_END", date(2026, 11, 1)):
            out = cer.evaluate(**case(now=NOV))
        self.assertFalse(out["temporary_source_continuity"]["active"])
        self.assertNotIn("OFFICIAL_SOURCE_REFRESH_DUE", out.get("cause_codes", []))
        self.assertEqual(out["temporary_source_continuity"]["expires_local_date"], "2026-11-01")


if __name__ == "__main__":
    unittest.main()
