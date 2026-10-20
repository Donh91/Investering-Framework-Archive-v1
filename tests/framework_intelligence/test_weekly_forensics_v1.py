import importlib.util, json, tempfile, unittest
from pathlib import Path

SCRIPT=Path("scripts/framework_intelligence/weekly_forensics_v1.py")
spec=importlib.util.spec_from_file_location("wf",SCRIPT); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class WeeklyForensicsTest(unittest.TestCase):
    def test_routes_are_closed(self):
        self.assertIn("GOVERNANCE_REVIEW",mod.ROUTES); self.assertIn("NO_ACTION",mod.ROUTES)
    def test_finding_has_routing_and_dedup_contract(self):
        x=mod.finding("META_HEALTH","HIGH","DETERMINISTIC_REPAIR","r",["e"],"o","n","s","g")
        for k in ("fingerprint","dedup_key","owner","next_action","stop_condition","acceptance_gate","cheapest_sufficient_executor"): self.assertIn(k,x)
    def test_invalid_route_rejected(self):
        with self.assertRaises(AssertionError): mod.finding("X","HIGH","MAGIC","r",[],"o","n","s","g")
    def test_frozen_reader_accepts_exact_legacy_literal_newline_only(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"FINAL.json"
            payload={"contract":"WEEKLY_FORENSICS_PACK_v1","iso_week":40}
            p.write_text(json.dumps(payload)+"\\n")
            self.assertEqual(mod.read_frozen_snapshot(p),payload)
            p.write_text(json.dumps(payload)+"garbage")
            self.assertIsNone(mod.read_frozen_snapshot(p))
    def test_writer_uses_real_newline_not_literal_escape(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"FINAL.json"
            payload={"contract":"WEEKLY_FORENSICS_PACK_v1"}
            mod.write_json(p,payload)
            raw=p.read_text()
            self.assertTrue(raw.endswith("\n"))
            self.assertFalse(raw.endswith("\\n"))
            self.assertEqual(json.loads(raw),payload)

if __name__=="__main__": unittest.main()

# FINAL snapshots are intentionally immutable and Monday FINAL targets the completed ISO week.
