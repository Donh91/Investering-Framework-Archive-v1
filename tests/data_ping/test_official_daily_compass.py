import json
import hashlib
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.data_ping.native_handlekompas import (
    CAPITALIZATION_ORDER,
    HORIZON_ORDER,
    OFFICIAL_AUTHORITY,
    build_official_compass,
    build_public_projection,
    write_official_compass,
)


class OfficialDailyCompassTest(unittest.TestCase):
    def auto(self, *, breadth=0.19, validation="PASS", decision="PASS", blockers=None, btc=75654.0, eth=2396.86, ethbtc=0.03168, deltas=None):
        return {
            "contract": "AUTO_MARKET_STATE_PACKET_v1",
            "packet_generated_at_utc": "2026-09-16T18:09:48Z",
            "packet_sha256": "packet-sha",
            "source_snapshot": {"exact_commit_sha": "source-commit"},
            "validation_status": validation,
            "decision_context_status": decision,
            "blockers": blockers or [],
            "optional_degraded_lanes": [],
            "deltas_since_prior_auto_packet": deltas if deltas is not None else {
                "btc_usdt": {"pct": -0.3},
                "eth_usdt": {"pct": -0.7},
                "ethbtc": {"pct": -0.4},
            },
            "normalized_state": {
                "live_market": {"btc_usdt": btc, "eth_usdt": eth, "ethbtc": ethbtc, "observation_open_utc": "2026-09-16T18:00:00Z"},
                "breadth": {"aggregate": {"advance_ratio": breadth, "advancers": 19, "decliners": 78, "equal_weight_mean_return_24h_pct": -2.59}},
                "entry_signal_reference": {"state": "WAIT"},
                "btc_dominance": {"value_pct": 58.4},
                "settled_etf": {"btc_reported_total_musd": -100.0, "eth_reported_total_musd": 50.0},
                "stablecoin_liquidity": {"total_usd": 300_000_000_000.0},
                "derivatives": {},
                "sentiment": {"classification": "NEUTRAL"},
                "altseason_context": {"blockchaincenter_altcoin_season": {"horizons": {"90": {"published_score": 27}}}},
            },
            "source_health": {
                "hourly_market": {
                    "status": "PASS",
                    "freshness": {
                        "status": "PASS",
                        "pointer_freshness": {"status": "PASS", "timestamp": "2026-09-16T18:08:16Z", "max_age_seconds": 10800},
                        "retrieval_freshness": {"status": "PASS", "timestamp": "2026-09-16T18:08:16Z", "max_age_seconds": 10800},
                        "session_coverage_freshness": {"status": "PASS", "timestamp": "2026-09-16T18:00:00Z", "max_age_seconds": 10800},
                        "source_observation_freshness": {"status": "PASS", "timestamp": "2026-09-16T18:00:00Z", "max_age_seconds": 10800},
                    },
                },
                "breadth": {"status": "PASS"},
                "btc_dominance": {"status": "PASS"},
                "settled_etf": {"status": "PASS"},
                "stablecoin_liquidity": {"status": "PASS"},
                "derivatives": {"status": "PASS"},
                "sentiment": {"status": "PASS"},
                "altseason_context": {"status": "PASS"},
                "entry_signal_reference": {"status": "PASS"},
            },
        }

    def cn(self):
        return {
            "issue_number": 26,
            "market_state": "Unresolved, volatile consolidation with elevated pullback risk.",
            "base_case_this_week": "W38 remains an unresolved, volatile consolidation with elevated pullback risk rather than a confirmed breakdown or broad risk expansion.",
            "base_case_2_3_weeks": "Selective ETH leadership may emerge, but volatile consolidation persists until breadth improves.",
            "altseason_countdown": [{"phase": "Broad altseason — PAUSED", "window": "No calendar ETA"}],
        }

    def build(self, root, *, include_cn=True, issued_at=None, run_reason="SCHEDULED_DAILY", **kwargs):
        return build_official_compass(
            self.auto(**kwargs),
            packet_path=Path("04_MARKET_LEARNING/entry_signals/auto_market_state/runs/test.json"),
            cn_package=self.cn() if include_cn else None,
            cn_binding={"status": "PASS"} if include_cn else {"status": "UNAVAILABLE"},
            repo_root=Path(root),
            issued_at=issued_at or datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc),
            run_reason=run_reason,
        )

    def test_deterministic_same_input_same_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self.build(tmp)
            b = self.build(tmp)
            self.assertEqual(a, b)
            self.assertEqual(a["compass_sha256"], b["compass_sha256"])

    def test_required_horizons_and_ladder_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            self.assertEqual(tuple(out["horizons"].keys()), HORIZON_ORDER)
            self.assertEqual(tuple(row["segment"] for row in out["capitalization_ladder"]), CAPITALIZATION_ORDER)
            self.assertEqual(out["authority"], OFFICIAL_AUTHORITY)
            self.assertFalse(out["authority"]["portfolio_execution"])
            self.assertEqual(out["horizons"]["CYCLE_ALTCOINS_3_8W"]["state"], "CONSOLIDATION")
            self.assertEqual(out["horizons"]["CYCLE_ALTCOINS_3_8W"]["through_date"], "2026-10-14")
            self.assertEqual(out["horizons"]["CYCLE_ALTCOINS_3_8W"]["warning"], "NONE")

    def test_missing_values_remain_null_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp, btc=None, eth=None, ethbtc=None)
            self.assertIsNone(out["market_reference"]["btc_usdt"])
            self.assertIsNone(out["market_reference"]["eth_usdt"])
            values = {row["feature_id"]: row["value"] for row in out["evidence_snapshot"]["selected_features"]}
            self.assertIsNone(values["btc_usdt"])
            self.assertIsNone(values["eth_usdt"])

    def test_degraded_state_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp, validation="FAIL", decision="DEGRADED", blockers=["hourly_market"])
            self.assertEqual(out["data_status"], "DEGRADED")
            self.assertTrue(all(row["status"] == "UNAVAILABLE" for row in out["capitalization_ladder"]))
            self.assertTrue(all(out["horizons"][key]["expected_direction"] == "UNAVAILABLE" for key in HORIZON_ORDER))

    def test_stale_owner_packet_fails_closed_at_issuance_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp, issued_at=datetime(2026, 9, 17, 0, 30, tzinfo=timezone.utc))
            self.assertEqual(out["data_status"], "DEGRADED")
            self.assertEqual(out["source_bindings"]["auto_market_state"]["freshness"]["status"], "STALE_OR_UNAVAILABLE")
            self.assertTrue(all(out["horizons"][key]["expected_direction"] == "UNAVAILABLE" for key in HORIZON_ORDER))

    def test_missing_cn_context_fails_forward_lanes_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp, include_cn=False)
            self.assertEqual(out["data_status"], "DEGRADED")
            self.assertNotEqual(out["horizons"]["NEXT_12H"]["expected_direction"], "UNAVAILABLE")
            for key in ("NEXT_1_3D", "NEXT_5_7D", "CYCLE_ALTCOINS_3_8W"):
                self.assertEqual(out["horizons"][key]["expected_direction"], "UNAVAILABLE")

    def test_missing_deltas_never_create_bullish_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp, breadth=0.55, deltas={})
            self.assertEqual(out["market_now"]["regime"], "PREPARE")
            self.assertEqual(out["market_now"]["directional_state"], "MIXED")

    def test_public_projection_does_not_leak_internal_bindings_or_threshold_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            public = build_public_projection(out)
            self.assertNotIn("source_bindings", public)
            self.assertNotIn("evidence_snapshot", public)
            self.assertNotIn("native_action_contract", public)
            for row in public["capitalization_ladder"]:
                self.assertNotIn("upgrade_trigger", row)
                self.assertNotIn("deterioration_trigger", row)

    def test_scheduled_daily_freeze_is_single_and_immutable(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            out = self.build(tmp)
            first = write_official_compass(out, root)
            second = write_official_compass(out, root)
            self.assertEqual(first["status"], "WRITTEN")
            self.assertEqual(second["status"], "EXISTING_DAILY_FREEZE")
            frozen = json.loads(Path(first["path"]).read_text())
            self.assertEqual(frozen["compass_sha256"], out["compass_sha256"])
            pointer = json.loads((root / "LATEST_COMPASS.json").read_text())
            public_pointer = json.loads((root / "PUBLIC_LATEST_COMPASS.json").read_text())
            self.assertEqual(pointer["compass_content_sha256"], hashlib.sha256(Path(first["path"]).read_bytes()).hexdigest())
            self.assertEqual(pointer["public_projection_content_sha256"], public_pointer["public_projection_content_sha256"])

    def test_morning_and_evening_are_independent_immutable_slots(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            morning = self.build(
                tmp,
                run_reason="SCHEDULED_MORNING",
                issued_at=datetime(2026, 9, 16, 6, 17, tzinfo=timezone.utc),
            )
            evening = self.build(
                tmp,
                run_reason="SCHEDULED_EVENING",
                issued_at=datetime(2026, 9, 16, 18, 17, tzinfo=timezone.utc),
            )
            self.assertNotEqual(morning["compass_id"], evening["compass_id"])

            first_morning = write_official_compass(morning, root)
            first_evening = write_official_compass(evening, root)
            retry_morning = write_official_compass(morning, root)
            retry_evening = write_official_compass(evening, root)

            self.assertEqual(first_morning["status"], "WRITTEN")
            self.assertEqual(first_evening["status"], "WRITTEN")
            self.assertEqual(retry_morning["status"], "EXISTING_DAILY_FREEZE")
            self.assertEqual(retry_evening["status"], "EXISTING_DAILY_FREEZE")
            self.assertNotEqual(first_morning["path"], first_evening["path"])
            self.assertEqual(
                json.loads(Path(first_morning["path"]).read_text())["run_reason"],
                "SCHEDULED_MORNING",
            )
            self.assertEqual(
                json.loads(Path(first_evening["path"]).read_text())["run_reason"],
                "SCHEDULED_EVENING",
            )

    def test_on_demand_same_source_rerun_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            first_compass = self.build(
                tmp,
                run_reason="ON_DEMAND",
                issued_at=datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc),
            )
            rerun_compass = self.build(
                tmp,
                run_reason="ON_DEMAND",
                issued_at=datetime(2026, 9, 16, 20, 18, tzinfo=timezone.utc),
            )
            self.assertEqual(first_compass["compass_id"], rerun_compass["compass_id"])
            self.assertNotEqual(first_compass["compass_sha256"], rerun_compass["compass_sha256"])

            first = write_official_compass(first_compass, root)
            frozen_bytes = Path(first["path"]).read_bytes()
            rerun = write_official_compass(rerun_compass, root)

            self.assertEqual(first["status"], "WRITTEN")
            self.assertEqual(rerun["status"], "EXISTING_DAILY_FREEZE")
            self.assertEqual(Path(first["path"]).read_bytes(), frozen_bytes)
            self.assertEqual(rerun["sha256"], first_compass["compass_sha256"])
            pointer = json.loads((root / "LATEST_COMPASS.json").read_text())
            self.assertEqual(pointer["issued_at_utc"], first_compass["issued_at_utc"])

    def test_existing_freeze_repairs_derived_projection_and_pointers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            compass = self.build(tmp, run_reason="ON_DEMAND")
            first = write_official_compass(compass, root)
            frozen_bytes = Path(first["path"]).read_bytes()

            Path(first["public_path"]).unlink()
            (root / "LATEST_COMPASS.json").unlink()
            (root / "PUBLIC_LATEST_COMPASS.json").unlink()

            repaired = write_official_compass(compass, root)

            self.assertEqual(repaired["status"], "EXISTING_DAILY_FREEZE")
            self.assertEqual(Path(first["path"]).read_bytes(), frozen_bytes)
            self.assertTrue(Path(first["public_path"]).exists())
            pointer = json.loads((root / "LATEST_COMPASS.json").read_text())
            public_pointer = json.loads((root / "PUBLIC_LATEST_COMPASS.json").read_text())
            self.assertEqual(pointer["compass_content_sha256"], hashlib.sha256(frozen_bytes).hexdigest())
            self.assertEqual(pointer["public_projection_content_sha256"], public_pointer["public_projection_content_sha256"])

    def test_existing_freeze_integrity_failure_is_blocking(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            compass = self.build(tmp, run_reason="ON_DEMAND")
            first = write_official_compass(compass, root)
            frozen = json.loads(Path(first["path"]).read_text())
            frozen["action_now"] = "PREPARE"
            Path(first["path"]).write_text(json.dumps(frozen))

            with self.assertRaisesRegex(ValueError, "IMMUTABLE_COMPASS_INTEGRITY_FAILED"):
                write_official_compass(compass, root)

    def test_global_route_resolves_official_pointer_first(self):
        route = json.loads(Path("07_PROMPTS_AND_AGENTS/action_compass/GLOBAL_ACTION_COMPASS_ROUTE_v1.json").read_text())
        official = "04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json"
        self.assertEqual(route["status"], "ACTIVE")
        self.assertEqual(route["official_daily_compass_pointer"], official)
        self.assertIn(official, route["authority_route"])


if __name__ == "__main__":
    unittest.main()
