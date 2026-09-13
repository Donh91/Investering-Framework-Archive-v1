"""AT-EXP-004 composition controls. Replay excludes only source_window_end_utc:
this is the declared retrieval-window boundary, not market evidence/detection time.
"""
import csv
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from scripts.daily_capture import build_hourly_sequence as h
from scripts.data_terminal import situation_room_daily_owner as sr

START = datetime(2026, 9, 1, tzinfo=timezone.utc)

def panel(n=48):
    spot, oi = {}, {}
    for symbol in h.SPOT_SYMBOLS:
        spot[symbol] = {}
        for i in range(n):
            spot[symbol][h.to_ms(START + timedelta(hours=i))] = dict(open=90+i, high=110+i, low=80+i, close=100+i, volume=3, quote_volume=300, trade_count=5, taker_buy_base_volume=1, taker_buy_quote_volume=100, taker_sell_quote_volume=200, taker_buy_quote_share=1/3)
    for symbol, _, _ in h.DERIVATIVE_SYMBOLS:
        oi[symbol] = {h.to_ms(START+timedelta(hours=i)): {'oi': 1000+i, 'value': 2000+i, 'source': 'FIXTURE'} for i in range(n)}
    return spot, oi

def build(a, b):
    spot, oi = panel()
    return h.build_rows(START+timedelta(hours=a), START+timedelta(hours=b), spot, oi, {}, {}, 'PASS', 'PASS')

def read(root):
    rows = []
    for path in sorted(root.glob('2026/*/*.csv')):
        with path.open() as f:
            rows.extend(csv.DictReader(f))
    return {r['timestamp_utc']: r for r in rows}

class PersistenceTests(unittest.TestCase):
    def test_missing_previous_close_and_first_degraded(self):
        row = build(1, 1)[0]
        self.assertIsNone(row['btc_return_1h_pct'])
        self.assertEqual(row['btc_price_oi_state'], '')
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); h.merge_rows(root, [row]); saved=next(iter(read(root).values()))
            self.assertEqual(saved['btc_price_oi_state'], '')
            self.assertEqual(saved['btc_return_1h_pct'], '')
            self.assertEqual(saved['btc_open'], '91')

    def test_good_degraded_both_orders_and_equal_quality(self):
        good, bad = build(0, 1)[1], build(1, 1)[0]
        self.assertNotIn(good['btc_price_oi_state'], ('', 'UNAVAILABLE'))
        for rows in ([good, bad], [bad, good]):
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as td:
                root=Path(td)
                for row in rows: h.merge_rows(root,[row])
                saved=read(root)[good['timestamp_utc']]
                self.assertEqual(saved, {f:h.fmt(good.get(f)) for f in h.FIELDS})
                changed=dict(good, btc_close=999, source_window_end_utc='2026-09-02T00:00:00Z')
                h.merge_rows(root,[changed]); self.assertEqual(read(root)[good['timestamp_utc']],saved)
                receipts=list((root/'superseded').glob('*.json')); self.assertTrue(receipts)
                h.merge_rows(root,[changed]); self.assertEqual(len(list((root/'superseded').glob('*.json'))),len(receipts))

    def test_two_schedule_replay_all_common_market_fields(self):
        archives=[]
        for cadence in (1,6):
            with tempfile.TemporaryDirectory() as td:
                root=Path(td)
                for end in range(5,48,cadence):
                    h.merge_rows(root,build(max(0,end-25),end))
                archives.append(read(root))
        common=set(archives[0]) & set(archives[1]); self.assertGreater(len(common),40)
        for key in common:
            a,b=archives[0][key],archives[1][key]
            self.assertEqual({f:v for f,v in a.items() if f!='source_window_end_utc'}, {f:v for f,v in b.items() if f!='source_window_end_utc'})
            for prefix in ('btc','eth'):
                if a[prefix+'_return_1h_pct'] and a[prefix+'_oi_change_1h_pct']:
                    self.assertNotIn(a[prefix+'_price_oi_state'], ('','UNAVAILABLE'))

    def test_situation_room_downgrade_upgrade_tie_and_audit(self):
        good=dict(observation_date_utc='2026-09-01',detection_time_utc='2026-09-01T12:00:00Z',run_status='PASS',daily_result='NO_NEW_MATERIAL_CATALYST',run_id='good',events=[])
        bad=dict(good,run_status='DEGRADED',run_id='bad',detection_time_utc='2026-09-01T13:00:00Z',events=[{'event_id':'REJECTED'}])
        for pair in ([good,bad],[bad,good]):
            with tempfile.TemporaryDirectory() as td:
                root=Path(td)
                for r in pair: sr.write_outputs(root,r)
                dated=root/'2026/09/2026-09-01.json'; self.assertEqual(json.loads(dated.read_text()),good)
                before=dated.read_bytes(); ledger=(root/'EVENT_LEDGER.jsonl').read_bytes(); pointer=(root/'LATEST.json').read_bytes()
                sr.write_outputs(root,bad)
                self.assertEqual(dated.read_bytes(),before); self.assertEqual((root/'EVENT_LEDGER.jsonl').read_bytes(),ledger); self.assertEqual((root/'LATEST.json').read_bytes(),pointer)
                self.assertTrue(list((root/'superseded').glob('*.json')))
                later=dict(good,run_id='later',detection_time_utc='2026-09-01T14:00:00Z')
                sr.write_outputs(root,later); self.assertEqual(json.loads(dated.read_text()),later)
                for stamp in ('garbage','2026-09-01T16:00:00','2026-09-01T11:00:00Z'):
                    sr.write_outputs(root,dict(good,detection_time_utc=stamp))
                    self.assertEqual(json.loads(dated.read_text()),later)
