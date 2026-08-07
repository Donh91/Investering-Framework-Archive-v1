import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "experiments" / "pdlt_v1_1.py"
SPEC = importlib.util.spec_from_file_location("pdlt_v1_1", MODULE_PATH)
pdlt = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(pdlt)

CONFIG = ROOT / "research" / "experiments" / "pdlt_v1_1" / "PDLT_CONFIG_v1_1.json"


class PDLTConfigTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads(CONFIG.read_text())

    def test_budget_is_fail_closed(self):
        result = pdlt.validate_config(self.cfg)
        self.assertEqual(result["historical_credits"], 12300)
        self.assertEqual(result["planned_credits"], 18060)
        self.assertEqual(result["maximum_credits"], 19980)
        self.assertLessEqual(result["maximum_credits"], 20000)

    def test_credit_formula_detects_drift(self):
        broken = json.loads(CONFIG.read_text())
        broken["cfgi"]["historical_plan"][0]["expected_credits"] = 7199
        with self.assertRaises(ValueError):
            pdlt.validate_config(broken)

    def test_field_set_is_frozen(self):
        broken = json.loads(CONFIG.read_text())
        broken["cfgi"]["historical_plan"][0]["fields"] = ["score"]
        with self.assertRaises(ValueError):
            pdlt.validate_config(broken)

    def test_epoch_boundary(self):
        boundary = self.cfg["cfgi"]["engine_epoch_boundary_utc"]
        self.assertEqual(pdlt.epoch_for("2026-07-07T23:59:59Z", boundary), "LEGACY_PRE_20260708")
        self.assertEqual(pdlt.epoch_for("2026-07-08T00:00:00Z", boundary), "UPGRADED_POST_20260708")

    def test_preregistration_hash_is_stable_for_same_config(self):
        a = pdlt.make_manifest(self.cfg)
        b = pdlt.make_manifest(self.cfg)
        self.assertEqual(a["config_sha256"], b["config_sha256"])
        self.assertEqual(a["arms"], b["arms"])
        self.assertEqual(a["outcomes"], b["outcomes"])

    def test_cfgi_validation_fails_on_truncated_block(self):
        expected = self.cfg["cfgi"]["historical_plan"][0]
        packet = {
            "contract": "CFGI_OWNER_SNAPSHOT_v3",
            "symbols": expected["symbols"],
            "timeframe": expected["timeframe"],
            "fields": expected["fields"],
            "limit": expected["limit"],
            "billing": {"expected_credits": expected["expected_credits"], "credits_used": None},
            "rows": []
        }
        with self.assertRaisesRegex(ValueError, "row_count_mismatch"):
            pdlt.validate_cfgi_snapshot(packet, self.cfg, expected)

    def test_cfgi_row_requires_every_requested_field(self):
        expected = {"symbols": ["MARKET"], "fields": pdlt.FIELDS, "timeframe": "4h", "limit": 1, "expected_credits": 10, "name": "test"}
        row = {
            "symbol": "MARKET",
            "timestamp": "2026-08-07T16:00:00Z",
            "stale": False,
            "score": 50,
            "components": {k: 50 for k in pdlt.FIELDS if k not in {"score", "orders"}}
        }
        packet = {
            "contract": "CFGI_OWNER_SNAPSHOT_v3",
            "symbols": ["MARKET"],
            "timeframe": "4h",
            "fields": pdlt.FIELDS,
            "limit": 1,
            "billing": {"expected_credits": 10, "credits_used": 10},
            "rows": [row]
        }
        with self.assertRaisesRegex(ValueError, "missing_requested_field"):
            pdlt.validate_cfgi_snapshot(packet, self.cfg, expected)


if __name__ == "__main__":
    unittest.main()
