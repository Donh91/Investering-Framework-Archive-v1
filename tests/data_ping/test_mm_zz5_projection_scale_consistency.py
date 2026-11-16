"""ZZ5 original source contracts; no frozen weekly forecast is reissued."""
import copy
import unittest
from datetime import datetime, timezone

from scripts.data_ping import native_handlekompas as nh
from scripts.cycle_navigator.weekly_offline_issuer import build_offline_value
from tests.cycle_navigator.test_weekly_offline_issuer import fixtures

UTC_AT = datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc)

def auto():
    t = "2026-09-16T18:08:16Z"
    fresh = {"status": "PASS", "timestamp": t, "max_age_seconds": 10800}
    return {
        "contract": "AUTO_MARKET_STATE_PACKET_v1",
        "packet_generated_at_utc": "2026-09-16T18:09:48Z",
        "packet_sha256": "source-fixture",
        "validation_status": "PASS", "decision_context_status": "PASS",
        "blockers": [], "optional_degraded_lanes": [],
        "predecessor": {"status": "NOT_AVAILABLE_FIRST_PACKET", "market_observation_open_utc": None},
        "deltas_since_prior_auto_packet": {"btc_usdt": {"pct": -0.3},
            "eth_usdt": {"pct": -0.7}, "ethbtc": {"pct": -0.4}},
        "normalized_state": {"live_market": {
            "btc_usdt": 75654.0, "eth_usdt": 2396.86, "ethbtc": 0.03168,
            "observation_open_utc": "2026-09-16T18:00:00Z"}},
        "source_health": {"hourly_market": {"status": "PASS",
            "freshness": {"status": "PASS", "pointer_freshness": dict(fresh),
                "retrieval_freshness": dict(fresh),
                "session_coverage_freshness": {"status": "PASS", "timestamp": "2026-09-16T18:00:00Z", "max_age_seconds": 10800},
                "source_observation_freshness": {"status": "PASS", "timestamp": "2026-09-16T18:00:00Z", "max_age_seconds": 10800}}}}
    }

def cn(*, direction="DOWN", summary="UNIQUE_TYYPED_CN_1_3D_PATH"):
    return {"issue_number": 26, "base_case_this_week": "Weekly conditional path.",
        "decision_projection": {"contract": "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1",
            "next_1_3d": {"direction": direction, "summary": summary},
            "next_5_7d": {"direction": "MIXED", "summary": "Mixed weekly path"},
            "next_2_3w": {"direction": "NO_EDGE", "summary": "No 2-3w edge."}},
        "forecast_freeze": {"bull_bear_scale": {"horizons": {
            "5_7d": {"bull": 4, "bear": 6, "bias": "LEAN_BEARISH"}}}}}

class MMZZ5ContractTest(unittest.TestCase):
    def test_1_3d_carries_typed_cn_summary_on_matching_direction(self):
        s="UNIQUE_TYYPED_CN_1_3D_PATH"
        rows=nh.horizon_map(auto(),{"NOW":"HOLD_WAIT"},cn(summary=s),as_of=UTC_AT)
        self.assertEqual(rows["NEXT_1_3D"]["expected_direction"],"DOWN")
        self.assertEqual(rows["NEXT_1_3D"]["expected_path"],s)
        self.assertEqual(nh.bull_bear_scale(rows)["horizons"]["1_3d"]["bias"],"BEARISH")

    def test_missing_typed_summary_does_not_invent_a_narrative(self):
        rows=nh.horizon_map(auto(),{"NOW":"HOLD_WAIT"},cn(summary=""),as_of=UTC_AT)
        self.assertEqual(rows["NEXT_1_3D"]["expected_direction"],"DOWN")
        self.assertEqual(rows["NEXT_1_3D"]["expected_path"],"No eligible typed Cycle Navigator 1-3 day path is published.")

    def test_action_override_does_not_mislabel_source_summary_as_forecast(self):
        rows=nh.horizon_map(auto(),{"NOW":"PREPARE"},cn(direction="SIDEWAYS",summary="Sideways only"),as_of=UTC_AT)
        self.assertEqual(rows["NEXT_1_3D"]["expected_direction"],"UP")
        self.assertIn("Action posture differs",rows["NEXT_1_3D"]["expected_path"])
        self.assertNotIn("Sideways only",rows["NEXT_1_3D"]["expected_path"])

    def test_display_is_still_neutral_for_mixed_not_auto_promoted(self):
        rows=nh.horizon_map(auto(),{"NOW":"HOLD_WAIT"},cn(),as_of=UTC_AT)
        h=nh.bull_bear_scale(rows)["horizons"]["5_7d"]
        self.assertEqual((h["bull"],h["bear"],h["bias"]),(5,5,"NEUTRAL"))

    def test_offline_bearish_lean_integer_and_label_agree_all_horizons(self):
        f=fixtures()
        before=copy.deepcopy(f[2])
        output=build_offline_value(*f,2026,46,34,33)
        for row in output["forecast_freeze"]["bull_bear_scale"]["horizons"].values():
            self.assertEqual((row["bull"],row["bear"],row["bias"]),(4,6,"LEAN_BEARISH"))
            self.assertEqual(nh._bull_bear_bias(row["bull"],row["bear"]),row["bias"])
        self.assertEqual(f[2],before,"prior freeze must remain immutable")

    def test_offline_bullish_lean_integer_and_label_agree(self):
        f=list(fixtures())
        f[0]=copy.deepcopy(f[0])
        f[0]["completed_week_hourly_capture"]["hourly_sequence"]["btc"]["week_range"]["close"]=80500
        f[0]["completed_week_hourly_capture"]["hourly_sequence"]["eth"]["week_range"]["close"]=2350
        output=build_offline_value(*f,2026,46,34,33)
        for row in output["forecast_freeze"]["bull_bear_scale"]["horizons"].values():
            self.assertEqual((row["bull"],row["bear"],row["bias"]),(6,4,"LEAN_BULLISH"))
            self.assertEqual(nh._bull_bear_bias(row["bull"],row["bear"]),row["bias"])
