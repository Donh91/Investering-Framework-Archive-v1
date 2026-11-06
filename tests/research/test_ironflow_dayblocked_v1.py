import sys
import unittest
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"/"research"))
from ironflow_hourly_stress_v1 import build
from ironflow_dayblocked_study_v1 import day_anchors

class DayBlockedLeakageFixtures(unittest.TestCase):
    def setUp(self):
        ts=pd.date_range("2026-10-01",periods=120,freq="h",tz="UTC")
        self.c=pd.DataFrame({"timestamp":ts,"market":"BTC-PERP","market_class":"perp",
                             "open":100.,"high":101.,"low":99.,"close":100.,"volume":10.})
        self.o=pd.DataFrame({"timestamp":ts,"market":"BTC-PERP","open_interest_usd":20000.})
        self.f=pd.DataFrame({"timestamp":ts+pd.Timedelta(milliseconds=9),
                             "market":"BTC-PERP","funding_rate":0.0001})
        self.l=pd.DataFrame({"timestamp":[ts[0]],"market":"BTC-PERP",
                             "position_side":"long","notional_usd":400.})
    def anchors(self):
        return day_anchors(build(self.c,self.o,self.f,self.l))
    def test_nonoverlap_anchor_has_matured_future(self):
        x=self.anchors()
        self.assertEqual(len(x),3)
        self.assertTrue(all(x.timestamp.dt.hour==23))
        self.assertTrue((x.decision_at_utc==x.timestamp+pd.Timedelta(hours=1)).all())
    def test_future_low_does_not_rewrite_prior_features(self):
        before=self.anchors()
        self.c.loc[50,"low"]=60.
        after=self.anchors()
        self.assertEqual(before.iloc[0].liq_ratio_24h,after.iloc[0].liq_ratio_24h)
        self.assertNotEqual(before.iloc[0].drawdown_next_24h,after.iloc[0].drawdown_next_24h)
    def test_unknown_funding_excludes_anchor(self):
        self.f.loc[40:50,"funding_rate"]=float("nan")
        x=self.anchors()
        self.assertEqual(len(x),2)
    def test_missing_hour_cannot_form_invalid_future(self):
        for name in ("c","o","f"):
            setattr(self,name,getattr(self,name).drop(90))
        x=self.anchors()
        self.assertLess(len(x),3)

if __name__=="__main__":unittest.main()
