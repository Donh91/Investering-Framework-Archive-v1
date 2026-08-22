#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from datetime import datetime,timezone,timedelta
from pathlib import Path

ROOT=Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
ROWS=ROOT/"data/PROSPECTIVE_SHARED_ROW_LEDGER.csv"
DETAIL=ROOT/"data/OUTCOME_DETAIL_LEDGER.csv"
HOURLY=Path("03_DAILY_CAPTURE_LOGS/hourly")
H={"24h":24,"72h":72,"7d":168}

def parse(v):return datetime.fromisoformat(v.replace("Z","+00:00")).astimezone(timezone.utc)
def iso(x):return x.replace(microsecond=0).isoformat().replace("+00:00","Z")
def canon(x):return json.dumps(x,sort_keys=True,separators=(",",":"))
def pct(v,b):return (v/b-1.0)*100.0

def load():
    out=[]
    for p in sorted(HOURLY.rglob("*.csv")):
        try:
            with p.open(newline="",encoding="utf-8-sig") as f:
                for r in csv.DictReader(f):
                    try:out.append({"ts":parse(r["timestamp_utc"]),"ethbtc":float(r["ethbtc_close"]),"btc":float(r["btc_close"]),"eth":float(r["eth_close"])})
                    except Exception:continue
        except Exception:continue
    d={x["ts"]:x for x in out};return [d[k] for k in sorted(d)]

def read_csv(p):
    with p.open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))
def write_csv(p,rows,fields):
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def detail_keys():
    if not DETAIL.exists():return set()
    return {(r["event_id"],r["horizon"]) for r in read_csv(DETAIL)}
def append_detail(r):
    with DETAIL.open(newline="",encoding="utf-8-sig") as f:fields=next(csv.reader(f))
    with DETAIL.open("a",newline="",encoding="utf-8") as f:csv.DictWriter(f,fieldnames=fields).writerow({k:r.get(k,"") for k in fields})
def select_baseline(data,cutoff):
    xs=[x for x in data if x["ts"]<=cutoff];return xs[-1] if xs else None
def select_end(data,target):
    xs=[x for x in data if target<=x["ts"]<=target+timedelta(hours=1)];return xs[0] if xs else None
def path(data,start,end):return [x for x in data if start<=x["ts"]<=end]
def calc(asset,baseline,end,pathrows):
    b=baseline[asset];e=end[asset];rets=[pct(x[asset],b) for x in pathrows]
    return {"baseline":b,"end":e,"forward":pct(e,b),"mae":min(rets),"mfe":max(rets)}

def main():
    rows=read_csv(ROWS);fields=list(rows[0].keys()) if rows else []
    if not rows:
        print(json.dumps({"status":"PASS","rows":0,"horizons_written":0},sort_keys=True));return
    data=load();existing=detail_keys();now=datetime.now(timezone.utc);changed=0
    for r in rows:
        cutoff=parse(r["information_cutoff_utc"]);baseline=select_baseline(data,cutoff)
        if baseline is None:continue
        for h,hours in H.items():
            of=f"outcome_{h}";ma=f"mae_{h}";mf=f"mfe_{h}"
            if str(r.get(of,"")).strip():continue
            target=cutoff+timedelta(hours=hours)
            if now<target:continue
            end=select_end(data,target)
            if end is None:continue
            pr=path(data,baseline["ts"],end["ts"])
            if not pr:continue
            er=calc("ethbtc",baseline,end,pr);br=calc("btc",baseline,end,pr);xr=calc("eth",baseline,end,pr)
            r[of]="1" if er["forward"]>0 else "0";r[ma]=f'{er["mae"]:.8f}';r[mf]=f'{er["mfe"]:.8f}'
            key=(r["event_id"],h)
            if key not in existing:
                d={"event_id":r["event_id"],"horizon":h,"observation_timestamp_utc":r["observation_timestamp_utc"],"information_cutoff_utc":r["information_cutoff_utc"],"target_timestamp_utc":iso(target),"selected_end_timestamp_utc":iso(end["ts"]),"baseline_timestamp_utc":iso(baseline["ts"]),"ethbtc_baseline":er["baseline"],"ethbtc_end":er["end"],"ethbtc_forward_return_pct":er["forward"],"ethbtc_mae_pct":er["mae"],"ethbtc_mfe_pct":er["mfe"],"btc_baseline":br["baseline"],"btc_end":br["end"],"btc_forward_return_pct":br["forward"],"btc_mae_pct":br["mae"],"btc_mfe_pct":br["mfe"],"eth_baseline":xr["baseline"],"eth_end":xr["end"],"eth_forward_return_pct":xr["forward"],"eth_mae_pct":xr["mae"],"eth_mfe_pct":xr["mfe"],"sample_count":len(pr),"source_contract":"HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT","matured_at_utc":iso(now)}
                d["provenance_hash"]=hashlib.sha256(canon(d).encode()).hexdigest();append_detail(d);existing.add(key)
            changed+=1
    if changed:write_csv(ROWS,rows,fields)
    print(json.dumps({"status":"PASS","rows":len(rows),"horizons_written":changed,"outcome_contract":"ETHBTC_FORWARD_RELATIVE_RETURN_OUTCOME_v1"},sort_keys=True))
if __name__=="__main__":main()
