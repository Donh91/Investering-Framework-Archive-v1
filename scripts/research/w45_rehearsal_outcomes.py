"""Read-only W45 four-day prospective rehearsal, never an original CN issue.

All four BTC+ETH target days were first published in the frozen Research Lab
packet at 2026-11-04T23:29:12.208Z, before their target UTC midnight closes.
Outputs are repeatable public evidence receipts, not scientific PIT
certification, official scorecards, trading authority, or Monday backfill.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.research.verify_w45_midweek_shadow_benchmark import verify, parse_utc

UTC = timezone.utc
CONTRACT = "RESEARCH_W45_PROSPECTIVE_OUTCOMES_v1"
WEEK_START = parse_utc("2026-11-02T00:00:00Z")
WEEK_END = parse_utc("2026-11-09T00:00:00Z")
ISSUE = parse_utc("2026-11-04T23:29:12.208Z")
EXPECTED_WEEK = "2026-W45"


def _stamp(at):
    return at.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _real(x):
    return type(x) in (int, float) and math.isfinite(x) and x > 0


def _observations(source, mode, now):
    """Only source-owned paired hourly BTC+ETH USDT closes, without forward fill."""
    if mode == "PUBLIC_LIVE_W45":
        live = (source or {}).get("public_live_precision") or {}
        path = live.get("hourly_price_path") or {}
        quote = live.get("price_quote_labels") or {}
        if not (
            live.get("contract") == "CN_PUBLIC_LIVE_PRICE_PRECISION_v1"
            and live.get("forecast_week") == EXPECTED_WEEK
            and type(live.get("public_issue_number")) is int
            and live["public_issue_number"] > 0
            and path.get("contract") == "CN_PUBLIC_HOURLY_PRICE_PATH_v1"
            and path.get("source") == "HOURLY_SPOT_PASS_ONLY"
            and path.get("semantics") == "OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST"
            and path.get("forecast_week") == EXPECTED_WEEK
            and path.get("public_issue_number") == live["public_issue_number"]
            and path.get("observed_through_utc") == live.get("live_as_of_utc")
            and quote.get("contract") == "CN_PUBLIC_PRICE_QUOTE_LABELS_v1"
            and quote.get("actual_native_spot") == {"BTC": "USDT", "ETH": "USDT"}
            and quote.get("conversion_applied") is False
        ):
            raise ValueError("PUBLIC_LIVE_SOURCE_IDENTITY_UNVERIFIED")
        btc, eth = path.get("BTC"), path.get("ETH")
        if not isinstance(btc, list) or not isinstance(eth, list) or len(btc) != len(eth):
            raise ValueError("PAIRED_HOURLY_SOURCE_MISSING")
        rows = []
        for a, e in zip(btc, eth):
            if a.get("observed_at_utc") != e.get("observed_at_utc"):
                raise ValueError("BTC_ETH_SOURCE_CLOCK_DIVERGED")
            rows.append({"observed_at_utc": a.get("observed_at_utc"),
                         "BTC": a.get("close"), "ETH": e.get("close")})
        through = parse_utc(path["observed_through_utc"])
        if not rows or parse_utc(rows[-1]["observed_at_utc"]) != through:
            raise ValueError("LATEST_SOURCE_CUTOFF_MISMATCH")
        issue = live["public_issue_number"]
    elif mode == "IMMUTABLE_W45_HISTORY":
        history = source or {}
        if not (
            history.get("contract") == "CN_GRAPH_HISTORY_ACTUAL_v1"
            and history.get("forecast_week") == EXPECTED_WEEK
            and history.get("actual_quote_unit") == "USDT"
            and history.get("semantics") == "PASS_HOURLY_CLOSE_ONLY"
            and isinstance(history.get("points"), list)
            and history.get("observed_hours") == len(history["points"])
            and len(history["points"]) <= 168
        ):
            raise ValueError("ARCHIVED_W45_SOURCE_IDENTITY_UNVERIFIED")
        rows = history["points"]
        if not rows:
            raise ValueError("ARCHIVED_W45_NO_SOURCE_POINTS")
        through = parse_utc(rows[-1]["observed_at_utc"])
        issue = None
    else:
        raise ValueError("UNSUPPORTED_OUTCOME_SOURCE_MODE")

    if through > now + timedelta(seconds=60) or through > WEEK_END:
        raise ValueError("FUTURE_KNOWN_SOURCE_REJECTED")
    times = set()
    observed = {}
    previous = None
    for row in rows:
        at = parse_utc(row["observed_at_utc"])
        if not (WEEK_START < at <= WEEK_END and at <= through and at <= now + timedelta(seconds=60)):
            raise ValueError("HOUR_OUTSIDE_SOURCE_OR_ISSUE_CLOCK")
        if at.minute or at.second or at.microsecond or at in times:
            raise ValueError("DUPLICATE_OR_NONHOURLY_SOURCE_CLOCK")
        if previous is not None and at <= previous:
            raise ValueError("UNSORTED_SOURCE_HOURS")
        if not (_real(row.get("BTC")) and _real(row.get("ETH"))):
            raise ValueError("INVALID_PAIRED_SPOT_PRICES")
        times.add(at)
        previous = at
        observed[at] = {"BTC": float(row["BTC"]), "ETH": float(row["ETH"])}
    return observed, through, len(rows), issue


def compile_outcomes(packet, source, now, *, source_mode="PUBLIC_LIVE_W45",
                     original_research_sha256=None):
    """No new predictions or trades; replay original prices only after target close."""
    if now.tzinfo is None:
        raise ValueError("UTC_NOW_REQUIRED")
    now = now.astimezone(UTC)
    verify(packet)  # Recalculate all original forecast values from their 238 source hours.
    issued = parse_utc(packet["generated_at_utc"])
    if issued != ISSUE or issued >= WEEK_END:
        raise ValueError("FROZEN_FORECAST_ORIGIN_CHANGED")
    sha = original_research_sha256
    if not isinstance(sha, str) or len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("FROZEN_RESEARCH_BLOB_HASH_REQUIRED")
    try:
        actual, observed_through, hour_count, source_issue = _observations(source, source_mode, now)
        source_state = "VERIFIED_PUBLIC_CAPTURE_NOT_INDEPENDENT_FIRST_KNOWN"
        source_failure = None
    except (KeyError, TypeError, ValueError) as exc:
        actual, observed_through, hour_count, source_issue = {}, None, 0, None
        source_state = "UNAVAILABLE_FAIL_CLOSED"
        source_failure = str(exc).split(":")[0][:90]

    rows = []
    for asset in ("BTC", "ETH"):
        for original in packet["forecast"]["assets"][asset]["forecast"]:
            target = parse_utc(original["target_close_at_utc"])
            if target <= issued or target > WEEK_END:
                raise ValueError("LOOKAHEAD_FORECAST_TARGET")
            obs = actual.get(target, {}).get(asset)
            after_target = now >= target
            if not after_target:
                state = "PENDING_UTC_TARGET"
            elif obs is None:
                state = "AWAITING_VERIFIED_SOURCE"
            else:
                state = "MATURED_PUBLIC_CAPTURE"
            b0 = original["B0_persistence_expected_close"]
            b1 = original["B1_decay_momentum_expected_close"]
            matured = state == "MATURED_PUBLIC_CAPTURE"
            rows.append({
                "asset": asset,
                "utc_date": original["utc_date"],
                "day": original["day"],
                "target_close_at_utc": original["target_close_at_utc"],
                "B0_original_expected_close_USDT": b0,
                "B1_original_expected_close_USDT": b1,
                "observed_close_USDT": obs if matured else None,
                "B0_absolute_percentage_error": round(100 * abs(b0 / obs - 1), 5) if matured else None,
                "B1_absolute_percentage_error": round(100 * abs(b1 / obs - 1), 5) if matured else None,
                "outcome_state": state,
            })

    eligible = [row for row in rows if row["outcome_state"] == "MATURED_PUBLIC_CAPTURE"]
    summary = {}
    for asset in ("BTC", "ETH"):
        subset = [x for x in eligible if x["asset"] == asset]
        summary[asset] = {
            "matured_days": len(subset),
            "total_issued_days": 4,
            "B0_mean_absolute_pct_error": round(
                sum(x["B0_absolute_percentage_error"] for x in subset) / len(subset), 5
            ) if subset else None,
            "B1_mean_absolute_pct_error": round(
                sum(x["B1_absolute_percentage_error"] for x in subset) / len(subset), 5
            ) if subset else None,
            "claim_of_edge": False,
        }
    return {
        "contract": CONTRACT,
        "forecast_week": EXPECTED_WEEK,
        "created_at_utc": _stamp(now),
        "original_research_issued_at_utc": _stamp(issued),
        "original_research_source_sha256": sha,
        "original_monday_daily_forecast_issued_counts": {"BTC": 0, "ETH": 0},
        "source_mode": source_mode,
        "source_state": source_state,
        "source_failure": source_failure,
        "source_issue_number": source_issue,
        "observed_through_utc": _stamp(observed_through) if observed_through else None,
        "observed_hours": hour_count,
        "matured_observations": len(eligible),
        "total_forecast_observations": 8,
        "assets": summary,
        "rows": rows,
        "research_only": True,
        "provider_first_known_verified": False,
        "independent_scientific_edge_proven": False,
        "official_scoring_eligible": False,
        "portfolio_action_authority": False,
    }


def _verified_archive(root):
    """Archive fallback requires pre-existing indexed hash-chain and exact W45 actual path."""
    index_file = root / "05_CYCLE_NAVIGATOR/graph_history/v1/index.json"
    path = root / "05_CYCLE_NAVIGATOR/graph_history/v1/weeks/2026/W45/actual-series.json"
    if not index_file.is_file() or not path.is_file():
        return None
    from scripts.cycle_navigator.build_graph_history import verify_index_chain
    index = json.loads(index_file.read_text())
    chain = verify_index_chain(index, root)
    row = chain.get(EXPECTED_WEEK) or {}
    if row.get("actual_path") != str(path.relative_to(root)):
        raise ValueError("UNBOUND_ARCHIVED_W45_OBSERVATIONS")
    return json.loads(path.read_text())


def compile_from_repo(root, now=None):
    now = datetime.now(UTC) if now is None else now
    packet_file = root / "06_RESEARCH_LAB/mission_packets/2026-11-05__W45_MIDWEEK_PROSPECTIVE_BENCHMARK_v1.json"
    raw = packet_file.read_bytes()
    packet = json.loads(raw)
    # The historical research issue is permanently source-hashed, not recomputed
    # from future observations. Replaying the original packet is verified above.
    sha = hashlib.sha256(raw).hexdigest()
    latest_file = root / "05_CYCLE_NAVIGATOR/site/dist/data/latest.json"
    public = json.loads(latest_file.read_text()) if latest_file.is_file() else {}
    mode = "PUBLIC_LIVE_W45"
    if (public.get("public_live_precision") or {}).get("forecast_week") != EXPECTED_WEEK:
        archived = _verified_archive(root)
        if archived is not None:
            public = archived
            mode = "IMMUTABLE_W45_HISTORY"
        else:
            public = {}
    return compile_outcomes(packet, public, now, source_mode=mode,
                            original_research_sha256=sha)
