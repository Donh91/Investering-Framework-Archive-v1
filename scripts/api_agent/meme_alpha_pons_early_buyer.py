from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from scripts.api_agent.meme_alpha_clean_g3 import (
    adjust_wallet_entities,
    clean_g3_feature_summary,
    compute_asof_wallet_quality_for_graph,
)

CASE_CONTRACT = "MAL_PONS_CURVE_CAPTURE_CASE_V1"
COHORT_CONTRACT = "MAL_PONS_EARLY_BUYER_COHORT_FREEZE_V1"
GRAPH_CONTRACT = "MEME_ALPHA_PONS_EARLY_BUYER_GRAPH_v1"
PACKET_CONTRACT = "MEME_ALPHA_PONS_WALLET_PRECURSOR_PACKET_v1"
WALLET_RECORD_CONTRACT = "WALLET_ALPHA_RECORD_V1"
EDGE_STATES = {"REPEATABLE_EDGE_CANDIDATE", "REPEATABLE_EDGE_SUPPORTED"}
FIXED_COHORT_WINDOW_SECONDS = 300


def _parse_utc(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _stable_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()


def _address(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text.startswith("0x") or len(text) != 42:
        raise ValueError("INVALID_EVM_ADDRESS")
    if any(ch not in "0123456789abcdef" for ch in text[2:]):
        raise ValueError("INVALID_EVM_ADDRESS")
    return text


def build_pons_early_buyer_graph(
    case_freeze: dict[str, Any],
    cohort_freeze: dict[str, Any],
) -> dict[str, Any]:
    if case_freeze.get("contract") != CASE_CONTRACT:
        raise ValueError("INVALID_PONS_CASE_CONTRACT")
    if cohort_freeze.get("contract") != COHORT_CONTRACT:
        raise ValueError("INVALID_PONS_COHORT_CONTRACT")
    if str(case_freeze.get("case_id")) != str(cohort_freeze.get("case_id")):
        raise ValueError("PONS_CASE_ID_MISMATCH")
    if str(cohort_freeze.get("wallet_semantics")) != "PONS_CURVE_BUY_TOKEN_RECIPIENT":
        raise ValueError("PONS_COHORT_WALLET_SEMANTICS_INVALID")
    if cohort_freeze.get("launch_time_action_credit") is not False:
        raise ValueError("RETROACTIVE_ACTION_CREDIT_FORBIDDEN")
    if str(case_freeze.get("chain")) != "robinhood-chain" or int(case_freeze.get("chain_id")) != 4663:
        raise ValueError("PONS_CHAIN_INVALID")

    origin = _parse_utc(case_freeze["launch_block_timestamp_utc"])
    cutoff = _parse_utc(cohort_freeze["cohort_window_end_utc"])
    cutoff_seconds = int((cutoff - origin).total_seconds())
    if cutoff_seconds != FIXED_COHORT_WINDOW_SECONDS:
        raise ValueError("PONS_COHORT_WINDOW_DRIFT")

    available_times = [
        _parse_utc(case_freeze["frozen_at_utc"]),
        _parse_utc(cohort_freeze["frozen_at_utc"]),
        _parse_utc(cohort_freeze["prospective_credit_from_utc"]),
    ]
    signal_available = max(available_times)

    cohort_wallets = [_address(v) for v in cohort_freeze.get("cohort_wallets") or []]
    if len(set(cohort_wallets)) != len(cohort_wallets):
        raise ValueError("DUPLICATE_PONS_COHORT_WALLET")
    if int(cohort_freeze.get("cohort_size", -1)) != len(cohort_wallets):
        raise ValueError("PONS_COHORT_SIZE_MISMATCH")

    evidence = cohort_freeze.get("first_buy_evidence") or []
    if len(evidence) != len(cohort_wallets):
        raise ValueError("PONS_FIRST_BUY_EVIDENCE_INCOMPLETE")

    evidence_by_wallet: dict[str, dict[str, Any]] = {}
    for row in evidence:
        wallet = _address(row.get("wallet"))
        if wallet in evidence_by_wallet:
            raise ValueError("DUPLICATE_PONS_FIRST_BUY_EVIDENCE")
        if wallet not in cohort_wallets:
            raise ValueError("PONS_FIRST_BUY_WALLET_NOT_IN_COHORT")
        event_time = _parse_utc(row["event_timestamp_utc"])
        if event_time < origin or event_time > cutoff:
            raise ValueError("PONS_FIRST_BUY_OUTSIDE_FIXED_WINDOW")
        evidence_by_wallet[wallet] = row

    buyers: list[dict[str, Any]] = []
    for wallet in cohort_wallets:
        row = evidence_by_wallet[wallet]
        event_time = _parse_utc(row["event_timestamp_utc"])
        tx_hash = str(row["transaction_hash"]).lower()
        log_index = int(row["log_index"])
        buyers.append({
            "wallet": wallet,
            "wallet_role_class": "PONS_TOKEN_RECIPIENT",
            "self_initiated_trade_proven": False,
            "initiator_equivalence_proven": False,
            "first_buy_effective_at_utc": _iso_z(event_time),
            "last_buy_effective_at_utc": _iso_z(event_time),
            "first_buy_latency_seconds": int((event_time - origin).total_seconds()),
            "buy_count": 1,
            "first_block": int(row["block_number"]),
            "first_transaction_index": int(row["transaction_index"]),
            "first_log_index": log_index,
            "source_event_identities": [f"{tx_hash}:{log_index}"],
        })

    buyers.sort(
        key=lambda row: (
            row["first_block"],
            row["first_transaction_index"],
            row["first_log_index"],
            row["wallet"],
        )
    )
    source_ids = [row["source_event_identities"][0] for row in buyers]
    token = _address(case_freeze["token_address"])

    graph_core = {
        "contract": GRAPH_CONTRACT,
        "case_id": str(case_freeze["case_id"]),
        "chain": "robinhood-chain",
        "chain_id": 4663,
        "venue": "pons-v2-bonding-curve",
        "token_id": token,
        "token_origin_utc": _iso_z(origin),
        "cutoff_seconds": cutoff_seconds,
        "cutoff_utc": _iso_z(cutoff),
        "signal_available_at_utc": _iso_z(signal_available),
        "prospective_credit_from_utc": str(cohort_freeze["prospective_credit_from_utc"]),
        "launch_time_action_credit": False,
        "capture_state": "COMPLETE",
        "eligible_for_training": True,
        "buyer_semantics": "CURVE_BUY_TOKEN_RECIPIENT_NOT_INITIATOR",
        "recipient_buyer_addresses": len(buyers),
        "buyers": buyers,
        "entity_count": "UNKNOWN",
        "source_event_identities": source_ids,
        "authority": {
            "automatic_trading": False,
            "portfolio_action": False,
            "position_size_output": False,
            "buy_now_promotion": False,
            "alert_authority": False,
        },
    }
    graph_core["graph_sha256"] = _stable_hash(graph_core)
    return graph_core


def _registry_state_asof(
    graph: dict[str, Any],
    wallet_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cutoff = _parse_utc(graph["cutoff_utc"])
    current = {str(row["wallet"]) for row in graph.get("buyers", [])}
    rows: list[dict[str, Any]] = []

    by_wallet: dict[str, list[dict[str, Any]]] = {wallet: [] for wallet in current}
    for record in wallet_records:
        if record.get("contract") != WALLET_RECORD_CONTRACT:
            continue
        wallet = record.get("wallet") if isinstance(record.get("wallet"), dict) else {}
        if str(wallet.get("chain")) not in {"robinhood", "robinhood-chain"}:
            continue
        try:
            address = _address(wallet.get("address"))
        except ValueError:
            continue
        if address in by_wallet:
            by_wallet[address].append(record)

    for wallet in sorted(current):
        admitted: list[dict[str, Any]] = []
        future_ignored = 0
        for record in by_wallet.get(wallet, []):
            states = record.get("states") if isinstance(record.get("states"), dict) else {}
            reviewed = states.get("last_review_utc")
            if not reviewed:
                continue
            if _parse_utc(reviewed) > cutoff:
                future_ignored += 1
                continue
            admitted.append(record)
        admitted.sort(
            key=lambda record: str(
                (record.get("states") if isinstance(record.get("states"), dict) else {}).get("last_review_utc")
                or ""
            )
        )
        chosen = admitted[-1] if admitted else None
        states = chosen.get("states") if isinstance(chosen, dict) and isinstance(chosen.get("states"), dict) else {}
        summary = chosen.get("summary") if isinstance(chosen, dict) and isinstance(chosen.get("summary"), dict) else {}
        rows.append({
            "wallet": wallet,
            "wallet_edge_state": str(states.get("wallet_edge_state") or "UNKNOWN"),
            "last_review_utc": states.get("last_review_utc"),
            "history_completeness": str(summary.get("history_completeness") or "UNKNOWN"),
            "future_registry_records_ignored": future_ignored,
            "source_record_present": chosen is not None,
        })
    return rows


def build_pons_wallet_precursor_packet(
    case_freeze: dict[str, Any],
    cohort_freeze: dict[str, Any],
    prior_outcomes: list[dict[str, Any]],
    wallet_records: list[dict[str, Any]],
    relationship_evidence: list[dict[str, Any]],
    *,
    min_prior_matured: int = 3,
) -> dict[str, Any]:
    graph = build_pons_early_buyer_graph(case_freeze, cohort_freeze)
    quality = compute_asof_wallet_quality_for_graph(
        graph,
        prior_outcomes,
        role="EARLY_LAUNCH",
        min_prior_matured=min_prior_matured,
    )
    entity = adjust_wallet_entities(quality, relationship_evidence, cutoff_utc=graph["cutoff_utc"])
    registry = _registry_state_asof(graph, wallet_records)
    registry_map = {row["wallet"]: row for row in registry}
    local_quality = {row["wallet"]: row for row in quality}

    edge_wallets = {
        wallet
        for wallet, state in registry_map.items()
        if state["wallet_edge_state"] in EDGE_STATES
        and local_quality.get(wallet, {}).get("qualified_history") is True
    }
    edge_quality_rows = [row for row in quality if row["wallet"] in edge_wallets]
    edge_entity = adjust_wallet_entities(
        edge_quality_rows,
        relationship_evidence,
        cutoff_utc=graph["cutoff_utc"],
    )
    independent_edge = int(
        edge_entity.get("qualified_effective_entity_count_strong_controller_only") or 0
    )

    if independent_edge >= 2:
        precursor_state = "MULTI_ENTITY_CONVERGENCE"
    elif independent_edge == 1:
        precursor_state = "WATCH"
    else:
        precursor_state = "UNKNOWN"

    packet_core = {
        "contract": PACKET_CONTRACT,
        "case_id": graph["case_id"],
        "chain": graph["chain"],
        "venue": graph["venue"],
        "token_id": graph["token_id"],
        "feature_cutoff_utc": graph["cutoff_utc"],
        "signal_available_at_utc": graph["signal_available_at_utc"],
        "launch_time_action_credit": False,
        "wallet_precursor_evidence": precursor_state,
        "time_sensitive_precursor_emission_supported": False,
        "buyer_graph": graph,
        "wallet_quality_rows": quality,
        "wallet_registry_states_asof": registry,
        "entity_adjustment": entity,
        "edge_wallets_asof": sorted(edge_wallets),
        "effective_independent_edge_wallets": independent_edge,
        "edge_entity_adjustment": edge_entity,
        "feature_summary": clean_g3_feature_summary(quality, entity),
        "scientific_limits": [
            "FIRST10_MEMBERSHIP_IS_KNOWN_ONLY_AFTER_BUY_EVENTS",
            "TOKEN_RECIPIENT_IS_NOT_AUTOMATICALLY_TX_INITIATOR",
            "NO_CROSS_CHAIN_OR_CROSS_VENUE_SKILL_IMPORT",
            "FUTURE_WALLET_STATE_AND_OUTCOMES_FORBIDDEN",
            "TIME_SENSITIVE_PRECURSOR_REQUIRES_SEPARATE_LEAD_TIME_EVIDENCE",
            "NO_LAUNCH_TIME_ACTION_CREDIT",
        ],
        "authority": {
            "research_only": True,
            "automatic_trading": False,
            "portfolio_action": False,
            "position_sizing": False,
            "buy_now_promotion": False,
            "alert_authority": False,
        },
    }
    packet_core["packet_sha256"] = _stable_hash(packet_core)
    return packet_core
