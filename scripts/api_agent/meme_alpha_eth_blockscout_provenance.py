from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


CHAIN = "ethereum-mainnet"
CHAIN_ID = 1
PRO_ROOT = f"https://api.blockscout.com/{CHAIN_ID}"
PUBLIC_ROOT = "https://eth.blockscout.com"
SOURCE_CONTRACT = "MEME_ALPHA_ETH_BLOCKSCOUT_EXACT_CA_PROVENANCE_v1"
PARENT_CONTRACT = "MOONSHOT_DETERMINISTIC_ALERT_EVIDENCE_v1"
USER_AGENT = "Investering-Framework-Meme-Alpha-ETH-Provenance/1.0"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def normalize_address(value: Any) -> str | None:
    if isinstance(value, dict):
        value = value.get("hash") or value.get("address") or value.get("address_hash")
    if not isinstance(value, str):
        return None
    value = value.strip().lower()
    if len(value) != 42 or not value.startswith("0x"):
        return None
    return value if all(ch in "0123456789abcdef" for ch in value[2:]) else None


def normalize_tx_hash(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    value = value.strip().lower()
    if len(value) != 66 or not value.startswith("0x"):
        return None
    return value if all(ch in "0123456789abcdef" for ch in value[2:]) else None


def _get_json(url: str, *, timeout: int = 20) -> tuple[int, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as exc:
        return exc.code, {"error": "HTTP_ERROR"}


def _safe_url(root: str, path: str, api_key: str | None) -> str:
    if not path.startswith("/api/v2/") or "?" in path or "#" in path:
        raise ValueError("BLOCKSCOUT_ENDPOINT_INVALID")
    url = root.rstrip("/") + path
    return url if not api_key else url + "?" + urllib.parse.urlencode({"apikey": api_key})


def blockscout_get(
    path: str,
    *,
    api_key: str | None = None,
    allow_public_fallback: bool = True,
    timeout: int = 20,
    getter: Callable[..., tuple[int, Any]] = _get_json,
) -> tuple[Any, dict[str, Any]]:
    """Read Ethereum Blockscout without ever returning a credential-bearing URL."""
    key = api_key if api_key is not None else os.environ.get("BLOCKSCOUT_API_KEY", "")
    attempts: list[tuple[str, str, str | None]] = []
    if key:
        attempts.append(("PRO_UNIFIED_ETH", PRO_ROOT, key))
    if allow_public_fallback:
        attempts.append(("PUBLIC_ETH_FALLBACK", PUBLIC_ROOT, None))
    if not attempts:
        raise RuntimeError("BLOCKSCOUT_API_KEY_MISSING_AND_PUBLIC_FALLBACK_DISABLED")

    failures: list[dict[str, Any]] = []
    for transport, root, transport_key in attempts:
        try:
            status, payload = getter(_safe_url(root, path, transport_key), timeout=timeout)
        except Exception as exc:
            failures.append({"transport": transport, "error_class": type(exc).__name__})
            continue
        if status == 200 and isinstance(payload, dict):
            return payload, {
                "status": "PASS",
                "transport": transport,
                "authenticated": transport == "PRO_UNIFIED_ETH",
                "chain_id": CHAIN_ID,
                "endpoint_path": path,
                "observed_at_utc": utc_now(),
                "fallback_used": transport == "PUBLIC_ETH_FALLBACK",
                "prior_failures": failures,
            }
        failures.append({"transport": transport, "http_status": status, "error_class": "HTTP_OR_PAYLOAD_ERROR"})
    raise RuntimeError("BLOCKSCOUT_ETH_TRANSPORTS_FAILED:" + json.dumps(failures, sort_keys=True))


def _creation_status(payload: dict[str, Any]) -> str:
    value = payload.get("status")
    if isinstance(value, bool):
        return "success" if value else "failed"
    normalized = str(value or "").strip().lower()
    return "success" if normalized in {"ok", "success", "1", "true"} else "failed" if normalized else "unknown"


def produce(
    candidate_id: str,
    token_ca: str,
    *,
    frozen_payload_ref: str,
    api_key: str | None = None,
    allow_public_fallback: bool = True,
    timeout: int = 20,
    getter: Callable[..., tuple[int, Any]] = _get_json,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Produce fail-closed deterministic P evidence for one frozen ETH identity."""
    token = normalize_address(token_ca)
    expected_candidate = f"eth:{token}" if token else ""
    if token is None or candidate_id != expected_candidate:
        frozen = {
            "contract": SOURCE_CONTRACT,
            "chain": CHAIN,
            "chain_id": CHAIN_ID,
            "candidate_id": candidate_id,
            "token_ca": token,
            "source_health": {"status": "UNKNOWN", "reason": "IDENTITY_BINDING_INVALID"},
        }
        return _evidence(candidate_id, token, "UNKNOWN", frozen, frozen_payload_ref), frozen

    try:
        address_payload, address_health = blockscout_get(
            f"/api/v2/addresses/{token}", api_key=api_key, allow_public_fallback=allow_public_fallback,
            timeout=timeout, getter=getter,
        )
        returned_address = normalize_address(address_payload.get("hash") or address_payload.get("address"))
        creation_hash = normalize_tx_hash(address_payload.get("creation_transaction_hash"))
        tx_payload: dict[str, Any] | None = None
        tx_health: dict[str, Any] | None = None
        if creation_hash:
            raw_tx, tx_health = blockscout_get(
                f"/api/v2/transactions/{creation_hash}", api_key=api_key,
                allow_public_fallback=allow_public_fallback, timeout=timeout, getter=getter,
            )
            tx_payload = raw_tx if isinstance(raw_tx, dict) else None
        frozen = {
            "contract": SOURCE_CONTRACT,
            "chain": CHAIN,
            "chain_id": CHAIN_ID,
            "candidate_id": candidate_id,
            "token_ca": token,
            "returned_address": returned_address,
            "is_contract": address_payload.get("is_contract"),
            "is_verified": address_payload.get("is_verified"),
            "is_scam": address_payload.get("is_scam"),
            "creator_address": normalize_address(address_payload.get("creator_address_hash") or address_payload.get("creator_address")),
            "creation_transaction_hash": creation_hash,
            "creation_status": _creation_status(tx_payload or {}),
            "source_health": {
                "status": "PASS" if address_health.get("status") == "PASS" and tx_health and tx_health.get("status") == "PASS" else "UNKNOWN",
                "address": address_health,
                "creation_transaction": tx_health,
            },
        }
    except Exception as exc:
        frozen = {
            "contract": SOURCE_CONTRACT,
            "chain": CHAIN,
            "chain_id": CHAIN_ID,
            "candidate_id": candidate_id,
            "token_ca": token,
            "source_health": {"status": "DEGRADED", "error_class": type(exc).__name__},
        }
        return _evidence(candidate_id, token, "DEGRADED", frozen, frozen_payload_ref), frozen

    passed = all((
        frozen["returned_address"] == token,
        frozen["is_contract"] is True,
        frozen["is_verified"] is True,
        frozen["creation_status"] == "success",
        frozen["creation_transaction_hash"] is not None,
        frozen["creator_address"] is not None,
        frozen["is_scam"] is False,
        frozen["source_health"]["status"] == "PASS",
    ))
    return _evidence(candidate_id, token, "PASS" if passed else "UNKNOWN", frozen, frozen_payload_ref), frozen


def _evidence(candidate_id: str, token_ca: str | None, status: str, frozen: dict[str, Any], frozen_payload_ref: str) -> dict[str, Any]:
    digest = sha256_hex(frozen)
    evidence = {
        "contract": PARENT_CONTRACT,
        "status": status,
        "candidate_id": candidate_id,
        "token_ca": token_ca,
        "chain": CHAIN,
        "chain_id": CHAIN_ID,
        "llm_generated": False,
        "frozen_payload_digest": f"sha256:{digest}",
        "receipts": [],
        "authority": "alert_gate_only",
        "portfolio_action": False,
        "automatic_trading": False,
    }
    if status == "PASS":
        evidence["receipts"] = [{
            "family": "P",
            "state": "PASS",
            "deterministic": True,
            "llm_generated": False,
            "source_contract": SOURCE_CONTRACT,
            "evidence_refs": [frozen_payload_ref, f"sha256:{digest}"],
            "frozen_payload_digest": f"sha256:{digest}",
        }]
    return evidence


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))


def main() -> None:
    parser = argparse.ArgumentParser(description="ETH-only deterministic Blockscout P-family provenance producer")
    parser.add_argument("--candidate-id", required=True)
    parser.add_argument("--token-ca", required=True)
    parser.add_argument("--frozen-payload-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-public-fallback", action="store_true")
    args = parser.parse_args()
    evidence, frozen = produce(
        args.candidate_id, args.token_ca,
        frozen_payload_ref=str(args.frozen_payload_output),
        allow_public_fallback=not args.no_public_fallback,
    )
    _write(args.frozen_payload_output, frozen)
    _write(args.output, evidence)
    print(json.dumps({"status": evidence["status"], "receipts": len(evidence["receipts"]), "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
