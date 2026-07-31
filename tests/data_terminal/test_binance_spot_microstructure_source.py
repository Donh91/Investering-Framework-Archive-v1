from __future__ import annotations
import importlib.util,json,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; P=ROOT/'scripts/data_terminal/binance_spot_microstructure_source.py'; S=importlib.util.spec_from_file_location('micro',P); m=importlib.util.module_from_spec(S); sys.modules[S.name]=m; S.loader.exec_module(m); FIX=Path(__file__).parent/'fixtures/binance_spot_owner'
class Tests(unittest.TestCase):
 def payloads(self): return {s:{'depth':(FIX/f'{s}_depth.json').read_bytes(),'aggTrades':(FIX/f'{s}_aggTrades.json').read_bytes()} for s in m.SYMBOLS}
 def test_capture_and_readback(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); o=m.run(self.payloads(),root,'2026-07-31T12:00:00Z'); self.assertFalse(o['authority']['binding']); self.assertFalse(o['data']['BTCUSDT']['depth']['replenishment_available']); self.assertLess(o['data']['BTCUSDT']['agg_trades']['taker_quote_imbalance'],0); self.assertEqual(m.verify(root)['status'],'PASS'); self.assertEqual((root/'raw'/'BTCUSDT_depth.json').read_bytes(),self.payloads()['BTCUSDT']['depth'])
 def test_crossed_book_rejected(self):
  with self.assertRaises(m.SourceError) as c: m.parse_depth(json.dumps({'lastUpdateId':1,'bids':[['2','1']],'asks':[['1','1']]}).encode(),'BTCUSDT')
  self.assertEqual(c.exception.status,'CROSSED_BOOK')
 def test_duplicate_trade_rejected(self):
  rows=json.loads(self.payloads()['BTCUSDT']['aggTrades']); rows.append(rows[0])
  with self.assertRaises(m.SourceError) as c: m.parse_trades(json.dumps(rows).encode(),'BTCUSDT')
  self.assertEqual(c.exception.status,'DUPLICATE_TRADE_ID')
 def test_geo_restriction_explicit(self):
  with self.assertRaises(m.SourceError) as c: m.parse_trades(b'{"code":0,"msg":"Service unavailable from a restricted location"}','BTCUSDT')
  self.assertEqual(c.exception.status,'GEO_RESTRICTED')
 def test_tamper_detected(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); m.run(self.payloads(),root,'2026-07-31T12:00:00Z'); (root/'owner_snapshot.json').write_text('{}'); self.assertEqual(m.verify(root)['status'],'FAIL')
if __name__=='__main__': unittest.main()
