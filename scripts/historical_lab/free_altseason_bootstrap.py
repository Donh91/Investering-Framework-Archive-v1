#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import gzip
import json
import math
import sqlite3
import statistics
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

BINANCE = "https://api.binance.com/api/v3/klines"
ALT_FNG = "https://api.alternative.me/fng/?limit=0&format=json"
DEFILLAMA = "https://stablecoins.llama.fi/stablecoincharts/all"
UA = {"User-Agent": "Investering-Historical-Altseason-Lab/1.0", "Accept": "application/json"}


def iso_to_ms(value: str) -> int:
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def ms_to_iso(value: int) -> str:
    return datetime.fromtimestamp(value / 1000, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def fetch_json(url: str, retries: int = 5):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except Exception as exc:
            last = exc
            time.sleep(min(8, 0.7 * (2 ** attempt)))
    raise RuntimeError(f"fetch_failed:{url}:{last}")


def fetch_klines(symbol: str, start_ms: int, end_ms: int):
    cursor = start_ms
    while cursor <= end_ms:
        q = urllib.parse.urlencode({
            "symbol": symbol,
            "interval": "1h",
            "startTime": cursor,
            "endTime": end_ms,
            "limit": 1000,
        })
        rows = fetch_json(BINANCE + "?" + q)
        if not isinstance(rows, list) or not rows:
            break
        for row in rows:
            yield row
        nxt = int(rows[-1][0]) + 3600_000
        if nxt <= cursor:
            break
        cursor = nxt
        time.sleep(0.05)


def init_db(conn: sqlite3.Connection):
    conn.executescript("""
    PRAGMA journal_mode=OFF;
    PRAGMA synchronous=OFF;
    CREATE TABLE bars(
      symbol TEXT NOT NULL,
      ts INTEGER NOT NULL,
      close REAL NOT NULL,
      quote_volume REAL,
      trades INTEGER,
      taker_buy_quote REAL,
      PRIMARY KEY(symbol, ts)
    );
    CREATE INDEX bars_ts ON bars(ts);
    """)


def ingest_symbol(conn: sqlite3.Connection, symbol: str, windows: list[dict]) -> dict:
    inserted = 0
    errors = []
    first_ts = None
    last_ts = None
    for w in windows:
        try:
            batch = []
            for r in fetch_klines(symbol, iso_to_ms(w["start_utc"]), iso_to_ms(w["end_utc"])):
                ts = int(r[0])
                batch.append((symbol, ts, float(r[4]), float(r[7]), int(r[8]), float(r[10])))
                first_ts = ts if first_ts is None else min(first_ts, ts)
                last_ts = ts if last_ts is None else max(last_ts, ts)
                if len(batch) >= 5000:
                    conn.executemany("INSERT OR REPLACE INTO bars VALUES(?,?,?,?,?,?)", batch)
                    inserted += len(batch); batch.clear()
            if batch:
                conn.executemany("INSERT OR REPLACE INTO bars VALUES(?,?,?,?,?,?)", batch)
                inserted += len(batch)
            conn.commit()
        except Exception as exc:
            errors.append({"window": w["id"], "error": str(exc)[:300]})
    return {
        "symbol": symbol,
        "row_count": inserted,
        "first_utc": ms_to_iso(first_ts) if first_ts is not None else None,
        "last_utc": ms_to_iso(last_ts) if last_ts is not None else None,
        "errors": errors,
    }


def load_daily_controls() -> tuple[list[tuple[int, float]], list[tuple[int, float]]]:
    fng = []
    stable = []
    try:
        doc = fetch_json(ALT_FNG)
        for r in doc.get("data", []):
            try: fng.append((int(r["timestamp"]) * 1000, float(r["value"])))
            except Exception: pass
        fng.sort()
    except Exception:
        pass
    try:
        doc = fetch_json(DEFILLAMA)
        rows = doc if isinstance(doc, list) else doc.get("peggedUSD", [])
        if isinstance(rows, list):
            for r in rows:
                try:
                    ts = int(r.get("date") or r.get("timestamp")) * 1000
                    total = r.get("totalCirculatingUSD")
                    if isinstance(total, dict): total = sum(float(v or 0) for v in total.values())
                    stable.append((ts, float(total)))
                except Exception: pass
        stable.sort()
    except Exception:
        pass
    return fng, stable


def latest_before(rows: list[tuple[int, float]], ts: int):
    lo, hi = 0, len(rows)
    while lo < hi:
        mid = (lo + hi) // 2
        if rows[mid][0] <= ts: lo = mid + 1
        else: hi = mid
    return rows[lo - 1] if lo else (None, None)


def build_features(conn: sqlite3.Connection, cfg: dict, out: Path) -> list[dict]:
    alts = cfg["alt_symbols"]
    min_active = int(cfg["minimum_active_alts_per_hour"])
    fng, stable = load_daily_controls()
    qmarks = ",".join("?" for _ in alts)
    query = f"""
    WITH e AS (
      SELECT symbol, ts, close, quote_volume, trades,
             CASE WHEN quote_volume>0 THEN taker_buy_quote/quote_volume END AS taker_share,
             LAG(close,1) OVER(PARTITION BY symbol ORDER BY ts) AS c1,
             LAG(close,6) OVER(PARTITION BY symbol ORDER BY ts) AS c6,
             LAG(close,24) OVER(PARTITION BY symbol ORDER BY ts) AS c24
      FROM bars WHERE symbol IN ({qmarks})
    )
    SELECT symbol,ts,close,quote_volume,trades,taker_share,
           CASE WHEN c1>0 THEN (close/c1-1)*100 END r1,
           CASE WHEN c6>0 THEN (close/c6-1)*100 END r6,
           CASE WHEN c24>0 THEN (close/c24-1)*100 END r24
    FROM e ORDER BY ts,symbol
    """
    cur = conn.execute(query, alts)
    groups = defaultdict(list)
    for row in cur:
        groups[int(row[1])].append(row)

    core = {}
    for sym in cfg["core_symbols"]:
        core[sym] = {int(ts): float(close) for ts, close in conn.execute("SELECT ts,close FROM bars WHERE symbol=?", (sym,))}

    features = []
    ew_index = 100.0
    prev_ts = None
    for ts in sorted(groups):
        rows = groups[ts]
        r1 = [float(r[6]) for r in rows if r[6] is not None]
        r6 = [float(r[7]) for r in rows if r[7] is not None]
        r24 = [float(r[8]) for r in rows if r[8] is not None]
        if len(r1) < min_active:
            continue
        mean1 = statistics.fmean(r1)
        ew_index *= 1.0 + mean1 / 100.0
        vols = [float(r[3]) for r in rows if r[3] is not None]
        trades = [int(r[4]) for r in rows if r[4] is not None]
        taker = [float(r[5]) for r in rows if r[5] is not None]
        fng_ts, fng_v = latest_before(fng, ts)
        st_ts, st_v = latest_before(stable, ts)
        btc = core.get("BTCUSDT", {}).get(ts)
        eth = core.get("ETHUSDT", {}).get(ts)
        ethbtc = core.get("ETHBTC", {}).get(ts)
        feat = {
            "timestamp_utc": ms_to_iso(ts),
            "timestamp_ms": ts,
            "active_alt_count": len(r1),
            "ew_index": ew_index,
            "ew_return_1h_pct": mean1,
            "median_return_1h_pct": statistics.median(r1),
            "dispersion_1h_pct": statistics.pstdev(r1) if len(r1) > 1 else 0.0,
            "breadth_1h": sum(v > 0 for v in r1) / len(r1),
            "breadth_6h": None if not r6 else sum(v > 0 for v in r6) / len(r6),
            "breadth_24h": None if not r24 else sum(v > 0 for v in r24) / len(r24),
            "mean_return_6h_pct": None if not r6 else statistics.fmean(r6),
            "mean_return_24h_pct": None if not r24 else statistics.fmean(r24),
            "median_taker_buy_share": None if not taker else statistics.median(taker),
            "total_quote_volume": sum(vols),
            "total_trade_count": sum(trades),
            "btc_usdt": btc,
            "eth_usdt": eth,
            "ethbtc": ethbtc,
            "free_fng_daily": fng_v,
            "free_fng_source_utc": ms_to_iso(fng_ts) if fng_ts else None,
            "stablecoin_total_usd_daily": st_v,
            "stablecoin_source_utc": ms_to_iso(st_ts) if st_ts else None,
            "prev_feature_ts_ms": prev_ts,
        }
        features.append(feat)
        prev_ts = ts

    if features:
        fields = list(features[0].keys())
        with gzip.open(out / "hourly_features.csv.gz", "wt", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(features)
    return features


def add_derived(features: list[dict]):
    by_ts = {r["timestamp_ms"]: r for r in features}
    for i, r in enumerate(features):
        for h in (1, 6, 24):
            j = i - h
            if j >= 0:
                p = features[j]
                for asset in ("btc_usdt", "eth_usdt", "ethbtc"):
                    a, b = r.get(asset), p.get(asset)
                    r[f"{asset}_return_{h}h_pct"] = None if not a or not b else (a / b - 1.0) * 100.0
        b24 = r.get("btc_usdt_return_24h_pct")
        e24 = r.get("eth_usdt_return_24h_pct")
        r["eth_minus_btc_24h_pp"] = None if b24 is None or e24 is None else e24 - b24
    return by_ts


def build_episodes(features: list[dict], cfg: dict) -> list[dict]:
    trigger = float(cfg["episode_drawdown_trigger_pct"])
    sep = int(cfg["episode_min_separation_hours"])
    recovery_fraction = float(cfg["episode_recovery_fraction"])
    levels = [float(x) for x in cfg["episode_severity_levels_pct"]]
    episodes = []
    peak_idx = None
    peak_val = -math.inf
    active = None
    last_close_idx = -10_000
    for i, r in enumerate(features):
        val = float(r["ew_index"])
        if active is None:
            if val > peak_val:
                peak_val, peak_idx = val, i
            dd = (val / peak_val - 1.0) * 100.0 if peak_val > 0 else 0.0
            if dd <= -trigger and i - last_close_idx >= sep:
                active = {"top_idx": peak_idx, "trigger_idx": i, "trough_idx": i, "trough_val": val, "peak_val": peak_val}
        else:
            if val < active["trough_val"]:
                active["trough_val"], active["trough_idx"] = val, i
            threshold = active["trough_val"] + recovery_fraction * (active["peak_val"] - active["trough_val"])
            if val >= threshold and i > active["trough_idx"]:
                top = features[active["top_idx"]]
                trig = features[active["trigger_idx"]]
                trough = features[active["trough_idx"]]
                max_dd = (active["trough_val"] / active["peak_val"] - 1.0) * 100.0
                ep = {
                    "episode_id": f"PB_{top['timestamp_utc'][:10]}_{len(episodes)+1:03d}",
                    "top_utc": top["timestamp_utc"],
                    "trigger_utc": trig["timestamp_utc"],
                    "trough_utc": trough["timestamp_utc"],
                    "recovery_utc": r["timestamp_utc"],
                    "max_drawdown_pct": max_dd,
                    "severity_flags": {f"ge_{int(x)}pct": abs(max_dd) >= x for x in levels},
                    "hours_top_to_trough": active["trough_idx"] - active["top_idx"],
                    "hours_trough_to_recovery": i - active["trough_idx"],
                    "active_alt_count_at_top": top["active_alt_count"],
                    "authority": "OUTCOME_LABEL_RESEARCH_ONLY",
                }
                episodes.append(ep)
                last_close_idx = i
                peak_val, peak_idx = val, i
                active = None
    return episodes


def feature_at(features: list[dict], idx: int, offset_h: int):
    j = idx + offset_h
    return None if j < 0 or j >= len(features) else features[j]


def build_matrix(features: list[dict], episodes: list[dict], out: Path):
    index = {r["timestamp_utc"]: i for i, r in enumerate(features)}
    offsets = [-72, -48, -24, -12, -6, -3, 0]
    rows = []
    for ep in episodes:
        top_i = index.get(ep["top_utc"]); trough_i = index.get(ep["trough_utc"]); rec_i = index.get(ep["recovery_utc"])
        if top_i is None: continue
        for off in offsets:
            f = feature_at(features, top_i, off)
            if f: rows.append({"episode_id": ep["episode_id"], "anchor": f"TOP{off:+d}H", "feature": f})
        for anchor, j in (("TROUGH", trough_i), ("TROUGH+3H", None if trough_i is None else trough_i+3), ("TROUGH+6H", None if trough_i is None else trough_i+6), ("TROUGH+12H", None if trough_i is None else trough_i+12), ("RECOVERY", rec_i)):
            if j is not None and 0 <= j < len(features): rows.append({"episode_id": ep["episode_id"], "anchor": anchor, "feature": features[j]})
    with gzip.open(out / "EPISODE_FEATURE_MATRIX.jsonl.gz", "wt", encoding="utf-8") as fh:
        for row in rows: fh.write(json.dumps(row, sort_keys=True) + "\n")


def continuation_controls(features: list[dict], episodes: list[dict], window_start: int, window_end: int, n=3):
    episode_ts = [datetime.fromisoformat(e["top_utc"].replace("Z", "+00:00")).timestamp()*1000 for e in episodes]
    candidates = []
    for i, r in enumerate(features):
        ts = r["timestamp_ms"]
        if ts < window_start or ts > window_end or i < 24 or i + 48 >= len(features): continue
        r24 = r.get("mean_return_24h_pct")
        if r24 is None or r24 < 3: continue
        future = min(float(x["ew_index"]) for x in features[i:i+49])
        dd = (future / float(r["ew_index"]) - 1) * 100
        if dd <= -5: continue
        if any(abs(ts - e) < 7*24*3600_000 for e in episode_ts): continue
        candidates.append((r24, i))
    candidates.sort(reverse=True)
    picked=[]
    for _, i in candidates:
        ts=features[i]["timestamp_ms"]
        if all(abs(ts-features[j]["timestamp_ms"]) >= 7*24*3600_000 for j in picked):
            picked.append(i)
            if len(picked)>=n: break
    return [{"control_id":f"CTRL_{k+1:02d}","event_utc":features[i]["timestamp_utc"],"basis":"STRONG_24H_CONTINUATION_WITHOUT_NEXT48H_5PCT_DRAWDOWN"} for k,i in enumerate(picked)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/config.json"))
    ap.add_argument("--output", type=Path, default=Path("06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts"))
    args = ap.parse_args(); args.output.mkdir(parents=True, exist_ok=True)
    cfg = json.loads(args.config.read_text())
    with tempfile.TemporaryDirectory() as td:
        conn = sqlite3.connect(Path(td)/"history.sqlite")
        init_db(conn)
        audit = {"contract":"HISTORICAL_ALTSEASON_FREE_SOURCE_AUDIT_v1","generated_at_utc":datetime.now(timezone.utc).isoformat(),"symbols":[],"limitations":["Research alt universe is survivorship-limited and is not claimed to be exact historical Top100 membership.","CFGI begins after the 2021 study window and is not fabricated into 2021."],"authority":cfg["authority"]}
        for sym in cfg["core_symbols"] + cfg["alt_symbols"]:
            res = ingest_symbol(conn, sym, cfg["research_windows"]); audit["symbols"].append(res)
            print(json.dumps({"symbol":sym,"rows":res["row_count"],"errors":len(res["errors"])}))
        (args.output/"FREE_SOURCE_AUDIT.json").write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
        features = build_features(conn, cfg, args.output)
    by_ts = add_derived(features)
    episodes = build_episodes(features, cfg)
    modern = next(w for w in cfg["research_windows"] if w["id"]=="MODERN_ANALOGUE_2025_2026")
    modern_start, modern_end = iso_to_ms(modern["start_utc"]), iso_to_ms(modern["end_utc"])
    modern_eps = [e for e in episodes if modern_start <= iso_to_ms(e["top_utc"]) <= modern_end]
    modern_eps_sorted = sorted(modern_eps, key=lambda e: abs(e["max_drawdown_pct"]), reverse=True)[:cfg["cfgi"]["max_pullback_windows"]]
    controls = continuation_controls(features, episodes, modern_start, modern_end, cfg["cfgi"]["max_control_windows"])
    catalog = {
        "contract":"HISTORICAL_ALTSEASON_EPISODE_CATALOG_v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "episode_count":len(episodes),
        "episodes":episodes,
        "cfgi_candidate_windows":{
            "pullbacks":[{"episode_id":e["episode_id"],"event_utc":e["top_utc"],"max_drawdown_pct":e["max_drawdown_pct"]} for e in modern_eps_sorted],
            "controls":controls,
            "selection_precedes_cfgi_query":True,
        },
        "authority":cfg["authority"],
    }
    (args.output/"EPISODE_CATALOG.json").write_text(json.dumps(catalog,indent=2,sort_keys=True)+"\n")
    build_matrix(features, episodes, args.output)
    summary = {
        "contract":"HISTORICAL_ALTSEASON_BACKTEST_SUMMARY_v1",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "free_hourly_feature_rows":len(features),
        "episode_count":len(episodes),
        "modern_cfgi_pullback_candidates":len(modern_eps_sorted),
        "modern_cfgi_continuation_controls":len(controls),
        "cfgi_status":"PENDING_TARGETED_ENRICHMENT",
        "machine_realistic_trim_reload_status":"NOT_TRAINED_YET",
        "perfect_hindsight_is_not_execution":"ACKNOWLEDGED",
        "authority":cfg["authority"],
    }
    (args.output/"BACKTEST_SUMMARY.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,sort_keys=True))

if __name__ == "__main__":
    main()
