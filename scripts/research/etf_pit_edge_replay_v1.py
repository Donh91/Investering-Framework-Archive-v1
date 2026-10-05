#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

FIRST_TIMED_CAPTURE = datetime.fromisoformat("2026-07-15T20:48:00+00:00")
FIRST_TIMED_SESSION = "2026-07-15"
A1_THRESHOLD = -500.0
A1_WINDOW = 5
A2_WINDOW = 3


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(repo_root: Path) -> str:
    return subprocess.check_output(["git","-C",str(repo_root),"rev-parse","HEAD"],text=True).strip()


def load_ledger(path: Path) -> list[dict[str,Any]]:
    with gzip.open(path,"rt") as h:
        return [json.loads(line) for line in h if line.strip()]


def numeric_total(row: dict[str,Any]) -> float | None:
    value=row.get("reported_total")
    if isinstance(value,bool) or not isinstance(value,(int,float)):
        return None
    return float(value)


def row_complete(row: dict[str,Any]) -> bool:
    return (
        row.get("is_nyse_session") is True
        and row.get("session_date","") >= FIRST_TIMED_SESSION
        and row.get("not_source_revision") is not True
        and numeric_total(row) is not None
        and row.get("parity") is True
        and int(row.get("unknown_cell_count") or 0) == 0
        and row.get("session_final_claim") is True
    )


def event_verified_only(row: dict[str,Any], activation: datetime | None) -> tuple[datetime,float] | None:
    if not row_complete(row):
        return None
    raw=row.get("verification_completed_at_utc")
    if not raw:
        return None
    k=ts(str(raw))
    if k < FIRST_TIMED_CAPTURE:
        return None
    return k, float(row["reported_total"])


def build_session_events(rows: list[dict[str,Any]], mode: str) -> dict[str,list[dict[str,Any]]]:
    by_session: dict[str,list[dict[str,Any]]] = {}
    for row in rows:
        if row.get("asset")!="BTC" or row.get("is_nyse_session") is not True or row.get("session_date","") < FIRST_TIMED_SESSION:
            continue
        by_session.setdefault(str(row["session_date"]),[]).append(row)

    output: dict[str,list[dict[str,Any]]] = {}
    for day, chain in by_session.items():
        chain=sorted(chain,key=lambda r:(ts(str(r["observed_at_utc"])),str(r.get("ledger_key") or "")))
        verified=[]
        for r in chain:
            ev=event_verified_only(r,None)
            if ev:
                verified.append((ev[0],ev[1],r))
        if not verified:
            output[day]=[]
            continue
        first_verified=min(k for k,_,_ in verified)
        events=[]
        if mode=="VERIFIED_ONLY":
            for k,total,r in verified:
                events.append({
                    "knowledge_at_utc":iso(k),"total_usd_m":total,"source":"VERIFIED_COMPLETE",
                    "ledger_key":r.get("ledger_key"),"observed_at_utc":r.get("observed_at_utc"),
                })
        elif mode=="D1_START_D4_COMPLETE_REVISIONS":
            for r in chain:
                if not row_complete(r):
                    continue
                verification=r.get("verification_completed_at_utc")
                observed=r.get("observed_at_utc")
                if verification:
                    k=ts(str(verification))
                    source="VERIFIED_COMPLETE"
                elif observed:
                    k=ts(str(observed))
                    source="OBSERVED_COMPLETE_REVISION"
                else:
                    continue
                if k < first_verified:
                    continue
                events.append({
                    "knowledge_at_utc":iso(k),"total_usd_m":float(r["reported_total"]),"source":source,
                    "ledger_key":r.get("ledger_key"),"observed_at_utc":r.get("observed_at_utc"),
                })
        else:
            raise ValueError("unsupported_mode")
        # Latest event at identical knowledge time wins deterministically by row order.
        dedup: dict[str,dict[str,Any]]={}
        for e in sorted(events,key=lambda e:(ts(e["knowledge_at_utc"]),str(e.get("ledger_key") or ""))):
            dedup[e["knowledge_at_utc"]]=e
        output[day]=list(dedup.values())
    return output


def latest_at(events: list[dict[str,Any]], cutoff: datetime) -> dict[str,Any] | None:
    eligible=[e for e in events if ts(e["knowledge_at_utc"])<=cutoff]
    return eligible[-1] if eligible else None


def state_a1(values: list[float]) -> bool:
    return sum(values) < A1_THRESHOLD


def state_a2(values: list[float]) -> bool:
    return all(v < 0 for v in values)


def evaluate_endpoint(
    calendar: list[str],
    endpoint_idx: int,
    events_by_session: dict[str,list[dict[str,Any]]],
    window: int,
    predicate: Callable[[list[float]],bool],
) -> dict[str,Any]:
    dates=calendar[endpoint_idx-window+1:endpoint_idx+1]
    chains=[events_by_session.get(day,[]) for day in dates]
    missing=[day for day,chain in zip(dates,chains) if not chain]
    if missing:
        return {
            "endpoint_session":calendar[endpoint_idx],
            "window_sessions":dates,
            "status":"UNAVAILABLE_MISSING_ADMISSIBLE_SESSION",
            "missing_sessions":missing,
        }
    first_eval=max(ts(chain[0]["knowledge_at_utc"]) for chain in chains)
    change_times=sorted({
        ts(e["knowledge_at_utc"])
        for chain in chains for e in chain
        if ts(e["knowledge_at_utc"])>=first_eval
    })
    timeline=[]
    last_state=None
    for cutoff in change_times:
        selected=[latest_at(chain,cutoff) for chain in chains]
        if any(v is None for v in selected):
            continue
        values=[float(v["total_usd_m"]) for v in selected if v is not None]
        state=predicate(values)
        if last_state is None or state!=last_state:
            timeline.append({
                "cutoff_utc":iso(cutoff),
                "state":state,
                "values_usd_m":values,
                "sum_usd_m":round(sum(values),3),
                "selected_ledger_keys":[v.get("ledger_key") for v in selected if v],
            })
            last_state=state
    first=timeline[0]
    final=timeline[-1]
    return {
        "endpoint_session":calendar[endpoint_idx],
        "window_sessions":dates,
        "status":"EVALUABLE",
        "first_evaluable_at_utc":first["cutoff_utc"],
        "first_state":first["state"],
        "first_values_usd_m":first["values_usd_m"],
        "first_sum_usd_m":first["sum_usd_m"],
        "final_state":final["state"],
        "final_values_usd_m":final["values_usd_m"],
        "final_sum_usd_m":final["sum_usd_m"],
        "state_changed_after_first_eval":first["state"]!=final["state"],
        "transitions":timeline,
        "feature_knowledge_rule":"MAX_KNOWLEDGE_TIME_WITHIN_EXACT_WINDOW",
        "consecutive_session_guard":True,
    }


def summarize(rows: list[dict[str,Any]], signal: str) -> dict[str,Any]:
    evaluable=[r for r in rows if r["status"]=="EVALUABLE"]
    first_true=[r for r in evaluable if r["first_state"]]
    final_true=[r for r in evaluable if r["final_state"]]
    changed=[r for r in evaluable if r["state_changed_after_first_eval"]]
    unavailable=[r for r in rows if r["status"]!="EVALUABLE"]
    return {
        "signal":signal,
        "endpoints_total":len(rows),
        "evaluable_endpoints":len(evaluable),
        "unavailable_endpoints":len(unavailable),
        "first_state_true_count":len(first_true),
        "final_state_true_count":len(final_true),
        "state_changed_after_first_eval_count":len(changed),
        "first_true_endpoints":[{
            "endpoint_session":r["endpoint_session"],
            "first_evaluable_at_utc":r["first_evaluable_at_utc"],
            "first_values_usd_m":r["first_values_usd_m"],
            "first_sum_usd_m":r["first_sum_usd_m"],
            "final_state":r["final_state"],
        } for r in first_true],
        "changed_endpoints":[{
            "endpoint_session":r["endpoint_session"],
            "first_state":r["first_state"],
            "final_state":r["final_state"],
            "transitions":r["transitions"],
        } for r in changed],
        "unavailable_examples":[{
            "endpoint_session":r["endpoint_session"],
            "missing_sessions":r["missing_sessions"],
        } for r in unavailable[:12]],
    }


def run_replay(rows: list[dict[str,Any]], mode: str) -> dict[str,Any]:
    events=build_session_events(rows,mode)
    calendar=sorted({
        str(r["session_date"]) for r in rows
        if r.get("asset")=="BTC" and r.get("is_nyse_session") is True and str(r.get("session_date") or "")>=FIRST_TIMED_SESSION
    })
    a1=[evaluate_endpoint(calendar,i,events,A1_WINDOW,state_a1) for i in range(A1_WINDOW-1,len(calendar))]
    a2=[evaluate_endpoint(calendar,i,events,A2_WINDOW,state_a2) for i in range(A2_WINDOW-1,len(calendar))]
    case_days={"2026-08-12","2026-08-13","2026-08-14","2026-08-17","2026-08-19","2026-09-08"}
    return {
        "mode":mode,
        "calendar_sessions":len(calendar),
        "calendar_first":calendar[0] if calendar else None,
        "calendar_last":calendar[-1] if calendar else None,
        "sessions_with_admissible_events":sum(bool(v) for v in events.values()),
        "admissible_event_count":sum(len(v) for v in events.values()),
        "a1":summarize(a1,"A1_BTC_5_SESSION_NET_LT_MINUS_500M"),
        "a2":summarize(a2,"A2_BTC_OUTFLOW_STREAK_GE_3"),
        "case_rows":{
            "a1":[r for r in a1 if r["endpoint_session"] in case_days],
            "a2":[r for r in a2 if r["endpoint_session"] in case_days],
        },
    }


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,default=Path("."))
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    ledger=args.repo_root/"research/etf_temporal_integrity/2026-09-23/ETF_VINTAGE_LEDGER.jsonl.gz"
    rows=load_ledger(ledger)
    result={
        "contract":"ETF_PIT_EDGE_REPLAY_v1",
        "mission_id":"RL-ETF-TEMPORAL-EDGE-001",
        "generated_from_main_sha":git_head(args.repo_root),
        "source_ledger_path":str(ledger.relative_to(args.repo_root)),
        "source_ledger_sha256":sha256(ledger),
        "source_ledger_rows":len(rows),
        "frozen_rules":{
            "A1":"BTC rolling net flow over exactly five consecutive NYSE sessions < -500m USD",
            "A2":"BTC net ETF outflow on each of exactly three consecutive NYSE sessions",
            "first_timed_capture_utc":"2026-07-15T20:48:00Z",
            "pre_capture_history_eligible":False,
            "feature_knowledge_time":"max knowledge time across exact window inputs",
            "missing_session_policy":"UNAVAILABLE; never bridge across a missing admissible trading session",
        },
        "interpretation_note":"This artifact measures signal reconstruction only. It does not measure price outcomes, economic decision value, baseline incremental value, or portfolio impact.",
        "variants":[
            run_replay(rows,"VERIFIED_ONLY"),
            run_replay(rows,"D1_START_D4_COMPLETE_REVISIONS"),
        ],
        "authority":{
            "framework_state_change":False,
            "market_rule_change":False,
            "threshold_change":False,
            "weight_change":False,
            "canonical_promotion":False,
            "portfolio_action":False,
        },
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":"PASS",
        "rows":len(rows),
        "variants":[{
            "mode":v["mode"],
            "a1_first_true":v["a1"]["first_state_true_count"],
            "a2_first_true":v["a2"]["first_state_true_count"],
            "a1_changed":v["a1"]["state_changed_after_first_eval_count"],
            "a2_changed":v["a2"]["state_changed_after_first_eval_count"],
            "sessions_with_events":v["sessions_with_admissible_events"],
        } for v in result["variants"]],
    },sort_keys=True))


if __name__=="__main__":
    main()
