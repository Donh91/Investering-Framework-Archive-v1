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
# BEANCAT transfers are independently visible around block 16,940,530. Keep
# discovery bounded, but do not assume the pool-creation block is in one stale
# hand-picked range. Arcscan is used only to locate the immutable event; the
# gate itself replays the exact event from JSON-RPC.
BEANCAT_FROM = 16_850_000
BEANCAT_TO = 17_000_000
INDEX_CHUNK = 10_000
RECENT_SPAN = 20_000


def get_json(url: str, timeout: int = 15) -> Any:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Investering-Framework-Arc-Replay/1.2", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read())


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


def indexed_logs(venue: str, from_block: int, to_block: int) -> list[dict[str, Any]]:
    meta = arc.VENUES[venue]
    query = urllib.parse.urlencode(
        {
            "module": "logs",
            "action": "getLogs",
            "fromBlock": from_block,
            "toBlock": to_block,
            "address": meta["emitter"],
            "topic0": meta["topic0"],
        }
    )
    payload = get_json(f"{ARCSCAN_API}/api?{query}")
    rows = payload.get("result") if isinstance(payload, dict) else None
    return rows if isinstance(rows, list) else []


def parse_indexed(venue: str, raw: dict[str, Any]) -> dict[str, Any] | None:
    return arc.parse_log(venue, raw, None, int(time.time()), "api.arc-scan.org")


def exact_rpc_event(rpc_url: str, venue: str, indexed_event: dict[str, Any]) -> dict[str, Any]:
    block = indexed_event.get("block_number")
    if not isinstance(block, int):
        raise RuntimeError("INDEX_EVENT_MISSING_BLOCK")
    meta = arc.VENUES[venue]
    params = [{
        "fromBlock": hex(block),
        "toBlock": hex(block),
        "address": meta["emitter"],
        "topics": [meta["topic0"]],
    }]
    rows = retrying_rpc_call(rpc_url, "eth_getLogs", params) or []
    if not isinstance(rows, list):
        raise RuntimeError("EXACT_RPC_LOG_RESULT_NOT_LIST")
    matches: list[dict[str, Any]] = []
    for raw in rows:
        if not isinstance(raw, dict):
            continue
        parsed = arc.parse_log(venue, raw, None, int(time.time()), arc.rpc_label(rpc_url))
        if parsed and parsed.get("transaction_hash") == indexed_event.get("transaction_hash") and parsed.get("log_index") == indexed_event.get("log_index"):
            matches.append(parsed)
    if len(matches) != 1:
        raise RuntimeError(f"EXACT_RPC_MATCH_COUNT:{len(matches)}")
    return matches[0]


def find_beancat_index_control() -> tuple[dict[str, Any], tuple[int, int]]:
    matches: list[dict[str, Any]] = []
    scanned_from = BEANCAT_FROM
    scanned_to = BEANCAT_TO
    for start in range(BEANCAT_FROM, BEANCAT_TO + 1, INDEX_CHUNK):
        end = min(start + INDEX_CHUNK - 1, BEANCAT_TO)
        for raw in indexed_logs("uniswap_v3", start, end):
            parsed = parse_indexed("uniswap_v3", raw)
            if not parsed:
                continue
            if str(parsed.get("target_token_ca") or "").lower() == BEANCAT_CA and str(parsed.get("pool_address") or "").lower() == BEANCAT_POOL:
                matches.append(parsed)
    unique = {(row.get("transaction_hash"), row.get("log_index")): row for row in matches}
    if len(unique) != 1:
        raise RuntimeError(f"BEANCAT_INDEX_CONTROL_MATCH_COUNT:{len(unique)}:RANGE:{scanned_from}-{scanned_to}")
    return next(iter(unique.values())), (scanned_from, scanned_to)


def find_recent_index_control(head: int) -> tuple[dict[str, Any], tuple[int, int]]:
    start = max(0, head - RECENT_SPAN)
    candidates: list[dict[str, Any]] = []
    for venue in ("uniswap_v3", "uniswap_v2", "uniswap_v4"):
        for raw in indexed_logs(venue, start, head):
            parsed = parse_indexed(venue, raw)
            if parsed and parsed.get("candidate_status") == "USDC_ANCHORED_CANDIDATE":
                candidates.append(parsed)
    if not candidates:
        raise RuntimeError("NO_RECENT_INDEXED_USDC_CONTROL")
    candidates.sort(key=lambda row: (row.get("block_number") or -1, row.get("log_index") or -1), reverse=True)
    preferred = [row for row in candidates if row.get("pool_address")]
    return (preferred or candidates)[0], (start, head)


def parity(indexed_event: dict[str, Any], rpc_event: dict[str, Any]) -> dict[str, bool]:
    comparable = [
        "venue", "emitter", "block_number", "transaction_hash", "log_index",
        "target_token_ca", "quote_asset", "quote_representation", "pool_address",
        "pool_id", "fee", "tick_spacing",
    ]
    return {key: indexed_event.get(key) == rpc_event.get(key) for key in comparable}


def run_replay(rpc_url: str) -> dict[str, Any]:
    if not hasattr(arc, "_replay_base_rpc_call"):
        arc._replay_base_rpc_call = arc.rpc_call  # type: ignore[attr-defined]
    arc.rpc_call = retrying_rpc_call

    chain_id_hex = retrying_rpc_call(rpc_url, "eth_chainId", [])
    chain_id = int(chain_id_hex, 16) if isinstance(chain_id_hex, str) else None
    if chain_id != arc.CHAIN_ID:
        raise RuntimeError(f"WRONG_CHAIN:{chain_id}")

    beancat_index, beancat_range = find_beancat_index_control()
    beancat_rpc = exact_rpc_event(rpc_url, "uniswap_v3", beancat_index)
    beancat_parity = parity(beancat_index, beancat_rpc)
    if not all(beancat_parity.values()):
        raise RuntimeError("BEANCAT_INDEX_RPC_PARITY_FAILED:" + ",".join(key for key, value in beancat_parity.items() if not value))

    head_hex = retrying_rpc_call(rpc_url, "eth_blockNumber", [])
    head = int(head_hex, 16)
    recent_index, recent_range = find_recent_index_control(head)
    recent_rpc = exact_rpc_event(rpc_url, recent_index["venue"], recent_index)
    recent_parity = parity(recent_index, recent_rpc)
    if not all(recent_parity.values()):
        raise RuntimeError("RECENT_INDEX_RPC_PARITY_FAILED:" + ",".join(key for key, value in recent_parity.items() if not value))

    gecko_ok = None
    if recent_rpc.get("pool_address"):
        try:
            gecko = get_json(f"{GECKO_API}/networks/arc/pools/{recent_rpc['pool_address']}")
            gecko_ok = contains_all(gecko, [recent_rpc["pool_address"], recent_rpc["target_token_ca"], arc.USDC_ERC20])
        except Exception:
            gecko_ok = None

    assertions = {
        "chain_id_5042": chain_id == arc.CHAIN_ID,
        "historical_beancat_exact_rpc_replay": all(beancat_parity.values()),
        "recent_index_rpc_parity": all(recent_parity.values()),
        "market_cap_not_inferred": recent_rpc.get("market_cap_usd") is None,
        "fdv_not_inferred": recent_rpc.get("fdv_usd") is None,
        "new_pool_not_equated_to_new_token": recent_rpc.get("new_pool_is_new_token") is False,
        "shadow_only": recent_rpc.get("status") == "SHADOW_ONLY",
        "data_integrity_pass": recent_rpc.get("data_integrity_status") == "PASS",
    }
    if not all(assertions.values()):
        raise RuntimeError("ASSERTION_FAILED:" + ",".join(key for key, value in assertions.items() if not value))

    return {
        "contract": "ALPHA_ARC_HISTORICAL_RPC_REPLAY_GATE_v4",
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
            "index_search_range": {"from_block": beancat_range[0], "to_block": beancat_range[1]},
            "indexed_event": beancat_index,
            "rpc_event": beancat_rpc,
            "parity": beancat_parity,
        },
        "recent_replay": {
            "head": head,
            "range": {"from_block": recent_range[0], "to_block": recent_range[1]},
            "indexed_event": recent_index,
            "rpc_event": recent_rpc,
            "parity": recent_parity,
        },
        "independent_readback": {
            "arcscan_index_vs_rpc_historical": True,
            "arcscan_index_vs_rpc_recent": True,
            "geckoterminal_pool_identity": gecko_ok,
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
