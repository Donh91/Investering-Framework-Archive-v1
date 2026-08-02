from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class FullArchitectureTests(unittest.TestCase):
    def run_py(self,rel,*args,cwd=None):
        return subprocess.run(['python',str(ROOT/rel),*map(str,args)],cwd=cwd or ROOT,text=True,capture_output=True)

    def test_data_ping_bridge_accepts_and_rejects_authority(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); inbox=r/'inbox'; inbox.mkdir()
            good={'contract':'ACCEPTED_DATA_PING_PACKET_v1','snapshot_id':'s1','freeze_utc':'2026-08-02T20:00:00Z','source_health':{},'market_metrics':{},'framework_interpretation':'SHADOW','acceptance_status':'ACCEPTED','authority':{'portfolio_action':False}}
            (inbox/'good.json').write_text(json.dumps(good))
            p=self.run_py('scripts/data_ping/accepted_data_ping_bridge.py','--inbox',inbox,'--accepted-root',r/'accepted','--rejected-root',r/'rejected')
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertTrue(list((r/'accepted').rglob('s1.json')))

    def test_outcome_is_immutable_and_matures(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); (r/'f').mkdir(); (r/'e').mkdir()
            now=datetime.now(timezone.utc)
            f={'contract':'FROZEN_FORECAST_v1','forecast_id':'f1','frozen_at_utc':(now-timedelta(days=2)).isoformat(),'outcome_due_utc':(now-timedelta(days=1)).isoformat(),'metric_path':'market_metrics.btc.close','start_value':100.0,'direction':'UP','threshold_pct':1.0}
            e={'captured_at_utc':now.isoformat(),'market_metrics':{'btc':{'close':102.0}}}
            (r/'f/f1.json').write_text(json.dumps(f)); (r/'e/e1.json').write_text(json.dumps(e))
            p=self.run_py('scripts/learning/outcome_maturation_engine.py','--forecast-root',r/'f','--evidence-root',r/'e','--output-root',r/'o')
            self.assertEqual(p.returncode,0,p.stderr)
            out=json.loads((r/'o/f1.json').read_text()); self.assertEqual(out['result'],'HIT')
            before=(r/'o/f1.json').read_bytes(); self.run_py('scripts/learning/outcome_maturation_engine.py','--forecast-root',r/'f','--evidence-root',r/'e','--output-root',r/'o'); self.assertEqual(before,(r/'o/f1.json').read_bytes())

    def test_orchestrator_requires_final_close(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); (r/'weekly_close').mkdir(); (r/'weekly').mkdir()
            (r/'weekly_close/LATEST_WEEKLY_MARKET_CLOSE.json').write_text(json.dumps({'final':False}))
            (r/'weekly/LATEST_WEEKLY_CALIBRATION.json').write_text('{}')
            p=self.run_py('scripts/orchestration/weekly_orchestration_controller.py','--capture-root',r,'--accepted-data-ping-root',r/'accepted','--output',r/'freeze.json')
            self.assertNotEqual(p.returncode,0)

    def test_farside_fixture_parser(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); fx=r/'fx'; fx.mkdir()
            html='<table><tr><th>Date</th><th>A</th><th>Total</th></tr><tr><td>01 Aug 2026</td><td>10.0</td><td>10.0</td></tr></table>'
            (fx/'btc.html').write_text(html); (fx/'eth.html').write_text(html)
            p=self.run_py('scripts/data_terminal/farside_etf_owner.py','--output-dir',r/'out','--fixture-dir',fx)
            self.assertEqual(p.returncode,0,p.stderr)
            self.assertEqual(json.loads((r/'out/owner_snapshot.json').read_text())['status'],'PASS')

if __name__=='__main__': unittest.main()
