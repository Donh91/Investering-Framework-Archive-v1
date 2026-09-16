from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

import scripts.api_agent.alpha_arc_direct_new_pair as arc

RPC_DEFAULT = "https://rpc.arc-scan.org"
ARCSCAN_API = "https://api.arc-scan.org"
GECKO_API = "https://api.geckoterminal.com/api/v2"
BEANCAT_CA = "0x41c8a71f630c636294009fa4fb0cc4c3bbe674fe"
BEANCAT_POOL = "0x1f7f6a5e2ba06e9b3644afa8db8e1c606b5a5abb"
# Independent Arcscan evidence places BEANCAT transfers at block 16,940,530.
# Search backwards from that immutable anchor in small RPC-only chunks. This
# avoids broad third-party index scans while still locating PoolCreated.
BEANCAT_ANCHOR_BLOCK = 16_940_530
BEANCAT_LOOKBACK = 50_000
RPC_CHUNK = 2_500
RECENT_SPAN = 5_000


def get_json(url: str, timeout: int = 12, attempts: int = 3) -> Any:
    last_error: Exception | None = None
    for attempt in range(attempts):
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Investering-Framework-Arc-Replay/1.3", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return json.loads(response.read())
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in {429, 502, 503, 504}:
                raise
            if attempt == attempts - 1:
                raise
            time.sleep(min(0.5 * (2**attempt), 2.0))
    raise RuntimeError(f"HTTP_RETRY_EXHAUSTED:{last_error}")


def contains_all(payload: Any, values: list[str]) -> bool:
    text = json.dumps(payload, sort_keys=True).lower()
    return all(value.lower() in text for value in values)


def retrying_rpc_call(
    rpc_url: str,
    method: str,
    params: list[Any],
    *,
    timeout: int = 12,
    attempts: int = 3,
) -> Any:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return arc._replay_base_rpc_call(rpc_url, method, params, timeout=timeout)  # type: ignore[attr-defined]
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 502, 503, 504} or attempt == attempts - 1:
                raise
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            try:
                delay = max(float(retry_after), 0.25) if retry_after else min(0.5 * (2**attempt), 2.0)
            except ValueError:
                delay = min(0.5 * (2**attempt), 2.0)
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt == attempts - 1:
                raise
            time.sleep(min(0.5 * (2**attempt), 2.0))
    raise RuntimeError(f"RPC_RETRY_EXHAUSTED:{method}:{last_error}")


def raw_rpc_logs(rpc_url: str, venue: str, from_block: int, to_block: int) -> list[dict[str, Any]]:
    meta = arc.VENUES[venue]
    rows = retrying_rpc_call(
        rpc_url,
        "eth_getLogs",
        [{
            "fromBlock": hex(from_block),
            "toBlock": hex(to_block),
            "address": meta["emitter"],
            "topics": [meta["topic0"]],
        }],
    ) or []
    if not isinstance(rows, list):
        raise RuntimeError(f"RPC_LOG_RESULT_NOT_LIST:{venue}")
    return [row for row in rows if isinstance(row, dict)]


def parse_rpc_rows(rpc_url: str, venue: str, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    observed = int(time.time())
    output: list[dict[str, Any]] = []
    for raw in rows:
        parsed = arc.parse_log(venue, raw, None, observed, arc.rpc_label(rpc_url))
        if parsed:
            output.append(parsed)
    return output


def indexed_exact_block(venue: str, block: int) -> list[dict[str, Any]]:
    meta = arc.VENUES[venue]
    query = urllib.parse.urlencode({
        "module": "logs",
        "action": "getLogs",
        "fromBlock": block,
        "toBlock": block,
        "address": meta["emitter"],
        "topic0": meta["topic0"],
    })
    payload = get_json(f"{ARCSCAN_API}/api?{query}")
    rows = payload.get("result") if isinstance(payload, dict) else None
    return rows if isinstance(rows, list) else []


def index_match(event: dict[str, Any]) -> dict[str, Any]:
    venue = str(event["venue"])
    block = event.get("block_number")
    if not isinstance(block, int):
        raise RuntimeError("RPC_EVENT_MISSING_BLOCK")
    matches: list[dict[str, Any]] = []
    for raw in indexed_exact_block(venue, block):
        parsed = arc.parse_log(venue, raw, None, int(time.time()), "api.arc-scan.org")
        if parsed and parsed.get("transaction_hash") == event.get("transaction_hash") and parsed.get("log_index") == event.get("log_index"):
            matches.append(parsed)
    if len(matches) != 1:
        raise RuntimeError(f"INDEX_EXACT_MATCH_COUNT:{len(matches)}")
    return matches[0]


def find_beancat_rpc_control(rpc_url: str) -> tuple[dict[str, Any], tuple[int, int]]:
    floor = max(0, BEANCAT_ANCHOR_BLOCK - BEANCAT_LOOKBACK)
    end = BEANCAT_ANCHOR_BLOCK
    while end >= floor:
        start = max(floor, end - RPC_CHUNK + 1)
        events = parse_rpc_rows(rpc_url, "uniswap_v3", raw_rpc_logs(rpc_url, "uniswap_v3", start, end))
        matches = [
            row for row in events
            if str(row.get("target_token_ca") or "").lower() == BEANCAT_CA
            and str(row.get("pool_address") or "").lower() == BEANCAT_POOL
        ]
        if len(matches) == 1:
            return matches[0], (start, end)
        if len(matches) > 1:
            raise RuntimeError(f"BEANCAT_RPC_CONTROL_MATCH_COUNT:{len(matches)}")
        end = start - 1
    raise RuntimeError(f"BEANCAT_RPC_CONTROL_MATCH_COUNT:0:RANGE:{floor}-{BEANCAT_ANCHOR_BLOCK}")


def find_recent_rpc_control(rpc_url: str, head: int) -> tuple[dict[str, Any], tuple[int, int]]:
    start = max(0, head - RECENT_SPAN)
    candidates: list[dict[str, Any]] = []
    for venue in ("uniswap_v3", "uniswap_v2", "uniswap_v4"):
        events = parse_rpc_rows(rpc_url, venue, raw_rpc_logs(rpc_url, venue, start, head))
        candidates.extend(row for row in events if row.get("candidate_status") == "USDC_ANCHORED_CANDIDATE")
    if not candidates:
        raise RuntimeError("NO_RECENT_RPC_USDC_CONTROL")
    candidates.sort(key=lambda row: (row.get("block_number") or -1, row.get("log_index") or -1), reverse=True)
    preferred = [row for row in candidates if row.get("pool_address")]
    return (preferred or candidates)[0], (start, head)


def parity(a: dict[str, Any], b: dict[str, Any]) -> dict[str, bool]:
    comparable = [
        "venue", "emitter", "block_number", "transaction_hash", "log_index",
        "target_token_ca", "quote_asset", "quote_representation", "pool_address",
        "pool_id", "fee", "tick_spacing",
    ]
    return {key: a.get(key) == b.get(key) for key in comparable}


def assert_parity(label: str, left: dict[str, Any], right: dict[str, Any]) -> dict[str, bool]:
    result = parity(left, right)
    if not all(result.values()):
        raise RuntimeError(label + ":" + ",".join(key for key, value in result.items() if not value))
    return result


def run_replay(rpc_url: str) -> dict[str, Any]:
    if not hasattr(arc, "_replay_base_rpc_call"):
        arc._replay_base_rpc_call = arc.rpc_call  # type: ignore[attr-defined]
    arc.rpc_call = retrying_rpc_call

    chain_id_hex = retrying_rpc_call(rpc_url, "eth_chainId", [])
    chain_id = int(chain_id_hex, 16) if isinstance(chain_id_hex, str) else None
    if chain_id != arc.CHAIN_ID:
        raise RuntimeError(f"WRONG_CHAIN:{chain_id}")

    beancat_rpc, beancat_range = find_beancat_rpc_control(rpc_url)
    beancat_index = index_match(beancat_rpc)
    beancat_parity = assert_parity("BEANCAT_RPC_INDEX_PARITY_FAILED", beancat_rpc, beancat_index)

    gecko_beancat = get_json(f"{GECKO_API}/networks/arc/pools/{BEANCAT_POOL}")
    if not contains_all(gecko_beancat, [BEANCAT_POOL, BEANCAT_CA, arc.USDC_ERC20]):
        raise RuntimeError("BEANCAT_GECKO_IDENTITY_FAILED")

    head_hex = retrying_rpc_call(rpc_url, "eth_blockNumber", [])
    head = int(head_hex, 16)
    recent_rpc, recent_range = find_recent_rpc_control(rpc_url, head)
    recent_index = index_match(recent_rpc)
    recent_parity = assert_parity("RECENT_RPC_INDEX_PARITY_FAILED", recent_rpc, recent_index)

    gecko_recent = None
    if recent_rpc.get("pool_address"):
        try:
            gecko = get_json(f"{GECKO_API}/networks/arc/pools/{recent_rpc['pool_address']}")
            gecko_recent = contains_all(gecko, [recent_rpc["pool_address"], recent_rpc["target_token_ca"], arc.USDC_ERC20])
        except Exception:
            gecko_recent = None

    assertions = {
        "chain_id_5042": chain_id == arc.CHAIN_ID,
        "historical_beancat_rpc_index_parity": all(beancat_parity.values()),
        "historical_beancat_gecko_identity": True,
        "recent_rpc_index_parity": all(recent_parity.values()),
        "market_cap_not_inferred": recent_rpc.get("market_cap_usd") is None,
        "fdv_not_inferred": recent_rpc.get("fdv_usd") is None,
        "new_pool_not_equated_to_new_token": recent_rpc.get("new_pool_is_new_token") is False,
        "shadow_only": recent_rpc.get("status") == "SHADOW_ONLY",
        "data_integrity_pass": recent_rpc.get("data_integrity_status") == "PASS",
    }
    if not all(assertions.values()):
        raise RuntimeError("ASSERTION_FAILED:" + ",".join(key for key, value in assertions.items() if not value))

    return {
        "contract": "ALPHA_ARC_HISTORICAL_RPC_REPLAY_GATE_v5",
        "status": "PASS",
        "authority": {
            "shadow_activation_eligible": True,
            "user_alert": False,
            "adaptive_learning": False,
            "automatic_trading": False,
        },
        "chain_id": chain_id,
        "rpc_source": arc.rpc_label(rpc_url),
        "historical_beancat_rpc": {
            "rpc_search_range": {"from_block": beancat_range[0], "to_block": beancat_range[1]},
            "rpc_event": beancat_rpc,
            "indexed_event": beancat_index,
            "parity": beancat_parity,
        },
        "recent_replay": {
            "head": head,
            "range": {"from_block": recent_range[0], "to_block": recent_range[1]},
            "rpc_event": recent_rpc,
            "indexed_event": recent_index,
            "parity": recent_parity,
        },
        "independent_readback": {
            "arcscan_index_vs_rpc_historical": True,
            "geckoterminal_beancat_identity": True,
            "arcscan_index_vs_rpc_recent": True,
            "geckoterminal_recent_pool_identity": gecko_recent,
        },
        "assertions": assertions,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rpc-url", default=RPC_DEFAULT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_replay(args.rpc_url)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "contract": result["contract"],
        "status": result["status"],
        "historical_block": result["historical_beancat_rpc"]["rpc_event"]["block_number"],
        "recent_block": result["recent_replay"]["rpc_event"]["block_number"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
