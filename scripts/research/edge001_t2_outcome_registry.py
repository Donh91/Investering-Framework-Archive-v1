#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,gzip,json,hashlib
from datetime import datetime,timezone,timedelta
from pathlib import Path

# T2 outcome membership is frozen before any Framework signal join.
SRC=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/hourly_features.csv.gz")
WINDOWS=("ALTSEASON_2020_2021","MODERN_ANALOGUE_2025_2026")
GRIDS={"BTCUSDT":(0.10,0.15,0.20),"ETHUSDT":(0.15,0.20,0.30)}
COL={"BTCUSDT":"btc_usdt","ETHUSDT":"eth_usdt"}
FAMILY_DAYS=14

def ts(s): return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)
def z(t): return t.isoformat().replace("+00:00","Z")

def load(path):
    with gzip.open(path,"rt",newline="") as f: rows=list(csv.DictReader(f))
    need={"timestamp_utc","research_window_id","continuity_segment_id","btc_usdt","eth_usdt"}
    if not rows or not need.issubset(rows[0]): raise ValueError("source_schema_invalid")
    return rows

def points(rows,window,asset):
    out=[]
    for r in rows:
        if r["research_window_id"]!=window: continue
        v=r.get(COL[asset],"")
        if not v: continue
        out.append({"t":ts(r["timestamp_utc"]),"v":float(v),"seg":r["continuity_segment_id"]})
    out.sort(key=lambda x:x["t"])
    return out

def episodes(p,thr):
    out=[]; start=0
    while start<len(p):
        peak_i=start; peak=p[start]["v"]; cross=None; trough_i=None; trough=None
        i=start+1
        while i<len(p):
            if p[i]["seg"]!=p[i-1]["seg"]:
                start=i; break
            v=p[i]["v"]
            if cross is None:
                if v>peak: peak=v; peak_i=i
                elif v<=peak*(1-thr): cross=i; trough_i=i; trough=v
            else:
                if v<trough: trough=v; trough_i=i
                elif v>=trough*(1+thr):
                    out.append(make_ep(p,peak_i,cross,trough_i,i,thr,False))
                    start=i; break
            i+=1
        else:
            if cross is not None: out.append(make_ep(p,peak_i,cross,trough_i,None,thr,True))
            break
    return out

def make_ep(p,pi,ci,ti,ri,thr,open_):
    pv=p[pi]["v"]; tv=p[ti]["v"]
    return {"peak_utc":z(p[pi]["t"]),"threshold_cross_utc":z(p[ci]["t"]),"trough_utc":z(p[ti]["t"]),
      "rebound_utc":None if ri is None else z(p[ri]["t"]),"peak":pv,"trough":tv,
      "drawdown_pct":(tv/pv-1)*100,"grid_pct":int(thr*100),"continuity_segment_id":p[pi]["seg"],
      "open_right_censored":open_,"peak_to_cross_h":(p[ci]["t"]-p[pi]["t"]).total_seconds()/3600,
      "peak_to_trough_h":(p[ti]["t"]-p[pi]["t"]).total_seconds()/3600}

def families(eps):
    if not eps:return []
    es=sorted(eps,key=lambda x:x["peak_utc"]); groups=[[es[0]]]
    for e in es[1:]:
        prev=groups[-1][-1]
        if ts(e["peak_utc"])-ts(prev["peak_utc"])<timedelta(days=FAMILY_DAYS): groups[-1].append(e)
        else: groups.append([e])
    out=[]
    for n,g in enumerate(groups,1):
        out.append({"family_id":f"F{n:02d}","episode_count":len(g),"first_peak_utc":g[0]["peak_utc"],
          "last_peak_utc":g[-1]["peak_utc"],"first_threshold_cross_utc":min(x["threshold_cross_utc"] for x in g),
          "deepest_drawdown_pct":min(x["drawdown_pct"] for x in g),"episodes":g})
    return out

def comparator_fires(p,dd):
    fires=[]; peak=None; peak_t=None; armed=True
    for i,x in enumerate(p):
        if i and x["seg"]!=p[i-1]["seg"]: peak=x["v"]; peak_t=x["t"]; armed=True; continue
        if peak is None or x["v"]>=peak:
            peak=x["v"]; peak_t=x["t"]; armed=True; continue
        if armed and x["v"]<=peak*(1-dd):
            fires.append({"fire_utc":z(x["t"]),"peak_utc":z(peak_t),"peak":peak,"fire_price":x["v"],
              "drawdown_pct":(x["v"]/peak-1)*100,"continuity_segment_id":x["seg"]})
            armed=False
        # causal reset only on regain/equal prior peak, handled above
    return fires

def controls(p,p1,primary_thr):
    # outcome-only V-reversal controls: P1 fires, regains causal pre-fire peak within 14d, never reaches primary grid first.
    by_t={z(x["t"]):i for i,x in enumerate(p)}; out=[]
    for f in p1:
        i=by_t.get(f["fire_utc"])
        if i is None: continue
        deadline=p[i]["t"]+timedelta(days=14); crossed=False; regained=None; trough=p[i]["v"]
        j=i
        while j+1<len(p) and p[j+1]["t"]<=deadline and p[j+1]["seg"]==p[i]["seg"]:
            j+=1; v=p[j]["v"]; trough=min(trough,v)
            if v<=f["peak"]*(1-primary_thr): crossed=True; break
            if v>=f["peak"]: regained=p[j]["t"]; break
        if regained and not crossed:
            out.append({"control_type":"V_REVERSAL","p1_fire_utc":f["fire_utc"],"pre_fire_peak_utc":f["peak_utc"],
              "recovery_utc":z(regained),"max_drawdown_pct":(trough/f["peak"]-1)*100,
              "continuity_segment_id":f["continuity_segment_id"]})
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo-root",type=Path,default=Path("."));ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
    src=a.repo_root/SRC; raw=src.read_bytes(); rows=load(src)
    result={"contract":"EDGE001_T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1","status":"IMMUTABLE_OUTCOME_ONLY_REGISTRY",
      "authority":"RESEARCH_ONLY","source_path":str(SRC),"source_sha256":hashlib.sha256(raw).hexdigest(),
      "framework_warning_data_joined":False,"primary_cell":{"asset":"BTCUSDT","grid_pct":10,"family_gap_days":14,
      "comparator":"P1_5PCT_CAUSAL_RUNNING_PEAK","warning_identity":"NOT_JOINED_IN_T2"},
      "comparator_contract":{"P1_drawdown_pct":5,"P2_sensitivity_pct":3,
      "reset":"ONLY_WHEN_ELIGIBLE_HOURLY_CLOSE_REGAINS_OR_EXCEEDS_PRIOR_RUNNING_PEAK","gap":"BREAK_AND_RESTART"},
      "windows":{},"interpretation":["Episode membership is outcome-only and frozen before any Framework warning join.",
      "This registry is not evidence of Framework skill.","Current typed historical Claim A remains NOT_TESTABLE_AT_PIT if no typed adverse family exists."]}
    for w in WINDOWS:
        wo={}
        for asset in GRIDS:
            p=points(rows,w,asset); p1=comparator_fires(p,.05); p2=comparator_fires(p,.03)
            ao={"first_utc":z(p[0]["t"]),"last_utc":z(p[-1]["t"]),"row_count":len(p),
                "P1_fires":p1,"P2_fires":p2,"grids":{}}
            for g in GRIDS[asset]:
                eps=episodes(p,g); ao["grids"][str(int(g*100))]={"episodes":eps,"families_14d":families(eps)}
            if asset=="BTCUSDT": ao["V_reversal_controls_primary10"]=controls(p,p1,.10)
            wo[asset]=ao
        result["windows"][w]=wo
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    summary={}
    for w,wo in result["windows"].items():
        summary[w]={}
        for asset,ao in wo.items():
            summary[w][asset]={"P1":len(ao["P1_fires"]),"P2":len(ao["P2_fires"]),
              "families":{g:len(v["families_14d"]) for g,v in ao["grids"].items()},
              "v_reversal_controls":len(ao.get("V_reversal_controls_primary10",[]))}
    print(json.dumps({"status":"PASS","summary":summary},sort_keys=True))
if __name__=="__main__": main()
