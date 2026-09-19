from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
VALIDATOR=ROOT/"06_RESEARCH_LAB/alpha_lab/tools/validate_alpha_prospective_edge_v1.py"
CONTRACT_PATH=ROOT/"06_RESEARCH_LAB/alpha_lab/ALPHA_LAB_PROSPECTIVE_EDGE_EXPERIMENTS_v1.json"
spec=importlib.util.spec_from_file_location("alpha_edge_validator",VALIDATOR)
assert spec and spec.loader
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
CONTRACT=json.loads(CONTRACT_PATH.read_text())
H="a"*64

class AlphaProspectiveEdgeValidatorTests(unittest.TestCase):
    def frozen_e3(self):
        return {
            "row_id":"E3-P1-I1",
            "row_type":"FROZEN_INPUT_ROW",
            "test_id":"ALPHA_LAB_PROSPECTIVE_EDGE_V1",
            "experiment_id":"ALPHA_E3_DELTA_PUBLISH",
            "prereg_id":"P1",
            "frozen_at_utc":"2026-09-19T10:00:00Z",
            "window_start_utc":"2026-09-19T11:00:00Z",
            "window_end_utc":"2026-10-31T00:00:00Z",
            "spec_sha256":H,
            "source_code_sha":"abc123",
            "eligibility_manifest_sha256":H,
            "metric_definition_sha256":H,
            "benchmark_definition_sha256":H,
            "kill_condition_sha256":H,
            "first_party_surface_url":"https://example.com/launch",
            "first_party_surface_content_sha256":H,
            "external_benchmark_definition_sha256":H,
            "external_edge_budget_minutes":60,
        }

    def test_valid_e3_freeze(self):
        result=m.validate(self.frozen_e3(),CONTRACT)
        self.assertTrue(result["valid"],result)

    def test_freeze_with_outcome_field_is_rejected(self):
        row=self.frozen_e3()
        row["machine_verdict"]="PROSPECTIVE_PASS"
        result=m.validate(row,CONTRACT)
        self.assertFalse(result["valid"])
        self.assertTrue(any(x.startswith("OUTCOME_PRESENT_AT_FREEZE") for x in result["errors"]))

    def test_partial_coverage_cannot_pass(self):
        row={
            "row_id":"E1-P1-O1","row_type":"OUTCOME_ROW",
            "test_id":"ALPHA_LAB_PROSPECTIVE_EDGE_V1","experiment_id":"ALPHA_E1_DISCLOSED_ADDRESS_DEPLOYER",
            "prereg_id":"P1","input_row_id":"E1-P1-I1","observed_at_utc":"2026-09-20T10:00:00Z",
            "data_health":"PASS","requested_coverage":100,"returned_coverage":50,"provider_identity":"provider",
            "source_content_sha256":H,"source_commit_receipt":"sha:path","eligibility":"ELIGIBLE",
            "machine_verdict":"PROSPECTIVE_PASS","future_launch_id":"L1","canonical_ca":"0x1",
            "receipt_from":"0x2","deployer":"0x2","exact_address_match":True,"corroboration_state":"CORROBORATED"
        }
        result=m.validate(row,CONTRACT)
        self.assertFalse(result["valid"])
        self.assertIn("PARTIAL_COVERAGE_CANNOT_PASS",result["errors"])

    def test_degraded_data_cannot_pass(self):
        row={
            "row_id":"E4-P1-O1","row_type":"OUTCOME_ROW",
            "test_id":"ALPHA_LAB_PROSPECTIVE_EDGE_V1","experiment_id":"ALPHA_E4_DEV_BUY_OOS",
            "prereg_id":"P1","input_row_id":"E4-P1-I1","observed_at_utc":"2026-09-20T10:00:00Z",
            "data_health":"DEGRADED","requested_coverage":100,"returned_coverage":100,"provider_identity":"provider",
            "source_content_sha256":H,"source_commit_receipt":"sha:path","eligibility":"ELIGIBLE",
            "machine_verdict":"PROSPECTIVE_PASS","eligible_launches":100,"qualified_dev_buy_launches":10,
            "qualified_outcomes":10,"base_rate":0.02,"observed_rate":0.03,"lift":1.5,
            "uncertainty_interval":[1.0,2.0]
        }
        result=m.validate(row,CONTRACT)
        self.assertFalse(result["valid"])
        self.assertIn("DEGRADED_DATA_CANNOT_PASS",result["errors"])

    def test_unknown_metric_cannot_be_encoded_as_zero(self):
        row={
            "row_id":"E1-P1-O2","row_type":"OUTCOME_ROW",
            "test_id":"ALPHA_LAB_PROSPECTIVE_EDGE_V1","experiment_id":"ALPHA_E1_DISCLOSED_ADDRESS_DEPLOYER",
            "prereg_id":"P1","input_row_id":"E1-P1-I1","observed_at_utc":"2026-09-20T10:00:00Z",
            "data_health":"UNKNOWN","requested_coverage":100,"returned_coverage":0,"provider_identity":"provider",
            "source_content_sha256":H,"source_commit_receipt":"sha:path","eligibility":"UNKNOWN",
            "machine_verdict":"DEGRADED","future_launch_id":"L1","canonical_ca":"0x1",
            "receipt_from":"UNKNOWN","deployer":"UNKNOWN","exact_address_match":"UNKNOWN","corroboration_state":"UNKNOWN",
            "metrics":{"matches":0},"metric_missingness":{"matches":"UNKNOWN"}
        }
        result=m.validate(row,CONTRACT)
        self.assertFalse(result["valid"])
        self.assertIn("MISSING_TO_ZERO:matches",result["errors"])

if __name__=="__main__":
    unittest.main()
