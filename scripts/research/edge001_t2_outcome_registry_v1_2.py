#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,gzip,json,hashlib,re
from datetime import datetime,timezone,timedelta
from pathlib import Path

SRC=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/hourly_features.csv.gz")
PARENT=Path("06_RESEARCH_LAB/high_value_edge_research/EDGE-001_TSUNAMI/T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1.json")
PARENT_V11=Path("06_RESEARCH_LAB/high_value_edge_research/EDGE-001_TSUNAMI/T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1_1.json")
WINDOWS=("ALTSEASON_2020_2021","MODERN_ANALOGUE_2025_2026")
GRIDS={"BTCUSDT":(0.10,0.15,0.20),"ETHUSDT":(0.15,0.20,0.30)}
COL={"BTCUSDT":"btc_usdt","ETHUSDT":"eth_usdt"}
PRIMARY={"BTCUSDT":10,"ETHUSDT":15}
FAMILY_DAYS=14

def ts(s): return datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(timezone.utc)
def z(t): return t.isoformat().replace("+00:00","Z")
def norm(s): return re.sub(r"[^A-Za-z0-9]+","",str(s))

def load(path):
    with gzip.open(path,"rt",newline="") as f: rows=list(csv.DictReader(f))
    need={"timestamp_utc","research_window_id","continuity_segment_id","btc_usdt","eth_usdt"}
    if not rows or not need.issubset(rows[0]): raise ValueError("source_schema_invalid")
    return rows

def points(rows,w,a):
    out=[]
    for r in rows:
        if r["research_window_id"]!=w: continue
        v=r.get(COL[a],"")
        if v: out.append({"t":ts(r["timestamp_utc"]),"v":float(v),"seg":r["continuity_segment_id"]})
    out.sort(key=lambda x:x["t"]); return out

def eid(w,a,g,p,c,seg):
    return f"EDGE001_EP_{norm(w)}_{a}_{g}_{norm(seg)}_{norm(z(p))}_{norm(z(c))}"

def make_ep(p,pi,ci,ti,ri,thr,w,a,censored=False,censor_i=None):
    pv=p[pi]["v"]; tv=p[ti]["v"]; g=int(thr*100)
    e={"episode_id":eid(w,a,g,p[pi]["t"],p[ci]["t"],p[pi]["seg"]),"peak_utc":z(p[pi]["t"]),
       "threshold_cross_utc":z(p[ci]["t"]),"trough_utc":z(p[ti]["t"]),
       "rebound_utc":None if ri is None else z(p[ri]["t"]),"peak":pv,"trough":tv,
       "drawdown_pct":(tv/pv-1)*100,"grid_pct":g,"continuity_segment_id":p[pi]["seg"],
       "right_censored":bool(censored),"censor_utc":None,"censor_reason":None,
       "peak_to_cross_h":(p[ci]["t"]-p[pi]["t"]).total_seconds()/3600,
       "peak_to_trough_h":(p[ti]["t"]-p[pi]["t"]).total_seconds()/3600}
    if censored:
        e["censor_utc"]=z(p[censor_i]["t"]); e["censor_reason"]="CONTINUITY_SEGMENT_END_BEFORE_REBOUND"
    return e

def episodes(p,thr,w,a):
    out=[]; start=0
    while start<len(p):
        seg=p[start]["seg"]; peak_i=start; peak=p[start]["v"]; cross=None; trough_i=None; trough=None; i=start+1
        while i<len(p) and p[i]["seg"]==seg:
            v=p[i]["v"]
            if cross is None:
                if v>peak: peak=v; peak_i=i
                elif v<=peak*(1-thr): cross=i; trough_i=i; trough=v
            else:
                if v<trough: trough=v; trough_i=i
                elif v>=trough*(1+thr):
                    out.append(make_ep(p,peak_i,cross,trough_i,i,thr,w,a)); start=i; break
            i+=1
        else:
            end=i-1
            if cross is not None: out.append(make_ep(p,peak_i,cross,trough_i,None,thr,w,a,True,end))
            start=i
            continue
        # rebound break sets start already
    return out

def families(eps,w,a,g):
    es=sorted(eps,key=lambda x:x["peak_utc"]); groups=[]
    for e in es:
        if not groups or e["continuity_segment_id"]!=groups[-1]["seg"]:
            groups.append({"seg":e["continuity_segment_id"],"end":ts(e["trough_utc"]),"eps":[e]}); continue
        cur=groups[-1]; pt=ts(e["peak_utc"])
        if pt<=cur["end"] or pt-cur["end"]<timedelta(days=FAMILY_DAYS):
            cur["eps"].append(e); cur["end"]=max(cur["end"],ts(e["trough_utc"]))
        else: groups.append({"seg":e["continuity_segment_id"],"end":ts(e["trough_utc"]),"eps":[e]})
    out=[]
    for n,x in enumerate(groups,1):
        gg=x["eps"]
        out.append({"family_id":f"EDGE001_FAM_{norm(w)}_{a}_{g}_{n:02d}","episode_count":len(gg),
          "continuity_segment_id":x["seg"],"first_peak_utc":gg[0]["peak_utc"],
          "family_end_trough_utc":z(x["end"]),"first_threshold_cross_utc":min(e["threshold_cross_utc"] for e in gg),
          "deepest_drawdown_pct":min(e["drawdown_pct"] for e in gg),
          "contains_right_censored_episode":any(e["right_censored"] for e in gg),
          "episode_ids":[e["episode_id"] for e in gg]})
    return out

def comparator_fires(p,dd,w,a,label):
    fires=[]; peak=None; peak_t=None; armed=True
    for i,x in enumerate(p):
        if i and x["seg"]!=p[i-1]["seg"]: peak=x["v"];peak_t=x["t"];armed=True;continue
        if peak is None or x["v"]>=peak: peak=x["v"];peak_t=x["t"];armed=True;continue
        if armed and x["v"]<=peak*(1-dd):
            fires.append({"fire_id":f"EDGE001_{label}_{norm(w)}_{a}_{norm(x['seg'])}_{norm(z(x['t']))}",
              "fire_utc":z(x["t"]),"peak_utc":z(peak_t),"peak":peak,"fire_price":x["v"],
              "drawdown_pct":(x["v"]/peak-1)*100,"continuity_segment_id":x["seg"]}); armed=False
    return fires

def controls(p,p1,w,a,primary_thr):
    idx={(x["seg"],z(x["t"])):i for i,x in enumerate(p)}; out=[]
    for f in p1:
        i=idx[(f["continuity_segment_id"],f["fire_utc"])]; deadline=p[i]["t"]+timedelta(days=14)
        crossed=p[i]["v"]<=f["peak"]*(1-primary_thr); regained=None; trough=p[i]["v"]; j=i; censored=False
        while not crossed and j+1<len(p) and p[j+1]["t"]<=deadline:
            if p[j+1]["seg"]!=p[i]["seg"]: censored=True; break
            j+=1; v=p[j]["v"]; trough=min(trough,v)
            if v<=f["peak"]*(1-primary_thr): crossed=True; break
            if v>=f["peak"]: regained=p[j]["t"]; break
        if not crossed and regained is None and p[j]["t"]<deadline:
            if j+1==len(p) or p[j+1]["seg"]!=p[i]["seg"]: censored=True
        cid=f"EDGE001_CTL_{norm(w)}_{a}_VREV_{norm(p[i]['seg'])}_{norm(f['fire_utc'])}"
        if regained and not crossed:
            out.append({"control_id":cid,"control_status":"V_REVERSAL","p1_fire_utc":f["fire_utc"],
              "pre_fire_peak_utc":f["peak_utc"],"recovery_utc":z(regained),"max_drawdown_pct":(trough/f["peak"]-1)*100,
              "continuity_segment_id":p[i]["seg"]})
        elif censored:
            out.append({"control_id":cid,"control_status":"CONTROL_CENSORED","p1_fire_utc":f["fire_utc"],
              "pre_fire_peak_utc":f["peak_utc"],"recovery_utc":None,"max_drawdown_pct":(trough/f["peak"]-1)*100,
              "continuity_segment_id":p[i]["seg"],"censor_utc":z(p[j]["t"]),
              "censor_reason":"DATASET_END_BEFORE_CONTROL_DEADLINE" if j+1==len(p) else "CONTINUITY_SEGMENT_END_BEFORE_CONTROL_DEADLINE"})
    return out

def xclusters(fams,w):
    items=[]
    for asset,fs in fams.items():
        for f in fs:
            items.append({"asset":asset,"family_id":f["family_id"],"start":ts(f["first_peak_utc"]),"end":ts(f["family_end_trough_utc"])})
    items.sort(key=lambda x:x["start"]); groups=[]
    for x in items:
        if not groups or x["start"]>groups[-1]["end"]:
            groups.append({"end":x["end"],"items":[x]})
        else:
            groups[-1]["items"].append(x);groups[-1]["end"]=max(groups[-1]["end"],x["end"])
    return [{"cluster_id":f"EDGE001_XCL_{norm(w)}_{i:02d}","start_utc":z(min(x["start"] for x in g["items"])),
      "end_utc":z(g["end"]),"family_ids":[x["family_id"] for x in g["items"]],
      "assets":sorted(set(x["asset"] for x in g["items"]))} for i,g in enumerate(groups,1)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo-root",type=Path,default=Path("."));ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
    src=a.repo_root/SRC; parent=a.repo_root/PARENT; raw=src.read_bytes(); parent_raw=parent.read_bytes(); rows=load(src)
    parent_v11_raw=(a.repo_root/PARENT_V11).read_bytes()
    if hashlib.sha256(parent_v11_raw).hexdigest()!="b8ffeadecf4a1adf182eac8a5ab163d002af1237c1274cf3e867588977592882": raise ValueError("parent_v11_hash_mismatch")
    result={"contract":"EDGE001_T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1_2","status":"IMMUTABLE_OUTCOME_ONLY_REGISTRY_CONTROL_REPAIR",
      "authority":"RESEARCH_ONLY","source_path":str(SRC),"source_sha256":hashlib.sha256(raw).hexdigest(),
      "parent_v1_path":str(PARENT),"parent_v1_sha256":hashlib.sha256(parent_raw).hexdigest(),
      "parent_v1_1_path":str(PARENT_V11),"parent_v1_1_sha256":hashlib.sha256(parent_v11_raw).hexdigest(),
      "framework_warning_data_joined":False,"method_repair":["TROUGH_BASED_14D_FAMILIES","PRESERVE_SEGMENT_END_RIGHT_CENSORING","STABLE_IDS","PRIMARY_CROSS_ASSET_CLUSTERS","CONTROL_DATASET_END_CENSORING","CONTROL_FIRE_CLOSE_ADVERSE_CHECK"],
      "windows":{},"reconciliation":{}}
    allids=set()
    for w in WINDOWS:
        wo={}; primary_fams={}
        for asset in GRIDS:
            p=points(rows,w,asset); p1=comparator_fires(p,.05,w,asset,"P1");p2=comparator_fires(p,.03,w,asset,"P2")
            ao={"first_utc":z(p[0]["t"]),"last_utc":z(p[-1]["t"]),"row_count":len(p),"P1_fires":p1,"P2_fires":p2,"grids":{}}
            for g in GRIDS[asset]:
                gi=int(g*100); eps=episodes(p,g,w,asset); fs=families(eps,w,asset,gi)
                ao["grids"][str(gi)]={"episodes":eps,"families_14d":fs}
                if gi==PRIMARY[asset]: primary_fams[asset]=fs
                for e in eps:
                    if e["episode_id"] in allids: raise ValueError("duplicate_episode_id")
                    allids.add(e["episode_id"])
                for f in fs:
                    if f["family_id"] in allids: raise ValueError("duplicate_family_id")
                    allids.add(f["family_id"])
            if asset=="BTCUSDT":
                cs=controls(p,p1,w,asset,.10);ao["V_reversal_controls_primary10"]=cs
                for c in cs:
                    if c["control_id"] in allids: raise ValueError("duplicate_control_id")
                    allids.add(c["control_id"])
            wo[asset]=ao
        wo["primary_cross_asset_clusters"]=xclusters(primary_fams,w);result["windows"][w]=wo
    old=json.loads(parent_raw)
    for w in WINDOWS:
        rec={}
        for a2 in GRIDS:
            rec[a2]={}
            for g in map(lambda x:str(int(x*100)),GRIDS[a2]):
                nv=result["windows"][w][a2]["grids"][g];ov=old["windows"][w][a2]["grids"][g]
                rec[a2][g]={"v1_episodes":len(ov["episodes"]),"v1_1_episodes":len(nv["episodes"]),
                  "v1_families":len(ov["families_14d"]),"v1_1_families":len(nv["families_14d"]),
                  "v1_1_right_censored":sum(e["right_censored"] for e in nv["episodes"])}
        rec["primary_cross_asset_cluster_count"]=len(result["windows"][w]["primary_cross_asset_clusters"])
        result["reconciliation"][w]=rec
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","unique_ids":len(allids),"reconciliation":result["reconciliation"]},sort_keys=True))
if __name__=="__main__": main()
