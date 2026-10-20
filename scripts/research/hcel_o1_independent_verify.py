#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, gzip, json, math, statistics
from datetime import datetime, timezone, timedelta
from pathlib import Path

PANEL=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/hourly_features.csv.gz")
TOPS={"EP-01_2021_SPRING_TOP","EP-02_2021_NOV_TOP_CENSORED","EP-03_2025_JAN_TOP","EP-04_2025_OCT_TOP_HOLDOUT"}
CONTROLS={"PB-01_2021_FEB_FALSE_BREAK","CTRL-01_2020Q4_BREAKOUT_LEG","CTRL-02_2021_SUMMER_RECOVERY_LEG","CTRL-03_2025_RECOVERY_LEG"}
EPISODES=[
 ("EP-01_2021_SPRING_TOP","2021-01-01","2021-07-31"),
 ("EP-02_2021_NOV_TOP_CENSORED","2021-08-01","2021-12-31"),
 ("EP-03_2025_JAN_TOP","2025-01-01","2025-06-30"),
 ("EP-04_2025_OCT_TOP_HOLDOUT","2025-07-01","2026-07-31"),
 ("PB-01_2021_FEB_FALSE_BREAK","2021-02-01","2021-04-14"),
 ("CTRL-01_2020Q4_BREAKOUT_LEG","2020-10-01","2021-01-07"),
 ("CTRL-02_2021_SUMMER_RECOVERY_LEG","2021-07-20","2021-11-10"),
 ("CTRL-03_2025_RECOVERY_LEG","2025-04-07","2025-10-06"),
]
ASSETS=("BTC","ETH","ALT_EW")
COSTS=(0,20,50)

def dt(s): return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)
def f(x):
    try:
        v=float(x); return v if math.isfinite(v) else None
    except: return None

def load_daily():
    with gzip.open(PANEL,"rt",newline="") as fh:
        rows=list(csv.DictReader(fh))
    rows.sort(key=lambda r: dt(r["timestamp_utc"]))
    out=[]; cur_window=None; ew=100.0; last_date=None
    seen_date=set()
    # Independent rule: ALT index is rebuilt separately inside each research window.
    for r in rows:
        t=dt(r["timestamp_utc"]); d=t.date(); w=r["research_window_id"]
        if w!=cur_window:
            cur_window=w; ew=100.0; last_date=None
        er=f(r.get("ew_return_1h_pct"))
        if er is not None: ew*=1+er/100.0
        key=(w,d)
        if key in seen_date: continue
        seen_date.add(key)
        out.append({
            "date":d,"ts":t,"window":w,
            "BTC":f(r.get("btc_usdt")),"ETH":f(r.get("eth_usdt")),"ALT_EW":ew,
            "ethbtc":f(r.get("ethbtc")),"breadth":f(r.get("breadth_24h")),
            "fng":f(r.get("free_fng_daily")),"stable":f(r.get("stablecoin_total_usd_daily")),
        })
    # Segment on window change or missing UTC calendar date.
    seg=-1; prev=None
    for x in out:
        if prev is None or x["window"]!=prev["window"] or x["date"]!=prev["date"]+timedelta(days=1):
            seg+=1
        x["segment"]=seg; prev=x
    return out

def window(vals, rows, i, n):
    seg=rows[i]["segment"]
    if i+1<n: return None
    ix=list(range(i+1-n,i+1))
    if any(rows[j]["segment"]!=seg for j in ix): return None
    z=[vals[j] for j in ix]
    if any(v is None for v in z): return None
    return z

def sma(vals,rows,i,n):
    z=window(vals,rows,i,n); return None if z is None else sum(z)/n

def rmax(vals,rows,i,n):
    z=window(vals,rows,i,n); return None if z is None else max(z)

def pchg(vals,rows,i,n):
    if i<n or rows[i]["segment"]!=rows[i-n]["segment"]: return None
    a,b=vals[i],vals[i-n]
    return None if a is None or b in (None,0) else 100*(a/b-1)

def build_features(rows,asset):
    px=[x[asset] for x in rows]; eb=[x["ethbtc"] for x in rows]; br=[x["breadth"] for x in rows]
    fg=[x["fng"] for x in rows]; st=[x["stable"] for x in rows]
    feats=[]
    for i,x in enumerate(rows):
        m90=rmax(px,rows,i,90); p=px[i]
        feats.append({
            "i":i,"date":x["date"],"segment":x["segment"],"px":p,
            "sma50":sma(px,rows,i,50),"sma140":sma(px,rows,i,140),
            "br7":sma(br,rows,i,7),"ethbtc30":pchg(eb,rows,i,30),
            "fng":fg[i],"fng14max":rmax(fg,rows,i,14),"stable30":pchg(st,rows,i,30),
        })
    return feats

class Persist:
    def __init__(self): self.n=0
    def update(self,c):
        if c is None: return self.n
        self.n=self.n+1 if c else 0
        return self.n

def e1_path(feats,s,e):
    below=Persist(); above=Persist(); exp=1.0; out=[]
    for i in range(s,e+1):
        z=feats[i]; sm=z["sma140"]
        if sm is not None and z["px"] is not None:
            b=below.update(z["px"]<sm); a=above.update(z["px"]>sm)
            if exp>0 and b>=2: exp=0.0
            elif exp<1 and a>=2: exp=1.0
        out.append((i,exp))
    return out

def e3_path(feats,s,e):
    p={k:Persist() for k in ("F1","F2","F3","F4","F5")}; f1false=Persist(); hard=False; exp=1.0; out=[]
    mp={0:1.0,1:1.0,2:.75,3:.5,4:.25,5:.25}
    for i in range(s,e+1):
        z=feats[i]
        cond={
          "F1":None if z["sma50"] is None else z["px"]<z["sma50"],
          "F2":None if z["br7"] is None else z["br7"]<.45,
          "F3":None if z["ethbtc30"] is None else z["ethbtc30"]<-10,
          "F4":None if z["fng14max"] is None or z["fng"] is None else (z["fng14max"]>=80 and z["fng"]<=60),
          "F5":None if z["stable30"] is None else z["stable30"]<=0,
        }
        if not all(v is None for v in cond.values()):
            active=sum(1 for k,c in cond.items() if p[k].update(c)>=3)
            f1=p["F1"].n>=3
            f1f=f1false.update(None if cond["F1"] is None else (not cond["F1"]))
            if f1 and active>=3: hard=True
            if hard and f1f>=3: hard=False
            exp=0.0 if hard else mp[active]
        out.append((i,exp))
    return out

def maxdd(path):
    pk=path[0]; m=0.0
    for x in path:
        pk=max(pk,x); m=max(m,1-x/pk)
    return 100*m

def evaluate(rows,feats,asset,start,end,policy,cost):
    ix={x["date"]:i for i,x in enumerate(rows)}
    s=ix[start]; e=ix[end]
    exps=e1_path(feats,s,e) if policy=="E1" else e3_path(feats,s,e)
    px=[x[asset] for x in rows]
    eq=1.0; hold=1.0; prev=1.0; eqpath=[1.0]; holdpath=[1.0]
    for i,ex in exps:
        if ex!=prev: eq*=1-abs(ex-prev)*cost/1e4
        if i<e and px[i] and px[i+1]:
            r=px[i+1]/px[i]-1
            eq*=1+ex*r; hold*=1+r
        eqpath.append(eq); holdpath.append(hold); prev=ex
    return {
      "twr":eq/hold if hold else None,
      "maxdd_policy":maxdd(eqpath),
      "maxdd_hold":maxdd(holdpath),
      "first_exposure_change_date":next((rows[i]["date"].isoformat() for i,ex in exps if ex!=1.0),None),
      "time_out":statistics.mean(1-ex for _,ex in exps),
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",type=Path,required=True); a=ap.parse_args()
    rows=load_daily(); date_to_i={x["date"]:i for i,x in enumerate(rows)}
    features={asset:build_features(rows,asset) for asset in ASSETS}
    result_rows=[]
    for ep,ss,ee in EPISODES:
        sd=datetime.fromisoformat(ss).date(); ed=datetime.fromisoformat(ee).date()
        for asset in ASSETS:
            for cost in COSTS:
                for pol in ("E1","E3"):
                    z=evaluate(rows,features[asset],asset,sd,ed,pol,cost)
                    result_rows.append({"episode":ep,"asset":asset,"cost":cost,"policy":pol,**z})
    scalars={}
    for cost in COSTS:
        scalars[str(cost)]={}
        for pol in ("E1","E3"):
            rr=[r for r in result_rows if r["cost"]==cost and r["policy"]==pol]
            w=[math.log(r["twr"]) for r in rr]
            d=[(r["maxdd_hold"]-r["maxdd_policy"])/100 for r in rr]
            scalars[str(cost)][pol]={
              "WA":statistics.mean(w),
              "WB":statistics.mean(.5*x+.5*y for x,y in zip(w,d)),
              "WC":statistics.mean(.3*x+.7*y for x,y in zip(w,d)),
            }
    warm={}
    b2025=next(i for i,x in enumerate(rows) if x["date"]==datetime(2025,1,1).date())
    for asset in ASSETS:
        ft=features[asset]
        warm[asset]={
          "sma50_first":next((x["date"].isoformat() for x in ft[b2025:] if x["sma50"] is not None),None),
          "sma140_first":next((x["date"].isoformat() for x in ft[b2025:] if x["sma140"] is not None),None),
          "br7_first":next((x["date"].isoformat() for x in ft[b2025:] if x["br7"] is not None),None),
          "ethbtc30_first":next((x["date"].isoformat() for x in ft[b2025:] if x["ethbtc30"] is not None),None),
          "stable30_first":next((x["date"].isoformat() for x in ft[b2025:] if x["stable30"] is not None),None),
        }
    selected=[r for r in result_rows if r["episode"] in ("EP-03_2025_JAN_TOP","CTRL-03_2025_RECOVERY_LEG") and r["cost"]==20]
    out={
      "contract":"HCEL_O1_INDEPENDENT_E1_E3_CONTINUITY_VERIFIER_v1",
      "status":"RESEARCH_ONLY_INDEPENDENT_IMPLEMENTATION",
      "panel":str(PANEL),
      "daily_rows":len(rows),
      "segments":max(x["segment"] for x in rows)+1,
      "warmup_2025":warm,
      "scalars":scalars,
      "selected_cells_cost20":selected,
      "interpretation":[
        "Implementation is independent of Claude's o1_continuity_audit.py and only covers E1/E3.",
        "No original v0 ranking value is used as an input.",
        "This verifies material ranking direction, not every one of the 54 changed cells.",
        "Historical F&G/stablecoin knowledge-time validity is not asserted.",
        "No live rule or portfolio authority."
      ]
    }
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(out,indent=2,default=str)+"\n")
    print(json.dumps({"status":"PASS","scalars":scalars,"selected":selected},default=str))

if __name__=="__main__": main()
