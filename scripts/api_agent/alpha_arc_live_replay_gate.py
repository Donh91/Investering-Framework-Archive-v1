from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import scripts.api_agent.alpha_arc_direct_new_pair as arc

RPC_DEFAULT = "https://rpc.arc-scan.org"
ARCSCAN_API = "https://api.arc-scan.org"
GECKO_API = "https://api.geckoterminal.com/api/v2"
BEANCAT_CA = "0x41c8a71f630c636294009fa4fb0cc4c3bbe674fe"
BEANCAT_POOL = "0x1f7f6a5e2ba06e9b3644afa8db8e1c606b5a5abb"
BEANCAT_FIRST_KNOWN_SWAP_BLOCK = 16_919_185
DEFAULT_FROM = 16_880_000
DEFAULT_TO = 16_920_000
DEFAULT_CHUNK = 5_000


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


def run_replay(rpc_url: str, from_block: int, to_block: int, chunk: int) -> dict[str, Any]:
    if not hasattr(arc, "_replay_base_rpc_call"):
        arc._replay_base_rpc_call = arc.rpc_call  # type: ignore[attr-defined]
    arc.rpc_call = retrying_rpc_call

    chain_id_hex = retrying_rpc_call(rpc_url, "eth_chainId", [])
    chain_id = int(chain_id_hex, 16) if isinstance(chain_id_hex, str) else None
    if chain_id != arc.CHAIN_ID:
        raise RuntimeError(f"WRONG_CHAIN:{chain_id}")

    events: list[dict[str, Any]] = []
    for start in range(from_block, to_block + 1, chunk):
        end = min(start + chunk - 1, to_block)
        events.extend(arc.scan_range(rpc_url, start, end))
        time.sleep(0.25)

    matches = [
        row for row in events
        if row.get("venue") == "uniswap_v3"
        and str(row.get("target_token_ca") or "").lower() == BEANCAT_CA
        and str(row.get("pool_address") or "").lower() == BEANCAT_POOL
    ]
    if len(matches) != 1:
        raise RuntimeError(f"CONTROL_MATCH_COUNT:{len(matches)}")
    match = matches[0]

    assertions = {
        "chain_id_5042": chain_id == arc.CHAIN_ID,
        "exact_ca": str(match.get("target_token_ca") or "").lower() == BEANCAT_CA,
        "exact_pool": str(match.get("pool_address") or "").lower() == BEANCAT_POOL,
        "quote_usdc_erc20": str(match.get("quote_asset") or "").lower() == arc.USDC_ERC20,
        "quote_representation": match.get("quote_representation") == "USDC_ERC20_6",
        "fee_10000": match.get("fee") == 10_000,
        "creation_precedes_known_swap": isinstance(match.get("block_number"), int) and match["block_number"] <= BEANCAT_FIRST_KNOWN_SWAP_BLOCK,
        "market_cap_not_inferred": match.get("market_cap_usd") is None,
        "fdv_not_inferred": match.get("fdv_usd") is None,
        "new_pool_not_equated_to_new_token": match.get("new_pool_is_new_token") is False,
        "shadow_only": match.get("status") == "SHADOW_ONLY",
        "data_integrity_pass": match.get("data_integrity_status") == "PASS",
    }
    if not all(assertions.values()):
        raise RuntimeError("CONTROL_ASSERTION_FAILED:" + ",".join(k for k, v in assertions.items() if not v))

    arcscan_token = get_json(f"{ARCSCAN_API}/v1/tokens/{BEANCAT_CA}")
    gecko_pool = get_json(f"{GECKO_API}/networks/arc/pools/{BEANCAT_POOL}")
    independent = {
        "arcscan_token_identity": contains_all(arcscan_token, [BEANCAT_CA]),
        "geckoterminal_pool_identity": contains_all(gecko_pool, [BEANCAT_POOL, BEANCAT_CA, arc.USDC_ERC20]),
    }
    if not all(independent.values()):
        raise RuntimeError("INDEPENDENT_READBACK_FAILED:" + ",".join(k for k, v in independent.items() if not v))

    return {
        "contract": "ALPHA_ARC_HISTORICAL_RPC_REPLAY_GATE_v1",
        "status": "PASS",
        "authority": {"shadow_activation_eligible": True, "user_alert": False, "adaptive_learning": False, "automatic_trading": False},
        "rpc_source": "rpc.arc-scan.org",
        "chain_id": chain_id,
        "range": {"from_block": from_block, "to_block": to_block, "chunk_size": chunk},
        "event_count": len(events),
        "control": {"name": "BEANCAT", "token_ca": BEANCAT_CA, "pool": BEANCAT_POOL, "first_known_swap_block": BEANCAT_FIRST_KNOWN_SWAP_BLOCK},
        "matched_event": match,
        "assertions": assertions,
        "independent_readback": independent,
        "independent_sources": [
            f"{ARCSCAN_API}/v1/tokens/{BEANCAT_CA}",
            f"{GECKO_API}/networks/arc/pools/{BEANCAT_POOL}",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rpc-url", default=RPC_DEFAULT)
    parser.add_argument("--from-block", type=int, default=DEFAULT_FROM)
    parser.add_argument("--to-block", type=int, default=DEFAULT_TO)
    parser.add_argument("--chunk", type=int, default=DEFAULT_CHUNK)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.chunk <= 0 or args.from_block < 0 or args.to_block < args.from_block:
        raise SystemExit("INVALID_RANGE")
    result = run_replay(args.rpc_url, args.from_block, args.to_block, args.chunk)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"contract": result["contract"], "status": result["status"], "event_count": result["event_count"], "matched_block": result["matched_event"]["block_number"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
