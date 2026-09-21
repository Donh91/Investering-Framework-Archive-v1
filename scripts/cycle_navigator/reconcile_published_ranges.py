from __future__ import annotations
import argparse,csv,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

FORMULA="70pct_containment_plus_30pct_jaccard"
AUTHORITY="CN_RANGE_CONTINUITY_CORRECTION_NO_PORTFOLIO_AUTHORITY"

def read_json(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(p,v):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,sort_keys=True,separators=(",",":"))+"\n")
def interval_score(fl,fh,al,ah):
    inter=max(0.0,min(fh,ah)-max(fl,al)); aw=ah-al; union=max(fh,ah)-min(fl,al)
    containment=inter/aw if aw>0 else 0.0; jaccard=inter/union if union>0 else 0.0
    return round(100*(0.7*containment+0.3*jaccard),2),round(100*containment,2),round(100*jaccard,2)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo-root",default="."); ap.add_argument("--year",type=int,required=True); ap.add_argument("--week",type=int,required=True)
    a=ap.parse_args(); r=Path(a.repo_root); tag=f"{a.year}-W{a.week:02d}"
    ledger=r/"05_CYCLE_NAVIGATOR/forward_range_ledger/CN_23_25_RANGE_BACKFILL_2026-09-17.csv"
    weekly=r/f"03_DAILY_CAPTURE_LOGS/weekly/{a.year}/W{a.week:02d}.json"
    if not ledger.exists() or not weekly.exists(): raise SystemExit("required_range_or_actual_source_missing")
    actual=read_json(weekly)
    if actual.get("readiness")!="READY" or int(actual.get("hourly_gap_diagnostics",{}).get("observed_hours",0))!=168: raise SystemExit("weekly_actuals_not_168h_ready")
    rows=list(csv.DictReader(ledger.read_text().splitlines()))
    eligible=[x for x in rows if x["forecast_week"]==tag]
    if not eligible: raise SystemExit("no_prospective_published_range_rows")
    issues={int(x["issue"]) for x in eligible}
    if len(issues)!=1: raise SystemExit("ambiguous_published_issue")
    issue=issues.pop()
    pub=r/f"05_CYCLE_NAVIGATOR/published/{a.year}/CYCLE_NAVIGATOR_{issue}_X_PUBLISHED_{datetime.fromisocalendar(a.year,a.week,1).date().isoformat()}.md"
    receipt=r/f"05_CYCLE_NAVIGATOR/weekly/{a.year}/W{a.week:02d}/CYCLE_NAVIGATOR_X_APPROVAL_RECEIPT.json"
    if not pub.exists() or not receipt.exists(): raise SystemExit("published_provenance_missing")
    rec=read_json(receipt)
    if rec.get("status")!="PUBLISHED_CONFIRMED_BY_USER" or int(rec.get("public_issue_number",-1))!=issue: raise SystemExit("publication_not_confirmed")
    if rec.get("published_copy_blob_sha") and rec["published_copy_blob_sha"]!=sha(pub): raise SystemExit("published_blob_hash_mismatch")
    windows=actual["day_window_actuals"]["windows"]; keymap={"day_1_2":"DAY1_2","day_3_4":"DAY3_4","day_5_7":"DAY5_7"}
    scored=[]; by_asset={"BTC":[],"ETH":[]}; by_window={k:[] for k in keymap}
    for x in eligible:
        asset=x["asset"]; window=x["window"]; act=windows[keymap[window]][asset.lower()]
        fl,fh=float(x["forecast_low"]),float(x["forecast_high"]); al,ah=float(act["low"]),float(act["high"])
        s,c,j=interval_score(fl,fh,al,ah)
        row={"asset":asset,"window":window,"forecast_low":fl,"forecast_high":fh,"actual_low":al,"actual_high":ah,"score":s,"containment_pct":c,"jaccard_pct":j}
        scored.append(row); by_asset[asset].append(s); by_window[window].append(s)
    asset_scores={k:round(sum(v)/len(v),2) for k,v in by_asset.items()}
    window_scores={k:round(sum(v)/len(v),2) for k,v in by_window.items()}
    combined=round(sum(x["score"] for x in scored)/len(scored),2)
    out={"contract":"CN_RANGE_CONTINUITY_CORRECTION_v1","authority":AUTHORITY,"status":"FINAL_RECONCILED_FROM_PROSPECTIVE_PUBLISHED_RANGES","forecast_week":tag,"issue_scored":issue,"score_formula":FORMULA,"price_range_score":combined,"asset_scores":asset_scores,"intraday_window_scores":window_scores,"rows":scored,"provenance":{"published_copy_path":str(pub.relative_to(r)),"published_copy_sha256":sha(pub),"approval_receipt_path":str(receipt.relative_to(r)),"approval_receipt_sha256":sha(receipt),"range_ledger_path":str(ledger.relative_to(r)),"range_ledger_sha256":sha(ledger),"weekly_actuals_path":str(weekly.relative_to(r)),"weekly_actuals_sha256":sha(weekly),"hourly_coverage":168},"rules":{"no_hindsight_forecast_creation":True,"append_only_correction":True,"machine_freeze_not_rewritten":True,"website_and_master_monday_may_consume_score":True}}
    target=r/f"05_CYCLE_NAVIGATOR/corrections/{a.year}/W{a.week:02d}/RANGE_SCORE_CORRECTION.json"; write_json(target,out)
    pointer={"contract":"CN_LATEST_RANGE_SCORE_POINTER_v1","forecast_week":tag,"issue_scored":issue,"path":str(target.relative_to(r)),"price_range_score":combined,"btc_score":asset_scores["BTC"],"eth_score":asset_scores["ETH"],"intraday_window_scores":window_scores,"status":out["status"]}
    write_json(r/"05_CYCLE_NAVIGATOR/LATEST_RANGE_SCORE.json",pointer)
    print(json.dumps(pointer,sort_keys=True))
if __name__=="__main__": main()
