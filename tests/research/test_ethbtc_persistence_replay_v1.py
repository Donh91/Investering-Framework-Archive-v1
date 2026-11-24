import unittest
from datetime import datetime, timedelta, timezone
from scripts.research.ethbtc_persistence_replay_v1 import replay, verify_window_inputs, METHOD

START = datetime(2026, 11, 1, tzinfo=timezone.utc)
H = timedelta(hours=1)
CUTOFF = START+169*H


def window(n=7, side=0.031):
    return [{"ts": START+i*H, "available": START+(i+1)*H,
             "ethbtc": side if i >= 168-n else 0.029} for i in range(168)]


def inputs(w):
    r = replay(w, CUTOFF)
    return dict(lookback_rows=168, sample_count=168, continuous_hours=168,
                window_start_utc=r['window_start_utc'], window_end_utc=r['window_end_utc'],
                consecutive_same_side=r['consecutive_same_side'], method=METHOD)


class ReplayTests(unittest.TestCase):
    def test_seven_hours_and_crossing(self):
        r = replay(window(), CUTOFF)
        self.assertEqual(r['consecutive_same_side'], 7)
        self.assertEqual(r['first_above_bar_utc'], (START+161*H).isoformat().replace('+00:00','Z'))
        self.assertFalse(r['left_censored'])
    def test_same_latest_different_persistence(self):
        self.assertNotEqual(replay(window(7), CUTOFF)['consecutive_same_side'], replay(window(11), CUTOFF)['consecutive_same_side'])
    def test_censored(self):
        r = replay(window(168), CUTOFF)
        self.assertTrue(r['left_censored'])
        self.assertIsNone(r['first_above_bar_utc'])
        self.assertEqual(r['consecutive_same_side'],168)
    def test_below_and_equal(self):
        self.assertEqual(replay(window(168,0.029), CUTOFF)['side'],'BELOW')
        self.assertEqual(replay(window(7,0.03), CUTOFF)['side'],'AT')
    def test_no_authority_or_invented_confirmation(self):
        r = replay(window(), CUTOFF)
        self.assertIsNone(r['stable_confirmation_utc'])
        self.assertIsNone(r['independent_first_known_utc'])
        self.assertFalse(r['scientific_pit_eligible'])
        self.assertFalse(r['forecast_authority'])
    def test_source_clock_not_bar_clock(self):
        w = window()
        w[-7]['available'] += H
        r = replay(w,CUTOFF)
        self.assertNotEqual(r['first_above_source_window_end_utc'],r['first_above_bar_utc'])
    def test_missing_duplicate_and_disordered(self):
        w = window()
        for invalid in [w[:-1], w[:5]+[w[4]]+w[6:], w[:5]+[w[6],w[5]]+w[7:]]:
            with self.subTest(invalid=len(invalid)), self.assertRaises(ValueError):
                replay(invalid,CUTOFF)
    def test_future_or_unsettled_source(self):
        for a in [CUTOFF+H, window()[-1]['ts']]:
            w=window(); w[-1]['available']=a
            with self.assertRaises(ValueError): replay(w,CUTOFF)
    def test_nonfinite_and_nonpositive(self):
        for value in [float('nan'),float('inf'),0,-1,True,'0.031']:
            w=window(); w[0]['ethbtc']=value
            with self.subTest(value=value), self.assertRaises(ValueError): replay(w,CUTOFF)
    def test_forged_duration(self):
        w=window(); p=inputs(w); p['consecutive_same_side']=168
        with self.assertRaisesRegex(ValueError,'consecutive_same_side'): verify_window_inputs(w,CUTOFF,p)
    def test_forged_type(self):
        w=window(1); p=inputs(w); p['consecutive_same_side']=True
        with self.assertRaisesRegex(ValueError,'consecutive_same_side'): verify_window_inputs(w,CUTOFF,p)
    def test_missing_and_mutated_metadata(self):
        w=window()
        for key in inputs(w):
            p=inputs(w); p.pop(key)
            with self.subTest(key=key), self.assertRaises(ValueError): verify_window_inputs(w,CUTOFF,p)
    def test_valid(self):
        w=window(); self.assertEqual(verify_window_inputs(w,CUTOFF,inputs(w))['consecutive_same_side'],7)

if __name__=='__main__': unittest.main()
