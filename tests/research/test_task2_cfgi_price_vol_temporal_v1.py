"""Adversarial Task2 incremental CFGI tests: frozen temporal split and no-lookahead."""
import math
import unittest
from datetime import date,datetime,timedelta,timezone
from scripts.research import task2_cfgi_price_vol_temporal_v1 as m

START=datetime(2026,8,18,tzinfo=timezone.utc)
H=timedelta(hours=1)
def spot(prices):
    return {START+i*H:{"spot_status":"PASS","btc_close":str(p),"eth_close":str(p*2)}
            for i,p in enumerate(prices)}
def row(i,y,score=0):
    return {"mom4_pct":i/40,"vol8_pct":abs(i)/25+1,
            "cfgi_centered":score,"y":int(y),"day":"2026-09-01",
            "week":"2026-W36","future_flat":0,
            "price_batch_end_uncertain":False}

class TimeSeparatedCFGIIncrementalTests(unittest.TestCase):
    def test_train_val_test_immutable_dates_and_embargo(self):
        self.assertEqual((m.TRAIN_END,m.VAL_START,m.VAL_END,m.TEST_START,m.TEST_END),
            (date(2026,9,27),date(2026,9,29),date(2026,10,5),date(2026,10,9),date(2026,10,20)))
        self.assertEqual(m.vintage_partition(date(2026,9,28)),"embargo_not_scored")
        self.assertEqual(m.vintage_partition(date(2026,10,7)),"embargo_not_scored")
        self.assertEqual(m.vintage_partition(date(2026,10,9)),"test_inspected_history")
    def test_historical_holdout_is_explicitly_inspected(self):
        self.assertFalse(m.AUTHORITY["holdout_unseen_before_study_design"])
        self.assertFalse(m.AUTHORITY["hypothesis_registered_before_outcomes"])
    def test_private_round3_source_forbidden(self):
        self.assertFalse(m.AUTHORITY["round3_private_values_read"])
        self.assertFalse(m.AUTHORITY["historical_edge_admitted"] if "historical_edge_admitted" in m.AUTHORITY else m.AUTHORITY["investable_after_cost_edge"])
    def test_past_vol_only_earlier_close(self):
        x=spot([100,101,99,102,101,100,103,102,105,107,109])
        t=START+8*H
        val=m.past_realized_vol(x,t,"BTC")
        x[START+10*H]["btc_close"]="1000000"
        self.assertAlmostEqual(val,m.past_realized_vol(x,t,"BTC"),12)
        self.assertGreater(val,0)
    def test_past_vol_missing_hour_excluded(self):
        x=spot([100]*10);del x[START+4*H]
        self.assertIsNone(m.past_realized_vol(x,START+8*H,"BTC"))
    def test_past_vol_nan_fails_closed(self):
        x=spot([100]*10)
        x[START+2*H]["btc_close"]="nan"
        self.assertIsNone(m.past_realized_vol(x,START+8*H,"BTC"))
    def test_no_future_outcome_in_train_feature_transform(self):
        train=[row(i,i%2,score=i/2) for i in range(30)]
        model=m.fit(train,m.AUG_FIELDS)
        copy={**row(18,1,score=5)}
        a=m.predict(model,copy)
        copy["y"]=0
        self.assertEqual(m.predict(model,copy),a)
    def test_model_deterministic_under_identical_train_rows(self):
        train=[row(i,i%3==0,score=i/2) for i in range(36)]
        a=m.fit(train,m.BASE_FIELDS);b=m.fit(train,m.BASE_FIELDS)
        self.assertEqual(a,b)
    def test_holdout_mutation_does_not_refit_model(self):
        train=[row(i,int(i%2==0),score=i) for i in range(30)]
        fitted=m.fit(train,m.AUG_FIELDS)
        separate=row(33,1,score=25)
        score_before=m.predict(fitted,separate)
        separate["mom4_pct"]=990000
        score_after=m.predict(fitted,separate)
        self.assertEqual(fitted["fields"],m.AUG_FIELDS)
        self.assertTrue(0<score_before<1)
        self.assertTrue(0<score_after<1)
    def test_insufficient_fit_sample_no_fabricated_calibration(self):
        with self.assertRaisesRegex(ValueError,"INSUFFICIENT_FIT_SAMPLE"):
            m.fit([row(i,0) for i in range(12)],m.AUG_FIELDS)
    def test_nonfinite_training_feature_rejected(self):
        train=[row(i,0) for i in range(24)]
        train[3]["vol8_pct"]=float("nan")
        with self.assertRaisesRegex(ValueError,"NONFINITE_TRAIN_FEATURE"):
            m.fit(train,m.BASE_FIELDS)
    def test_proper_scoring_baseline_denominator(self):
        train=[row(i,int(i%2==0),score=i-20) for i in range(40)]
        models={"price_vol":m.fit(train,m.BASE_FIELDS),
                "price_vol_cfgi":m.fit(train,m.AUG_FIELDS)}
        test=[row(i,int(i%3==0),score=i-10) for i in range(20)]
        x=m.metrics(test,models)
        self.assertEqual(x["rows"],20)
        self.assertEqual(x["positive_outcome"]+x["negative_outcome"],20)
        self.assertIsNotNone(x["descriptive_brier_improvement_vs_price_vol"])
        for arm in ("price_vol","price_vol_cfgi"):
            self.assertGreaterEqual(x[arm]["brier"],0)
            self.assertLessEqual(x[arm]["brier"],1)
        self.assertFalse(x["market_edge_admitted"])
    def test_constant_input_scaler_does_not_divide_by_zero(self):
        train=[row(0,int(i%2==0)) for i in range(22)]
        a=m.fit(train,m.BASE_FIELDS)
        self.assertTrue(all(math.isfinite(x) for x in a["coef"]))
        self.assertTrue(0<m.predict(a,row(0,0))<1)
    def test_no_config_tuning_or_auto_sell(self):
        self.assertEqual((m.ITERATIONS,m.LEARNING_RATE,m.RIDGE),(750,0.08,0.3))
        self.assertFalse(m.AUTHORITY["live_rule_change"])
        self.assertFalse(m.AUTHORITY["new_provider_requests"])
    def test_full_original_archive_when_available(self):
        if m.archive.CAPTURE_ROOT.is_dir() and m.archive.PRICE_ROOT.is_dir():
            x=m.execute()
            self.assertEqual(x["contract"],m.CONTRACT)
            self.assertEqual(set(x["asset_results"]),{"BTC","ETH"})
            self.assertFalse(x["statistical_significance_or_economic_edge_claim"])
            self.assertFalse(x["underlying_source_values_emitted"])
            self.assertFalse(x["authority"]["provider_first_publication_proven"])
            for asset,segments in x["asset_results"].items():
                self.assertGreater(segments["train"]["rows"],100)
                self.assertGreater(segments["validation"]["rows"],10)
                self.assertGreater(segments["test_inspected_history"]["rows"],20)
                self.assertFalse(segments["model_selection_after_validation"])
if __name__=="__main__":unittest.main()
