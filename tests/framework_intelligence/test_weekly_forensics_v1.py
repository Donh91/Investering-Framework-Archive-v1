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

if __name__=="__main__": unittest.main()
