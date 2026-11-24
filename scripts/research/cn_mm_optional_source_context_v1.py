"""Optional original-owner source coverage, never a trade or confirmation rule."""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from datetime import timezone

from scripts.experiments.etf_absorption_transmission_v1 import (
    pinned_settled_context, strict_json_bytes, parse_utc,
)
from scripts.daily_capture.pullback_forensics_collector import canonical_bytes, AUTHORITY

ROOT = "03_DAILY_CAPTURE_LOGS/pullback_forensics"


def forensics_context(replay, source_commit, cutoff):
    """Read only the original row-time pinned capture; never live/latest fallback.

    The collector records retrieval *start*, not completion. This is an archived
    lower-bound summary, not independent known-by or event-level reproduction.
    A small or absent count never proves liquidation clearance.
    """
    base = {"contract": "PINNED_PULLBACK_FORENSICS_CONTEXT_v1",
            "authority": "RESEARCH_ONLY_NON_CANONICAL", "forecast_authority": False,
            "scientific_pit_eligible": False, "status": "UNAVAILABLE",
            "liquidation_clearance": None, "reclaim": None,
            "source_commit": source_commit, "independent_first_known_utc": None}
    try:
        replay.require_ancestor(source_commit)
        raw = replay.read_blob(source_commit, ROOT + "/LATEST.json")
        obj = strict_json_bytes(raw)
        if (obj.get("contract") != "PULLBACK_FORENSICS_PASSIVE_CAPTURE_v1" or
                obj.get("authority") != AUTHORITY or obj.get("status") not in {"PASS", "PARTIAL"}):
            raise ValueError("FORENSICS_OWNER_CONTRACT_INVALID")
        body = dict(obj)
        claimed = body.pop("payload_sha256")
        if claimed != hashlib.sha256(canonical_bytes(body)).hexdigest():
            raise ValueError("FORENSICS_PAYLOAD_HASH_MISMATCH")
        at = parse_utc(obj["observed_at_utc"])
        if at > cutoff:
            raise ValueError("FORENSICS_CAPTURE_AFTER_CUTOFF")
        run = obj["run_id"]
        if not isinstance(run, str) or not re.fullmatch(r"pfr-[0-9]+-[0-9]+", run):
            raise ValueError("FORENSICS_RUN_ID_INVALID")
        path = ROOT + "/runs/" + at.strftime("%Y/%m/%d") + "/" + run + "/PULLBACK_FORENSICS.json"
        if replay.read_blob(source_commit, path) != raw:
            raise ValueError("FORENSICS_DATED_OWNER_MISMATCH")
        assets = {}
        for asset in ("BTC", "ETH"):
            lane = obj["lane1_liquidations"].get(asset, {})
            if lane.get("status") != "PASS" or lane.get("source_class") != "EXECUTED_LIQUIDATIONS":
                assets[asset] = {"status": "UNAVAILABLE"}
                continue
            meta = lane["instrument_metadata"]
            if (meta.get("instId") != asset + "-USDT-SWAP" or meta.get("ctType") != "linear" or
                    meta.get("ctMult") != "1" or meta.get("ctValCcy") != asset):
                raise ValueError("FORENSICS_INSTRUMENT_MISMATCH")
            for kind in ("instrument", "liquidations"):
                receipt = lane["source_receipts"][kind]
                if (receipt.get("http_status") != 200 or
                        not re.fullmatch("[0-9a-f]{64}", receipt["payload_sha256"]) or
                        type(receipt["payload_bytes"]) is not int or receipt["payload_bytes"] <= 0 or
                        not at <= parse_utc(receipt["retrieved_at_utc"]) <= cutoff):
                    raise ValueError("FORENSICS_RECEIPT_INVALID")
            agg = lane["persisted_rolling_aggregates"]
            if (agg.get("aggregates_are_lower_bound") is not True or
                    agg.get("source_completeness") != "UNVERIFIED_LEGACY_REST_WINDOW" or
                    agg.get("basis") != "DEDUPED_PERSISTED_EVENTS_FROM_ALL_PILOT_CAPTURES"):
                raise ValueError("FORENSICS_COMPLETENESS_MISREPRESENTED")
            fields = {}
            for hours in (1, 6, 24):
                count = agg[f"event_count_{hours}h"]
                if type(count) is not int or count < 0:
                    raise ValueError("FORENSICS_COUNT_INVALID")
                fields[f"event_count_{hours}h"] = count
                for side in ("long", "short"):
                    key = f"{side}_liq_usd_{hours}h"
                    value = agg[key]
                    if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
                        raise ValueError("FORENSICS_NOTIONAL_INVALID")
                    fields[key] = value
            for stem in ("event_count_", "long_liq_usd_", "short_liq_usd_"):
                if not fields[stem+"1h"] <= fields[stem+"6h"] <= fields[stem+"24h"]:
                    raise ValueError("FORENSICS_ROLLING_WINDOW_INCONSISTENT")
            assets[asset] = {"status": "ARCHIVED_LOWER_BOUND_ONLY", "lower_bound": True,
                             "source_completeness_verified": False, **fields}
        available = sum(v["status"] == "ARCHIVED_LOWER_BOUND_ONLY" for v in assets.values())
        return {**base, "status": "ARCHIVED_LOWER_BOUND_CONTEXT_ONLY" if available else "UNAVAILABLE",
                "source_path": path, "source_sha256": hashlib.sha256(raw).hexdigest(),
                "owner_payload_sha256": claimed, "capture_start_utc": at.isoformat(),
                "capture_completion_utc": None, "assets": assets}
    except (ValueError, KeyError, TypeError, AttributeError, OSError, OverflowError,
            __import__("subprocess").SubprocessError) as exc:
        return {**base, "reason": str(exc).split(":", 1)[0]}


def coverage(replay, observations):
    """Same source commits and cutoffs as admitted core; no outcome access."""
    etf_counts, liquidation_counts = Counter(), Counter()
    sessions, runs = set(), set()
    for row in observations:
        cutoff = parse_utc(row["observation_utc"])
        source = row["source_commit"]
        etf = pinned_settled_context(replay.repo, source, replay.checkout, cutoff)
        liq = forensics_context(replay, source, cutoff)
        etf_counts[etf["status"]] += 1
        liquidation_counts[liq["status"]] += 1
        if etf["status"] == "VERIFIED_DECLARED_CLOCK_CONTEXT_ONLY":
            sessions.add(etf["session_date"])
        if liq["status"] == "ARCHIVED_LOWER_BOUND_CONTEXT_ONLY":
            runs.add(liq["source_path"])
    return {"contract": "OPTIONAL_SOURCE_COVERAGE_v1", "observation_n": len(observations),
            "etf_status_counts": dict(etf_counts), "etf_distinct_sessions": len(sessions),
            "liquidation_status_counts": dict(liquidation_counts), "liquidation_distinct_captures": len(runs),
            "scientific_pit_eligible": False, "forecast_authority": False,
            "absorption_transform": "UNFROZEN", "liquidation_clearance_transform": "UNFROZEN",
            "source_completeness_verified": False}
