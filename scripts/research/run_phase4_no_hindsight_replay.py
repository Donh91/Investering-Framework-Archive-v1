#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, csv, datetime as dt, gzip, hashlib, json, math, random, re, statistics
from pathlib import Path

SEED=20260823
RNG=random.Random(SEED)
EP=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/EPISODE_CATALOG.json")
HF=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/hourly_features.csv.gz")
BTC=Path("08_SOURCE_MATERIAL/market_data/etf_flows/2026-07-06__btc_spot_etf_flows_raw_history.csv")
ETH=Path("08_SOURCE_MATERIAL/market_data/etf_flows/2026-07-06__eth_spot_etf_flows_raw_history.csv.gz.b64")
DP=Path("08_SOURCE_MATERIAL/data_ping")
R3=Path("06_RESEARCH_LAB/round3_new_information_v1/PRIMARY_HYPOTHESIS_REGISTRY_v1.json")

def sha(p):
    if not p.exists(): return None
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def jload(p): return json.loads(p.read_text(encoding="utf-8"))

def date(x):
    try: return dt.date.fromisoformat(str(x)[:10])
    except: return None

def ts(x):
    x=str(x or "").strip()
    if not x: return None
    try:
        n=float(x)
        if n>1e12: return dt.datetime.fromtimestamp(n/1000,tz=dt.timezone.utc)
        if n>1e9: return dt.datetime.fromtimestamp(n,tz=dt.timezone.utc)
    except: pass
    try:
        z=dt.datetime.fromisoformat(x.replace("Z","+00:00"))
        if z.tzinfo is None: z=z.replace(tzinfo=dt.timezone.utc)
        return z.astimezone(dt.timezone.utc)
    except: return None

def parse_etf_csv_text(raw):
    out=[]
    for r in csv.DictReader(raw.splitlines()):
        d=date(r.get("ISO_DATE"))
        try: v=float(r.get("Total",""))
        except: continue
        if d and math.isfinite(v): out.append((d,v))
    return sorted(out)

def etf_csv(p):
    try:
        rows=parse_etf_csv_text(p.read_text(encoding="utf-8"))
        return rows,{"status":"PASS","rows":len(rows),"file_sha256":sha(p)}
    except Exception as e:
        return [],{"status":"SOURCE_INTEGRITY_FAIL","error_type":type(e).__name__,"error":str(e),"file_sha256":sha(p)}

def etf_b64(p):
    qa={"file_sha256":sha(p),"status":"SOURCE_INTEGRITY_FAIL","partial_data_allowed":False}
    try:
        text=p.read_text(encoding="utf-8")
        compact="".join(text.split())
        qa["base64_characters"]=len(compact)
        packed=base64.b64decode(compact,validate=True)
        qa["decoded_gzip_bytes"]=len(packed)
        raw=gzip.decompress(packed).decode("utf-8")
        rows=parse_etf_csv_text(raw)
        qa.update(status="PASS",rows=len(rows),decoded_csv_sha256=hashlib.sha256(raw.encode()).hexdigest())
        return rows,qa
    except Exception as e:
        qa.update(error_type=type(e).__name__,error=str(e))
        return [],qa

def detect(header, asset):
    low={h.lower():h for h in header}
    for k in (f"{asset}_close",f"{asset}_close_usd",f"{asset}_price",f"{asset}usd_close",f"{asset}_spot_close",f"{asset}_index_close"):
        if k in low: return low[k]
    for h in header:
        l=h.lower()
        if asset in l and ("close" in l or "price" in l) and not any(q in l for q in ("ret","return","change","pct")):
            return h
    return None

def prices(p):
    info={"available":p.exists(),"path":str(p)}
    if not p.exists(): return {"BTC":{},"ETH":{}},dict(info,usable=False,reason="MISSING_FILE")
    try:
        with gzip.open(p,"rt",encoding="utf-8",newline="") as f:
            rd=csv.DictReader(f); hd=rd.fieldnames or []
            tc=next((h for h in hd if h.lower() in ("timestamp_utc","time_utc","timestamp","datetime","utc","open_time")),None)
            if not tc: tc=next((h for h in hd if "time" in h.lower()),None)
            bc,ec=detect(hd,"btc"),detect(hd,"eth")
            info.update(time_column=tc,btc_column=bc,eth_column=ec)
            if not tc or not bc:
                info.update(usable=False,reason="NO_CONSERVATIVE_TIME_OR_BTC_PRICE_COLUMN")
                return {"BTC":{},"ETH":{}},info
            latest={}
            for r in rd:
                t=ts(r.get(tc))
                if not t: continue
                for a,c in (("BTC",bc),("ETH",ec)):
                    if not c: continue
                    try: px=float(r.get(c,""))
                    except: continue
                    if px<=0 or not math.isfinite(px): continue
                    k=(a,t.date())
                    if k not in latest or t>latest[k][0]: latest[k]=(t,px)
            out={"BTC":{},"ETH":{}}
            for (a,d),(_,px) in latest.items(): out[a][d]=px
            info.update(usable=bool(out["BTC"]),btc_days=len(out["BTC"]),eth_days=len(out["ETH"]),file_sha256=sha(p))
            return out,info
    except Exception as e:
        info.update(usable=False,reason="PRICE_SOURCE_READ_FAIL",error_type=type(e).__name__,error=str(e),file_sha256=sha(p))
        return {"BTC":{},"ETH":{}},info

def roll(rows,n):
    out={}; vals=[]
    for d,v in rows:
        vals.append(v)
        if len(vals)>=n: out[d]=sum(vals[-n:])
    return out

def streak(rows):
    out={}; s=0
    for d,v in rows:
        s=s+1 if v<0 else 0; out[d]=float(s)
    return out

def fut(px,d,h):
    if d not in px:return None
    p0=px[d]; target=d+dt.timedelta(days=h)
    for k in range(5):
        q=px.get(target+dt.timedelta(days=k))
        if q is not None:return q/p0-1
    return None

def rank(x):
    order=sorted(range(len(x)),key=lambda i:x[i]); r=[0.]*len(x); i=0
    while i<len(order):
        q=i+1
        while q<len(order) and x[order[q]]==x[order[i]]:q+=1
        z=(i+1+q)/2
        for k in range(i,q):r[order[k]]=z
        i=q
    return r

def pear(x,y):
    if len(x)<3:return None
    mx,my=statistics.mean(x),statistics.mean(y)
    a=[v-mx for v in x]; b=[v-my for v in y]
    den=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b))
    return None if not den else sum(u*v for u,v in zip(a,b))/den

def spear(x,y): return pear(rank(x),rank(y)) if len(x)>=3 else None

def align(fmap,px,h):
    ds=[];x=[];y=[]
    for d,v in sorted(fmap.items()):
        q=fut(px,d,h)
        if q is not None: ds.append(d);x.append(v);y.append(q)
    return ds,x,y

def yearly(ds,x,y):
    z={}
    for d,a,b in zip(ds,x,y): z.setdefault(d.year,([],[]));z[d.year][0].append(a);z[d.year][1].append(b)
    return {str(k):{"n":len(a),"spearman":spear(a,b)} for k,(a,b) in sorted(z.items())}

def family_test(items,perms=1000):
    obs={k:spear(x,y) for k,(x,y) in items.items()}
    valid={k:(x,y) for k,(x,y) in items.items() if obs[k] is not None}
    if not valid:return obs,{}
    nmin=min(len(y) for x,y in valid.values())
    if nmin<30:return obs,{k:1.0 for k in valid}
    null=[]
    for _ in range(perms):
        sh=RNG.randint(max(5,nmin//10),max(6,nmin-max(5,nmin//10)))
        ss=[]
        for x,y in valid.values():
            s=sh%len(y); yp=y[s:]+y[:s]; q=spear(x,yp)
            if q is not None:ss.append(abs(q))
        null.append(max(ss) if ss else 0.)
    return obs,{k:(1+sum(m>=abs(obs[k]) for m in null))/(1+len(null)) for k in valid}

def lane(rows,px,source_status="PASS"):
    if source_status!="PASS": return {"status":"UNTESTABLE_SOURCE_INTEGRITY_FAIL"}
    if not rows or not px:return {"status":"UNTESTABLE_MISSING_DATA"}
    f={"flow_3session_sum":roll(rows,3),"flow_5session_sum":roll(rows,5),"flow_7session_sum":roll(rows,7),"negative_session_streak":streak(rows)}
    r3=f["flow_3session_sum"]; ds=sorted(r3); f["flow_3session_delta"]={ds[i]:r3[ds[i]]-r3[ds[i-1]] for i in range(1,len(ds))}
    aligned={}; fam={}
    for h in (1,3,7):
        for n,m in f.items():
            d,x,y=align(m,px,h); k=f"{n}__next_{h}d_return";aligned[k]=(d,x,y);fam[k]=(x,y)
    obs,p=family_test(fam)
    tests={k:{"n":len(x),"spearman":obs.get(k),"familywise_circular_shift_p":p.get(k),"by_year":yearly(d,x,y)} for k,(d,x,y) in aligned.items()}
    st=[]
    for i in range(3,len(rows)):
        if sum(v for _,v in rows[i-3:i])<0 and rows[i][1]>=0:st.append(rows[i][0])
    so={}
    for h in (1,3,7):
        v=[fut(px,d,h) for d in st];v=[q for q in v if q is not None]
        so[str(h)]={"n":len(v),"median_return":statistics.median(v) if v else None,"positive_rate":sum(q>0 for q in v)/len(v) if v else None}
    return {"status":"DISCOVERY_ONLY_NO_PROMOTION","continuous_tests":tests,"stabilization":{"definition":"current Total >=0 after prior 3 ETF sessions sum <0","events":len(st),"outcomes":so}}

def pings(root):
    fs=sorted(root.rglob("*.md")) if root.exists() else []; ds=[]
    for p in fs:
        m=re.match(r"(\d{4}-\d{2}-\d{2})",p.name)
        if m and date(m.group(1)):ds.append(date(m.group(1)))
    return {"file_count":len(fs),"dated_file_count":len(ds),"date_min":min(ds).isoformat() if ds else None,"date_max":max(ds).isoformat() if ds else None}

def coverage(rows): return [str(rows[0][0]),str(rows[-1][0])] if rows else None

def modern(cat,cov):
    if not cov:return []
    lo,hi=(date(cov[0]),date(cov[1]))
    return [e["episode_id"] for e in cat.get("episodes",[]) if (d:=date(e.get("top_utc"))) and lo<=d<=hi]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo-root",default=".");ap.add_argument("--output",default="phase4_replay_report.json");ap.add_argument("--self-test",action="store_true");a=ap.parse_args()
    if a.self_test:
        assert rank([1,1,3])==[1.5,1.5,3.0];assert abs(spear([1,2,3],[1,2,3])-1)<1e-12;print("PHASE4_SELF_TEST_PASS");return
    root=Path(a.repo_root).resolve(); rp=lambda p:root/p
    for p in (EP,BTC):
        if not rp(p).exists():raise SystemExit(f"missing required independent input {p}")
    cat=jload(rp(EP)); br,bqa=etf_csv(rp(BTC)); er,eqa=etf_b64(rp(ETH)) if rp(ETH).exists() else ([],{"status":"SOURCE_MISSING","file_sha256":None})
    px,pinfo=prices(rp(HF)); bc,ec=coverage(br),coverage(er); bm,em=modern(cat,bc),modern(cat,ec)
    divres={"status":"UNTESTABLE_SOURCE_INTEGRITY_FAIL"}
    if eqa.get("status")=="PASS" and br and er and px.get("BTC"):
        b3,e3=roll(br,3),roll(er,3); common=sorted(set(b3)&set(e3)&set(px["BTC"]))
        div={d:(1.0 if b3[d]<0<=e3[d] else -1.0 if e3[d]<0<=b3[d] else 0.0) for d in common}
        divres={"status":"DISCOVERY_ONLY_NO_PROMOTION","definition":"sign disagreement of 3-session sums","results":{}}
        for h in (1,3,7):
            d,x,y=align(div,px["BTC"],h);divres["results"][str(h)]={"n":len(x),"spearman":spear(x,y),"by_year":yearly(d,x,y)}
    r3=jload(rp(R3)) if rp(R3).exists() else {}
    min_event_count=min(len(bm),len(em)) if em else 0
    rep={
      "contract":"PHASE4_NO_HINDSIGHT_REPLAY_REPORT_v1","status":"RESEARCH_ONLY_NON_CANONICAL","generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"deterministic_seed":SEED,
      "authority":{"market_state_changes":False,"threshold_changes":False,"weight_changes":False,"portfolio_execution":False,"auto_promotion":False},
      "input_hashes":{"episode_catalog":sha(rp(EP)),"hourly_features":sha(rp(HF)),"btc_etf":sha(rp(BTC)),"eth_etf_b64":sha(rp(ETH)),"round3_registry":sha(rp(R3))},
      "source_qa":{"frozen_episode_count":cat.get("episode_count"),"btc_etf":bqa,"btc_etf_coverage":bc,"eth_etf":eqa,"eth_etf_coverage":ec,"v0_btc_etf_episodes":bm,"v0_eth_etf_episodes":em,"price_source":pinfo,"data_ping_inventory":pings(rp(DP)),"etf_vendor_revision_risk":"KNOWN_POINT_IN_TIME_SOURCE_VERSION_RISK_DO_NOT_SILENTLY_REWRITE"},
      "lanes":{
        "A_provenance_red_team":{"verdict":"SOURCE_INTEGRITY_LIMITATION_RETAINED" if eqa.get("status")!="PASS" else "PASS_WITH_LIMITATIONS","notes":["no missing historical values imputed","no partial ETH gzip recovery accepted","DATA PING treated as contemporaneous evidence only","ETF archive treated as point-in-time source version"]},
        "B_etf_flow_asymmetry":{"BTC":lane(br,px.get("BTC",{}),bqa.get("status")),"ETH":lane(er,px.get("ETH",{}),eqa.get("status"))},
        "C_btc_eth_divergence":divres,
        "D_v0_testability":{"btc_episode_count":len(bm),"eth_episode_count":len(em),"verdict":"INSUFFICIENT_FOR_V0_EVENT_CONTROL_PROMOTION" if min_event_count<10 else "TESTABLE"},
        "E_round3_boundary":{"registry_status":r3.get("status"),"primary_count":r3.get("primary_count"),"verdict":"PROSPECTIVE_ONLY_DO_NOT_BACKFILL_OR_RESCORE"},
        "F_supervisor":{"P4-C01-ETF-PERSISTENCE":"DISCOVERY_ONLY_PENDING_ROBUSTNESS_AND_DECISION_VALUE" if bqa.get("status")=="PASS" else "UNTESTABLE","P4-C02-ETF-STABILIZATION":"DISCOVERY_ONLY_PENDING_ROBUSTNESS_AND_DECISION_VALUE" if bqa.get("status")=="PASS" else "UNTESTABLE","P4-C03-BTC-ETH-ETF-DIVERGENCE":"UNTESTABLE_SOURCE_INTEGRITY_FAIL" if eqa.get("status")!="PASS" else "DISCOVERY_ONLY_PENDING_ROBUSTNESS_AND_DECISION_VALUE","P4-C04-DISPERSION-THEN-BREADTH":"OBSERVE_EXISTING_EVIDENCE_NO_PROMOTION","P4-C05-PRICE-DOWN-OI-UP":"PROSPECTIVE_ONLY","P4-C06-PRICE-OI-SPOT-DIVERGENCE":"PROSPECTIVE_ONLY_SOURCE_COVERAGE_REQUIRED","P4-C07-POST-FLUSH-RECLAIM-OI":"PROSPECTIVE_ONLY","P4-X01-CFGI-ORDERS":"EXPLORATORY_ONLY_INSUFFICIENT_INDEPENDENT_EPISODES"}
      }}
    out=Path(a.output);out=out if out.is_absolute() else root/out;out.write_text(json.dumps(rep,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"output":str(out),"btc_rows":len(br),"btc_source":bqa.get("status"),"eth_rows":len(er),"eth_source":eqa.get("status"),"v0_btc_etf_episodes":len(bm),"v0_eth_etf_episodes":len(em),"price_usable":pinfo.get("usable")},sort_keys=True))
if __name__=="__main__":main()
