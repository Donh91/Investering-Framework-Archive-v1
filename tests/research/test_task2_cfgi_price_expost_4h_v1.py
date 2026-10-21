"""Negative controls for strictly descriptive Task2 archived CFGI/price joins."""
import unittest
from datetime import datetime, timezone, timedelta
from scripts.research import task2_cfgi_price_expost_4h_v1 as m

T=datetime(2026,10,18,12,37,20,tzinfo=timezone.utc)
def dt(t):return t.isoformat().replace("+00:00","Z")
BASE=T.replace(minute=0,second=0,microsecond=0)-timedelta(hours=1)
def price_row(timestamp,btc,eth,*,status="PASS",batch_end=None):
    return {"timestamp_utc":dt(timestamp),
            "source_window_end_utc":dt(batch_end or timestamp+timedelta(hours=1)),
            "spot_status":status,"btc_close":str(btc),"eth_close":str(eth)}
def triplet(btc=(90,100,110),eth=(200,190,180)):
    return {BASE-timedelta(hours=4):price_row(BASE-timedelta(hours=4),btc[0],eth[0]),
            BASE:price_row(BASE,btc[1],eth[1],batch_end=BASE+timedelta(hours=3)),
            BASE+timedelta(hours=4):price_row(BASE+timedelta(hours=4),btc[2],eth[2])}
def meta():
    return {"capture_utc":dt(T),
        "source_symbol_times":{
          "BTC":{"original_row_utc":dt(T-timedelta(minutes=1))},
          "ETH":{"original_row_utc":dt(T-timedelta(minutes=2))}}}
def snap(btc=75,eth=25):
    return {"rows":[{"symbol":"BTC","score":btc},{"symbol":"ETH","score":eth}]}
class CFGIPriceJoinTests(unittest.TestCase):
    def test_retro_paired_exact_two_symbols(self):
        out=m.classify_opportunity(snap(),meta(),triplet())
        self.assertEqual(len(out),2)
        self.assertEqual([x["state"] for x in out],["EXPOST_JOIN_ONLY"]*2)
        self.assertEqual([x["cfgi_score_sign"] for x in out],[1,-1])
        self.assertEqual([x["momentum_sign"] for x in out],[1,-1])
        self.assertEqual([x["outcome_sign"] for x in out],[1,-1])
        self.assertTrue(out[0]["price_batch_end_after_nominal_close"])
        s=m.summarize(out)
        self.assertEqual(s["paired_both_correct"],2)
        self.assertEqual(s["paired_cfgi_only_correct"],0)
        self.assertEqual(s["independent_event_families_admitted"],0)
        self.assertIsNone(s["statistical_p_value"])
    def test_neutral_score_abstention_keeps_denominator(self):
        out=m.classify_opportunity(snap(btc=50),meta(),triplet())
        s=m.summarize(out)
        self.assertEqual(s["symbol_observations"],2)
        self.assertEqual(s["score_50_abstentions"],1)
        self.assertEqual(s["strictly_paired_non_neutral_opportunities"],1)
    def test_future_not_used_to_compute_momentum(self):
        before=m.classify_opportunity(snap(),meta(),triplet())
        after=m.classify_opportunity(snap(),meta(),triplet(btc=(90,100,50)))
        self.assertEqual(before[0]["momentum_sign"],after[0]["momentum_sign"])
        self.assertNotEqual(before[0]["outcome_sign"],after[0]["outcome_sign"])
    def test_partial_hour_not_silently_used(self):
        spot=triplet();spot[BASE-timedelta(hours=4)]["spot_status"]="DEGRADED"
        out=m.classify_opportunity(snap(),meta(),spot)
        self.assertEqual(out[0]["state"],"INCOMPLETE_OR_DEGRADED_PRICE")
    def test_missing_future_does_not_become_false_zero(self):
        spot=triplet();del spot[BASE+timedelta(hours=4)]
        out=m.classify_opportunity(snap(),meta(),spot)
        self.assertEqual(out[0]["state"],"MISSING_ARCHIVED_PRICE_BOUNDARY")
    def test_missing_past_is_not_filled(self):
        spot=triplet();del spot[BASE-timedelta(hours=4)]
        self.assertEqual(m.classify_opportunity(snap(),meta(),spot)[0]["state"],
                         "MISSING_ARCHIVED_PRICE_BOUNDARY")
    def test_missing_score_explicitly_excluded(self):
        out=m.classify_opportunity(snap(btc=None),meta(),triplet())
        self.assertEqual(out[0]["state"],"NO_VALID_CFGI_SCORE")
    def test_out_of_range_score_rejected(self):
        out=m.classify_opportunity(snap(btc=200),meta(),triplet())
        self.assertEqual(out[0]["state"],"INVALID_CFGI_SCORE")
    def test_nonfinite_price_fails_closed(self):
        out=m.classify_opportunity(snap(),meta(),triplet(btc=(90,float("nan"),110)))
        self.assertEqual(out[0]["state"],"INCOMPLETE_OR_DEGRADED_PRICE")
    def test_timestamp_after_capture_rejected(self):
        z=meta();z["source_symbol_times"]["BTC"]["original_row_utc"]=dt(T+timedelta(minutes=5))
        with self.assertRaisesRegex(ValueError,"SOURCE_ROW_FUTURE_TO_CAPTURE"):
            m.classify_opportunity(snap(),z,triplet())
    def test_distinct_momentum_and_cfgi_sign_is_not_forced_agreement(self):
        out=m.classify_opportunity(snap(btc=25),meta(),triplet())
        s=m.summarize(out)
        self.assertEqual(s["paired_momentum_only_correct"],1)
        self.assertEqual(s["paired_both_correct"],1)
    def test_no_inference_if_correlation_needs_power(self):
        self.assertIsNone(m.safe_correlation([1,2],[3,4]))
        self.assertIsNone(m.safe_correlation([0,0,0],[1,2,3]))
    def test_frozen_date_and_non_pit_source(self):
        self.assertEqual(len(m.DAYS),7)
        self.assertFalse(m.AUTHORITY["price_first_known_at_decision_certified"])
        self.assertFalse(m.AUTHORITY["scientific_hypothesis_pre_registered"])
    def test_full_existing_original_week_if_mounted(self):
        if m.CAPTURE_ROOT.exists() and m.SPOT_ROOT.exists():
            d=m.execute()
            self.assertEqual(d["original_capture_opportunities"],42)
            self.assertEqual(d["original_symbol_opportunities"],84)
            self.assertEqual(d["joined_development_only_symbol_opportunities"]+
                             sum(d["missing_or_degraded_symbol_opportunities"].values()),84)
            self.assertFalse(d["historical_or_live_cfgi_edge_proven"])
            self.assertTrue(d["no_price_from_vendor"])
            self.assertEqual(set(d["by_symbol"]),{"BTC","ETH"})
if __name__=="__main__":unittest.main()
