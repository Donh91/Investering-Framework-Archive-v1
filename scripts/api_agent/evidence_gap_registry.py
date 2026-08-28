from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TERMINAL_STATES = {"ALREADY_COVERED", "CLOSED", "PROSPECTIVE_CAPTURE_ACTIVE"}
ACTIONABLE_STATES = {"BACKFILL_QUEUED", "PROSPECTIVE_CAPTURE_REQUIRED", "SOURCE_DISCOVERY_REQUIRED"}
STATE_PRECEDENCE = {
    "SOURCE_DISCOVERY_REQUIRED": 3,
    "PROSPECTIVE_CAPTURE_REQUIRED": 2,
    "BACKFILL_QUEUED": 1,
}
DEFAULT_FAMILY = "EG-UNCLASSIFIED-EVIDENCE"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text[:80] or "gap"


def normalized_text(candidate: dict[str, Any]) -> str:
    values = [
        candidate.get("metric_name"),
        candidate.get("decision_relevance"),
        candidate.get("missing_history_problem"),
        candidate.get("evidence_reference"),
    ]
    return " ".join(str(v or "").lower().replace("_", " ") for v in values)


def gap_key(candidate: dict[str, Any]) -> str:
    """Stable observation identity. This is deliberately not the GitHub issue identity."""
    identity = {
        "metric_name": str(candidate.get("metric_name", "")).strip().lower(),
        "data_shape": candidate.get("data_shape"),
        "capability_hint": candidate.get("capability_hint"),
        "desired_cadence_minutes": candidate.get("desired_cadence_minutes"),
    }
    return hashlib.sha256(canonical_bytes(identity)).hexdigest()[:16]


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def family_definitions(policy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = policy.get("families")
    if not isinstance(rows, dict):
        return {}
    return {str(k): v for k, v in rows.items() if isinstance(v, dict)}


def gap_family(candidate: dict[str, Any], policy: dict[str, Any]) -> str:
    """Resolve one durable work-owner family from an evidence observation."""
    families = family_definitions(policy)
    direct = policy.get("direct_capability_map") if isinstance(policy.get("direct_capability_map"), dict) else {}
    hint = str(candidate.get("capability_hint") or "UNKNOWN_SOURCE")
    text = normalized_text(candidate)

    if hint == "LIVE_BREADTH" and any(
        token in text
        for token in ("btc dominance", "total2", "total3", "market capitalization", "market-capitalization")
    ):
        return "EG-MARKET-STRUCTURE"

    mapped = str(direct.get(hint) or "")
    if mapped and mapped in families:
        return mapped

    rules = (
        ("EG-PROVENANCE", ("frozen-reference", "frozen reference", "source binding", "provenance bridge", "settlement convention", "settled-session convention")),
        ("EG-SENTIMENT", ("cfgi", "fear and greed", "fear & greed", "sentiment component")),
        ("EG-ETF-FLOWS", ("etf flow", "etf net-flow", "etf net flow", "settled etf")),
        ("EG-MACRO-HISTORY", ("fred", "treasury yield", "2-year yield", "10-year yield", "broad dollar", "macro observation", "macro context", "rates, dollar", "financial-condition")),
        ("EG-MARKET-STRUCTURE", ("btc dominance", "total2", "total3", "market capitalization", "market-capitalization", "market structure dominance", "total market path")),
        ("EG-BREADTH-HISTORY", ("breadth", "advancer", "decliner", "constituent", "fixed universe", "stable universe")),
        ("EG-DERIVATIVES-FORENSICS", ("funding", "open interest", "liquidation", "order book", "order-book", "taker flow", "depth imbalance", "option chain", "option-chain", "skew", "derivatives", "microstructure")),
        ("EG-FORECAST-OUTCOMES", ("forecast candidate", "candidate outcome", "candidate maturation", "candidate specification", "candidate issuance", "candidate freeze", "range candidate", "range score", "benchmark score", "matured outcome", "scoring record", "prospective candidate")),
        ("EG-HOURLY-SEQUENCE", ("hourly", "eth/btc persistence", "ethbtc persistence", "ethbtc level", "price path", "return sequence", "anchor-aligned", "fixed-anchor")),
        ("EG-STABLECOIN-LIQUIDITY", ("stablecoin supply", "stablecoin liquidity", "stablecoin deployment", "stablecoin exchange", "stablecoin aggregate")),
    )
    for family_id, tokens in rules:
        if family_id in families and any(token in text for token in tokens):
            return family_id
    return DEFAULT_FAMILY if DEFAULT_FAMILY in families else str(policy.get("fallback_family") or DEFAULT_FAMILY)


def route(candidate: dict[str, Any], capabilities: dict[str, Any]) -> tuple[str, str]:
    hint = str(candidate.get("capability_hint") or "UNKNOWN_SOURCE")
    cap = capabilities.get(hint) if isinstance(capabilities.get(hint), dict) else capabilities.get("UNKNOWN_SOURCE", {})
    if hint == "UNKNOWN_SOURCE":
        return "SOURCE_DISCOVERY_REQUIRED", "No allowlisted source capability is known yet."
    mode = str(cap.get("closure_mode") or "")
    if mode == "SOURCE_DISCOVERY_REQUIRED" or mode == "SOURCE_OWNER_REQUIRED":
        return "SOURCE_DISCOVERY_REQUIRED", f"{hint} requires a verified source/owner implementation before capture."
    if bool(cap.get("historical_backfill")):
        return "BACKFILL_QUEUED", f"{hint} supports bounded historical retrieval or derivation; queue backfill first."
    if bool(cap.get("prospective_capture")):
        return "PROSPECTIVE_CAPTURE_REQUIRED", f"{hint} is point-in-time/perishable; preserve the historical gap and start prospective capture."
    return "SOURCE_DISCOVERY_REQUIRED", f"{hint} has no executable closure path in the capability registry."


def _iso_min(values: list[str], fallback: str) -> str:
    valid = [v for v in values if v]
    return min(valid) if valid else fallback


def _iso_max(values: list[str], fallback: str) -> str:
    valid = [v for v in values if v]
    return max(valid) if valid else fallback


def _merge_unique(values: list[Any]) -> list[Any]:
    out: list[Any] = []
    seen: set[str] = set()
    for value in values:
        if value is None or value == "":
            continue
        marker = json.dumps(value, sort_keys=True, default=str)
        if marker in seen:
            continue
        seen.add(marker)
        out.append(value)
    return out


def observation_from_item(item: dict[str, Any], *, observation_key: str | None = None, legacy_gap_id: str | None = None) -> dict[str, Any]:
    obs = {
        "observation_key": observation_key or str(item.get("observation_key") or gap_key(item)),
        "metric_name": item.get("metric_name"),
        "decision_relevance": item.get("decision_relevance"),
        "missing_history_problem": item.get("missing_history_problem"),
        "desired_history_days": item.get("desired_history_days"),
        "desired_cadence_minutes": item.get("desired_cadence_minutes"),
        "data_shape": item.get("data_shape"),
        "capability_hint": item.get("capability_hint"),
        "evidence_reference": item.get("evidence_reference"),
        "first_seen_utc": item.get("first_seen_utc"),
        "last_seen_utc": item.get("last_seen_utc"),
        "observation_count": int(item.get("observation_count", 1) or 1),
        "closure_state": item.get("closure_state"),
        "routing_rationale": item.get("routing_rationale"),
    }
    if legacy_gap_id:
        obs["legacy_gap_id"] = legacy_gap_id
    if isinstance(item.get("validation"), dict):
        obs["legacy_validation"] = item.get("validation")
    return obs


def merge_observation(observations: list[dict[str, Any]], incoming: dict[str, Any]) -> list[dict[str, Any]]:
    key = str(incoming.get("observation_key") or "")
    for existing in observations:
        if str(existing.get("observation_key") or "") != key:
            continue
        existing["first_seen_utc"] = _iso_min(
            [str(existing.get("first_seen_utc") or ""), str(incoming.get("first_seen_utc") or "")],
            str(existing.get("first_seen_utc") or incoming.get("first_seen_utc") or ""),
        )
        existing["last_seen_utc"] = _iso_max(
            [str(existing.get("last_seen_utc") or ""), str(incoming.get("last_seen_utc") or "")],
            str(incoming.get("last_seen_utc") or existing.get("last_seen_utc") or ""),
        )
        existing["observation_count"] = int(existing.get("observation_count", 0) or 0) + int(incoming.get("observation_count", 0) or 0)
        for field in (
            "metric_name", "decision_relevance", "missing_history_problem", "desired_history_days",
            "desired_cadence_minutes", "data_shape", "capability_hint", "evidence_reference",
            "closure_state", "routing_rationale", "legacy_gap_id", "legacy_validation",
        ):
            if incoming.get(field) not in (None, ""):
                existing[field] = incoming.get(field)
        return observations
    observations.append(incoming)
    return observations


def aggregate_state(observations: list[dict[str, Any]]) -> str:
    active = [
        str(obs.get("closure_state") or "")
        for obs in observations
        if str(obs.get("closure_state") or "") in ACTIONABLE_STATES
    ]
    if active:
        return max(active, key=lambda state: STATE_PRECEDENCE[state])
    terminal = [str(obs.get("closure_state") or "") for obs in observations if str(obs.get("closure_state") or "") in TERMINAL_STATES]
    if terminal and len(terminal) == len(observations):
        if "PROSPECTIVE_CAPTURE_ACTIVE" in terminal:
            return "PROSPECTIVE_CAPTURE_ACTIVE"
        if "ALREADY_COVERED" in terminal:
            return "ALREADY_COVERED"
        return "CLOSED"
    return "SOURCE_DISCOVERY_REQUIRED"


def build_family_item(
    family_id: str,
    observations: list[dict[str, Any]],
    policy: dict[str, Any],
    timestamp: str,
    *,
    previous_family_item: dict[str, Any] | None = None,
) -> dict[str, Any]:
    defs = family_definitions(policy)
    meta = defs.get(family_id, {})
    observations = sorted(
        observations,
        key=lambda row: (str(row.get("first_seen_utc") or ""), str(row.get("observation_key") or "")),
    )
    counts = [int(row.get("observation_count", 0) or 0) for row in observations]
    first_seen = _iso_min([str(row.get("first_seen_utc") or "") for row in observations], timestamp)
    last_seen = _iso_max([str(row.get("last_seen_utc") or "") for row in observations], timestamp)
    desired_days = [int(row.get("desired_history_days")) for row in observations if isinstance(row.get("desired_history_days"), int)]
    cadences = [int(row.get("desired_cadence_minutes")) for row in observations if isinstance(row.get("desired_cadence_minutes"), int) and int(row.get("desired_cadence_minutes")) > 0]
    metric_names = _merge_unique([row.get("metric_name") for row in observations])
    hints = _merge_unique([row.get("capability_hint") for row in observations])
    legacy_ids = _merge_unique([row.get("legacy_gap_id") for row in observations])
    latest = max(observations, key=lambda row: str(row.get("last_seen_utc") or "")) if observations else {}

    state = aggregate_state(observations)
    if previous_family_item and str(previous_family_item.get("closure_state") or "") in TERMINAL_STATES:
        state = str(previous_family_item["closure_state"])

    item: dict[str, Any] = {
        "gap_id": family_id,
        "family_id": family_id,
        "family_name": meta.get("name") or family_id,
        "metric_name": meta.get("metric_name") or meta.get("name") or family_id,
        "family_scope": meta.get("scope"),
        "decision_relevance": latest.get("decision_relevance"),
        "missing_history_problem": latest.get("missing_history_problem"),
        "desired_history_days": max(desired_days) if desired_days else None,
        "desired_cadence_minutes": min(cadences) if cadences else None,
        "data_shape": "FAMILY_AGGREGATE",
        "capability_hint": hints[0] if len(hints) == 1 else "FAMILY_AGGREGATE",
        "capability_hints": hints,
        "evidence_reference": latest.get("evidence_reference"),
        "first_seen_utc": first_seen,
        "last_seen_utc": last_seen,
        "observation_count": sum(counts),
        "observation_variant_count": len(observations),
        "metric_names": metric_names,
        "legacy_gap_ids": legacy_ids,
        "closure_state": state,
        "routing_rationale": meta.get("routing_rationale") or "Repeated evidence observations are consolidated under one durable work owner.",
        "observations": observations,
        "authority": {"evidence_only": True, "market_semantics": False},
    }
    if previous_family_item and isinstance(previous_family_item.get("validation"), dict):
        item["validation"] = previous_family_item["validation"]
    if previous_family_item and previous_family_item.get("rejection_reason"):
        item["rejection_reason"] = previous_family_item.get("rejection_reason")
    return item


def migrate_registry(registry: dict[str, Any], policy: dict[str, Any], timestamp: str) -> dict[str, Any]:
    old_items = registry.get("items") if isinstance(registry.get("items"), dict) else {}
    grouped: dict[str, list[dict[str, Any]]] = {}
    previous_family_items: dict[str, dict[str, Any]] = {}

    for old_id, raw in old_items.items():
        if not isinstance(raw, dict):
            continue
        old_id = str(old_id)
        if old_id in family_definitions(policy):
            previous_family_items[old_id] = raw
            raw_observations = raw.get("observations") if isinstance(raw.get("observations"), list) else []
            if raw_observations:
                grouped.setdefault(old_id, []).extend(obs for obs in raw_observations if isinstance(obs, dict))
            else:
                grouped.setdefault(old_id, []).append(observation_from_item(raw))
            continue

        family_id = gap_family(raw, policy)
        grouped.setdefault(family_id, []).append(observation_from_item(raw, legacy_gap_id=old_id))

    new_items: dict[str, dict[str, Any]] = {}
    for family_id, raw_observations in grouped.items():
        merged: list[dict[str, Any]] = []
        for obs in raw_observations:
            merged = merge_observation(merged, dict(obs))
        new_items[family_id] = build_family_item(
            family_id,
            merged,
            policy,
            timestamp,
            previous_family_item=previous_family_items.get(family_id),
        )

    registry["contract"] = "ADAPTIVE_EVIDENCE_GAP_REGISTRY_v1"
    registry["status"] = registry.get("status") or "ACTIVE_SHADOW_RESEARCH_ONLY"
    registry["items"] = new_items
    registry["family_policy_contract"] = policy.get("contract")
    registry["family_count"] = len(new_items)
    registry["legacy_item_migration"] = "FAMILY_CONSOLIDATED_NO_EVIDENCE_DELETION"
    registry.setdefault("authority", {"market_rule_change": False, "canonical_state": False, "portfolio_action": False, "self_merge": False})
    return registry


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=Path, required=True)
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--capabilities", type=Path, required=True)
    ap.add_argument("--queue", type=Path, required=True)
    ap.add_argument("--families", type=Path)
    args = ap.parse_args()

    audit = load_json(args.audit, {"candidates": []})
    capability_doc = load_json(args.capabilities, {"capabilities": {}})
    caps = capability_doc.get("capabilities") if isinstance(capability_doc.get("capabilities"), dict) else {}
    family_path = args.families or args.capabilities.with_name("EVIDENCE_GAP_FAMILY_POLICY_v1.json")
    policy = load_json(family_path, {})
    if not family_definitions(policy):
        raise SystemExit(f"evidence_gap_family_policy_missing_or_invalid:{family_path}")

    registry = load_json(args.registry, {
        "contract": "ADAPTIVE_EVIDENCE_GAP_REGISTRY_v1",
        "status": "ACTIVE_SHADOW_RESEARCH_ONLY",
        "items": {},
        "authority": {"market_rule_change": False, "canonical_state": False, "portfolio_action": False, "self_merge": False},
    })

    timestamp = now_utc()
    registry = migrate_registry(registry, policy, timestamp)
    touched: list[str] = []

    for candidate in audit.get("candidates", []):
        if not isinstance(candidate, dict) or not str(candidate.get("metric_name") or "").strip():
            continue
        family_id = gap_family(candidate, policy)
        previous = registry["items"].get(family_id) if isinstance(registry["items"].get(family_id), dict) else None
        state, rationale = route(candidate, caps)
        observation = observation_from_item(
            {
                **candidate,
                "first_seen_utc": timestamp,
                "last_seen_utc": timestamp,
                "observation_count": 1,
                "closure_state": state,
                "routing_rationale": rationale,
            },
            observation_key=gap_key(candidate),
        )
        observations = [dict(obs) for obs in (previous.get("observations", []) if previous else []) if isinstance(obs, dict)]
        observations = merge_observation(observations, observation)
        registry["items"][family_id] = build_family_item(
            family_id,
            observations,
            policy,
            timestamp,
            previous_family_item=previous,
        )
        if family_id not in touched:
            touched.append(family_id)

    registry["updated_at_utc"] = timestamp
    registry["item_count"] = len(registry["items"])
    registry["family_count"] = len(registry["items"])
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_bytes(canonical_bytes(registry))

    queue_items = [
        item for item in registry["items"].values()
        if isinstance(item, dict) and item.get("closure_state") in ACTIONABLE_STATES
    ]
    queue_items.sort(
        key=lambda row: (
            -int(row.get("observation_count", 0)),
            str(row.get("first_seen_utc", "")),
            str(row.get("gap_id", "")),
        )
    )
    queue_doc = {
        "contract": "ADAPTIVE_EVIDENCE_GAP_QUEUE_v1",
        "generated_at_utc": timestamp,
        "family_policy_contract": policy.get("contract"),
        "issue_identity": "ONE_DURABLE_OWNER_PER_GAP_FAMILY",
        "touched_gap_ids": touched,
        "family_count": len(registry["items"]),
        "actionable_family_count": len(queue_items),
        "items": queue_items,
        "rules": [
            "GitHub issues represent bounded work owners; repeated evidence observations remain ledger rows under the same family.",
            "BACKFILL_QUEUED may execute only through allowlisted source capability contracts.",
            "PROSPECTIVE_CAPTURE_REQUIRED preserves past unknowns and starts future collection only through normal implementation/CI gates.",
            "SOURCE_DISCOVERY_REQUIRED is a research task, not permission to scrape or self-promote a source.",
            "Legacy gap IDs are retained as provenance and never create parallel owner issues after family migration.",
        ],
    }
    args.queue.parent.mkdir(parents=True, exist_ok=True)
    args.queue.write_bytes(canonical_bytes(queue_doc))
    print(json.dumps({
        "status": "PASS",
        "touched": len(touched),
        "registry_families": len(registry["items"]),
        "queue_families": len(queue_items),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
