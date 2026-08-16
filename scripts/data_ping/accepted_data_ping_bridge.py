from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED = {"snapshot_id", "freeze_utc", "source_health", "market_metrics", "framework_interpretation", "acceptance_status"}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate(value: dict[str, Any]) -> None:
    if value.get("contract") != "ACCEPTED_DATA_PING_PACKET_v1":
        raise ValueError("wrong_contract")
    missing = sorted(REQUIRED - set(value))
    if missing:
        raise ValueError("missing:" + ",".join(missing))
    if value["acceptance_status"] != "ACCEPTED":
        raise ValueError("not_accepted")
    if not isinstance(value["source_health"], dict) or not isinstance(value["market_metrics"], dict):
        raise ValueError("invalid_owner_payload")
    forbidden = {"portfolio_action", "model_weight_change", "canonical_promotion"}
    authority = value.get("authority", {})
    if any(authority.get(key) is True for key in forbidden):
        raise ValueError("forbidden_authority")


def immutable_packet(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "bridge_receipt"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", type=Path, required=True)
    ap.add_argument("--accepted-root", type=Path, required=True)
    ap.add_argument("--rejected-root", type=Path, required=True)
    ap.add_argument("--processed-root", type=Path)
    ap.add_argument("--run-id", default="manual")
    args = ap.parse_args()
    processed_root = args.processed_root or args.inbox.parent / "processed"
    accepted = rejected = replayed = 0

    for path in sorted(args.inbox.glob("*.json")):
        try:
            raw_value = json.loads(path.read_text())
            validate(raw_value)
            packet = immutable_packet(raw_value)
            packet_hash = sha(packet)
            freeze = datetime.fromisoformat(packet["freeze_utc"].replace("Z", "+00:00"))
            iso = freeze.isocalendar()
            destination = args.accepted_root / str(iso.year) / f"W{iso.week:02d}" / f"{packet['snapshot_id']}.json"
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                existing = json.loads(destination.read_text())
                existing_packet = immutable_packet(existing)
                if sha(existing_packet) != packet_hash:
                    raise ValueError("snapshot_id_collision")
                replayed += 1
            else:
                acceptance_time = utc_now()
                stored = dict(packet)
                stored["bridge_receipt"] = {
                    "contract": "DATA_PING_BRIDGE_RECEIPT_v2",
                    # Legacy storage-time field retained for compatibility. It is
                    # not promoted to framework_ingest_time without a separate
                    # receipt proving that earlier lifecycle transition.
                    "ingested_at_utc": acceptance_time,
                    "ingested_at_semantics": "IMMUTABLE_ACCEPTED_STORAGE_EVENT_NOT_FRAMEWORK_INGEST_LIFECYCLE_TIME",
                    "framework_ingest_time": None,
                    "framework_ingest_status": "UNAVAILABLE",
                    "framework_acceptance_time": acceptance_time,
                    "framework_acceptance_status": "KNOWN",
                    "acceptance_event": "ACCEPTED_DATA_PING_PACKET_v1 validated and immutably stored",
                    "acceptance_run_id": args.run_id,
                    "source_filename": path.name,
                    "packet_sha256": packet_hash,
                    "immutable": True,
                    "policy_evaluable_time": None,
                    "policy_evaluable_status": "UNAVAILABLE",
                    "decision_evaluation_time": None,
                    "decision_evaluation_status": "UNAVAILABLE",
                    "action_divergence_time": None,
                    "action_divergence_status": "UNAVAILABLE",
                    "framework_ingest_not_inferred": True,
                    "no_policy_evaluability_inferred": True,
                    "no_decision_evaluation_inferred": True,
                }
                destination.write_bytes(canonical(stored))
                accepted += 1
            processed_root.mkdir(parents=True, exist_ok=True)
            processed_name = f"{packet['snapshot_id']}__{packet_hash[:12]}.json"
            processed_path = processed_root / processed_name
            if not processed_path.exists():
                shutil.move(str(path), str(processed_path))
            else:
                path.unlink()
        except Exception as exc:
            args.rejected_root.mkdir(parents=True, exist_ok=True)
            error_name = f"{path.stem}__{args.run_id}__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.error.json"
            (args.rejected_root / error_name).write_text(json.dumps({"source": str(path), "error": str(exc)}, sort_keys=True) + "\n")
            rejected += 1

    print(json.dumps({"accepted": accepted, "replayed": replayed, "rejected": rejected}, sort_keys=True))
    if rejected:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
