#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.request
from datetime import datetime, timezone
from typing import Any

CONTRACT = "COINMETRICS_COMMUNITY_RESEARCH_PROBE_v0_2"
URL_TEMPLATE = "https://raw.githubusercontent.com/coinmetrics/data/{ref}/csv/btc.csv"
UA = {"User-Agent": "Investering-Research-Source-Probe/0.2", "Accept": "text/csv"}
REQUIRED_FIELDS = ("time", "PriceUSD", "CapMVRVCur")
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$")
AUTHORITY = {
    "binding": False,
    "canonical_acceptance": False,
    "state_change": False,
    "portfolio_action": False,
    "automatic_promotion": False,
}


class ProbeError(ValueError):
    pass


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as response:
        raw = response.read()
        status = getattr(response, "status", 200)
        if status != 200:
            raise ProbeError(f"http_status_{status}")
        if not raw:
            raise ProbeError("empty_payload")
        return raw


def summarize_csv(raw: bytes, source_ref: str) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ProbeError("non_utf8_csv") from exc
    reader = csv.DictReader(io.StringIO(text))
    fields = reader.fieldnames or []
    if "time" not in fields:
        raise ProbeError("missing_time_field")

    rows = 0
    earliest = None
    latest = None
    non_null = {key: 0 for key in REQUIRED_FIELDS if key in fields}
    for row in reader:
        day = (row.get("time") or "").strip()
        if not day:
            continue
        rows += 1
        earliest = day if earliest is None or day < earliest else earliest
        latest = day if latest is None or day > latest else latest
        for key in non_null:
            if (row.get(key) or "").strip():
                non_null[key] += 1
    if rows == 0:
        raise ProbeError("no_rows")

    immutable = bool(COMMIT_SHA.fullmatch(source_ref))
    return {
        "contract": CONTRACT,
        "source": "COIN_METRICS_COMMUNITY_GITHUB_ARCHIVE",
        "source_ref": source_ref,
        "source_ref_immutable_commit": immutable,
        "source_ref_evidence_eligible": immutable,
        "payload_sha256": sha256(raw),
        "payload_bytes": len(raw),
        "row_count": rows,
        "earliest_date": earliest,
        "latest_date": latest,
        "field_count": len(fields),
        "required_field_presence": {key: key in fields for key in REQUIRED_FIELDS},
        "non_null_counts": non_null,
        "raw_persisted": False,
        "authority": AUTHORITY,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Coin Metrics Community immutable-source research probe.")
    parser.add_argument("--ref", required=True, help="Evidence runs require an immutable 40-char Git commit SHA.")
    args = parser.parse_args()
    if not COMMIT_SHA.fullmatch(args.ref):
        raise SystemExit("FAIL evidence_ref_must_be_40_char_commit_sha")
    url = URL_TEMPLATE.format(ref=args.ref)
    receipt = summarize_csv(fetch_bytes(url), args.ref)
    receipt["url"] = url
    receipt["retrieved_at_utc"] = now_utc()
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
