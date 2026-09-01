import importlib.util, json, pathlib, unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

CM=load("cm",pathlib.Path("scripts/research_sources/coinmetrics_community_probe.py"))
BG=load("bg",pathlib.Path("scripts/research_sources/bgeometrics_research_probe.py"))
PM=load("pm",pathlib.Path("scripts/research_sources/polymarket_expectations_parser.py"))

class TestResearchSourceProbes(unittest.TestCase):
    def test_coinmetrics_summary(self):
        raw=b"time,PriceUSD,CapMVRVCur,HashRate\n2009-01-03,,,\n2026-08-31,78000,1.7,100\n"
        r=CM.summarize_csv(raw,"deadbeef")
        self.assertEqual(r["row_count"],2)
        self.assertFalse(r["source_ref_mutable"])
        self.assertTrue(r["required_field_presence"]["CapMVRVCur"])
        self.assertFalse(r["raw_persisted"])

    def test_coinmetrics_fails_without_time(self):
        with self.assertRaises(CM.ProbeError): CM.summarize_csv(b"x\n1\n","main")

    def test_bgeometrics_series_summary(self):
        raw=json.dumps([{"d":"2026-08-30","mvrv":1.5},{"d":"2026-08-31","mvrv":1.6}]).encode()
        r=BG.summarize_series(raw,"mvrv")
        self.assertEqual(r["row_count"],2); self.assertEqual(r["latest_observation"],"2026-08-31")
        self.assertFalse(r["persistence"]["raw_public_persistence"])

    def test_bgeometrics_urpd_summary(self):
        raw=json.dumps([
            {"theDate":"2026-08-31","priceLower":70000,"priceUpper":71000,"btcSupply":10,"pctSupply":0.1},
            {"theDate":"2026-08-31","priceLower":71000,"priceUpper":72000,"btcSupply":20,"pctSupply":0.2}
        ]).encode()
        r=BG.summarize_urpd(raw)
        self.assertEqual(r["snapshot_dates"],["2026-08-31"])
        self.assertEqual(r["median_bin_width"],1000.0)
        self.assertAlmostEqual(r["pct_supply_sum"],0.3)

    def test_bgeometrics_guardrails(self):
        with self.assertRaises(BG.ProbeError): BG.build_url("funding-rate",None)
        with self.assertRaises(BG.ProbeError): BG.build_url("mvrv","2026-08-31")

    def test_polymarket_offline_parser(self):
        raw=json.dumps({"history":[{"t":1,"p":0.2},{"t":2,"p":0.8}]}).encode()
        r=PM.summarize_prices_history(raw)
        self.assertEqual(r["row_count"],2)
        self.assertIn("BLOCKED",r["network_collection"])
        self.assertFalse(r["raw_persisted"])

    def test_polymarket_rejects_non_probability(self):
        raw=json.dumps({"history":[{"t":1,"p":1.2}]}).encode()
        with self.assertRaises(PM.ProbeError): PM.summarize_prices_history(raw)

if __name__=="__main__": unittest.main()
