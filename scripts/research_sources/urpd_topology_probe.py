#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

CONTRACT = "BGEOMETRICS_URPD_TOPOLOGY_RESEARCH_PROBE_v0_1"
BASE = "https://bitcoin-data.com/v1/urpd"
UA = {"User-Agent": "Investering-Research-Source-Probe/0.2", "Accept": "application/json"}
AUTHORITY = {"binding": False, "canonical_acceptance": False, "state_change": False, "portfolio_action": False, "automatic_promotion": False}

class ProbeError(ValueError):
    pass

def validate_day(day: str) -> str:
    try:
        parsed = datetime.strptime(day, "%Y-%m-%d")
    except ValueError as exc:
        raise ProbeError("bad_requested_day") from exc
    return parsed.strftime("%Y-%m-%d")

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

def _number(row: dict[str, Any], key: str) -> float:
    try:
        value = float(row[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ProbeError(f"bad_{key}") from exc
    if not math.isfinite(value):
        raise ProbeError(f"nonfinite_{key}")
    return value

def _percentile(values: list[float], q: float) -> float:
    if not values:
        raise ProbeError("empty_percentile_input")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    low = int(math.floor(position))
    high = int(math.ceil(position))
    if low == high:
        return ordered[low]
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight

def summarize_topology(raw: bytes, requested_day: str, spot_price: float) -> dict[str, Any]:
    requested_day = validate_day(requested_day)
    if spot_price <= 0 or not math.isfinite(spot_price):
        raise ProbeError("bad_spot_price")
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProbeError("invalid_json") from exc
    if not isinstance(doc, list) or not doc:
        raise ProbeError("empty_or_nonlist_payload")
    if not all(isinstance(row, dict) for row in doc):
        raise ProbeError("non_object_row")
    bins: list[dict[str, float]] = []
    for row in doc:
        low = _number(row, "priceLower")
        high = _number(row, "priceUpper")
        pct = _number(row, "pctSupply")
        btc = _number(row, "btcSupply")
        utxo = _number(row, "utxoCount")
        if low < 0 or high <= low or pct < 0 or btc < 0 or utxo < 0:
            raise ProbeError("invalid_urpd_bin")
        bins.append({"low": low, "high": high, "pct": pct, "btc": btc, "utxo": utxo})
    bins.sort(key=lambda item: (item["low"], item["high"]))
    for previous, current in zip(bins, bins[1:]):
        if current["low"] < previous["high"]:
            raise ProbeError("overlapping_bins")
    mids = [(item["low"] + item["high"]) / 2.0 for item in bins]
    pct_values = [item["pct"] for item in bins]
    pct_total = sum(pct_values)
    if pct_total <= 0:
        raise ProbeError("zero_pct_supply")
    near5 = sum(item["pct"] for item, mid in zip(bins, mids) if abs(mid / spot_price - 1) <= 0.05)
    below10 = sum(item["pct"] for item, mid in zip(bins, mids) if -0.10 <= mid / spot_price - 1 < 0)
    above10 = sum(item["pct"] for item, mid in zip(bins, mids) if 0 <= mid / spot_price - 1 <= 0.10)
    dense_threshold = _percentile(pct_values, 0.75)
    vacuum_threshold = _percentile(pct_values, 0.25)
    dense_distances = [abs(mid / spot_price - 1) for item, mid in zip(bins, mids) if item["pct"] >= dense_threshold]
    vacuum_distances = [abs(mid / spot_price - 1) for item, mid in zip(bins, mids) if item["pct"] <= vacuum_threshold]
    probabilities = [value / pct_total for value in pct_values if value > 0]
    entropy = -sum(value * math.log(value) for value in probabilities)
    entropy_norm = entropy / math.log(len(probabilities)) if len(probabilities) > 1 else 0.0
    return {
        "contract": CONTRACT,
        "source": "BGEOMETRICS",
        "metric": "urpd",
        "requested_day": requested_day,
        "day_lineage": {
            "requested_day_bound": True,
            "provider_payload_day_field_present": False,
            "provider_attested_snapshot_day": False,
            "lineage_class": "REQUEST_BOUND_ONLY_NOT_PROVIDER_ATTESTED",
        },
        "spot_price_input": spot_price,
        "payload_sha256": sha256(raw),
        "payload_bytes": len(raw),
        "row_count": len(bins),
        "price_min": bins[0]["low"],
        "price_max": bins[-1]["high"],
        "pct_supply_sum": round(pct_total, 10),
        "btc_supply_sum": round(sum(item["btc"] for item in bins), 8),
        "derived_features": {
            "supply_near_spot_5pct": round(near5, 10),
            "supply_below_spot_10pct": round(below10, 10),
            "supply_above_spot_10pct": round(above10, 10),
            "above_below_10pct_asymmetry": round(above10 - below10, 10),
            "nearest_dense_bin_distance_pct": round(min(dense_distances) * 100, 8) if dense_distances else None,
            "nearest_vacuum_bin_distance_pct": round(min(vacuum_distances) * 100, 8) if vacuum_distances else None,
            "cost_basis_concentration_entropy_norm": round(entropy_norm, 10),
        },
        "raw_persisted": False,
        "persistence": {"raw_public_persistence": False, "derived_receipt_only": True, "historical_retention_assumed": False},
        "authority": AUTHORITY,
    }

def build_url(day: str) -> str:
    day = validate_day(day)
    return BASE + "?" + urllib.parse.urlencode({"day": day})

def main() -> int:
    parser = argparse.ArgumentParser(description="Prospective research-only URPD topology probe.")
    parser.add_argument("--day", required=True, help="Requested snapshot date YYYY-MM-DD.")
    parser.add_argument("--spot-price", required=True, type=float, help="Externally-settled BTC spot for feature geometry.")
    args = parser.parse_args()
    url = build_url(args.day)
    receipt = summarize_topology(fetch_bytes(url), args.day, args.spot_price)
    receipt["url"] = url
    receipt["retrieved_at_utc"] = now_utc()
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
