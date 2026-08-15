from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

HORIZONS_HOURS = (1, 4, 12, 24, 72)
NUMERIC_FIELDS = (
    "btc_close", "eth_close", "ethbtc_close",
    "btc_open_interest", "eth_open_interest",
    "btc_long_short_ratio", "eth_long_short_ratio",
    "btc_quote_volume", "eth_quote_volume",
    "btc_taker_buy_quote_volume", "eth_taker_buy_quote_volume",
)


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def parse_ts(raw: Any) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def to_float(raw: Any) -> float | None:
    try:
        if raw in (None, ""):
            return None
        return float(raw)
    except Exception:
        return None


def load_hourly_rows(root: Path, cutoff: datetime) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return rows
    for path in sorted(root.rglob("*.csv")):
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                for raw in csv.DictReader(handle):
                    ts = parse_ts(raw.get("timestamp_utc"))
                    if ts is None or ts > cutoff:
                        continue
                    row: dict[str, Any] = {"timestamp": ts, "source_path": str(path)}
                    for field in NUMERIC_FIELDS:
                        row[field] = to_float(raw.get(field))
                    row["btc_taker_buy_quote_share"] = to_float(raw.get("btc_taker_buy_quote_share"))
                    row["eth_taker_buy_quote_share"] = to_float(raw.get("eth_taker_buy_quote_share"))
                    row["btc_high"] = to_float(raw.get("btc_high")); row["btc_low"] = to_float(raw.get("btc_low"))
                    row["eth_high"] = to_float(raw.get("eth_high")); row["eth_low"] = to_float(raw.get("eth_low"))
                    rows.append(row)
        except Exception:
            continue
    rows.sort(key=lambda item: item["timestamp"])
    return rows


def pct_change(latest: float | None, anchor: float | None) -> float | None:
    if latest is None or anchor in (None, 0): return None
    return round((latest / anchor - 1.0) * 100.0, 6)


def mean(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 6) if values else None


def select_anchor(rows: list[dict[str, Any]], target: datetime, max_lag_hours: float) -> dict[str, Any] | None:
    candidates = [row for row in rows if row["timestamp"] <= target]
    if not candidates: return None
    anchor = candidates[-1]
    lag = (target - anchor["timestamp"]).total_seconds() / 3600.0
    return anchor if lag <= max_lag_hours else None


def aggressive_flow(row: dict[str, Any], asset: str) -> float | None:
    total=row.get(f"{asset}_quote_volume"); buy=row.get(f"{asset}_taker_buy_quote_volume")
    if not isinstance(total,float) or not isinstance(buy,float): return None
    return round(2.0*buy-total,6)


def build_horizon(rows: list[dict[str, Any]], cutoff: datetime, hours: int) -> dict[str, Any]:
    if not rows: return {"status": "UNAVAILABLE", "target_hours": hours}
    latest = rows[-1]; target = cutoff - timedelta(hours=hours)
    tolerance = 1.25 if hours == 1 else min(6.0, max(2.0, hours * 0.25))
    anchor = select_anchor(rows, target, tolerance)
    if anchor is None: return {"status": "UNAVAILABLE", "target_hours": hours, "reason": "NO_ANCHOR_WITHIN_TOLERANCE"}
    window = [row for row in rows if anchor["timestamp"] <= row["timestamp"] <= latest["timestamp"]]
    btc_highs=[v for v in (r.get("btc_high") for r in window) if isinstance(v,float)]; btc_lows=[v for v in (r.get("btc_low") for r in window) if isinstance(v,float)]
    eth_highs=[v for v in (r.get("eth_high") for r in window) if isinstance(v,float)]; eth_lows=[v for v in (r.get("eth_low") for r in window) if isinstance(v,float)]
    btc_taker=[v for v in (r.get("btc_taker_buy_quote_share") for r in window) if isinstance(v,float)]; eth_taker=[v for v in (r.get("eth_taker_buy_quote_share") for r in window) if isinstance(v,float)]
    btc_flow=[v for v in (aggressive_flow(r,"btc") for r in window) if isinstance(v,float)]; eth_flow=[v for v in (aggressive_flow(r,"eth") for r in window) if isinstance(v,float)]
    return {
        "status":"READY","target_hours":hours,
        "anchor_timestamp_utc":anchor["timestamp"].isoformat().replace("+00:00","Z"),
        "latest_timestamp_utc":latest["timestamp"].isoformat().replace("+00:00","Z"),
        "actual_span_hours":round((latest["timestamp"]-anchor["timestamp"]).total_seconds()/3600.0,3),"sample_count":len(window),
        "btc_return_pct":pct_change(latest.get("btc_close"),anchor.get("btc_close")),"eth_return_pct":pct_change(latest.get("eth_close"),anchor.get("eth_close")),"ethbtc_return_pct":pct_change(latest.get("ethbtc_close"),anchor.get("ethbtc_close")),
        "btc_oi_change_pct":pct_change(latest.get("btc_open_interest"),anchor.get("btc_open_interest")),"eth_oi_change_pct":pct_change(latest.get("eth_open_interest"),anchor.get("eth_open_interest")),
        "btc_long_short_change_pct":pct_change(latest.get("btc_long_short_ratio"),anchor.get("btc_long_short_ratio")),"eth_long_short_change_pct":pct_change(latest.get("eth_long_short_ratio"),anchor.get("eth_long_short_ratio")),
        "btc_taker_buy_quote_share_mean":mean(btc_taker),"eth_taker_buy_quote_share_mean":mean(eth_taker),
        "btc_net_aggressive_quote_flow_sum":round(sum(btc_flow),6) if btc_flow else None,"eth_net_aggressive_quote_flow_sum":round(sum(eth_flow),6) if eth_flow else None,
        "btc_window_high":max(btc_highs) if btc_highs else None,"btc_window_low":min(btc_lows) if btc_lows else None,"eth_window_high":max(eth_highs) if eth_highs else None,"eth_window_low":min(eth_lows) if eth_lows else None,
    }


def ethbtc_persistence(rows: list[dict[str, Any]], level: float = 0.03, lookback_hours: int = 168) -> dict[str, Any]:
    valid=[r for r in rows[-lookback_hours:] if isinstance(r.get("ethbtc_close"),float)]
    if not valid: return {"status":"UNAVAILABLE","level":level}
    vals=[float(r["ethbtc_close"]) for r in valid]; latest=vals[-1]
    side="ABOVE" if latest>level else "BELOW" if latest<level else "AT"
    consecutive=0
    for v in reversed(vals):
        s="ABOVE" if v>level else "BELOW" if v<level else "AT"
        if s!=side: break
        consecutive+=1
    last_touch=None
    for r in reversed(valid):
        if abs(float(r["ethbtc_close"])-level) <= level*0.001:
            last_touch=r["timestamp"].isoformat().replace("+00:00","Z"); break
    return {"status":"READY","level":level,"latest_close":latest,"latest_side":side,"consecutive_hourly_closes_same_side":consecutive,"closes_above":sum(v>level for v in vals),"closes_below":sum(v<level for v in vals),"sample_count":len(vals),"last_near_touch_0_1pct_utc":last_touch,"method":"DIRECT_ETHBTC_HOURLY_CLOSES_NO_RATIO_SYNTHESIS"}


def breadth_ratio(metrics: dict[str, Any]) -> float | None:
    breadth=metrics.get("breadth") if isinstance(metrics.get("breadth"),dict) else {}; values=[breadth.get("advancers"),breadth.get("decliners"),breadth.get("flat")]
    if not all(isinstance(v,(int,float)) for v in values): return None
    total=float(sum(values)); return round(float(breadth["advancers"])/total,6) if total else None


def breadth_context(base: dict[str, Any]) -> dict[str, Any]:
    latest=base.get("latest_capture") if isinstance(base.get("latest_capture"),dict) else {}; previous=base.get("previous_capture") if isinstance(base.get("previous_capture"),dict) else {}
    lm=latest.get("market_metrics",{}) if isinstance(latest.get("market_metrics"),dict) else {}; pm=previous.get("market_metrics",{}) if isinstance(previous.get("market_metrics"),dict) else {}
    latest_ratio=breadth_ratio(lm); previous_ratio=breadth_ratio(pm); rich=lm.get("breadth") if isinstance(lm.get("breadth"),dict) else {}
    return {"latest_advance_ratio":latest_ratio,"previous_advance_ratio":previous_ratio,"advance_ratio_delta_pp":round((latest_ratio-previous_ratio)*100.0,4) if latest_ratio is not None and previous_ratio is not None else None,"rich_latest":rich,"source":"OWNER_CAPTURE_BREADTH_ONLY"}


def settled_etf_context(pointer_path: Path) -> dict[str, Any]:
    if not pointer_path.exists(): return {"status":"UNAVAILABLE","reason":"ETF_POINTER_MISSING"}
    try:
        pointer=json.loads(pointer_path.read_text()); data_path=Path(str(pointer.get("path",""))); value=json.loads(data_path.read_text())
    except Exception: return {"status":"UNAVAILABLE","reason":"ETF_POINTER_OR_PAYLOAD_INVALID"}
    rows=[]
    for row in value.get("rows",[]):
        if isinstance(row,dict): rows.append({"asset":row.get("asset"),"date":row.get("date"),"reported_total":row.get("reported_total"),"session_final":row.get("session_final"),"total_parity":row.get("total_parity")})
    return {"status":value.get("status") or pointer.get("status") or "PASS","session_date":value.get("session_date") or pointer.get("session_date"),"retrieved_at_utc":value.get("retrieved_at_utc") or pointer.get("retrieved_at_utc"),"row_signature_sha256":value.get("row_signature_sha256") or pointer.get("row_signature_sha256"),"rows":rows,"source":"DAILY_SETTLED_ETF_CALIBRATION_v2"}


def pullback_forensics_context(path: Path) -> dict[str, Any]:
    if not path.exists(): return {"status":"UNAVAILABLE","reason":"PULLBACK_FORENSICS_POINTER_MISSING"}
    try: v=json.loads(path.read_text())
    except Exception: return {"status":"UNAVAILABLE","reason":"PULLBACK_FORENSICS_INVALID"}
    return {"status":v.get("status"),"observed_at_utc":v.get("observed_at_utc"),"lane1_liquidations":v.get("lane1_liquidations",{}),"lane2b_moneyness_skew":v.get("lane2b_moneyness_skew",{}),"errors":v.get("errors",[]),"payload_sha256":v.get("payload_sha256"),"authority":v.get("authority"),"source":"PULLBACK_FORENSICS_PASSIVE_CAPTURE_v1"}


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("--context",type=Path,required=True); parser.add_argument("--hourly-root",type=Path,required=True); parser.add_argument("--etf-pointer",type=Path,default=Path("03_DAILY_CAPTURE_LOGS/etf/LATEST.json")); parser.add_argument("--pullback-pointer",type=Path,default=Path("03_DAILY_CAPTURE_LOGS/pullback_forensics/LATEST.json")); parser.add_argument("--output",type=Path,required=True); args=parser.parse_args()
    context=json.loads(args.context.read_text()); latest=context.get("latest_capture") if isinstance(context.get("latest_capture"),dict) else {}; cutoff=parse_ts(latest.get("captured_at_utc"))
    if cutoff is None: raise SystemExit("latest_capture_timestamp_required")
    rows=load_hourly_rows(args.hourly_root,cutoff)
    context["api_intelligence_v2"]={
        "contract":"API_INTELLIGENCE_SEQUENCE_CONTEXT_v2_1","authority":"SHADOW_CONTEXT_ONLY","canonical_state":False,"cutoff_utc":cutoff.isoformat().replace("+00:00","Z"),"hourly_rows_available":len(rows),
        "horizons":{str(h):build_horizon(rows,cutoff,h) for h in HORIZONS_HOURS},"ethbtc_0_0300_persistence":ethbtc_persistence(rows),"breadth_delta":breadth_context(context),"latest_settled_etf":settled_etf_context(args.etf_pointer),"pullback_forensics":pullback_forensics_context(args.pullback_pointer),
        "rules":["All deltas are deterministic observations from retained owner/hourly data.","ETHBTC persistence uses direct retained ETHBTC closes and never a synthetic ETH/USD divided by BTC/USD ratio.","Net aggressive quote flow is taker-buy quote minus inferred taker-sell quote from the same exchange bar and is not labelled CVD.","Settled ETF context is copied only from verified retained ETF owner payload; missing sessions are not imputed.","Pullback Forensics remains SHADOW_RESEARCH_ONLY and cannot create market state or portfolio action.","Unavailable horizons remain unknown and are not imputed."]}
    context["context_hash"]=hashlib.sha256(canonical_bytes({k:v for k,v in context.items() if k!="context_hash"})).hexdigest(); args.output.parent.mkdir(parents=True,exist_ok=True); args.output.write_bytes(canonical_bytes(context)); print(json.dumps({"status":"PASS","hourly_rows":len(rows),"context_hash":context["context_hash"]},sort_keys=True))

if __name__=="__main__": main()
