from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return text[:80] or "gap"


def gap_key(candidate: dict[str, Any]) -> str:
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", type=Path, required=True)
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--capabilities", type=Path, required=True)
    ap.add_argument("--queue", type=Path, required=True)
    args = ap.parse_args()

    audit = load_json(args.audit, {"candidates": []})
    capability_doc = load_json(args.capabilities, {"capabilities": {}})
    caps = capability_doc.get("capabilities") if isinstance(capability_doc.get("capabilities"), dict) else {}
    registry = load_json(args.registry, {
        "contract": "ADAPTIVE_EVIDENCE_GAP_REGISTRY_v1",
        "status": "ACTIVE_SHADOW_RESEARCH_ONLY",
        "items": {},
        "authority": {"market_rule_change": False, "canonical_state": False, "portfolio_action": False, "self_merge": False}
    })
    if not isinstance(registry.get("items"), dict):
        registry["items"] = {}

    timestamp = now_utc()
    touched: list[str] = []
    for candidate in audit.get("candidates", []):
        if not isinstance(candidate, dict) or not str(candidate.get("metric_name") or "").strip():
            continue
        key = gap_key(candidate)
        gap_id = f"EG-{slug(str(candidate['metric_name']))}-{key}"
        state, rationale = route(candidate, caps)
        previous = registry["items"].get(gap_id) if isinstance(registry["items"].get(gap_id), dict) else {}
        first_seen = previous.get("first_seen_utc") or timestamp
        count = int(previous.get("observation_count", 0) or 0) + 1
        item = {
            "gap_id": gap_id,
            "metric_name": candidate.get("metric_name"),
            "decision_relevance": candidate.get("decision_relevance"),
            "missing_history_problem": candidate.get("missing_history_problem"),
            "desired_history_days": candidate.get("desired_history_days"),
            "desired_cadence_minutes": candidate.get("desired_cadence_minutes"),
            "data_shape": candidate.get("data_shape"),
            "capability_hint": candidate.get("capability_hint"),
            "evidence_reference": candidate.get("evidence_reference"),
            "first_seen_utc": first_seen,
            "last_seen_utc": timestamp,
            "observation_count": count,
            "closure_state": previous.get("closure_state") if previous.get("closure_state") in {"ALREADY_COVERED", "CLOSED", "PROSPECTIVE_CAPTURE_ACTIVE"} else state,
            "routing_rationale": rationale,
            "authority": {"evidence_only": True, "market_semantics": False}
        }
        registry["items"][gap_id] = item
        touched.append(gap_id)

    registry["updated_at_utc"] = timestamp
    registry["item_count"] = len(registry["items"])
    args.registry.parent.mkdir(parents=True, exist_ok=True)
    args.registry.write_bytes(canonical_bytes(registry))

    actionable_states = {"BACKFILL_QUEUED", "PROSPECTIVE_CAPTURE_REQUIRED", "SOURCE_DISCOVERY_REQUIRED"}
    queue_items = [
        item for item in registry["items"].values()
        if isinstance(item, dict) and item.get("closure_state") in actionable_states
    ]
    queue_items.sort(key=lambda row: (-int(row.get("observation_count", 0)), str(row.get("first_seen_utc", "")), str(row.get("gap_id", ""))))
    queue_doc = {
        "contract": "ADAPTIVE_EVIDENCE_GAP_QUEUE_v1",
        "generated_at_utc": timestamp,
        "touched_gap_ids": touched,
        "items": queue_items,
        "rules": [
            "BACKFILL_QUEUED may execute only through allowlisted source capability contracts.",
            "PROSPECTIVE_CAPTURE_REQUIRED preserves past unknowns and starts future collection only through normal implementation/CI gates.",
            "SOURCE_DISCOVERY_REQUIRED is a research task, not permission to scrape or self-promote a source."
        ]
    }
    args.queue.parent.mkdir(parents=True, exist_ok=True)
    args.queue.write_bytes(canonical_bytes(queue_doc))
    print(json.dumps({"status": "PASS", "touched": len(touched), "registry_items": len(registry["items"]), "queue_items": len(queue_items)}, sort_keys=True))


if __name__ == "__main__":
    main()
