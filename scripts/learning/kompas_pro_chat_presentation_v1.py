"""Text-only Kompas Pro view, source-conservative and analyst-overlay aware.

This is a presentation consumer, NOT a price model, source authenticator,
forecast issuer, official market/action owner, scorer or portfolio executor.
The upstream caller is responsible for independent source custody/receipt
verification. Pro-analysis scenarios are human-authored, nonbinding and never
become original CN forecasts, official targets or scored prospective rows.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
import re
from typing import Any, Mapping

from scripts.learning.kompas_pro_horizon_readback_v2 import HORIZON_IDS

CONTRACT = "KOMPAS_PRO_CHAT_PRESENTATION_v1"
LONG_HORIZONS = frozenset(("H1_3M", "H3_6M", "H6_9M", "H9_12M"))
SHORT_HORIZONS = frozenset(("H0_12H", "H24H", "H1_3D", "H5_7D"))
OFFICIAL_HORIZONS = {
    "H0_12H": "NEXT_12H", "H1_3D": "NEXT_1_3D",
    "H5_7D": "NEXT_5_7D", "H2_3W": "NEXT_2_3W",
}
METHODS = frozenset(("CONDITIONAL_MACRO_CYCLE", "STRUCTURE_AND_LIQUIDITY", "RISK_ENVELOPE", "VOLATILITY_BASELINE_ONLY"))
FORBIDDEN_SCENARIO_KEYS = frozenset((
    "official_action", "original_issue_id", "original_source_sha256",
    "public_issuance_verified", "model_authority", "probability",
    "calibrated_probability", "win_probability", "trade_signal",
))
ALLOWED_DIRECTIONS = frozenset(("UP", "CAUTIOUS_UP", "MIXED", "CAUTIOUS_DOWN", "DOWN", "NO_EDGE"))
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
RISK_ORDER = {"NORMAL": 1, "BUILDING": 2, "ELEVATED": 3, "HIGH": 4, "CONFIRMED": 5}
ASSET_IDS = ("BTC", "ETH", "LARGE_CAPS", "MID_CAPS", "SMALL_CAPS", "MICROCAPS", "MEMES")


def _parse_utc(v: Any) -> datetime:
    if not isinstance(v, str) or not v.endswith("Z"):
        raise ValueError("UTC_SOURCE_CLOCK_REQUIRED")
    try:
        d = datetime.fromisoformat(v[:-1] + "+00:00")
    except ValueError as exc:
        raise ValueError("UTC_SOURCE_CLOCK_INVALID") from exc
    if d.tzinfo is None:
        raise ValueError("UTC_SOURCE_CLOCK_INVALID")
    return d.astimezone(timezone.utc)


def _num(v: Any) -> float:
    if isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(float(v)) or v <= 0:
        raise ValueError("PRICE_MUST_BE_FINITE_POSITIVE")
    return float(v)


def _validate_case(case: Any) -> tuple[float, float]:
    if not isinstance(case, Mapping):
        raise ValueError("BASE_BULL_BEAR_CASE_REQUIRED")
    low, high = _num(case.get("low")), _num(case.get("high"))
    if low > high:
        raise ValueError("PRICE_BOUNDS_REVERSED")
    return low, high


def validate_analysis_overlay(analyst: Mapping[str, Any], *, as_of_utc: str) -> dict[str, dict[str, Any]]:
    """Validate already-authored analyst estimates, never calculate or issue any."""
    now = _parse_utc(as_of_utc)
    if not isinstance(analyst, Mapping):
        raise ValueError("ANALYST_OVERLAY_MUST_BE_MAPPING")
    result = {}
    for horizon_id, row in analyst.items():
        if horizon_id not in HORIZON_IDS or horizon_id == "NOW" or not isinstance(row, Mapping):
            raise ValueError("UNKNOWN_ANALYST_HORIZON")
        if set(row).intersection(FORBIDDEN_SCENARIO_KEYS):
            raise ValueError("ANALYST_CANNOT_ASSERT_OFFICIAL_OR_PROBABILITY_AUTHORITY")
        if row.get("classification") != "PRO_ANALYSIS_NONBINDING_UNCALIBRATED" or row.get("asset") != "BTC":
            raise ValueError("ANALYST_CLASSIFICATION_REQUIRED")
        if row.get("quote") not in ("USD", "USDT"):
            raise ValueError("ANALYST_QUOTE_REQUIRED")
        method = row.get("method")
        if method not in METHODS or (horizon_id in LONG_HORIZONS and method != "CONDITIONAL_MACRO_CYCLE"):
            raise ValueError("UNSUPPORTED_METHOD_OR_LONG_RANGE_EXTRAPOLATION")
        direction = row.get("direction")
        if direction not in ALLOWED_DIRECTIONS:
            raise ValueError("ANALYST_DIRECTION_INVALID")
        observed_at = _parse_utc(row.get("source_observed_at_utc"))
        assessed_at = _parse_utc(row.get("assessed_at_utc"))
        if not (observed_at <= assessed_at <= now) or (horizon_id in SHORT_HORIZONS and (now - observed_at).total_seconds() > 24 * 3600):
            raise ValueError("ANALYST_SOURCE_FUTURE_OR_STALE")
        evidence = row.get("source_refs")
        if not isinstance(evidence, list) or not evidence or any(not isinstance(v, str) or not v.startswith("https://") or "Donh91/secrets" in v for v in evidence):
            raise ValueError("ANALYST_SOURCE_REFERENCES_REQUIRED")
        assumptions = row.get("assumptions")
        if not isinstance(assumptions, list) or len(assumptions) < (2 if horizon_id in LONG_HORIZONS else 1) or any(not isinstance(v, str) or not v.strip() for v in assumptions):
            raise ValueError("ANALYST_ASSUMPTIONS_REQUIRED")
        falsifier = row.get("falsifier")
        if not isinstance(falsifier, str) or len(falsifier.strip()) < 10:
            raise ValueError("ANALYST_FALSIFIER_REQUIRED")
        cases = row.get("cases")
        if not isinstance(cases, Mapping) or set(cases) != {"base", "bull", "bear"}:
            raise ValueError("ALL_THREE_CONDITIONAL_CASES_REQUIRED")
        valid_cases = {name: _validate_case(case) for name, case in cases.items()}
        result[horizon_id] = {
            "classification": "PRO_ANALYSIS_NONBINDING_UNCALIBRATED",
            "direction": direction, "quote": row["quote"], "cases": valid_cases,
            "assessed_at_utc": row["assessed_at_utc"],
            "source_observed_at_utc": row["source_observed_at_utc"],
            "source_refs": list(evidence), "method": method,
            "assumptions": list(assumptions), "falsifier": falsifier,
        }
    return result


def _inline(value: str) -> str:
    """Make external text safe for a one-line Markdown presentation."""
    return value.replace("|", "/").replace("\n", " ").replace("\r", " ").replace("<", "&lt;").replace(">", "&gt;")


def _official_current(official: Mapping[str, Any], pointer: Mapping[str, Any] | None,
                      now: datetime) -> bool:
    """Necessary pointer/clock/quality gates, not independent Git custody proof."""
    if not isinstance(pointer, Mapping):
        return False
    if (pointer.get("contract") != "OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1"
        or official.get("contract") != "OFFICIAL_DAILY_COMPASS_v1"
        or pointer.get("data_status") != "OK" or official.get("data_status") != "OK"):
        return False
    sha = official.get("compass_sha256")
    if (not isinstance(sha, str) or not SHA256.fullmatch(sha)
        or pointer.get("compass_id") != official.get("compass_id")
        or pointer.get("compass_sha256") != sha
        or pointer.get("issued_at_utc") != official.get("issued_at_utc")):
        return False
    native = ((official.get("source_bindings") or {}).get("auto_market_state") or {})
    if ((native.get("freshness") or {}).get("status") != "PASS"
        or not isinstance(native.get("packet_sha256"), str)
        or pointer.get("source_packet_sha256") != native.get("packet_sha256")):
        return False
    try:
        age = (now - _parse_utc(official.get("issued_at_utc"))).total_seconds()
    except ValueError:
        return False
    return 0 <= age <= 10800


def _price_range(pair: tuple[float, float], quote: str) -> str:
    low, high = pair
    return f"{low:,.0f}–{high:,.0f} {quote}".replace(",", ".")


def render_chat(ledger: Mapping[str, Any], official: Mapping[str, Any], *,
                official_pointer: Mapping[str, Any] | None = None,
                as_of_utc: str, analyst: Mapping[str, Any] | None = None,
                interpretation: str = "Ingen uafhængig prognose konkluderet.") -> str:
    """Make a source-aware, text-only chat view; the caller verifies real custody."""
    now = _parse_utc(as_of_utc)
    if not isinstance(ledger, Mapping) or [x.get("id") for x in ledger.get("horizons", [])] != list(HORIZON_IDS):
        raise ValueError("CANONICAL_14_HORIZON_LEDGER_REQUIRED")
    if not isinstance(official, Mapping):
        raise ValueError("OFFICIAL_SOURCE_OBJECT_REQUIRED")
    rows = validate_analysis_overlay(analyst or {}, as_of_utc=as_of_utc)
    official_ok = _official_current(official, official_pointer, now)
    raw = official.get("market_reference") or {}
    btc_spot = raw.get("btc_usdt")
    try:
        spot_time = _parse_utc(raw.get("observation_open_utc"))
        spot_fresh = 0 <= (now - spot_time).total_seconds() <= 10800
        spot_str = f"{_num(btc_spot):,.0f} USDT (observation {raw['observation_open_utc']})".replace(",", ".") if spot_fresh else "UKENDT / ikke frisk"
    except (ValueError, KeyError):
        spot_str = "UKENDT / ikke frisk"
    if not official_ok:
        spot_str = "UKENDT / kilde ikke verificeret"
    action = official.get("action_now") if official_ok else None
    if action not in ("HOLD_WAIT", "HOLD_DEFENSIVE_WAIT", "PREPARE", "GRADUATED_TOPUP_ACTIVE", "HOLD_WAIT_DATA_DEGRADED"):
        action = "OFFICIEL HANDLING IKKE TILGÆNGELIG"
    hdr = ["# 🧭 KOMPAS PRO", f"As of {as_of_utc} · Official {'OK' if official_ok else 'DEGRADED/EXPIRED'} · BTC {spot_str}",
           f"**Officiel handling:** {action}. **PRO ANALYSIS:** ikke-bindende, ukalibrerede betingede scenarier.", "",
           "## Horisonter, BTC", "| Horisont | Kildesignal | BTC-pris / status |", "|---|---|---|"]
    tactical = []
    for h in ledger["horizons"]:
        hid = h["id"]
        name = h["label"]
        signal = "IKKE UDSTEDT"
        field = OFFICIAL_HORIZONS.get(hid)
        if official_ok and field:
            raw_h = (official.get("horizons") or {}).get(field) or {}
            direction = raw_h.get("expected_direction")
            if direction in ("UP", "DOWN", "MIXED", "SIDEWAYS", "LEAN_BULLISH", "LEAN_BEARISH"):
                signal = f"OBSERVATION {direction}" if hid == "H0_12H" else f"OFFICIAL {direction}"
        r = rows.get(hid)
        price = f"PRO ANALYSIS, base {_price_range(r['cases']['base'], r['quote'])}" if r else "Ikke udstedt / ingen selvstændig analyse"
        if hid == "NOW":
            price = f"Observation: {spot_str}"
        hdr.append(f"| {name} | {signal} | {price} |")
        if hid in ("H0_12H", "H1_3D", "H5_7D", "H2_3W", "H4_8W"):
            posture = ((official.get("horizons") or {}).get(field) or {}).get("action_posture") if official_ok and field else None
            tactical.append((name, signal, posture if posture in ("HOLD", "WAIT", "PREPARE") else "Ingen ny officiel handling"))
    hdr.extend(["", "## Mit taktiske Kompas", "| Tid | Retning | Handling |", "|---|---|---|"])
    hdr.extend(f"| {name} | {signal} | {posture} |" for name, signal, posture in tactical)
    hdr.extend(["", "## Aktivklasser", "| Aktiv | Status | Handling |", "|---|---|---|"])
    ladder = official.get("capitalization_ladder") or []
    by_asset = {entry.get("segment"): entry for entry in ladder
                if isinstance(entry, Mapping) and entry.get("segment") in ASSET_IDS} if official_ok and isinstance(ladder, list) else {}
    for asset in ASSET_IDS:
        entry = by_asset.get(asset) or {}
        state = entry.get("direction")
        posture = entry.get("action")
        if posture not in ("HOLD", "WAIT", "HARD_WAIT", "UNAVAILABLE"):
            posture = "Ingen ny autoriseret handling"
        hdr.append(f"| {asset} | {_inline(state) if isinstance(state, str) and state else 'Ikke aktuelt vurderet'} | {posture} |")
    protect = official.get("protection_tracker") or {} if official_ok else {}
    risk = protect.get("pullback_risk_state") if official_ok else None
    ordinal = f"{RISK_ORDER[risk]}/5" if risk in RISK_ORDER else "UKENDT"
    quality = protect.get("confidence_quality", "UKENDT") if official_ok else "UKENDT"
    sell = (official.get("sell_assessment") or {}).get("state", "UNAVAILABLE") if official_ok else "UNAVAILABLE"
    hdr.extend(["", f"**Pullback Radar:** {ordinal} ({risk or 'ukendt'}), evidenskvalitet {quality}.",
                f"**SELL/Swing/Re-entry:** SELL {sell}, ingen automatisk porteføljehandling eller implicit genkøb."])
    if rows:
        hdr.extend(["", "**PRO ANALYSIS, betingede scenarier (ikke officielle prognoser):**"])
        for hid in HORIZON_IDS:
            r = rows.get(hid)
            if not r:
                continue
            hdr.append(f"- {hid}: bear {_price_range(r['cases']['bear'], r['quote'])}, base {_price_range(r['cases']['base'], r['quote'])}, bull {_price_range(r['cases']['bull'], r['quote'])}. {r['method']}. Ugyldiggøres hvis: {_inline(r['falsifier'])}. Kilder: {', '.join(_inline(ref) for ref in r['source_refs'])}.")
    if not isinstance(interpretation, str) or not interpretation.strip():
        raise ValueError("ANALYST_INTERPRETATION_REQUIRED")
    hdr.extend(["", "## 🧠 MIN FORTOLKNING · NÆSTE 1–3 DAGE", _inline(interpretation.strip())])
    return "\n".join(hdr) + "\n"
