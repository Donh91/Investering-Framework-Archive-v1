from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from scripts.api_agent.meme_alpha_prospective import freeze_shadow_observation

SUPPORTED_CUTOFF_SECONDS = {60, 300, 900, 1800}
SUPPORTED_LINK_KINDS = {"SAME_FUNDER", "BUNDLE_LINK", "STRONG_CONTROLLER"}
SUPPORTED_WALLET_ROLES = {
    "EARLY_LAUNCH",
    "CURVE_OR_MIGRATION",
    "MOMENTUM_RUNNER",
    "TAIL_HOLDER",
    "EXIT_DISCIPLINE",
    "PHOENIX_REENTRY",
    "LORE_NATIVE",
}


def _parse_utc(value: str) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _epoch_utc(seconds: int) -> str:
    return datetime.fromtimestamp(int(seconds), tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _shrunk_rate(wins: int, n: int, *, alpha: float = 1.0, beta: float = 1.0) -> float | None:
    if n < 0 or wins < 0 or wins > n:
        raise ValueError("INVALID_BINOMIAL_COUNTS")
    return (wins + alpha) / (n + alpha + beta) if n or alpha + beta else None


def build_current_token_buyer_graph(
    create_event: dict[str, Any],
    trade_events: list[dict[str, Any]],
    *,
    cutoff_seconds: int,
    excluded_addresses: set[str] | None = None,
    capture_state: str = "COMPLETE",
) -> dict[str, Any]:
    """Build a point-in-time buyer graph from normalized immutable Pump events.

    A normalized native BUY event is treated as evidence of a trade by its `user`,
    but known routers/pools/programs supplied by the caller are excluded. This
    layer never equates multiple addresses with multiple independent entities.
    """

    if cutoff_seconds not in SUPPORTED_CUTOFF_SECONDS:
        raise ValueError("UNSUPPORTED_CLEAN_G3_CUTOFF")
    if create_event.get("contract") != "MEME_ALPHA_PUMP_CREATE_EVENT_v1":
        raise ValueError("INVALID_PUMP_CREATE_EVENT")
    if capture_state not in {"COMPLETE", "DEGRADED"}:
        raise ValueError("INVALID_CAPTURE_STATE")

    excluded = {str(item) for item in (excluded_addresses or set())}
    origin = int(create_event["event_timestamp"])
    cutoff_epoch = origin + int(cutoff_seconds)
    mint = str(create_event["mint"])
    quote_mint = str(create_event["quote_mint"])

    deduped: dict[str, dict[str, Any]] = {}
    for event in trade_events:
        if event.get("contract") != "MEME_ALPHA_PUMP_TRADE_EVENT_v1":
            raise ValueError("INVALID_PUMP_TRADE_EVENT")
        if str(event.get("mint")) != mint:
            raise ValueError("CLEAN_G3_MINT_MISMATCH")
        if str(event.get("quote_mint")) != quote_mint:
            raise ValueError("CLEAN_G3_QUOTE_MINT_MISMATCH")
        deduped[str(event["source_record_or_event_identity"])] = event

    eligible = [
        event for event in deduped.values()
        if bool(event.get("is_buy"))
        and origin <= int(event["event_timestamp"]) <= cutoff_epoch
    ]
    eligible.sort(key=lambda event: (int(event["event_timestamp"]), int(event["slot"]), str(event["source_record_or_event_identity"])))

    by_wallet: dict[str, list[dict[str, Any]]] = defaultdict(list)
    excluded_hits: list[dict[str, Any]] = []
    for event in eligible:
        wallet = str(event["user"])
        if wallet in excluded:
            excluded_hits.append({
                "wallet": wallet,
                "reason": "CALLER_SUPPLIED_ROUTER_POOL_PROGRAM_EXCLUSION",
                "event_identity": str(event["source_record_or_event_identity"]),
            })
            continue
        by_wallet[wallet].append(event)

    buyer_rows: list[dict[str, Any]] = []
    for wallet, events in sorted(by_wallet.items()):
        first = events[0]
        last = events[-1]
        gross_quote = sum(int(event["quote_amount_raw"]) for event in events)
        gross_token = sum(int(event["token_amount_raw"]) for event in events)
        buyer_rows.append({
            "wallet": wallet,
            "wallet_role_class": "SELF_INITIATED_TRADE",
            "first_buy_effective_at_utc": str(first["event_timestamp_utc"]),
            "last_buy_effective_at_utc": str(last["event_timestamp_utc"]),
            "first_buy_latency_seconds": int(first["event_timestamp"]) - origin,
            "buy_count": len(events),
            "gross_quote_amount_raw": gross_quote,
            "gross_token_amount_raw": gross_token,
            "first_slot": int(first["slot"]),
            "last_slot": int(last["slot"]),
            "source_event_identities": [str(event["source_record_or_event_identity"]) for event in events],
        })

    provenance_ids = sorted(
        str(event["source_record_or_event_identity"])
        for event in eligible
    )
    return {
        "contract": "MEME_ALPHA_CURRENT_TOKEN_BUYER_GRAPH_v1",
        "chain": "solana",
        "venue": "pump.fun",
        "mint": mint,
        "quote_mint": quote_mint,
        "token_origin_utc": str(create_event["event_timestamp_utc"]),
        "cutoff_seconds": int(cutoff_seconds),
        "cutoff_utc": _epoch_utc(cutoff_epoch),
        "capture_state": capture_state,
        "eligible_for_training": capture_state == "COMPLETE",
        "native_buy_events_seen": len(eligible),
        "raw_unique_buy_addresses": len({str(event["user"]) for event in eligible}),
        "router_pool_program_excluded_addresses": len({item["wallet"] for item in excluded_hits}),
        "self_initiated_buyer_addresses": len(buyer_rows),
        "buyers": buyer_rows,
        "excluded": excluded_hits,
        "entity_count": "UNKNOWN",
        "entity_resolution_state": "ADDRESS_ONLY_ROUTER_POOL_EXCLUSIONS_APPLIED",
        "source_event_identities": provenance_ids,
        "graph_sha256": _stable_hash({
            "mint": mint,
            "cutoff_utc": _epoch_utc(cutoff_epoch),
            "buyers": buyer_rows,
            "excluded": excluded_hits,
            "events": provenance_ids,
        }),
        "authority": {
            "automatic_trading": False,
            "portfolio_action": False,
            "position_size_output": False,
            "buy_now_promotion": False,
        },
    }


def compute_asof_wallet_quality(
    buyer_graph: dict[str, Any],
    prior_outcomes: list[dict[str, Any]],
    *,
    role: str = "EARLY_LAUNCH",
    min_prior_matured: int = 3,
) -> list[dict[str, Any]]:
    """Compute wallet quality using only outcomes matured before candidate cutoff.

    Outcomes are chain/venue/role local by default. Cross-chain evidence must be
    tested separately and is not silently imported into a wallet's local skill.
    """

    if buyer_graph.get("contract") != "MEME_ALPHA_CURRENT_TOKEN_BUYER_GRAPH_v1":
        raise ValueError("INVALID_BUYER_GRAPH")
    if role not in SUPPORTED_WALLET_ROLES:
        raise ValueError("INVALID_WALLET_SPECIALISM_ROLE")
    if min_prior_matured < 1:
        raise ValueError("INVALID_MIN_PRIOR_MATURED")

    cutoff = _parse_utc(str(buyer_graph["cutoff_utc"]))
    chain = str(buyer_graph["chain"])
    venue = str(buyer_graph["venue"])
    current_wallets = {str(item["wallet"]): item for item in buyer_graph.get("buyers", [])}

    by_wallet: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for outcome in prior_outcomes:
        wallet = str(outcome.get("wallet", ""))
        if wallet not in current_wallets:
            continue
        if str(outcome.get("chain", "")) != chain or str(outcome.get("venue", "")) != venue:
            continue
        if str(outcome.get("role", "")) != role:
            continue
        matured_at = outcome.get("maturity_at_utc")
        if not matured_at:
            continue
        if _parse_utc(str(matured_at)) > cutoff:
            continue
        by_wallet[wallet].append(outcome)

    rows: list[dict[str, Any]] = []
    for wallet, buyer in sorted(current_wallets.items()):
        history = sorted(by_wallet.get(wallet, []), key=lambda item: str(item["maturity_at_utc"]))
        n = len(history)
        wins_2x = sum(1 for item in history if item.get("sellable_2x") is True)
        wins_5x = sum(1 for item in history if item.get("sellable_5x") is True)
        wins_10x = sum(1 for item in history if item.get("sellable_10x") is True)
        known_2x = sum(1 for item in history if item.get("sellable_2x") in {True, False})
        known_5x = sum(1 for item in history if item.get("sellable_5x") in {True, False})
        known_10x = sum(1 for item in history if item.get("sellable_10x") in {True, False})
        mfes = [float(item["realizable_mfe_x"]) for item in history if item.get("realizable_mfe_x") is not None]
        maes = [float(item["mae_fraction"]) for item in history if item.get("mae_fraction") is not None]
        liq = [bool(item["liquidity_survived"]) for item in history if item.get("liquidity_survived") in {True, False}]
        rows.append({
            "wallet": wallet,
            "role": role,
            "chain": chain,
            "venue": venue,
            "first_buy_latency_seconds": buyer.get("first_buy_latency_seconds"),
            "current_token_buy_count": buyer.get("buy_count"),
            "prior_matured_count": n,
            "qualified_history": n >= min_prior_matured,
            "known_2x_count": known_2x,
            "known_5x_count": known_5x,
            "known_10x_count": known_10x,
            "sellable_2x_hits": wins_2x,
            "sellable_5x_hits": wins_5x,
            "sellable_10x_hits": wins_10x,
            "shrunk_sellable_2x_rate": round(_shrunk_rate(wins_2x, known_2x), 6) if known_2x else None,
            "shrunk_sellable_5x_rate": round(_shrunk_rate(wins_5x, known_5x), 6) if known_5x else None,
            "shrunk_sellable_10x_rate": round(_shrunk_rate(wins_10x, known_10x), 6) if known_10x else None,
            "mean_realizable_mfe_x": round(_mean(mfes), 6) if mfes else None,
            "mean_mae_fraction": round(_mean(maes), 6) if maes else None,
            "liquidity_survival_rate": round(sum(liq) / len(liq), 6) if liq else None,
            "latest_matured_outcome_at_utc": str(history[-1]["maturity_at_utc"]) if history else None,
            "source_outcome_ids": [str(item.get("outcome_id", "UNKNOWN")) for item in history],
        })
    return rows


class _UnionFind:
    def __init__(self, items: set[str]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: str) -> str:
        p = self.parent[item]
        if p != item:
            self.parent[item] = self.find(p)
        return self.parent[item]

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def adjust_wallet_entities(
    wallet_quality_rows: list[dict[str, Any]],
    link_evidence: list[dict[str, Any]],
    *,
    cutoff_utc: str,
) -> dict[str, Any]:
    """Apply conservative entity evidence without treating shared funder as identity.

    SAME_FUNDER and BUNDLE_LINK are retained as relationship evidence. Only
    STRONG_CONTROLLER evidence collapses addresses into a common effective entity.
    """

    cutoff = _parse_utc(cutoff_utc)
    wallets = {str(row["wallet"]) for row in wallet_quality_rows}
    qualified = {str(row["wallet"]) for row in wallet_quality_rows if row.get("qualified_history") is True}
    uf = _UnionFind(wallets)
    same_funder_groups: dict[str, set[str]] = defaultdict(set)
    bundle_edges: list[tuple[str, str]] = []
    strong_edges: list[tuple[str, str]] = []

    used_evidence: list[dict[str, Any]] = []
    for item in link_evidence:
        kind = str(item.get("kind", ""))
        if kind not in SUPPORTED_LINK_KINDS:
            continue
        effective_at = item.get("effective_at_utc")
        if not effective_at or _parse_utc(str(effective_at)) > cutoff:
            continue
        if kind == "SAME_FUNDER":
            wallet = str(item.get("wallet", ""))
            funder = str(item.get("funder", ""))
            if wallet in wallets and funder:
                same_funder_groups[funder].add(wallet)
                used_evidence.append(dict(item))
        else:
            a, b = str(item.get("wallet_a", "")), str(item.get("wallet_b", ""))
            if a not in wallets or b not in wallets or a == b:
                continue
            if kind == "BUNDLE_LINK":
                bundle_edges.append((a, b))
            elif kind == "STRONG_CONTROLLER":
                strong_edges.append((a, b))
                uf.union(a, b)
            used_evidence.append(dict(item))

    strong_groups: dict[str, set[str]] = defaultdict(set)
    for wallet in wallets:
        strong_groups[uf.find(wallet)].add(wallet)
    effective_entity_count = len(strong_groups)
    largest_strong = max((len(group) for group in strong_groups.values()), default=0)

    same_funder_linked_qualified: set[str] = set()
    largest_funder_group = 0
    for group in same_funder_groups.values():
        qgroup = group & qualified
        if len(qgroup) >= 2:
            same_funder_linked_qualified.update(qgroup)
            largest_funder_group = max(largest_funder_group, len(qgroup))

    return {
        "contract": "MEME_ALPHA_G3_ENTITY_ADJUSTMENT_v1",
        "cutoff_utc": cutoff_utc,
        "raw_wallet_count": len(wallets),
        "qualified_wallet_count": len(qualified),
        "effective_entity_count_strong_controller_only": effective_entity_count,
        "largest_strong_controller_entity_size": largest_strong,
        "same_funder_linked_qualified_wallets": len(same_funder_linked_qualified),
        "same_funder_fraction_of_qualified": round(len(same_funder_linked_qualified) / len(qualified), 6) if qualified else None,
        "largest_same_funder_qualified_group": largest_funder_group,
        "bundle_link_edge_count": len(bundle_edges),
        "strong_controller_edge_count": len(strong_edges),
        "same_funder_group_count": sum(1 for group in same_funder_groups.values() if len(group) >= 2),
        "entity_resolution_confidence": "PARTIAL_STRONG_CONTROLLER_ONLY",
        "same_funder_collapses_identity": False,
        "used_evidence_sha256": _stable_hash(sorted(used_evidence, key=lambda item: json.dumps(item, sort_keys=True))),
    }


def clean_g3_feature_summary(
    wallet_quality_rows: list[dict[str, Any]],
    entity_adjustment: dict[str, Any],
) -> dict[str, Any]:
    qualified = [row for row in wallet_quality_rows if row.get("qualified_history") is True]
    rates_5x = [float(row["shrunk_sellable_5x_rate"]) for row in qualified if row.get("shrunk_sellable_5x_rate") is not None]
    rates_10x = [float(row["shrunk_sellable_10x_rate"]) for row in qualified if row.get("shrunk_sellable_10x_rate") is not None]
    mfes = [float(row["mean_realizable_mfe_x"]) for row in qualified if row.get("mean_realizable_mfe_x") is not None]

    return {
        "qualified_wallet_count_raw": len(qualified),
        "effective_entity_count_strong_controller_only": entity_adjustment.get("effective_entity_count_strong_controller_only"),
        "same_funder_fraction_of_qualified": entity_adjustment.get("same_funder_fraction_of_qualified"),
        "largest_same_funder_qualified_group": entity_adjustment.get("largest_same_funder_qualified_group"),
        "mean_asof_shrunk_sellable_5x_rate": round(_mean(rates_5x), 6) if rates_5x else None,
        "max_asof_shrunk_sellable_5x_rate": round(max(rates_5x), 6) if rates_5x else None,
        "mean_asof_shrunk_sellable_10x_rate": round(_mean(rates_10x), 6) if rates_10x else None,
        "mean_prior_realizable_mfe_x": round(_mean(mfes), 6) if mfes else None,
        "clean_g3_status": "MEASURED" if qualified else "INSUFFICIENT_PRIOR_HISTORY",
    }


def clean_g3_shadow_features(
    buyer_graph: dict[str, Any],
    wallet_quality_rows: list[dict[str, Any]],
    entity_adjustment: dict[str, Any],
) -> list[dict[str, Any]]:
    summary = clean_g3_feature_summary(wallet_quality_rows, entity_adjustment)
    cutoff_utc = str(buyer_graph["cutoff_utc"])
    provenance = {
        "buyer_graph_sha256": buyer_graph["graph_sha256"],
        "wallet_quality": wallet_quality_rows,
        "entity_adjustment_sha256": entity_adjustment["used_evidence_sha256"],
    }
    source_hash = _stable_hash(provenance)
    return [
        {
            "feature_name": name,
            "feature_value_at_cutoff": value if value is not None else "UNKNOWN",
            "feature_effective_at_utc": cutoff_utc,
            "source_observed_at_utc": cutoff_utc,
            "source_or_schema_version": "PROSPECTIVE_CLEAN_G3_BUYER_GRAPH_SPEC_v1",
            "source_record_or_event_identity": f"clean-g3:{buyer_graph['mint']}:{buyer_graph['cutoff_seconds']}s:{source_hash}:{name}",
            "mutability_class": "DERIVED_FROM_PINNED_EVENTS" if value is not None else "UNKNOWN",
        }
        for name, value in summary.items()
        if name != "clean_g3_status"
    ]


def freeze_clean_g3_shadow_packet(
    *,
    buyer_graph: dict[str, Any],
    g2_features: list[dict[str, Any]],
    wallet_quality_rows: list[dict[str, Any]],
    entity_adjustment: dict[str, Any],
) -> dict[str, Any]:
    cutoff_minutes = int(buyer_graph["cutoff_seconds"]) // 60
    g3_features = clean_g3_shadow_features(buyer_graph, wallet_quality_rows, entity_adjustment)
    packet = freeze_shadow_observation(
        identity={
            "chain": str(buyer_graph["chain"]),
            "token_id": str(buyer_graph["mint"]),
            "token_origin_utc": str(buyer_graph["token_origin_utc"]),
        },
        cutoff_minutes=cutoff_minutes,
        cutoff_utc=str(buyer_graph["cutoff_utc"]),
        features=list(g2_features) + g3_features,
        wallet_roles=["SELF_INITIATED_TRADE"],
        collector_status="ACTIVE" if buyer_graph.get("capture_state") == "COMPLETE" else "DEGRADED",
    )
    packet["clean_g3_contract"] = "PROSPECTIVE_CLEAN_G3_BUYER_GRAPH_SPEC_v1"
    packet["clean_g3_status"] = clean_g3_feature_summary(wallet_quality_rows, entity_adjustment)["clean_g3_status"]
    packet["authority"]["buy_now_promotion"] = False
    packet["observation_sha256"] = _stable_hash({k: v for k, v in packet.items() if k != "observation_sha256"})
    return packet
