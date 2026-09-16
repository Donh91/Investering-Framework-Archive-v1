#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPASS_ROOT = ROOT / "05_COMPASS"
MIN_POINTS = 100

BINANCE = "https://api.binance.com"
FAPI = "https://fapi.binance.com"
COINGECKO = "https://api.coingecko.com/api/v3/global"


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def fetch_json(url: str, timeout: int = 20) -> tuple[Any | None, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "Investering-Framework-Action-Compass/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8")), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def num(value: Any) -> float | None:
    try:
        x = float(value)
        if math.isfinite(x):
            return x
    except (TypeError, ValueError):
        pass
    return None


def flatten(value: Any, prefix: str, out: dict[str, Any], limit: int = 1200) -> None:
    if len(out) >= limit:
        return
    if isinstance(value, dict):
        for key in sorted(value):
            flatten(value[key], f"{prefix}.{key}" if prefix else key, out, limit)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            flatten(item, f"{prefix}[{i}]", out, limit)
    elif value is None or isinstance(value, (str, int, float, bool)):
        out[prefix] = value


def latest_cn_context() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    pointer_path = ROOT / "05_CYCLE_NAVIGATOR" / "LATEST_CYCLE_NAVIGATOR_POINTER.json"
    pointer = read_json(pointer_path) or {}
    sources: list[dict[str, Any]] = []
    ctx: dict[str, Any] = {"pointer": pointer}
    if pointer:
        sources.append({"id": "cn_pointer", "kind": "internal", "path": str(pointer_path.relative_to(ROOT)), "data": pointer})
    week_dir = pointer.get("week_dir")
    if week_dir:
        week = ROOT / str(week_dir)
        for name, key in [
            ("CYCLE_NAVIGATOR_FORECAST_FREEZE.json", "forecast_freeze"),
            ("CYCLE_NAVIGATOR_MACHINE_PACKAGE.json", "machine_package"),
        ]:
            p = week / name
            data = read_json(p)
            if data is not None:
                ctx[key] = data
                sources.append({"id": f"cn_{key}", "kind": "internal", "path": str(p.relative_to(ROOT)), "data": data})
    return ctx, sources


def ext_source(source_id: str, url: str) -> dict[str, Any]:
    data, error = fetch_json(url)
    return {"id": source_id, "kind": "external", "url": url, "data": data, "error": error}


def kline_url(symbol: str) -> str:
    q = urllib.parse.urlencode({"symbol": symbol, "interval": "4h", "limit": 8})
    return f"{BINANCE}/api/v3/klines?{q}"


def collect_external() -> list[dict[str, Any]]:
    urls = {
        "binance_btc_24h": f"{BINANCE}/api/v3/ticker/24hr?symbol=BTCUSDT",
        "binance_eth_24h": f"{BINANCE}/api/v3/ticker/24hr?symbol=ETHUSDT",
        "binance_ethbtc_24h": f"{BINANCE}/api/v3/ticker/24hr?symbol=ETHBTC",
        "binance_btc_4h": kline_url("BTCUSDT"),
        "binance_eth_4h": kline_url("ETHUSDT"),
        "binance_ethbtc_4h": kline_url("ETHBTC"),
        "binance_btc_funding": f"{FAPI}/fapi/v1/premiumIndex?symbol=BTCUSDT",
        "binance_eth_funding": f"{FAPI}/fapi/v1/premiumIndex?symbol=ETHUSDT",
        "binance_btc_oi": f"{FAPI}/fapi/v1/openInterest?symbol=BTCUSDT",
        "binance_eth_oi": f"{FAPI}/fapi/v1/openInterest?symbol=ETHUSDT",
        "binance_btc_top_positions": f"{FAPI}/futures/data/topLongShortPositionRatio?symbol=BTCUSDT&period=1h&limit=1",
        "binance_eth_top_positions": f"{FAPI}/futures/data/topLongShortPositionRatio?symbol=ETHUSDT&period=1h&limit=1",
        "coingecko_global": COINGECKO,
    }
    return [ext_source(k, v) for k, v in urls.items()]


def source_map(sources: list[dict[str, Any]]) -> dict[str, Any]:
    return {s["id"]: s.get("data") for s in sources if s.get("data") is not None}


def kline_momentum(data: Any, periods: int = 3) -> float | None:
    if not isinstance(data, list) or len(data) < periods + 1:
        return None
    try:
        start = float(data[-(periods + 1)][4])
        end = float(data[-1][4])
        return (end / start - 1.0) * 100.0 if start else None
    except Exception:
        return None


def global_values(data: Any) -> tuple[float | None, float | None, float | None]:
    if not isinstance(data, dict):
        return None, None, None
    d = data.get("data", data)
    change = None
    btc_dom = None
    eth_dom = None
    try:
        change = num(d.get("market_cap_change_percentage_24h_usd"))
        pcts = d.get("market_cap_percentage") or {}
        btc_dom = num(pcts.get("btc"))
        eth_dom = num(pcts.get("eth"))
    except Exception:
        pass
    return change, btc_dom, eth_dom


def signal(value: float | None, threshold: float) -> float | None:
    if value is None:
        return None
    if value >= threshold:
        return 1.0
    if value <= -threshold:
        return -1.0
    return 0.0


def direction(score: float) -> str:
    if score >= 0.20:
        return "BULLISH"
    if score <= -0.20:
        return "BEARISH"
    return "NEUTRAL"


def action_for(score: float, allow_deploy: bool = False) -> str:
    if score <= -0.75:
        return "DE_RISK"
    if score <= -0.20:
        return "WAIT"
    if score < 0.20:
        return "HOLD"
    if score < 0.65 or not allow_deploy:
        return "PREPARE"
    return "DEPLOY"


def confidence(score: float, components: int, expected: int) -> float:
    coverage = min(1.0, components / max(1, expected))
    return round(min(0.95, 0.45 + 0.35 * abs(score) + 0.15 * coverage), 2)


def weighted_score(values: list[tuple[float | None, float]]) -> tuple[float, int]:
    used = [(v, w) for v, w in values if v is not None]
    if not used:
        return 0.0, 0
    denom = sum(abs(w) for _, w in used)
    return (sum(v * w for v, w in used) / denom if denom else 0.0), len(used)


def derive(smap: dict[str, Any]) -> dict[str, Any]:
    btc = smap.get("binance_btc_24h") or {}
    eth = smap.get("binance_eth_24h") or {}
    eb = smap.get("binance_ethbtc_24h") or {}
    global_change, btc_dom, eth_dom = global_values(smap.get("coingecko_global"))

    btc_px = num(btc.get("lastPrice"))
    eth_px = num(eth.get("lastPrice"))
    eb_px = num(eb.get("lastPrice"))
    btc_24 = num(btc.get("priceChangePercent"))
    eth_24 = num(eth.get("priceChangePercent"))
    eb_24 = num(eb.get("priceChangePercent"))
    btc_12 = kline_momentum(smap.get("binance_btc_4h"), 3)
    eth_12 = kline_momentum(smap.get("binance_eth_4h"), 3)
    eb_12 = kline_momentum(smap.get("binance_ethbtc_4h"), 3)

    sigs = [
        (signal(btc_24, 1.0), 1.2),
        (signal(eth_24, 1.0), 1.0),
        (signal(eb_24, 0.35), 0.7),
        (signal(global_change, 1.0), 0.9),
        (signal(btc_12, 0.75), 1.0),
        (signal(eth_12, 0.75), 0.8),
        (signal(eb_12, 0.25), 0.5),
    ]
    score, count = weighted_score(sigs)

    h12 = score
    d13 = score * 0.72
    d57 = score * 0.42

    return {
        "score_now": round(score, 4),
        "component_count": count,
        "score_h12": round(h12, 4),
        "score_d1_3": round(d13, 4),
        "score_d5_7": round(d57, 4),
        "market": {
            "btc_usd": btc_px,
            "eth_usd": eth_px,
            "ethbtc": eb_px,
            "btc_change_24h_pct": btc_24,
            "eth_change_24h_pct": eth_24,
            "ethbtc_change_24h_pct": eb_24,
            "btc_change_12h_pct": None if btc_12 is None else round(btc_12, 4),
            "eth_change_12h_pct": None if eth_12 is None else round(eth_12, 4),
            "ethbtc_change_12h_pct": None if eb_12 is None else round(eb_12, 4),
            "total_market_change_24h_pct": global_change,
            "btc_dominance_pct": btc_dom,
            "eth_dominance_pct": eth_dom,
            "btc_24h_low": num(btc.get("lowPrice")),
            "btc_24h_high": num(btc.get("highPrice")),
            "btc_24h_weighted_avg": num(btc.get("weightedAvgPrice")),
            "eth_24h_low": num(eth.get("lowPrice")),
            "eth_24h_high": num(eth.get("highPrice")),
            "eth_24h_weighted_avg": num(eth.get("weightedAvgPrice")),
            "ethbtc_24h_low": num(eb.get("lowPrice")),
            "ethbtc_24h_high": num(eb.get("highPrice")),
            "btc_funding_rate": num((smap.get("binance_btc_funding") or {}).get("lastFundingRate")),
            "eth_funding_rate": num((smap.get("binance_eth_funding") or {}).get("lastFundingRate")),
            "btc_open_interest": num((smap.get("binance_btc_oi") or {}).get("openInterest")),
            "eth_open_interest": num((smap.get("binance_eth_oi") or {}).get("openInterest")),
        },
    }


def fmt_level(value: float | None, decimals: int = 0) -> str:
    if value is None:
        return "available confirmation level"
    return f"{value:,.{decimals}f}"


def horizon_obj(name: str, score: float, at: datetime, maturity: datetime | None, market: dict[str, Any], comp_count: int) -> dict[str, Any]:
    d = direction(score)
    a = action_for(score)
    btc_avg = market.get("btc_24h_weighted_avg")
    eth_avg = market.get("eth_24h_weighted_avg")
    btc_low = market.get("btc_24h_low")
    eth_low = market.get("eth_24h_low")
    if d == "BEARISH":
        expl = "Downside pressure remains dominant; require reclaim and stabilization before increasing risk."
    elif d == "BULLISH":
        expl = "Current evidence is constructive, but risk should advance only if strength survives pullbacks and broadens."
    else:
        expl = "Evidence is mixed or range-bound; preserve optionality and wait for a directional confirmation."
    trigger = f"BTC holds/reclaims ~{fmt_level(btc_avg)} and ETH holds/reclaims ~{fmt_level(eth_avg)} with ETH/BTC stabilization."
    invalid = f"Acceptance below recent BTC ~{fmt_level(btc_low)} / ETH ~{fmt_level(eth_low)} lows without rapid reclaim."
    windows = {"NOW": "now", "H12": "next 12 hours", "D1_3": "next 1–3 days", "D5_7": "next 5–7 days"}
    return {
        "direction": d,
        "action": a,
        "confidence": confidence(score, comp_count, 7),
        "window": windows[name],
        "explanation": expl,
        "confirmation_trigger": trigger,
        "invalidation": invalid,
        "maturity_at_utc": None if maturity is None else iso(maturity),
    }


def ladder(derived: dict[str, Any]) -> dict[str, Any]:
    m = derived["market"]
    s = derived["score_now"]
    eb24 = m.get("ethbtc_change_24h_pct")
    global24 = m.get("total_market_change_24h_pct")
    btc_status = "DE_RISK" if s <= -0.75 else ("WAIT" if s <= -0.2 else "HOLD")
    eth_rel_ok = eb24 is not None and eb24 >= 0
    eth_status = "PREPARE" if s > 0.2 and eth_rel_ok else ("WAIT" if s < -0.2 or not eth_rel_ok else "HOLD")
    large_ready = s > 0.2 and eth_rel_ok and global24 is not None and global24 > 0
    large_status = "PREPARE" if large_ready else "WAIT"
    return {
        "BTC": {
            "status": btc_status,
            "eta": "0–24h monitoring",
            "why": "BTC is the liquidity anchor; preserve core exposure while short-horizon structure resolves.",
            "trigger": "Sustained reclaim of the 24h weighted-average zone with improving market breadth.",
            "invalidation": "Acceptance below the recent 24h low without rapid reclaim."
        },
        "ETH": {
            "status": eth_status,
            "eta": "12–48h if relative strength confirms",
            "why": "ETH needs both absolute stabilization and ETH/BTC relative-strength confirmation.",
            "trigger": "ETH reclaims its 24h weighted-average zone and ETH/BTC turns non-negative/persistent.",
            "invalidation": "ETH underperforms BTC while both lose recent support."
        },
        "LARGE_CAP": {
            "status": large_status,
            "eta": "1–3d earliest",
            "why": "Large-cap expansion should follow durable ETH-relative strength, not precede it.",
            "trigger": "ETH/BTC strength plus positive broader-market participation survives a pullback.",
            "invalidation": "Leadership remains isolated to BTC/ETH or breadth deteriorates."
        },
        "MID_CAP": {
            "status": "WAIT",
            "eta": "3–7d earliest; conditional",
            "why": "Mid-cap transmission requires broader participation evidence not inferable from majors alone.",
            "trigger": "Large-cap leadership persists and eligible breadth/transmission evidence confirms expansion.",
            "invalidation": "Large-cap leadership fails or breadth remains weak."
        },
        "SMALL_CAP": {
            "status": "WAIT",
            "eta": "5–14d earliest; no fixed ETA without transmission",
            "why": "Small-cap risk stays fail-closed until mid-cap transmission is established.",
            "trigger": "Confirmed mid-cap transmission plus improving breadth and pullback resilience.",
            "invalidation": "Mid-cap transmission fails or liquidity retreats to majors."
        },
        "MICRO_CAP": {
            "status": "WAIT",
            "eta": "7d+ / unbounded until broad speculative expansion",
            "why": "Microcaps are last in the rotation ladder and require broad risk appetite, not a majors-only bounce.",
            "trigger": "Sustained small-cap expansion, broad breadth and persistent risk-on conditions.",
            "invalidation": "Any break in the upstream rotation ladder or renewed liquidity concentration."
        }
    }


def cn_alignment(cn: dict[str, Any], d57: str) -> dict[str, Any]:
    pointer = cn.get("pointer") or {}
    freeze = cn.get("forecast_freeze") or {}
    text = " ".join(str(x) for x in freeze.get("structural_calls", []))
    issue = pointer.get("issue_number")
    if not pointer:
        return {"state": "UNAVAILABLE", "explanation": "No current Cycle Navigator pointer was available.", "cn_issue_number": None}
    if "unresolved" in text.lower() and d57 == "NEUTRAL":
        state = "ALIGNED"
        explanation = "Daily 5–7d Compass remains consistent with the active CN unresolved/consolidation base case."
    elif "unresolved" in text.lower() and d57 in {"BULLISH", "BEARISH"}:
        state = "TACTICAL_DIVERGENCE"
        explanation = "Daily evidence is directional while the active CN weekly freeze remains unresolved; divergence is preserved for later scoring."
    else:
        state = "UNAVAILABLE"
        explanation = "CN alignment could not be classified mechanically without inventing a weekly directional label."
    return {"state": state, "explanation": explanation, "cn_issue_number": int(issue) if str(issue).isdigit() else None}


def evidence(sources: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    points: dict[str, Any] = {}
    source_rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for s in sources:
        sid = s["id"]
        data = s.get("data")
        local: dict[str, Any] = {}
        if data is not None:
            flatten(data, sid, local)
            points.update(local)
        else:
            missing.append(sid)
        row = {"id": sid, "kind": s.get("kind"), "available": data is not None, "scalar_points": len(local)}
        if s.get("url"):
            row["source"] = s["url"]
        if s.get("path"):
            row["source"] = s["path"]
        if s.get("error"):
            row["error"] = s["error"]
        source_rows.append(row)
    keys_hash = hashlib.sha256("\n".join(sorted(points)).encode("utf-8")).hexdigest()
    manifest = {
        "observed_scalar_points": len(points),
        "minimum_breadth_target": MIN_POINTS,
        "breadth_target_met": len(points) >= MIN_POINTS,
        "source_families_expected": len(sources),
        "source_families_available": sum(1 for s in sources if s.get("data") is not None),
        "missing_sources": missing,
        "point_keys_sha256": keys_hash,
        "sources": source_rows
    }
    return manifest, points


def build(mode: str) -> Path | None:
    at = utcnow()
    cn, internal_sources = latest_cn_context()
    sources = internal_sources + collect_external()
    smap = source_map(sources)
    derived = derive(smap)
    manifest, points = evidence(sources)

    if mode == "daily":
        out = COMPASS_ROOT / "daily" / f"{at.year:04d}" / f"{at.month:02d}" / f"{at.date().isoformat()}__DAILY_COMPASS.json"
        artifact_type = "DAILY_COMPASS_FREEZE"
        freeze_id = f"COMPASS-{at.date().isoformat()}-DAILY"
        if out.exists():
            print(f"Daily Compass already frozen: {out.relative_to(ROOT)}")
            return None
    else:
        stamp = at.strftime("%Y-%m-%dT%H%M%SZ")
        out = COMPASS_ROOT / "events" / f"{at.year:04d}" / f"{at.month:02d}" / f"{stamp}__EVENT_COMPASS.json"
        artifact_type = "EVENT_COMPASS_FREEZE"
        freeze_id = f"COMPASS-{stamp}-EVENT"

    scores = {
        "NOW": derived["score_now"],
        "H12": derived["score_h12"],
        "D1_3": derived["score_d1_3"],
        "D5_7": derived["score_d5_7"]
    }
    horizons = {
        "NOW": horizon_obj("NOW", scores["NOW"], at, None, derived["market"], derived["component_count"]),
        "H12": horizon_obj("H12", scores["H12"], at, at + timedelta(hours=12), derived["market"], derived["component_count"]),
        "D1_3": horizon_obj("D1_3", scores["D1_3"], at, at + timedelta(hours=72), derived["market"], derived["component_count"]),
        "D5_7": horizon_obj("D5_7", scores["D5_7"], at, at + timedelta(hours=168), derived["market"], derived["component_count"])
    }
    align = cn_alignment(cn, horizons["D5_7"]["direction"])
    degraded = bool(manifest["missing_sources"]) or not manifest["breadth_target_met"]

    now_d = horizons["NOW"]["direction"].lower()
    payload = {
        "schema_version": "ACTION_COMPASS_V1",
        "freeze_id": freeze_id,
        "artifact_type": artifact_type,
        "generated_at_utc": iso(at),
        "as_of_utc": iso(at),
        "authority": "NAVIGATION_ONLY",
        "immutable": True,
        "status": "DEGRADED" if degraded else "OK",
        "market_state": {
            "direction": horizons["NOW"]["direction"],
            "action": horizons["NOW"]["action"],
            "confidence": horizons["NOW"]["confidence"],
            "summary": f"Current evidence is {now_d}; preserve confirmation discipline and do not infer broad rotation from majors alone.",
            "market": derived["market"]
        },
        "horizons": horizons,
        "capitalization_ladder": ladder(derived),
        "evidence_manifest": manifest,
        "evidence_snapshot": {"points": points},
        "cn_alignment": align,
        "conclusion": {
            "now": f"Market now: {horizons['NOW']['direction']} / {horizons['NOW']['action']}.",
            "next_12h": f"Next 12h: {horizons['H12']['direction']} / {horizons['H12']['action']}; wait for confirmation trigger before changing risk.",
            "next_1_3d": f"Next 1–3d: {horizons['D1_3']['direction']} / {horizons['D1_3']['action']}.",
            "next_5_7d": f"Next 5–7d: {horizons['D5_7']['direction']} / {horizons['D5_7']['action']}; weekly CN alignment = {align['state']}.",
            "action": "Use the capitalization ladder and horizon triggers; smaller-cap deployment remains fail-closed until eligible breadth/transmission evidence confirms."
        }
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    pointer = {
        "contract": "LATEST_ACTION_COMPASS_POINTER_V1",
        "freeze_id": freeze_id,
        "artifact_type": artifact_type,
        "as_of_utc": iso(at),
        "status": payload["status"],
        "freeze_path": str(out.relative_to(ROOT)),
        "freeze_sha256": digest,
        "authority": "NAVIGATION_ONLY"
    }
    (COMPASS_ROOT / "LATEST_COMPASS.json").write_text(json.dumps(pointer, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)} ({manifest['observed_scalar_points']} scalar evidence points)")
    return out


def validate_latest() -> None:
    pointer_path = COMPASS_ROOT / "LATEST_COMPASS.json"
    pointer = read_json(pointer_path)
    if not isinstance(pointer, dict):
        raise SystemExit("LATEST_COMPASS.json missing or invalid")
    rel = pointer.get("freeze_path")
    if not rel:
        raise SystemExit("LATEST_COMPASS has no freeze_path")
    freeze_path = ROOT / rel
    freeze = read_json(freeze_path)
    required = ["schema_version", "freeze_id", "artifact_type", "generated_at_utc", "as_of_utc", "authority", "immutable", "market_state", "horizons", "capitalization_ladder", "evidence_manifest", "cn_alignment", "conclusion"]
    missing = [k for k in required if k not in (freeze or {})]
    if missing:
        raise SystemExit(f"Compass contract missing: {missing}")
    if freeze["schema_version"] != "ACTION_COMPASS_V1" or freeze["authority"] != "NAVIGATION_ONLY" or freeze["immutable"] is not True:
        raise SystemExit("Compass authority/immutability invariant failed")
    if set(freeze["horizons"]) != {"NOW", "H12", "D1_3", "D5_7"}:
        raise SystemExit("Compass horizon set failed")
    if set(freeze["capitalization_ladder"]) != {"BTC", "ETH", "LARGE_CAP", "MID_CAP", "SMALL_CAP", "MICRO_CAP"}:
        raise SystemExit("Compass ladder set failed")
    actual = hashlib.sha256(freeze_path.read_bytes()).hexdigest()
    if actual != pointer.get("freeze_sha256"):
        raise SystemExit("LATEST_COMPASS hash mismatch")
    print("Compass contract check: PASS")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["daily", "event"], default="daily")
    p.add_argument("--validate-latest", action="store_true")
    args = p.parse_args()
    if args.validate_latest:
        validate_latest()
        return
    build(args.mode)
    validate_latest()


if __name__ == "__main__":
    main()
