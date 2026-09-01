from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from scripts.data_terminal import situation_room_daily_owner as owner


SITUATION_ROOM_ARCHIVE = "https://situationroom.space/briefings"
SITUATION_ROOM_DAILY_PREFIX = "https://situationroom.space/briefing/"
BASE_CANDIDATE_LINKS = owner.candidate_links


def daily_briefing_url(date_utc: str) -> str:
    return f"{SITUATION_ROOM_DAILY_PREFIX}{date_utc}"


def sources_for_date(date_utc: str):
    daily_url = daily_briefing_url(date_utc)
    return tuple(
        (source_id, role, daily_url if source_id == "SITUATION_ROOM" else url)
        for source_id, role, url in owner.SOURCES
    )


def direct_daily_candidate_links(source_id: str, base_url: str, parser):
    """Yield the deterministic daily briefing itself, then preserve v1 behavior elsewhere."""
    if source_id == "SITUATION_ROOM":
        parsed = urlparse(base_url)
        if parsed.netloc == "situationroom.space" and parsed.path.startswith("/briefing/"):
            title = parser.title or f"Situation Room daily briefing {parsed.path.rsplit('/', 1)[-1]}"
            yield base_url, title
            return
    yield from BASE_CANDIDATE_LINKS(source_id, base_url, parser)


def apply_dated_discovery_fail_closed(result: dict, date_utc: str) -> None:
    """A dated Situation Room page is today's discovery even if HTML lacks a timestamp.

    The URL date is used only to establish discovery scope. It is never promoted to a
    precise event_time_utc and never verifies the event. This prevents a client/metadata
    limitation from being silently converted into NO_NEW_MATERIAL_CATALYST.
    """
    expected_url = daily_briefing_url(date_utc)
    rows = [
        item for item in result.get("unverified_discoveries", [])
        if item.get("verification_status") == "DISCOVERY_UNVERIFIED"
        and item.get("url") == expected_url
    ]
    if not rows:
        return
    current = result.setdefault("current_unverified_discoveries", [])
    known = {item.get("url") for item in current}
    for item in rows:
        if item.get("url") not in known:
            item["discovery_date_basis"] = "DETERMINISTIC_DATED_SOURCE_URL"
            current.append(item)
            known.add(item.get("url"))
    if result.get("daily_result") == "NO_NEW_MATERIAL_CATALYST":
        result["daily_result"] = "REVIEW_REQUIRED_UNVERIFIED_DISCOVERY"
        result["run_status"] = "DEGRADED"


def apply_situation_room_retrieval_fail_closed(result: dict) -> None:
    """Do not turn an unavailable Situation Room briefing into a clean no-event result."""
    situation_room_receipt = next(
        (
            receipt
            for receipt in result.get("source_coverage", {}).get("receipts", [])
            if receipt.get("source_id") == "SITUATION_ROOM"
        ),
        None,
    )
    if (
        result.get("daily_result") == "NO_NEW_MATERIAL_CATALYST"
        and situation_room_receipt is not None
        and situation_room_receipt.get("status") != "PASS"
    ):
        result["daily_result"] = "REVIEW_REQUIRED_UNVERIFIED_DISCOVERY"
        result["run_status"] = "DEGRADED"


def run(output_root: Path, date_utc: str, timeout: int = 15) -> dict:
    original_sources = owner.SOURCES
    original_candidate_links = owner.candidate_links
    try:
        owner.SOURCES = sources_for_date(date_utc)
        owner.candidate_links = direct_daily_candidate_links
        result = owner.run(output_root, date_utc, timeout=timeout)
    finally:
        owner.SOURCES = original_sources
        owner.candidate_links = original_candidate_links

    apply_dated_discovery_fail_closed(result, date_utc)
    apply_situation_room_retrieval_fail_closed(result)
    result.setdefault("retrieval", {})
    result["retrieval"].update({
        "situation_room_archive_url": SITUATION_ROOM_ARCHIVE,
        "situation_room_daily_url": daily_briefing_url(date_utc),
        "strategy": "DETERMINISTIC_STATIC_DAILY_BRIEFING",
        "dynamic_archive_shell_not_required": True,
    })
    owner.write_outputs(output_root, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room"),
    )
    parser.add_argument("--date-utc", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()

    result = run(args.output_root, args.date_utc, timeout=args.timeout)
    print(json.dumps({
        "run_id": result["run_id"],
        "daily_result": result["daily_result"],
        "run_status": result["run_status"],
        "situation_room_daily_url": daily_briefing_url(args.date_utc),
    }, sort_keys=True))

    if result["daily_result"] == "COLLECTOR_FAILURE":
        raise SystemExit(2)
    if result["daily_result"] in {
        "UNKNOWN_DUE_TO_SOURCE_FAILURE",
        "REVIEW_REQUIRED_UNRESOLVED_CANDIDATES",
        "REVIEW_REQUIRED_UNVERIFIED_DISCOVERY",
    }:
        raise SystemExit(78)


if __name__ == "__main__":
    main()
