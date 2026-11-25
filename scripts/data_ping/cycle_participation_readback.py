"""Non-binding readback of the existing Auto Market State participation owner.
No prices, returns, membership lists, portfolio permission or phase forecast.
"""
from datetime import datetime, timedelta, timezone
import math
import re
from typing import Mapping

CONTRACT = "CN_CYCLE_PARTICIPATION_READBACK_v1"
SEMANTICS = "OBSERVED_24H_RELATIVE_PERFORMANCE_NOT_CAPITAL_FLOW"
# Same source expiry as auto_market_state.normalize_breadth.
MAX_AGE = timedelta(hours=8)
WINDOWS = {"LARGE_ALT_PROXY": (3, 20), "MID_ALT_PROXY": (21, 50),
           "SMALL_ALT_PROXY": (51, 100)}


def mapping(value):
    return value if isinstance(value, Mapping) else {}


def clock(value):
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc) if dt.utcoffset() is not None else None
    except (ValueError, OverflowError):
        return None


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def majority(value):
    if not number(value) or not 0 <= value <= 1:
        return "UNAVAILABLE"
    return "MAJORITY" if value > .5 else "MINORITY" if value < .5 else "HALF"


def unavailable(reason):
    return {"contract": CONTRACT, "status": "UNAVAILABLE", "reason": reason,
            "semantics": SEMANTICS, "observed_at_utc": None, "valid_until_utc": None,
            "relative_leader": "UNAVAILABLE",
            "buckets": {k: {"state": "UNAVAILABLE"} for k in
                        (*WINDOWS, "MICROCAP_PROXY", "MEMES")},
            "phase": "UNAVAILABLE", "rotation_confirmed": False,
            "authority": "DESCRIPTIVE_ONLY_NO_ACTION_OR_FORECAST"}


def cycle_participation_readback(auto_state, *, as_of):
    """Read only the authenticated public Auto Market State owner's existing proxy.

    Caller must verify packet ancestry/digest before invoking this helper.
    A bucket is an observed rank-window proxy, never an inferred capital flow.
    """
    packet = mapping(auto_state)
    state = mapping(packet.get("normalized_state"))
    health = mapping(mapping(packet.get("source_health")).get("breadth"))
    norm = mapping(health.get("normalization"))
    breadth = mapping(state.get("breadth"))
    proxy = mapping(state.get("capitalization_transmission_proxy"))
    now = as_of.astimezone(timezone.utc) if isinstance(as_of, datetime) and as_of.utcoffset() is not None else None
    issued = clock(packet.get("packet_generated_at_utc"))
    stamp = clock(proxy.get("source_retrieved_at_utc"))
    if now is None or issued is None or stamp is None or not stamp <= issued <= now:
        return unavailable("SOURCE_CLOCK_INVALID")
    if now - stamp >= MAX_AGE:
        return unavailable("BREADTH_OWNER_EXPIRED")
    if health.get("status") != "PASS" or norm.get("status") != "PASS":
        return unavailable("BREADTH_OWNER_NOT_PASS")
    if (proxy.get("contract") != "CAPITALIZATION_TRANSMISSION_PROXY_v2"
            or proxy.get("bucket_semantics") != "FILTERED_TOP100_RANK_WINDOWS_EXPLICIT_NON_BETA_EXCLUSIONS_PROXY_ONLY"):
        return unavailable("SOURCE_CONTRACT_MISMATCH")
    authority = mapping(proxy.get("authority"))
    if (not all(authority.get(k) is False for k in ("binding", "canonical_rotation", "portfolio_action", "market_threshold_change"))
            or type(authority.get("execution_weight")) is not int or authority["execution_weight"] != 0):
        return unavailable("SOURCE_AUTHORITY_MISMATCH")
    membership = mapping(breadth.get("universe")).get("membership_hash") or mapping(breadth.get("aggregate")).get("membership_hash")
    if (not isinstance(membership, str) or not re.fullmatch(r"[0-9a-f]{64}", membership)
            or membership != proxy.get("source_membership_hash")
            or stamp != clock(breadth.get("retrieved_at_utc"))
            or stamp != clock(norm.get("retrieved_at_utc"))):
        return unavailable("SOURCE_MEMBERSHIP_OR_CLOCK_MISMATCH")
    out = unavailable("NO_QUALIFIED_BUCKET")
    btc, eth = proxy.get("btc_return_24h_pct"), proxy.get("eth_return_24h_pct")
    if not all(number(x) for x in (btc, eth)):
        return out
    out["observed_at_utc"] = stamp.isoformat().replace("+00:00", "Z")
    out["valid_until_utc"] = (stamp + MAX_AGE).isoformat().replace("+00:00", "Z")
    out["relative_leader"] = "BTC" if btc > eth else "ETH" if eth > btc else "TIED"
    buckets = mapping(proxy.get("buckets"))
    for key, (lo, hi) in WINDOWS.items():
        row = mapping(buckets.get(key))
        counts = [row.get(k) for k in ("raw_rank_window_constituent_count", "excluded_non_beta_count", "constituent_count")]
        if (row.get("status") != "OBSERVED_PROXY" or row.get("rank_window") != [lo, hi]
                or not all(type(n) is int and n >= 0 for n in counts)
                or counts[0] != hi - lo + 1 or counts[1] + counts[2] != counts[0] or not counts[2]):
            continue
        values = [majority(row.get(k)) for k in ("advance_ratio_24h", "outperforming_btc_share_24h", "outperforming_eth_share_24h")]
        coverage = "TOP100_TAIL_ONLY_NOT_FULL_SMALL_CAP_UNIVERSE" if key == "SMALL_ALT_PROXY" else "TOP100_FULL_RANK_WINDOW"
        if "UNAVAILABLE" in values or row.get("coverage") != coverage:
            continue
        out["buckets"][key] = dict(state="OBSERVED_PROXY", coverage=coverage,
                                   advancing=values[0], outperforming_btc=values[1],
                                   outperforming_eth=values[2])
    observed = sum(out["buckets"][k]["state"] == "OBSERVED_PROXY" for k in WINDOWS)
    out["status"] = "OBSERVED_PARTICIPATION" if observed == len(WINDOWS) else "PARTIAL_OBSERVATION"
    out["reason"] = "SOURCE_PROXY_ONLY" if observed == len(WINDOWS) else "INCOMPLETE_RANK_WINDOWS"
    return out
