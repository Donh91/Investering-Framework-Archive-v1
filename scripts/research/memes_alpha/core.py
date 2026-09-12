from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Iterable

EVENT_CLASSES = {
    "INTENTIONAL_BUY", "PASSIVE_RECEIPT", "DUST_OR_SPAM", "SELL_OR_DISTRIBUTION",
    "FUNDING_SOURCE_LINK", "NEW_TOKEN_ACQUISITION", "MULTI_WALLET_CONVERGENCE",
    "SUPPLY_ACCUMULATION_CHANGE", "CTO_OR_COMMUNITY_TAKEOVER", "SOCIAL_METADATA_CHANGE",
    "LIQUIDITY_QUALITY_CHANGE", "WALLET_QUALITY_REVIEW_DUE",
}
ORIGINS = {"USER_SUPPLIED", "AUTONOMOUS_DISCOVERY", "HISTORICAL_REFERENCE", "EXTERNAL_RESEARCH_LEAD"}
CHAIN_IDS = {"ethereum", "robinhood_chain", "solana", "evm_other", "other"}
CADENCES = {"COLD": 6, "WATCH": 2, "HOT": 1}
FORBIDDEN_ACTION_KEYS = {"buy", "sell", "position_size", "portfolio_action", "canonical_promotion", "threshold_mutation", "model_weight"}
PRIVATE_KEY_HINTS = {"wallet", "address", "contract", "mint", "token_id", "private_identifier", "provider_value", "raw_value"}
HEX_ADDRESS = re.compile(r"^0x[a-fA-F0-9]{40}$")
BASE58_LIKE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{32,64}$")
HEX_HASH = re.compile(r"^[a-fA-F0-9]{64}$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def stable_hash(value: Any) -> str:
    if isinstance(value, bytes):
        payload = value
    elif isinstance(value, str):
        payload = value.encode("utf-8")
    else:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def canonical_identity(chain_id: str, contract_or_mint: str) -> str:
    if chain_id not in CHAIN_IDS:
        raise ValueError(f"unsupported chain_id: {chain_id}")
    if not contract_or_mint:
        raise ValueError("exact contract/mint identity required")
    return stable_hash({"chain_id": chain_id, "identity": contract_or_mint.strip()})


def validate_origin(origin: str) -> str:
    if origin not in ORIGINS:
        raise ValueError(f"invalid origin: {origin}")
    return origin


def classify_transfer(obs: dict[str, Any]) -> str:
    if obs.get("spam") or obs.get("dust") or obs.get("airdrop"):
        return "DUST_OR_SPAM"
    direction = obs.get("direction")
    if direction == "OUT" and obs.get("token_disposed") is True:
        return "SELL_OR_DISTRIBUTION"
    if direction == "IN" and obs.get("wallet_initiated") is True and obs.get("capital_committed") is True and obs.get("swap_proven") is True:
        return "INTENTIONAL_BUY"
    return "PASSIVE_RECEIPT"


def make_event(*, chain_id: str, identity: str, wallet_ref: str, origin: str,
               observation: dict[str, Any], observed_at: str, source_refs: list[str]) -> dict[str, Any]:
    event_class = classify_transfer(observation)
    event = {
        "schema": "MEMES_ALPHA_RESEARCH_EVENT_v1",
        "event_id": stable_hash({"chain_id": chain_id, "identity": identity, "wallet_ref": wallet_ref,
                                 "observed_at": observed_at, "event_class": event_class})[:24],
        "chain_id": chain_id,
        "asset_identity_hash": canonical_identity(chain_id, identity),
        "wallet_identity_hash": stable_hash(wallet_ref),
        "origin": validate_origin(origin),
        "event_class": event_class,
        "observed_at": observed_at,
        "source_refs": list(source_refs),
        "missingness": sorted(observation.get("missingness", [])),
        "frozen_features": {
            "liquidity_evidence": observation.get("liquidity_evidence", "UNKNOWN"),
            "holder_evidence": observation.get("holder_evidence", "UNKNOWN"),
            "social_evidence": observation.get("social_evidence", "UNKNOWN"),
            "cluster_evidence": observation.get("cluster_evidence", "UNKNOWN"),
            "paid_boost": observation.get("paid_boost", "UNKNOWN"),
        },
    }
    assert_no_trade_authority(event)
    return event


def convergence_events(events: Iterable[dict[str, Any]], qualified_wallet_hashes: set[str]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], set[str]] = defaultdict(set)
    earliest: dict[tuple[str, str], str] = {}
    for event in events:
        if event.get("event_class") != "INTENTIONAL_BUY":
            continue
        wallet = event.get("wallet_identity_hash")
        if wallet not in qualified_wallet_hashes:
            continue
        key = (event["chain_id"], event["asset_identity_hash"])
        grouped[key].add(wallet)
        earliest[key] = min(earliest.get(key, event["observed_at"]), event["observed_at"])
    out = []
    for (chain_id, asset_hash), wallets in sorted(grouped.items()):
        if len(wallets) >= 2:
            out.append({"schema": "MEMES_ALPHA_RESEARCH_EVENT_v1",
                        "event_id": stable_hash({"chain": chain_id, "asset": asset_hash, "kind": "convergence", "wallets": sorted(wallets)})[:24],
                        "chain_id": chain_id, "asset_identity_hash": asset_hash, "origin": "AUTONOMOUS_DISCOVERY",
                        "event_class": "MULTI_WALLET_CONVERGENCE", "observed_at": earliest[(chain_id, asset_hash)],
                        "qualified_wallet_count": len(wallets), "missingness": []})
    return out


def solana_risk_features(*, exact_mint_verified: bool, top10_concentration: float | None,
                         linked_fresh_wallet_cluster: bool | None, paid_boost: bool | None,
                         creator_verified: bool | None) -> dict[str, Any]:
    if not exact_mint_verified:
        raise ValueError("Solana identity requires exact mint verification")
    distribution = "UNKNOWN"
    if linked_fresh_wallet_cluster is True:
        distribution = "CLUSTER_RISK"
    elif top10_concentration is not None and linked_fresh_wallet_cluster is False:
        distribution = "CONCENTRATION_OBSERVED"
    return {"chain_id": "solana", "identity_verified": True, "distribution_state": distribution,
            "creator_state": "VERIFIED" if creator_verified is True else "REBUTTED" if creator_verified is False else "UNKNOWN",
            "paid_boost_state": "PAID" if paid_boost is True else "NOT_OBSERVED" if paid_boost is False else "UNKNOWN",
            "paid_boost_counts_as_independent_alpha": False}


def cross_chain_snapshot(rows: Iterable[dict[str, Any]], horizons=("5m", "15m", "1h", "6h", "24h")) -> dict[str, Any]:
    result: dict[str, Any] = {"schema": "MEMES_ALPHA_CROSS_CHAIN_SNAPSHOT_v1", "horizons": list(horizons), "rows": []}
    for row in rows:
        if not row.get("identity_verified"):
            raise ValueError("ticker/name match cannot create cross-chain sibling relationship")
        frozen = row.get("frozen_discovery_features") or {}
        if any(k in frozen for k in ("future_return", "matured_outcome", "later_price")):
            raise ValueError("no-hindsight violation in frozen discovery features")
        result["rows"].append({"chain_id": row["chain_id"], "asset_identity_hash": row["asset_identity_hash"],
                               "narrative_id": row.get("narrative_id", "UNKNOWN"), "frozen_discovery_features": frozen,
                               "outcomes_by_horizon": {h: (row.get("outcomes_by_horizon") or {}).get(h, "PENDING") for h in horizons}})
    return result


def choose_cadence(*, high_value_event: bool, qualified_case_count: int, source_degraded: bool) -> str:
    if source_degraded:
        return "COLD"
    if high_value_event:
        return "HOT"
    return "WATCH" if qualified_case_count > 0 else "COLD"


def cadence_due(last_full_refresh_utc: str | None, cadence: str, now_utc: datetime) -> bool:
    if cadence not in CADENCES:
        raise ValueError("invalid cadence")
    if not last_full_refresh_utc:
        return True
    last = datetime.fromisoformat(last_full_refresh_utc.replace("Z", "+00:00"))
    return (now_utc - last).total_seconds() >= CADENCES[cadence] * 3600


def assert_no_trade_authority(payload: Any) -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            if key.lower() in FORBIDDEN_ACTION_KEYS:
                raise ValueError(f"forbidden trade/authority key: {key}")
            assert_no_trade_authority(value)
    elif isinstance(payload, list):
        for value in payload:
            assert_no_trade_authority(value)


def _looks_private_identifier(value: str) -> bool:
    v = value.strip()
    return bool(HEX_ADDRESS.match(v) or BASE58_LIKE.match(v))


def validate_public_payload(payload: Any, path: str = "$") -> None:
    if isinstance(payload, dict):
        for key, value in payload.items():
            lower = key.lower()
            if lower in FORBIDDEN_ACTION_KEYS:
                raise ValueError(f"forbidden authority key in public payload: {path}.{key}")
            is_hash_key = lower.endswith("_hash") or lower.endswith("_sha256") or lower in {"private_manifest_sha256", "private_seed_sha256"}
            if any(hint in lower for hint in PRIVATE_KEY_HINTS) and not is_hash_key:
                raise ValueError(f"private key not allowed in public payload: {path}.{key}")
            if is_hash_key and isinstance(value, str):
                if not HEX_HASH.match(value):
                    raise ValueError(f"invalid hash field: {path}.{key}")
                continue
            validate_public_payload(value, f"{path}.{key}")
    elif isinstance(payload, list):
        for i, value in enumerate(payload):
            validate_public_payload(value, f"{path}[{i}]")
    elif isinstance(payload, str) and _looks_private_identifier(payload):
        raise ValueError(f"private-looking identifier not allowed in public payload: {path}")


def build_public_manifest(*, private_manifest_hash: str, seed_hash: str, case_count: int,
                          event_counts: dict[str, int], chain_coverage: dict[str, str],
                          health: str, reason_codes: list[str], generated_at: str | None = None) -> dict[str, Any]:
    if health not in {"PASS", "DEGRADED", "BLOCKED"}:
        raise ValueError("invalid health")
    for event_class in event_counts:
        if event_class not in EVENT_CLASSES:
            raise ValueError(f"invalid event class: {event_class}")
    payload = {"schema": "MEMES_ALPHA_PUBLIC_MANIFEST_v1", "generated_at": generated_at or utc_now(),
               "private_manifest_sha256": private_manifest_hash, "private_seed_sha256": seed_hash,
               "case_count": int(case_count), "event_counts": {k: int(v) for k, v in sorted(event_counts.items())},
               "chain_coverage": dict(sorted(chain_coverage.items())), "health": health,
               "reason_codes": sorted(set(reason_codes)), "authority": "RESEARCH_ONLY_NO_TRADE_AUTHORITY"}
    assert_no_trade_authority(payload)
    validate_public_payload(payload)
    return payload
