"""Task2 source-window integrity; synthetic time-and-cost negative controls only."""
import unittest
from datetime import datetime, timezone
from scripts.research import task2_matched_windows_v1 as m

T=int(datetime(2020,9,1,tzinfo=timezone.utc).timestamp()*1000)
def tape(values):
    return [(T+i*m.HOUR_MS,float(v)) for i,v in enumerate(values)]
def continuous(n,era=m.ERA_NAMES[0]):
    return {'era':era,'rows':tape([100]*n)}

class MatchedArchiveTests(unittest.TestCase):
    def test_nonoverlap_fixed_windows_without_outcome_peeking(self):
        cases=m.windows_from_segments([continuous(48+336*2+100)])
        self.assertEqual(len(cases),2)
        self.assertEqual(cases[0]['tape'][48][0],T+48*m.HOUR_MS)
        self.assertEqual(cases[1]['tape'][48][0],T+(48+336)*m.HOUR_MS)
        self.assertEqual(len(cases[0]['tape']),384)
        self.assertEqual(cases[0]['tape'][-1][0]+m.HOUR_MS,cases[1]['tape'][48][0)
    def test_short_segment_and_tail_excluded(self):
        self.assertEqual(len(m.windows_from_segments([continuous(48+335)])),0)
        self.assertEqual(len(m.windows_from_segments([continuous(48+336+335)])),1)
    def test_gap_rejected(self):
        s=continuous(500);s['rows'][123]=(s['rows'][123][0]+m.HOUR_MS,100.)
        with self.assertRaisesRegex(ValueError,'CROSSED_HOURLY_GAP'):m.windows_from_segments([s])
    def test_wrong_era_rejected(self):
        with self.assertRaisesRegex(ValueError,'SOURCE_SEGMENT_ERA'):m.windows_from_segments([continuous(600,era='UNREGISTERED')])
    def test_starting_cash_benchmark_flat_no_signal(self):
        t=tape([100]*384)
        self.assertIsNone(m.first_price_trigger(t,6,.05))
        z=m.evaluate_window(t,None,.25,24,.02)
        self.assertEqual(z['status'],'NO_SIGNAL')
        self.assertEqual(z['delta_vs_hold_pct_initial'],0)
    def test_sale_next_bar_never_signal_bar(self):
        x=[100.]*384;x[48]=90.;x[49]=70.;x[50:]=[100.]*(384-50)
        t=tape(x);j=m.first_price_trigger(t,6,.05)
        self.assertEqual(j,49)
        z=m.evaluate_window(t,j,.50,24,0)
        self.assertTrue(z['sale_attempted'])
        self.assertFalse(z['left_in_cash'])
        self.assertLess(z['delta_vs_hold_pct_initial'],0)
    def test_fixed_reentry_only_after_sale_and_not_at_best_price(self):
        x=[100.]*384;x[48]=94.;x[49]=90.;x[50:]=[50.]*(384-50)
        t=tape(x);j=m.first_price_trigger(t,6,.05)
        self.assertEqual(j,49)
        a=m.evaluate_window(t,j,.50,24,0)
        self.assertTrue(a['reentered'])
        self.assertGreater(a['delta_vs_hold_pct_initial'],0)
    def test_cost_monotone_given_identical_schedule(self):
        x=[100.]*384;x[48]=90;x[49]=80;x[80]=95;x[100:]=[90.]*(384-100)
        t=tape(x);j=m.first_price_trigger(t,6,.05)
        vals=[m.evaluate_window(t,j,.25,24,c)['delta_vs_hold_pct_initial'] for c in (0,.003,.01,.02)]
        self.assertEqual(vals,sorted(vals,reverse=True))
    def test_false_exit_and_fee_penalty(self):
        x=[100.]*384;x[48]=90;x[49]=90;x[50:]=[120.]*(384-50)
        t=tape(x);j=m.first_price_trigger(t,6,.05)
        a=m.evaluate_window(t,j,.50,24,0)
        b=m.evaluate_window(t,j,.50,24,.02)
        self.assertLess(b['delta_vs_hold_pct_initial'],a['delta_vs_hold_pct_initial'])
    def test_missing_reentry_leaves_cash_not_fake_fill(self):
        s=m.evaluate_window(tape([100.]*384),382,.25,168,.003)
        self.assertTrue(s['left_in_cash'])
        self.assertFalse(s['reentered'])
    def test_invalid_earlier_sale_rejected(self):
        with self.assertRaisesRegex(ValueError,'SALE_BEFORE_KNOWLEDGE'):
            m.evaluate_window(tape([100]*384),48,.25,24,0)
    def test_nonfinite_price_rejected(self):
        arr=[100.]*384;arr[57]=float('nan')
        with self.assertRaisesRegex(ValueError,'INVALID_PRICE_TAPE'):
            m.evaluate_window(tape(arr),57,.25,24,0)
    def test_no_future_price_used_to_choose_first_trigger(self):
        x=[100.]*384;x[48]=94;x[49]=100
        a=m.first_price_trigger(tape(x),6,.05)
        x[100]=10000
        b=m.first_price_trigger(tape(x),6,.05)
        self.assertEqual(a,b)
    def test_trim_zero_not_permitted(self):
        with self.assertRaisesRegex(ValueError,'BAD_FROZEN_EXECUTION_CONFIG'):
            m.evaluate_window(tape([100.]*384),49,0,24,.003)
    def test_window_len_and_warmup_frozen(self):
        self.assertEqual((m.WINDOW_HOURS,m.WARMUP_HOURS),(336,48))
    def test_no_promise_of_independent_edge(self):
        self.assertIn('NOT_PIT_NOT_EDGE',m.CLASSIFICATION)

if __name__ == '__main__':
    unittest.main()
