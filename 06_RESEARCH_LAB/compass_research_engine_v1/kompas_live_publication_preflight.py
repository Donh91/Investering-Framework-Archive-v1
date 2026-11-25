"""Offline binding of Kompas Live capture to native Pages parity and hourly census.

No caller-provided receipt authenticates itself. No scoring, storage, network or
production authority. Native workflow provenance must be verified separately.
"""
import base64
import datetime as dt
import json
import hashlib
import re
from collections import defaultdict

PATH = "data/kompas-live.json"
ORIGIN = "https://donh91.github.io/Investering-Framework-Archive-v1/"
HOUR = dt.timedelta(hours=1)
MAX_BYTES = 4 * 1024 * 1024
FLAGS = {"research_only": True, "official_forecast": False,
         "compass_probability_claim": False, "trading": False,
         "promotion": False, "site_synthesis": False}


def unique_object(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ValueError("duplicate JSON key")
        obj[k] = v
    return obj


def reject_constant(value):
    raise ValueError("nonfinite JSON constant")


def verify_capture_metadata(raw, capture):
    """Cross-check metadata against exact bytes; not proof of publication."""
    if not 0 < len(raw) <= MAX_BYTES:
        raise ValueError("invalid source size")
    doc = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                     parse_constant=reject_constant)
    if not isinstance(doc, dict) or doc.get("contract") != "KOMPAS_LIVE_PATH_v1":
        raise ValueError("wrong source contract")
    authority = doc.get("authority")
    if not isinstance(authority, dict) or any(authority.get(k) is not v for k, v in FLAGS.items()):
        raise ValueError("unexpected source authority")
    assets = doc.get("assets")
    if (not isinstance(assets, dict) or set(assets) != {"BTC", "ETH"}
            or any(not isinstance(a, dict) or a.get("status") not in ("OK", "UNAVAILABLE")
                   for a in assets.values())):
        raise ValueError("invalid source assets")
    count = sum(a["status"] == "OK" for a in assets.values())
    if doc.get("status") != ("OK" if count == 2 else "PARTIAL" if count == 1 else "UNAVAILABLE"):
        raise ValueError("inconsistent source status")
    seal = doc.pop("path_sha256", None)
    canonical = json.dumps(doc, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    if not sha(seal, 64) or hashlib.sha256(canonical).hexdigest() != seal:
        raise ValueError("invalid source seal")
    if (capture.get("source_contract") != doc["contract"]
            or capture.get("source_seal_sha256") != seal
            or utc(capture["generated_at_utc"]) != utc(doc["generated_at_utc"])
            or capture.get("source_status") != doc.get("status")
            or doc.get("status") not in ("OK", "PARTIAL", "UNAVAILABLE")
            or capture.get("source_bytes_base64") != base64.b64encode(raw).decode("ascii")):
        raise ValueError("capture metadata not derived from source")



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
    verify_capture_metadata(raw, capture)
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
    digest_identity = {}
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
        digest = row["source_bytes_sha256"]
        identity = (clock, row["source_status"])
        if digest in digest_identity and digest_identity[digest] != identity:
            raise ValueError("same bytes, inconsistent issue identity")
        digest_identity[digest] = identity
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
