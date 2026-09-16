from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHAIN = "arc"
CHAIN_ID = 5042
ZERO = "0x0000000000000000000000000000000000000000"
USDC_ERC20 = "0x3600000000000000000000000000000000000000"

VENUES = {
    "uniswap_v2": {
        "emitter": "0x89e5db8b5aa49aa85ac63f691524311aeb649eba",
        "topic0": "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9",
    },
    "uniswap_v3": {
        "emitter": "0xf0db7b58379503491d857db50ac9ece64c653918",
        "topic0": "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118",
    },
    "uniswap_v4": {
        "emitter": "0x8366a39cc670b4001a1121b8f6a443a643e40951",
        "topic0": "0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438",
    },
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def hex_int(value: str | None) -> int | None:
    if not isinstance(value, str) or not value.startswith("0x"):
        return None
    try:
        return int(value, 16)
    except ValueError:
        return None


def word(data: str, index: int) -> str | None:
    if not isinstance(data, str) or not data.startswith("0x"):
        return None
    body = data[2:]
    start = index * 64
    end = start + 64
    if len(body) < end:
        return None
    return body[start:end]


def address_from_word(value: str | None) -> str | None:
    if not isinstance(value, str) or len(value) != 64:
        return None
    tail = value[-40:].lower()
    if any(ch not in "0123456789abcdef" for ch in tail):
        return None
    return "0x" + tail


def address_from_topic(value: str | None) -> str | None:
    if not isinstance(value, str) or not value.startswith("0x"):
        return None
    return address_from_word(value[2:].rjust(64, "0")[-64:])


def signed_int(word_hex: str | None, bits: int) -> int | None:
    if not isinstance(word_hex, str) or len(word_hex) != 64:
        return None
    value = int(word_hex, 16) & ((1 << bits) - 1)
    if value >= 1 << (bits - 1):
        value -= 1 << bits
    return value


def quote_semantics(a: str | None, b: str | None) -> tuple[str | None, str | None, str]:
    a = a.lower() if isinstance(a, str) else None
    b = b.lower() if isinstance(b, str) else None
    anchors = {USDC_ERC20: "USDC_ERC20_6", ZERO: "NATIVE_USDC_18"}
    a_anchor, b_anchor = anchors.get(a), anchors.get(b)
    if bool(a_anchor) == bool(b_anchor):
        return None, None, "AMBIGUOUS_OR_NON_USDC_ANCHORED"
    if a_anchor:
        return a, b, a_anchor
    return b, a, b_anchor or "UNKNOWN"


def rpc_label(rpc_url: str) -> str:
    """Return non-secret provenance. Never persist RPC paths, query strings or credentials."""
    parsed = urllib.parse.urlparse(rpc_url)
    return parsed.hostname or "configured_arc_rpc"


def rpc_call(rpc_url: str, method: str, params: list[Any], *, timeout: int = 20, attempts: int = 4) -> Any:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last_error: Exception | None = None
    for attempt in range(attempts):
        req = urllib.request.Request(rpc_url, data=body, headers={"Content-Type": "application/json", "User-Agent": "Investering-Framework-Arc-Shadow/1.1"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = json.loads(response.read())
            if payload.get("error"):
                raise RuntimeError(f"RPC_ERROR:{method}:{payload['error']}")
            return payload.get("result")
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 502, 503, 504} or attempt == attempts - 1:
                raise
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            try:
                delay = max(float(retry_after), 0.5) if retry_after else min(0.75 * (2**attempt), 4.0)
            except ValueError:
                delay = min(0.75 * (2**attempt), 4.0)
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt == attempts - 1:
                raise
            time.sleep(min(0.75 * (2**attempt), 4.0))
    raise RuntimeError(f"RPC_RETRY_EXHAUSTED:{method}:{last_error}")


def parse_log(venue: str, log: dict[str, Any], block_timestamp: int | None, observed_at: int, rpc_source: str) -> dict[str, Any] | None:
    topics = log.get("topics") if isinstance(log.get("topics"), list) else []
    data = str(log.get("data") or "0x")
    emitter = str(log.get("address") or "").lower()
    expected = VENUES[venue]
    if emitter != expected["emitter"] or not topics or str(topics[0]).lower() != expected["topic0"]:
        return None

    token0 = token1 = pool_address = pool_id = None
    fee = tick_spacing = None
    hooks = None
    if venue == "uniswap_v2":
        if len(topics) < 3:
            return None
        token0 = address_from_topic(topics[1])
        token1 = address_from_topic(topics[2])
        pool_address = address_from_word(word(data, 0))
    elif venue == "uniswap_v3":
        if len(topics) < 4:
            return None
        token0 = address_from_topic(topics[1])
        token1 = address_from_topic(topics[2])
        fee = hex_int(str(topics[3]))
        tick_spacing = signed_int(word(data, 0), 24)
        pool_address = address_from_word(word(data, 1))
    else:
        if len(topics) < 4:
            return None
        pool_id = str(topics[1]).lower()
        token0 = address_from_topic(topics[2])
        token1 = address_from_topic(topics[3])
        fee_word = word(data, 0)
        fee = int(fee_word, 16) & ((1 << 24) - 1) if fee_word else None
        tick_spacing = signed_int(word(data, 1), 24)
        hooks = address_from_word(word(data, 2))

    quote_asset, target_token, quote_representation = quote_semantics(token0, token1)
    block_number = hex_int(log.get("blockNumber"))
    return {
        "contract": "ALPHA_ARC_DIRECT_NEW_PAIR_EVENT_v1",
        "status": "SHADOW_ONLY",
        "chain": CHAIN,
        "chain_id": CHAIN_ID,
        "venue": venue,
        "emitter": emitter,
        "block_number": block_number,
        "block_hash": log.get("blockHash"),
        "block_timestamp": block_timestamp,
        "block_timestamp_utc": datetime.fromtimestamp(block_timestamp, tz=timezone.utc).isoformat().replace("+00:00", "Z") if block_timestamp else None,
        "transaction_hash": log.get("transactionHash"),
        "transaction_index": hex_int(log.get("transactionIndex")),
        "log_index": hex_int(log.get("logIndex")),
        "token0_or_currency0": token0,
        "token1_or_currency1": token1,
        "quote_asset": quote_asset,
        "quote_representation": quote_representation,
        "target_token_ca": target_token,
        "candidate_status": "USDC_ANCHORED_CANDIDATE" if target_token else "AMBIGUOUS_OR_NON_USDC_ANCHORED",
        "pool_address": pool_address,
        "pool_id": pool_id,
        "fee": fee,
        "tick_spacing": tick_spacing,
        "hooks": hooks,
        "observed_at_unix": observed_at,
        "observed_at_utc": datetime.fromtimestamp(observed_at, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "rpc_source": rpc_source,
        "new_pool_is_new_token": False,
        "market_cap_usd": None,
        "fdv_usd": None,
        "data_integrity_status": "PASS" if token0 and token1 and (pool_address or pool_id) else "DEGRADED_DATA",
    }


def scan_range(rpc_url: str, from_block: int, to_block: int, *, timeout: int = 20) -> list[dict[str, Any]]:
    observed_at = int(time.time())
    source_label = rpc_label(rpc_url)
    raw_logs: list[tuple[str, dict[str, Any]]] = []
    for venue, meta in VENUES.items():
        params = [{
            "fromBlock": hex(from_block),
            "toBlock": hex(to_block),
            "address": meta["emitter"],
            "topics": [meta["topic0"]],
        }]
        rows = rpc_call(rpc_url, "eth_getLogs", params, timeout=timeout) or []
        if not isinstance(rows, list):
            raise RuntimeError(f"RPC_LOG_RESULT_NOT_LIST:{venue}")
        raw_logs.extend((venue, row) for row in rows if isinstance(row, dict))

    # Timestamps enrich evidence but are not identity-critical. A transient
    # block-read failure must not erase a valid PoolCreated event already read
    # from eth_getLogs; preserve the event with a null timestamp instead.
    timestamps: dict[int, int | None] = {}
    for _, row in raw_logs:
        block_number = hex_int(row.get("blockNumber"))
        if block_number is None or block_number in timestamps:
            continue
        try:
            block = rpc_call(rpc_url, "eth_getBlockByNumber", [hex(block_number), False], timeout=timeout)
            timestamps[block_number] = hex_int(block.get("timestamp")) if isinstance(block, dict) else None
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
            timestamps[block_number] = None

    output: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for venue, row in raw_logs:
        block_number = hex_int(row.get("blockNumber"))
        event = parse_log(venue, row, timestamps.get(block_number) if block_number is not None else None, observed_at, source_label)
        if not event:
            continue
        key = (event["venue"], event["transaction_hash"], event["log_index"])
        if key in seen:
            continue
        seen.add(key)
        output.append(event)
    return sorted(output, key=lambda row: (row.get("block_number") or -1, row.get("log_index") or -1, row["venue"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="Shadow-only Arc direct Uniswap V2/V3/V4 new-pool event adapter.")
    parser.add_argument("--rpc-url", default=os.environ.get("ARC_RPC_URL"))
    parser.add_argument("--from-block", type=int, required=True)
    parser.add_argument("--to-block", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.rpc_url:
        raise SystemExit("ARC_RPC_URL_OR_--rpc-url_REQUIRED")
    if args.from_block < 0 or args.to_block < args.from_block:
        raise SystemExit("INVALID_BLOCK_RANGE")
    events = scan_range(args.rpc_url, args.from_block, args.to_block)
    payload = {
        "contract": "ALPHA_ARC_DIRECT_NEW_PAIR_BATCH_v1",
        "status": "SHADOW_ONLY",
        "chain": CHAIN,
        "chain_id": CHAIN_ID,
        "from_block": args.from_block,
        "to_block": args.to_block,
        "event_count": len(events),
        "usdc_anchored_candidate_count": sum(1 for row in events if row["candidate_status"] == "USDC_ANCHORED_CANDIDATE"),
        "events": events,
        "authority": {"user_alert": False, "adaptive_learning": False, "automatic_trading": False},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(payload))
    print(json.dumps({"contract": payload["contract"], "events": len(events), "candidates": payload["usdc_anchored_candidate_count"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
