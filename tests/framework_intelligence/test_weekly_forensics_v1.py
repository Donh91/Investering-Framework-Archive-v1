import importlib.util, json, tempfile, unittest
from pathlib import Path

SCRIPT=Path("scripts/framework_intelligence/weekly_forensics_v1.py")
spec=importlib.util.spec_from_file_location("wf",SCRIPT); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class WeeklyForensicsTest(unittest.TestCase):
    def write_fsa_packet(self, root, hourly_row_status="PASS", bc_status="PASS", bc_score=49, price=63000):
        pointer = root / "04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json"
        path = "04_MARKET_LEARNING/entry_signals/auto_market_state/runs/2026/11/19/072641_123456789abc.json"
        packet = {"source_health": {"hourly_market": {"status": "PASS", "row": {"status": hourly_row_status}},
                                    "altseason_context": {"status": "PASS"}},
                  "normalized_state": {"live_market": {"btc_usdt": price, "eth_usdt": 1800, "ethbtc": .028},
                      "altseason_context": {"blockchaincenter_altcoin_season": {"status": bc_status, "horizons": {"90": {"published_score": bc_score}}},
                                            "coinmarketcap_altcoin_season": {"status": "PASS", "published_score": 58}}}}
        raw = (json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()
        packet["packet_sha256"] = mod.hashlib.sha256(raw).hexdigest()
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        mod.write_json(target, packet)
        mod.write_json(pointer, {"packet_path": path, "packet_sha256": packet["packet_sha256"]})
        return pointer, target

    def test_fsa_source_checks_healthy_and_valid_zero(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fsa_packet(root, bc_score=0)
            self.assertEqual(mod.surgical_source_findings(root), [])

    def test_fsa_detects_exact_row_and_altseason_false_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fsa_packet(root, hourly_row_status="UNAVAILABLE", bc_status="DEGRADED", bc_score=None)
            xs = mod.surgical_source_findings(root)
            self.assertEqual(len(xs), 2)
            self.assertTrue(all(x["owner"] == "#1827" and x["severity"] == "HIGH" for x in xs))
            self.assertTrue(any("hourly PASS" in x["reason"] for x in xs))
            self.assertTrue(any("BlockchainCenter 90d" in x["reason"] for x in xs))

    def test_fsa_invalid_price_and_boolean_score(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write_fsa_packet(root, price=0, bc_score=True)
            self.assertEqual(len(mod.surgical_source_findings(root)), 2)

    def test_fsa_rejects_bad_binding_and_path_escape(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pointer, target = self.write_fsa_packet(root)
            target.write_text("{}")
            self.assertIn("binding unavailable", mod.surgical_source_findings(root)[0]["reason"])
            mod.write_json(pointer, {"packet_path": "../../outside.json", "packet_sha256": "x"})
            self.assertIn("binding unavailable", mod.surgical_source_findings(root)[0]["reason"])

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
