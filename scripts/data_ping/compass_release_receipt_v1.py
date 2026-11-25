#!/usr/bin/env python3
"""Release receipt for the descriptive Compass fields (the fourth fact: consumer delivery).

The producer never claims delivery. This read-only classifier turns four OBSERVED readbacks into one state, so
"merged" is never reported as "served" and "served" is never reported as "seen". It makes no network call and
writes nothing: each input is a file or a value that a person or an agent already read back natively.

  NOT_MERGED               no squash commit was read back
  MERGED_NOT_EMITTED       merged, but the newest naturally issued official packet lacks the fields
  MERGED_BUT_NOT_SERVED    a valid packet carries the fields, but the served bundle does not carry that packet's fields
  SERVED_NOT_USER_VISIBLE  the served bundle carries them, but no browser readback at both widths exists
  USER_VISIBLE             all four receipts were observed
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "COMPASS_DESCRIPTIVE_RELEASE_RECEIPT_v1"
FIELDS = ("source_freshness", "cn_band_status", "risk_freshness")
REQUIRED_WIDTHS = (390, 1280)


def _carries_fields(packet: Any) -> bool:
    return isinstance(packet, Mapping) and all(
        isinstance(packet.get(key), Mapping) and isinstance(packet[key].get("contract"), str) for key in FIELDS
    )


def classify(
    *,
    merged_squash_sha: str | None,
    emitted_packet: Mapping[str, Any] | None,
    served_packet: Mapping[str, Any] | None,
    browser_readback_widths: tuple[int, ...] = (),
) -> dict[str, Any]:
    merged = isinstance(merged_squash_sha, str) and len(merged_squash_sha) == 40
    emitted = merged and _carries_fields(emitted_packet) and int((emitted_packet or {}).get("schema_version") or 0) >= 5
    served = bool(
        emitted and _carries_fields(served_packet)
        and served_packet.get("compass_id") == emitted_packet.get("compass_id")
        and all(served_packet[key].get("status", served_packet[key].get("forecast_floor_status"))
                == emitted_packet[key].get("status", emitted_packet[key].get("forecast_floor_status")) for key in FIELDS)
    )
    visible = served and all(width in browser_readback_widths for width in REQUIRED_WIDTHS)
    if not merged:
        state = "NOT_MERGED"
    elif not emitted:
        state = "MERGED_NOT_EMITTED"
    elif not served:
        state = "MERGED_BUT_NOT_SERVED"
    elif not visible:
        state = "SERVED_NOT_USER_VISIBLE"
    else:
        state = "USER_VISIBLE"
    return {
        "contract": CONTRACT,
        "state": state,
        "receipts": {"merged": merged, "producer_emitted": bool(emitted), "pages_served": served, "user_visible": bool(visible)},
        "compass_id": (emitted_packet or {}).get("compass_id") if emitted else None,
        "authority": "OBSERVED_READBACK_ONLY_NO_DELIVERY_CLAIM_WITHOUT_EVIDENCE",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--merged-squash-sha")
    parser.add_argument("--emitted-packet", type=Path)
    parser.add_argument("--served-packet", type=Path)
    parser.add_argument("--browser-width", type=int, action="append", default=[])
    args = parser.parse_args()
    load = lambda path: json.loads(path.read_text()) if path and path.exists() else None  # noqa: E731
    print(json.dumps(classify(
        merged_squash_sha=args.merged_squash_sha,
        emitted_packet=load(args.emitted_packet),
        served_packet=load(args.served_packet),
        browser_readback_widths=tuple(args.browser_width),
    ), sort_keys=True))


if __name__ == "__main__":
    main()
