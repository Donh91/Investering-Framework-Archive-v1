"""Offline binding of Kompas Live capture to native Pages parity and hourly census.

No caller-provided receipt authenticates itself. No scoring, storage, network or
production authority. Native workflow provenance must be verified separately.
"""
import datetime as dt
import hashlib
import re
from collections import defaultdict

PATH = "data/kompas-live.json"
ORIGIN = "https://donh91.github.io/Investering-Framework-Archive-v1/"
HOUR = dt.timedelta(hours=1)


def utc(value):
    if not isinstance(value, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value):
        raise ValueError("explicit UTC required")
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso(value):
    return value.isoformat().replace("+00:00", "Z")


def sha(value, length):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{%d}" % length, value) is not None


def bind_publication(raw, capture, parity):
    """Match bytes and clocks, not trusted first-known or PIT admission."""
    if not isinstance(raw, bytes) or not raw:
        raise ValueError("exact nonempty bytes required")
    digest = hashlib.sha256(raw).hexdigest()
    if (capture.get("contract") != "KOMPAS_LIVE_MEMORY_CAPTURE_v1"
            or capture.get("source_bytes_sha256") != digest
            or type(capture.get("source_bytes")) is not int
            or capture["source_bytes"] != len(raw)
            or any(capture.get(k) is not False for k in
                   ("publication_authenticated", "pit_admitted", "scoring_authorized"))
            or capture.get("research_only") is not True
            or capture.get("source_url_label") != ORIGIN + PATH):
        raise ValueError("capture binding mismatch")
    issued = utc(capture["generated_at_utc"])
    observed = utc(capture["observer_reported_at_utc"])
    checked = utc(parity["checked_at_utc"])
    if issued > observed or issued > checked:
        raise ValueError("receipt predates issue")
    if (parity.get("contract") != "CN_PAGES_ARTIFACT_TO_CDN_PARITY_v1"
            or parity.get("status") != "PASS"
            or parity.get("canonical_public_url") != ORIGIN
            or parity.get("discovery_status") != "PASS"
            or parity.get("discovery_error") is not None
            or not sha(parity.get("run_head_sha"), 40)
            or not sha(parity.get("built_checkout_sha"), 40)):
        raise ValueError("not a successful parity receipt")
    files = parity.get("files")
    if not isinstance(files, list) or not files:
        raise ValueError("missing parity files")
    names = set()
    match = None
    for row in files:
        if (not isinstance(row, dict) or not isinstance(row.get("path"), str)
                or not row["path"] or row["path"] in names
                or row.get("status") != "PASS" or row.get("http_status") != 200
                or not sha(row.get("expected_sha256"), 64)
                or row["expected_sha256"] != row.get("served_sha256")):
            raise ValueError("invalid, duplicate or nonpassing parity row")
        names.add(row["path"])
        if row["path"] == PATH:
            match = row
    if not match or match["served_sha256"] != digest:
        raise ValueError("Kompas bytes not bound")
    return {"contract": "KOMPAS_LIVE_PUBLICATION_MATCH_v1",
            "status": "BYTE_MATCH_UNAUTHENTICATED",
            "source_bytes_sha256": digest, "generated_at_utc": iso(issued),
            "observer_reported_at_utc": iso(observed),
            "parity_checked_at_utc": iso(checked),
            "run_head_sha": parity["run_head_sha"],
            "built_checkout_sha": parity["built_checkout_sha"],
            "publication_authenticated": False, "pit_admitted": False,
            "scoring_authorized": False}


def census(start, end, rows):
    """Count producer-clock hours, not independently authenticated deliveries.

    Half-open UTC range, explicit expected slots. Distinguish absent hours,
    unavailable packets, retries, multiple issues and divergent same-clock bytes.
    Never substitute a subsequent packet for a missing hour.
    """
    start, end = utc(start), utc(end)
    if (start.minute or start.second or start.microsecond or end.minute or
            end.second or end.microsecond or not start < end or end-start > 366*24*HOUR):
        raise ValueError("invalid census bounds")
    slots = defaultdict(dict)
    duplicates = defaultdict(int)
    outside = 0
    for row in rows:
        if (row.get("contract") != "KOMPAS_LIVE_MEMORY_CAPTURE_v1"
                or row.get("pit_admitted") is not False
                or row.get("scoring_authorized") is not False
                or row.get("publication_authenticated") is not False
                or row.get("research_only") is not True
                or row.get("source_status") not in ("OK", "PARTIAL", "UNAVAILABLE")
                or not sha(row.get("source_bytes_sha256"), 64)):
            raise ValueError("invalid census row")
        clock = utc(row["generated_at_utc"])
        observed = utc(row["observer_reported_at_utc"])
        if observed < clock:
            raise ValueError("future issue")
        if not start <= clock < end:
            outside += 1
            continue
        slot = clock.replace(minute=0, second=0, microsecond=0)
        by_clock = slots[slot].setdefault(clock, {})
        digest = row["source_bytes_sha256"]
        if digest in by_clock:
            if by_clock[digest] != row["source_status"]:
                raise ValueError("same bytes, inconsistent status")
            duplicates[slot] += 1
        by_clock[digest] = row["source_status"]
    report = []
    clock = start
    while clock < end:
        by_clock = slots.get(clock, {})
        statuses = [v for by_digest in by_clock.values() for v in by_digest.values()]
        conflict = any(len(by_digest)>1 for by_digest in by_clock.values())
        state = ("MISSING" if not by_clock else "CONFLICT" if conflict else
                 "MULTIPLE_ISSUES" if len(by_clock)>1 else statuses[0])
        report.append({"hour_utc": iso(clock), "state": state,
                       "unique_issue_clocks": len(by_clock), "unique_packets": len(statuses),
                       "duplicate_observations": duplicates[clock]})
        clock += HOUR
    return {"contract": "KOMPAS_LIVE_MEMORY_CENSUS_v1",
            "scope": "CALLER_SUPPLIED_PRODUCER_CLOCK_INVENTORY_ONLY",
            "expected_hours": len(report),
            "missing_hours": sum(r["state"]=="MISSING" for r in report),
            "outside_window_rows": outside, "hours": report,
            "publication_authenticated": False, "pit_admitted": False,
            "scoring_authorized": False}
