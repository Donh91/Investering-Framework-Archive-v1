#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

CONTRACT = "BGEOMETRICS_RESEARCH_PROBE_v0_2"
BASE = "https://bitcoin-data.com/v1"
ALLOWED_SERIES = ("mvrv", "sth-mvrv", "sopr", "vdd")
UA = {
    "User-Agent": "Investering-Research-Source-Probe/0.2",
    "Accept": "application/json",
}
AUTHORITY = {
    "binding": False,
    "canonical_acceptance": False,
    "state_change": False,
    "portfolio_action": False,
    "automatic_promotion": False,
}
PERSISTENCE = {
    "raw_public_persistence": False,
    "receipt_only": True,
    "reason": "provider_terms_restrict_raw_redistribution",
}


class ProbeError(ValueError):
    pass


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as response:
        raw = response.read()
        status = getattr(response, "status", 200)
        if status != 200:
            raise ProbeError(f"http_status_{status}")
        if not raw:
            raise ProbeError("empty_payload")
        return raw


def _date_value(row: dict[str, Any]) -> str | None:
    for key in ("d", "date", "time", "timestamp", "unixTs"):
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def summarize_series(raw: bytes, metric: str) -> dict[str, Any]:
    if metric not in ALLOWED_SERIES:
        raise ProbeError("metric_not_allowlisted")
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProbeError("invalid_json") from exc
    if not isinstance(doc, list) or not doc:
        raise ProbeError("empty_or_nonlist_payload")
    if not all(isinstance(row, dict) for row in doc):
        raise ProbeError("non_object_row")

    fields = sorted({str(key) for row in doc for key in row})
    dates = sorted(value for row in doc if (value := _date_value(row)) is not None)
    if not dates:
        raise ProbeError("no_dates")

    return {
        "contract": CONTRACT,
        "source": "BGEOMETRICS",
        "metric": metric,
        "payload_sha256": sha256(raw),
        "payload_bytes": len(raw),
        "row_count": len(doc),
        "earliest_observation": dates[0],
        "latest_observation": dates[-1],
        "field_names": fields,
        "raw_persisted": False,
        "persistence": PERSISTENCE,
        "authority": AUTHORITY,
    }


def build_url(metric: str, startday: str | None, endday: str | None) -> str:
    if metric not in ALLOWED_SERIES:
        raise ProbeError("metric_not_allowlisted")
    params: dict[str, str] = {}
    if startday:
        params["startday"] = startday
    if endday:
        params["endday"] = endday
    if bool(startday) != bool(endday):
        raise ProbeError("startday_and_endday_must_be_paired")
    url = f"{BASE}/{metric}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return url


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded research-only BGeometrics series probe.")
    parser.add_argument("--metric", choices=ALLOWED_SERIES, required=True)
    parser.add_argument("--startday", help="Inclusive YYYY-MM-DD research window start.")
    parser.add_argument("--endday", help="Inclusive YYYY-MM-DD research window end.")
    args = parser.parse_args()

    url = build_url(args.metric, args.startday, args.endday)
    receipt = summarize_series(fetch_bytes(url), args.metric)
    receipt["url"] = url
    receipt["retrieved_at_utc"] = now_utc()
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
