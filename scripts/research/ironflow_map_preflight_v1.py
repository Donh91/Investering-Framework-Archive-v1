"""Offline Ironflow projected-map source preflight; no collection or signal authority."""
import hashlib
import json
import math
from datetime import datetime, timezone


def clock(value):
    if not isinstance(value, str):
        raise ValueError("invalid_clock")
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None:
        raise ValueError("invalid_clock")
    return d.astimezone(timezone.utc)


def number(value, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError("invalid_number")
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def preflight(raw, market, received_at, cutoff):
    """Caller supplies trusted receipt clocks; validates bytes, not source authenticity.

    Keyless route only. No inference from omitted buckets, no cumulative sums,
    no portfolio-wide prediction and no historical first-known assertion.
    """
    if market not in ("BTC-PERP", "ETH-PERP") or not isinstance(raw, bytes):
        raise ValueError("invalid_request")
    p = json.loads(raw, object_pairs_hook=unique_object)
    if p.get("market") != market or p.get("side") != "both" or p.get("stale") is not False:
        raise ValueError("wrong_market_side_or_stale")
    snapshot = p["snapshot"]
    height = snapshot["height"]
    if type(height) is not int or height <= 0:
        raise ValueError("invalid_height")
    s, a, r, c = map(clock, (snapshot["time"], p["as_of"], received_at, cutoff))
    if not s <= a <= r < c or (c - s).total_seconds() > 1800:
        raise ValueError("clock_or_age_gate")
    mark = number(p["mark_px"], positive=True)
    width = number(p["bucket_size"], positive=True)
    if number(p["range_pct"], positive=True) != 10:
        raise ValueError("unexpected_keyless_range")
    coverage = p["coverage"]
    pct = number(coverage["with_liq_px_pct"])
    if pct > 100:
        raise ValueError("invalid_coverage")
    number(coverage["notional_usd"])
    levels = p["levels"]
    if not isinstance(levels, list) or not 1 <= len(levels) <= 10:
        raise ValueError("unexpected_keyless_level_count")
    intervals = []
    for row in levels:
        lo, hi = number(row["price_lo"], True), number(row["price_hi"], True)
        if not lo < hi or not math.isclose(hi - lo, width, rel_tol=1e-8, abs_tol=1e-9):
            raise ValueError("invalid_bucket")
        # Boundary buckets may straddle the advertised range; never clip or extrapolate them.
        if hi < mark * .9 or lo > mark * 1.1:
            raise ValueError("outside_keyless_range")
        for side in ("long", "short"):
            number(row[side + "_usd"])
            n = row[side + "_positions"]
            if type(n) is not int or n < 0:
                raise ValueError("invalid_position_count")
        intervals.append((lo, hi))
    ordered = sorted(intervals)
    if any(left[1] > right[0] for left, right in zip(ordered, ordered[1:])):
        raise ValueError("overlapping_buckets")
    return {"contract": "IRONFLOW_MAP_PREFLIGHT_v1", "market": market,
            "payload_sha256": hashlib.sha256(raw).hexdigest(), "snapshot_height": height,
            "returned_bucket_count": len(levels), "coverage_class": "TOP10_PARTIAL_MODELLED_MAP",
            "status": "STRUCTURAL_PREFLIGHT_ONLY", "source_authenticated": False,
            "first_known_verified": False, "full_map_features": None, "signal": None,
            "canonical_authority": False, "portfolio_authority": False}
