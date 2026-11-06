import sys,unittest
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"/"research"))
from ironflow_full18m_walkforward_v1 import MONTHS,walkforward,summarize,verify_frozen_72_source_sha

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
        self.assertEqual(out[0]["month"],"2025-06")
    def test_month_boundary_uses_only_labels_matured_before_test(self):
        d=self.mock_data()
        edge=d[(d.month=="2025-10")&(d.market=="BTC-PERP")].iloc[[0]].copy()
        edge["timestamp"]=pd.Timestamp("2025-10-31T23:00:00Z")
        d=pd.concat([d,edge],ignore_index=True)
        out=walkforward(d)
        first=out[0]
        self.assertGreaterEqual(first["training_labels_excluded_due_to_embargo"],1)
        self.assertLess(pd.Timestamp(first["max_train_label_maturity_utc"]),
                        pd.Timestamp(first["training_boundary_cutoff_utc"]))
        self.assertEqual(first["training_label_embargo_hours"],25)
    def test_all_72_original_sha_registry_enforced_and_mutation_rejected(self):
        registry=Path(__file__).resolve().parents[2]/"06_RESEARCH_LAB"/"hugging_face_task2_audit_20261022"/"IRONFLOW_FULL18M_SOURCE_SHA256_REGISTRY_20261107.md"
        records=[]
        for line in registry.read_text(encoding="utf8").splitlines():
            parts=line.split()
            if len(parts)==5 and parts[0] in MONTHS:
                for family,digest in zip(("liquidations","funding","oi","candles"),parts[1:]):
                    records.append({"month":parts[0],"family":family,"actual_sha256":digest})
        self.assertEqual(len(records),72)
        self.assertEqual(verify_frozen_72_source_sha(records,registry)["file_digests_verified_against_frozen_registry"],72)
        bad=[dict(r) for r in records]
        bad[0]["actual_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"FROZEN_ORIGINAL_SOURCE_SHA256_MISMATCH"):
            verify_frozen_72_source_sha(bad,registry)
    def test_no_valid_months_fails_closed(self):
        s=summarize([{"status":"INSUFFICIENT_SOURCE_ANCHORS"}])
        self.assertEqual(s["status"],"NO_VALID_MONTHS")
if __name__=="__main__":unittest.main()
