from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backtest_engine.blind_dual_run import (
    FULL_PROFILE,
    REDUCED_PROFILE,
    REDUCED_SENSOR_IDS,
    collect_from_latest_capture,
    coverage_progress,
    fixed_window_id,
    load_pair_receipts,
)

FULL_ONLY = (
    "ETHBTC_DERIVED","ETH_DOMINANCE","BREADTH_ABOVE_MA50","ETF_FLOW_DIVERGENCE",
    "FUTURES_BASIS","FUTURES_TAKER_RATIO","CFGI","TDBC","YIELD_CURVE","VIX",
    "DOLLAR_INDEX","STABLECOIN_SUPPLY","CHAIN_TVL","DEX_VOLUME",
)
FULL_SENSORS = REDUCED_SENSOR_IDS + FULL_ONLY


def registry():
    rows = [[s, "X", "X", "X", "CORE", "OWNER", "FAIL_CLOSED"] for s in FULL_SENSORS]
    return {
        "schema_version":"SENSOR_ROLE_DEPENDENCY_REGISTRY_v1",
        "rows": rows,
        "stack_profiles":{
            FULL_PROFILE:"all non-retired sensors",
            REDUCED_PROFILE:list(REDUCED_SENSOR_IDS),
        },
    }


def policy_registry():
    return {
        "schema_version":"POLICY_FAMILY_REGISTRY_v1",
        "families":{
            "ROTATION_PERMISSION":{"decision_values":["NO_ROTATION","ETH_RELATIVE_STRENGTH","SELECTIVE_LARGE_CAP","BROAD_ALT"]},
            "REBUY_LOCK":{"decision_values":["LOCKED","WATCH_ONLY","PERMITTED"]},
            "TRIM_NO_TRIM":{"decision_values":["NO_TRIM","PARTIAL_TRIM","FULL_TRIM"]},
        },
    }


def capture(ts="2026-08-09T09:22:03Z"):
    return {
        "contract":"DAILY_LIVE_ANCHOR_INDEX_v3",
        "status":"COMPLETE",
        "authority":"SHADOW_OBSERVATION_ONLY",
        "framework_state_change":False,
        "portfolio_action":False,
        "captured_at_utc":ts,
        "anchor_core_passed":3,
        "anchor_core_planned":3,
        "market_metrics":{
            "breadth":{"advancers":46,"decliners":32,"flat":22,"constituent_count":100}
        },
        "owners":[],
    }


class FixedCoverageTests(unittest.TestCase):
    def test_gate0f_five_timestamps_are_one_window(self):
        values = [
            "2026-07-28T17:12:27.297Z",
            "2026-07-28T19:43:35.031Z",
            "2026-07-29T00:11:40.027Z",
            "2026-07-29T05:11:52.428Z",
            "2026-07-29T16:51:00.829Z",
        ]
        self.assertEqual(len({fixed_window_id(v) for v in values}), 1)

    def test_dense_four_hour_observations_thirteen_weeks_have_at_least_30_windows(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        receipts = []
        current = start
        end = start + timedelta(weeks=13)
        while current <= end:
            receipts.append({
                "snapshot_utc": current.isoformat().replace("+00:00","Z"),
                "lane_eligibility":{"ROTATION_PERMISSION":{"eligible_for_both":True}},
            })
            current += timedelta(hours=4)
        result = coverage_progress(receipts, now_utc=end.isoformat().replace("+00:00","Z"))
        self.assertGreaterEqual(result["per_lane"]["ROTATION_PERMISSION"]["occupied_fixed_72h_windows"], 30)
        self.assertGreaterEqual(result["per_lane"]["ROTATION_PERMISSION"]["elapsed_prospective_weeks"], 12)

    def test_continuous_observations_do_not_transitively_collapse(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        values = [(start + timedelta(hours=4*i)).isoformat().replace("+00:00","Z") for i in range(24*21//4)]
        self.assertGreater(len({fixed_window_id(v) for v in values}), 1)


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.capture_root = self.root/"03_DAILY_CAPTURE_LOGS"/"captures"
        self.capture_root.mkdir(parents=True)
        cap = capture()
        cap_path = self.capture_root/"2026"/"08"/"09"/"092203_run.json"
        cap_path.parent.mkdir(parents=True)
        cap_path.write_text(json.dumps(cap,sort_keys=True)+"\n")
        (self.capture_root/"LATEST.json").write_text(json.dumps({
            "contract":"DAILY_LIVE_ANCHOR_LATEST_POINTER_v1",
            "captured_at_utc":cap["captured_at_utc"],
            "path":"captures/2026/08/09/092203_run.json",
            "run_id":"gh-test-1",
            "status":"COMPLETE",
        },sort_keys=True)+"\n")
        self.sensor = self.root/"sensor.json"
        self.policy = self.root/"policy.json"
        self.rotation = self.root/"rotation.py"
        self.crosswalk = self.root/"crosswalk.json"
        self.sensor.write_text(json.dumps(registry()))
        self.policy.write_text(json.dumps(policy_registry()))
        self.rotation.write_text("native-rotation-evaluator\n")
        self.crosswalk.write_text('{"contract":"GATE0E_PRIMARY_POLICY_SURFACE_CONTRACT_v1"}\n')
        self.out = self.root/"dual"

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self):
        return collect_from_latest_capture(
            capture_root=self.capture_root,
            output_root=self.out,
            sensor_registry_path=self.sensor,
            policy_registry_path=self.policy,
            rotation_evaluator_path=self.rotation,
            crosswalk_contract_path=self.crosswalk,
        )

    def test_full_and_reduced_same_t_capture_hash_and_exact_profiles(self):
        result = self._run()
        receipt = json.loads(Path(result["pair_receipt"]).read_text())
        full = json.loads(Path(receipt["profiles"][FULL_PROFILE]["path"]).read_text())
        reduced = json.loads(Path(receipt["profiles"][REDUCED_PROFILE]["path"]).read_text())
        self.assertEqual(full["snapshot_utc"], reduced["snapshot_utc"])
        self.assertEqual(full["capture_hash"], reduced["capture_hash"])
        self.assertEqual(full["profile_sensor_count"], 32)
        self.assertEqual(reduced["profile_sensor_count"], 18)

    def test_no_future_minimal_emitted(self):
        result = self._run()
        receipt = json.loads(Path(result["pair_receipt"]).read_text())
        self.assertEqual(receipt["excluded_profiles"], {"LEGACY_MINIMAL":"EXCLUDED_UNRECOVERABLE"})
        self.assertFalse(any("MINIMAL" in p.name for p in Path(result["pair_receipt"]).parent.iterdir()))

    def test_rotation_native_fail_closed_and_missingness_preserved(self):
        result = self._run()
        receipt = json.loads(Path(result["pair_receipt"]).read_text())
        full = json.loads(Path(receipt["profiles"][FULL_PROFILE]["path"]).read_text())
        lane = full["policy_lanes"]["ROTATION_PERMISSION"]
        self.assertEqual(lane["output"], "NO_ROTATION")
        self.assertEqual(lane["native_source"]["adapter_mode"], "NATIVE_FAIL_CLOSED")
        self.assertFalse(lane["native_source"]["imputation"])
        self.assertEqual(full["missingness_by_sensor"]["ETHBTC_DIRECT"], "UNAVAILABLE")

    def test_rebuy_and_trim_not_synthesized(self):
        result = self._run()
        receipt = json.loads(Path(result["pair_receipt"]).read_text())
        full = json.loads(Path(receipt["profiles"][FULL_PROFILE]["path"]).read_text())
        self.assertIsNone(full["policy_lanes"]["REBUY_STATE"]["output"])
        self.assertEqual(full["policy_lanes"]["REBUY_STATE"]["exclusion_reason"], "POLICY_OUTPUT_UNAVAILABLE")
        self.assertIsNone(full["policy_lanes"]["TRIM_EXIT_STATE"]["output"])

    def test_no_comparison_metrics_generated(self):
        result = self._run()
        all_text = "\n".join(p.read_text() for p in Path(result["pair_receipt"]).parent.glob("*.json"))
        forbidden = ("agreement_rate","disagreement","divergence","stack_rank","winner","forecast_score")
        for token in forbidden:
            self.assertNotIn(token, all_text)

    def test_coverage_monitor_does_not_read_policy_children(self):
        result = self._run()
        receipt_path = Path(result["pair_receipt"])
        receipt = json.loads(receipt_path.read_text())
        for profile in (FULL_PROFILE, REDUCED_PROFILE):
            Path(receipt["profiles"][profile]["path"]).write_text("THIS IS NOT JSON")
        rows = load_pair_receipts(self.out/"runs")
        summary = coverage_progress(rows, now_utc="2026-08-09T09:22:03Z")
        self.assertEqual(summary["paired_receipt_count"], 1)
        self.assertEqual(summary["per_lane"]["ROTATION_PERMISSION"]["occupied_fixed_72h_windows"], 1)

    def test_idempotent_same_capture(self):
        first = self._run()
        second = self._run()
        self.assertEqual(first["run_id"], second["run_id"])
        rows = load_pair_receipts(self.out/"runs")
        self.assertEqual(len(rows), 1)


if __name__ == "__main__":
    unittest.main()
