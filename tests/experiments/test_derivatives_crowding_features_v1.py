import unittest
from scripts.experiments.derivatives_crowding_features_v1 import build_vector,HOUR_MS

BASE=1791273600000

def capture(*,spot_sign=1,fut_sign=1,oi_sign=1,price_sign=1):
    # 25 completed hourly rows ending one hour before BASE, plus one deliberately
    # incomplete/future raw row that the cutoff must ignore.
    spot=[];oi=[];fut=[];basis=[]
    for step in range(26):
        ts=BASE-25*HOUR_MS+step*HOUR_MS
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


from scripts.research.s5_source_clock_census_v1 import census_capture
from copy import deepcopy


class S5SourceClockCensusV1Tests(unittest.TestCase):
    def test_replay_complete_is_not_pit_or_edge(self):
        out=census_capture(capture(),source_blob_sha="fixture-blob")
        self.assertEqual(out["capability_24h_window_state"],"COMPLETE")
        self.assertEqual(out["source_clock_state"],"UNVERIFIED_FIRST_KNOWN")
        self.assertEqual(out["economic_edge_claim"],"NOT_ESTIMABLE")
        self.assertFalse(out["prospective_pit_admitted"])
        self.assertEqual(out["series"]["funding_events"]["rows_at_or_after_cutoff"],1)

    def test_missing_baseline_detected(self):
        data=capture()
        data["spot_hourly"].pop(0)
        self.assertEqual(census_capture(data)["capability_24h_window_state"],"MISSING_INPUT_WINDOW")

    def test_self_declared_first_known_cannot_certify(self):
        data=capture()
        data["provenance"]={"captured_at_utc":"2026-10-06T07:59:59Z"}
        for name in ("spot_hourly","oi_hourly","futures_taker_hourly","basis_hourly"):
            for row in data[name]:
                row["source_first_known_utc"]="2026-10-05T00:00:00Z"
                row["retrieved_at_utc"]="2026-10-06T07:59:59Z"
        out=census_capture(data)
        self.assertGreater(out["source_publication_clocks_declared"],0)
        self.assertFalse(out["independent_provider_first_known_verified"])
        self.assertFalse(out["prospective_pit_admitted"])

    def test_duplicate_hour_detected(self):
        data=capture()
        data["oi_hourly"].append(deepcopy(data["oi_hourly"][0]))
        with self.assertRaisesRegex(ValueError,"duplicate_hourly_clock"):
            census_capture(data)

    def test_naive_cutoff_fails_closed(self):
        data=capture()
        data["decision_cutoff_utc"]="2026-10-06T08:00:00"
        with self.assertRaisesRegex(ValueError,"decision_cutoff"):
            census_capture(data)

    def test_unused_oi_and_basis_hours_do_not_false_fail(self):
        data=capture()
        # The S5 24h vector only consumes OI baseline/end and latest basis.
        data["oi_hourly"].pop(8)
        data["basis_hourly"].pop(8)
        out=census_capture(data)
        self.assertEqual(out["capability_24h_window_state"],"COMPLETE")
        self.assertEqual(out["series"]["oi_hourly"]["required_24h_timestamps"],2)
        self.assertEqual(out["series"]["basis_hourly"]["required_24h_timestamps"],1)

    def test_no_funding_not_imputed(self):
        data=capture()
        data["funding_events"]=[]
        out=census_capture(data)
        self.assertEqual(out["series"]["funding_events"]["rows_before_cutoff"],0)
        self.assertFalse(out["prospective_pit_admitted"])

if __name__=='__main__':unittest.main()
