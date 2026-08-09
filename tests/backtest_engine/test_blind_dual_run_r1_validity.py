from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backtest_engine.blind_dual_run import (
    COVERAGE_CONTRACT,
    CURRENT_DEPENDENCY_MAP,
    DEPENDENCY_MAP_HASH,
    FULL_PROFILE,
    REDUCED_PROFILE,
    REDUCED_SENSOR_IDS,
    VALIDITY_CONTRACT,
    collect_from_latest_capture,
    coverage_progress,
    fixed_window_id,
    load_pair_receipts,
    obj_sha,
)

FULL_ONLY = (
    "ETHBTC_DERIVED","ETH_DOMINANCE","BREADTH_ABOVE_MA50","ETF_FLOW_DIVERGENCE",
    "FUTURES_BASIS","FUTURES_TAKER_RATIO","CFGI","TDBC","YIELD_CURVE","VIX",
    "DOLLAR_INDEX","STABLECOIN_SUPPLY","CHAIN_TVL","DEX_VOLUME",
)
FULL_SENSORS = REDUCED_SENSOR_IDS + FULL_ONLY


def registry():
    return {
        "rows": [[s,"X","X","X","CORE","OWNER","FAIL_CLOSED"] for s in FULL_SENSORS],
        "stack_profiles": {FULL_PROFILE:"all non-retired sensors", REDUCED_PROFILE:list(REDUCED_SENSOR_IDS)},
    }


def policies():
    return {"families": {
        "ROTATION_PERMISSION":{"decision_values":["NO_ROTATION","ETH_RELATIVE_STRENGTH","SELECTIVE_LARGE_CAP","BROAD_ALT"]},
        "REBUY_LOCK":{"decision_values":["LOCKED","WATCH_ONLY","PERMITTED"]},
        "TRIM_NO_TRIM":{"decision_values":["NO_TRIM","PARTIAL_TRIM","FULL_TRIM"]},
    }}


def base_capture(ts="2026-08-09T14:02:39Z"):
    return {
        "contract":"DAILY_LIVE_ANCHOR_INDEX_v3","status":"COMPLETE","authority":"SHADOW_OBSERVATION_ONLY",
        "framework_state_change":False,"portfolio_action":False,"captured_at_utc":ts,
        "anchor_core_passed":3,"anchor_core_planned":3,
        "market_metrics":{"breadth":{"advancers":46,"decliners":32,"flat":22,"constituent_count":100}},
        "owners":[],
    }


def synthetic_receipt(ts: str, *, pair=True, identifying=False, schema="BLINDED_PAIRED_EVIDENCE_RECEIPT_v3"):
    lane_validity = {}
    for lane in ("ROTATION_PERMISSION","REBUY_STATE","TRIM_EXIT_STATE"):
        lane_validity[lane] = {
            "pair_execution_valid": pair,
            "identifying_opportunity": identifying,
            "structural_identifiability":"IDENTIFYING_PATH_PROVEN" if identifying else "DEPENDENCY_MAP_UNPROVEN",
            "dependency_provenance_status":"PROVEN" if identifying else "UNPROVEN",
        }
    return {
        "schema_version":schema,
        "snapshot_utc":ts,
        "lane_eligibility":{lane:{"eligible_for_both":pair} for lane in lane_validity},
        "lane_validity":lane_validity,
    }


class R1ValidityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.caproot = self.root/"captures"
        cap = base_capture()
        cap_path = self.caproot/"2026"/"08"/"09"/"140239_run.json"
        cap_path.parent.mkdir(parents=True)
        cap_path.write_text(json.dumps(cap)+"\n")
        (self.caproot/"LATEST.json").write_text(json.dumps({"path":"captures/2026/08/09/140239_run.json"})+"\n")
        self.sensor=self.root/"sensor.json"; self.sensor.write_text(json.dumps(registry()))
        self.policy=self.root/"policy.json"; self.policy.write_text(json.dumps(policies()))
        self.rotation=self.root/"rotation.py"; self.rotation.write_text("frozen rotation\n")
        self.crosswalk=self.root/"crosswalk.json"; self.crosswalk.write_text('{"contract":"frozen"}\n')
        self.out=self.root/"out"

    def tearDown(self):
        self.tmp.cleanup()

    def run_collect(self):
        return collect_from_latest_capture(
            capture_root=self.caproot,output_root=self.out,sensor_registry_path=self.sensor,
            policy_registry_path=self.policy,rotation_evaluator_path=self.rotation,crosswalk_contract_path=self.crosswalk,
        )

    def test_01_fail_closed_pair_is_technical_not_identifying(self):
        result=self.run_collect(); receipt=json.loads(Path(result["pair_receipt"]).read_text())
        row=receipt["lane_validity"]["ROTATION_PERMISSION"]
        self.assertTrue(row["pair_execution_valid"])
        self.assertFalse(row["identifying_opportunity"])
        self.assertEqual(row["identifying_exclusion_reason"],"NO_PROFILE_SPECIFIC_COUNTERFACTUAL_EVIDENCE")

    def test_02_fail_closed_pair_does_not_count_toward_b2_readiness(self):
        result=self.run_collect(); monitor=json.loads(Path(result["coverage"]).read_text())
        lane=monitor["per_lane"]["ROTATION_PERMISSION"]
        self.assertEqual(lane["occupied_pair_execution_windows"],1)
        self.assertEqual(lane["occupied_identifying_windows"],0)
        self.assertFalse(lane["b2_coverage_ready"])

    def test_03_current_receipt_is_versioned_v3(self):
        result=self.run_collect(); receipt=json.loads(Path(result["pair_receipt"]).read_text())
        self.assertEqual(receipt["schema_version"],"BLINDED_PAIRED_EVIDENCE_RECEIPT_v3")
        self.assertEqual(receipt["coverage_validity_contract"],COVERAGE_CONTRACT)

    def test_04_pre_r1_v2_is_never_identifying_by_default(self):
        old={"schema_version":"BLINDED_PAIRED_EVIDENCE_RECEIPT_v2","snapshot_utc":"2026-08-01T00:00:00Z","lane_eligibility":{"ROTATION_PERMISSION":{"eligible_for_both":True}}}
        out=coverage_progress([old],now_utc="2026-08-01T01:00:00Z")["per_lane"]["ROTATION_PERMISSION"]
        self.assertEqual(out["pair_execution_valid_rows"],1)
        self.assertEqual(out["identifying_opportunity_rows"],0)
        self.assertFalse(out["b2_coverage_ready"])

    def test_05_thirteen_weeks_identifying_metadata_can_satisfy_math(self):
        start=datetime(2026,1,1,tzinfo=timezone.utc); end=start+timedelta(weeks=13); rows=[]; cur=start
        while cur<=end:
            rows.append(synthetic_receipt(cur.isoformat().replace('+00:00','Z'),identifying=True)); cur+=timedelta(hours=4)
        lane=coverage_progress(rows,now_utc=end.isoformat().replace('+00:00','Z'))["per_lane"]["ROTATION_PERMISSION"]
        self.assertGreaterEqual(lane["occupied_identifying_windows"],30)
        self.assertGreaterEqual(lane["elapsed_identifying_weeks"],12)
        self.assertTrue(lane["b2_coverage_ready"])

    def test_06_thirteen_weeks_nonidentifying_never_becomes_ready(self):
        start=datetime(2026,1,1,tzinfo=timezone.utc); end=start+timedelta(weeks=13); rows=[]; cur=start
        while cur<=end:
            rows.append(synthetic_receipt(cur.isoformat().replace('+00:00','Z'),identifying=False)); cur+=timedelta(hours=4)
        lane=coverage_progress(rows,now_utc=end.isoformat().replace('+00:00','Z'))["per_lane"]["ROTATION_PERMISSION"]
        self.assertGreaterEqual(lane["occupied_pair_execution_windows"],30)
        self.assertEqual(lane["occupied_identifying_windows"],0)
        self.assertFalse(lane["b2_coverage_ready"])

    def test_07_dependency_map_frozen_and_hashed(self):
        self.assertEqual(DEPENDENCY_MAP_HASH,obj_sha(CURRENT_DEPENDENCY_MAP))
        self.assertEqual(DEPENDENCY_MAP_HASH,"2a56444ba7ae9ab46a23c891379c062a79bb417bc8b4c2c351d4a8c516d63622")

    def test_08_rotation_dependency_provenance_is_unproven_not_invented(self):
        row=CURRENT_DEPENDENCY_MAP["ROTATION_PERMISSION"]
        self.assertEqual(row["dependency_provenance_status"],"UNPROVEN")
        self.assertEqual(row["candidate_full_only_dependencies"],["BREADTH_ABOVE_MA50"])
        self.assertEqual(row["proven_consumed_full_only_dependencies"],[])

    def test_09_rebuy_and_trim_native_output_unavailable(self):
        result=self.run_collect(); receipt=json.loads(Path(result["pair_receipt"]).read_text())
        for lane in ("REBUY_STATE","TRIM_EXIT_STATE"):
            validity=receipt["lane_validity"][lane]
            self.assertFalse(validity["pair_execution_valid"])
            self.assertFalse(validity["identifying_opportunity"])
            self.assertEqual(validity["identifying_exclusion_reason"],"NATIVE_OUTPUT_UNAVAILABLE_FOR_PROSPECTIVE_COUNTERFACTUAL")

    def test_10_explicit_rotation_evidence_still_fails_closed_on_unproven_dependency_map(self):
        cap=base_capture(); evidence={
            "direct_ethbtc_available":True,"ethbtc_authority_status":"DIRECT_OWNER","ethbtc_settled_close":0.031,
            "ethbtc_positive_settled_run":4,"eth_leads_btc_sessions":2,"large_cap_breadth":0.55,
            "broad_alt_breadth":0.60,"beta_neutral_alt_return_20d":0.01,"btc_dominance_change_5d":-0.1,
            "flow_confirmation":True,"source_qa_pass":True,
        }
        cap["profile_native_rotation_evidence"]={FULL_PROFILE:evidence,REDUCED_PROFILE:evidence}
        p=self.caproot/"2026"/"08"/"09"/"140239_run.json"; p.write_text(json.dumps(cap)+"\n")
        result=self.run_collect(); receipt=json.loads(Path(result["pair_receipt"]).read_text())
        v=receipt["lane_validity"]["ROTATION_PERMISSION"]
        self.assertTrue(v["pair_execution_valid"])
        self.assertFalse(v["identifying_opportunity"])
        self.assertEqual(v["identifying_exclusion_reason"],"DEPENDENCY_MAP_UNPROVEN")

    def test_11_receipt_contains_metadata_not_policy_values(self):
        result=self.run_collect(); receipt=json.loads(Path(result["pair_receipt"]).read_text())
        text=json.dumps(receipt,sort_keys=True)
        self.assertNotIn('"output"',text)
        self.assertIn('lane_validity',receipt)

    def test_12_monitor_does_not_open_children(self):
        result=self.run_collect(); receipt=json.loads(Path(result["pair_receipt"]).read_text())
        for profile in (FULL_PROFILE,REDUCED_PROFILE): Path(receipt["profiles"][profile]["path"]).write_text("NOT JSON")
        rows=load_pair_receipts(self.out/"runs")
        lane=coverage_progress(rows,now_utc="2026-08-09T14:02:39Z")["per_lane"]["ROTATION_PERMISSION"]
        self.assertEqual(lane["pair_execution_valid_rows"],1)
        self.assertEqual(lane["identifying_opportunity_rows"],0)

    def test_13_fixed_epoch_math_unchanged(self):
        vals=["2026-07-28T17:12:27.297Z","2026-07-28T19:43:35.031Z","2026-07-29T00:11:40.027Z","2026-07-29T05:11:52.428Z","2026-07-29T16:51:00.829Z"]
        self.assertEqual(len({fixed_window_id(v) for v in vals}),1)

    def test_14_no_legacy_minimal(self):
        result=self.run_collect(); receipt=json.loads(Path(result["pair_receipt"]).read_text())
        self.assertEqual(receipt["excluded_profiles"],{"LEGACY_MINIMAL":"EXCLUDED_UNRECOVERABLE"})

    def test_15_exact_profile_counts_remain_32_and_18(self):
        result=self.run_collect(); receipt=json.loads(Path(result["pair_receipt"]).read_text())
        full=json.loads(Path(receipt["profiles"][FULL_PROFILE]["path"]).read_text()); reduced=json.loads(Path(receipt["profiles"][REDUCED_PROFILE]["path"]).read_text())
        self.assertEqual(full["profile_sensor_count"],32); self.assertEqual(reduced["profile_sensor_count"],18)

    def test_16_monitor_contract_explicitly_identifying_only(self):
        out=coverage_progress([],now_utc="2026-08-09T14:02:39Z")
        self.assertEqual(out["schema_version"],"PROSPECTIVE_B2_COVERAGE_MONITOR_v2")
        self.assertEqual(out["validity_contract"],VALIDITY_CONTRACT)
        self.assertEqual(out["readiness_basis"],"IDENTIFYING_OPPORTUNITY_ONLY")

    def test_17_runtime_wrapper_direct_execution_can_import_package(self):
        repo=Path(__file__).resolve().parents[2]
        proc=subprocess.run([sys.executable,"scripts/daily_capture/materialize_blind_dual_run.py","--help"],cwd=repo,text=True,capture_output=True)
        self.assertEqual(proc.returncode,0,proc.stderr)

    def test_18_right_edge_is_reported_separately_for_pair_and_identifying(self):
        row=synthetic_receipt("2026-08-09T14:00:00Z",identifying=False)
        lane=coverage_progress([row],now_utc="2026-08-09T14:01:00Z")["per_lane"]["ROTATION_PERMISSION"]
        self.assertTrue(lane["pair_execution_right_edge_partial_window"])
        self.assertFalse(lane["right_edge_partial_window"])


if __name__ == "__main__":
    unittest.main()
