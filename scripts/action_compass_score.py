#!/usr/bin/env python3
from __future__ import annotations

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
BINANCE = "https://api.binance.com"
HORIZONS = {"H12": 12, "H72": 72, "H168": 168}


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def fetch_json(url: str, timeout: int = 20) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "Investering-Framework-Action-Compass-Scorer/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def price_at(symbol: str, when: datetime) -> float | None:
    ms = int(when.timestamp() * 1000)
    q = urllib.parse.urlencode({"symbol": symbol, "interval": "1m", "startTime": ms, "limit": 1})
    try:
        rows = fetch_json(f"{BINANCE}/api/v3/klines?{q}")
        if not rows:
            return None
        return float(rows[0][4])
    except Exception:
        return None


def pct(start: float | None, end: float | None) -> float | None:
    if start is None or end is None or start == 0:
        return None
    x = (end / start - 1.0) * 100.0
    return round(x, 4) if math.isfinite(x) else None


def realized_direction(proxy: float | None) -> str | None:
    if proxy is None:
        return None
    if proxy > 1.0:
        return "BULLISH"
    if proxy < -1.0:
        return "BEARISH"
    return "NEUTRAL"


def direction_score(pred: str, real: str | None) -> int | None:
    if real is None:
        return None
    if pred == real:
        return 100
    if "NEUTRAL" in {pred, real}:
        return 50
    return 0


def action_score(action: str, real: str | None) -> int | None:
    if real is None:
        return None
    if action in {"PREPARE", "DEPLOY"}:
        return 100 if real == "BULLISH" else (50 if real == "NEUTRAL" else 0)
    if action in {"WAIT", "DE_RISK"}:
        return 100 if real == "BEARISH" else (75 if real == "NEUTRAL" else 0)
    if action == "HOLD":
        return 100 if real == "NEUTRAL" else 50
    return None


def read(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def score_freeze(path: Path, now: datetime) -> int:
    freeze = read(path)
    if not freeze or freeze.get("artifact_type") != "DAILY_COMPASS_FREEZE":
        return 0
    as_of = parse_iso(freeze["as_of_utc"])
    start = freeze.get("market_state", {}).get("market", {})
    start_btc = start.get("btc_usd")
    start_eth = start.get("eth_usd")
    start_eb = start.get("ethbtc")
    if not all(isinstance(x, (int, float)) for x in [start_btc, start_eth, start_eb]):
        return 0

    mapping = {
        "H12": freeze.get("horizons", {}).get("H12", {}),
        "H72": freeze.get("horizons", {}).get("D1_3", {}),
        "H168": freeze.get("horizons", {}).get("D5_7", {})
    }
    made = 0
    for label, hours in HORIZONS.items():
        maturity = as_of + timedelta(hours=hours)
        if now < maturity:
            continue
        out_dir = COMPASS_ROOT / "outcomes" / f"{as_of.year:04d}" / f"{as_of.month:02d}"
        out = out_dir / f"{freeze['freeze_id']}__{label}.json"
        if out.exists():
            continue
        end_btc = price_at("BTCUSDT", maturity)
        end_eth = price_at("ETHUSDT", maturity)
        end_eb = price_at("ETHBTC", maturity)
        btc_ret = pct(float(start_btc), end_btc)
        eth_ret = pct(float(start_eth), end_eth)
        eb_ret = pct(float(start_eb), end_eb)
        if btc_ret is None or eth_ret is None:
            continue
        proxy = round((btc_ret + eth_ret) / 2.0, 4)
        real = realized_direction(proxy)
        pred = mapping[label].get("direction")
        action = mapping[label].get("action")
        payload = {
            "schema_version": "ACTION_COMPASS_OUTCOME_V1",
            "freeze_id": freeze["freeze_id"],
            "freeze_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "horizon": label,
            "issued_at_utc": freeze["as_of_utc"],
            "maturity_at_utc": iso(maturity),
            "scored_at_utc": iso(now),
            "prediction": {"direction": pred, "action": action},
            "realized": {
                "btc_return_pct": btc_ret,
                "eth_return_pct": eth_ret,
                "ethbtc_return_pct": eb_ret,
                "market_return_proxy_pct": proxy,
                "direction": real,
                "btc_price": end_btc,
                "eth_price": end_eth,
                "ethbtc": end_eb
            },
            "score": {
                "direction_score": direction_score(pred, real) if pred else None,
                "action_utility_score": action_score(action, real) if action else None,
                "ladder_segment_score": None,
                "ladder_segment_score_reason": "Segment-level outcomes are not inferred from BTC/ETH proxies; requires eligible cap-segment evidence."
            },
            "authority": "LEARNING_ONLY",
            "immutable": True
        }
        out_dir.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Scored {freeze['freeze_id']} {label}: {real}, direction={payload['score']['direction_score']}")
        made += 1
    return made


def main() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    total = 0
    for path in sorted((COMPASS_ROOT / "daily").glob("*/*/*__DAILY_COMPASS.json")):
        total += score_freeze(path, now)
    print(f"Outcome scorer complete: {total} new record(s)")


if __name__ == "__main__":
    main()
