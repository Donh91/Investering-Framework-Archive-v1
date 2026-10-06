import unittest
from scripts.experiments.derivatives_crowding_features_v1 import build_vector,HOUR_MS

BASE=1791273600000

def capture(*,spot_sign=1,fut_sign=1,oi_sign=1,price_sign=1):
    # 25 completed hourly rows ending one hour before BASE, plus one deliberately
    # incomplete/future raw row that the cutoff must ignore.
    spot=[];oi=[];fut=[];basis=[]
    for age in range(25,-1,-1):
        ts=BASE-HOUR_MS-age*HOUR_MS
        step=25-age
        close=100.0 + price_sign*step
        oiv=1000.0 + oi_sign*step*5
        q=1000.0
        # +/- 10% normalized spot imbalance.
        tq=q*(0.55 if spot_sign>0 else 0.45)
        spot.append({'timestamp_ms':ts,'close':close,'quote_volume':q,'taker_buy_quote_volume':tq})
        oi.append({'timestamp_ms':ts,'open_interest_value':oiv})
        fut.append({'timestamp_ms':ts,'buy_volume':110.0 if fut_sign>0 else 90.0,'sell_volume':90.0 if fut_sign>0 else 110.0})
        basis.append({'timestamp_ms':ts,'basis_rate':0.001})
    return {
      'contract':'DERIVATIVES_HOURLY_SOURCE_CAPTURE_V1','source_id':'FIXTURE','venue':'TEST','symbol':'TESTUSDT',
      'decision_cutoff_utc':'2026-10-06T08:00:00Z',
      'spot_hourly':spot,'oi_hourly':oi,'futures_taker_hourly':fut,'basis_hourly':basis,
      'funding_events':[
        {'timestamp_ms':BASE-8*HOUR_MS,'funding_rate':0.0001},
        {'timestamp_ms':BASE+1,'funding_rate':0.5}
      ]
    }

class DerivativesCrowdingV1Tests(unittest.TestCase):
    def test_full_windows_and_future_funding_excluded(self):
        out=build_vector(capture())
        self.assertEqual(out['latest_funding_rate'],0.0001)
        self.assertEqual(out['windows']['24h']['row_count'],24)
        self.assertFalse(out['thresholds_tuned'])
        self.assertFalse(out['compass_authority'])

    def test_incomplete_current_hour_is_ignored(self):
        d=capture()
        # Last raw row is timestamp BASE and deliberately absurd.
        d['spot_hourly'][-1]['close']=999999
        d['oi_hourly'][-1]['open_interest_value']=999999
        out=build_vector(d)
        self.assertLess(out['windows']['1h']['price_return_pct'],10)
        self.assertLess(out['windows']['1h']['oi_value_delta_pct'],10)

    def test_spot_imbalance_formula(self):
        out=build_vector(capture())
        self.assertAlmostEqual(out['windows']['4h']['spot_taker_imbalance'],0.1)
        self.assertAlmostEqual(out['windows']['4h']['futures_taker_imbalance'],0.1)

    def test_broad_risk_on_tag_is_descriptive_only(self):
        out=build_vector(capture(spot_sign=1,fut_sign=1,oi_sign=1,price_sign=1))
        self.assertIn('BROAD_RISK_ON_COMPATIBLE',out['windows']['4h']['compatibility_tags'])
        self.assertFalse(out['interpretation_boundary']['warning_state_created'])

    def test_leverage_led_and_distribution_can_overlap(self):
        out=build_vector(capture(spot_sign=-1,fut_sign=1,oi_sign=1,price_sign=1))
        tags=out['windows']['4h']['compatibility_tags']
        self.assertIn('LEVERAGE_LED_PUMP_COMPATIBLE',tags)
        self.assertIn('DISTRIBUTION_INTO_LEVERAGED_LONGS_FLOW_COMPATIBLE',tags)

    def test_broad_weakness(self):
        out=build_vector(capture(spot_sign=-1,fut_sign=-1,oi_sign=-1,price_sign=-1))
        self.assertIn('BROAD_WEAKNESS_COMPATIBLE',out['windows']['12h']['compatibility_tags'])

    def test_healthy_deleveraging(self):
        out=build_vector(capture(spot_sign=1,fut_sign=-1,oi_sign=-1,price_sign=1))
        self.assertIn('HEALTHY_DELEVERAGING_COMPATIBLE',out['windows']['4h']['compatibility_tags'])

    def test_missing_window_fails_window_not_whole_capture(self):
        d=capture()
        target=BASE-HOUR_MS-12*HOUR_MS
        d['spot_hourly']=[r for r in d['spot_hourly'] if r['timestamp_ms']!=target]
        out=build_vector(d)
        self.assertEqual(out['windows']['12h']['state'],'INSUFFICIENT_WINDOW')
        self.assertEqual(out['windows']['4h']['state'],'COMPLETE')

if __name__=='__main__':unittest.main()
