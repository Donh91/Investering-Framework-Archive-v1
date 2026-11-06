import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"/"research"))
from ironflow_oot_ablation_v1 import matrix,evaluate,paired_day_bootstrap

class OTTAblationFixtures(unittest.TestCase):
    def setUp(self):
        rows=[]
        for j,month in enumerate(("2025-10","2026-09","2026-10")):
            for k,market in enumerate(("BTC-PERP","ETH-PERP","HYPE-PERP")):
                for i in range(28):
                    rows.append({
                        "market":market,"month":month,
                        "timestamp":pd.Timestamp(month+"-01",tz="UTC")+pd.Timedelta(days=i,hours=23),
                        "past_price_return_24h":float((i%7-3)*.01),
                        "past_volatility_24h":float(.01+(.001*((i+k)%6))),
                        "liq_ratio_24h":float(.005+.003*((i+k+j)%5)),
                        "oi_change_24h":float((k+i%7-3)*.008),
                        "settled_funding_sum_24h":float((i%5-2)*.0002),
                        "drawdown_2pct_next_day":bool((i+k+j)%3==0)})
        self.a=pd.DataFrame(rows)
    def test_deterministic_columns_no_outcome_leak(self):
        a=matrix(self.a,False)
        b=matrix(self.a,True)
        self.assertEqual(a.shape[1],4)
        self.assertEqual(b.shape[1],7)
        self.assertTrue(all("drawdown_next" not in c for c in b.columns))
    def test_two_temporal_splits_execute(self):
        x=evaluate(self.a)
        self.assertEqual(len(x),2)
        self.assertEqual(x[0]["test_month"],"2026-09")
        self.assertEqual(x[1]["test_month"],"2026-10")
        self.assertEqual(x[0]["n_test"],84)
        self.assertEqual(x[1]["clustered_paired_brier"]["n_date_clusters"],28)
        self.assertEqual(x[1]["verdict"],"EXPLORATORY_WITH_EXPLICIT_SELECTION_CONTAMINATION")
    def test_day_clusters_preserve_correlated_assets(self):
        d=self.a[self.a.month=="2026-10"].copy()
        y=d.drawdown_2pct_next_day.to_numpy(dtype=int)
        p0=np.full(len(y),0.5)
        p1=np.full(len(y),0.3)
        s=paired_day_bootstrap(d,y,p0,p1)
        self.assertEqual(s["n_date_clusters"],28)
        self.assertEqual(len(s["paired_day_bootstrap_95pct_interval"]),2)
    def test_2month_sample_purges_unmatured_prior_month_labels(self):
        edge=self.a[(self.a.month=="2026-09")&(self.a.market=="BTC-PERP")].iloc[[0]].copy()
        edge["timestamp"]=pd.Timestamp("2026-09-30T23:00:00Z")
        d=pd.concat([self.a,edge],ignore_index=True)
        results=evaluate(d)
        self.assertGreaterEqual(results[1]["purged_unmatured_training_labels"],1)
        self.assertLess(pd.Timestamp(results[1]["max_training_target_maturity_utc"]),
                        pd.Timestamp(results[1]["test_month_start_utc"]))
    def test_invalid_source_is_fail_closed(self):
        a=self.a.copy()
        a.loc[0,"settled_funding_sum_24h"]=np.nan
        with self.assertRaisesRegex(ValueError,"invalid feature matrix"):matrix(a,True)
if __name__=="__main__":unittest.main()
