from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

GECKO_BASE = "https://api.geckoterminal.com/api/v2"
GECKO_ACCEPT = "application/json;version=20230203"
STABLE_OR_WRAPPED = {
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "0x6b175474e89094c44da98b954eedeac495271d0f",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def number(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def integer(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def parse_time(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    if not isinstance(value, str) or not value:
        return 0
    try:
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return 0


def token_address(token_id: Any) -> str | None:
    if not isinstance(token_id, str):
        return None
    tail = token_id.split("_", 1)[-1].lower()
    return tail if tail.startswith("0x") and len(tail) == 42 else None


def included_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in payload.get("included", []) if isinstance(item, dict) and isinstance(item.get("id"), str)}


def choose_target(resource: dict[str, Any], included: dict[str, dict[str, Any]]) -> tuple[str | None, str | None, str | None, str | None]:
    rel = resource.get("relationships") if isinstance(resource.get("relationships"), dict) else {}
    rows: list[tuple[str, str, dict[str, Any]]] = []
    for role in ("base", "quote"):
        key = role + "_token"
        data = rel.get(key, {}).get("data") if isinstance(rel.get(key), dict) else None
        token_id = data.get("id") if isinstance(data, dict) else None
        address = token_address(token_id)
        if address:
            rows.append((address, role, included.get(token_id, {})))
    preferred = [row for row in rows if row[0] not in STABLE_OR_WRAPPED]
    # Conservative scope: base is preferred when both assets are non-anchor. Quote is selected when base is an anchor.
    selected = preferred[0] if preferred else (rows[0] if rows else None)
    if selected is None:
        return None, None, None, None
    address, role, meta = selected
    attrs = meta.get("attributes") if isinstance(meta.get("attributes"), dict) else {}
    return address, role, str(attrs.get("symbol") or "") or None, str(attrs.get("name") or "") or None


def normalize_pool(resource: dict[str, Any], included: dict[str, dict[str, Any]], *, now_unix: int | None = None) -> dict[str, Any] | None:
    attrs = resource.get("attributes") if isinstance(resource.get("attributes"), dict) else {}
    token_ca, role, symbol, name = choose_target(resource, included)
    if not token_ca or role not in {"base", "quote"}:
        return None
    now = int(now_unix or time.time())
    created = parse_time(attrs.get("pool_created_at"))
    age_minutes = max(0.1, (now - created) / 60.0) if created else 999999.0
    txns = attrs.get("transactions") if isinstance(attrs.get("transactions"), dict) else {}
    volumes = attrs.get("volume_usd") if isinstance(attrs.get("volume_usd"), dict) else {}
    changes = attrs.get("price_change_percentage") if isinstance(attrs.get("price_change_percentage"), dict) else {}
    h1 = txns.get("h1") if isinstance(txns.get("h1"), dict) else {}
    m5 = txns.get("m5") if isinstance(txns.get("m5"), dict) else {}
    base_buys_h1, base_sells_h1 = integer(h1.get("buys")), integer(h1.get("sells"))
    base_buys_m5, base_sells_m5 = integer(m5.get("buys")), integer(m5.get("sells"))
    if role == "base":
        buys_h1, sells_h1 = base_buys_h1, base_sells_h1
        buys_m5, sells_m5 = base_buys_m5, base_sells_m5
        price_h1, price_h6 = number(changes.get("h1")), number(changes.get("h6"))
        price_change_resolved = True
        market_cap = number(attrs.get("market_cap_usd")) or number(attrs.get("fdv_usd"))
        fdv = number(attrs.get("fdv_usd"))
        price_usd = number(attrs.get("base_token_price_usd"))
    else:
        # A base-token buy is economically a quote-token sell and vice versa.
        buys_h1, sells_h1 = base_sells_h1, base_buys_h1
        buys_m5, sells_m5 = base_sells_m5, base_buys_m5
        # Gecko pool price-change fields are base-token oriented. We do not fabricate quote-token USD changes by inversion.
        price_h1, price_h6 = None, None
        price_change_resolved = False
        # Pool-level fdv/market-cap fields refer to the base asset, so never misattribute them to a quote target.
        market_cap = 0.0
        fdv = 0.0
        price_usd = number(attrs.get("quote_token_price_usd"))
    liq = number(attrs.get("reserve_in_usd"))
    vol_h1, vol_m5 = number(volumes.get("h1")), number(volumes.get("m5"))
    denom_age = max(1.0, min(age_minutes, 60.0))
    return {
        "contract": "MOONSHOT_STAGE0_EVENT_v2",
        "network": "eth",
        "pool_id": resource.get("id"),
        "pool_address": str(attrs.get("address") or resource.get("id") or ""),
        "dex_id": (resource.get("relationships", {}).get("dex", {}).get("data", {}) or {}).get("id"),
        "token_ca": token_ca,
        "token_role": role,
        "token_price_usd": price_usd,
        "target_price_change_resolved": price_change_resolved,
        "symbol": symbol,
        "name": name,
        "pool_created_at": attrs.get("pool_created_at"),
        "observed_at_unix": now,
        "age_minutes": round(age_minutes, 3),
        "liquidity_usd": liq,
        "market_cap_usd": market_cap,
        "fdv_usd": fdv,
        "volume_m5_usd": vol_m5,
        "volume_h1_usd": vol_h1,
        "buys_m5": buys_m5,
        "sells_m5": sells_m5,
        "buys_h1": buys_h1,
        "sells_h1": sells_h1,
        "buyer_velocity_per_minute": buys_h1 / denom_age,
        "transaction_velocity_per_minute": (buys_h1 + sells_h1) / denom_age,
        "volume_to_liquidity_h1": vol_h1 / liq if liq > 0 else 0.0,
        "liquidity_to_market_cap_pct": (100.0 * liq / market_cap) if market_cap > 0 else None,
        "price_change_h1_pct": price_h1,
        "price_change_h6_pct": price_h6,
        "raw_sha256": hashlib.sha256(canonical_bytes(resource)).hexdigest(),
    }


def fetch_new_pools(network: str, pages: int, *, timeout: int = 20) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for page in range(1, max(1, pages) + 1):
        url = f"{GECKO_BASE}/networks/{urllib.parse.quote(network)}/new_pools?page={page}&include=base_token,quote_token,dex"
        req = urllib.request.Request(url, headers={"Accept": GECKO_ACCEPT, "User-Agent": "Investering-Framework-Moonshot-Sentinel/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read())
        included = included_map(payload)
        for resource in payload.get("data", []):
            if not isinstance(resource, dict):
                continue
            event = normalize_pool(resource, included)
            if not event:
                continue
            key = f"{event['network']}:{event['token_ca']}:{event['pool_address']}"
            if key not in seen:
                seen.add(key)
                output.append(event)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Target-token-aware Moonshot Stage0 GeckoTerminal scanner.")
    parser.add_argument("--network", default="eth")
    parser.add_argument("--pages", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = {
        "contract": "MOONSHOT_SCAN_BATCH_v2",
        "created_unix": int(time.time()),
        "events": fetch_new_pools(args.network, args.pages),
        "target_token_price_captured": True,
        "base_quote_semantics_normalized": True,
        "quote_price_change_fails_closed": True,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(payload))
    print(json.dumps({"events": len(payload["events"]), "contract": payload["contract"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
