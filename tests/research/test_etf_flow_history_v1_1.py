from __future__ import annotations
import csv, hashlib, importlib.util, json, unittest
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
PACK=ROOT/"04_MARKET_LEARNING/truth_layer/etf_flows/2026-09-23__us-spot-crypto-etf-flow-history-v1_1"
V1=ROOT/"04_MARKET_LEARNING/truth_layer/etf_flows/2026-07-26__us-spot-crypto-etf-flow-history"
MANIFEST=json.loads((PACK/"manifest.json").read_text())

EXPECTED_REPAIRS={
"BTC|2025-09-19":[246.1,0,0,0,0,0,0,0,0,0,-23.5,0,222.6],
"BTC|2025-10-24":[32.7,57.9,0,0,0,0,0,0,0,0,0,0,90.6],
"BTC|2025-11-03":[-186.5,0,0,0,0,0,0,0,0,0,0,0,-186.5],
"BTC|2025-11-06":[112.4,61.6,5.5,60.4,0,0,0,0,0,0,0,0,239.9],
"BTC|2025-11-10":[0,0,1.2,0,0,0,0,0,0,0,0,0,1.2],
"BTC|2025-12-19":[-173.6,15.3,0,0,0,0,0,0,0,0,0,0,-158.3],
"BTC|2025-12-29":[-7.9,5.7,0,-6.7,-10.4,0,0,0,0,0,0,0,-19.3],
"BTC|2026-03-02":[263.2,94.8,36.4,5.7,6.2,14,0,19.5,0,0,0,18.4,458.2],
"BTC|2026-05-20":[-61.5,-10.1,0,0,0,0,0,0,0,1.1,0,0,-70.5],
"ETH|2024-10-25":[0,0,0,0,0,0,0,0,-19.2,0,-19.2],
"ETH|2024-11-01":[0,0,0,0,0,0,0.5,0,-11.4,0,-10.9],
}

def rows(asset):
    out=[]
    for p in sorted((PACK/"data").glob(f"us_spot_{asset.lower()}_etf_flows_daily_*.csv")):
        with p.open(newline="") as h: out.extend(csv.DictReader(h))
    return out

class ETFHistoryV11Tests(unittest.TestCase):
    def test_v1_source_bytes_are_unchanged_from_creation_readback(self):
        for name,meta in MANIFEST["v1_source_readback"].items():
            raw=(V1/"data"/name).read_bytes()
            self.assertEqual(len(raw),meta["bytes"],name)
            self.assertEqual(hashlib.sha256(raw).hexdigest(),meta["sha256"],name)

    def test_rows_are_full_width_reconciled_and_session_labelled(self):
        total_non=0
        for asset in ("BTC","ETH"):
            rs=rows(asset)
            expected=MANIFEST["coverage"][asset.lower()]
            self.assertEqual(len(rs),expected["rows"])
            self.assertEqual(min(r["date"] for r in rs),expected["start_date"])
            self.assertEqual(max(r["date"] for r in rs),expected["end_date"])
            for r in rs:
                self.assertIn(r["session_status"],{"TRADING_SESSION","NYSE_FULL_CLOSURE"})
                funds=[c for c in r if c not in {"date","Total","session_status"}]
                self.assertAlmostEqual(round(sum(float(r[c]) for c in funds),1),round(float(r["Total"]),1),places=1)
            non=sum(r["session_status"]=="NYSE_FULL_CLOSURE" for r in rs)
            self.assertEqual(non,expected["non_sessions"])
            total_non += non
        self.assertEqual(total_non,26)

    def test_all_11_recovery_rows_match_frozen_evidence(self):
        seen={}
        for asset in ("BTC","ETH"):
            for r in rows(asset):
                key=f"{asset}|{r['date']}"
                if key in EXPECTED_REPAIRS:
                    cols=[c for c in r if c not in {"date","session_status"}]
                    seen[key]=[float(r[c]) for c in cols]
        self.assertEqual(set(seen),set(EXPECTED_REPAIRS))
        for key,values in EXPECTED_REPAIRS.items():
            self.assertEqual(seen[key],values,key)

    def test_nonclosure_zero_rows_remain_trading_sessions(self):
        examples=[]
        for asset in ("BTC","ETH"):
            examples += [r for r in rows(asset) if float(r["Total"])==0.0 and r["session_status"]=="TRADING_SESSION"]
        self.assertTrue(examples)

    def test_feature_helper_skips_closure_without_resetting_session_streak(self):
        spec=importlib.util.spec_from_file_location("v11_builder",PACK/"scripts/build_etf_flow_features.py")
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        frame=pd.DataFrame([
            {"date":"2025-01-17","Total":10.0,"session_status":"TRADING_SESSION"},
            {"date":"2025-01-20","Total":0.0,"session_status":"NYSE_FULL_CLOSURE"},
            {"date":"2025-01-21","Total":5.0,"session_status":"TRADING_SESSION"},
        ])
        trading=mod.trading_sessions(frame)
        self.assertEqual(trading["date"].tolist(),["2025-01-17","2025-01-21"])
        positive,negative=mod.streaks(trading["Total"])
        self.assertEqual(positive,[1,2]);self.assertEqual(negative,[0,0])
        self.assertEqual(trading["Total"].rolling(2,min_periods=1).sum().tolist(),[10.0,15.0])

if __name__=="__main__":
    unittest.main()
