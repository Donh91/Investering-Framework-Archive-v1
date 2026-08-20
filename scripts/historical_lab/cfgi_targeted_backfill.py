#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = "https://cfgi.io/api/v3"
UA = {"User-Agent": "Investering-Historical-Altseason-CFGI/1.0", "Accept": "application/json"}


def dt(value: str) -> datetime:
    x = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return x if x.tzinfo else x.replace(tzinfo=timezone.utc)


def iso(x: datetime) -> str:
    return x.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def request_json(url: str, headers=None, retries=4):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={**UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=90) as r:
                body = json.loads(r.read())
                hdr = {k: v for k, v in r.headers.items() if k.lower().startswith("x-")}
                return body, hdr
        except urllib.error.HTTPError as exc:
            payload = exc.read().decode(errors="replace")
            if exc.code in {400, 401, 402, 429}:
                raise RuntimeError(f"CFGI_HTTP_{exc.code}:{payload[:400]}") from exc
            last = exc
        except Exception as exc:
            last = exc
        time.sleep(min(8, 0.8 * (2 ** attempt)))
    raise RuntimeError(f"CFGI_fetch_failed:{last}")


def int_header(h: dict, key: str):
    for k, v in h.items():
        if k.lower() == key.lower():
            try: return int(v)
            except Exception: return None
    return None


def coverage(symbol: str):
    q = urllib.parse.urlencode({"symbol": symbol})
    try:
        body, _ = request_json(f"{BASE}/coverage?{q}")
        return {"symbol": symbol, "status": "PASS", "payload": body}
    except Exception as exc:
        return {"symbol": symbol, "status": "UNAVAILABLE", "error": str(exc)[:500]}


def budget_probe(key: str, symbol="MARKET"):
    q = urllib.parse.urlencode({
        "api_key": key,
        "symbols": symbol,
        "timeframe": "1h",
        "fields": "score",
        "limit": 1,
    })
    body, hdr = request_json(f"{BASE}/scores?{q}")
    return {
        "credits_used": int_header(hdr, "X-Credits-Used"),
        "credits_remaining": int_header(hdr, "X-Credits-Remaining"),
        "headers": hdr,
        "row_count": len(body.get("data", [])),
    }


def candidate_events(catalog: dict) -> list[dict]:
    c = catalog.get("cfgi_candidate_windows") or {}
    pullbacks = [{"kind": "PULLBACK", **x} for x in c.get("pullbacks", [])]
    controls = [{"kind": "CONTROL", **x} for x in c.get("controls", [])]
    out = []
    for i in range(max(len(pullbacks), len(controls))):
        if i < len(pullbacks): out.append(pullbacks[i])
        if i < len(controls): out.append(controls[i])
    return out


def merge_intervals(intervals: list[tuple[datetime, datetime]]) -> list[tuple[datetime, datetime]]:
    if not intervals: return []
    rows = sorted(intervals)
    out = [rows[0]]
    for s, e in rows[1:]:
        ps, pe = out[-1]
        if s <= pe + timedelta(hours=1): out[-1] = (ps, max(pe, e))
        else: out.append((s, e))
    return out


def estimated_rows(intervals, symbol_count):
    hours = sum(int((e - s).total_seconds() // 3600) + 1 for s, e in intervals)
    return hours * symbol_count


def select_events(events: list[dict], cfg: dict, remaining: int | None):
    pre = int(cfg["pre_event_hours"]); post = int(cfg["post_event_hours"])
    fields = len(cfg["fields"]); syms = len(cfg["symbols"])
    hard = int(cfg["expected_credit_hard_cap"]); reserve = int(cfg["minimum_credits_reserve"])
    selected=[]; intervals=[]
    for ev in events:
        t = dt(ev["event_utc"])
        trial_events = selected + [ev]
        trial_intervals = merge_intervals(intervals + [(t-timedelta(hours=pre), t+timedelta(hours=post))])
        est = estimated_rows(trial_intervals, syms) * fields
        if est > hard: continue
        if remaining is not None and remaining - est < reserve: continue
        selected = trial_events; intervals = trial_intervals
    return selected, intervals, estimated_rows(intervals, syms) * fields


def split_intervals(intervals, max_hours=240):
    out=[]
    for s,e in intervals:
        cur=s
        while cur<=e:
            ce=min(e, cur+timedelta(hours=max_hours-1))
            out.append((cur,ce)); cur=ce+timedelta(hours=1)
    return out


def fetch_scores(key: str, cfg: dict, intervals: list[tuple[datetime,datetime]]):
    rows=[]; receipts=[]
    for idx,(s,e) in enumerate(split_intervals(intervals), start=1):
        q = urllib.parse.urlencode({
            "api_key": key,
            "symbols": ",".join(cfg["symbols"]),
            "timeframe": cfg["timeframe"],
            "fields": ",".join(cfg["fields"]),
            "start": iso(s),
            "end": iso(e),
            "static": "true" if cfg.get("static", True) else "false",
        })
        body,hdr=request_json(f"{BASE}/scores?{q}")
        data=body.get("data",[])
        rows.extend(data)
        receipts.append({
            "chunk":idx,"start":iso(s),"end":iso(e),"row_count":len(data),
            "x_headers":hdr,
            "credits_used":int_header(hdr,"X-Credits-Used"),
            "credits_remaining":int_header(hdr,"X-Credits-Remaining"),
        })
        time.sleep(0.25)
    return rows,receipts


def flatten(row: dict):
    comp=row.get("components") or {}
    out={
        "symbol":row.get("symbol"),"timestamp":row.get("timestamp"),
        "score":row.get("score"),"classification":row.get("classification"),
        "real_price":row.get("price"),"market_cap":row.get("market_cap"),
    }
    for k in ("price","volatility","volume","impulse","technical","social","dominance","trends","whales","orders"):
        out[f"component_{k}"]=comp.get(k)
    return out


def nearest_before(rows_by_symbol: dict[str,list[dict]], symbol: str, target: datetime):
    rows=rows_by_symbol.get(symbol,[]); best=None
    for r in rows:
        t=dt(r["timestamp"])
        if t<=target: best=r
        else: break
    return best


def signature_for_event(ev: dict, rows_by_symbol: dict[str,list[dict]], cfg: dict):
    t=dt(ev["event_utc"]); result={"event":ev,"symbols":{}}
    fields=["score"]+[f"component_{x}" for x in cfg["fields"] if x!="score"]
    for sym in cfg["symbols"]:
        now=nearest_before(rows_by_symbol,sym,t)
        h6=nearest_before(rows_by_symbol,sym,t-timedelta(hours=6))
        h24=nearest_before(rows_by_symbol,sym,t-timedelta(hours=24))
        if not now: continue
        sig={"timestamp":now["timestamp"],"classification":now.get("classification"),"real_price":now.get("real_price")}
        for f in fields:
            v=now.get(f); sig[f]=v
            sig[f"{f}_delta_6h"]=None if v is None or not h6 or h6.get(f) is None else float(v)-float(h6[f])
            sig[f"{f}_delta_24h"]=None if v is None or not h24 or h24.get(f) is None else float(v)-float(h24[f])
        result["symbols"][sym]=sig
    return result


def compare_signatures(signatures: list[dict], cfg: dict):
    metrics=["score"]+[f"component_{x}" for x in cfg["fields"] if x!="score"]
    summary={"contract":"CFGI_PULLBACK_VS_CONTROL_SIGNATURE_v1","metrics":{}}
    for sym in cfg["symbols"]:
        for metric in metrics:
            for suffix in ("", "_delta_6h", "_delta_24h"):
                key=metric+suffix; p=[]; c=[]
                for s in signatures:
                    v=(s.get("symbols",{}).get(sym) or {}).get(key)
                    if v is None: continue
                    (p if s["event"]["kind"]=="PULLBACK" else c).append(float(v))
                summary["metrics"][f"{sym}.{key}"]={
                    "pullback_n":len(p),"control_n":len(c),
                    "pullback_mean":None if not p else sum(p)/len(p),
                    "control_mean":None if not c else sum(c)/len(c),
                    "mean_difference":None if not p or not c else sum(p)/len(p)-sum(c)/len(c),
                }
    return summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--config",type=Path,default=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/config.json"))
    ap.add_argument("--catalog",type=Path,default=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/EPISODE_CATALOG.json"))
    ap.add_argument("--output",type=Path,default=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts"))
    args=ap.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    cfg=json.loads(args.config.read_text()); ccfg=cfg["cfgi"]
    key=os.environ.get("CFGI_API_KEY")
    if not key: raise SystemExit("CFGI_API_KEY_missing")
    catalog=json.loads(args.catalog.read_text())

    coverage_rows=[coverage(s) for s in ccfg["symbols"]]
    (args.output/"CFGI_COVERAGE.json").write_text(json.dumps({
        "contract":"CFGI_TARGETED_COVERAGE_AUDIT_v1","generated_at_utc":iso(datetime.now(timezone.utc)),
        "coverage":coverage_rows,"important_limitation":"CFGI history begins after the 2021 altseason study window; no CFGI value is fabricated for 2021."
    },indent=2,sort_keys=True)+"\n")

    probe=budget_probe(key)
    remaining=probe.get("credits_remaining")
    events=candidate_events(catalog)
    selected,intervals,expected=select_events(events,ccfg,remaining)
    if not selected:
        billing={"contract":"CFGI_TARGETED_BILLING_v1","status":"STOPPED_BY_BUDGET_GUARD","probe":probe,"expected_credits":expected,"selected_events":[],"reserve":ccfg["minimum_credits_reserve"]}
        (args.output/"CFGI_BILLING.json").write_text(json.dumps(billing,indent=2,sort_keys=True)+"\n")
        print(json.dumps(billing,sort_keys=True)); return

    raw,receipts=fetch_scores(key,ccfg,intervals)
    flat=[flatten(r) for r in raw]
    flat.sort(key=lambda r:(r.get("symbol") or "", r.get("timestamp") or ""))
    with gzip.open(args.output/"cfgi_targeted.jsonl.gz","wt",encoding="utf-8") as fh:
        for r in flat: fh.write(json.dumps(r,sort_keys=True)+"\n")
    bysym={}
    for s in ccfg["symbols"]:
        bysym[s]=[r for r in flat if r.get("symbol")==s]
    signatures=[signature_for_event(ev,bysym,ccfg) for ev in selected]
    comparison=compare_signatures(signatures,ccfg)
    (args.output/"CFGI_EVENT_SIGNATURES.json").write_text(json.dumps({"contract":"CFGI_EVENT_SIGNATURES_v1","events":signatures,"comparison":comparison},indent=2,sort_keys=True)+"\n")

    used=sum(x.get("credits_used") or 0 for x in receipts)+(probe.get("credits_used") or 0)
    final_remaining=None
    for x in receipts:
        if x.get("credits_remaining") is not None: final_remaining=x["credits_remaining"]
    billing={
        "contract":"CFGI_TARGETED_BILLING_v1","status":"PASS","generated_at_utc":iso(datetime.now(timezone.utc)),
        "probe":probe,"selected_events":selected,"merged_intervals":[{"start":iso(s),"end":iso(e)} for s,e in intervals],
        "expected_worst_case_credits":expected,"actual_credits_used_from_headers":used,"final_credits_remaining":final_remaining,
        "hard_cap":ccfg["expected_credit_hard_cap"],"minimum_reserve":ccfg["minimum_credits_reserve"],"request_receipts":receipts,
        "fields":ccfg["fields"],"symbols":ccfg["symbols"],"timeframe":ccfg["timeframe"],"static":ccfg.get("static",True),
    }
    (args.output/"CFGI_BILLING.json").write_text(json.dumps(billing,indent=2,sort_keys=True)+"\n")
    summary_path=args.output/"BACKTEST_SUMMARY.json"
    summary=json.loads(summary_path.read_text()) if summary_path.exists() else {}
    summary.update({
        "cfgi_status":"TARGETED_ENRICHMENT_COMPLETE",
        "cfgi_selected_event_count":len(selected),
        "cfgi_expected_worst_case_credits":expected,
        "cfgi_actual_credits_used_from_headers":used,
        "cfgi_final_credits_remaining":final_remaining,
        "cfgi_comparison_artifact":"CFGI_EVENT_SIGNATURES.json",
        "interpretation_status":"DESCRIPTIVE_BOOTSTRAP_NOT_PROMOTED_TO_RULES",
    })
    summary_path.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":"PASS","events":len(selected),"rows":len(flat),"used":used,"remaining":final_remaining},sort_keys=True))

if __name__=="__main__":
    main()
