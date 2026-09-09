from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Current Live Point-in-Time Anchor owner contract is a 4-hour tactical cadence.
# This is not a new market rule or tolerance. It prevents the Director freshness
# gate from treating an unseen identity as proof that old source evidence is fresh.
OWNER_CAPTURE_CADENCE = timedelta(hours=4)


def context_capture(path: Path) -> tuple[str | None, object]:
    try:
        value = json.loads(path.read_text())
    except Exception:
        return None, None
    latest = value.get("latest_capture") if isinstance(value.get("latest_capture"), dict) else {}
    run_id = latest.get("run_id")
    return (str(run_id) if run_id else None), latest.get("captured_at_utc")


def parse_source_timestamp(raw: object) -> datetime | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if value.utcoffset() is None:
        return None
    return value.astimezone(timezone.utc)


def evaluate(context: Path, output_root: Path, now: datetime | None = None) -> dict[str, object]:
    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    current_run_id, source_raw = context_capture(context)
    if not current_run_id:
        return {"fresh_ready": False, "fresh_reason": "CURRENT_RUN_ID_MISSING"}

    source_timestamp = parse_source_timestamp(source_raw)
    if source_timestamp is None:
        return {
            "fresh_ready": False,
            "fresh_reason": "CURRENT_CAPTURE_TIMESTAMP_INVALID_OR_MISSING",
            "current_run_id": current_run_id,
            "source_timestamp_valid": False,
        }

    age_seconds = (now - source_timestamp).total_seconds()
    diagnostics: dict[str, object] = {
        "current_run_id": current_run_id,
        "source_timestamp_valid": True,
        "source_timestamp_utc": source_timestamp.isoformat().replace("+00:00", "Z"),
        "source_age_seconds": round(age_seconds, 3),
        "owner_capture_cadence_seconds": int(OWNER_CAPTURE_CADENCE.total_seconds()),
    }
    if age_seconds < 0:
        return {**diagnostics, "fresh_ready": False, "fresh_reason": "CURRENT_CAPTURE_TIMESTAMP_FUTURE"}
    if age_seconds > OWNER_CAPTURE_CADENCE.total_seconds():
        return {**diagnostics, "fresh_ready": False, "fresh_reason": "CURRENT_CAPTURE_SOURCE_STALE"}

    seen: set[str] = set()
    if output_root.exists():
        for path in output_root.rglob("context.json"):
            run_id, _ = context_capture(path)
            if run_id:
                seen.add(run_id)
    unseen = current_run_id not in seen
    return {
        **diagnostics,
        "identity_unseen": unseen,
        "fresh_ready": unseen,
        "fresh_reason": "NEW_OWNER_RUN_FRESH_SOURCE" if unseen else "OWNER_RUN_ALREADY_ANALYZED",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--now-utc", help="Deterministic test/replay clock; defaults to current UTC time.")
    args = parser.parse_args()

    now = parse_source_timestamp(args.now_utc) if args.now_utc else None
    if args.now_utc and now is None:
        raise SystemExit("invalid_now_utc")
    result = evaluate(args.context, args.output_root, now)
    for key in (
        "fresh_ready",
        "fresh_reason",
        "current_run_id",
        "identity_unseen",
        "source_timestamp_valid",
        "source_timestamp_utc",
        "source_age_seconds",
        "owner_capture_cadence_seconds",
    ):
        if key not in result:
            continue
        value = result[key]
        if isinstance(value, bool):
            value = "true" if value else "false"
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
