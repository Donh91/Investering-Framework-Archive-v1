from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

if __package__:
    from . import meme_alpha_fomo_robinhood_observer as observer
else:
    import meme_alpha_fomo_robinhood_observer as observer

ELIGIBLE = "ELIGIBLE_CONVERGENCE_FROZEN"
FROZEN_WINDOWS = (15, 30, 60, 180)


def canon(value: Any) -> bytes:
    return observer.canon(value)


def parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    normalized = observer.iso_exact(value)
    return datetime.fromisoformat(normalized.replace("Z", "+00:00")) if normalized else None


def eligible_receipt(row: dict[str, Any]) -> bool:
    return (
        isinstance(row, dict)
        and row.get("state") == "PROVENANCE_PASS"
        and row.get("provenance_class") == "PROVENANCE_PASS"
        and observer.receipt_state(row) == "PROVENANCE_PASS"
    )


def window_event(chain: str, token: str, rows: list[dict[str, Any]], minutes: int) -> dict[str, Any] | None:
    for i, first in enumerate(rows):
        start = parse_ts(first["observed_at_utc_exact"])
        assert start is not None
        entities: dict[str, dict[str, Any]] = {}
        for row in rows[i:]:
            ts = parse_ts(row["observed_at_utc_exact"])
            assert ts is not None
            if (ts - start).total_seconds() > minutes * 60:
                break
            entities.setdefault(str(row["economic_entity_id_or_PENDING"]), row)
        if len(entities) < 2:
            continue
        chosen = list(entities.values())
        entity_ids = sorted(entities)
        observation_ids = sorted(str(row["observation_id"]) for row in chosen)
        identity = {"chain": chain, "token_ca": token, "entity_ids": entity_ids, "observation_ids": observation_ids}
        first_seen = min(parse_ts(row["observed_at_utc_exact"]) for row in chosen)
        last_seen = max(parse_ts(row["observed_at_utc_exact"]) for row in chosen)
        assert first_seen is not None and last_seen is not None
        return {
            "contract": "FOMO_ROBINHOOD_INDEPENDENT_CONVERGENCE_v1",
            "convergence_id": "FOMO-CONV-" + hashlib.sha256(canon(identity)).hexdigest()[:20],
            "state": ELIGIBLE,
            "chain": chain,
            "token_ca": token,
            "independent_entity_count": len(entity_ids),
            "economic_entity_ids": entity_ids,
            "observation_ids": observation_ids,
            "first_seen_at_utc": first_seen.isoformat().replace("+00:00", "Z"),
            "convergence_at_utc": last_seen.isoformat().replace("+00:00", "Z"),
            "window_minutes": minutes,
            "promotion_counter_eligible": True,
            "promotion_counter_increment": 0,
            "authority": observer.authority(),
        }
    return None


def aggregate(batch: dict[str, Any], *, window_minutes: int | None = None) -> dict[str, Any]:
    receipts = batch.get("receipts") if isinstance(batch, dict) else None
    if not isinstance(receipts, list):
        raise ValueError("receipts_must_be_list")
    if window_minutes is not None and (type(window_minutes) is not int or window_minutes not in FROZEN_WINDOWS):
        raise ValueError("window_minutes_must_be_frozen")
    windows = FROZEN_WINDOWS if window_minutes is None else (window_minutes,)

    by_id: dict[str, list[dict[str, Any]]] = {}
    rejected = 0
    for row in receipts:
        if not isinstance(row, dict) or not observer.evidence_text(row.get("observation_id")):
            rejected += 1
            continue
        by_id.setdefault(str(row["observation_id"]), []).append(row)

    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    duplicate_count = 0
    for variants in by_id.values():
        if len({canon(row) for row in variants}) != 1:
            rejected += len(variants)
            continue
        row = variants[0]
        if not eligible_receipt(row):
            rejected += len(variants)
            continue
        duplicate_count += len(variants) - 1
        groups.setdefault((str(row["chain"]), str(row["token_ca"]).lower()), []).append(row)

    for rows in groups.values():
        rows.sort(key=lambda row: (parse_ts(row["observed_at_utc_exact"]), str(row["observation_id"])))

    views: list[dict[str, Any]] = []
    representatives: dict[tuple[str, str], dict[str, Any]] = {}
    qualifying: dict[tuple[str, str], list[int]] = {}
    for minutes in windows:
        events = []
        for (chain, token), rows in sorted(groups.items()):
            event = window_event(chain, token, rows, minutes)
            if event is None:
                continue
            events.append(event)
            key = (chain, token)
            representatives.setdefault(key, event)
            qualifying.setdefault(key, []).append(minutes)
        views.append({"window_minutes": minutes, "eligible_convergences": events})

    events = [
        {**representatives[key], "qualifying_window_minutes": qualifying[key]}
        for key in sorted(representatives)
    ]
    return {
        "contract": "FOMO_ROBINHOOD_CONVERGENCE_BATCH_v1",
        "source_contract": batch.get("contract") if isinstance(batch, dict) else None,
        "evaluated_window_minutes": list(windows),
        "window_results": views,
        "eligible_convergences": events,
        "eligible_convergence_count": len(events),
        "unique_chain_token_count": len(events),
        "rejected_or_pending_receipt_count": rejected,
        "duplicate_receipt_count": duplicate_count,
        "promotion_counter_increment": 0,
        "authority": observer.authority(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Independent-entity convergence over fail-closed FOMO/RH receipts.")
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--window-minutes", type=int, choices=FROZEN_WINDOWS, default=None)
    args = parser.parse_args()
    payload = aggregate(json.loads(args.receipts.read_text()), window_minutes=args.window_minutes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canon(payload))
    print(json.dumps({"eligible_convergences": payload["eligible_convergence_count"], "promotion_counter_increment": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
