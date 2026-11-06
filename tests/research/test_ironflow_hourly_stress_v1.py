import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"/"research"))
from ironflow_hourly_stress_v1 import build,describe

class TestIronflowStress(unittest.TestCase):
    def setUp(self):
        ts=pd.date_range("2026-10-01",periods=95,freq="h",tz="UTC")
        self.c=pd.DataFrame({"timestamp":ts,"market":"BTC-PERP","market_class":"perp",
                             "open":100.,"high":101.,"low":99.,"close":100.,
                             "volume":10.})
        self.o=pd.DataFrame({"timestamp":ts,"market":"BTC-PERP",
                             "open_interest_usd":10000.})
        self.f=pd.DataFrame({"timestamp":ts,"market":"BTC-PERP",
                             "funding_rate":0.0001})
        self.l=pd.DataFrame({"timestamp":[ts[0]+pd.Timedelta(minutes=9)],
                             "market":["BTC-PERP"],"notional_usd":[400.],
                             "position_side":["long"]})
    def p(self):
        return build(self.c,self.o,self.f,self.l)
    def test_liquidation_one_event_and_ratio(self):
        p=self.p()
        self.assertEqual(int(p.liq_events.sum()),1)
        self.assertAlmostEqual(p.iloc[0].liquidation_ratio_to_approx_quote_volume,0.4)
    def test_candle_end_knowability(self):
        p=self.p()
        self.assertTrue((p.decision_at_utc>p.timestamp).all())
        self.assertAlmostEqual(p.iloc[0].drawdown_next_4h,-0.01)
        self.assertAlmostEqual(p.iloc[0].return_next_4h,0.)
    def test_future_hour_no_feature_leakage(self):
        before=self.p()
        self.c.loc[4,"low"]=60.
        after=self.p()
        self.assertAlmostEqual(after.iloc[0].drawdown_next_4h,-0.4)
        self.assertEqual(after.iloc[0].close,before.iloc[0].close)
        self.assertTrue(pd.isna(after.iloc[0].price_change_1h))
    def test_duplicate_rejected(self):
        self.c=pd.concat([self.c,self.c.iloc[[0]]],ignore_index=True)
        with self.assertRaisesRegex(ValueError,"duplicate candles"):self.p()
    def test_ohlc_rejected(self):
        self.c.loc[1,"low"]=150
        with self.assertRaisesRegex(ValueError,"bad OHLC"):self.p()
    def test_oi_missing_stays_unknown(self):
        self.o=self.o.iloc[1:].copy()
        p=self.p()
        self.assertTrue(pd.isna(p.iloc[0].open_interest_usd))
        self.assertTrue(pd.isna(p.iloc[1].oi_change_1h))
    def test_funding_fractional_settlement_time_joins_hour(self):
        self.f["timestamp"]=self.f.timestamp+pd.Timedelta(milliseconds=123)
        p=self.p()
        self.assertEqual(int(p.funding_rate.isna().sum()),0)
        self.assertAlmostEqual(float(p.iloc[0].funding_rate),0.0001)
    def test_funding_duplicate_after_hour_floor_rejected(self):
        f2=self.f.iloc[[0]].copy()
        f2["timestamp"]=f2.timestamp+pd.Timedelta(milliseconds=321)
        self.f=pd.concat([self.f,f2],ignore_index=True)
        with self.assertRaisesRegex(ValueError,"duplicate funding"):self.p()
    def test_gap_refuses_false_horizon(self):
        self.c=self.c.drop(2)
        self.o=self.o.drop(2)
        self.f=self.f.drop(2)
        p=self.p()
        self.assertTrue(pd.isna(p.iloc[1].drawdown_next_4h))
        self.assertTrue(pd.isna(p.iloc[2].price_change_1h))
    def test_no_edge_or_independence_claim(self):
        out=describe(self.p())
        self.assertTrue(all(x["note"]=="NOT_INDEPENDENT_NOT_OOS_NO_EDGE_CLAIM" for x in out))
        self.assertTrue(all(x["n_overlapping_hours"]>=0 for x in out))

if __name__=="__main__":unittest.main()
