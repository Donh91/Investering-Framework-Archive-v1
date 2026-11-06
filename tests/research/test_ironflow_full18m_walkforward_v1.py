import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"/"research"))
from ironflow_full18m_walkforward_v1 import MONTHS,walkforward,summarize

class Full18mWalkForwardTests(unittest.TestCase):
    @staticmethod
    def mock_data():
        records=[]
        for j,month in enumerate(MONTHS):
            for market_i,market in enumerate(("BTC-PERP","ETH-PERP","HYPE-PERP")):
                for day in range(1,25):
                    records.append({
                      "month":month,"market":market,
                      "timestamp":pd.Timestamp(month+"-"+str(day).zfill(2)+"T23:00:00Z"),
                      "drawdown_2pct_next_day":bool((day+market_i+j)%3==0),
                      "liq_ratio_24h":float((day+j)%5)/100,
                      "past_price_return_24h":float((day%5-2)*.011),
                      "past_volatility_24h":float(.015+(day%4)*.001),
                      "oi_change_24h":float((day%7-3)*.012),
                      "settled_funding_sum_24h":float((day%3-1)*.0005)})
        return pd.DataFrame(records)
    def test_exact_continuous_months(self):
        self.assertEqual(len(MONTHS),18)
        self.assertEqual(MONTHS[0],"2025-05")
        self.assertEqual(MONTHS[-1],"2026-10")
    def test_month_by_month_no_future_train(self):
        d=self.mock_data()
        out=walkforward(d)
        self.assertEqual(len(out),12)
        self.assertTrue(all(x["status"]=="HISTORICAL_MONTH_REPLAY_OK" for x in out))
        for x in out:
            self.assertTrue(all(m<x["month"] for m in x["train_months"]))
            self.assertEqual(x["test_n"],72)
            self.assertEqual(x["test_distinct_UTC_dates"],24)
        s=summarize(out)
        self.assertEqual(s["tested_months"],12)
        self.assertEqual(s["decision"],"NO_CONFIRMED_TRADING_OR_INFORMATION_EDGE")
    def test_no_eligibility_if_missing_train(self):
        d=self.mock_data()
        out=walkforward(d,months=MONTHS[:2],min_train_months=1)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["test_month"],"2025-06") if "test_month" in out[0] else self.assertEqual(out[0]["month"],"2025-06")
    def test_no_valid_months_fails_closed(self):
        s=summarize([{"status":"INSUFFICIENT_SOURCE_ANCHORS"}])
        self.assertEqual(s["status"],"NO_VALID_MONTHS")
if __name__=="__main__":unittest.main()
