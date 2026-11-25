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


def leverage_context(replay, row, cutoff):
    """Read existing OKX derivatives columns in the exact verified hourly family.

    This is source-declared context, not independently known-by, verified venue
    raw response, cross-venue leverage, liquidation clearance or reset evidence.
    Missing funding-event rows are never forward-filled or turned into zero.
    """
    import csv
    import io
    import json
    from datetime import timedelta
    base={"contract":"PINNED_HOURLY_LEVERAGE_CONTEXT_v1","status":"UNAVAILABLE",
          "authority":"RESEARCH_ONLY_NON_CANONICAL","forecast_authority":False,
          "scientific_pit_eligible":False,"independent_first_known_utc":None,
          "reset_state":None,"reclaim_state":None,"assets":{}}
    try:
        from scripts.research import cn_mm_core_shadow_bridge_v1 as bridge
        owner=bridge.load_owner()
        source=row["source_version_commit"]
        replay.require_ancestor(source)
        family=json.loads(row["source_binding_manifest"])["families"]["ETHBTC_PERSISTENCE"]
        baseline=family["baseline"]
        anchor=parse_utc(baseline["timestamp_utc"])
        if not anchor+timedelta(hours=1)<=parse_utc(baseline["source_window_end_utc"])<=cutoff:
            raise ValueError("LEVERAGE_BASELINE_CLOCK_INVALID")
        payloads=owner._bound_payloads("ETHBTC_PERSISTENCE",family,source,read_blob=replay.read_blob)
        samples={}
        wanted={anchor,anchor-timedelta(hours=24)}
        for path,raw in payloads:
            reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig"),newline=""),strict=True)
            if not reader.fieldnames or len(set(reader.fieldnames))!=len(reader.fieldnames):
                raise ValueError("LEVERAGE_CSV_HEADER_INVALID")
            for item in reader:
                at=parse_utc(item["timestamp_utc"])
                if at not in wanted: continue
                available=parse_utc(item["source_window_end_utc"])
                if at+timedelta(hours=1)>available or available>cutoff:
                    continue
                if at in samples:
                    raise ValueError("LEVERAGE_DUPLICATE_HOUR")
                samples[at]=(item,path,hashlib.sha256(raw).hexdigest())
        latest,path,digest=samples[anchor]
        if (parse_utc(latest["source_window_end_utc"])!=parse_utc(baseline["source_window_end_utc"]) or
                any(float(latest[a+"_close"])!=float(baseline[a+"_close"]) for a in ("btc","eth","ethbtc"))):
            raise ValueError("LEVERAGE_PRICE_BASELINE_MISMATCH")
        def number(item,key,*,positive=False):
            value=item.get(key)
            if value in (None,""): return None
            n=float(value)
            if not math.isfinite(n) or (positive and n<=0):
                raise ValueError("LEVERAGE_INVALID_NUMERIC:"+key)
            return n
        prior=samples.get(anchor-timedelta(hours=24))
        assets={}
        for asset in ("btc","eth"):
            oi=ratio=funding=notional=notional_delta=None
            if latest.get("derivatives_status")=="PASS":
                if latest.get(asset+"_open_interest_source")=="OKX_CONTRACT_OI_HISTORY":
                    oi=number(latest,asset+"_open_interest",positive=True)
                    notional=number(latest,asset+"_open_interest_value",positive=True)
                if latest.get(asset+"_long_short_source")=="OKX_GLOBAL_ACCOUNT_RATIO":
                    ratio=number(latest,asset+"_long_short_ratio",positive=True)
                if latest.get(asset+"_funding_source")=="OKX_FUNDING_HISTORY":
                    funding=number(latest,asset+"_funding_event_rate")
                # The existing hourly owner permits array contract amounts
                # and legacy dict base/other amounts under one source tag.
                # The CSV does not preserve that quantity-shape identity.
                # USD notional is separately declared by the owner; a change
                # in it includes price effects and is not contract deleveraging.
                if notional is not None and prior:
                    old=prior[0]
                    if old.get("derivatives_status")=="PASS" and old.get(asset+"_open_interest_source")=="OKX_CONTRACT_OI_HISTORY":
                        old_notional=number(old,asset+"_open_interest_value",positive=True)
                        if old_notional is not None:
                            notional_delta=(notional/old_notional-1)*100
                            if not math.isfinite(notional_delta):
                                raise ValueError("LEVERAGE_NOTIONAL_DELTA_NONFINITE")
            assets[asset.upper()]={"open_interest_owner_amount":oi,"open_interest_amount_unit":"UNVERIFIED_OWNER_QUANTITY_SHAPE",
                    "open_interest_contracts":None,"oi_change_24h_pct":None,
                    "open_interest_owner_declared_usd_notional":notional,
                    "oi_owner_declared_usd_notional_change_24h_pct":notional_delta,
                    "notional_change_is_contract_deleveraging":False,
                    "long_short_account_ratio":ratio,"funding_event_rate":funding,
                    "funding_event_observation_utc":bridge.iso(anchor) if funding is not None else None,
                    "scope":"OKX_SINGLE_VENUE_CONTEXT_ONLY"}
        available=any(v["open_interest_owner_amount"] is not None or v["open_interest_owner_declared_usd_notional"] is not None or v["long_short_account_ratio"] is not None or
                      v["funding_event_rate"] is not None for v in assets.values())
        return {**base,"status":"ARCHIVED_DECLARED_CLOCK_CONTEXT_ONLY" if available else "UNAVAILABLE",
                "source_commit":source,"source_path":path,"source_sha256":digest,
                "observation_bar_utc":bridge.iso(anchor),"source_window_end_utc":latest["source_window_end_utc"],
                "prior_24h_source_sha256":prior[2] if prior else None,"assets":assets}
    except (ValueError,KeyError,TypeError,AttributeError,OSError,OverflowError,csv.Error,
            __import__("subprocess").SubprocessError):
        return {**base,"reason":"LEVERAGE_BOUND_SOURCE_UNAVAILABLE"}
