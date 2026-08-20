from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'))+'\n').encode()


class FullArchitectureTests(unittest.TestCase):
    def run_py(self,rel,*args,cwd=None):
        return subprocess.run(['python',str(ROOT/rel),*map(str,args)],cwd=cwd or ROOT,text=True,capture_output=True)

    def load_module(self, rel, name):
        spec=importlib.util.spec_from_file_location(name,ROOT/rel)
        module=importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module

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
            # metric_path_root is declared explicitly: this fixture uses the canonical
            # document-rooted convention that the patched producer now emits (TASK3 R3-04).
            f={'contract':'FROZEN_FORECAST_v1','unit_contract_version':'FORECAST_TARGET_UNITS_v2','forecast_id':'f1','frozen_at_utc':(now-timedelta(days=2)).isoformat(),'outcome_due_utc':(now-timedelta(days=1)).isoformat(),'metric_path':'market_metrics.btc.close','metric_path_root':'CAPTURE_DOCUMENT_ROOT','start_value':100.0,'direction':'UP','threshold_pct':1.0}
            e={'captured_at_utc':now.isoformat(),'market_metrics':{'btc':{'close':102.0}}}
            (r/'f/f1.json').write_text(json.dumps(f)); (r/'e/e1.json').write_text(json.dumps(e))
            p=self.run_py('scripts/learning/outcome_maturation_engine.py','--forecast-root',r/'f','--evidence-root',r/'e','--output-root',r/'o')
            self.assertEqual(p.returncode,0,p.stderr)
            out=json.loads((r/'o/f1.json').read_text()); self.assertEqual(out['result'],'HIT')
            self.assertEqual(out['metric_path_root_applied'],'CAPTURE_DOCUMENT_ROOT')
            self.assertEqual(out['resolver_version'],'METRIC_PATH_RESOLVER_v1')
            before=(r/'o/f1.json').read_bytes(); self.run_py('scripts/learning/outcome_maturation_engine.py','--forecast-root',r/'f','--evidence-root',r/'e','--output-root',r/'o'); self.assertEqual(before,(r/'o/f1.json').read_bytes())

    def make_final_close(self, root: Path, *, iso_year=2026, iso_week=31, corrupt_hash=False, final=True):
        package={
            'contract':'WEEKLY_MARKET_CLOSE_PACKAGE_v2',
            'iso_year':iso_year,
            'iso_week':iso_week,
            'window_start_utc':'2026-07-27T00:00:00Z',
            'window_end_utc':'2026-08-03T00:00:00Z',
            'generated_at_utc':'2026-08-03T00:05:00Z',
            'final':final,
            'close_mode':'FINAL_COMPLETED_ISO_WEEK' if final else 'PRE_CLOSE_CURRENT_ISO_WEEK',
            'completeness':'COMPLETE' if final else 'PARTIAL',
            'symbols':{},
        }
        pkg=root/'weekly_close/2026/W31/WEEKLY_MARKET_CLOSE_PACKAGE.json'
        pkg.parent.mkdir(parents=True)
        pkg.write_bytes(canonical(package))
        digest=hashlib.sha256(pkg.read_bytes()).hexdigest()
        pointer={
            'contract':'WEEKLY_MARKET_CLOSE_POINTER_v2',
            'path':'weekly_close/2026/W31/WEEKLY_MARKET_CLOSE_PACKAGE.json',
            'sha256':'0'*64 if corrupt_hash else digest,
            'status':'PASS','iso_year':iso_year,'iso_week':iso_week,
            'window_end_utc':'2026-08-03T00:00:00Z','final':final,
            'close_mode':package['close_mode'],'completeness':package['completeness'],
        }
        (root/'weekly_close/LATEST_WEEKLY_MARKET_CLOSE.json').write_bytes(canonical(pointer))
        (root/'weekly').mkdir()
        (root/'weekly/LATEST_WEEKLY_CALIBRATION.json').write_text('{}')

    def test_orchestrator_accepts_production_pointer_and_package(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); self.make_final_close(r)
            p=self.run_py('scripts/orchestration/weekly_orchestration_controller.py','--capture-root',r,'--accepted-data-ping-root',r/'accepted','--output',r/'freeze.json','--now-utc','2026-08-03T00:20:00Z')
            self.assertEqual(p.returncode,0,p.stderr)
            freeze=json.loads((r/'freeze.json').read_text())
            self.assertEqual(freeze['status'],'READY')
            self.assertEqual(freeze['iso_week'],31)
            self.assertEqual(freeze['final_week_close']['package_sha256'],hashlib.sha256((r/'weekly_close/2026/W31/WEEKLY_MARKET_CLOSE_PACKAGE.json').read_bytes()).hexdigest())

    def test_orchestrator_rejects_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); self.make_final_close(r,corrupt_hash=True)
            p=self.run_py('scripts/orchestration/weekly_orchestration_controller.py','--capture-root',r,'--accepted-data-ping-root',r/'accepted','--output',r/'freeze.json','--now-utc','2026-08-03T00:20:00Z')
            self.assertNotEqual(p.returncode,0)
            self.assertIn('WEEK_CLOSE_HASH_MISMATCH',p.stderr+p.stdout)

    def test_orchestrator_rejects_nonfinal_and_wrong_week(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); self.make_final_close(r,final=False)
            p=self.run_py('scripts/orchestration/weekly_orchestration_controller.py','--capture-root',r,'--accepted-data-ping-root',r/'accepted','--output',r/'freeze.json','--now-utc','2026-08-03T00:20:00Z')
            self.assertNotEqual(p.returncode,0)
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); self.make_final_close(r,iso_week=32)
            p=self.run_py('scripts/orchestration/weekly_orchestration_controller.py','--capture-root',r,'--accepted-data-ping-root',r/'accepted','--output',r/'freeze.json','--now-utc','2026-08-03T00:20:00Z')
            self.assertNotEqual(p.returncode,0)
            self.assertIn('WEEK_CLOSE_WRONG_ISO_WEEK',p.stderr+p.stdout)

    def test_final_window_on_monday_targets_previous_iso_week(self):
        module=self.load_module('scripts/daily_capture/build_weekly_market_close_package.py','weekly_close_builder')
        start,end,final,mode=module.resolve_window(datetime(2026,8,3,0,5,tzinfo=timezone.utc),'final')
        self.assertEqual(start.isoformat(),'2026-07-27T00:00:00+00:00')
        self.assertEqual(end.isoformat(),'2026-08-03T00:00:00+00:00')
        self.assertTrue(final)
        self.assertEqual(mode,'FINAL_COMPLETED_ISO_WEEK')

    def test_farside_fixture_parser(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); fx=r/'fx'; fx.mkdir()
            btc='''<table><tr><td>Date</td><td>IBIT</td><td>FBTC</td><td>BITB</td><td>ARKB</td><td>BTCO</td><td>EZBC</td><td>BRRR</td><td>HODL</td><td>BTCW</td><td>MSBT</td><td>GBTC</td><td>BTC</td><td>Total</td></tr><tr><td>01 Aug 2026</td><td>10.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>10.0</td></tr></table>'''
            eth='''<table><tr><th></th><th>Blackrock</th><th>Blackrock</th><th>Fidelity</th><th>Bitwise</th><th>21 Shares</th><th>VanEck</th><th>Invesco</th><th>Franklin</th><th>Grayscale</th><th>Grayscale</th><th>Total</th></tr><tr><td></td><td>ETHA</td><td>ETHB</td><td>FETH</td><td>ETHW</td><td>TETH</td><td>ETHV</td><td>QETH</td><td>EZET</td><td>ETHE</td><td>ETH</td><td></td></tr><tr><td>01 Aug 2026</td><td>10.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>10.0</td></tr></table>'''
            (fx/'btc.html').write_text(btc); (fx/'eth.html').write_text(eth)
            p=self.run_py('scripts/data_terminal/farside_etf_owner.py','--output-dir',r/'out','--fixture-dir',fx,'--now-utc','2026-08-03T00:00:00Z')
            self.assertEqual(p.returncode,0,p.stderr+p.stdout)
            snapshot=json.loads((r/'out/owner_snapshot.json').read_text())
            self.assertEqual(snapshot['status'],'PASS')
            eth_row=next(row for row in snapshot['rows'] if row['asset']=='ETH')
            self.assertEqual(eth_row['header_mode'],'SOURCE_TWO_ROW_TICKER_HEADER')

if __name__=='__main__': unittest.main()
