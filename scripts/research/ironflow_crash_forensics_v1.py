#!/usr/bin/env python3
"""Historical stress-event anatomy, not pre-event signal proof.
Attribution: Ironflow (ironflow.sh) CC BY 4.0.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from ironflow_hourly_stress_v1 import build,H
from ironflow_dayblocked_study_v1 import load,M

EPISODES={
"2025-10-10_CRASH":"2025-10-10",
"2025-10-17_CONTROL":"2025-10-17",
"2026-10-07_PULLBACK":"2026-10-07",
"2026-10-08_PULLBACK":"2026-10-08",
"2026-10-12_RISK":"2026-10-12",
"2026-10-23_CONTROL":"2026-10-23"}
def analyze(root):
    tables=load(root,M)
    d=build(tables["candles"],tables["oi"],tables["funding"],tables["liquidations"])
    results=[]
    for name,day in EPISODES.items():
        subset=d[d.timestamp.dt.strftime("%Y-%m-%d")==day].copy()
        if len(subset)==0:
            results.append({"name":name,"status":"NO_ORIGINAL_SOURCE_ROWS"})
            continue
        for market,x in subset.groupby("market"):
            top=x.nlargest(5,"liq_usd")
            results.append({
                "name":name,"market":market,"available_hour_count":len(x),
                "total_position_events":int(x.liq_events.sum()),
                "total_liquidated_notional_usd":round(float(x.liq_usd.sum()),2),
                "long_liquidated_notional_usd":round(float(x.liq_long_usd.sum()),2),
                "most_intense_hours":[{
                    "complete_hour_end_utc":(r.timestamp+H).isoformat(),
                    "liquidated_position_events":int(r.liq_events),
                    "liquidated_notional_usd":round(float(r.liq_usd),2),
                    "price_return_during_same_hour":None if pd.isna(r.price_change_1h) else round(float(r.price_change_1h),6),
                    "return_after_next_4h":None if pd.isna(r.return_next_4h) else round(float(r.return_next_4h),6),
                    "max_drawdown_next_4h":None if pd.isna(r.drawdown_next_4h) else round(float(r.drawdown_next_4h),6)
                } for r in top.itertuples(index=False)],
                "interpretation":"ALREADY_OCCURRING_LIQUIDATIONS_NOT_PRE_EVENT_WARNING"})
    return {"contract":"IRONFLOW_CRASH_FORENSICS_V1",
        "source":"Ironflow (ironflow.sh), CC BY 4.0",
        "warning_lead_time_from_original_framework":"UNVERIFIED",
        "historically_eligible_Ironflow_Nov2026_feed":"FALSE",
        "price_data_clock":"COMPLETED_CANDLE_ONLY",
        "episode_results":results}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    r=analyze(a.root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":"HISTORICAL_EPISODE_QA_COMPLETE",
                      "rows":len(r["episode_results"])}))
if __name__=="__main__":main()
