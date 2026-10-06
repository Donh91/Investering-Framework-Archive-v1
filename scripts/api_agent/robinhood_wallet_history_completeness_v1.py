from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Callable

from scripts.api_agent.meme_alpha_blockscout import blockscout_get, normalize_address

CONTRACT = "ROBINHOOD_WALLET_HISTORY_COMPLETENESS_RECEIPT_v1"
ENDPOINTS = {
    "transactions": "/api/v2/addresses/{wallet}/transactions",
    "token_transfers": "/api/v2/addresses/{wallet}/token-transfers",
}
STATES = {
    "COMPLETE_WINDOW",
    "TRUNCATED_PAGE_CAP",
    "DATA_INSUFFICIENT",
    "DATA_CONFLICT",
    "SOURCE_ERROR",
}


def _parse_utc(value: Any) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("TIMESTAMP_REQUIRED")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return parsed.astimezone(timezone.utc)


def _stable_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()


def _item_identity(item: dict[str, Any]) -> str:
    tx = str(item.get("hash") or item.get("transaction_hash") or "")
    log_index = item.get("log_index")
    if tx:
        return tx.lower() if log_index is None else f"{tx.lower()}:{log_index}"
    return "sha256:" + _stable_hash(item)


def _scan_endpoint(
    *,
    endpoint_path: str,
    history_start_utc: str,
    cutoff_utc: str,
    max_pages: int,
    fetch_page: Callable[[str, dict[str, Any]], tuple[Any, dict[str, Any]]],
) -> dict[str, Any]:
    start = _parse_utc(history_start_utc)
    cutoff = _parse_utc(cutoff_utc)
    if start >= cutoff:
        raise ValueError("INVALID_HISTORY_WINDOW")
    if max_pages < 1 or max_pages > 100:
        raise ValueError("INVALID_MAX_PAGES")

    query: dict[str, Any] = {}
    seen_cursors: set[str] = set()
    seen_ids: set[str] = set()
    in_window_ids: list[str] = []
    page_receipts: list[dict[str, Any]] = []
    previous_oldest: datetime | None = None
    oldest_seen: datetime | None = None
    newest_seen: datetime | None = None
    reached_window_start = False

    for page_number in range(1, max_pages + 1):
        try:
            payload, health = fetch_page(endpoint_path, query)
        except Exception as exc:
            return {
                "state": "SOURCE_ERROR",
                "pages_fetched": page_number - 1,
                "items_seen": len(seen_ids),
                "in_window_items": len(in_window_ids),
                "error_class": type(exc).__name__,
                "page_receipts": page_receipts,
            }

        if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
            return {
                "state": "DATA_INSUFFICIENT",
                "pages_fetched": page_number,
                "items_seen": len(seen_ids),
                "in_window_items": len(in_window_ids),
                "reason": "ITEMS_ARRAY_MISSING",
                "page_receipts": page_receipts,
            }

        timestamps: list[datetime] = []
        page_new = 0
        page_in_window = 0
        for item in payload["items"]:
            if not isinstance(item, dict) or not item.get("timestamp"):
                return {
                    "state": "DATA_INSUFFICIENT",
                    "pages_fetched": page_number,
                    "items_seen": len(seen_ids),
                    "in_window_items": len(in_window_ids),
                    "reason": "TIMESTAMP_MISSING",
                    "page_receipts": page_receipts,
                }
            try:
                ts = _parse_utc(item["timestamp"])
            except ValueError:
                return {
                    "state": "DATA_INSUFFICIENT",
                    "pages_fetched": page_number,
                    "items_seen": len(seen_ids),
                    "in_window_items": len(in_window_ids),
                    "reason": "TIMESTAMP_INVALID",
                    "page_receipts": page_receipts,
                }
            timestamps.append(ts)
            identity = _item_identity(item)
            if identity not in seen_ids:
                seen_ids.add(identity)
                page_new += 1
                if start <= ts <= cutoff:
                    in_window_ids.append(identity)
                    page_in_window += 1

        if any(timestamps[i] < timestamps[i + 1] for i in range(len(timestamps) - 1)):
            return {
                "state": "DATA_CONFLICT",
                "pages_fetched": page_number,
                "items_seen": len(seen_ids),
                "in_window_items": len(in_window_ids),
                "reason": "PAGE_NOT_DESCENDING_BY_TIMESTAMP",
                "page_receipts": page_receipts,
            }

        page_newest = max(timestamps) if timestamps else None
        page_oldest = min(timestamps) if timestamps else None
        if previous_oldest is not None and page_newest is not None and page_newest > previous_oldest:
            return {
                "state": "DATA_CONFLICT",
                "pages_fetched": page_number,
                "items_seen": len(seen_ids),
                "in_window_items": len(in_window_ids),
                "reason": "PAGINATION_TIME_REVERSAL",
                "page_receipts": page_receipts,
            }
        if page_oldest is not None:
            previous_oldest = page_oldest
            oldest_seen = page_oldest if oldest_seen is None else min(oldest_seen, page_oldest)
            newest_seen = page_newest if newest_seen is None else max(newest_seen, page_newest)
            if page_oldest <= start:
                reached_window_start = True

        next_params = payload.get("next_page_params")
        if next_params is not None and not isinstance(next_params, dict):
            return {
                "state": "DATA_INSUFFICIENT",
                "pages_fetched": page_number,
                "items_seen": len(seen_ids),
                "in_window_items": len(in_window_ids),
                "reason": "NEXT_PAGE_PARAMS_INVALID",
                "page_receipts": page_receipts,
            }

        page_receipts.append({
            "page": page_number,
            "new_items": page_new,
            "in_window_items": page_in_window,
            "newest_utc": page_newest.isoformat().replace("+00:00", "Z") if page_newest else None,
            "oldest_utc": page_oldest.isoformat().replace("+00:00", "Z") if page_oldest else None,
            "transport": health.get("transport") if isinstance(health, dict) else None,
            "authenticated": health.get("authenticated") if isinstance(health, dict) else None,
            "fallback_used": health.get("fallback_used") if isinstance(health, dict) else None,
            "next_page_present": bool(next_params),
        })

        if reached_window_start or not next_params:
            return {
                "state": "COMPLETE_WINDOW",
                "completion_basis": "REACHED_WINDOW_START" if reached_window_start else "PAGINATION_EXHAUSTED",
                "pages_fetched": page_number,
                "items_seen": len(seen_ids),
                "in_window_items": len(in_window_ids),
                "newest_seen_utc": newest_seen.isoformat().replace("+00:00", "Z") if newest_seen else None,
                "oldest_seen_utc": oldest_seen.isoformat().replace("+00:00", "Z") if oldest_seen else None,
                "page_receipts": page_receipts,
            }

        cursor_key = json.dumps(next_params, sort_keys=True, separators=(",", ":"))
        if cursor_key in seen_cursors:
            return {
                "state": "DATA_CONFLICT",
                "pages_fetched": page_number,
                "items_seen": len(seen_ids),
                "in_window_items": len(in_window_ids),
                "reason": "REPEATED_CURSOR",
                "page_receipts": page_receipts,
            }
        seen_cursors.add(cursor_key)
        query = dict(next_params)

    return {
        "state": "TRUNCATED_PAGE_CAP",
        "pages_fetched": max_pages,
        "items_seen": len(seen_ids),
        "in_window_items": len(in_window_ids),
        "newest_seen_utc": newest_seen.isoformat().replace("+00:00", "Z") if newest_seen else None,
        "oldest_seen_utc": oldest_seen.isoformat().replace("+00:00", "Z") if oldest_seen else None,
        "page_receipts": page_receipts,
    }


def audit_robinhood_wallet_history(
    wallet: str,
    *,
    history_start_utc: str,
    cutoff_utc: str,
    max_pages_per_endpoint: int = 20,
    api_key: str | None = None,
    allow_public_fallback: bool = True,
    fetcher=blockscout_get,
) -> dict[str, Any]:
    normalized = normalize_address(wallet)
    if normalized is None:
        raise ValueError("INVALID_EVM_ADDRESS")
    _parse_utc(history_start_utc)
    _parse_utc(cutoff_utc)

    def fetch_page(endpoint_path: str, query: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
        return fetcher(
            endpoint_path,
            api_key=api_key,
            query=query,
            allow_public_fallback=allow_public_fallback,
        )

    surfaces: dict[str, Any] = {}
    for name, template in ENDPOINTS.items():
        surfaces[name] = _scan_endpoint(
            endpoint_path=template.format(wallet=normalized),
            history_start_utc=history_start_utc,
            cutoff_utc=cutoff_utc,
            max_pages=max_pages_per_endpoint,
            fetch_page=fetch_page,
        )

    states = {surface["state"] for surface in surfaces.values()}
    if states == {"COMPLETE_WINDOW"}:
        overall = "COMPLETE_WINDOW"
    elif "SOURCE_ERROR" in states:
        overall = "SOURCE_ERROR"
    elif "DATA_CONFLICT" in states:
        overall = "DATA_CONFLICT"
    elif "DATA_INSUFFICIENT" in states:
        overall = "DATA_INSUFFICIENT"
    else:
        overall = "TRUNCATED_PAGE_CAP"

    receipt = {
        "contract": CONTRACT,
        "status": "RESEARCH_ONLY",
        "chain": "robinhood-chain",
        "chain_id": 4663,
        "wallet": normalized,
        "history_start_utc": history_start_utc,
        "cutoff_utc": cutoff_utc,
        "max_pages_per_endpoint": max_pages_per_endpoint,
        "coverage_state": overall,
        "surfaces": surfaces,
        "negative_activity_claim_admissible": overall == "COMPLETE_WINDOW",
        "downstream_incomplete_state": "UNKNOWN" if overall != "COMPLETE_WINDOW" else None,
        "authority": {
            "automatic_trading": False,
            "portfolio_action": False,
            "buy_now_promotion": False,
            "alert_authority": False,
        },
    }
    receipt["receipt_sha256"] = _stable_hash(receipt)
    return receipt
