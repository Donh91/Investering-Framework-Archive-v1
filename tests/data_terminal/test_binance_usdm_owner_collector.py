from __future__ import annotations
import importlib.util, json, sys, tempfile, unittest
from pathlib import Path

MODULE_PATH=Path(__file__).resolve().parents[2]/"scripts/data_terminal/binance_usdm_owner_collector.py"
SPEC=importlib.util.spec_from_file_location("binance_usdm_owner_collector",MODULE_PATH)
module=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=module; SPEC.loader.exec_module(module)

class TestBinanceUsdmOwnerCollector(unittest.TestCase):
    def test_funding_parse(self):
        payload=json.dumps([{"symbol":"BTCUSDT","fundingTime":1753968000000,"fundingRate":"0.0001"}]).encode()
        rows=module.parse("funding","BTCUSDT",payload,"2026-07-31T18:00:00Z")
        self.assertEqual(rows[0]["metric"],"funding")
        self.assertAlmostEqual(rows[0]["value"],0.0001)
    def test_open_interest_parse(self):
        payload=json.dumps({"symbol":"BTCUSDT","openInterest":"12345.6","time":1753968000000}).encode()
        rows=module.parse("open_interest","BTCUSDT",payload,"2026-07-31T18:00:00Z")
        self.assertEqual(rows[0]["units"],"base_asset")
    def test_mark_parse(self):
        payload=json.dumps({"symbol":"ETHUSDT","markPrice":"3210.5","time":1753968000000}).encode()
        rows=module.parse("mark_price","ETHUSDT",payload,"2026-07-31T18:00:00Z")
        self.assertEqual(rows[0]["value"],3210.5)
    def test_schema_drift(self):
        with self.assertRaises(module.CollectorError): module.parse("funding","BTCUSDT",b"{}","2026-07-31T18:00:00Z")
    def test_negative_non_funding_rejected(self):
        payload=json.dumps({"symbol":"BTCUSDT","openInterest":"-1","time":1753968000000}).encode()
        with self.assertRaises(module.CollectorError): module.parse("open_interest","BTCUSDT",payload,"2026-07-31T18:00:00Z")
    def test_manifest_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/"x.txt").write_text("ok")
            b=(root/"x.txt").read_bytes()
            (root/"artifact_manifest.json").write_text(json.dumps({"members":[{"path":"x.txt","bytes":len(b),"sha256":module.sha(b)}]}))
            self.assertEqual(module.verify(root)["status"],"PASS")

if __name__=="__main__": unittest.main()
