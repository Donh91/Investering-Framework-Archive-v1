#!/usr/bin/env python3
"""Offline CoinGecko news discovery challenger for the existing News Intelligence Shadow test.

No network, scheduler, automatic verification or canonical market authority. Feed snapshots
must originate from an authorized retrieval path; licensed raw data stays off public Git.
"""
from __future__ import annotations

import argparse
import os
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

CONTRACT = "COINGECKO_NEWS_SHADOW_COMPARISON_v1"
AUTHORITY = "SHADOW_RESEARCH_ONLY_NON_CANONICAL"
STOP = frozenset("a an and are as at by for from in is of on or the to with after amid says over under market markets crypto bitcoin".split())
TRACKING = frozenset({"fbclid", "gclid", "ref", "source", "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"})


def timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be an ISO-8601 string")
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        raise ValueError("timestamp must include timezone")
    return moment.astimezone(timezone.utc)


def utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_url(url: str) -> str:
    if not isinstance(url, str) or not url:
        return ""
    try:
        p = urlsplit(url.strip())
        if p.scheme.lower() not in {"https", "http"} or not p.hostname:
            return ""
        host = p.hostname.lower().removeprefix("www.")
        query = urlencode(sorted((k, v) for k, v in parse_qsl(p.query) if k.lower() not in TRACKING))
        return urlunsplit(("https", host, p.path.rstrip("/") or "/", query, ""))
    except ValueError:
        return ""


def tokens(title: str) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9]+", title.lower()) if len(word) > 2 and word not in STOP}


def possible_headline_match(a: str, b: str) -> bool:
    left, right = tokens(a), tokens(b)
    if len(left) < 4 or len(right) < 4:
        return False
    return len(left & right) / len(left | right) >= 0.8


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_document(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError("input must be a JSON object")
    return result, sha_bytes(raw)


def validate_coingecko(doc: dict, asof: datetime) -> list[dict]:
    if doc.get("source_status") != "PASS":
        raise ValueError("CoinGecko source_status must be PASS, otherwise source unavailable")
    capture = timestamp(doc.get("captured_at_utc"))
    if capture > asof:
        raise ValueError("CoinGecko capture is later than the comparison cutoff")
    if doc.get("provider") != "CoinGecko":
        raise ValueError("provider must be CoinGecko")
    if not isinstance(doc.get("articles"), list):
        raise ValueError("articles must be present as an array")
    return doc["articles"]


def validate_situation(doc: dict, asof: datetime) -> list[dict]:
    observed = timestamp(doc.get("detection_time_utc"))
    if observed > asof:
        raise ValueError("Situation Room observation is later than the comparison cutoff")
    if doc.get("contract") != "SITUATION_ROOM_DAILY_OWNER_v1":
        raise ValueError("Situation Room must use its existing daily-owner contract")
    output = []
    for key in ("events", "current_unverified_discoveries", "unverified_discoveries"):
        values = doc.get(key) or []
        if not isinstance(values, list):
            raise ValueError("invalid Situation Room events list")
        output.extend(item for item in values if isinstance(item, dict))
    return output


def compare(cg: dict, sr: dict, asof: datetime, *, max_age_hours: int = 48) -> tuple[dict, list[dict]]:
    articles = validate_coingecko(cg, asof)
    capture_time = timestamp(cg["captured_at_utc"])
    baseline = validate_situation(sr, asof)
    urls = {canonical_url(x.get("url")) for x in baseline if canonical_url(x.get("url"))}
    heads = [x.get("title", "") for x in baseline if isinstance(x.get("title"), str)]
    observed = set()
    counts = {
        "provider_items": len(articles), "news_valid": 0, "guides_skipped": 0,
        "invalid_or_future": 0, "stale": 0, "duplicate_provider_url": 0,
        "same_url_in_situation_room": 0, "possible_headline_overlap_unverified": 0,
        "new_discoveries_unverified": 0,
    }
    candidates = []
    for item in articles:
        if not isinstance(item, dict):
            counts["invalid_or_future"] += 1
            continue
        if item.get("type") != "news":
            counts["guides_skipped"] += 1
            continue
        url = canonical_url(item.get("url"))
        title = item.get("title")
        try:
            published = timestamp(item.get("posted_at"))
        except (ValueError, TypeError):
            counts["invalid_or_future"] += 1
            continue
        if not url or not isinstance(title, str) or not title.strip() or published > asof or published > capture_time:
            counts["invalid_or_future"] += 1
            continue
        if url in observed:
            counts["duplicate_provider_url"] += 1
            continue
        if (asof - published).total_seconds() > max_age_hours * 3600:
            counts["stale"] += 1
            continue
        observed.add(url)
        counts["news_valid"] += 1
        if url in urls:
            status = "SAME_URL_DISCOVERY_ONLY"
            counts["same_url_in_situation_room"] += 1
        elif any(possible_headline_match(title, head) for head in heads):
            status = "POSSIBLE_HEADLINE_OVERLAP_UNVERIFIED"
            counts["possible_headline_overlap_unverified"] += 1
        else:
            status = "NEW_DISCOVERY_UNVERIFIED"
            counts["new_discoveries_unverified"] += 1
        ident = sha_bytes((url + "|" + utc_iso(published)).encode())[:20]
        candidates.append({
            "candidate_id": "CGNEWS_" + ident,
            "title": title,
            "source_url": item["url"],
            "source_name": item.get("source_name", "UNKNOWN"),
            "published_at_utc": utc_iso(published),
            "knowledge_cutoff_utc": utc_iso(asof),
            "discovery_status": status,
            "verification_status": "UNVERIFIED",
            "canonical_effect": False,
            "market_state_effect": False,
            "portfolio_effect": False,
            "execution_authority": False,
            "prospective_news_test_credit": False,
        })
    summary = {
        "contract": CONTRACT,
        "authority": AUTHORITY,
        "as_of_utc": utc_iso(asof),
        "source_status": "PASS" if articles else "EMPTY_SNAPSHOT_NO_COVERAGE_INFERENCE",
        "situation_room_run_status": sr.get("run_status", "UNKNOWN"),
        "metrics": counts,
        "primary_corrob_events_created": 0,
        "verified_news_cards_created": 0,
        "prospective_news_test_credit": 0,
        "canonical_effect": False,
        "market_state_effect": False,
        "portfolio_effect": False,
        "execution_authority": False,
        "interpretation": "DISCOVERY_COVERAGE_ONLY; do not infer impact or event confirmation",
    }
    return summary, candidates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coingecko-snapshot", required=True, type=Path)
    parser.add_argument("--situation-room-daily", required=True, type=Path)
    parser.add_argument("--as-of-utc", required=True)
    parser.add_argument("--private-candidates-output", type=Path, help="Write raw candidate detail ONLY to approved private temporary storage")
    args = parser.parse_args()
    try:
        asof = timestamp(args.as_of_utc)
        repo_root = Path(__file__).resolve().parents[2]
        provider_snapshot = args.coingecko_snapshot
        if not provider_snapshot.is_absolute():
            raise ValueError("CoinGecko snapshot path must be absolute")
        provider_snapshot = provider_snapshot.resolve()
        if provider_snapshot == repo_root or repo_root in provider_snapshot.parents:
            raise ValueError("licensed source payload must not be stored in the public repository")
        cg, cg_hash = load_document(provider_snapshot)
        sr, sr_hash = load_document(args.situation_room_daily)
        summary, candidates = compare(cg, sr, asof)
        summary["source_sha256"] = {"coingecko_snapshot": cg_hash, "situation_room_daily": sr_hash}
        if args.private_candidates_output is not None:
            # Reject repo-local, relative and world/group-readable destinations.
            target_path = args.private_candidates_output
            if not target_path.is_absolute():
                raise ValueError("private output path must be absolute")
            target_path = target_path.resolve()
            repo_root = Path(__file__).resolve().parents[2]
            if target_path == repo_root or repo_root in target_path.parents:
                raise ValueError("cannot persist licensed candidates inside control-plane repo")
            parent = target_path.parent
            if not parent.is_dir() or parent.stat().st_mode & 0o077:
                raise ValueError("private output parent must exist with mode 0700")
            descriptor = os.open(target_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as fh:
                json.dump({"contract": CONTRACT, "authority": AUTHORITY, "candidates": candidates}, fh, sort_keys=True)
                fh.write("\n")
        print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
        return 0
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        # Do not expose provider inputs or paths in error messages.
        print(json.dumps({"contract": CONTRACT, "status": "BLOCKED_SOURCE_OR_SCHEMA_UNAVAILABLE",
                          "reason_class": type(exc).__name__, "canonical_effect": False, "portfolio_effect": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
