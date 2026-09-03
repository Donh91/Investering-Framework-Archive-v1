from __future__ import annotations
import json, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / 'scripts' / 'learning' / 'build_model_calibration_ledger.py'

class ForecastSettlementScopeT13Test(unittest.TestCase):
    def test_settlement_eligibility_never_claims_skill_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); frozen=root/'FROZEN'; matured=root/'MATURED'; frozen.mkdir(); matured.mkdir()
            forecast={'contract':'FROZEN_FORECAST_v1','unit_contract_version':'FORECAST_TARGET_UNITS_v2','forecast_id':'f1','candidate_id':'c1','direction':'UP','metric_path':'spot.BTCUSDT.close','horizon_days':1}
            outcome={'contract':'MATURED_OUTCOME_v3','forecast_id':'f1','status':'MATURED','result':'HIT','created_at_utc':'2026-09-05T00:00:00Z','scientific_score_eligible':True,'settlement_contract_version':'FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1','settlement_target_utc':'2026-09-05T00:00:00Z','settlement_observation_utc':'2026-09-05T00:00:00Z','settlement_offset_seconds':0.0}
            (frozen/'f1.json').write_text(json.dumps(forecast)); (matured/'f1.json').write_text(json.dumps(outcome))
            output=root/'ledger.csv'; sidecar=root/'eligibility.json'
            proc=subprocess.run([sys.executable,str(LEDGER),'--forecast-root',str(frozen),'--outcome-root',str(matured),'--output',str(output),'--eligibility-output',str(sidecar)],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            doc=json.loads(sidecar.read_text()); row=doc['rows'][0]
            self.assertEqual(doc['eligibility_scope'],'SETTLEMENT_TIMING_ONLY')
            self.assertEqual(doc['scientific_skill_status'],'NOT_ASSESSED_SETTLEMENT_TIMING_ONLY')
            self.assertFalse(doc['scientific_skill_authority'])
            self.assertFalse(doc['authority']['forecast_skill_claim'])
            self.assertTrue(row['settlement_score_eligible'])
            self.assertFalse(row['scientific_skill_eligible'])

if __name__ == '__main__': unittest.main()
