#!/usr/bin/env python3
"""Kompas live path (KOMPAS_LIVE_PATH_v1): server-side producer for the Kompas live card.

Research display only. It issues no official forecast, no probability claim on behalf of the
Official Compass, no trading signal and no promotion. The browser only renders this JSON; it
never computes a tilt or a probability (Official Compass bull/bear is
EVIDENCE_BALANCE_NOT_PROBABILITY and the site keeps site_synthesis_allowed === false).

Inputs (public plane only, all already committed to the repository or the Pages bundle):
  * 03_DAILY_CAPTURE_LOGS/hourly/<YYYY>/<MM>/<date>.csv   PASS/OK hourly spot bars
  * 04_MARKET_LEARNING/handlekompas/official/daily/...   Official Compass packets
  * <Pages bundle> data/latest.json                       this week's frozen weekly zone
  * Challenger B pre-registration JSON (tilt, short_horizon_hours); absent -> flat path
  * this week's frozen Challenger A issuance (range z at q=0.5); absent -> registered seed

Line = Challenger B (pre-registered TASK2_CHALLENGER_B_KOMPAS_TILT_v1, formula B1):
  g_h      = tilt * (bull_h - bear_h)/10 * sigma_hourly * sqrt(24)
  m(h)     = g_13 * min(h, short)/24 + g_57 * max(h - short, 0)/24
  centre_k = P0 * exp(m(h_k))
  p_up_k   = Phi(m(h_k) / (sigma_hourly * sqrt(h_k)))
Frames = Challenger A range family, q = 0.5: centre_k * exp(-/+ z * sigma_hourly * sqrt(h_k)).

Stdlib only. Deterministic for a fixed --now. Always writes the output file; data problems
produce status UNAVAILABLE with a reason (fail closed) instead of a stale or invented forecast.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

CONTRACT = "KOMPAS_LIVE_PATH_v1"
HOURLY_DIR = "03_DAILY_CAPTURE_LOGS/hourly"
PACKET_DIR = "04_MARKET_LEARNING/handlekompas/official/daily"
OFFICIAL_POINTER_PATH = "04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json"
PUBLIC_PROJECTION_DIR = "04_MARKET_LEARNING/handlekompas/official/public"
B_PREREG_PATH = ("06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/"
                 "CHALLENGER_B_KOMPAS_TILT_PREREG_v1.json")
B_CONTRACT = "TASK2_CHALLENGER_B_KOMPAS_TILT_v1"
B_FORMULA_VERSION = "B1"
A_ISSUANCE_PATH = "06_RESEARCH_LAB/task2_challenger_a/issued/{year}/W{week:02d}/CHALLENGER_A_FROZEN_ISSUANCE.json"
A_CONTRACT = "TASK2_CHALLENGER_A_SQRT_T_VOL_BAND_v1"
# Registered Challenger A seed, range family, q = 0.5 (CHALLENGER_A_SQRT_T_VOL_BAND_PREREG_v1 seed_z.range."0.5").
A_SEED_Z_RANGE_50 = 0.966374
PACKET_CONTRACT = "OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1"
PACKET_SEMANTICS = "EVIDENCE_BALANCE_NOT_PROBABILITY"
PACKET_LOOKBACK_HOURS = 24
VIEW_HORIZONS = (("1_3d", "g13"), ("5_7d", "g57"))
FRESHNESS_SLA_MINUTES = 90
CLIENT_STALE_AFTER_MINUTES = 180
SIGMA_WINDOW_HOURS = 168
# SAMPLE std (ddof 1) of the last 168 hourly log returns: the same definition as Challenger A's
# sigma_hourly (v2.1 and S1's #2124), which is Challenger B's registered input. Coordinator decision
# 2026-11-14 (replaces the earlier population-std draft).
SIGMA_DDOF = 1
NORM_WINDOW_HOURS = 672
NORM_MIN_RETURNS = 500
DISPLAY_BACK_HOURS = 96
MAX_HORIZON_DAYS = 7
HORIZONS = (1, 3, 7)
MIN_DISPLAY_MOVE_PCT = 0.3
ZONE_HYSTERESIS_CLOSES = 3
MAX_EVENTS = 24
ASSETS = {"BTC": ("btc_close", "btc_high", "btc_low"), "ETH": ("eth_close", "eth_high", "eth_low")}
QUOTE = "USDT"
DIRECTION_CODES = ("UP", "DOWN", "MIXED", "SIDEWAYS", "NO_EDGE")
HOUR = dt.timedelta(hours=1)
DAY = dt.timedelta(days=1)
WEEKDAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")


class Unavailable(Exception):
    """A data condition that must fail closed (no forecast is shown)."""


# ---------------------------------------------------------------- helpers

def utc(value: Any) -> dt.datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("timestamp_required")
    t = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("timezone_required")
    return t.astimezone(dt.timezone.utc)


def iso(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def floor_day(t: dt.datetime) -> dt.datetime:
    return t.replace(hour=0, minute=0, second=0, microsecond=0)


def ceil_day(t: dt.datetime) -> dt.datetime:
    f = floor_day(t)
    return f if f == t else f + DAY


def week_monday(t: dt.datetime) -> dt.datetime:
    return floor_day(t) - dt.timedelta(days=t.weekday())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(obj: Any) -> str:
    return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def positive(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        x = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return x if math.isfinite(x) and x > 0 else None


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def r(x: float | None, n: int) -> float | None:
    return None if x is None else round(float(x), n)


def pstdev(values: list[float], ddof: int = 0) -> float:
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - ddof))


def display_round(price: float) -> int:
    """Display rounding of a model level: 100s above 10 000, else 10s (presentation only)."""
    step = 100 if price >= 10_000 else 10
    return int(round(price / step) * step)


# ------------------------------------------------------------- text format

DA_WEEKDAY = {"MON": "mandag", "TUE": "tirsdag", "WED": "onsdag", "THU": "torsdag",
              "FRI": "fredag", "SAT": "lørdag", "SUN": "søndag"}
EN_WEEKDAY = {"MON": "Monday", "TUE": "Tuesday", "WED": "Wednesday", "THU": "Thursday",
              "FRI": "Friday", "SAT": "Saturday", "SUN": "Sunday"}
OFFICIAL_WORD = {"UP": ("Stigende", "Rising"), "DOWN": ("Faldende", "Falling"), "MIXED": ("Blandet", "Mixed"),
                 "SIDEWAYS": ("Sideværts", "Sideways"), "NO_EDGE": ("Ingen dokumenteret fordel", "No proven edge")}


def fmt_int(x: float, lang: str) -> str:
    s = f"{int(round(x)):,}"
    return s.replace(",", ".") if lang == "da" else s


def fmt_pct(x: float, lang: str) -> str:
    v = round(float(x), 1)
    if v == 0:
        v = 0.0
    s = f"{abs(v):.1f}"
    if lang == "da":
        s = s.replace(".", ",")
    sign = "−" if v < 0 else ("+" if v > 0 else "")
    return sign + s


def weekday_of_close(end: dt.datetime) -> str:
    return WEEKDAYS[(end - dt.timedelta(seconds=1)).weekday()]


def close_phrase(code: str, lang: str) -> str:
    return f"ved {DA_WEEKDAY[code]}ens lukning" if lang == "da" else f"by {EN_WEEKDAY[code]}'s close"


def official_word(code: str | None, lang: str) -> str | None:
    if code not in OFFICIAL_WORD:
        return None
    return OFFICIAL_WORD[code][0 if lang == "da" else 1]


# ------------------------------------------------------------- hourly data

def load_hourly(root: Path, start: dt.datetime, now: dt.datetime) -> tuple[dict[str, list[tuple[dt.datetime, float]]], list[dict]]:
    """PASS/OK spot bars per asset, {asset: [(close_time, close)]}, closed in (start, now].

    Mirrors build_public_live_precision.py: spot_status PASS/OK, hour-aligned timestamp_utc
    (bar OPEN time), positive finite low <= close <= high per asset; first row of a duplicate
    timestamp wins. Never interpolates or fills.
    """
    series: dict[str, dict[dt.datetime, float]] = {a: {} for a in ASSETS}
    files = []
    day = floor_day(start - HOUR)
    while day <= now:
        rel = f"{HOURLY_DIR}/{day:%Y}/{day:%m}/{day:%Y-%m-%d}.csv"
        path = root / rel
        if path.is_file():
            data = path.read_bytes()
            files.append({"path": rel, "sha256": sha256_bytes(data)})
            text = data.decode("utf-8", errors="replace").splitlines()
            for row in csv.DictReader(text):
                try:
                    opened = utc(row.get("timestamp_utc") or "")
                except ValueError:
                    continue
                if opened.minute or opened.second or opened.microsecond:
                    continue
                if str(row.get("spot_status") or "").upper() not in {"PASS", "OK"}:
                    continue
                closed = opened + HOUR
                if not start < closed <= now:
                    continue
                for asset, (c, h, l) in ASSETS.items():
                    close, high, low = positive(row.get(c)), positive(row.get(h)), positive(row.get(l))
                    if close is None or high is None or low is None or not low <= close <= high:
                        continue
                    series[asset].setdefault(closed, close)
        day += DAY
    return {a: sorted(v.items()) for a, v in series.items()}, files


def sigma_at(bars: list[tuple[dt.datetime, float]], window: int = SIGMA_WINDOW_HOURS) -> float:
    """Sample std (ddof SIGMA_DDOF) of the last `window` hourly log returns, as Challenger A; fails closed on any gap."""
    tail = bars[-(window + 1):]
    if len(tail) != window + 1 or tail[-1][0] - tail[0][0] != window * HOUR:
        raise Unavailable("SIGMA_WINDOW_GAP")
    rets = [math.log(tail[i][1] / tail[i - 1][1]) for i in range(1, len(tail))]
    sd = pstdev(rets, SIGMA_DDOF)
    if not (math.isfinite(sd) and sd > 0):
        raise Unavailable("SIGMA_NOT_POSITIVE")
    return sd


def sigma_norm(bars: list[tuple[dt.datetime, float]], as_of: dt.datetime) -> float | None:
    """28-day descriptive norm: std (same ddof) over consecutive (exactly 1 h apart) returns."""
    lo = as_of - NORM_WINDOW_HOURS * HOUR
    rows = [b for b in bars if b[0] >= lo]
    rets = [math.log(rows[i][1] / rows[i - 1][1]) for i in range(1, len(rows)) if rows[i][0] - rows[i - 1][0] == HOUR]
    if len(rets) < NORM_MIN_RETURNS:
        return None
    sd = pstdev(rets, SIGMA_DDOF)
    return sd if math.isfinite(sd) and sd > 0 else None


def close_at(bars: list[tuple[dt.datetime, float]], t: dt.datetime) -> float | None:
    for closed, close in bars:
        if closed == t:
            return close
    return None


def close_at_or_before(bars: list[tuple[dt.datetime, float]], t: dt.datetime) -> tuple[dt.datetime, float] | None:
    best = None
    for b in bars:
        if b[0] <= t:
            best = b
        else:
            break
    return best


# -------------------------------------------------------- Challenger B prereg

def load_prereg(root: Path) -> tuple[dict | None, dict]:
    path = root / B_PREREG_PATH
    info: dict[str, Any] = {"path": B_PREREG_PATH, "present": path.is_file(), "sha256": None}
    if not path.is_file():
        return None, {**info, "status": "ABSENT", "reason": "PREREG_ABSENT"}
    data = path.read_bytes()
    info["sha256"] = sha256_bytes(data)
    try:
        doc = json.loads(data)
        params = doc["params"]
        tilt, short = params["tilt"], params["short_horizon_hours"]
        ok = (doc.get("contract") == B_CONTRACT and doc.get("formula_version") == B_FORMULA_VERSION
              and isinstance(tilt, (int, float)) and not isinstance(tilt, bool) and math.isfinite(tilt) and 0 < tilt <= 1
              and isinstance(short, int) and not isinstance(short, bool) and 0 < short <= MAX_HORIZON_DAYS * 24
              and params.get("packet_contract") == PACKET_CONTRACT
              and params.get("packet_semantics") == PACKET_SEMANTICS
              and params.get("packet_lookback_hours") == PACKET_LOOKBACK_HOURS)
    except (ValueError, KeyError, TypeError):
        ok = False
    if not ok:
        return None, {**info, "status": "INVALID", "reason": "PREREG_INVALID"}
    return {"tilt": float(tilt), "short_horizon_hours": int(short)}, {**info, "status": "OK", "reason": None}


# ------------------------------------------------------- Official packets

def scale_view(packet: dict, horizon: str) -> tuple[int, int] | None:
    """(bull, bear) for one horizon of a valid official packet, else None (no view). Same rule as B."""
    s = packet.get("bull_bear_scale") if isinstance(packet, dict) else None
    if not isinstance(s, dict) or s.get("contract") != PACKET_CONTRACT or s.get("semantics") != PACKET_SEMANTICS:
        return None
    h = (s.get("horizons") or {}).get(horizon) or {}
    if not isinstance(h, dict):
        return None
    bull, bear = h.get("bull"), h.get("bear")
    if h.get("status") != "OK" or not isinstance(bull, int) or not isinstance(bear, int):
        return None
    if isinstance(bull, bool) or isinstance(bear, bool) or bull + bear != 10 or min(bull, bear) < 0:
        return None
    return bull, bear


def structurally_valid(packet: Any) -> bool:
    s = packet.get("bull_bear_scale") if isinstance(packet, dict) else None
    return isinstance(s, dict) and s.get("contract") == PACKET_CONTRACT and s.get("semantics") == PACKET_SEMANTICS




def source_expiry(packet: dict, issued: dt.datetime, now: dt.datetime) -> dt.datetime:
    """Exact original Official Compass owner deadline, not its 24h publication lookback.

    Matches the existing public builder's owner policy: minimum timestamp + max_age_seconds
    over all PASS checks. No site-side TTL extension, backfill or substitution.
    """
    freshness = ((packet.get("source_bindings") or {}).get("auto_market_state") or {}).get("freshness") or {}
    checks = freshness.get("checks")
    if freshness.get("status") != "PASS" or not isinstance(checks, list) or not checks:
        raise ValueError("OFFICIAL_POINTER_SOURCE_FRESHNESS_INVALID")
    deadlines: list[dt.datetime] = []
    for row in checks:
        if not isinstance(row, dict) or row.get("status") != "PASS":
            raise ValueError("OFFICIAL_POINTER_SOURCE_FRESHNESS_INVALID")
        seconds = row.get("max_age_seconds")
        if (not isinstance(seconds, (int, float)) or isinstance(seconds, bool) or
                not math.isfinite(seconds) or not 0 < seconds <= 31 * 24 * 3600):
            raise ValueError("OFFICIAL_POINTER_SOURCE_FRESHNESS_INVALID")
        try:
            stamp = utc(row.get("timestamp"))
        except (ValueError, TypeError, OverflowError):
            raise ValueError("OFFICIAL_POINTER_SOURCE_FRESHNESS_INVALID") from None
        if stamp > issued:
            raise ValueError("OFFICIAL_POINTER_SOURCE_FRESHNESS_INVALID")
        deadlines.append(stamp + dt.timedelta(seconds=seconds))
    deadline = min(deadlines)
    if now >= deadline:
        raise ValueError("OFFICIAL_POINTER_SOURCE_EXPIRED")
    return deadline


def bound_official_packet(root: Path, now: dt.datetime) -> tuple[dict | None, dict]:
    """Use ONLY the current Official Compass pointer, its hash-bound original and public projection.

    The source repository is checked out at main in the Pages producer. A historical daily file
    discovered by directory traversal is never eligible to replace a missing or mismatched pointer.
    """
    info: dict[str, Any] = {"pointer": OFFICIAL_POINTER_PATH, "status": "UNAVAILABLE", "reason": "OFFICIAL_POINTER_MISSING"}
    pointer_file = root / OFFICIAL_POINTER_PATH
    if not pointer_file.is_file():
        return None, info
    try:
        pointer_bytes = pointer_file.read_bytes()
        pointer = json.loads(pointer_bytes)
        if not isinstance(pointer, dict) or pointer.get("contract") != "OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1" or pointer.get("data_status") != "OK":
            raise ValueError("OFFICIAL_POINTER_INVALID")
        rel, public_rel = pointer["compass_path"], pointer["public_projection_path"]
        # Both source paths must be rooted under their exact public-plane owner.
        for candidate, prefix in ((rel, PACKET_DIR), (public_rel, PUBLIC_PROJECTION_DIR)):
            if not isinstance(candidate, str) or not candidate.startswith(prefix + "/") or any(
                    segment in ("", ".", "..") for segment in candidate.split("/")) or not candidate.endswith(".json"):
                raise ValueError("OFFICIAL_POINTER_PATH_INVALID")
        if not (Path(rel).stem == pointer["compass_id"] == Path(public_rel).stem):
            raise ValueError("OFFICIAL_POINTER_ID_MISMATCH")
        raw = (root / rel).read_bytes()
        public_raw = (root / public_rel).read_bytes()
        if (sha256_bytes(raw) != pointer.get("compass_content_sha256") or
                sha256_bytes(public_raw) != pointer.get("public_projection_content_sha256")):
            raise ValueError("OFFICIAL_POINTER_CONTENT_MISMATCH")
        packet, public = json.loads(raw), json.loads(public_raw)
        issued = utc(pointer["issued_at_utc"])
        if issued > now or issued <= now - PACKET_LOOKBACK_HOURS * HOUR:
            raise ValueError("OFFICIAL_POINTER_STALE")
        if (packet.get("contract") != "OFFICIAL_DAILY_COMPASS_v1" or
                public.get("contract") != "PUBLIC_COMPASS_PROJECTION_v1" or
                packet.get("data_status") != "OK" or public.get("data_status") != "OK" or
                packet.get("compass_id") != pointer["compass_id"] or
                public.get("compass_id") != pointer["compass_id"] or
                packet.get("compass_sha256") != pointer.get("compass_sha256") or
                public.get("source_compass_sha256") != pointer.get("compass_sha256") or
                public.get("projection_sha256") != pointer.get("public_projection_sha256") or
                packet.get("issued_at_utc") != pointer["issued_at_utc"] or
                public.get("issued_at_utc") != pointer["issued_at_utc"] or
                (packet.get("source_bindings") or {}).get("auto_market_state", {}).get("packet_sha256") != pointer.get("source_packet_sha256") or
                not structurally_valid(packet) or
                any(((packet.get("bull_bear_scale", {}).get("horizons", {}).get(h) or {}).get("status") == "OK" and
                     scale_view(packet, h) is None) for h, _ in VIEW_HORIZONS)):
            raise ValueError("OFFICIAL_POINTER_PACKAGE_MISMATCH")
        deadline = source_expiry(packet, issued, now)
        candidate = {"path": rel, "sha256": sha256_bytes(raw), "issued": issued, "packet": packet}
        return candidate, {"pointer": OFFICIAL_POINTER_PATH, "status": "VERIFIED", "reason": None,
                           "pointer_sha256": sha256_bytes(pointer_bytes), "compass_path": rel,
                           "compass_content_sha256": sha256_bytes(raw),
                           "public_projection_content_sha256": sha256_bytes(public_raw),
                           "issued_at_utc": iso(issued), "valid_until_utc": iso(deadline)}
    except (OSError, KeyError, TypeError, AttributeError, ValueError, json.JSONDecodeError) as error:
        code = str(error) if isinstance(error, ValueError) else "OFFICIAL_POINTER_PACKAGE_UNAVAILABLE"
        # Never publish private paths, raw payloads or exception detail into the public JSON.
        return None, {**info, "reason": code if code.startswith("OFFICIAL_POINTER_") else "OFFICIAL_POINTER_PACKAGE_UNAVAILABLE"}


def load_packets(root: Path, start: dt.datetime, now: dt.datetime) -> list[dict]:
    """Packets issued in (start, now], sorted by issue time. Unreadable files are skipped."""
    out = []
    day = floor_day(start)
    while day <= now:
        folder = root / PACKET_DIR / f"{day:%Y}" / f"{day:%m}" / f"{day:%d}"
        if folder.is_dir():
            for p in sorted(folder.glob("CMP-*.json")):
                try:
                    data = p.read_bytes()
                    packet = json.loads(data)
                    issued = utc(packet.get("issued_at_utc"))
                except (OSError, ValueError, AttributeError):
                    continue
                if not start < issued <= now:
                    continue
                out.append({"path": p.relative_to(root).as_posix(), "sha256": sha256_bytes(data),
                            "issued": issued, "packet": packet})
        day += DAY
    out.sort(key=lambda c: (c["issued"], c["path"]))
    return out


def official_direction(packet: dict, key: str = "NEXT_1_3D") -> str | None:
    d = ((packet.get("horizons") or {}).get(key) or {}).get("expected_direction")
    return d if d in DIRECTION_CODES else None


def select_views(candidates: list[dict], now: dt.datetime) -> dict:
    """Per horizon: the latest packet issued in (now-24h, now] with an OK, integer, sum-to-10 view."""
    lo = now - PACKET_LOOKBACK_HOURS * HOUR
    out = {}
    for horizon, _ in VIEW_HORIZONS:
        best = None
        for c in candidates:
            if not lo < c["issued"] <= now:
                continue
            view = scale_view(c["packet"], horizon)
            if view and (best is None or c["issued"] >= best[0]["issued"]):
                best = (c, view)
        if best is None:
            out[horizon] = None
            continue
        c, (bull, bear) = best
        key = "NEXT_1_3D" if horizon == "1_3d" else "NEXT_5_7D"
        out[horizon] = {"issued_at_utc": iso(c["issued"]), "path": c["path"], "file_sha256": c["sha256"],
                        "compass_sha256": c["packet"].get("compass_sha256"), "bull": bull, "bear": bear,
                        "official_direction": official_direction(c["packet"], key)}
    return out


# ---------------------------------------------------- Challenger A frames z

def load_a_z(root: Path, now: dt.datetime) -> dict:
    year, week, _ = now.isocalendar()
    rel = A_ISSUANCE_PATH.format(year=year, week=week)
    info: dict[str, Any] = {"family": "range", "quantile": 0.5, "a_issuance_path": rel, "a_issuance_sha256": None}
    path = root / rel
    if not path.is_file():
        return {**info, "z": A_SEED_Z_RANGE_50, "z_source": "REGISTERED_SEED", "reason": "A_ISSUANCE_ABSENT"}
    data = path.read_bytes()
    info["a_issuance_sha256"] = sha256_bytes(data)
    z = None
    try:
        doc = json.loads(data)
        if doc.get("contract") == A_CONTRACT and doc.get("week") == f"{year}-W{week:02d}":
            for holder in (doc.get("calibration") or {}, doc):
                cand = ((holder.get("z") or {}).get("range") or {}).get("0.5")
                if isinstance(cand, (int, float)) and not isinstance(cand, bool) and math.isfinite(cand) and 0.1 < cand < 5:
                    z = float(cand)
                    break
    except (ValueError, AttributeError, TypeError):
        z = None
    if z is None:
        return {**info, "z": A_SEED_Z_RANGE_50, "z_source": "REGISTERED_SEED", "reason": "A_ISSUANCE_UNPARSEABLE"}
    return {**info, "z": z, "z_source": "CHALLENGER_A_FROZEN_ISSUANCE", "reason": None}


# ------------------------------------------------------- weekly frozen zone

def frozen_zones(latest_path: Path | None, now: dt.datetime) -> tuple[dict, dict]:
    year, week, _ = now.isocalendar()
    label = f"{year}-W{week:02d}"
    status: dict[str, Any] = {"week": label, "source": "data/latest.json package.forecast_freeze", "sha256": None, "observed_quote": QUOTE}
    if latest_path is None or not latest_path.is_file():
        return {}, {**status, "status": "UNAVAILABLE", "reason": "LATEST_JSON_ABSENT"}
    data = latest_path.read_bytes()
    status["sha256"] = sha256_bytes(data)
    try:
        latest = json.loads(data)
        pointer = latest.get("pointer") or {}
        freeze = (latest.get("package") or {}).get("forecast_freeze") or {}
    except (ValueError, AttributeError):
        return {}, {**status, "status": "UNAVAILABLE", "reason": "LATEST_JSON_INVALID"}
    if pointer.get("iso_year") != year or pointer.get("iso_week") != week:
        return {}, {**status, "status": "UNAVAILABLE", "reason": "FROZEN_WEEK_NOT_CURRENT"}
    # A weekly freeze without verified quote provenance must not be overlaid onto USDT spot bars.
    # The current public sanitizer may omit price_quote; absence is deliberately unavailable.
    quote = freeze.get("price_quote")
    status["freeze_quote"] = quote
    if not isinstance(quote, str) or quote != QUOTE:
        return {}, {**status, "status": "UNAVAILABLE", "reason": "FROZEN_ZONE_QUOTE_MISMATCH"}
    zones = {}
    for asset in ASSETS:
        lo, hi = positive(freeze.get(f"{asset.lower()}_range_low")), positive(freeze.get(f"{asset.lower()}_range_high"))
        if lo is not None and hi is not None and lo < hi:
            zones[asset] = {"low": lo, "high": hi, "week": label}
    if not zones:
        return {}, {**status, "status": "UNAVAILABLE", "reason": "FROZEN_ZONE_MISSING"}
    return zones, {**status, "status": "OK", "reason": None}


def zone_state(x: float, zone: dict | None) -> int | None:
    if not zone:
        return None
    return -1 if x < zone["low"] else (1 if x > zone["high"] else 0)


def deviation(x: float, zone: dict | None) -> dict:
    if not zone:
        return {"state": "NO_ZONE", "pct": None}
    if x < zone["low"]:
        return {"state": "BELOW", "pct": r((x / zone["low"] - 1) * 100, 4)}
    if x > zone["high"]:
        return {"state": "ABOVE", "pct": r((x / zone["high"] - 1) * 100, 4)}
    return {"state": "INSIDE", "pct": 0.0}


# ------------------------------------------------------------- the path

def day_grid(now: dt.datetime) -> list[dict]:
    first, last = floor_day(now) + DAY, ceil_day(now + MAX_HORIZON_DAYS * DAY)
    out, end = [], first
    while end <= last:
        out.append({"start": max(end - DAY, now), "end": end, "h": (end - now).total_seconds() / 3600})
        end += DAY
    return out


def horizon_ends(now: dt.datetime) -> dict[str, dt.datetime]:
    return {str(n): ceil_day(now + n * DAY) for n in HORIZONS}


def log_shift(h: float, g13: float, g57: float, short: int) -> float:
    return g13 * min(h, short) / 24 + g57 * max(h - short, 0.0) / 24


def strength(diff: int) -> str | None:
    d = abs(diff)
    return None if d <= 1 else ("svag" if d <= 3 else ("moderat" if d <= 5 else "tydelig"))


def headline_for(hz_end: dt.datetime, days: list[dict], p0: float, views: dict, model: dict, short: int) -> dict:
    day = next(d for d in days if d["end"] == hz_end)
    m = day["m"]
    pct = (math.exp(m) - 1) * 100
    used = [("1_3d", views.get("1_3d"))]
    if day["h"] > short:
        used.append(("5_7d", views.get("5_7d")))
    used = [(k, v) for k, v in used if v]
    # Strength comes only from views that push the path the way it actually goes (sign of m), so an
    # opposite 5-7 d view can never label a DOWN path "tydelig". Ties keep the 1-3 d view.
    sign = (m > 0) - (m < 0)
    balance = None
    for k, v in used:
        if (v["bull"] - v["bear"]) * sign > 0 and (
                balance is None or abs(v["bull"] - v["bear"]) > abs(balance["bull"] - balance["bear"])):
            balance = {"horizon": k, "bull": v["bull"], "bear": v["bear"]}
    if balance is None and used:
        k, v = used[0]
        balance = {"horizon": k, "bull": v["bull"], "bear": v["bear"]}
    st = strength(balance["bull"] - balance["bear"]) if balance and sign else None
    if not model["applied"]:
        direction, reason = "NONE", model["reason"]
    elif not used:
        direction, reason = "NONE", "NO_VIEW"
    elif st is None:
        direction, reason = "NONE", "BALANCED"
    elif abs(pct) < MIN_DISPLAY_MOVE_PCT:
        direction, reason = "NONE", "SMALL_MOVE"
    else:
        direction, reason = ("UP" if m > 0 else "DOWN"), None
    return {"direction": direction, "reason": reason, "end_utc": iso(hz_end), "end_weekday": weekday_of_close(hz_end),
            "target": r(day["centre"], 2), "target_display": display_round(day["centre"]), "pct": r(pct, 4),
            "strength": st if direction != "NONE" else None, "balance": balance,
            "tilting_views": [k for k, v in used if v["bull"] != v["bear"]] if model["applied"] else [],
            "official_direction": {k: (v or {}).get("official_direction") for k, v in
                                   (("1_3d", views.get("1_3d")), ("5_7d", views.get("5_7d") if day["h"] > short else None))}}


# ------------------------------------------------------------- comments

def _views_phrase(head: dict, lang: str) -> str:
    """The official Kompas direction words behind the path: 1-3 d always, 5-7 d only where it tilts the path."""
    parts = []
    for k, label in (("1_3d", "1–3 d"), ("5_7d", "5–7 d")):
        word = official_word(head["official_direction"].get(k), lang)
        if word and (k == "1_3d" or k in head.get("tilting_views", [])):
            parts.append(f"{label}: {word}")
    if not parts:
        return ""
    return ("Kompas " if lang == "da" else "Compass ") + " · ".join(parts) + ". "


def now_text(head: dict, p0: float, sigma: float, lang: str) -> str:
    move = fmt_int(display_round(p0 * sigma * math.sqrt(24)), lang)
    when = close_phrase(head["end_weekday"], lang)
    if lang == "da":
        tail = f"Et normalt dagsudsving er ± {move} USDT, så vejen derhen går sjældent i en lige linje."
        if head["direction"] in ("UP", "DOWN"):
            word = "op" if head["direction"] == "UP" else "ned"
            return (f"{_views_phrase(head, 'da')}Challenger B (forsøg) hælder derfor kursbanen {word} mod ca. "
                    f"{fmt_int(head['target_display'], 'da')} {when} ({fmt_pct(head['pct'], 'da')} %). {tail}")
        lead = {
            "PREREG_ABSENT": "Challenger B er ikke registreret i denne udgave, så kursbanen hælder ikke.",
            "PREREG_INVALID": "Challenger B's registrering kunne ikke læses, så kursbanen hælder ikke.",
            "NO_VIEW": "Kompas har ingen gyldig vurdering for perioden de seneste 24 timer, så Challenger B (forsøg) hælder ikke kursbanen.",
            "BALANCED": "Kompas' evidens er i balance, så Challenger B (forsøg) hælder ikke kursbanen.",
            "SMALL_MOVE": f"Challenger B (forsøg) hælder kun lidt ({fmt_pct(head['pct'], 'da')} % {when}).",
        }[head["reason"]]
        return f"{_views_phrase(head, 'da') if head['reason'] in ('BALANCED', 'SMALL_MOVE') else ''}{lead} Et normalt dagsudsving er ± {move} USDT."
    tail = f"A normal daily move is ± {move} USDT, so the way there is rarely a straight line."
    if head["direction"] in ("UP", "DOWN"):
        word = "up" if head["direction"] == "UP" else "down"
        return (f"{_views_phrase(head, 'en')}Challenger B (trial) therefore tilts the path {word} toward approx. "
                f"{fmt_int(head['target_display'], 'en')} {when} ({fmt_pct(head['pct'], 'en')}%). {tail}")
    lead = {
        "PREREG_ABSENT": "Challenger B is not registered in this build, so the path does not tilt.",
        "PREREG_INVALID": "Challenger B's registration could not be read, so the path does not tilt.",
        "NO_VIEW": "Compass has no valid reading for the period in the last 24 hours, so Challenger B (trial) does not tilt the path.",
        "BALANCED": "Compass evidence is balanced, so Challenger B (trial) does not tilt the path.",
        "SMALL_MOVE": f"Challenger B (trial) tilts only slightly ({fmt_pct(head['pct'], 'en')}% {when}).",
    }[head["reason"]]
    return f"{_views_phrase(head, 'en') if head['reason'] in ('BALANCED', 'SMALL_MOVE') else ''}{lead} A normal daily move is ± {move} USDT."


def _event(kind: str, asset: str, t: dt.datetime, price: float, zone: dict | None, last: float,
           da: str, en: str, since: bool = True) -> dict:
    return {"id": f"{kind}-{asset}-{iso(t)}", "kind": kind, "t_utc": iso(t), "price": price,
            "deviation": deviation(price, zone), "text": {"da": da, "en": en},
            "since_pct": r((last / price - 1) * 100, 4) if since else None,
            "author": "AUTOMATIC", "text_source": "CODE_TEMPLATE_v1", "ai_text": None}


def comment_events(asset: str, bars: list[tuple[dt.datetime, float]], week_start: dt.datetime, now: dt.datetime,
                   zone: dict | None, packets: list[dict], heads: dict, p0: float, sigma: float) -> list[dict]:
    last = p0
    events = []
    week_bars = [b for b in bars if week_start <= b[0] <= now]
    opening = close_at(bars, week_start)
    opening_bar = (week_start, opening) if opening is not None else (week_bars[0] if week_bars else None)
    if opening_bar is not None:
        x = opening_bar[1]
        if zone:
            where_da = "inde i" if zone["low"] <= x <= zone["high"] else "uden for"
            where_en = "inside" if zone["low"] <= x <= zone["high"] else "outside"
            da = (f"Ugen startede ved {fmt_int(x, 'da')}, {where_da} ugens frosne prognose "
                  f"({fmt_int(zone['low'], 'da')}–{fmt_int(zone['high'], 'da')}).")
            en = (f"The week opened at {fmt_int(x, 'en')}, {where_en} this week's frozen forecast "
                  f"({fmt_int(zone['low'], 'en')}–{fmt_int(zone['high'], 'en')}).")
        else:
            da = f"Ugen startede ved {fmt_int(x, 'da')}. Ugens frosne prognose er ikke tilgængelig."
            en = f"The week opened at {fmt_int(x, 'en')}. This week's frozen forecast is not available."
        events.append(_event("WEEK_START", asset, opening_bar[0], x, zone, last, da, en))
    # Official Kompas 1-3 d direction changes (the official word, attributed to Kompas).
    prev = None
    for c in packets:
        if not structurally_valid(c["packet"]):
            continue
        d = official_direction(c["packet"])
        if d is None:
            continue
        if prev is not None and d != prev and c["issued"] > week_start:
            bar = close_at_or_before(bars, c["issued"])
            if bar is not None:
                da = f"Kompas 1–3 d skiftede fra {official_word(prev, 'da')} til {official_word(d, 'da')}."
                en = f"Compass 1–3 d changed from {official_word(prev, 'en')} to {official_word(d, 'en')}."
                events.append(_event("KOMPAS_1_3D_CHANGE", asset, c["issued"], bar[1], zone, last, da, en))
        prev = d
    # Zone breaks: a change counts only after ZONE_HYSTERESIS_CLOSES consecutive hourly closes.
    if zone and week_bars:
        seq = ([opening_bar] if opening is not None else []) + [b for b in week_bars if b[0] > week_start]
        state = zone_state(seq[0][1], zone)
        n = ZONE_HYSTERESIS_CLOSES
        for i in range(1, len(seq)):
            s = zone_state(seq[i][1], zone)
            if s == state:
                continue
            run = seq[i:i + n]
            if len(run) == n and all(zone_state(b[1], zone) == s for b in run) and \
                    all(run[j + 1][0] - run[j][0] == HOUR for j in range(n - 1)):
                t, x = run[0]  # the event is dated at the first close of the confirmed run
                if s < 0:
                    da = (f"Kursen lukkede under ugens frosne prognose-bund ({fmt_int(zone['low'], 'da')}) "
                          f"{n} timer i træk.")
                    en = (f"Price closed below this week's frozen forecast floor ({fmt_int(zone['low'], 'en')}) "
                          f"for {n} hours in a row.")
                elif s > 0:
                    da = (f"Kursen lukkede over ugens frosne prognose-top ({fmt_int(zone['high'], 'da')}) "
                          f"{n} timer i træk.")
                    en = (f"Price closed above this week's frozen forecast top ({fmt_int(zone['high'], 'en')}) "
                          f"for {n} hours in a row.")
                else:
                    da = f"Kursen er tilbage inde i ugens frosne prognose ({n} timelukninger i træk)."
                    en = f"Price is back inside this week's frozen forecast ({n} hourly closes in a row)."
                events.append(_event("ZONE_BREAK", asset, t, x, zone, last, da, en))
                state = s
    order = {"NOW": 3, "ZONE_BREAK": 2, "KOMPAS_1_3D_CHANGE": 1, "WEEK_START": 0}
    events.sort(key=lambda e: (e["t_utc"], order[e["kind"]]), reverse=True)
    events = events[:MAX_EVENTS - 1]
    nowe = _event("NOW", asset, now, p0, zone, last, now_text(heads["3"], p0, sigma, "da"),
                  now_text(heads["3"], p0, sigma, "en"), since=False)
    nowe["text_by_horizon"] = {k: {"da": now_text(h, p0, sigma, "da"), "en": now_text(h, p0, sigma, "en")}
                               for k, h in heads.items()}
    return [nowe] + events


# ---------------------------------------------------------------- assets

def challenger_b_block(days: list[dict], model: dict) -> dict:
    """Challenger B's own model probability, nested under its own authority block.

    p_up is B's registered research output (Phi(m / (sigma*sqrt(h)))), used for scoring. It is NOT an
    Official Compass field and NOT rendered on the site. Without a registered B there is no p_up at all.
    """
    return {
        "model": "Challenger B", "contract": B_CONTRACT, "formula_version": B_FORMULA_VERSION, "status": "TRIAL",
        "authority": {"research_only": True, "compass_probability_claim": False, "official_compass": False,
                      "rendered_on_site": False, "trading": False, "promotion": False},
        "semantics": "CHALLENGER_B_MODEL_PROBABILITY_DAY_CLOSE_ABOVE_P0_NOT_A_KOMPAS_FIELD",
        "applied": model["applied"], "reason": model["reason"],
        "p_up_by_day": [{"end_utc": iso(d["end"]), "p_up": r(d["p_up"], 6)} for d in days] if model["applied"] else None,
    }


def asset_block(asset: str, bars: list[tuple[dt.datetime, float]], now: dt.datetime, views: dict, model: dict,
                frames: dict, zone: dict | None, packets: list[dict], week_start: dt.datetime) -> dict:
    if not bars:
        raise Unavailable("HOURLY_MISSING")
    as_of, p0 = bars[-1]
    if now - as_of > dt.timedelta(minutes=FRESHNESS_SLA_MINUTES):
        raise Unavailable("HOURLY_STALE")
    sd = sigma_at(bars)
    norm = sigma_norm(bars, as_of)
    tilt, short = (model["tilt"], model["short_horizon_hours"]) if model["applied"] else (0.0, 72)
    g = {"g13": 0.0, "g57": 0.0}
    for horizon, key in VIEW_HORIZONS:
        v = views.get(horizon)
        if model["applied"] and v:
            g[key] = tilt * (v["bull"] - v["bear"]) / 10 * sd * math.sqrt(24)
    z = frames["z"]
    days = []
    for d in day_grid(now):
        h = d["h"]
        m = log_shift(h, g["g13"], g["g57"], short)
        centre = p0 * math.exp(m)
        w = z * sd * math.sqrt(h)
        days.append({"start": d["start"], "end": d["end"], "h": h, "m": m, "centre": centre,
                     "lo": centre * math.exp(-w), "hi": centre * math.exp(w),
                     "p_up": phi(m / (sd * math.sqrt(h))) if h > 0 else 0.5})
    ends = horizon_ends(now)
    heads = {k: headline_for(e, days, p0, views, model, short) for k, e in ends.items()}
    day_move = sd * math.sqrt(24) * 100
    level = None
    if norm:
        nm = norm * math.sqrt(24) * 100
        level = "HIGH" if day_move > nm * 1.1 else ("LOW" if day_move < nm * 0.9 else "NORMAL")
    p24, pw = close_at(bars, as_of - 24 * HOUR), close_at(bars, week_start)
    lo_display = now - DISPLAY_BACK_HOURS * HOUR
    return {
        "status": "OK", "reason": None, "quote": QUOTE, "as_of_utc": iso(as_of), "p0": p0,
        "sigma_hourly": r(sd, 10), "sigma_hourly_norm_28d": r(norm, 10),
        "daily_move_pct": r(day_move, 4), "daily_move_level": level,
        "daily_move_usdt_display": display_round(p0 * sd * math.sqrt(24)),
        "chips": {"change_24h_pct": r((p0 / p24 - 1) * 100, 4) if p24 else None,
                  "change_week_pct": r((p0 / pw - 1) * 100, 4) if pw else None},
        "drift_per_day": {k: r(v, 10) for k, v in g.items()},
        "points": [[iso(t), c] for t, c in bars if t >= lo_display],
        "days": [{"index": i, "start_utc": iso(d["start"]), "end_utc": iso(d["end"]), "h": r(d["h"], 4),
                  "weekday": weekday_of_close(d["end"]), "log_shift": r(d["m"], 10), "centre": r(d["centre"], 2),
                  "lo": r(d["lo"], 2), "hi": r(d["hi"], 2)} for i, d in enumerate(days)],
        "challenger_b": challenger_b_block(days, model),
        "headline": heads,
        "frozen_zone": zone,
        "events": comment_events(asset, bars, week_start, now, zone, packets, heads, p0, sd),
    }


# ---------------------------------------------------------------- build

def base_document(now: dt.datetime) -> dict:
    year, week, _ = now.isocalendar()
    monday = week_monday(now)
    return {
        "contract": CONTRACT,
        "generated_at_utc": iso(now),
        "status": "UNAVAILABLE",
        "reasons": [],
        "official_source_valid_until_utc": None,
        "authority": {"research_only": True, "official_forecast": False, "compass_probability_claim": False,
                      "trading": False, "promotion": False, "site_synthesis": False,
                      "line_label": "live, Challenger B\u0027s formel (forsøg)", "frames_label": "live, beregnet hver time med Challenger A\u0027s formel"},
        "display_rules": {"freshness_sla_minutes": FRESHNESS_SLA_MINUTES,
                          "client_stale_after_minutes": CLIENT_STALE_AFTER_MINUTES,
                          "min_display_move_pct": MIN_DISPLAY_MOVE_PCT, "horizons_days": list(HORIZONS),
                          "display_back_hours": DISPLAY_BACK_HOURS, "zone_hysteresis_closes": ZONE_HYSTERESIS_CLOSES,
                          "strength": {"svag": "|bull-bear| 2-3", "moderat": "4-5", "tydelig": ">=6", "none": "<=1"}},
        "week": {"iso_week": f"{year}-W{week:02d}", "start_utc": iso(monday), "end_utc": iso(monday + 7 * DAY)},
        "horizon_end_utc": {k: iso(v) for k, v in horizon_ends(now).items()},
        "comment_track": {"author": "AUTOMATIC", "text_source": "CODE_TEMPLATE_v1", "ai_text": None,
                          "ai_text_model": None,
                          "note": "AI-written text is a separately registered Challenger C; until then ai_text stays null."},
        "inputs": {},
        "models": {},
        "kompas_views": {"1_3d": None, "5_7d": None},
        "assets": {},
    }


def build(root: Path, latest_json: Path | None, now: dt.datetime) -> dict:
    doc = base_document(now)
    params, prereg = load_prereg(root)
    model = {"name": "Challenger B", "status": "TRIAL", "contract": B_CONTRACT, "formula_version": B_FORMULA_VERSION,
             "applied": params is not None, "reason": prereg["reason"],
             "tilt": params["tilt"] if params else None,
             "short_horizon_hours": params["short_horizon_hours"] if params else None,
             "line": "TILTED" if params else "FLAT",
             "sigma_estimator": f"std of last {SIGMA_WINDOW_HOURS} hourly log returns, ddof={SIGMA_DDOF}"}
    frames = {"name": "Challenger A", "status": "TRIAL", **load_a_z(root, now)}
    doc["models"] = {"line": model, "frames": frames}
    week_start = week_monday(now)
    bound, official_binding = bound_official_packet(root, now)
    packets = load_packets(root, min(now - PACKET_LOOKBACK_HOURS * HOUR, week_start - 2 * DAY), now)
    in_window = [bound] if bound is not None else []
    doc["official_source_valid_until_utc"] = official_binding.get("valid_until_utc") if bound else None
    # A discovered historical daily packet NEVER substitutes for the current canonical pointer.
    views = select_views(in_window, now)
    doc["kompas_views"] = views
    zones, zone_status = frozen_zones(latest_json, now)
    start = now - (max(SIGMA_WINDOW_HOURS + 1, NORM_WINDOW_HOURS, DISPLAY_BACK_HOURS, (now - week_start) // HOUR + 2) + 2) * HOUR
    series, files = load_hourly(root, start, now)
    doc["inputs"] = {"hourly": {"dir": HOURLY_DIR, "row_filter": "spot_status PASS/OK, low<=close<=high, hour-aligned",
                                "files": files},
                     "packets": {"dir": PACKET_DIR, "lookback_hours": PACKET_LOOKBACK_HOURS,
                                 "valid_in_window": len(in_window)},
                     "challenger_b_prereg": prereg,
                     "challenger_a_issuance": {"path": frames["a_issuance_path"], "sha256": frames["a_issuance_sha256"],
                                               "used": frames["z_source"] == "CHALLENGER_A_FROZEN_ISSUANCE"},
                     "frozen_zone": zone_status, "official_compass": official_binding}
    reasons = []
    if not in_window:
        reasons.append(official_binding["reason"] or "OFFICIAL_POINTER_PACKAGE_UNAVAILABLE")
    for asset in ASSETS:
        if reasons:
            doc["assets"][asset] = {"status": "UNAVAILABLE", "reason": reasons[0], "quote": QUOTE}
            continue
        try:
            doc["assets"][asset] = asset_block(asset, series[asset], now, views, model, frames,
                                               zones.get(asset), packets, week_start)
        except Unavailable as exc:
            doc["assets"][asset] = {"status": "UNAVAILABLE", "reason": str(exc), "quote": QUOTE}
    ok = [a for a, b in doc["assets"].items() if b["status"] == "OK"]
    doc["status"] = "OK" if len(ok) == len(ASSETS) else ("PARTIAL" if ok else "UNAVAILABLE")
    doc["reasons"] = sorted({b["reason"] for b in doc["assets"].values() if b.get("reason")} | set(reasons))
    return doc


def failure_document(now: dt.datetime, reason: str) -> dict:
    doc = base_document(now)
    doc["reasons"] = [reason]
    doc["assets"] = {a: {"status": "UNAVAILABLE", "reason": reason, "quote": QUOTE} for a in ASSETS}
    return doc


def seal(doc: dict) -> dict:
    doc.pop("path_sha256", None)
    doc["path_sha256"] = digest(doc)
    return doc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--latest-json", default="05_CYCLE_NAVIGATOR/site/dist/data/latest.json")
    ap.add_argument("--output", default="05_CYCLE_NAVIGATOR/site/dist/data/kompas-live.json")
    ap.add_argument("--now", help="issue clock, ISO-8601 with timezone (default: current UTC time)")
    a = ap.parse_args(argv)
    now = utc(a.now) if a.now else dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    root = Path(a.repo_root)
    try:
        doc = build(root, Path(a.latest_json) if a.latest_json else None, now)
    except Exception as exc:  # never block the canonical Pages build; publish an honest UNAVAILABLE instead
        doc = failure_document(now, "PRODUCER_ERROR:" + type(exc).__name__)
        print(f"::warning::KOMPAS_LIVE_PRODUCER_ERROR {type(exc).__name__}", file=sys.stderr)
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(seal(doc), indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = {"contract": CONTRACT, "status": doc["status"], "reasons": doc["reasons"],
               "line": doc.get("models", {}).get("line", {}).get("line"),
               "z_source": doc.get("models", {}).get("frames", {}).get("z_source")}
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
