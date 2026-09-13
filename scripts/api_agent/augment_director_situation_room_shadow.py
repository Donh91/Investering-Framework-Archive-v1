#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

DEFAULT_POINTER = Path("04_MARKET_LEARNING/external_research/situation_room_shadow/LATEST.json")
AUTHORITY = "SHADOW_RESEARCH_ONLY_NON_CANONICAL"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _firewall_ok(pointer: dict[str, Any], row: dict[str, Any]) -> bool:
    if pointer.get("authority") != AUTHORITY or row.get("authority") != AUTHORITY:
        return False
    if pointer.get("canonical_effect") is True or pointer.get("portfolio_effect") is True:
        return False
    firewall = row.get("authority_firewall")
    if not isinstance(firewall, dict):
        return False
    for key in ("canonical_effect", "market_state_effect", "portfolio_effect", "topup_authority", "execution_authority"):
        if firewall.get(key) is not False:
            return False
    return True


def situation_room_shadow(pointer_path: Path) -> tuple[dict[str, Any], list[Path]]:
    if not pointer_path.exists():
        return ({
            "status": "UNAVAILABLE",
            "reason": "SITUATION_ROOM_SHADOW_POINTER_MISSING",
            "authority": AUTHORITY,
        }, [])
    try:
        pointer = load_json(pointer_path)
    except Exception as exc:
        return ({
            "status": "BLOCKED_INVALID_POINTER",
            "reason": type(exc).__name__,
            "authority": AUTHORITY,
        }, [pointer_path])

    source_path_raw = pointer.get("path")
    if not isinstance(source_path_raw, str) or not source_path_raw:
        return ({
            "status": "BLOCKED_INVALID_POINTER",
            "reason": "POINTER_PATH_MISSING",
            "authority": AUTHORITY,
        }, [pointer_path])
    source_path = Path(source_path_raw)
    if not source_path.exists():
        return ({
            "status": "UNAVAILABLE",
            "reason": "SITUATION_ROOM_SHADOW_ROW_MISSING",
            "authority": AUTHORITY,
            "source_path": source_path_raw,
        }, [pointer_path])
    try:
        row = load_json(source_path)
    except Exception as exc:
        return ({
            "status": "BLOCKED_INVALID_ROW",
            "reason": type(exc).__name__,
            "authority": AUTHORITY,
            "source_path": source_path_raw,
        }, [pointer_path, source_path])

    if not _firewall_ok(pointer, row):
        return ({
            "status": "BLOCKED_AUTHORITY_FIREWALL",
            "reason": "SITUATION_ROOM_SHADOW_AUTHORITY_INVARIANT_FAILED",
            "authority": AUTHORITY,
            "source_path": source_path_raw,
        }, [pointer_path, source_path])

    accepted_raw = row.get("verified_shadow_context") if isinstance(row.get("verified_shadow_context"), list) else []
    pending_raw = row.get("pending_verification") if isinstance(row.get("pending_verification"), list) else []
    accepted: list[dict[str, Any]] = []
    for item in accepted_raw:
        if not isinstance(item, dict):
            continue
        if item.get("shadow_admission") != "ACCEPTED_VERIFIED_CONTEXT":
            continue
        if item.get("verification_status") not in {"PRIMARY_EVENT_CORROBORATED", "PRIMARY_LINK_CORROBORATED"}:
            continue
        accepted.append({
            "shadow_id": item.get("shadow_id"),
            "title": item.get("title"),
            "event_time_utc": item.get("event_time_utc"),
            "verification_status": item.get("verification_status"),
            "verification_method": item.get("verification_method"),
            "match_score": item.get("match_score"),
            "shared_tokens": item.get("shared_tokens"),
            "primary_event_id": item.get("primary_event_id"),
            "primary_title": item.get("primary_title"),
            "primary_url": item.get("primary_url"),
        })

    pending_titles: list[str] = []
    for item in pending_raw:
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        if isinstance(title, str) and title:
            pending_titles.append(title)
        if len(pending_titles) >= 8:
            break

    return ({
        "status": "READY",
        "authority": AUTHORITY,
        "canonical_effect": False,
        "portfolio_effect": False,
        "observation_date_utc": row.get("observation_date_utc"),
        "bridge_status": row.get("status"),
        "verified_count": len(accepted),
        "pending_count": len(pending_raw),
        "verified_context": accepted[:12],
        "pending_titles_context_only": pending_titles,
        "instruction": (
            "Use verified_context only as corroborated Shadow/catalyst context. "
            "Pending items are discovery queue metadata, not evidence. "
            "Situation Room has no canonical, market-state, top-up, portfolio or execution authority."
        ),
    }, [pointer_path, source_path])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--pointer", type=Path, default=DEFAULT_POINTER)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    context = load_json(args.context)
    routed, paths = situation_room_shadow(args.pointer)
    context["situation_room_shadow"] = routed
    context["situation_room_shadow_provenance"] = [
        {"path": str(path), "sha256": sha256(path)} for path in paths if path.exists()
    ]

    routing = context.setdefault("context_routing_contract", {})
    families = routing.setdefault("required_context_families", [])
    if isinstance(families, list) and "situation_room_shadow" not in families:
        families.append("situation_room_shadow")
    routing["no_automatic_authority_promotion"] = True
    routing["situation_room_shadow_rule"] = (
        "VERIFIED_SHADOW_CONTEXT_MAY_INFORM_ANALYSIS_ONLY; PENDING_DISCOVERIES_ARE_NOT_EVIDENCE"
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(context, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": routed.get("status"),
        "verified_count": routed.get("verified_count", 0),
        "pending_count": routed.get("pending_count", 0),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
