"""Adversarial static and source-only tests for owner-approved Kompas PRO v2.

Synthetic inputs here are NOT market forecasts or provider-first-known proof.
"""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.learning.kompas_pro_horizon_readback_v2 import (
    HORIZON_IDS, build_visible_horizon_rows, validate_route_and_ledger,
)

ROOT = Path(__file__).resolve().parents[2]
ROUTE = ROOT / "07_PROMPTS_AND_AGENTS/action_compass/GLOBAL_ACTION_COMPASS_ROUTE_v1.json"
LEDGER = ROOT / "07_PROMPTS_AND_AGENTS/action_compass/KOMPAS_PRO_HORIZON_IMPLEMENTATION_LEDGER_v2.json"
CONTRACT = ROOT / "07_PROMPTS_AND_AGENTS/action_compass/2026-11-02__kompas-pro-internal-output-and-forward-horizon-v2__owner-approved.md"


def get():
    return json.loads(ROUTE.read_text()), json.loads(LEDGER.read_text())


def issued():
    return {
        "status": "ISSUED_NUMERIC",
        "price_owner": "CN_ORIGINAL_WEEKLY_1593",
        "model_authority": "ORIGINAL_CN_FORECAST",
        "public_issuance_verified": True,
        "original_issue_id": "TEST-SYNTHETIC-ONLY",
        "original_source_sha256": "a" * 64,
        "source_first_known_at_utc": "2026-11-02T07:00:00Z",
        "issued_at_utc": "2026-11-02T09:05:00Z",
        "forecast_start_utc": "2026-11-02T09:06:00Z",
        "forecast_end_utc": "2026-11-09T00:00:00Z",
        "price_quote": "USD",
        "price_venue": "SOURCE_OWNED_CN_WEEKLY",
        "price_semantics": "daily_expected_close",
        "low": 77000.0,
        "expected_close": 80000.0,
        "high": 84000.0,
        "direction": "MIXED",
    }


class KompasProContractTests(unittest.TestCase):
    def setUp(self):
        self.route, self.ledger = get()

    def test_versioned_contract_is_bound_to_real_global_hard_trigger(self):
        validate_route_and_ledger(self.route, self.ledger)
        self.assertTrue(CONTRACT.is_file())
        doc = CONTRACT.read_text()
        self.assertIn("Internal Kompas", doc)
        self.assertIn("21–30D", doc)
        self.assertIn("ONE BTC graph", doc)
        self.assertIn("No synthetic numeric forecast", doc)
        self.assertTrue(self.route["output"]["kompas_pro_presentational_contract"]["deep_internal_analysis_required_before_visible_answer"])

    def test_exact_fourteen_horizons_not_an_abbreviated_four_horizon_read(self):
        self.assertEqual([r["id"] for r in self.ledger["horizons"]], list(HORIZON_IDS))
        self.assertEqual(len(self.ledger["horizons"]), 14)
        self.assertEqual(len(self.ledger["full_internal_required_families"]), 16)

    def test_safely_read_no_original_forecast_is_grey_not_zero_or_50_percent(self):
        rows = build_visible_horizon_rows(self.ledger, {})
        self.assertEqual(len(rows), 14)
        self.assertEqual({r["status"] for r in rows}, {"NOT_ISSUED"})
        self.assertEqual({r["color"] for r in rows}, {"GREY"})
        self.assertTrue(all(r["price_expected_close"] is None for r in rows))

    def test_real_observation_is_not_an_expected_future_close(self):
        x = {"status": "OBSERVED", "observed_price": 78000.0, "observed_at_utc": "2026-11-02T09:00:00Z", "price_quote": "USDT", "asset": "BTC", "price_venue": "BINANCE_SPOT_BTCUSDT"}
        rows = build_visible_horizon_rows(self.ledger, {"NOW": x}, as_of_utc="2026-11-02T09:30:00Z")
        self.assertEqual(rows[0]["observed_price"], 78000)
        self.assertIsNone(rows[0]["price_expected_close"])
        with self.assertRaisesRegex(ValueError, "OBSERVED_AS_FORECAST"):
            build_visible_horizon_rows(self.ledger, {"H0_12H": x})

    def test_grok_strategic_direction_cannot_become_official(self):
        with self.assertRaises(ValueError):
            build_visible_horizon_rows(self.ledger, {"H21_30D": {
                "status": "OFFICIAL_DIRECTION",
                "direction_owner": "STRATEGIC_COMPASS_CN_PROJECTION",
                "direction": "UP",
            }})
        ledger = deepcopy(self.ledger)
        ledger["horizons"][5]["direction_owner"] = "OFFICIAL_DAILY_COMPASS"
        with self.assertRaisesRegex(ValueError, "RESEARCH_DIRECTION_CANNOT_BE_OFFICIAL"):
            build_visible_horizon_rows(ledger, {"H8_14D": {
                "status": "OFFICIAL_DIRECTION",
                "direction_owner": "OFFICIAL_DAILY_COMPASS",
                "direction": "DOWN",
            }})
        self.assertEqual(build_visible_horizon_rows(self.ledger, {"H1_3D": {
            "status": "OFFICIAL_DIRECTION",
            "direction_owner": "OFFICIAL_DAILY_COMPASS",
            "direction": "UP",
        }})[3]["color"], "GREEN")

    def test_grok_observed_btc_source_and_freshness(self):
        valid = {"status": "OBSERVED", "observed_price": 78000.0,
                 "observed_at_utc": "2026-11-02T09:00:00Z",
                 "price_quote": "USDT", "asset": "BTC",
                 "price_venue": "BINANCE_SPOT_BTCUSDT"}
        self.assertEqual(build_visible_horizon_rows(
            self.ledger, {"NOW": valid}, as_of_utc="2026-11-02T10:59:59Z"
        )[0]["observed_price"], 78000.0)
        for change, clock in [
            ({"asset": "ETH"}, "2026-11-02T09:30:00Z"),
            ({"price_venue": "UNKNOWN"}, "2026-11-02T09:30:00Z"),
            ({}, "2026-11-02T11:00:01Z"),
            ({}, "2026-11-02T08:59:59Z"),
            ({}, None),
        ]:
            with self.subTest(change=change, clock=clock), self.assertRaises(ValueError):
                row = dict(valid)
                row.update(change)
                build_visible_horizon_rows(self.ledger, {"NOW": row}, as_of_utc=clock)

    def test_grok_all_required_guards_and_sixteen_families(self):
        for field in ("require_target_start_end_utc", "require_original_source_hash"):
            ledger = deepcopy(self.ledger)
            ledger["horizons"][0][field] = False
            with self.assertRaises(ValueError):
                validate_route_and_ledger(self.route, ledger)
        ledger = deepcopy(self.ledger)
        ledger["full_internal_required_families"] = ledger["full_internal_required_families"][:14]
        with self.assertRaisesRegex(ValueError, "INTERNAL_SOURCE_AUDIT_TOO_SHALLOW"):
            validate_route_and_ledger(self.route, ledger)

    def test_official_mixed_direction_retains_label_but_never_mints_price(self):
        rows = build_visible_horizon_rows(self.ledger, {
            "H1_3D": {"status": "OFFICIAL_DIRECTION", "direction_owner": "OFFICIAL_DAILY_COMPASS",
                      "direction": "MIXED"},
        })
        item = rows[3]
        self.assertEqual((item["direction"], item["color"], item["price_status"]), ("MIXED", "AMBER", "NOT_ISSUED"))

    def test_structurally_eligible_numeric_is_not_publicly_source_verified(self):
        # A caller-supplied plausible SHA/verified flag is NOT original-source proof.
        row = build_visible_horizon_rows(self.ledger, {"H5_7D": issued()})[4]
        self.assertIsNone(row["price_expected_close"])
        self.assertIsNone(row["price_low"])
        self.assertIsNone(row["price_high"])
        self.assertIsNone(row["quote"])
        self.assertEqual(row["price_status"], "ORIGINAL_BINDING_REQUIRED")
        self.assertEqual(row["status"], "ORIGINAL_BINDING_REQUIRED")
        self.assertEqual(row["color"], "GREY")
        self.assertIsNone(build_visible_horizon_rows(self.ledger, {"H8_14D": {"status": "RESEARCH_ONLY"}})[5]["price_low"])

    def test_unissued_or_research_numeric_leak_is_rejected(self):
        for status in ("RESEARCH_ONLY", "NOT_ISSUED"):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "PRICE_LEAK"):
                build_visible_horizon_rows(self.ledger, {"H21_30D": {"status": status, "expected_close": 99000}})
        with self.assertRaisesRegex(ValueError, "PRICE"):
            build_visible_horizon_rows(self.ledger, {"H1_3D": {"status": "OFFICIAL_DIRECTION",
                "direction_owner": "OFFICIAL_DAILY_COMPASS", "direction": "UP", "low": 90000}})

    def test_unsupported_old_or_future_issuance_is_rejected(self):
        for change in [
            {"issued_at_utc": "2026-11-02T09:10:00Z"},
            {"source_first_known_at_utc": "2026-11-02T09:07:00Z"},
            {"forecast_end_utc": "2026-11-02T08:00:00Z"},
            {"original_source_sha256": "invalid"},
            {"public_issuance_verified": False},
            {"model_authority": "SHADOW_MODEL"},
            {"original_issue_id": ""},
            {"price_owner": "FORWARD_PATH_1516"},
        ]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                row = issued()
                row.update(change)
                build_visible_horizon_rows(self.ledger, {"H5_7D": row})

    def test_wrong_venue_and_mixed_quote_not_promoted(self):
        row = issued()
        row["price_quote"] = "USDT"
        with self.assertRaisesRegex(ValueError, "PROVENANCE"):
            build_visible_horizon_rows(self.ledger, {"H5_7D": row})
        row["price_venue"] = "BINANCE_SPOT_BTCUSDT"
        protected = build_visible_horizon_rows(self.ledger, {"H5_7D": row})[4]
        self.assertIsNone(protected["quote"])
        self.assertIsNone(protected["price_expected_close"])
        self.assertEqual(protected["status"], "ORIGINAL_BINDING_REQUIRED")

    def test_fictitious_price_bounds_or_nonfinite_rejected(self):
        for change in [
            {"low": 85000}, {"high": 79000}, {"expected_close": 99000},
            {"expected_close": float("nan")}, {"low": True}, {"low": -1},
        ]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                row = issued()
                row.update(change)
                build_visible_horizon_rows(self.ledger, {"H5_7D": row})

    def test_authority_and_scope_guards_are_not_cosmetic(self):
        for field, bad in [
            ("require_quote_parity", False),
            ("require_original_issue", False),
            ("numeric_publication_default", "PUBLISHED"),
            ("action_owner", "SHADOW"),
        ]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                ledger = deepcopy(self.ledger)
                ledger["horizons"][6][field] = bad
                validate_route_and_ledger(self.route, ledger)
        route = deepcopy(self.route)
        route["output"]["prompt_presentation_routing"]["kompas"] = "LEGACY_SHORT"
        with self.assertRaises(ValueError):
            validate_route_and_ledger(route, self.ledger)

    def test_graph_source_independence_and_release_safety_cannot_be_removed(self):
        led = deepcopy(self.ledger)
        led["graph_history"]["green_actual_independent_of_blue"] = False
        with self.assertRaisesRegex(ValueError, "GRAPH_SOURCE"):
            validate_route_and_ledger(self.route, led)
        led = deepcopy(self.ledger)
        led["release_gates"]["high_impact_requires_separate_vault_restore"] = False
        with self.assertRaisesRegex(ValueError, "RELEASE_SAFETY"):
            validate_route_and_ledger(self.route, led)

    def test_release_readback_reconciles_source_merges_without_inventing_w45_original_prices(self):
        phases = {row["id"]: row for row in self.ledger["release_phases"]}
        meta = self.ledger["release_phase_status_readback"]
        self.assertEqual(meta["contract"], "KOMPAS_PRO_RELEASE_PARTIAL_SOURCE_EVIDENCE_v1")
        for field in ("no_product_completion_claim", "no_shadow_promotion",
                      "no_original_week45_mutation", "no_portfolio_action_authority"):
            self.assertIs(meta[field], True)
        self.assertEqual(phases["G0"]["state"], "IN_PROGRESS")
        self.assertEqual(phases["G0"]["code_delivery"]["state"], "MERGED_MAIN_VERIFIED")
        self.assertIn("LITERAL_KOMPAS_CURRENT_SOURCE_OUTPUT_READBACK",
                      phases["G0"]["code_delivery"]["remaining_before_verified_complete"])
        self.assertEqual(phases["G1"]["state"], "NATURAL_WAIT")
        self.assertEqual(phases["G1"]["code_delivery"]["state"],
                         "SOURCE_AND_SITE_PIPELINES_MERGED_VERIFIED")
        self.assertEqual({x["pr"] for x in phases["G1"]["code_delivery"]["implemented"]},
                         {1879, 1872, 1901, 1902})
        delivery = phases["G1"]["actual_product_delivery"]
        self.assertEqual(delivery["forecast_week"], "2026-W45")
        self.assertEqual(delivery["original_frozen_daily_expected_close_counts"], {"BTC": 0, "ETH": 0})
        self.assertEqual(delivery["original_frozen_daily_range_plan_counts"], {"BTC": 0, "ETH": 0})
        self.assertEqual(delivery["original_frozen_7d_blue_status"], "UNAVAILABLE")
        self.assertEqual(delivery["unverified_weekly_quote_for_W45"], "UNAVAILABLE")
        self.assertIs(delivery["prospectively_issued_7d_product"], False)
        self.assertIs(delivery["shadow_research_can_substitute"], False)
        self.assertEqual(delivery["next_natural_target_forecast_week"], "2026-W46")
        self.assertEqual(delivery["next_natural_utc_monday"], "2026-11-09")
        self.assertEqual(delivery["required_daily_expected_closes_each_asset"], 7)
        self.assertEqual(delivery["required_reasoned_daily_range_plan_each_asset"], 7)
        self.assertNotEqual(phases["G1"]["state"], "VERIFIED_COMPLETE")
        frozen = json.loads((ROOT /
            "05_CYCLE_NAVIGATOR/weekly/2026/W45/CYCLE_NAVIGATOR_FORECAST_FREEZE.json").read_text())
        for asset in ("BTC", "ETH"):
            self.assertEqual(frozen["daily_price_path"][asset]["status"], "UNAVAILABLE")
            self.assertEqual(frozen["daily_price_path"][asset]["points"], [])
            self.assertEqual(frozen["daily_range_plan"][asset]["status"], "UNAVAILABLE")
        validate_route_and_ledger(self.route, self.ledger)

    def test_graph_history_is_partial_g4_not_full_horizon_promotion(self):
        phases = {row["id"]: row for row in self.ledger["release_phases"]}
        g4 = phases["G4"]
        self.assertEqual(g4["state"], "IN_PROGRESS")
        self.assertEqual(g4["code_delivery"]["state"],
                         "SOURCE_BOUND_GRAPH_HISTORY_AND_MOBILE_RUNTIME_AVAILABLE_NOT_FULL_14_HORIZON_RELEASE")
        self.assertEqual({p["pr"] for p in g4["code_delivery"]["verified"]}, {1872, 1905, 1909})
        self.assertIs(g4["code_delivery"]["research_expected_close_7_of_7_promoted"], False)
        self.assertIs(g4["code_delivery"]["physical_iphone_safari_visual_review_verified"], False)
        self.assertIs(g4["code_delivery"]["full_14_horizon_source_grade_public_renderer_verified"], False)
        self.assertEqual(g4["code_delivery"]["canonical_w45_7d_blue_status"], "UNAVAILABLE")
        self.assertTrue((ROOT / "05_CYCLE_NAVIGATOR/site/research-w45/index.html").is_file())
        self.assertTrue((ROOT / "05_CYCLE_NAVIGATOR/site/research-w45/preview.test.mjs").is_file())
        self.assertNotEqual(g4["state"], "VERIFIED_COMPLETE")

    def test_site_cannot_issue_price_and_long_range_is_not_marked_complete(self):
        self.assertTrue(self.ledger["public_projection"]["site_cannot_issue_forecast"])
        phases = self.ledger["release_phases"]
        self.assertEqual([x["id"] for x in phases], [f"G{i}" for i in range(7)])
        self.assertTrue(all(x["state"] != "VERIFIED_COMPLETE" for x in phases))
        self.assertTrue(all(x["completion_evidence"] for x in phases))
        self.assertTrue(all(x["restart_trigger"] for x in phases))
        self.assertEqual(self.ledger["graph_history"]["start_week"], "2026-W45")


if __name__ == "__main__":
    unittest.main()
