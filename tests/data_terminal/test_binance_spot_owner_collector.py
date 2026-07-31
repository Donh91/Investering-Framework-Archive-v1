from __future__ import annotations
import importlib.util, json, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'scripts/data_terminal/binance_spot_owner_collector.py'
S=importlib.util.spec_from_file_location('binance_spot_owner',P); m=importlib.util.module_from_spec(S); sys.modules[S.name]=m; S.loader.exec_module(m)
FIX=Path(__file__).parent/'fixtures/binance_spot_owner'

class Tests(unittest.TestCase):
 def payloads(self): return {s:(FIX/f'{s}.json').read_bytes() for s in m.SYMBOLS}
 def test_fixture_materializes_direct_owner(self):
  with tempfile.TemporaryDirectory() as t:
   o=m.run(self.payloads(),Path(t),'2026-07-31T12:00:00Z','1h')
   self.assertTrue(o['direct_ethbtc']); self.assertFalse(o['interpolation']); self.assertEqual(set(o['candles']),set(m.SYMBOLS)); self.assertEqual(m.verify(Path(t))['status'],'PASS')
 def test_raw_payloads_preserved(self):
  with tempfile.TemporaryDirectory() as t:
   m.run(self.payloads(),Path(t),'2026-07-31T12:00:00Z','1h')
   for s,b in self.payloads().items(): self.assertEqual((Path(t)/'raw'/f'{s}.json').read_bytes(),b)
 def test_duplicate_rejected(self):
  rows=json.loads(self.payloads()['BTCUSDT']); rows.append(rows[0])
  with self.assertRaises(m.CollectorError) as c: m.parse(json.dumps(rows).encode(),'BTCUSDT')
  self.assertEqual(c.exception.status,'DUPLICATE_TIMESTAMP')
 def test_schema_drift_rejected(self):
  with self.assertRaises(m.CollectorError) as c: m.parse(b'{"code":-1,"msg":"bad"}','BTCUSDT')
  self.assertEqual(c.exception.status,'SOURCE_ERROR')
 def test_geo_restriction_explicit(self):
  with self.assertRaises(m.CollectorError) as c: m.parse(b'{"code":0,"msg":"Service unavailable from a restricted location"}','BTCUSDT')
  self.assertEqual(c.exception.status,'GEO_RESTRICTED')
 def test_tamper_detected(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); m.run(self.payloads(),root,'2026-07-31T12:00:00Z','1h'); (root/'owner_snapshot.json').write_text('{}')
   self.assertEqual(m.verify(root)['status'],'FAIL')
 def test_no_zero_or_null_invented(self):
  candles=m.parse(self.payloads()['ETHBTC'],'ETHBTC')
  self.assertTrue(all(c['close']>0 for c in candles)); self.assertTrue(all(c['closed'] is True for c in candles))
if __name__=='__main__': unittest.main()
