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

CHAIN = "robinhood"
CHAIN_ID = 4663
PRO_ROOT = f"https://api.blockscout.com/{CHAIN_ID}"
PUBLIC_ROOT = "https://robinhoodchain.blockscout.com"
USER_AGENT = "Investering-Framework-Meme-Alpha-Blockscout/1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_address(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip().lower()
    if not value.startswith("0x") or len(value) != 42:
        return None
    if any(ch not in "0123456789abcdef" for ch in value[2:]):
        return None
    return value


def address_of(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("hash") or value.get("address") or value.get("address_hash")
    return normalize_address(value)


def _safe_endpoint(endpoint_path: str) -> str:
    if not isinstance(endpoint_path, str) or not endpoint_path.startswith("/api/v2/"):
        raise ValueError("BLOCKSCOUT_ENDPOINT_MUST_START_/api/v2/")
    if "?" in endpoint_path or "#" in endpoint_path:
        raise ValueError("BLOCKSCOUT_ENDPOINT_QUERY_MUST_BE_SEPARATE")
    return endpoint_path


def _url(root: str, endpoint_path: str, *, api_key: str | None = None, query: dict[str, Any] | None = None) -> str:
    params = dict(query or {})
    if api_key:
        params["apikey"] = api_key
    base = root.rstrip("/") + _safe_endpoint(endpoint_path)
    return base if not params else base + "?" + urllib.parse.urlencode(params, doseq=True)


def _get_json(url: str, *, timeout: int = 20) -> tuple[int, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        body = exc.read()
        try:
            payload = json.loads(body)
        except Exception:
            payload = {"error": body[:300].decode("utf-8", "replace")}
        return exc.code, payload


def blockscout_get(
    endpoint_path: str,
    *,
    api_key: str | None = None,
    query: dict[str, Any] | None = None,
    timeout: int = 20,
    allow_public_fallback: bool = True,
    getter=_get_json,
) -> tuple[Any, dict[str, Any]]:
    """Authenticated Blockscout PRO first, Robinhood public explorer fallback second.

    Credentials are never returned in receipts or embedded in persisted URLs.
    Failure of both transports is a source-health failure, never negative chain evidence.
    """
    key = api_key if api_key is not None else os.environ.get("BLOCKSCOUT_API_KEY", "")
    attempts: list[tuple[str, str, str | None]] = []
    if key:
        attempts.append(("PRO_UNIFIED", PRO_ROOT, key))
    if allow_public_fallback:
        attempts.append(("PUBLIC_CHAIN_FALLBACK", PUBLIC_ROOT, None))
    if not attempts:
        raise RuntimeError("BLOCKSCOUT_API_KEY_MISSING_AND_PUBLIC_FALLBACK_DISABLED")

    errors: list[dict[str, Any]] = []
    for transport, root, transport_key in attempts:
        url = _url(root, endpoint_path, api_key=transport_key, query=query)
        try:
            status, payload = getter(url, timeout=timeout)
        except Exception as exc:
            errors.append({"transport": transport, "error_class": type(exc).__name__})
            continue
        if status == 200 and isinstance(payload, (dict, list)):
            return payload, {
                "status": "PASS",
                "transport": transport,
                "authenticated": transport == "PRO_UNIFIED",
                "chain_id": CHAIN_ID,
                "endpoint_path": endpoint_path,
                "observed_at_utc": utc_now(),
                "fallback_used": transport == "PUBLIC_CHAIN_FALLBACK",
                "prior_failures": errors,
            }
        errors.append({
            "transport": transport,
            "http_status": status,
            "error_class": "HTTP_OR_PAYLOAD_ERROR",
        })

    raise RuntimeError("BLOCKSCOUT_ALL_TRANSPORTS_FAILED:" + json.dumps(errors, sort_keys=True))


def _parameter_map(decoded_input: Any) -> dict[str, Any]:
    if not isinstance(decoded_input, dict):
        return {}
    rows = decoded_input.get("parameters")
    if not isinstance(rows, list):
        return {}
    output: dict[str, Any] = {}
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("name"), str):
            output[row["name"]] = row.get("value")
    return output


def _token_amount(raw: Any, decimals: Any) -> float | None:
    try:
        return int(str(raw)) / (10 ** int(str(decimals)))
    except (TypeError, ValueError, OverflowError):
        return None


def _initial_tokens_received(tx: dict[str, Any], token_ca: str, recipient: str | None) -> float | None:
    if recipient is None:
        return None
    transfers = tx.get("token_transfers")
    if not isinstance(transfers, list):
        return None
    total = 0.0
    matched = False
    for row in transfers:
        if not isinstance(row, dict):
            continue
        token = row.get("token") if isinstance(row.get("token"), dict) else {}
        address = normalize_address(token.get("address_hash") or token.get("address"))
        to = address_of(row.get("to"))
        if address != token_ca or to != recipient:
            continue
        value = row.get("total") if isinstance(row.get("total"), dict) else {}
        amount = _token_amount(value.get("value"), value.get("decimals") or token.get("decimals"))
        if amount is not None:
            total += amount
            matched = True
    return total if matched else None


def launch_origin_snapshot(
    address: str,
    *,
    api_key: str | None = None,
    allow_public_fallback: bool = True,
    timeout: int = 20,
    getter=_get_json,
) -> dict[str, Any]:
    token_ca = normalize_address(address)
    if token_ca is None:
        raise ValueError("INVALID_EVM_ADDRESS")

    address_payload, address_health = blockscout_get(
        f"/api/v2/addresses/{token_ca}",
        api_key=api_key,
        timeout=timeout,
        allow_public_fallback=allow_public_fallback,
        getter=getter,
    )

    creation_tx = address_payload.get("creation_transaction_hash") if isinstance(address_payload, dict) else None
    tx_payload: dict[str, Any] | None = None
    tx_health: dict[str, Any] | None = None
    if isinstance(creation_tx, str) and creation_tx.startswith("0x"):
        raw_tx, tx_health = blockscout_get(
            f"/api/v2/transactions/{creation_tx}",
            api_key=api_key,
            timeout=timeout,
            allow_public_fallback=allow_public_fallback,
            getter=getter,
        )
        tx_payload = raw_tx if isinstance(raw_tx, dict) else None

    token = address_payload.get("token") if isinstance(address_payload, dict) and isinstance(address_payload.get("token"), dict) else {}
    params = _parameter_map(tx_payload.get("decoded_input") if tx_payload else None)
    launch_params = params.get("params")
    launch_socials: list[str] = []
    embedded_description = None
    if isinstance(launch_params, list):
        if len(launch_params) > 3 and isinstance(launch_params[3], str):
            embedded_description = launch_params[3]
        if len(launch_params) > 4 and isinstance(launch_params[4], list):
            launch_socials = [str(v) for v in launch_params[4] if isinstance(v, str) and v.strip()]

    recipient = normalize_address(params.get("recipient"))
    quote_in_raw = params.get("quoteIn")
    quote_in_native = None
    try:
        quote_in_native = int(str(quote_in_raw)) / 10**18 if quote_in_raw is not None else None
    except (TypeError, ValueError, OverflowError):
        pass

    total_supply = _token_amount(token.get("total_supply"), token.get("decimals"))
    initial_tokens = _initial_tokens_received(tx_payload or {}, token_ca, recipient)
    initial_buy_pct = None
    if initial_tokens is not None and total_supply not in (None, 0):
        initial_buy_pct = (initial_tokens / total_supply) * 100.0

    exemptions = params.get("snipeTaxExemptions")
    exemptions_count = len(exemptions) if isinstance(exemptions, list) else None

    return {
        "contract": "MEME_ALPHA_BLOCKSCOUT_EXACT_CA_ENRICHMENT_v1",
        "status": "RESEARCH_ENRICHMENT_ONLY",
        "observed_at_utc": utc_now(),
        "chain": CHAIN,
        "chain_id": CHAIN_ID,
        "token_ca": token_ca,
        "address": {
            "is_contract": address_payload.get("is_contract") if isinstance(address_payload, dict) else None,
            "is_verified": address_payload.get("is_verified") if isinstance(address_payload, dict) else None,
            "proxy_type": address_payload.get("proxy_type") if isinstance(address_payload, dict) else None,
            "contract_name": address_payload.get("name") if isinstance(address_payload, dict) else None,
            "creator_address": address_of(address_payload.get("creator_address_hash")) if isinstance(address_payload, dict) else None,
            "creation_transaction_hash": creation_tx,
        },
        "token": {
            "name": token.get("name"),
            "symbol": token.get("symbol"),
            "decimals": token.get("decimals"),
            "total_supply": total_supply,
            "holders_count_at_observation": token.get("holders_count"),
            "exchange_rate_at_observation": token.get("exchange_rate"),
            "volume_24h_at_observation": token.get("volume_24h"),
        },
        "launch": {
            "transaction_hash": creation_tx,
            "block_number": tx_payload.get("block_number") if tx_payload else None,
            "timestamp": tx_payload.get("timestamp") if tx_payload else None,
            "method": tx_payload.get("method") if tx_payload else None,
            "from": address_of(tx_payload.get("from")) if tx_payload else None,
            "to": address_of(tx_payload.get("to")) if tx_payload else None,
            "recipient": recipient,
            "pair_token": normalize_address(params.get("pairToken")),
            "quote_in_native": quote_in_native,
            "initial_tokens_received": initial_tokens,
            "initial_buy_pct_supply": initial_buy_pct,
            "snipe_exemption_count": exemptions_count,
            "embedded_project_socials": launch_socials,
            "embedded_description": embedded_description,
        },
        "source_health": {
            "address": address_health,
            "transaction": tx_health,
            "overall": "PASS" if address_health.get("status") == "PASS" and (creation_tx is None or (tx_health or {}).get("status") == "PASS") else "DEGRADED",
            "missing_is_negative_evidence": False,
        },
        "authority": {
            "portfolio_action": False,
            "automatic_trading": False,
            "canonical_promotion": False,
            "project_ownership_proven": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Exact-CA Blockscout enrichment for Meme Alpha / Alpha Lab.")
    parser.add_argument("--address", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-public-fallback", action="store_true")
    args = parser.parse_args()

    payload = launch_origin_snapshot(
        args.address,
        allow_public_fallback=not args.no_public_fallback,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    print(json.dumps({
        "contract": payload["contract"],
        "token_ca": payload["token_ca"],
        "source_health": payload["source_health"]["overall"],
        "transport": payload["source_health"]["address"]["transport"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
