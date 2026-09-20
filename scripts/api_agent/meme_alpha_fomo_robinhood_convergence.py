from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

ELIGIBLE = "ELIGIBLE_CONVERGENCE_FROZEN"


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def parse_ts(value: Any) -> datetime | None:
    if not isinstance(value, str) or value in {"", "UNKNOWN"}:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo is not None else None


def eligible_receipt(row: dict[str, Any]) -> bool:
    return (
        row.get("contract") == "FOMO_ROBINHOOD_OBSERVER_RECEIPT_v1"
        and row.get("state") == "PROVENANCE_PASS"
        and row.get("provenance_independently_reproduced") is True
        and row.get("sellability_state") == "PASS"
        and row.get("economic_entity_id_or_PENDING") not in {None, "", "PENDING", "UNKNOWN"}
        and parse_ts(row.get("observed_at_utc_exact")) is not None
        and isinstance(row.get("token_ca"), str)
    )


def aggregate(batch: dict[str, Any], *, window_minutes: int = 60) -> dict[str, Any]:
    receipts = batch.get("receipts") if isinstance(batch, dict) else None
    if not isinstance(receipts, list):
        raise ValueError("receipts_must_be_list")
    if window_minutes <= 0:
        raise ValueError("window_minutes_must_be_positive")

    groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    rejected = 0
    for row in receipts:
        if not isinstance(row, dict) or not eligible_receipt(row):
            rejected += 1
            continue
        key = (str(row.get("chain") or "robinhood"), str(row["token_ca"]).lower())
        groups.setdefault(key, []).append(row)

    events: list[dict[str, Any]] = []
    for (chain, token), rows in sorted(groups.items()):
        rows.sort(key=lambda r: (parse_ts(r["observed_at_utc_exact"]), str(r.get("observation_id"))))
        for i, first in enumerate(rows):
            start = parse_ts(first["observed_at_utc_exact"])
            assert start is not None
            in_window = []
            for row in rows[i:]:
                ts = parse_ts(row["observed_at_utc_exact"])
                assert ts is not None
                if (ts - start).total_seconds() > window_minutes * 60:
                    break
                in_window.append(row)
            entities: dict[str, dict[str, Any]] = {}
            for row in in_window:
                entity = str(row["economic_entity_id_or_PENDING"])
                current = entities.get(entity)
                if current is None or parse_ts(row["observed_at_utc_exact"]) < parse_ts(current["observed_at_utc_exact"]):
                    entities[entity] = row
            if len(entities) < 2:
                continue
            chosen = sorted(entities.values(), key=lambda r: (parse_ts(r["observed_at_utc_exact"]), str(r.get("observation_id"))))
            entity_ids = sorted(entities)
            observation_ids = sorted(str(r.get("observation_id")) for r in chosen)
            identity = {"chain": chain, "token_ca": token, "entity_ids": entity_ids, "observation_ids": observation_ids}
            first_seen = min(parse_ts(r["observed_at_utc_exact"]) for r in chosen)
            last_seen = max(parse_ts(r["observed_at_utc_exact"]) for r in chosen)
            events.append({
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
                "window_minutes": window_minutes,
                "promotion_counter_eligible": True,
                "promotion_counter_increment": 1,
                "authority": {"buy": False, "sell": False, "copy_trade": False, "portfolio_action": False},
            })
            break

    return {
        "contract": "FOMO_ROBINHOOD_CONVERGENCE_BATCH_v1",
        "source_contract": batch.get("contract") if isinstance(batch, dict) else None,
        "eligible_convergences": events,
        "eligible_convergence_count": len(events),
        "rejected_or_pending_receipt_count": rejected,
        "promotion_counter_increment": len(events),
        "authority": {"buy": False, "sell": False, "copy_trade": False, "portfolio_action": False},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Independent-entity convergence over fail-closed FOMO/RH receipts.")
    parser.add_argument("--receipts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--window-minutes", type=int, default=60)
    args = parser.parse_args()
    payload = aggregate(json.loads(args.receipts.read_text()), window_minutes=args.window_minutes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canon(payload))
    print(json.dumps({"eligible_convergences": payload["eligible_convergence_count"], "promotion_counter_increment": payload["promotion_counter_increment"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
