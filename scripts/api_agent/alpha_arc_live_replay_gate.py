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
BEANCAT_FROM = 16_880_000
BEANCAT_TO = 16_920_000
RECENT_SPAN = 9_000
CHUNK = 3_000


def get_json(url: str, timeout: int = 20) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "Investering-Framework-Arc-Replay/1.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read())


def contains_all(payload: Any, values: list[str]) -> bool:
    text = json.dumps(payload, sort_keys=True).lower()
    return all(value.lower() in text for value in values)


def retrying_rpc_call(rpc_url: str, method: str, params: list[Any], *, timeout: int = 20, attempts: int = 5) -> Any:
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
                delay = max(float(retry_after), 0.5) if retry_after else min(0.5 * (2 ** attempt), 4.0)
            except ValueError:
                delay = min(0.5 * (2 ** attempt), 4.0)
            time.sleep(delay)
        except TimeoutError as exc:
            last_error = exc
            if attempt == attempts - 1:
                raise
            time.sleep(min(0.5 * (2 ** attempt), 4.0))
    raise RuntimeError(f"RPC_RETRY_EXHAUSTED:{method}:{last_error}")


def indexed_logs(venue: str, from_block: int, to_block: int) -> list[dict[str, Any]]:
    meta = arc.VENUES[venue]
    query = urllib.parse.urlencode({
        "module": "logs", "action": "getLogs", "fromBlock": from_block, "toBlock": to_block,
        "address": meta["emitter"], "topic0": meta["topic0"],
    })
    payload = get_json(f"{ARCSCAN_API}/api?{query}")
    rows = payload.get("result") if isinstance(payload, dict) else None
    return rows if isinstance(rows, list) else []


def find_recent_control(rpc_url: str, head: int) -> tuple[dict[str, Any], dict[str, Any], tuple[int, int]]:
    start = max(0, head - RECENT_SPAN)
    replay = arc.scan_range(rpc_url, start, head)
    candidates = [row for row in replay if row.get("candidate_status") == "USDC_ANCHORED_CANDIDATE"]
    if not candidates:
        raise RuntimeError("NO_RECENT_RPC_USDC_CONTROL")
    candidates.sort(key=lambda row: (row.get("block_number") or -1, row.get("log_index") or -1), reverse=True)
    preferred = [row for row in candidates if row.get("pool_address")]
    rpc_event = (preferred or candidates)[0]
    venue = rpc_event["venue"]
    block = rpc_event["block_number"]
    indexed = []
    for raw in indexed_logs(venue, block, block):
        parsed = arc.parse_log(venue, raw, None, int(time.time()), "api.arc-scan.org")
        if parsed and parsed.get("transaction_hash") == rpc_event.get("transaction_hash") and parsed.get("log_index") == rpc_event.get("log_index"):
            indexed.append(parsed)
    if len(indexed) != 1:
        raise RuntimeError(f"RECENT_INDEX_MATCH_COUNT:{len(indexed)}")
    return indexed[0], rpc_event, (start, head)


def run_replay(rpc_url: str) -> dict[str, Any]:
    if not hasattr(arc, "_replay_base_rpc_call"):
        arc._replay_base_rpc_call = arc.rpc_call  # type: ignore[attr-defined]
    arc.rpc_call = retrying_rpc_call
    chain_id_hex = retrying_rpc_call(rpc_url, "eth_chainId", [])
    chain_id = int(chain_id_hex, 16) if isinstance(chain_id_hex, str) else None
    if chain_id != arc.CHAIN_ID:
        raise RuntimeError(f"WRONG_CHAIN:{chain_id}")

    historical_status = "PASS"
    historical_match = None
    try:
        events: list[dict[str, Any]] = []
        for start in range(BEANCAT_FROM, BEANCAT_TO + 1, CHUNK):
            end = min(start + CHUNK - 1, BEANCAT_TO)
            events.extend(arc.scan_range(rpc_url, start, end))
        matches = [row for row in events if row.get("venue") == "uniswap_v3" and str(row.get("target_token_ca") or "").lower() == BEANCAT_CA and str(row.get("pool_address") or "").lower() == BEANCAT_POOL]
        if len(matches) != 1:
            raise RuntimeError(f"BEANCAT_CONTROL_MATCH_COUNT:{len(matches)}")
        historical_match = matches[0]
    except RuntimeError as exc:
        if "pruned history unavailable" not in str(exc):
            raise
        historical_status = "RPC_HISTORY_PRUNED"

    head_hex = retrying_rpc_call(rpc_url, "eth_blockNumber", [])
    head = int(head_hex, 16)
    indexed_event, rpc_event, recent_range = find_recent_control(rpc_url, head)
    comparable = ["venue", "emitter", "block_number", "transaction_hash", "log_index", "target_token_ca", "quote_asset", "quote_representation", "pool_address", "pool_id", "fee", "tick_spacing"]
    parity = {key: indexed_event.get(key) == rpc_event.get(key) for key in comparable}
    if not all(parity.values()):
        raise RuntimeError("INDEX_RPC_PARITY_FAILED:" + ",".join(k for k, v in parity.items() if not v))

    gecko_ok = None
    if rpc_event.get("pool_address"):
        try:
            gecko = get_json(f"{GECKO_API}/networks/arc/pools/{rpc_event['pool_address']}")
            gecko_ok = contains_all(gecko, [rpc_event["pool_address"], rpc_event["target_token_ca"], arc.USDC_ERC20])
        except Exception:
            gecko_ok = None

    assertions = {
        "chain_id_5042": chain_id == arc.CHAIN_ID,
        "recent_index_rpc_parity": all(parity.values()),
        "market_cap_not_inferred": rpc_event.get("market_cap_usd") is None,
        "fdv_not_inferred": rpc_event.get("fdv_usd") is None,
        "new_pool_not_equated_to_new_token": rpc_event.get("new_pool_is_new_token") is False,
        "shadow_only": rpc_event.get("status") == "SHADOW_ONLY",
        "data_integrity_pass": rpc_event.get("data_integrity_status") == "PASS",
    }
    if not all(assertions.values()):
        raise RuntimeError("ASSERTION_FAILED:" + ",".join(k for k, v in assertions.items() if not v))

    return {
        "contract": "ALPHA_ARC_HISTORICAL_RPC_REPLAY_GATE_v2",
        "status": "PASS_WITH_PRUNED_HISTORICAL_CONTROL" if historical_status != "PASS" else "PASS",
        "authority": {"shadow_activation_eligible": True, "user_alert": False, "adaptive_learning": False, "automatic_trading": False},
        "chain_id": chain_id,
        "rpc_source": "rpc.arc-scan.org",
        "historical_beancat_rpc": {"status": historical_status, "matched_event": historical_match, "reason_if_pruned": "public RPC no longer retains the BEANCAT block range; no empty-result inference is permitted"},
        "recent_replay": {"head": head, "range": {"from_block": recent_range[0], "to_block": recent_range[1]}, "indexed_event": indexed_event, "rpc_event": rpc_event, "parity": parity},
        "independent_readback": {"arcscan_index_vs_rpc": True, "geckoterminal_pool_identity": gecko_ok},
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
    print(json.dumps({"contract": result["contract"], "status": result["status"], "recent_block": result["recent_replay"]["rpc_event"]["block_number"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
