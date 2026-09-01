import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CM = load("cm", pathlib.Path("scripts/research_sources/coinmetrics_community_probe.py"))
BG = load("bg", pathlib.Path("scripts/research_sources/bgeometrics_research_probe.py"))
URPD = load("urpd", pathlib.Path("scripts/research_sources/urpd_topology_probe.py"))
PM = load("pm", pathlib.Path("scripts/research_sources/polymarket_expectations_parser.py"))


class TestResearchSourceProbes(unittest.TestCase):
    def test_coinmetrics_summary_requires_immutable_evidence_ref(self):
        raw = b"time,PriceUSD,CapMVRVCur,HashRate\n2009-01-03,,,\n2026-05-23,78000,1.7,100\n"
        good_ref = "a" * 40
        result = CM.summarize_csv(raw, good_ref)
        self.assertEqual(result["row_count"], 2)
        self.assertTrue(result["source_ref_evidence_eligible"])
        self.assertTrue(result["required_field_presence"]["CapMVRVCur"])
        self.assertFalse(result["raw_persisted"])
        mutable = CM.summarize_csv(raw, "main")
        self.assertFalse(mutable["source_ref_evidence_eligible"])

    def test_coinmetrics_fails_without_time(self):
        with self.assertRaises(CM.ProbeError):
            CM.summarize_csv(b"x\n1\n", "a" * 40)

    def test_bgeometrics_series_summary(self):
        raw = json.dumps([{"d": "2026-08-30", "mvrv": 1.5}, {"d": "2026-08-31", "mvrv": 1.6}]).encode()
        result = BG.summarize_series(raw, "mvrv")
        self.assertEqual(result["row_count"], 2)
        self.assertEqual(result["latest_observation"], "2026-08-31")
        self.assertFalse(result["persistence"]["raw_public_persistence"])

    def test_bgeometrics_build_url(self):
        self.assertEqual(BG.build_url("mvrv", None, None), "https://bitcoin-data.com/v1/mvrv")
        self.assertIn("startday=2026-01-01", BG.build_url("sopr", "2026-01-01", "2026-02-01"))
        with self.assertRaises(BG.ProbeError):
            BG.build_url("funding-rate", None, None)
        with self.assertRaises(BG.ProbeError):
            BG.build_url("mvrv", "2026-01-01", None)

    def test_urpd_topology_derived_only(self):
        raw = json.dumps([
            {"priceLower": 80, "priceUpper": 90, "utxoCount": 10, "btcSupply": 1, "pctSupply": 0.10},
            {"priceLower": 90, "priceUpper": 100, "utxoCount": 20, "btcSupply": 2, "pctSupply": 0.20},
            {"priceLower": 100, "priceUpper": 110, "utxoCount": 30, "btcSupply": 3, "pctSupply": 0.40},
            {"priceLower": 110, "priceUpper": 120, "utxoCount": 20, "btcSupply": 2, "pctSupply": 0.20},
            {"priceLower": 120, "priceUpper": 130, "utxoCount": 10, "btcSupply": 1, "pctSupply": 0.10},
        ]).encode()
        result = URPD.summarize_topology(raw, "2026-08-30", 100.0)
        self.assertEqual(result["requested_day"], "2026-08-30")
        self.assertEqual(result["row_count"], 5)
        self.assertFalse(result["raw_persisted"])
        self.assertIn("cost_basis_concentration_entropy_norm", result["derived_features"])
        self.assertNotIn("bins", result)

    def test_urpd_rejects_missing_schema(self):
        raw = json.dumps([{"price": 100, "supply": 1}]).encode()
        with self.assertRaises(URPD.ProbeError):
            URPD.summarize_topology(raw, "2026-08-30", 100.0)

    def test_polymarket_offline_parser(self):
        raw = json.dumps({"history": [{"t": 1, "p": 0.2}, {"t": 2, "p": 0.8}]}).encode()
        result = PM.summarize_prices_history(raw)
        self.assertEqual(result["row_count"], 2)
        self.assertIn("DISABLED", result["network_collection"])
        self.assertIn("RESEARCH", result["research_access"])
        self.assertFalse(result["raw_persisted"])

    def test_polymarket_rejects_non_probability(self):
        raw = json.dumps({"history": [{"t": 1, "p": 1.2}]}).encode()
        with self.assertRaises(PM.ProbeError):
            PM.summarize_prices_history(raw)


if __name__ == "__main__":
    unittest.main()
