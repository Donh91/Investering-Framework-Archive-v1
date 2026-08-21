#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = "https://cfgi.io/api/v3"
UA = {"User-Agent":"Investering-Historical-Altseason-CFGI/1.1","Accept":"application/json"}
LAB = Path("06_RESEARCH_LAB/historical_altseason_pullback_v1")
ART = LAB / "artifacts"
GAP_AUTH = Path("00_ARCHIVE_CONTROL/research_runtime/HISTORICAL_ALTSEASON_CFGI_MARKET_GAPFILL_AUTHORIZATION.json")
FINGERPRINT = "6106f96285a66f03e324595b68c1777627f4d83e5e70dc6c64d9b1022e544a8f"


def dt(value: str) -> datetime:
    x=datetime.fromisoformat(value.replace("Z","+00:00"))
    return x.astimezone(timezone.utc) if x.tzinfo else x.replace(tzinfo=timezone.utc)


def iso(x: datetime) -> str:
    return x.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")


def request_json(url: str, headers=None, retries=4):
    last=None
    for attempt in range(retries):
        try:
            req=urllib.request.Request(url,headers={**UA,**(headers or {})})
            with urllib.request.urlopen(req,timeout=90) as r:
                body=json.loads(r.read())
                hdr={k:v for k,v in r.headers.items() if k.lower().startswith("x-")}
                return body,hdr
        except urllib.error.HTTPError as exc:
            payload=exc.read().decode(errors="replace")
            if exc.code in {400,401,402,429}:
                raise RuntimeError(f"CFGI_HTTP_{exc.code}:{payload[:400]}") from exc
            last=exc
        except Exception as exc:
            last=exc
        time.sleep(min(8,0.8*(2**attempt)))
    raise RuntimeError(f"CFGI_fetch_failed:{last}")


def int_header(h:dict,key:str):
    for k,v in h.items():
        if k.lower()==key.lower():
            try:return int(v)
            except Exception:return None
    return None


def coverage(symbol:str):
    q=urllib.parse.urlencode({"symbol":symbol})
    try:
        body,_=request_json(f"{BASE}/coverage?{q}")
        return {"symbol":symbol,"status":"PASS","payload":body}
    except Exception as exc:
        return {"symbol":symbol,"status":"UNAVAILABLE","error":str(exc)[:500]}


def budget_probe(key:str,symbol="MARKET"):
    q=urllib.parse.urlencode({"api_key":key,"symbols":symbol,"timeframe":"1h","fields":"score","limit":1})
    body,hdr=request_json(f"{BASE}/scores?{q}")
    return {"credits_used":int_header(hdr,"X-Credits-Used"),"credits_remaining":int_header(hdr,"X-Credits-Remaining"),"headers":hdr,"row_count":len(body.get("data",[]))}


def candidate_events(catalog:dict)->list[dict]:
    c=catalog.get("cfgi_candidate_windows") or {}
    pullbacks=[{"kind":"PULLBACK",**x} for x in c.get("pullbacks",[])]
    controls=[{"kind":"CONTROL",**x} for x in c.get("controls",[])]
    out=[]
    for i in range(max(len(pullbacks),len(controls))):
        if i<len(pullbacks):out.append(pullbacks[i])
        if i<len(controls):out.append(controls[i])
    return out


def merge_intervals(intervals):
    if not intervals:return []
    rows=sorted(intervals);out=[rows[0]]
    for s,e in rows[1:]:
        ps,pe=out[-1]
        if s<=pe+timedelta(hours=1):out[-1]=(ps,max(pe,e))
        else:out.append((s,e))
    return out


def estimated_rows(intervals,symbol_count):
    hours=sum(int((e-s).total_seconds()//3600)+1 for s,e in intervals)
    return hours*symbol_count


def select_events(events,cfg,remaining):
    pre=int(cfg["pre_event_hours"]);post=int(cfg["post_event_hours"])
    fields=len(cfg["fields"]);syms=len(cfg["symbols"])
    hard=int(cfg["expected_credit_hard_cap"]);reserve=int(cfg["minimum_credits_reserve"])
    selected=[];intervals=[]
    for ev in events:
        t=dt(ev["event_utc"])
        trial_intervals=merge_intervals(intervals+[(t-timedelta(hours=pre),t+timedelta(hours=post))])
        est=estimated_rows(trial_intervals,syms)*fields
        if est>hard:continue
        if remaining is not None and remaining-est<reserve:continue
        selected=selected+[ev];intervals=trial_intervals
    return selected,intervals,estimated_rows(intervals,syms)*fields


def split_intervals(intervals,max_hours=240):
    out=[]
    for s,e in intervals:
        cur=s
        while cur<=e:
            ce=min(e,cur+timedelta(hours=max_hours-1));out.append((cur,ce));cur=ce+timedelta(hours=1)
    return out


def fetch_scores(key,cfg,intervals,symbols=None):
    symbols=list(symbols or cfg["symbols"])
    rows=[];receipts=[]
    for idx,(s,e) in enumerate(split_intervals(intervals),start=1):
        q=urllib.parse.urlencode({"api_key":key,"symbols":",".join(symbols),"timeframe":cfg["timeframe"],"fields":",".join(cfg["fields"]),"start":iso(s),"end":iso(e),"static":"true" if cfg.get("static",True) else "false"})
        body,hdr=request_json(f"{BASE}/scores?{q}")
        data=body.get("data",[]);rows.extend(data)
        receipts.append({"chunk":idx,"start":iso(s),"end":iso(e),"row_count":len(data),"requested_symbols":symbols,"x_headers":hdr,"credits_used":int_header(hdr,"X-Credits-Used"),"credits_remaining":int_header(hdr,"X-Credits-Remaining")})
        time.sleep(0.25)
    return rows,receipts


def flatten(row):
    comp=row.get("components") or {}
    out={"symbol":row.get("symbol"),"timestamp":row.get("timestamp"),"score":row.get("score"),"classification":row.get("classification"),"real_price":row.get("price"),"market_cap":row.get("market_cap")}
    for k in ("price","volatility","volume","impulse","technical","social","dominance","trends","whales","orders"):
        out[f"component_{k}"]=comp.get(k)
    return out


def read_flat(path:Path)->list[dict]:
    if not path.exists():return []
    out=[]
    with gzip.open(path,"rt",encoding="utf-8") as fh:
        for line in fh:
            if line.strip():out.append(json.loads(line))
    return out


def write_flat(path:Path,rows:list[dict]):
    rows=sorted(rows,key=lambda r:(r.get("symbol") or "",r.get("timestamp") or ""))
    with gzip.open(path,"wt",encoding="utf-8") as fh:
        for r in rows:fh.write(json.dumps(r,sort_keys=True)+"\n")


def nearest_before(rows_by_symbol,symbol,target):
    best=None
    for r in rows_by_symbol.get(symbol,[]):
        if dt(r["timestamp"])<=target:best=r
        else:break
    return best


def signature_for_event(ev,rows_by_symbol,cfg):
    t=dt(ev["event_utc"]);result={"event":ev,"symbols":{}}
    fields=["score"]+[f"component_{x}" for x in cfg["fields"] if x!="score"]
    for sym in cfg["symbols"]:
        now=nearest_before(rows_by_symbol,sym,t);h6=nearest_before(rows_by_symbol,sym,t-timedelta(hours=6));h24=nearest_before(rows_by_symbol,sym,t-timedelta(hours=24))
        if not now:continue
        sig={"timestamp":now["timestamp"],"classification":now.get("classification"),"real_price":now.get("real_price")}
        for f in fields:
            v=now.get(f);sig[f]=v
            sig[f"{f}_delta_6h"]=None if v is None or not h6 or h6.get(f) is None else float(v)-float(h6[f])
            sig[f"{f}_delta_24h"]=None if v is None or not h24 or h24.get(f) is None else float(v)-float(h24[f])
        result["symbols"][sym]=sig
    return result


def compare_signatures(signatures,cfg):
    metrics=["score"]+[f"component_{x}" for x in cfg["fields"] if x!="score"]
    summary={"contract":"CFGI_PULLBACK_VS_CONTROL_SIGNATURE_v1","metrics":{}}
    for sym in cfg["symbols"]:
        for metric in metrics:
            for suffix in ("","_delta_6h","_delta_24h"):
                key=metric+suffix;p=[];c=[]
                for s in signatures:
                    v=(s.get("symbols",{}).get(sym) or {}).get(key)
                    if v is None:continue
                    (p if s["event"]["kind"]=="PULLBACK" else c).append(float(v))
                summary["metrics"][f"{sym}.{key}"]={"pullback_n":len(p),"control_n":len(c),"pullback_mean":None if not p else sum(p)/len(p),"control_mean":None if not c else sum(c)/len(c),"mean_difference":None if not p or not c else sum(p)/len(p)-sum(c)/len(c)}
    return summary


def rebuild_signatures(output:Path,combined:list[dict],events:list[dict],ccfg:dict):
    bysym={s:sorted([r for r in combined if r.get("symbol")==s],key=lambda r:r.get("timestamp") or "") for s in ccfg["symbols"]}
    signatures=[signature_for_event(ev,bysym,ccfg) for ev in events]
    comparison=compare_signatures(signatures,ccfg)
    (output/"CFGI_EVENT_SIGNATURES.json").write_text(json.dumps({"contract":"CFGI_EVENT_SIGNATURES_v1","events":signatures,"comparison":comparison},indent=2,sort_keys=True)+"\n")


def maybe_market_gapfill(output:Path,cfg:dict,key:str)->bool:
    raw_path=output/"cfgi_targeted.jsonl.gz";cum_path=output/"CFGI_CUMULATIVE_BILLING.json";bill_path=output/"CFGI_BILLING.json"
    if not (raw_path.exists() and cum_path.exists() and bill_path.exists() and GAP_AUTH.exists()):return False
    existing=read_flat(raw_path);present=sorted({str(r.get("symbol")) for r in existing if r.get("symbol")});required=list(cfg["cfgi"]["symbols"]);missing=[s for s in required if s not in present]
    if not missing:return False
    auth=json.loads(GAP_AUTH.read_text());cumulative=json.loads(cum_path.read_text());prior_billing=json.loads(bill_path.read_text())
    if auth.get("contract")!="HISTORICAL_ALTSEASON_CFGI_MARKET_GAPFILL_AUTHORIZATION_v1" or auth.get("input_fingerprint_sha256")!=FINGERPRINT:raise SystemExit("CFGI_GAPFILL_AUTH_INVALID")
    if auth.get("allowed_symbols")!=["MARKET"] or missing!=["MARKET"]:raise SystemExit(f"CFGI_GAPFILL_SCOPE_BLOCKED present={present} missing={missing}")
    if sorted(present)!=["BTC","ETH"]:raise SystemExit(f"CFGI_GAPFILL_PRESERVED_SYMBOLS_INVALID:{present}")
    if cumulative.get("status")!="PASS" or int(cumulative["cumulative_actual_credits_used"])!=10518:raise SystemExit("CFGI_GAPFILL_PRIOR_CUMULATIVE_BILLING_INVALID")
    events=prior_billing.get("selected_events") or [];intervals=[(dt(x["start"]),dt(x["end"])) for x in prior_billing.get("merged_intervals") or []]
    if len(events)!=2 or not intervals:raise SystemExit("CFGI_GAPFILL_FROZEN_EVENTS_OR_INTERVALS_MISSING")
    expected=estimated_rows(intervals,1)*len(cfg["cfgi"]["fields"])+1
    if expected>int(auth["max_worst_case_credits"]):raise SystemExit("CFGI_GAPFILL_AUTHORIZED_CAP_EXCEEDED")
    if int(cumulative["cumulative_actual_credits_used"])+expected>int(cfg["cfgi"]["expected_credit_hard_cap"]):raise SystemExit("CFGI_GAPFILL_CUMULATIVE_HARD_CAP_EXCEEDED")
    if int(cumulative["final_credits_remaining"])-expected<int(cfg["cfgi"]["minimum_credits_reserve"]):raise SystemExit("CFGI_GAPFILL_PROJECTED_RESERVE_BREACH")

    coverage_row=coverage("MARKET");probe=budget_probe(key,"MARKET")
    if probe.get("credits_remaining") is None or int(probe["credits_remaining"])-expected<int(cfg["cfgi"]["minimum_credits_reserve"]):raise SystemExit("CFGI_GAPFILL_LIVE_RESERVE_BREACH")
    raw,receipts=fetch_scores(key,cfg["cfgi"],intervals,symbols=["MARKET"]);flat=[flatten(r) for r in raw];returned=sorted({str(r.get("symbol")) for r in flat if r.get("symbol")})
    if returned!=["MARKET"] or not flat:
        fail={"contract":"CFGI_MARKET_GAPFILL_BILLING_v1","status":"FAIL_PROVIDER_DID_NOT_RETURN_MARKET","requested_symbols":["MARKET"],"returned_symbols":returned,"row_count":len(flat),"request_receipts":receipts,"probe":probe,"input_fingerprint_sha256":FINGERPRINT}
        (output/"CFGI_MARKET_GAPFILL_BILLING.json").write_text(json.dumps(fail,indent=2,sort_keys=True)+"\n")
        raise SystemExit(f"CFGI_MARKET_GAPFILL_PROVIDER_RETURN_INVALID:{returned}:{len(flat)}")
    existing_keys={(r.get("symbol"),r.get("timestamp")) for r in existing}
    if any((r.get("symbol"),r.get("timestamp")) in existing_keys for r in flat):raise SystemExit("CFGI_GAPFILL_UNEXPECTED_RAW_COLLISION")
    combined=existing+flat;write_flat(raw_path,combined);rebuild_signatures(output,combined,events,cfg["cfgi"])
    used=sum(int(x.get("credits_used") or 0) for x in receipts)+int(probe.get("credits_used") or 0);final_remaining=next((int(x["credits_remaining"]) for x in reversed(receipts) if x.get("credits_remaining") is not None),None)
    if final_remaining is None:raise SystemExit("CFGI_GAPFILL_FINAL_RESERVE_HEADER_MISSING")
    new_total=int(cumulative["cumulative_actual_credits_used"])+used
    if new_total>int(cfg["cfgi"]["expected_credit_hard_cap"]) or final_remaining<int(cfg["cfgi"]["minimum_credits_reserve"]):raise SystemExit("CFGI_GAPFILL_POSTCALL_BUDGET_BREACH")
    gap_bill={"contract":"CFGI_MARKET_GAPFILL_BILLING_v1","status":"PASS","generated_at_utc":iso(datetime.now(timezone.utc)),"input_fingerprint_sha256":FINGERPRINT,"billing_scope":"MARKET_ONLY_GAPFILL","requested_symbols":["MARKET"],"forbidden_repurchase_symbols":auth["forbidden_repurchase_symbols"],"preserved_existing_symbols":present,"selected_events":events,"merged_intervals":[{"start":iso(s),"end":iso(e)} for s,e in intervals],"expected_worst_case_credits":expected,"actual_credits_used_from_headers":used,"final_credits_remaining":final_remaining,"request_receipts":receipts,"probe":probe,"coverage":coverage_row,"row_count":len(flat)}
    (output/"CFGI_MARKET_GAPFILL_BILLING.json").write_text(json.dumps(gap_bill,indent=2,sort_keys=True)+"\n")
    billing={"contract":"CFGI_TARGETED_BILLING_v1","status":"PASS","generated_at_utc":gap_bill["generated_at_utc"],"input_fingerprint_contract":"CFGI_TARGETED_INPUT_FINGERPRINT_v1","input_fingerprint_sha256":FINGERPRINT,"billing_scope":"MARKET_ONLY_GAPFILL_AFTER_PRESERVED_BTC_ETH_RECOVERY","probe":probe,"selected_events":events,"merged_intervals":gap_bill["merged_intervals"],"expected_worst_case_credits":expected,"actual_credits_used_from_headers":used,"final_credits_remaining":final_remaining,"hard_cap":cfg["cfgi"]["expected_credit_hard_cap"],"minimum_reserve":cfg["cfgi"]["minimum_credits_reserve"],"request_receipts":receipts,"fields":cfg["cfgi"]["fields"],"symbols":["MARKET"],"timeframe":cfg["cfgi"]["timeframe"],"static":cfg["cfgi"].get("static",True),"preserved_existing_symbols":present}
    bill_path.write_text(json.dumps(billing,indent=2,sort_keys=True)+"\n")
    new_cum={"contract":"HISTORICAL_ALTSEASON_CFGI_CUMULATIVE_BILLING_v1","status":"PASS","input_fingerprint_sha256":FINGERPRINT,"prior_actual_credits_used":int(cumulative["cumulative_actual_credits_used"]),"current_actual_credits_used":used,"cumulative_actual_credits_used":new_total,"hard_cap_credits":cfg["cfgi"]["expected_credit_hard_cap"],"final_credits_remaining":final_remaining,"minimum_reserve_credits":cfg["cfgi"]["minimum_credits_reserve"],"prior_attempt_count":2,"current_attempt_scope":"MARKET_ONLY_GAPFILL","current_run_id":os.environ.get("GITHUB_RUN_ID")}
    cum_path.write_text(json.dumps(new_cum,indent=2,sort_keys=True)+"\n")
    summary_path=output/"BACKTEST_SUMMARY.json";summary=json.loads(summary_path.read_text()) if summary_path.exists() else {};summary.update({"cfgi_status":"TARGETED_ENRICHMENT_COMPLETE_WITH_MARKET_GAPFILL","cfgi_market_gapfill_rows":len(flat),"cfgi_current_actual_credits_used":used,"cfgi_cumulative_actual_credits_used":new_total,"cfgi_final_credits_remaining":final_remaining,"cfgi_input_fingerprint_sha256":FINGERPRINT,"interpretation_status":"DESCRIPTIVE_BOOTSTRAP_NOT_PROMOTED_TO_RULES"});summary_path.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS_MARKET_ONLY_GAPFILL","rows":len(flat),"used":used,"cumulative":new_total,"remaining":final_remaining,"preserved_symbols":present},sort_keys=True));return True


def standard_run(output:Path,cfg:dict,key:str,catalog_path:Path):
    ccfg=cfg["cfgi"];catalog=json.loads(catalog_path.read_text());coverage_rows=[coverage(s) for s in ccfg["symbols"]]
    (output/"CFGI_COVERAGE.json").write_text(json.dumps({"contract":"CFGI_TARGETED_COVERAGE_AUDIT_v1","generated_at_utc":iso(datetime.now(timezone.utc)),"coverage":coverage_rows,"important_limitation":"CFGI history begins after the 2021 altseason study window; no CFGI value is fabricated for 2021."},indent=2,sort_keys=True)+"\n")
    probe=budget_probe(key);remaining=probe.get("credits_remaining");events=candidate_events(catalog);selected,intervals,expected=select_events(events,ccfg,remaining)
    if not selected:
        billing={"contract":"CFGI_TARGETED_BILLING_v1","status":"STOPPED_BY_BUDGET_GUARD","probe":probe,"expected_credits":expected,"selected_events":[],"reserve":ccfg["minimum_credits_reserve"]};(output/"CFGI_BILLING.json").write_text(json.dumps(billing,indent=2,sort_keys=True)+"\n");print(json.dumps(billing,sort_keys=True));return
    raw,receipts=fetch_scores(key,ccfg,intervals);flat=[flatten(r) for r in raw];write_flat(output/"cfgi_targeted.jsonl.gz",flat);rebuild_signatures(output,flat,selected,ccfg)
    used=sum(x.get("credits_used") or 0 for x in receipts)+(probe.get("credits_used") or 0);final_remaining=next((x["credits_remaining"] for x in reversed(receipts) if x.get("credits_remaining") is not None),None)
    billing={"contract":"CFGI_TARGETED_BILLING_v1","status":"PASS","generated_at_utc":iso(datetime.now(timezone.utc)),"probe":probe,"selected_events":selected,"merged_intervals":[{"start":iso(s),"end":iso(e)} for s,e in intervals],"expected_worst_case_credits":expected,"actual_credits_used_from_headers":used,"final_credits_remaining":final_remaining,"hard_cap":ccfg["expected_credit_hard_cap"],"minimum_reserve":ccfg["minimum_credits_reserve"],"request_receipts":receipts,"fields":ccfg["fields"],"symbols":ccfg["symbols"],"timeframe":ccfg["timeframe"],"static":ccfg.get("static",True)};(output/"CFGI_BILLING.json").write_text(json.dumps(billing,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":"PASS","events":len(selected),"rows":len(flat),"used":used,"remaining":final_remaining},sort_keys=True))


def main():
    ap=argparse.ArgumentParser();ap.add_argument("--config",type=Path,default=LAB/"config.json");ap.add_argument("--catalog",type=Path,default=ART/"EPISODE_CATALOG.json");ap.add_argument("--output",type=Path,default=ART);args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True);cfg=json.loads(args.config.read_text());key=os.environ.get("CFGI_API_KEY")
    if not key:raise SystemExit("CFGI_API_KEY_missing")
    if maybe_market_gapfill(args.output,cfg,key):return
    standard_run(args.output,cfg,key,args.catalog)


if __name__=="__main__":main()
