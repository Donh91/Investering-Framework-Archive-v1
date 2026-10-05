#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from bisect import bisect_right
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

MISSION_ID = "RL-ETF-TEMPORAL-EDGE-001"
REPLAY_REL = "06_RESEARCH_LAB/m1_replay/2026-10-05__RL-ETF-TEMPORAL-EDGE-001__pit-edge-replay-v1.json"
C2_THRESHOLD_PCT = -3.0
HORIZONS_HOURS = (24, 72, 168)


def ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def git_head(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()


def num(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_hourly(root: Path) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "03_DAILY_CAPTURE_LOGS/hourly/2026/09").glob("*.csv")):
        with path.open(newline="") as h:
            for row in csv.DictReader(h):
                stamp = row.get("timestamp_utc")
                if not stamp:
                    continue
                start = ts(stamp)
                close = start + timedelta(hours=1)
                parsed = {
                    "bar_start_utc": iso(start),
                    "bar_close_utc": iso(close),
                    "btc_open": num(row.get("btc_open")),
                    "btc_high": num(row.get("btc_high")),
                    "btc_low": num(row.get("btc_low")),
                    "btc_close": num(row.get("btc_close")),
                    "ethbtc_close": num(row.get("ethbtc_close")),
                    "spot_status": row.get("spot_status"),
                    "source_path": str(path.relative_to(root)),
                }
                if parsed["btc_close"] is not None and parsed["ethbtc_close"] is not None:
                    rows[stamp] = parsed
    return sorted(rows.values(), key=lambda r: ts(r["bar_close_utc"]))


def load_hourly_runs(root: Path) -> list[dict[str, Any]]:
    out=[]
    base=root/"03_DAILY_CAPTURE_LOGS/hourly/runs/2026/09"
    for path in sorted(base.glob("*/*.json")):
        try:
            obj=json.loads(path.read_text())
        except Exception:
            continue
        retrieved=obj.get("retrieved_at_utc")
        end=obj.get("window_end_utc")
        if not retrieved or not end:
            continue
        out.append({
            "path":str(path.relative_to(root)),
            "retrieved_at_utc":retrieved,
            "window_end_utc":end,
            "spot_status":obj.get("spot_status"),
            "status":obj.get("status"),
            "directional_summary":obj.get("directional_summary") if isinstance(obj.get("directional_summary"),dict) else {},
        })
    return sorted(out,key=lambda r:ts(r["retrieved_at_utc"]))


def load_captures(root: Path) -> list[dict[str, Any]]:
    out=[]
    base=root/"03_DAILY_CAPTURE_LOGS/captures/2026/09"
    for path in sorted(base.glob("*/*.json")):
        try:
            obj=json.loads(path.read_text())
        except Exception:
            continue
        stamp=obj.get("captured_at_utc")
        metrics=obj.get("market_metrics")
        if not stamp or not isinstance(metrics,dict):
            continue
        out.append({"path":str(path.relative_to(root)),"captured_at_utc":stamp,"metrics":metrics})
    return sorted(out,key=lambda r:ts(r["captured_at_utc"]))


def latest_le(items: list[dict[str,Any]], field: str, cutoff: datetime) -> dict[str,Any] | None:
    eligible=[r for r in items if r.get(field) and ts(str(r[field])) <= cutoff]
    return eligible[-1] if eligible else None


def bar_le(hourly: list[dict[str,Any]], cutoff: datetime) -> dict[str,Any] | None:
    eligible=[r for r in hourly if ts(r["bar_close_utc"]) <= cutoff]
    return eligible[-1] if eligible else None


def bar_ge(hourly: list[dict[str,Any]], cutoff: datetime) -> dict[str,Any] | None:
    for row in hourly:
        if ts(row["bar_close_utc"]) >= cutoff:
            return row
    return None


def return_pct(start: float | None, end: float | None) -> float | None:
    if start in (None, 0) or end is None:
        return None
    return round((end/start-1)*100, 4)


def price_context(hourly: list[dict[str,Any]], signal: datetime, anchor_price: float) -> dict[str,Any]:
    out={}
    for hours in (24,72,120):
        prior=bar_le(hourly, signal-timedelta(hours=hours))
        out[f"btc_return_prior_{hours}h_pct"]=return_pct(prior.get("btc_close") if prior else None, anchor_price)
        if hours==120:
            out["ethbtc_return_prior_120h_pct"]=return_pct(
                prior.get("ethbtc_close") if prior else None,
                bar_le(hourly,signal).get("ethbtc_close") if bar_le(hourly,signal) else None,
            )
            c2=out["ethbtc_return_prior_120h_pct"]
            out["c2_ethbtc_5d_le_minus_3pct"]=bool(c2 is not None and c2 <= C2_THRESHOLD_PCT)
            out["c2_definition"]="ETHBTC 5d return <= -3%, frozen Sensor Survival C2 definition"
    return out


def outcome(hourly: list[dict[str,Any]], signal: datetime, anchor_price: float) -> dict[str,Any]:
    rows_after=[r for r in hourly if ts(r["bar_close_utc"]) > signal]
    result={}
    for hours in HORIZONS_HOURS:
        target=signal+timedelta(hours=hours)
        end=bar_ge(hourly,target)
        window=[r for r in rows_after if ts(r["bar_close_utc"]) <= target+timedelta(hours=1)]
        lows=[r["btc_low"] for r in window if r["btc_low"] is not None]
        highs=[r["btc_high"] for r in window if r["btc_high"] is not None]
        result[f"h{hours}"]={
            "target_utc":iso(target),
            "observed_bar_close_utc":end.get("bar_close_utc") if end else None,
            "target_offset_minutes":round((ts(end["bar_close_utc"])-target).total_seconds()/60,2) if end else None,
            "btc_close":end.get("btc_close") if end else None,
            "btc_return_pct":return_pct(anchor_price,end.get("btc_close") if end else None),
            "btc_min_low":min(lows) if lows else None,
            "btc_max_high":max(highs) if highs else None,
            "btc_max_drawdown_from_anchor_pct":return_pct(anchor_price,min(lows)) if lows else None,
            "btc_max_upside_from_anchor_pct":return_pct(anchor_price,max(highs)) if highs else None,
            "ethbtc_close":end.get("ethbtc_close") if end else None,
        }
    return result


def capture_snapshot(row: dict[str,Any] | None) -> dict[str,Any] | None:
    if not row:
        return None
    m=row["metrics"]
    b=m.get("breadth") if isinstance(m.get("breadth"),dict) else {}
    rot=m.get("rotation_context") if isinstance(m.get("rotation_context"),dict) else {}
    bc=rot.get("blockchaincenter_altcoin_season") if isinstance(rot.get("blockchaincenter_altcoin_season"),dict) else {}
    horizons=bc.get("horizons") if isinstance(bc.get("horizons"),dict) else {}
    h30=horizons.get("30") if isinstance(horizons.get("30"),dict) else {}
    h90=horizons.get("90") if isinstance(horizons.get("90"),dict) else {}
    sentiment=m.get("sentiment") if isinstance(m.get("sentiment"),dict) else {}
    cfgi=sentiment.get("cfgi") if isinstance(sentiment.get("cfgi"),dict) else {}
    btc=((cfgi.get("symbols") or {}).get("BTC") if isinstance(cfgi.get("symbols"),dict) else {}) or {}
    return {
        "path":row["path"],
        "captured_at_utc":row["captured_at_utc"],
        "breadth_advancers":b.get("advancers"),
        "breadth_decliners":b.get("decliners"),
        "breadth_constituent_count":b.get("constituent_count"),
        "breadth_advancer_share":round(float(b.get("advancers"))/float(b.get("constituent_count")),4) if num(b.get("advancers")) is not None and num(b.get("constituent_count")) not in (None,0) else None,
        "blockchaincenter_30d_score":h30.get("published_score"),
        "blockchaincenter_30d_outperforming_btc_share":h30.get("outperforming_btc_share"),
        "blockchaincenter_90d_score":h90.get("published_score"),
        "blockchaincenter_90d_outperforming_btc_share":h90.get("outperforming_btc_share"),
        "cfgi_btc_score":btc.get("score"),
        "cfgi_btc_classification":btc.get("classification"),
    }


def exact_hourly_anchor(runs: list[dict[str,Any]], signal: datetime) -> dict[str,Any]:
    eligible=[
        r for r in runs
        if ts(r["retrieved_at_utc"]) <= signal
        and ts(r["window_end_utc"]) <= signal
        and r.get("spot_status")=="PASS"
    ]
    if not eligible:
        raise ValueError(f"no_point_in_time_hourly_run_before_signal:{iso(signal)}")
    run=eligible[-1]
    observations=(run.get("directional_summary") or {}).get("latest_observations") or []
    obs=[]
    for x in observations:
        if not isinstance(x,dict) or not x.get("timestamp_utc"):
            continue
        close_time=ts(x["timestamp_utc"])+timedelta(hours=1)
        if close_time <= signal and num(x.get("btc_close")) is not None:
            obs.append((close_time,x))
    if not obs:
        raise ValueError(f"hourly_run_has_no_closed_anchor:{run['path']}")
    close_time,x=sorted(obs,key=lambda z:z[0])[-1]
    return {
        "run_path":run["path"],
        "run_retrieved_at_utc":run["retrieved_at_utc"],
        "run_window_end_utc":run["window_end_utc"],
        "anchor_bar_open_utc":x["timestamp_utc"],
        "anchor_bar_close_utc":iso(close_time),
        "btc_close":float(x["btc_close"]),
        "eth_close":num(x.get("eth_close")),
        "ethbtc_close":num(x.get("ethbtc_close")),
        "btc_return_1h_pct":num(x.get("btc_return_1h_pct")),
        "ethbtc_return_1h_pct":num(x.get("ethbtc_return_1h_pct")),
        "availability_lag_minutes":round((signal-ts(run["retrieved_at_utc"])).total_seconds()/60,2),
    }


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=Path,default=Path("."))
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    root=args.repo_root
    replay=json.loads((root/REPLAY_REL).read_text())
    verified=next(v for v in replay["variants"] if v["mode"]=="VERIFIED_ONLY")
    hourly=load_hourly(root)
    runs=load_hourly_runs(root)
    captures=load_captures(root)

    signals=[]
    for key,label in (("a2","A2_BTC_OUTFLOW_STREAK_GE_3"),("a1","A1_BTC_5_SESSION_NET_LT_MINUS_500M")):
        trues=verified[key]["first_true_endpoints"]
        if not trues:
            continue
        first=trues[0]
        signal_time=ts(first["first_evaluable_at_utc"])
        anchor=exact_hourly_anchor(runs,signal_time)
        anchor_price=float(anchor["btc_close"])
        cap=latest_le(captures,"captured_at_utc",signal_time)
        cap24=latest_le(captures,"captured_at_utc",signal_time-timedelta(hours=24))
        snap=capture_snapshot(cap)
        prev=capture_snapshot(cap24)
        breadth_delta=None
        if snap and prev and snap["breadth_advancer_share"] is not None and prev["breadth_advancer_share"] is not None:
            breadth_delta=round(snap["breadth_advancer_share"]-prev["breadth_advancer_share"],4)
        signals.append({
            "signal":label,
            "episode_onset_endpoint_session":first["endpoint_session"],
            "signal_known_at_utc":first["first_evaluable_at_utc"],
            "signal_values_usd_m":first["first_values_usd_m"],
            "signal_sum_usd_m":first["first_sum_usd_m"],
            "persistence_true_endpoints":[x["endpoint_session"] for x in trues],
            "hourly_anchor":anchor,
            "pre_signal_price_rotation_context":price_context(hourly,signal_time,anchor_price),
            "last_live_capture_before_signal":snap,
            "live_capture_24h_baseline":prev,
            "breadth_advancer_share_change_vs_24h_baseline":breadth_delta,
            "outcomes":outcome(hourly,signal_time,anchor_price),
        })

    result={
        "contract":"ETF_PIT_DECISION_VALUE_CROSSWALK_v1",
        "mission_id":MISSION_ID,
        "generated_from_main_sha":git_head(root),
        "source_replay":REPLAY_REL,
        "purpose":"Measure point-in-time ETF warning onset against contemporaneous pre-signal price/rotation context and subsequent outcomes without inventing new warning thresholds.",
        "baseline_rules":{
            "price_anchor":"latest CLOSED 1h BTC bar from an hourly owner run retrieved before signal knowledge time",
            "price_context":"plain prior 24h/72h BTC returns, descriptive only",
            "C2":"existing frozen ETHBTC 5d return <= -3% warning definition",
            "breadth_rotation":"last live capture at or before signal time, descriptive only",
            "D2_D3":"not recomputed because the current source packet does not freeze enough implementation detail to reconstruct swingDOWN / 20d-range-break without inventing semantics",
            "outcomes":"future closed-hour BTC/ETHBTC bars, 24h/72h/168h plus max adverse/upside excursion",
        },
        "signals":signals,
        "limits":[
            "Only two independent signal onsets are available in verified PIT data: A2 onset and later A1 onset; persistence endpoints are not independent events.",
            "This crosswalk measures timing/outcomes, not causal incremental value versus a full multivariate baseline.",
            "Breadth and rotation capture metrics are descriptive and retain zero standalone predictive authority.",
            "Outcome bars are final historical closed bars and are never used as signal-time inputs.",
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
        "signal_count":len(signals),
        "signals":[{
            "signal":s["signal"],
            "known_at":s["signal_known_at_utc"],
            "btc_anchor":s["hourly_anchor"]["btc_close"],
            "btc_prior_24h":s["pre_signal_price_rotation_context"]["btc_return_prior_24h_pct"],
            "btc_prior_72h":s["pre_signal_price_rotation_context"]["btc_return_prior_72h_pct"],
            "c2":s["pre_signal_price_rotation_context"]["c2_ethbtc_5d_le_minus_3pct"],
            "btc_24h":s["outcomes"]["h24"]["btc_return_pct"],
            "btc_72h":s["outcomes"]["h72"]["btc_return_pct"],
            "btc_168h":s["outcomes"]["h168"]["btc_return_pct"],
        } for s in signals],
    },sort_keys=True))


if __name__=="__main__":
    main()
