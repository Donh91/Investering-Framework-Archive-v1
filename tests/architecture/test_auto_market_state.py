from __future__ import annotations
import json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from scripts.data_ping import auto_market_state as a
NOW=datetime(2026,9,1,21,0,tzinfo=timezone.utc)

class FakeSnapshot:
    commit_sha="a"*40; resolution_count=1
    def read_json(self,path): raise FileNotFoundError(path)

class T(unittest.TestCase):
    def registry(self): return {"sources":[{"manual_replacement_lane":x,"unattended_git_owner":True,"normalization_contract":"X"} for x in a.LANES]}
    def health(self): return {x:{"status":"PASS"} for x in a.LANES}
    def stable(self,total=309e9,binding=False): return {"contract":"DEFILLAMA_STABLECOIN_LIQUIDITY_OWNER_v1_1","global":{"total_usd":total,"change_1d_pct":-.1,"change_7d_pct":.2,"change_30d_pct":1.1},"evidence_semantics":{"evidence_role":"SUPPLY_LIQUIDITY","deployment_confirmation":"NOT_ESTABLISHED"},"authority":{"binding":binding,"canonical_acceptance":False,"state_change":False,"portfolio_action":False}}
    def test_stablecoin_supply_only(self):
        v,h=a.normalize_stablecoin(self.stable(),now_utc=NOW); self.assertEqual(h["status"],"PASS"); self.assertEqual(v["evidence_semantics"]["deployment_confirmation"],"NOT_ESTABLISHED")
    def test_stablecoin_missing_not_zero(self):
        v,h=a.normalize_stablecoin(self.stable(None),now_utc=NOW); self.assertIsNone(v); self.assertEqual(h["status"],"UNAVAILABLE")
    def test_stablecoin_authority_fails(self):
        v,h=a.normalize_stablecoin(self.stable(1,True),now_utc=NOW); self.assertIsNone(v); self.assertEqual(h["classification"],"STABLECOIN_AUTHORITY_ESCALATION")
    def test_crosscheck_independence_and_conflict(self):
        x=a.normalize_crosscheck(.031,.03101,primary_family="BINANCE",crosscheck_family="BINANCE",tolerance_pct=.25); self.assertFalse(x["independent"]); self.assertEqual(x["status"],"AGREE")
        x=a.normalize_crosscheck(100,120,primary_family="A",crosscheck_family="B",tolerance_pct=1); self.assertTrue(x["independent"]); self.assertEqual(x["status"],"TRUE_CONFLICT"); self.assertFalse(x["owner_switch_permitted"])
    def test_crosscheck_missing_and_not_comparable(self):
        self.assertEqual(a.normalize_crosscheck(1,None,primary_family="A",crosscheck_family="B")["status"],"STALE_CROSSCHECK")
        self.assertEqual(a.normalize_crosscheck(None,1,primary_family="A",crosscheck_family="B")["status"],"STALE_PRIMARY")
        self.assertEqual(a.normalize_crosscheck(1,2,primary_family="A",crosscheck_family="B",comparable=False)["status"],"NOT_COMPARABLE")
    def test_etf_finality(self):
        good={"target":{"contract":"DAILY_SETTLED_ETF_CALIBRATION_v2","session_date":"2026-08-31","rows":[{"asset":"BTC","reported_total":216.7,"session_final":True,"total_parity":True},{"asset":"ETH","reported_total":87.6,"session_final":True,"total_parity":True}]}}
        v,h=a.normalize_etf(good,now_utc=NOW); self.assertEqual(h["status"],"PASS"); self.assertEqual(v["btc_reported_total_musd"],216.7)
        good["target"]["rows"][1]["session_final"]=False; v,h=a.normalize_etf(good,now_utc=NOW); self.assertIsNone(v); self.assertIn("NOT_FINAL",h["classification"])
    def test_missing_json_unavailable(self):
        v,h=a.read_json_lane(FakeSnapshot(),"missing.json"); self.assertIsNone(v); self.assertEqual(h["status"],"UNAVAILABLE")
    def test_score_separate_dimensions(self):
        s=a.replacement_score(self.registry(),self.health(),None); self.assertEqual(s["acquisition_automation_pct"],100); self.assertEqual(s["normalization_validation_automation_pct"],100); self.assertEqual(s["decision_context_readiness_pct"],100); self.assertEqual(s["manual_input_residual_pct"],0); self.assertIsNone(s["packet_parity_pct"]); self.assertTrue(s["no_blended_marketing_score"])
        h=self.health(); h["catalyst_context"]={"status":"DEGRADED"}; s=a.replacement_score(self.registry(),h,None); self.assertEqual(s["acquisition_automation_pct"],100); self.assertLess(s["decision_context_readiness_pct"],100)
    def test_replay_parity_separate(self):
        s=a.replacement_score(self.registry(),self.health(),{"packet_parity_pct":91,"packets_replayed":2,"comparable_fields":20}); self.assertEqual(s["packet_parity_pct"],91); self.assertEqual(s["packet_parity_evidence"]["packets"],2)
    def test_delta_missing(self):
        self.assertIsNone(a.delta(1,None)); self.assertEqual(a.delta(2,1)["absolute"],1)
    def test_write_nonbinding(self):
        p={"contract":a.CONTRACT,"packet_generated_at_utc":"2026-09-01T21:00:00Z","packet_sha256":"a"*64,"validation_status":"DEGRADED","source_snapshot":{"exact_commit_sha":"b"*40},"replacement_score":{"manual_input_residual_pct":0},"authority":a.AUTHORITY}
        with tempfile.TemporaryDirectory() as d:
            r=a.write_packet(p,Path(d)); q=json.loads((Path(d)/"LATEST.json").read_text()); self.assertEqual(q["packet_sha256"],"a"*64); self.assertFalse(q["authority"]["portfolio_action"]); self.assertTrue(Path(r["packet_path"]).exists())
    def test_110_deterministic_fail_closed_cases(self):
        for i in range(110):
            m=i%5
            if m==0:x=a.normalize_crosscheck(100,None,primary_family="A",crosscheck_family="B",tolerance_pct=1); e="STALE_CROSSCHECK"
            elif m==1:x=a.normalize_crosscheck(100,100.2,primary_family="A",crosscheck_family="A",tolerance_pct=1); e="AGREE"; self.assertFalse(x["independent"])
            elif m==2:x=a.normalize_crosscheck(100,120,primary_family="A",crosscheck_family="B",tolerance_pct=1); e="TRUE_CONFLICT"
            elif m==3:x=a.normalize_crosscheck(24,26,primary_family="A",crosscheck_family="B",comparable=False); e="NOT_COMPARABLE"
            else:x=a.normalize_crosscheck(None,100,primary_family="A",crosscheck_family="B",tolerance_pct=1); e="STALE_PRIMARY"
            self.assertEqual(x["status"],e); self.assertFalse(x["owner_switch_permitted"])
if __name__=="__main__":unittest.main()
