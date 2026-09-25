import json
import hashlib
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.cycle_navigator.build_weekly_cycle_navigator import (
    output_schema as cycle_navigator_output_schema,
    validate_status_reason_codes,
)
from scripts.data_ping.native_handlekompas import (
    CAPITALIZATION_ORDER,
    HORIZON_ORDER,
    OFFICIAL_AUTHORITY,
    build_official_compass,
    build_public_projection,
    load_cn_context,
    protection_tracker,
    write_official_compass,
)


class OfficialDailyCompassTest(unittest.TestCase):
    def auto(self, *, breadth=0.19, validation="PASS", decision="PASS", blockers=None, btc=75654.0, eth=2396.86, ethbtc=0.03168, deltas=None, packet_sha="packet-sha", optional_degraded_lanes=None):
        return {
            "contract": "AUTO_MARKET_STATE_PACKET_v1",
            "packet_generated_at_utc": "2026-09-16T18:09:48Z",
            "packet_sha256": packet_sha,
            "source_snapshot": {"exact_commit_sha": "source-commit"},
            "validation_status": validation,
            "decision_context_status": decision,
            "blockers": blockers or [],
            "optional_degraded_lanes": optional_degraded_lanes or [],
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
            "base_case_4_8_weeks": "Consolidation remains the evidence-bounded long-cycle state.",
            "altseason_countdown": [{"phase": "Broad altseason - PAUSED", "window": "No calendar ETA"}],
            "decision_projection": {
                "contract": "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1",
                "next_1_3d": {"direction": "SIDEWAYS", "summary": "Structured short-horizon consolidation."},
                "next_5_7d": {"direction": "SIDEWAYS", "summary": "Structured weekly consolidation."},
                "weeks_4_8": {
                    "state": "CONSOLIDATION",
                    "warning": "NONE",
                    "direction": "SIDEWAYS",
                    "action_posture": "HOLD",
                    "summary": "Consolidation remains the evidence-bounded long-cycle state.",
                    "through_date": "2026-10-14",
                    "horizon_days": 28,
                    "eta": "through 2026-10-14",
                    "confidence": "MEDIUM",
                },
                "protection": {
                    "pullback_risk_state": "ELEVATED",
                    "pullback_class": "VOLATILE_CONSOLIDATION",
                    "distribution_risk": "NONE",
                    "eta_window": "UNKNOWN",
                    "confidence_quality": "MEDIUM",
                    "drivers": ["Structured Cycle Navigator protection state is elevated."],
                    "invalidation": "Later structured evidence must clear the warning.",
                },
            },
        }

    def build(self, root, *, include_cn=True, issued_at=None, run_reason="SCHEDULED_DAILY", cn_binding_override=None, **kwargs):
        binding = cn_binding_override if cn_binding_override is not None else ({"status": "PASS"} if include_cn else {"status": "UNAVAILABLE"})
        return build_official_compass(
            self.auto(**kwargs),
            packet_path=Path("04_MARKET_LEARNING/entry_signals/auto_market_state/runs/test.json"),
            cn_package=self.cn() if include_cn else None,
            cn_binding=binding,
            repo_root=Path(root),
            issued_at=issued_at or datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc),
            run_reason=run_reason,
        )

    def test_cycle_navigator_machine_projection_contract_is_required(self):
        schema = cycle_navigator_output_schema()
        self.assertIn("decision_projection", schema["required"])
        projection = schema["properties"]["decision_projection"]
        self.assertEqual(
            set(projection["required"]),
            {"contract", "next_1_3d", "next_5_7d", "weeks_4_8", "protection"},
        )
        self.assertEqual(
            projection["properties"]["contract"]["const"],
            "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1",
        )
        self.assertIn("status_reason_codes", schema["required"])
        self.assertFalse(schema["additionalProperties"])
        self.assertIn(
            "MATURING_CONTEXT",
            schema["properties"]["status_reason_codes"]["items"]["enum"],
        )

    def test_cycle_navigator_non_ready_status_requires_machine_reason(self):
        validate_status_reason_codes({"status": "READY", "status_reason_codes": []})
        validate_status_reason_codes({
            "status": "DEGRADED",
            "status_reason_codes": ["MATURING_CONTEXT"],
        })
        with self.assertRaisesRegex(ValueError, "non_ready_status_requires_reason_code"):
            validate_status_reason_codes({"status": "DEGRADED", "status_reason_codes": []})
        with self.assertRaisesRegex(ValueError, "ready_status_reason_codes_must_be_empty"):
            validate_status_reason_codes({
                "status": "READY",
                "status_reason_codes": ["DATA_QUALITY_DEGRADED"],
            })

    def test_deterministic_same_input_same_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = self.build(tmp)
            b = self.build(tmp)
            self.assertEqual(a, b)
            self.assertEqual(a["compass_sha256"], b["compass_sha256"])

    def test_required_horizons_and_ladder_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            self.assertEqual(out["schema_version"], 3)
            self.assertEqual(tuple(out["horizons"].keys()), HORIZON_ORDER)
            self.assertEqual(tuple(row["segment"] for row in out["capitalization_ladder"]), CAPITALIZATION_ORDER)
            self.assertTrue(all("action" in row for row in out["capitalization_ladder"]))
            self.assertEqual(tuple(row["action"] for row in out["capitalization_ladder"]), ("HOLD", "HOLD", "WAIT", "WAIT", "WAIT", "HARD_WAIT", "UNAVAILABLE"))
            memes = out["capitalization_ladder"][-1]
            self.assertEqual(memes["segment"], "MEMES")
            self.assertEqual(memes["status"], "UNAVAILABLE")
            self.assertEqual(memes["direction"], "UNAVAILABLE")
            self.assertIn("MICROCAPS cannot be used as a proxy", memes["reason"])
            self.assertEqual(out["authority"], OFFICIAL_AUTHORITY)
            self.assertFalse(out["authority"]["portfolio_execution"])
            self.assertEqual(out["horizons"]["CYCLE_ALTCOINS_3_8W"]["state"], "CONSOLIDATION")
            self.assertEqual(out["horizons"]["CYCLE_ALTCOINS_3_8W"]["through_date"], "2026-10-14")
            self.assertEqual(out["horizons"]["CYCLE_ALTCOINS_3_8W"]["warning"], "NONE")

    def test_long_cycle_buy_cannot_exceed_main_framework_permission(self):
        with tempfile.TemporaryDirectory() as tmp:
            cn = self.cn()
            cn["decision_projection"]["weeks_4_8"]["state"] = "ROTATION"
            cn["decision_projection"]["weeks_4_8"]["direction"] = "UP"
            cn["decision_projection"]["weeks_4_8"]["action_posture"] = "BUY"
            out = build_official_compass(
                self.auto(),
                packet_path=Path("04_MARKET_LEARNING/entry_signals/auto_market_state/runs/test.json"),
                cn_package=cn,
                cn_binding={"status": "PASS"},
                repo_root=Path(tmp),
                issued_at=datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc),
                run_reason="ON_DEMAND",
            )
            lane = out["horizons"]["CYCLE_ALTCOINS_3_8W"]
            self.assertEqual(out["action_now"], "HOLD_WAIT")
            self.assertEqual(lane["action_posture"], "WAIT")
            public = build_public_projection(out)
            self.assertEqual(
                public["horizons"]["CYCLE_ALTCOINS_3_8W"]["action_posture"],
                "WAIT",
            )

    def test_sell_is_separate_and_fail_closed_without_governed_owner(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            sell = out["sell_assessment"]
            self.assertEqual(sell["contract"], "COMPASS_SELL_ASSESSMENT_v1")
            self.assertEqual(sell["state"], "UNAVAILABLE")
            self.assertEqual(sell["horizon"], "UNKNOWN")
            self.assertFalse(sell["authority"]["portfolio_execution"])
            self.assertFalse(sell["authority"]["new_sell_rule"])
            self.assertFalse(sell["authority"]["protection_is_sell_authority"])
            self.assertIn("not sell instructions", sell["reason"])

            public = build_public_projection(out)
            self.assertEqual(public["sell_assessment"], sell)

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
            self.assertTrue(all(row["action"] == "UNAVAILABLE" for row in out["capitalization_ladder"]))
            self.assertTrue(all(out["horizons"][key]["expected_direction"] == "UNAVAILABLE" for key in HORIZON_ORDER))

    def test_optional_degradation_remains_decision_eligible(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(
                tmp,
                validation="DEGRADED",
                decision="PASS",
                optional_degraded_lanes=["catalyst_context"],
            )
            self.assertEqual(out["data_status"], "OK")
            self.assertNotEqual(out["market_now"]["directional_state"], "UNAVAILABLE")
            self.assertNotEqual(out["horizons"]["NEXT_12H"]["expected_direction"], "UNAVAILABLE")

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
            self.assertEqual(out["market_now"]["regime"], "HOLD_WAIT")
            self.assertEqual(out["market_now"]["directional_state"], "MIXED")

    def test_weekly_pullback_risk_projects_conservatively(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(
                tmp,
                breadth=0.60,
                deltas={
                    "btc_usdt": {"pct": 0.5},
                    "eth_usdt": {"pct": 1.0},
                    "ethbtc": {"pct": 0.6},
                },
            )
            tracker = out["protection_tracker"]
            self.assertEqual(tracker["contract"], "COMPASS_PROTECTION_TRACKER_v1")
            self.assertEqual(tracker["pullback_risk_state"], "ELEVATED")
            self.assertEqual(tracker["pullback_class"], "VOLATILE_CONSOLIDATION")
            self.assertEqual(tracker["distribution_risk"], "NONE")
            self.assertEqual(tracker["eta_window"], "UNKNOWN")
            self.assertEqual(tracker["reentry_state"], "INACTIVE")
            self.assertFalse(tracker["authority"]["portfolio_execution"])
            self.assertFalse(tracker["authority"]["wallet_specific"])

    def test_distribution_cycle_state_escalates_without_wallet_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            cn = {
                "issue_number": 26,
                "market_state": "Distribution regime.",
                "base_case_this_week": "Distribution is active.",
                "base_case_2_3_weeks": "Risk remains defensive.",
                "base_case_4_8_weeks": "Distribution remains active.",
                "decision_projection": {
                    "contract": "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1",
                    "next_1_3d": {"direction": "DOWN", "summary": "Risk is defensive."},
                    "next_5_7d": {"direction": "DOWN", "summary": "Distribution remains active."},
                    "weeks_4_8": {
                        "state": "DISTRIBUTION",
                        "warning": "DISTRIBUTION_WARNING",
                        "direction": "DOWN",
                        "action_posture": "HOLD",
                        "summary": "Distribution is active.",
                        "through_date": "2026-10-14",
                        "horizon_days": 28,
                        "eta": "through 2026-10-14",
                        "confidence": "HIGH",
                    },
                    "protection": {
                        "pullback_risk_state": "HIGH",
                        "pullback_class": "DISTRIBUTION",
                        "distribution_risk": "CONFIRMED",
                        "eta_window": "UNKNOWN",
                        "confidence_quality": "HIGH",
                        "drivers": ["Structured Cycle Navigator distribution state is confirmed."],
                        "invalidation": "A later structured state must explicitly clear distribution.",
                    },
                },
            }
            out = build_official_compass(
                self.auto(),
                packet_path=Path("04_MARKET_LEARNING/entry_signals/auto_market_state/runs/test.json"),
                cn_package=cn,
                cn_binding={"status": "PASS"},
                repo_root=Path(tmp),
                issued_at=datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc),
                run_reason="ON_DEMAND",
            )
            tracker = out["protection_tracker"]
            self.assertEqual(tracker["pullback_risk_state"], "HIGH")
            self.assertEqual(tracker["pullback_class"], "DISTRIBUTION")
            self.assertEqual(tracker["distribution_risk"], "CONFIRMED")
            self.assertEqual(tracker["confidence_quality"], "HIGH")
            self.assertEqual(tracker["reentry_state"], "WAIT_FOR_FLUSH")

    def test_reentry_review_requires_prior_reclaim_state_and_constructive_compass(self):
        now = datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc)
        auto = self.auto(
            breadth=0.60,
            deltas={
                "btc_usdt": {"pct": 0.5},
                "eth_usdt": {"pct": 1.0},
                "ethbtc": {"pct": 0.6},
            },
        )
        cn = {
            "issue_number": 26,
            "market_state": "Constructive transition.",
            "base_case_this_week": "Constructive transition without an active pullback warning.",
            "base_case_2_3_weeks": "Selective leadership may broaden.",
            "decision_projection": {
                "contract": "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1",
                "next_1_3d": {"direction": "UP", "summary": "Constructive transition."},
                "next_5_7d": {"direction": "UP", "summary": "Selective leadership may broaden."},
                "weeks_4_8": {
                    "state": "PRE_ROTATION",
                    "warning": "NONE",
                    "direction": "UP",
                    "action_posture": "HOLD",
                    "summary": "Pre-rotation remains under review.",
                    "through_date": None,
                    "horizon_days": None,
                    "eta": "UNKNOWN",
                    "confidence": "LOW",
                },
                "protection": {
                    "pullback_risk_state": "NORMAL",
                    "pullback_class": "UNKNOWN",
                    "distribution_risk": "NONE",
                    "eta_window": "UNKNOWN",
                    "confidence_quality": "MEDIUM",
                    "drivers": ["Structured protection state is normal."],
                    "invalidation": "A later structured warning would invalidate the normal state.",
                },
            },
        }
        action = {"NOW": "PREPARE"}
        market = {"directional_state": "BULLISH", "regime": "PREPARE"}
        prior = {
            "protection_tracker": {
                "pullback_risk_state": "NORMAL",
                "pullback_class": "UNKNOWN",
                "distribution_risk": "NONE",
                "eta_window": "UNKNOWN",
                "confidence_quality": "MEDIUM",
                "reentry_state": "WAIT_FOR_RECLAIM",
                "last_material_change_at": "2026-09-16T18:00:00Z",
            }
        }
        tracker = protection_tracker(
            auto, action, market, cn, as_of=now, prior_compass=prior
        )
        self.assertEqual(tracker["pullback_risk_state"], "NORMAL")
        self.assertEqual(tracker["reentry_state"], "REVIEW")
        self.assertIn("not an automatic buy", tracker["reentry_message"])

    def test_prose_only_cycle_navigator_cannot_drive_machine_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            prose_only = {
                "issue_number": 26,
                "market_state": "Distribution and pullback risk confirmed with broad expansion.",
                "base_case_this_week": "Not a breakdown, but distribution risk is high.",
                "base_case_2_3_weeks": "Broad altseason rotation.",
                "base_case_4_8_weeks": "Exit risk.",
                "altseason_countdown": [{"phase": "Broad altseason", "window": "soon"}],
            }
            out = build_official_compass(
                self.auto(),
                packet_path=Path("04_MARKET_LEARNING/entry_signals/auto_market_state/runs/test.json"),
                cn_package=prose_only,
                cn_binding={"status": "PASS"},
                repo_root=Path(tmp),
                issued_at=datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc),
                run_reason="ON_DEMAND",
            )
            self.assertEqual(out["horizons"]["NEXT_1_3D"]["expected_direction"], "NO_EDGE")
            self.assertEqual(out["horizons"]["NEXT_5_7D"]["expected_direction"], "NO_EDGE")
            self.assertEqual(out["horizons"]["CYCLE_ALTCOINS_3_8W"]["expected_direction"], "UNAVAILABLE")
            self.assertEqual(out["protection_tracker"]["pullback_risk_state"], "UNAVAILABLE")
            self.assertEqual(out["protection_tracker"]["distribution_risk"], "UNKNOWN")

    def test_evidence_snapshot_carries_persistence_baseline_features(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            values = {row["feature_id"]: row["value"] for row in out["evidence_snapshot"]["selected_features"]}
            self.assertAlmostEqual(values["btc_delta_since_prior_packet_pct"], -0.3)
            self.assertAlmostEqual(values["eth_delta_since_prior_packet_pct"], -0.7)
            self.assertAlmostEqual(values["ethbtc_delta_since_prior_packet_pct"], -0.4)

    def test_legacy_cn_projection_addendum_is_hash_bound_and_non_rewriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            week_dir = root / "05_CYCLE_NAVIGATOR/weekly/2026/W39"
            week_dir.mkdir(parents=True)
            package = {"issue_number": 27, "market_state": "legacy narrative only"}
            package_path = week_dir / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
            package_path.write_text(json.dumps(package, sort_keys=True) + "\n")
            package_sha = hashlib.sha256(package_path.read_bytes()).hexdigest()
            pointer_path = root / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json"
            pointer_path.parent.mkdir(parents=True, exist_ok=True)
            pointer_path.write_text(json.dumps({
                "issue_number": 27,
                "iso_week": 39,
                "iso_year": 2026,
                "week_dir": "05_CYCLE_NAVIGATOR/weekly/2026/W39",
            }))
            projection = {
                "contract": "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1",
                "next_1_3d": {"direction": "NO_EDGE", "summary": "Compatibility only."},
                "next_5_7d": {"direction": "NO_EDGE", "summary": "Compatibility only."},
                "weeks_4_8": {
                    "state": "UNCLEAR", "warning": "NONE", "direction": "UNAVAILABLE",
                    "action_posture": "UNAVAILABLE", "summary": "Compatibility only.",
                    "through_date": None, "horizon_days": None, "eta": "UNKNOWN", "confidence": "LOW",
                },
                "protection": {
                    "pullback_risk_state": "UNAVAILABLE", "pullback_class": "UNKNOWN",
                    "distribution_risk": "UNKNOWN", "eta_window": "UNKNOWN",
                    "confidence_quality": "LOW", "drivers": [],
                    "invalidation": "Prospective structured evidence required.",
                },
            }
            addendum_path = week_dir / "DECISION_PROJECTION_ADDENDUM_v1.json"
            addendum_path.write_text(json.dumps({
                "contract": "CYCLE_NAVIGATOR_DECISION_PROJECTION_ADDENDUM_v1",
                "base_machine_package_sha256": package_sha,
                "forecast_rewrite": False,
                "portfolio_execution": False,
                "decision_projection": projection,
            }))

            loaded, binding = load_cn_context(
                root, Path("05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
            )
            self.assertEqual(loaded["decision_projection"], projection)
            self.assertEqual(binding["decision_projection_source"], "HASH_BOUND_COMPATIBILITY_ADDENDUM")
            self.assertNotIn("decision_projection", json.loads(package_path.read_text()))

            bad = json.loads(addendum_path.read_text())
            bad["base_machine_package_sha256"] = "0" * 64
            addendum_path.write_text(json.dumps(bad))
            loaded_bad, binding_bad = load_cn_context(
                root, Path("05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
            )
            self.assertNotIn("decision_projection", loaded_bad)
            self.assertEqual(binding_bad["decision_projection_source"], "INVALID_COMPATIBILITY_ADDENDUM_IGNORED")

    def test_public_projection_does_not_leak_internal_bindings_or_threshold_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = self.build(tmp)
            public = build_public_projection(out)
            self.assertNotIn("source_bindings", public)
            self.assertNotIn("evidence_snapshot", public)
            self.assertNotIn("native_action_contract", public)
            self.assertEqual(public["protection_tracker"]["contract"], "COMPASS_PROTECTION_TRACKER_v1")
            self.assertTrue(all("action" in row for row in public["capitalization_ladder"]))
            self.assertFalse(public["protection_tracker"]["authority"]["wallet_specific"])
            self.assertFalse(any(key in public["protection_tracker"] for key in ("wallet_address", "holdings", "positions", "portfolio_actions")))
            self.assertNotRegex(json.dumps(public["protection_tracker"]), r"0x[a-fA-F0-9]{8,}")
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

    def test_on_demand_reuses_latest_when_owner_packet_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            scheduled = self.build(
                tmp,
                run_reason="SCHEDULED_MORNING",
                issued_at=datetime(2026, 9, 16, 6, 17, tzinfo=timezone.utc),
                packet_sha="same-owner-packet",
            )
            requested = self.build(
                tmp,
                run_reason="ON_DEMAND",
                issued_at=datetime(2026, 9, 16, 7, 5, tzinfo=timezone.utc),
                packet_sha="same-owner-packet",
            )
            first = write_official_compass(scheduled, root)
            second = write_official_compass(requested, root)

            self.assertEqual(first["status"], "WRITTEN")
            self.assertEqual(second["status"], "EXISTING_DAILY_FREEZE")
            self.assertEqual(second["compass_id"], first["compass_id"])
            self.assertEqual(second["path"], first["path"])

    def test_on_demand_writes_when_cycle_navigator_context_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            first_compass = self.build(
                tmp,
                run_reason="ON_DEMAND",
                issued_at=datetime(2026, 9, 16, 7, 5, tzinfo=timezone.utc),
                packet_sha="same-owner-packet",
                cn_binding_override={
                    "status": "PASS",
                    "issue_number": 26,
                    "machine_package": {"content_sha256": "cn-a"},
                    "decision_projection_source": "MACHINE_PACKAGE",
                },
            )
            second_compass = self.build(
                tmp,
                run_reason="ON_DEMAND",
                issued_at=datetime(2026, 9, 16, 7, 6, tzinfo=timezone.utc),
                packet_sha="same-owner-packet",
                cn_binding_override={
                    "status": "PASS",
                    "issue_number": 27,
                    "machine_package": {"content_sha256": "cn-b"},
                    "decision_projection_source": "MACHINE_PACKAGE",
                },
            )
            self.assertNotEqual(first_compass["decision_context_fingerprint"], second_compass["decision_context_fingerprint"])
            self.assertNotEqual(first_compass["compass_id"], second_compass["compass_id"])

            first = write_official_compass(first_compass, root)
            second = write_official_compass(second_compass, root)

            self.assertEqual(first["status"], "WRITTEN")
            self.assertEqual(second["status"], "WRITTEN")
            self.assertNotEqual(first["path"], second["path"])
            pointer = json.loads((root / "LATEST_COMPASS.json").read_text())
            self.assertEqual(pointer["decision_context_fingerprint"], second_compass["decision_context_fingerprint"])

    def test_on_demand_writes_when_owner_packet_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            scheduled = self.build(
                tmp,
                run_reason="SCHEDULED_MORNING",
                issued_at=datetime(2026, 9, 16, 6, 17, tzinfo=timezone.utc),
                packet_sha="owner-packet-a",
            )
            requested = self.build(
                tmp,
                run_reason="ON_DEMAND",
                issued_at=datetime(2026, 9, 16, 7, 5, tzinfo=timezone.utc),
                packet_sha="owner-packet-b",
            )
            first = write_official_compass(scheduled, root)
            second = write_official_compass(requested, root)

            self.assertEqual(first["status"], "WRITTEN")
            self.assertEqual(second["status"], "WRITTEN")
            self.assertNotEqual(second["compass_id"], first["compass_id"])
            pointer = json.loads((root / "LATEST_COMPASS.json").read_text())
            self.assertEqual(pointer["source_packet_sha256"], "owner-packet-b")

    def test_policy_migration_same_source_creates_new_immutable_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            current = self.build(
                tmp,
                run_reason="ON_DEMAND",
                issued_at=datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc),
                packet_sha="same-owner-packet",
            )
            legacy = json.loads(json.dumps(current))
            legacy["decision_policy_version"] = "LEGACY_POLICY"
            legacy_identity = (
                "same-owner-packet|2026-09-16|ON_DEMAND|"
                "schema=2|policy=LEGACY_POLICY"
            )
            legacy["compass_id"] = "CMP-20260916-" + hashlib.sha256(legacy_identity.encode()).hexdigest()[:12]
            legacy_payload = {k: v for k, v in legacy.items() if k != "compass_sha256"}
            legacy["compass_sha256"] = hashlib.sha256(
                (json.dumps(legacy_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()
            ).hexdigest()

            first = write_official_compass(legacy, root)
            second = write_official_compass(current, root)

            self.assertEqual(first["status"], "WRITTEN")
            self.assertEqual(second["status"], "WRITTEN")
            self.assertNotEqual(first["compass_id"], second["compass_id"])
            self.assertNotEqual(first["path"], second["path"])
            self.assertTrue(Path(first["public_path"]).exists())
            self.assertTrue(Path(second["public_path"]).exists())

    def test_schema_migration_same_source_creates_new_immutable_freeze(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "official"
            current = self.build(
                tmp,
                run_reason="ON_DEMAND",
                issued_at=datetime(2026, 9, 16, 20, 17, tzinfo=timezone.utc),
                packet_sha="same-owner-packet",
            )
            legacy = json.loads(json.dumps(current))
            legacy["schema_version"] = 1
            legacy.pop("protection_tracker", None)
            legacy_identity = "same-owner-packet|2026-09-16|ON_DEMAND"
            legacy["compass_id"] = "CMP-20260916-" + hashlib.sha256(legacy_identity.encode()).hexdigest()[:12]
            legacy_payload = {k: v for k, v in legacy.items() if k != "compass_sha256"}
            legacy["compass_sha256"] = hashlib.sha256(
                (json.dumps(legacy_payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()
            ).hexdigest()

            first = write_official_compass(legacy, root)
            second = write_official_compass(current, root)

            self.assertEqual(first["status"], "WRITTEN")
            self.assertEqual(second["status"], "WRITTEN")
            self.assertNotEqual(first["compass_id"], second["compass_id"])
            self.assertNotEqual(first["path"], second["path"])
            pointer = json.loads((root / "LATEST_COMPASS.json").read_text())
            self.assertEqual(pointer["compass_id"], current["compass_id"])
            published = json.loads(Path(second["public_path"]).read_text())
            self.assertEqual(published["protection_tracker"]["contract"], "COMPASS_PROTECTION_TRACKER_v1")

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
        refresh = route["official_compass_policy"]["on_demand_refresh"]
        self.assertTrue(refresh["enabled"])
        self.assertEqual(refresh["run_reason"], "ON_DEMAND")
        self.assertEqual(refresh["same_source_behavior"], "REUSE_EXISTING_IMMUTABLE_FREEZE")
        self.assertFalse(route["official_compass_policy"]["render_request_creates_new_freeze"])


if __name__ == "__main__":
    unittest.main()
