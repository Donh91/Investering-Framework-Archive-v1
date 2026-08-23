#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, csv, datetime as dt, gzip, hashlib, json, math, random, re, statistics
from collections import defaultdict
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
    try:return dt.date.fromisoformat(str(x)[:10])
    except:return None

def ts(x):
    x=str(x or "").strip()
    if not x:return None
    try:
        n=float(x)
        if n>1e12:return dt.datetime.fromtimestamp(n/1000,tz=dt.timezone.utc)
        if n>1e9:return dt.datetime.fromtimestamp(n,tz=dt.timezone.utc)
    except:pass
    try:
        z=dt.datetime.fromisoformat(x.replace("Z","+00:00"))
        if z.tzinfo is None:z=z.replace(tzinfo=dt.timezone.utc)
        return z.astimezone(dt.timezone.utc)
    except:return None

def parse_etf_text(raw):
    records=[]
    for r in csv.DictReader(raw.splitlines()):
        d=date(r.get("ISO_DATE"))
        try:v=float(r.get("Total",""))
        except:continue
        if d and math.isfinite(v):records.append((d,v))
    return records

def normalize_etf(records,file_hash):
    by=defaultdict(list)
    for d,v in records:by[d].append(v)
    duplicate_dates={d:vals for d,vals in by.items() if len(vals)>1}
    conflicting={d:vals for d,vals in duplicate_dates.items() if len(set(vals))>1}
    exact={d:vals for d,vals in duplicate_dates.items() if len(set(vals))==1}
    rows=sorted((d,vals[0]) for d,vals in by.items())
    status="SOURCE_INTEGRITY_FAIL" if conflicting else ("PASS_WITH_EXACT_DUPLICATES" if exact else "PASS")
    qa={
      "status":status,"file_sha256":file_hash,"raw_rows":len(records),"unique_dates":len(rows),
      "duplicate_date_count":len(duplicate_dates),"exact_duplicate_date_count":len(exact),
      "conflicting_duplicate_date_count":len(conflicting),
      "exact_duplicate_dates":[str(x) for x in sorted(exact)],
      "conflicting_duplicate_dates":{str(k):v for k,v in sorted(conflicting.items())},
      "deduplication_policy":"EXACT_IDENTICAL_DATE_TOTAL_ONLY" if exact and not conflicting else "NONE"
    }
    return (rows if not conflicting else []),qa

def etf_csv(p):
    try:return normalize_etf(parse_etf_text(p.read_text(encoding="utf-8")),sha(p))
    except Exception as e:return [],{"status":"SOURCE_INTEGRITY_FAIL","error_type":type(e).__name__,"error":str(e),"file_sha256":sha(p)}

def etf_b64(p):
    qa={"file_sha256":sha(p),"status":"SOURCE_INTEGRITY_FAIL","partial_data_allowed":False}
    try:
        compact="".join(p.read_text(encoding="utf-8").split());qa["base64_characters"]=len(compact)
        packed=base64.b64decode(compact,validate=True);qa["decoded_gzip_bytes"]=len(packed)
        raw=gzip.decompress(packed).decode("utf-8")
        rows,nqa=normalize_etf(parse_etf_text(raw),sha(p));qa.update(nqa)
        qa["decoded_csv_sha256"]=hashlib.sha256(raw.encode()).hexdigest();return rows,qa
    except Exception as e:qa.update(error_type=type(e).__name__,error=str(e));return [],qa

def prices(p):
    info={"available":p.exists(),"path":str(p),"verified_schema_binding":{"BTC":"btc_usdt","ETH":"eth_usdt"}}
    if not p.exists():return {"BTC":{},"ETH":{}},dict(info,usable=False,reason="MISSING_FILE")
    try:
        with gzip.open(p,"rt",encoding="utf-8",newline="") as f:
            rd=csv.DictReader(f);hd=rd.fieldnames or [];tc="timestamp_utc" if "timestamp_utc" in hd else None
            bc="btc_usdt" if "btc_usdt" in hd else None;ec="eth_usdt" if "eth_usdt" in hd else None
            info.update(time_column=tc,btc_column=bc,eth_column=ec,column_count=len(hd))
            if not tc or not bc:
                info.update(usable=False,reason="VERIFIED_SCHEMA_BINDING_MISSING");return {"BTC":{},"ETH":{}},info
            latest={}
            for r in rd:
                t=ts(r.get(tc))
                if not t:continue
                for a,c in (("BTC",bc),("ETH",ec)):
                    if not c:continue
                    try:px=float(r.get(c,""))
                    except:continue
                    if px<=0 or not math.isfinite(px):continue
                    k=(a,t.date())
                    if k not in latest or t>latest[k][0]:latest[k]=(t,px)
            out={"BTC":{},"ETH":{}}
            for (a,d),(_,px) in latest.items():out[a][d]=px
            info.update(usable=bool(out["BTC"]),btc_days=len(out["BTC"]),eth_days=len(out["ETH"]),file_sha256=sha(p))
            return out,info
    except Exception as e:
        info.update(usable=False,reason="PRICE_SOURCE_READ_FAIL",error_type=type(e).__name__,error=str(e),file_sha256=sha(p));return {"BTC":{},"ETH":{}},info

def roll(rows,n):
    vals=[];out={}
    for d,v in rows:
        vals.append(v)
        if len(vals)>=n:out[d]=sum(vals[-n:])
    return out

def streak(rows):
    s=0;out={}
    for d,v in rows:s=s+1 if v<0 else 0;out[d]=float(s)
    return out

def fut(px,d,h):
    if d not in px:return None
    p0=px[d];target=d+dt.timedelta(days=h)
    for k in range(5):
        q=px.get(target+dt.timedelta(days=k))
        if q is not None:return q/p0-1
    return None

def rank(x):
    order=sorted(range(len(x)),key=lambda i:x[i]);r=[0.]*len(x);i=0
    while i<len(order):
        q=i+1
        while q<len(order) and x[order[q]]==x[order[i]]:q+=1
        z=(i+1+q)/2
        for k in range(i,q):r[order[k]]=z
        i=q
    return r

def pear(x,y):
    if len(x)<3:return None
    mx,my=statistics.mean(x),statistics.mean(y);a=[v-mx for v in x];b=[v-my for v in y]
    den=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b));return None if not den else sum(u*v for u,v in zip(a,b))/den

def spear(x,y):return pear(rank(x),rank(y)) if len(x)>=3 else None

def partial_spear(x,y,z):
    if len(x)<4 or len(x)!=len(y) or len(x)!=len(z):return None
    xy,xz,yz=spear(x,y),spear(x,z),spear(y,z)
    if None in (xy,xz,yz):return None
    den=math.sqrt(max(0.0,(1-xz*xz)*(1-yz*yz)))
    return None if den==0 else (xy-xz*yz)/den

def align(feature,px,h,baseline=None):
    ds=[];x=[];y=[];z=[]
    for d,v in sorted(feature.items()):
        q=fut(px,d,h)
        if q is None or (baseline is not None and d not in baseline):continue
        ds.append(d);x.append(v);y.append(q)
        if baseline is not None:z.append(baseline[d])
    return ds,x,y,z

def yearly(ds,x,y):
    by={}
    for d,a,b in zip(ds,x,y):by.setdefault(d.year,([],[]));by[d.year][0].append(a);by[d.year][1].append(b)
    return {str(k):{"n":len(a),"spearman":spear(a,b)} for k,(a,b) in sorted(by.items())}

def family_test(items,perms=1000):
    obs={k:spear(x,y) for k,(x,y) in items.items()};valid={k:(x,y) for k,(x,y) in items.items() if obs[k] is not None}
    if not valid:return obs,{}
    nmin=min(len(y) for x,y in valid.values())
    if nmin<30:return obs,{k:1.0 for k in valid}
    null=[]
    for _ in range(perms):
        sh=RNG.randint(max(5,nmin//10),max(6,nmin-max(5,nmin//10)));mx=0.0
        for x,y in valid.values():
            s=sh%len(y);q=spear(x,y[s:]+y[:s]);mx=max(mx,abs(q or 0.0))
        null.append(mx)
    return obs,{k:(1+sum(m>=abs(obs[k]) for m in null))/(1+len(null)) for k in valid}

def lane(rows,px,source_status):
    if source_status not in ("PASS","PASS_WITH_EXACT_DUPLICATES"):return {"status":"UNTESTABLE_SOURCE_INTEGRITY_FAIL"}
    if not rows or not px:return {"status":"UNTESTABLE_MISSING_DATA"}
    single={d:v for d,v in rows}
    features={"single_print":single,"flow_3session_sum":roll(rows,3),"flow_5session_sum":roll(rows,5),"flow_7session_sum":roll(rows,7),"negative_session_streak":streak(rows)}
    r3=features["flow_3session_sum"];ds=sorted(r3);features["flow_3session_delta"]={ds[i]:r3[ds[i]]-r3[ds[i-1]] for i in range(1,len(ds))}
    raw={};fam={}
    for h in (1,3,7):
        for name,feature in features.items():
            d,x,y,z=align(feature,px,h,single if name!="single_print" else None);k=f"{name}__next_{h}d_return";raw[k]=(d,x,y,z);fam[k]=(x,y)
    obs,p=family_test(fam)
    tests={}
    for k,(d,x,y,z) in raw.items():
        name=k.split("__")[0]
        tests[k]={"n":len(x),"spearman":obs.get(k),"familywise_circular_shift_p":p.get(k),"by_year":yearly(d,x,y),"partial_spearman_vs_single_print":None if name=="single_print" else partial_spear(x,y,z)}
    st=[]
    for i in range(3,len(rows)):
        if sum(v for _,v in rows[i-3:i])<0 and rows[i][1]>=0:st.append(rows[i][0])
    so={}
    for h in (1,3,7):
        vals=[fut(px,d,h) for d in st];vals=[v for v in vals if v is not None]
        so[str(h)]={"n":len(vals),"median_return":statistics.median(vals) if vals else None,"positive_rate":sum(v>0 for v in vals)/len(vals) if vals else None}
    return {"status":"DISCOVERY_ONLY_NO_PROMOTION","baseline":"single_print","continuous_tests":tests,"stabilization":{"definition":"current Total >=0 after prior 3 ETF sessions sum <0","events":len(st),"outcomes":so}}

def pings(root):
    fs=sorted(root.rglob("*.md")) if root.exists() else [];ds=[]
    for p in fs:
        m=re.match(r"(\d{4}-\d{2}-\d{2})",p.name)
        if m and date(m.group(1)):ds.append(date(m.group(1)))
    return {"file_count":len(fs),"dated_file_count":len(ds),"date_min":min(ds).isoformat() if ds else None,"date_max":max(ds).isoformat() if ds else None}

def coverage(rows):return [str(rows[0][0]),str(rows[-1][0])] if rows else None

def modern(cat,cov):
    if not cov:return []
    lo,hi=map(date,cov);return [e["episode_id"] for e in cat.get("episodes",[]) if (d:=date(e.get("top_utc"))) and lo<=d<=hi]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo-root",default=".");ap.add_argument("--output",default="phase4_replay_report.json");ap.add_argument("--self-test",action="store_true");a=ap.parse_args()
    if a.self_test:
        assert rank([1,1,3])==[1.5,1.5,3.0];assert abs(spear([1,2,3],[1,2,3])-1)<1e-12;print("PHASE4_SELF_TEST_PASS");return
    root=Path(a.repo_root).resolve();rp=lambda p:root/p
    for p in (EP,BTC):
        if not rp(p).exists():raise SystemExit(f"missing required independent input {p}")
    cat=jload(rp(EP));br,bqa=etf_csv(rp(BTC));er,eqa=etf_b64(rp(ETH)) if rp(ETH).exists() else ([],{"status":"SOURCE_MISSING"});px,pinfo=prices(rp(HF))
    bc,ec=coverage(br),coverage(er);bm,em=modern(cat,bc),modern(cat,ec)
    div={"status":"UNTESTABLE_SOURCE_INTEGRITY_FAIL"}
    if eqa.get("status") in ("PASS","PASS_WITH_EXACT_DUPLICATES") and br and er and px.get("BTC"):
        b3,e3=roll(br,3),roll(er,3);common=sorted(set(b3)&set(e3)&set(px["BTC"]));state={d:(1.0 if b3[d]<0<=e3[d] else -1.0 if e3[d]<0<=b3[d] else 0.0) for d in common};res={}
        for h in (1,3,7):
            d,x,y,_=align(state,px["BTC"],h);res[str(h)]={"n":len(x),"spearman":spear(x,y),"by_year":yearly(d,x,y)}
        div={"status":"DISCOVERY_ONLY_NO_PROMOTION","definition":"sign disagreement of 3-session sums","results":res}
    r3=jload(rp(R3)) if rp(R3).exists() else {};min_events=min(len(bm),len(em)) if em else 0
    rep={
      "contract":"PHASE4_NO_HINDSIGHT_REPLAY_REPORT_v1","status":"RESEARCH_ONLY_NON_CANONICAL","generated_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"deterministic_seed":SEED,
      "authority":{"market_state_changes":False,"threshold_changes":False,"weight_changes":False,"portfolio_execution":False,"auto_promotion":False},
      "input_hashes":{"episode_catalog":sha(rp(EP)),"hourly_features":sha(rp(HF)),"btc_etf":sha(rp(BTC)),"eth_etf_b64":sha(rp(ETH)),"round3_registry":sha(rp(R3))},
      "source_qa":{"frozen_episode_count":cat.get("episode_count"),"btc_etf":bqa,"btc_etf_coverage":bc,"eth_etf":eqa,"eth_etf_coverage":ec,"v0_btc_etf_episodes":bm,"v0_eth_etf_episodes":em,"price_source":pinfo,"data_ping_inventory":pings(rp(DP)),"etf_vendor_revision_risk":"KNOWN_POINT_IN_TIME_SOURCE_VERSION_RISK_DO_NOT_SILENTLY_REWRITE"},
      "lanes":{
        "A_provenance_red_team":{"verdict":"SOURCE_LIMITATIONS_RETAINED","notes":["no missing historical values imputed","only exact identical BTC date/Total duplicates may be deterministically collapsed","conflicting duplicates fail closed","no partial ETH gzip recovery accepted","DATA PING treated as contemporaneous evidence only","ETF archive treated as point-in-time source version"]},
        "B_etf_flow_asymmetry":{"BTC":lane(br,px.get("BTC",{}),bqa.get("status")),"ETH":lane(er,px.get("ETH",{}),eqa.get("status"))},
        "C_btc_eth_divergence":div,
        "D_v0_testability":{"btc_episode_count":len(bm),"eth_episode_count":len(em),"verdict":"INSUFFICIENT_FOR_V0_EVENT_CONTROL_PROMOTION" if min_events<10 else "TESTABLE"},
        "E_round3_boundary":{"registry_status":r3.get("status"),"primary_count":r3.get("primary_count"),"verdict":"PROSPECTIVE_ONLY_DO_NOT_BACKFILL_OR_RESCORE"},
        "F_supervisor":{"P4-C01-ETF-PERSISTENCE":"DISCOVERY_ONLY_PENDING_INDEPENDENT_EVENT_EVIDENCE_AND_DECISION_VALUE" if bqa.get("status") in ("PASS","PASS_WITH_EXACT_DUPLICATES") else "UNTESTABLE","P4-C02-ETF-STABILIZATION":"DISCOVERY_ONLY_PENDING_INDEPENDENT_EVENT_EVIDENCE_AND_DECISION_VALUE" if bqa.get("status") in ("PASS","PASS_WITH_EXACT_DUPLICATES") else "UNTESTABLE","P4-C03-BTC-ETH-ETF-DIVERGENCE":"UNTESTABLE_SOURCE_INTEGRITY_FAIL" if eqa.get("status") not in ("PASS","PASS_WITH_EXACT_DUPLICATES") else "DISCOVERY_ONLY","P4-C04-DISPERSION-THEN-BREADTH":"OBSERVE_EXISTING_EVIDENCE_NO_PROMOTION","P4-C05-PRICE-DOWN-OI-UP":"PROSPECTIVE_ONLY","P4-C06-PRICE-OI-SPOT-DIVERGENCE":"PROSPECTIVE_ONLY_SOURCE_COVERAGE_REQUIRED","P4-C07-POST-FLUSH-RECLAIM-OI":"PROSPECTIVE_ONLY","P4-X01-CFGI-ORDERS":"EXPLORATORY_ONLY_INSUFFICIENT_INDEPENDENT_EPISODES"}
      }}
    out=Path(a.output);out=out if out.is_absolute() else root/out;out.write_text(json.dumps(rep,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"output":str(out),"btc_rows_used":len(br),"btc_source":bqa.get("status"),"btc_duplicate_dates":bqa.get("duplicate_date_count"),"eth_rows":len(er),"eth_source":eqa.get("status"),"v0_btc_etf_episodes":len(bm),"v0_eth_etf_episodes":len(em),"price_usable":pinfo.get("usable")},sort_keys=True))
if __name__=="__main__":main()
