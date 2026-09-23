from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

CHAIN = "robinhood"
CHAIN_ID = 4663
CHAIN_ID_HEX = hex(CHAIN_ID)
PONS_V2_FACTORY = "0x7ed598bcef8bd9edd8c97a195c6d13f40801ec7e"
TOKEN_LAUNCHED_TOPIC0 = "0x8d4aad4953d0ca700d468f3753aa14432d1b35b43ec6409f051fb6aa43a89607"
MAX_LOG_SPAN = 2_000


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def normalize_address(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.lower()
    if not value.startswith("0x") or len(value) != 42:
        return None
    if any(ch not in "0123456789abcdef" for ch in value[2:]):
        return None
    return value


def address_from_topic(value: Any) -> str | None:
    if not isinstance(value, str) or not value.startswith("0x"):
        return None
    body = value[2:].lower()
    if len(body) != 64 or any(ch not in "0123456789abcdef" for ch in body):
        return None
    return normalize_address("0x" + body[-40:])


def padded_address_topic(address: str) -> str:
    normalized = normalize_address(address)
    if normalized is None:
        raise ValueError("INVALID_EVM_ADDRESS")
    return "0x" + ("0" * 24) + normalized[2:]


def data_word(data: Any, index: int) -> str | None:
    if not isinstance(data, str) or not data.startswith("0x"):
        return None
    body = data[2:]
    start = index * 64
    end = start + 64
    if len(body) < end:
        return None
    word = body[start:end].lower()
    if any(ch not in "0123456789abcdef" for ch in word):
        return None
    return word


def address_from_word(value: str | None) -> str | None:
    if not isinstance(value, str) or len(value) != 64:
        return None
    return normalize_address("0x" + value[-40:])


def uint_from_word(value: str | None) -> int | None:
    if not isinstance(value, str) or len(value) != 64:
        return None
    try:
        return int(value, 16)
    except ValueError:
        return None


def hex_int(value: Any) -> int | None:
    if not isinstance(value, str) or not value.startswith("0x"):
        return None
    try:
        return int(value, 16)
    except ValueError:
        return None


def provider_label(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return parsed.hostname or "configured_robinhood_rpc"


def parse_token_launched_log(
    log: dict[str, Any],
    *,
    observed_at_unix: int | None = None,
    rpc_source: str | None = None,
) -> dict[str, Any] | None:
    """Decode only immutable Pons V2 launch identity.

    Metadata, market cap, FDV, liquidity and price are intentionally not
    required for discovery. Enrichment failures must never erase a valid
    TokenLaunched row.
    """
    emitter = normalize_address(log.get("address"))
    topics = log.get("topics") if isinstance(log.get("topics"), list) else []
    if emitter != PONS_V2_FACTORY or len(topics) < 4:
        return None
    if str(topics[0]).lower() != TOKEN_LAUNCHED_TOPIC0:
        return None

    token = address_from_topic(topics[1])
    curve = address_from_topic(topics[2])
    deployer = address_from_topic(topics[3])
    if token is None or curve is None or deployer is None:
        return None

    data = log.get("data")
    pair_token = address_from_word(data_word(data, 0))
    launch_config_id = uint_from_word(data_word(data, 1))
    graduation_threshold = uint_from_word(data_word(data, 2))
    observed = int(observed_at_unix or time.time())
    block_number = hex_int(log.get("blockNumber"))

    return {
        "contract": "MEME_ALPHA_ROBINHOOD_PONS_V2_LAUNCH_EVENT_v1",
        "status": "SHADOW_ONLY",
        "chain": CHAIN,
        "chain_id": CHAIN_ID,
        "origin_type": "PONS_V2_TOKEN_LAUNCHED",
        "origin_emitter": emitter,
        "origin_topic0": TOKEN_LAUNCHED_TOPIC0,
        "token_ca": token,
        "curve": curve,
        "deployer": deployer,
        "pair_token": pair_token,
        "launch_config_id": launch_config_id,
        "graduation_threshold_raw": graduation_threshold,
        "block_number": block_number,
        "block_hash": log.get("blockHash"),
        "transaction_hash": log.get("transactionHash"),
        "transaction_index": hex_int(log.get("transactionIndex")),
        "log_index": hex_int(log.get("logIndex")),
        "observed_at_unix": observed,
        "observed_at_utc": datetime.fromtimestamp(observed, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "rpc_source": rpc_source,
        "raw_log_sha256": sha256(log),
        "token_name": None,
        "token_symbol": None,
        "token_supply": None,
        "market_cap_usd": None,
        "fdv_usd": None,
        "liquidity_usd": None,
        "price_usd": None,
        "metadata_state": "UNKNOWN",
        "market_state": "UNKNOWN",
        "new_pool_is_new_token": False,
        "data_integrity_status": "PASS",
        "authority": {
            "user_alert": False,
            "adaptive_learning": False,
            "automatic_trading": False,
        },
    }


def exact_target_match(
    event: dict[str, Any],
    *,
    target_ca: str | None = None,
    target_symbol: str | None = None,
    target_name: str | None = None,
    token_symbol: str | None = None,
    token_name: str | None = None,
) -> bool:
    """Exact identity helper used by targeted research fixtures.

    CA wins. Symbol/name are exact normalized fallbacks only; substring matching
    is forbidden because ASKR must not match BASKR.
    """
    if target_ca is not None:
        expected = normalize_address(target_ca)
        actual = normalize_address(event.get("token_ca"))
        return expected is not None and actual == expected

    if target_symbol is not None and token_symbol is not None:
        return token_symbol.strip().upper().lstrip("$") == target_symbol.strip().upper().lstrip("$")

    if target_name is not None and token_name is not None:
        norm = lambda s: "".join(ch for ch in s.upper() if ch.isalnum())
        return norm(token_name) == norm(target_name)

    return False


def _raw_rpc(url: str, method: str, params: list[Any], *, timeout: int = 15) -> Any:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "Investering-Framework-Robinhood-Pons-Shadow/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = json.loads(response.read())
    if payload.get("error"):
        raise RuntimeError(f"RPC_ERROR:{method}:{payload['error']}")
    return payload.get("result")


def rpc_call(
    url: str,
    method: str,
    params: list[Any],
    *,
    timeout: int = 15,
    attempts: int = 3,
) -> Any:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            return _raw_rpc(url, method, params, timeout=timeout)
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


def provider_call(
    rpc_urls: Iterable[str],
    method: str,
    params: list[Any],
    *,
    timeout: int = 15,
) -> tuple[Any, str, dict[str, str]]:
    """Fail over providers, requiring Robinhood chain identity on each provider."""
    errors: dict[str, str] = {}
    for url in rpc_urls:
        label = provider_label(url)
        try:
            chain_id = rpc_call(url, "eth_chainId", [], timeout=timeout)
            if str(chain_id).lower() != CHAIN_ID_HEX:
                raise RuntimeError(f"WRONG_CHAIN:{chain_id}")
            result = rpc_call(url, method, params, timeout=timeout)
            return result, label, errors
        except Exception as exc:
            errors[label] = repr(exc)
    raise RuntimeError("ALL_ROBINHOOD_PROVIDERS_FAILED:" + json.dumps(errors, sort_keys=True))


def provider_preflight(rpc_urls: Iterable[str], *, timeout: int = 15) -> dict[str, Any]:
    """Probe every configured provider without turning one-provider success into health proof."""
    rows: list[dict[str, Any]] = []
    for url in rpc_urls:
        label = provider_label(url)
        row: dict[str, Any] = {
            "provider": label,
            "chain_id_ok": False,
            "head_block": None,
            "state": "UNAVAILABLE",
            "error": None,
        }
        try:
            chain_id = rpc_call(url, "eth_chainId", [], timeout=timeout)
            if str(chain_id).lower() != CHAIN_ID_HEX:
                raise RuntimeError(f"WRONG_CHAIN:{chain_id}")
            head = hex_int(rpc_call(url, "eth_blockNumber", [], timeout=timeout))
            if head is None:
                raise RuntimeError("INVALID_HEAD_BLOCK")
            row.update({"chain_id_ok": True, "head_block": head, "state": "HEALTHY"})
        except Exception as exc:
            row["error"] = repr(exc)
        rows.append(row)
    healthy = [x for x in rows if x["state"] == "HEALTHY"]
    return {
        "providers": rows,
        "configured_provider_count": len(rows),
        "healthy_provider_count": len(healthy),
        "provider_redundancy_proven": len(healthy) >= 2,
        "minimum_healthy_head": min((x["head_block"] for x in healthy), default=None),
        "maximum_healthy_head": max((x["head_block"] for x in healthy), default=None),
    }


def _log_params(from_block: int, to_block: int, *, token_ca: str | None = None) -> dict[str, Any]:
    if from_block < 0 or to_block < from_block:
        raise ValueError("INVALID_BLOCK_RANGE")
    topics: list[Any] = [TOKEN_LAUNCHED_TOPIC0]
    if token_ca is not None:
        topics.append(padded_address_topic(token_ca))
    return {
        "address": PONS_V2_FACTORY,
        "topics": topics,
        "fromBlock": hex(from_block),
        "toBlock": hex(to_block),
    }


def scan_range(
    rpc_urls: Iterable[str],
    from_block: int,
    to_block: int,
    *,
    token_ca: str | None = None,
    timeout: int = 15,
) -> dict[str, Any]:
    """Scan canonical Pons V2 launches with bounded ranges and provider failover."""
    observed = int(time.time())
    rpc_urls = list(rpc_urls)
    preflight = provider_preflight(rpc_urls, timeout=timeout)
    min_head = preflight["minimum_healthy_head"]
    cursor_covered = min_head is not None and to_block <= min_head
    events: list[dict[str, Any]] = []
    provider_errors: dict[str, str] = {}
    providers_used: set[str] = set()

    cursor = from_block
    while cursor <= to_block:
        end = min(to_block, cursor + MAX_LOG_SPAN - 1)
        rows, source, errors = provider_call(
            rpc_urls,
            "eth_getLogs",
            [_log_params(cursor, end, token_ca=token_ca)],
            timeout=timeout,
        )
        providers_used.add(source)
        provider_errors.update(errors)
        if not isinstance(rows, list):
            raise RuntimeError("RPC_LOG_RESULT_NOT_LIST")
        for raw in rows:
            if not isinstance(raw, dict):
                continue
            event = parse_token_launched_log(raw, observed_at_unix=observed, rpc_source=source)
            if event is None:
                continue
            if token_ca is not None and event["token_ca"] != normalize_address(token_ca):
                continue
            events.append(event)
        cursor = end + 1

    # Canonical log identity dedupe. Overlap during recovery is expected.
    deduped: dict[tuple[Any, Any, Any], dict[str, Any]] = {}
    for event in events:
        key = (event.get("block_hash"), event.get("transaction_hash"), event.get("log_index"))
        deduped[key] = event

    output = sorted(
        deduped.values(),
        key=lambda row: (row.get("block_number") or -1, row.get("log_index") or -1),
    )
    if preflight["healthy_provider_count"] == 0:
        health_class = "UNAVAILABLE"
    elif not preflight["provider_redundancy_proven"] or not cursor_covered:
        health_class = "PARTIAL"
    elif output:
        health_class = "HEALTHY_NONEMPTY"
    else:
        health_class = "HEALTHY_ZERO"

    return {
        "contract": "MEME_ALPHA_ROBINHOOD_PONS_V2_BATCH_v1",
        "status": "SHADOW_ONLY",
        "chain": CHAIN,
        "chain_id": CHAIN_ID,
        "from_block": from_block,
        "to_block": to_block,
        "target_ca": normalize_address(token_ca) if token_ca else None,
        "event_count": len(output),
        "source_health": {
            "health_class": health_class,
            "observed_at_utc": datetime.fromtimestamp(observed, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
            "coverage_start_block": from_block,
            "coverage_end_block": to_block,
            "head_and_cursor_health": "PASS" if cursor_covered else "UNKNOWN_OR_LAGGING",
            "provider_redundancy_proven": preflight["provider_redundancy_proven"],
            "configured_provider_count": preflight["configured_provider_count"],
            "healthy_provider_count": preflight["healthy_provider_count"],
            "provider_preflight": preflight["providers"],
            "absence_is_evidence": health_class == "HEALTHY_ZERO",
        },
        "providers_used": sorted(providers_used),
        "provider_errors": provider_errors,
        "events": output,
        "authority": {
            "user_alert": False,
            "adaptive_learning": False,
            "automatic_trading": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Shadow-only Robinhood Pons V2 launch adapter.")
    parser.add_argument("--rpc-url", action="append", default=[])
    parser.add_argument("--from-block", type=int, required=True)
    parser.add_argument("--to-block", type=int, required=True)
    parser.add_argument("--token-ca")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rpc_urls = list(args.rpc_url)
    if not rpc_urls:
        env = os.environ.get("ROBINHOOD_RPC_URLS", "")
        rpc_urls = [value.strip() for value in env.split(",") if value.strip()]
    if not rpc_urls:
        raise SystemExit("ROBINHOOD_RPC_URLS_OR_--rpc-url_REQUIRED")

    payload = scan_range(
        rpc_urls,
        args.from_block,
        args.to_block,
        token_ca=args.token_ca,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical_bytes(payload))
    print(json.dumps({
        "contract": payload["contract"],
        "events": payload["event_count"],
        "providers_used": payload["providers_used"],
        "status": payload["status"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
