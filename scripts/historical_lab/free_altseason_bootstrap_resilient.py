#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import io
import importlib.util
import json
import math
import sqlite3
import statistics
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
TARGET = BASE / "free_altseason_bootstrap.py"
VISION = "https://data.binance.vision/data/spot"
UA = {"User-Agent": "Investering-Historical-Altseason-Lab/1.3", "Accept": "*/*"}
HOUR_MS = 3600_000
SOURCE_EVENTS: list[dict] = []


def _norm_ts(value: str | int) -> int:
    x = int(value)
    if x > 10**15:
        x //= 1000
    return x


def _download_zip(url: str, retries: int = 4) -> bytes:
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            last = exc
            if exc.code == 404:
                raise
        except Exception as exc:
            last = exc
        time.sleep(min(8, 0.8 * (2 ** attempt)))
    raise RuntimeError(f"vision_fetch_failed:{url}:{last}")


def _rows_from_zip(blob: bytes):
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith('.csv')]
        if not names:
            return
        with zf.open(names[0]) as fh:
            text = io.TextIOWrapper(fh, encoding='utf-8')
            for row in csv.reader(text):
                if not row or not row[0].strip().isdigit() or len(row) < 11:
                    continue
                out = list(row)
                out[0] = _norm_ts(out[0])
                if len(out) > 6 and str(out[6]).strip().isdigit():
                    out[6] = _norm_ts(out[6])
                yield out


def _month_floor(x: datetime) -> datetime:
    return datetime(x.year, x.month, 1, tzinfo=timezone.utc)


def _next_month(x: datetime) -> datetime:
    return datetime(x.year + (x.month == 12), 1 if x.month == 12 else x.month + 1, 1, tzinfo=timezone.utc)


def _vision_monthly(symbol: str, month: datetime):
    ym = month.strftime('%Y-%m')
    url = f"{VISION}/monthly/klines/{symbol}/1h/{symbol}-1h-{ym}.zip"
    return _rows_from_zip(_download_zip(url))


def _vision_daily(symbol: str, day: datetime):
    ds = day.strftime('%Y-%m-%d')
    url = f"{VISION}/daily/klines/{symbol}/1h/{symbol}-1h-{ds}.zip"
    return _rows_from_zip(_download_zip(url))


def vision_klines(symbol: str, start_ms: int, end_ms: int):
    """Use daily archives for 2020-2021 because corrected daily files can differ from old monthly files."""
    start = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
    end = datetime.fromtimestamp(end_ms / 1000, tz=timezone.utc)
    month = _month_floor(start)
    current_month = _month_floor(datetime.now(timezone.utc))
    emitted = set()
    prefer_daily_before = datetime(2022, 1, 1, tzinfo=timezone.utc)
    while month <= end:
        month_end = _next_month(month) - timedelta(milliseconds=1)
        use_monthly = month >= prefer_daily_before and month < current_month and month_end <= end
        monthly_ok = False
        if use_monthly:
            try:
                for row in _vision_monthly(symbol, month):
                    monthly_ok = True
                    ts = int(row[0])
                    if start_ms <= ts <= end_ms and ts not in emitted:
                        emitted.add(ts); yield row
            except urllib.error.HTTPError as exc:
                if exc.code != 404: raise
        if not use_monthly or not monthly_ok:
            day = max(start, month)
            day = datetime(day.year, day.month, day.day, tzinfo=timezone.utc)
            last_day = min(end, month_end)
            while day <= last_day:
                try:
                    for row in _vision_daily(symbol, day):
                        ts = int(row[0])
                        if start_ms <= ts <= end_ms and ts not in emitted:
                            emitted.add(ts); yield row
                except urllib.error.HTTPError as exc:
                    if exc.code != 404: raise
                day += timedelta(days=1)
        month = _next_month(month)


def load_target():
    spec = importlib.util.spec_from_file_location("free_altseason_bootstrap_base", TARGET)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot_load_base_bootstrap")
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod


def _window_for_ts(cfg: dict, ts: int):
    for w in cfg["research_windows"]:
        if _iso_ms(w["start_utc"]) <= ts <= _iso_ms(w["end_utc"]): return w["id"]
    return None


def _iso_ms(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def _ms_iso(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _exact_return(now, prior):
    if now is None or prior in (None, 0): return None
    return (float(now) / float(prior) - 1.0) * 100.0


def strict_build_features(mod, conn: sqlite3.Connection, cfg: dict, out: Path) -> list[dict]:
    alts = cfg["alt_symbols"]; min_active = int(cfg["minimum_active_alts_per_hour"])
    fng, stable = mod.load_daily_controls()
    qmarks = ",".join("?" for _ in alts)
    raw = defaultdict(dict)
    query = f"SELECT symbol,ts,close,quote_volume,trades,CASE WHEN quote_volume>0 THEN taker_buy_quote/quote_volume END FROM bars WHERE symbol IN ({qmarks}) ORDER BY ts,symbol"
    for sym, ts, close, qv, trades, taker in conn.execute(query, alts):
        raw[str(sym)][int(ts)] = {"close":float(close),"quote_volume":None if qv is None else float(qv),"trades":None if trades is None else int(trades),"taker_share":None if taker is None else float(taker)}
    all_ts = sorted({ts for rows in raw.values() for ts in rows})
    core = {sym:{int(ts):float(c) for ts,c in conn.execute("SELECT ts,close FROM bars WHERE symbol=?",(sym,))} for sym in cfg["core_symbols"]}
    panel_rows=[]; features=[]; ew_index=100.0; prev_ts=None; prev_window=None; segment=-1
    recent_by_segment: deque[dict] = deque(maxlen=73)
    for ts in all_ts:
        wid=_window_for_ts(cfg,ts)
        if wid is None: continue
        gap = None if prev_ts is None else (ts-prev_ts)//HOUR_MS
        discontinuity = prev_ts is None or wid != prev_window or gap != 1
        if discontinuity:
            segment += 1; ew_index=100.0; recent_by_segment.clear()
        rows=[]
        for sym in alts:
            x=raw.get(sym,{}).get(ts)
            if not x: continue
            rec={"timestamp_utc":_ms_iso(ts),"timestamp_ms":ts,"research_window_id":wid,"continuity_segment_id":segment,"symbol":sym,"close":x["close"],"quote_volume":x["quote_volume"],"trade_count":x["trades"],"taker_buy_share":x["taker_share"]}
            for h in (1,6,24):
                p=raw[sym].get(ts-h*HOUR_MS)
                rec[f"return_{h}h_pct"]=_exact_return(x["close"], None if not p else p["close"])
            rows.append(rec)
        r1=[r["return_1h_pct"] for r in rows if r["return_1h_pct"] is not None]
        if len(r1) < min_active:
            prev_ts,prev_window=ts,wid; continue
        qvs=sorted([(r["quote_volume"] or 0.0,r) for r in rows],key=lambda z:z[0])
        denom=max(1,len(qvs)-1)
        for rank,(_,r) in enumerate(qvs):
            r["liquidity_rank_pct"]=rank/denom
            r["liquidity_cohort_proxy"]="LOW" if rank/denom<1/3 else ("MID" if rank/denom<2/3 else "HIGH")
            panel_rows.append(r)
        mean1=statistics.fmean(r1); ew_index *= 1.0+mean1/100.0
        def vals(k): return [r[k] for r in rows if r.get(k) is not None]
        r6=vals("return_6h_pct"); r24=vals("return_24h_pct"); taker=[r["taker_buy_share"] for r in rows if r["taker_buy_share"] is not None]
        vols=[r["quote_volume"] for r in rows if r["quote_volume"] is not None]; trades=[r["trade_count"] for r in rows if r["trade_count"] is not None]
        fng_ts,fng_v=mod.latest_before(fng,ts); st_ts,st_v=mod.latest_before(stable,ts)
        feat={
            "timestamp_utc":_ms_iso(ts),"timestamp_ms":ts,"research_window_id":wid,"continuity_segment_id":segment,
            "gap_from_previous_feature_hours":gap,"segment_reset":bool(discontinuity),"active_alt_count":len(r1),"active_alt_count_6h":len(r6),"active_alt_count_24h":len(r24),
            "ew_index":ew_index,"ew_return_1h_pct":mean1,"median_return_1h_pct":statistics.median(r1),"dispersion_1h_pct":statistics.pstdev(r1) if len(r1)>1 else 0.0,
            "breadth_1h":sum(v>0 for v in r1)/len(r1),"breadth_6h":None if not r6 else sum(v>0 for v in r6)/len(r6),"breadth_24h":None if not r24 else sum(v>0 for v in r24)/len(r24),
            "mean_return_6h_pct":None if not r6 else statistics.fmean(r6),"mean_return_24h_pct":None if not r24 else statistics.fmean(r24),
            "median_taker_buy_share":None if not taker else statistics.median(taker),"total_quote_volume":sum(vols),"total_trade_count":sum(trades),
            "btc_usdt":core.get("BTCUSDT",{}).get(ts),"eth_usdt":core.get("ETHUSDT",{}).get(ts),"ethbtc":core.get("ETHBTC",{}).get(ts),
            "free_fng_daily":fng_v,"free_fng_source_utc":_ms_iso(fng_ts) if fng_ts else None,"stablecoin_total_usd_daily":st_v,"stablecoin_source_utc":_ms_iso(st_ts) if st_ts else None,
            "prev_feature_ts_ms":prev_ts,
        }
        for asset in ("btc_usdt","eth_usdt","ethbtc"):
            sym={"btc_usdt":"BTCUSDT","eth_usdt":"ETHUSDT","ethbtc":"ETHBTC"}[asset]
            for h in (1,3,6,12,24,48,72): feat[f"{asset}_return_{h}h_pct"]=_exact_return(feat[asset],core.get(sym,{}).get(ts-h*HOUR_MS))
        feat["eth_minus_btc_24h_pp"]=None if feat["btc_usdt_return_24h_pct"] is None or feat["eth_usdt_return_24h_pct"] is None else feat["eth_usdt_return_24h_pct"]-feat["btc_usdt_return_24h_pct"]
        prior6=next((x for x in reversed(recent_by_segment) if x["timestamp_ms"]==ts-6*HOUR_MS),None)
        prior12=next((x for x in reversed(recent_by_segment) if x["timestamp_ms"]==ts-12*HOUR_MS),None)
        for k in ("breadth_1h","breadth_6h","breadth_24h","median_taker_buy_share","dispersion_1h_pct","mean_return_24h_pct"):
            v=feat.get(k); feat[f"{k}_delta_6h"]=None if v is None or not prior6 or prior6.get(k) is None else v-prior6[k]
            if prior6 and prior12 and v is not None and prior6.get(k) is not None and prior12.get(k) is not None:
                feat[f"{k}_accel_6h"]=(v-prior6[k])-(prior6[k]-prior12[k])
            else: feat[f"{k}_accel_6h"]=None
        same=[x for x in recent_by_segment if x["continuity_segment_id"]==segment]
        for h in (24,72):
            window=[x["ew_index"] for x in same[-(h-1):]]+[ew_index]
            peak=max(window) if window else ew_index
            feat[f"ew_drawdown_from_{h}h_peak_pct"]=(ew_index/peak-1)*100 if peak else None
        features.append(feat); recent_by_segment.append(feat); prev_ts,prev_window=ts,wid
    if features:
        with gzip.open(out/"hourly_features.csv.gz","wt",newline="",encoding="utf-8") as fh:
            w=csv.DictWriter(fh,fieldnames=list(features[0])); w.writeheader(); w.writerows(features)
    if panel_rows:
        with gzip.open(out/"alt_hourly_panel.csv.gz","wt",newline="",encoding="utf-8") as fh:
            w=csv.DictWriter(fh,fieldnames=list(panel_rows[0])); w.writeheader(); w.writerows(panel_rows)
    return features


def strict_add_derived(features: list[dict]):
    return {r["timestamp_ms"]:r for r in features}


def strict_build_episodes(features: list[dict], cfg: dict) -> list[dict]:
    trigger=float(cfg["episode_drawdown_trigger_pct"]); recf=float(cfg["episode_recovery_fraction"]); levels=[float(x) for x in cfg["episode_severity_levels_pct"]]; sep=int(cfg["episode_min_separation_hours"])
    episodes=[]; active=None; peak=None; last_close_ts=None; prev_seg=None
    for r in features:
        seg=r["continuity_segment_id"]; ts=r["timestamp_ms"]; val=float(r["ew_index"])
        if seg!=prev_seg: active=None; peak=r; last_close_ts=None; prev_seg=seg
        if active is None:
            if peak is None or val>float(peak["ew_index"]): peak=r
            dd=(val/float(peak["ew_index"])-1)*100
            separated=last_close_ts is None or (ts-last_close_ts)>=sep*HOUR_MS
            if dd<=-trigger and separated:
                active={"top":peak,"trigger":r,"trough":r,"peak_val":float(peak["ew_index"]),"trough_val":val,"segment":seg}
        else:
            if val<active["trough_val"]: active["trough_val"]=val; active["trough"]=r
            threshold=active["trough_val"]+recf*(active["peak_val"]-active["trough_val"])
            if val>=threshold and ts>active["trough"]["timestamp_ms"]:
                top=active["top"]; trig=active["trigger"]; trough=active["trough"]; dd=(active["trough_val"]/active["peak_val"]-1)*100
                episodes.append({"episode_id":f"PB_{top['timestamp_utc'][:10]}_{len(episodes)+1:03d}","research_window_id":top["research_window_id"],"continuity_segment_id":seg,"top_utc":top["timestamp_utc"],"trigger_utc":trig["timestamp_utc"],"trough_utc":trough["timestamp_utc"],"recovery_utc":r["timestamp_utc"],"max_drawdown_pct":dd,"severity_flags":{f"ge_{int(x)}pct":abs(dd)>=x for x in levels},"hours_top_to_trigger":(trig["timestamp_ms"]-top["timestamp_ms"])/HOUR_MS,"hours_top_to_trough":(trough["timestamp_ms"]-top["timestamp_ms"])/HOUR_MS,"hours_trough_to_recovery":(r["timestamp_ms"]-trough["timestamp_ms"])/HOUR_MS,"active_alt_count_at_top":top["active_alt_count"],"authority":"OUTCOME_LABEL_RESEARCH_ONLY"})
                last_close_ts=ts; peak=r; active=None
    return episodes


def strict_build_matrix(features: list[dict], episodes: list[dict], out: Path):
    by_ts={(r["continuity_segment_id"],r["timestamp_ms"]):r for r in features}; rows=[]; coverage=[]
    specs=[("TOP",0),("TOP-72H",-72),("TOP-48H",-48),("TOP-24H",-24),("TOP-12H",-12),("TOP-6H",-6),("TOP-3H",-3)]
    for ep in episodes:
        seg=ep["continuity_segment_id"]; top=_iso_ms(ep["top_utc"]); trough=_iso_ms(ep["trough_utc"]); rec=_iso_ms(ep["recovery_utc"]); got=[]
        for label,off in specs:
            f=by_ts.get((seg,top+off*HOUR_MS));
            if f: rows.append({"episode_id":ep["episode_id"],"anchor":label,"relative_hour":off,"feature":f}); got.append(label)
        for label,t in (("TRIGGER",_iso_ms(ep["trigger_utc"])),("TROUGH",trough),("TROUGH+3H",trough+3*HOUR_MS),("TROUGH+6H",trough+6*HOUR_MS),("TROUGH+12H",trough+12*HOUR_MS),("RECOVERY",rec)):
            f=by_ts.get((seg,t));
            if f: rows.append({"episode_id":ep["episode_id"],"anchor":label,"feature":f}); got.append(label)
        coverage.append({"episode_id":ep["episode_id"],"required_anchor_count":13,"available_anchor_count":len(got),"available_anchors":got})
    with gzip.open(out/"EPISODE_FEATURE_MATRIX.jsonl.gz","wt",encoding="utf-8") as fh:
        for row in rows: fh.write(json.dumps(row,sort_keys=True)+"\n")
    (out/"EPISODE_MATRIX_COVERAGE.json").write_text(json.dumps({"contract":"EPISODE_MATRIX_COVERAGE_v1","episodes":coverage},indent=2,sort_keys=True)+"\n")


def strict_continuation_controls(features, episodes, window_start, window_end, n=3):
    by_ts={(r["continuity_segment_id"],r["timestamp_ms"]):r for r in features}; episode_tops=[_iso_ms(e["top_utc"]) for e in episodes]
    candidates=[]
    for r in features:
        ts=r["timestamp_ms"]
        if not (window_start<=ts<=window_end) or r.get("mean_return_24h_pct") is None or r["mean_return_24h_pct"]<3: continue
        seg=r["continuity_segment_id"]; fut=[by_ts.get((seg,ts+h*HOUR_MS)) for h in range(1,49)]
        if any(x is None for x in fut): continue
        future_min=min(float(x["ew_index"]) for x in fut); dd=(future_min/float(r["ew_index"])-1)*100
        if dd<=-5 or any(abs(ts-e)<7*24*HOUR_MS for e in episode_tops): continue
        candidates.append(r)
    modern_eps=[e for e in episodes if window_start<=_iso_ms(e["top_utc"])<=window_end]
    modern_eps=sorted(modern_eps,key=lambda e:abs(e["max_drawdown_pct"]),reverse=True)[:n]
    used=set(); out=[]
    keys=["mean_return_24h_pct","breadth_24h","dispersion_1h_pct","eth_minus_btc_24h_pp","active_alt_count"]
    fby={r["timestamp_utc"]:r for r in features}
    for idx,ep in enumerate(modern_eps,1):
        target=fby.get(ep["top_utc"])
        if not target: continue
        scored=[]
        for c in candidates:
            if c["timestamp_ms"] in used: continue
            score=0.0; terms=0
            for k in keys:
                a=target.get(k); b=c.get(k)
                if a is None or b is None: continue
                scale=max(1e-9,abs(float(a)),1.0); score+=abs(float(a)-float(b))/scale; terms+=1
            if terms: scored.append((score/terms,c))
        if not scored: continue
        scored.sort(key=lambda z:z[0]); score,c=scored[0]; used.add(c["timestamp_ms"])
        out.append({"control_id":f"CTRL_{idx:02d}","matched_episode_id":ep["episode_id"],"event_utc":c["timestamp_utc"],"basis":"MATCHED_STRONG_24H_CONTINUATION_WITHOUT_NEXT48H_5PCT_DRAWDOWN","matching_distance":score,"matching_features":keys,"future_outcome_used_for_control_label_only":True})
    return out


def _write_integrity(features: list[dict], cfg: dict, out: Path):
    gaps=[]; cross=[]; prev=None
    for r in features:
        if prev:
            dh=(r["timestamp_ms"]-prev["timestamp_ms"])/HOUR_MS
            if dh!=1 or r["research_window_id"]!=prev["research_window_id"]:
                gaps.append({"from":prev["timestamp_utc"],"to":r["timestamp_utc"],"hours":dh,"from_window":prev["research_window_id"],"to_window":r["research_window_id"]})
                if r["continuity_segment_id"]==prev["continuity_segment_id"]: cross.append(gaps[-1])
        prev=r
    doc={"contract":"HISTORICAL_TIME_INTEGRITY_AUDIT_v1","strict_timestamp_lags":True,"cross_window_lags_forbidden":True,"row_offsets_treated_as_hours":False,"feature_rows":len(features),"continuity_gap_count":len(gaps),"continuity_segment_violation_count":len(cross),"gaps":gaps[:200],"status":"PASS" if not cross else "FAIL","liquidity_cohort_label":"LIQUIDITY_COHORT_PROXY_NOT_MARKET_CAP"}
    (out/"TIME_INTEGRITY_AUDIT.json").write_text(json.dumps(doc,indent=2,sort_keys=True)+"\n")


def main():
    mod=load_target(); original=mod.fetch_klines
    def resilient(symbol,start_ms,end_ms):
        try:
            rows=list(original(symbol,start_ms,end_ms))
            if rows:
                SOURCE_EVENTS.append({"symbol":symbol,"start":_ms_iso(start_ms),"end":_ms_iso(end_ms),"source":"BINANCE_REST","rows":len(rows)}); yield from rows; return
        except Exception as exc:
            SOURCE_EVENTS.append({"symbol":symbol,"start":_ms_iso(start_ms),"end":_ms_iso(end_ms),"source":"BINANCE_REST_FAILED","error":str(exc)[:250]})
        rows=list(vision_klines(symbol,start_ms,end_ms)); SOURCE_EVENTS.append({"symbol":symbol,"start":_ms_iso(start_ms),"end":_ms_iso(end_ms),"source":"BINANCE_VISION_DAILY_PREFERRED_PRE_2022","rows":len(rows)}); yield from rows
    mod.fetch_klines=resilient; mod.build_features=lambda conn,cfg,out:strict_build_features(mod,conn,cfg,out); mod.add_derived=strict_add_derived; mod.build_episodes=strict_build_episodes; mod.build_matrix=strict_build_matrix; mod.continuation_controls=strict_continuation_controls
    rc=mod.main()
    out=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts")
    hp=out/"hourly_features.csv.gz"; features=[]
    if hp.exists():
        with gzip.open(hp,"rt",encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                for k in ("timestamp_ms","continuity_segment_id"): r[k]=int(float(r[k]))
                for k,v in list(r.items()):
                    if v=="": r[k]=None
                    elif k not in {"timestamp_utc","research_window_id","timestamp_ms","continuity_segment_id"}:
                        try:r[k]=float(v)
                        except Exception:pass
                features.append(r)
        _write_integrity(features,json.loads(Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/config.json").read_text()),out)
    ap=out/"FREE_SOURCE_AUDIT.json"
    if ap.exists():
        audit=json.loads(ap.read_text()); audit["source_resolution_events"]=SOURCE_EVENTS; audit.setdefault("limitations",[]).append("Historical Binance archives can be revised; Vision fallback prefers daily archives before 2022 to reduce stale-monthly revision risk."); audit["time_semantics"]="STRICT_TIMESTAMP_BASED_NO_POSITIONAL_HOUR_ASSUMPTIONS"; audit["liquidity_cohort_semantics"]="CROSS_SECTIONAL_QUOTE_VOLUME_PROXY_NOT_HISTORICAL_MARKET_CAP"; ap.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
    return rc


if __name__=='__main__': raise SystemExit(main())
