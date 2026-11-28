"""C5 context-only adapters for existing FRED and OKX capture owners.

No collection, network, scoring, forecast changes or raw-publication authority.
The OKX totals are captured lower bounds, never total market liquidation volume.
"""
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from statistics import median
from zoneinfo import ZoneInfo
import json
import math
import re

from scripts.data_terminal import fred_csv_collector as fred
from scripts.daily_capture import pullback_forensics_collector as pfr
from scripts.master_monday.build_preflight_package_v3 import nyse_full_day_holidays
from scripts.research.vix_term_structure_shadow_v1 import features

VIX_SERIES = ("VIXCLS", "VXVCLS")
FRED_MAX_CAPTURE_HOURS = 36
OKX_MAX_CAPTURE_HOURS = 6
NON_SCORING = "CONTEXT_ONLY_NOT_DECISION_OR_SCORING"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def utc(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value
    if not isinstance(dt, datetime) or dt.utcoffset() is None:
        raise ValueError("INVALID_CLOCK")
    return dt.astimezone(timezone.utc)


def iso(value):
    return utc(value).isoformat().replace("+00:00", "Z")


def is_hash(value):
    return isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value) is not None


def seal(value):
    return {**value, "context_sha256": digest(value)}


def valid_seal(value):
    return isinstance(value, dict) and is_hash(value.get("context_sha256")) and value["context_sha256"] == digest({k: v for k, v in value.items() if k != "context_sha256"})


def unavailable(reason):
    return seal({"status": "UNAVAILABLE", "reason": reason, "authority": NON_SCORING, "scoring_allowed": False})


def business_day(day):
    holidays = set().union(*(nyse_full_day_holidays(y) for y in (day.year-1, day.year, day.year+1)))
    return day.weekday() < 5 and day not in holidays


def session_close(day):
    return datetime(day.year, day.month, day.day, 16, tzinfo=ZoneInfo("America/New_York")).astimezone(timezone.utc)


def conservative_release(day):
    day += timedelta(days=1)
    while not business_day(day):
        day += timedelta(days=1)
    return datetime(day.year, day.month, day.day, 21, tzinfo=timezone.utc)


def fred_from_payload(payload, capture_run_id, captured_at, cutoff, pit_method="NATIVE_CAPTURE"):
    """All historical observations are known at this capture, not at earlier issues."""
    try:
        captured_at, cutoff = utc(captured_at), utc(cutoff)
        if not re.fullmatch(r"gh-[0-9]+-[0-9]+", capture_run_id or ""):
            return unavailable("FRED_NATIVE_RUN_ID_UNVERIFIED")
        if not captured_at < cutoff or cutoff-captured_at > timedelta(hours=FRED_MAX_CAPTURE_HOURS):
            return unavailable("FRED_CAPTURE_CLOCK_INVALID_OR_STALE")
        if pit_method not in ("NATIVE_CAPTURE", "CONSERVATIVE_RELEASE_LAG"):
            return unavailable("FRED_PIT_METHOD_INVALID")
        observed, _ = fred.parse_fred_csv(payload, VIX_SERIES)
        # Expected sessions are constrained by FRED dates AND the existing
        # NYSE full-day calendar. Unknown closures and missing rows fail closed.
        by_series = {s: {date.fromisoformat(r.date[:10]): r.value for r in observed[s]} for s in VIX_SERIES}
        days = []
        cursor = captured_at.astimezone(ZoneInfo("America/New_York")).date()
        for _ in range(20):
            if business_day(cursor) and session_close(cursor) < captured_at:
                if pit_method == "NATIVE_CAPTURE" or conservative_release(cursor) <= captured_at:
                    days.append(cursor)
            if len(days) == 4:
                break
            cursor -= timedelta(days=1)
        days.reverse()
        if len(days) != 4 or any(day not in by_series[s] for day in days for s in VIX_SERIES):
            return unavailable("FRED_MATCHED_SESSION_GAP")
        source_hash = sha256(payload).hexdigest()
        rows, sessions = [], []
        for day in days:
            close = session_close(day)
            known = captured_at if pit_method == "NATIVE_CAPTURE" else conservative_release(day)
            sessions.append({"date": day.isoformat(), "close_utc": iso(close)})
            for series in VIX_SERIES:
                rows.append({"date": day.isoformat(), "series": series, "value": by_series[series][day],
                             "available_at_utc": iso(known), "captured_at_utc": iso(captured_at),
                             "payload_sha256": source_hash})
        result = features(rows, sessions, iso(cutoff))["features"]
        ratio = float(result["vix_3m_ratio"])
        term = "INVERTED" if result["inverted_index_term_structure"] else "FLAT" if ratio == 1 else "CONTANGO"
        return seal({"status": "AVAILABLE", "authority": NON_SCORING, "scoring_allowed": False,
                     "source_class": "FRED_CBOE_TERM_STRUCTURE", "pit_method": pit_method,
                     "source_sha256": source_hash, "capture_run_id": capture_run_id,
                     "as_of_utc": iso(captured_at), "session_date": days[-1].isoformat(),
                     "term_structure_class": term, "vix_3m_ratio": round(ratio, 3),
                     "ratio_change_3_sessions": round(float(result["ratio_change_3_sessions"]), 3)})
    except (TypeError, ValueError, KeyError, OSError, fred.CollectorError, ArithmeticError):
        return unavailable("FRED_INPUT_INVALID")


def capture_fred_context(directory, capture_run_id, captured_at, cutoff, owner_exit_code):
    if owner_exit_code == 78:
        return unavailable("FRED_NOT_SCHEDULED")
    if owner_exit_code != 0:
        return unavailable("FRED_CAPTURE_FAILED")
    try:
        receipts = list((directory / "receipts").glob("*__receipt.json"))
        if len(receipts) != 1:
            return unavailable("FRED_RECEIPT_MISSING_OR_AMBIGUOUS")
        receipt = json.loads(receipts[0].read_text())
        if receipt.get("source_id") != "FRED_CSV_MACRO_CORE" or not set(VIX_SERIES) <= set(receipt.get("series", [])):
            return unavailable("FRED_RECEIPT_SCOPE_INVALID")
        if receipt.get("source_substitution") != {"used": False, "substitute_source_id": None, "reason": None} or receipt.get("conflicts") != []:
            return unavailable("FRED_RECEIPT_SCOPE_INVALID")
        if receipt.get("receipt_sha256") != fred.sha256_bytes(fred.canonical_json_bytes({k: v for k, v in receipt.items() if k != "receipt_sha256"})):
            return unavailable("FRED_RECEIPT_HASH_MISMATCH")
        raw_files = list((directory / "raw").glob("*__fred.csv"))
        if len(raw_files) != 1 or fred.verify_artifact_readback(directory).get("status") != "PASS":
            return unavailable("FRED_ARTIFACT_UNVERIFIED")
        payload = raw_files[0].read_bytes()
        if sha256(payload).hexdigest() != receipt.get("payload_sha256") or utc(receipt["retrieval_timestamp"]) > utc(captured_at):
            return unavailable("FRED_SOURCE_BINDING_INVALID")
        observed, _ = fred.parse_fred_csv(payload, VIX_SERIES)
        if any(receipt["source_timestamps"].get(s) != observed[s][-1].date for s in VIX_SERIES):
            return unavailable("FRED_SOURCE_IDENTITY_INVALID")
        return fred_from_payload(payload, capture_run_id, captured_at, cutoff)
    except (OSError, TypeError, KeyError, ValueError, fred.CollectorError):
        return unavailable("FRED_CAPTURE_UNVERIFIED")


def latest_fred_context(root, cutoff):
    cutoff = utc(cutoff)
    anchor_root = root / "03_DAILY_CAPTURE_LOGS/captures"
    candidates = []
    try:
        for offset in range(8):
            day = cutoff.date()-timedelta(days=offset)
            for path in (anchor_root / day.strftime("%Y/%m/%d")).glob("*.json"):
                packet = json.loads(path.read_text())
                if packet.get("contract") != "DAILY_LIVE_ANCHOR_INDEX_v3":
                    continue
                stamp = utc(packet["captured_at_utc"])
                row = packet.get("c5_vix_context")
                if stamp >= cutoff or not isinstance(row, dict) or row.get("reason") == "FRED_NOT_SCHEDULED":
                    continue
                candidates.append((stamp, packet.get("run_id"), row))
        if not candidates:
            return unavailable("FRED_C5_CAPTURE_NOT_AVAILABLE")
        stamp, run_id, row = max(candidates, key=lambda t: t[0])
        if not valid_seal(row) or row.get("authority") != NON_SCORING or row.get("scoring_allowed") is not False:
            return unavailable("FRED_CONTEXT_INTEGRITY_INVALID")
        if row.get("status") != "AVAILABLE":
            return unavailable(row.get("reason") if isinstance(row.get("reason"), str) and re.fullmatch(r"FRED_[A-Z_]+", row["reason"]) else "FRED_CAPTURE_UNVERIFIED")
        if row.get("capture_run_id") != run_id or utc(row["as_of_utc"]) != stamp or not is_hash(row.get("source_sha256")):
            return unavailable("FRED_CONTEXT_BINDING_INVALID")
        if cutoff-stamp > timedelta(hours=FRED_MAX_CAPTURE_HOURS):
            return unavailable("FRED_CAPTURE_STALE")
        return row
    except (OSError, ValueError, KeyError, TypeError):
        return unavailable("FRED_CONTEXT_UNVERIFIED")


def verified_pfr(raw):
    value = json.loads(raw)
    if value.get("contract") != "PULLBACK_FORENSICS_PASSIVE_CAPTURE_v1":
        raise ValueError("PFR_CONTRACT")
    if value.get("payload_sha256") != pfr.sha256_bytes(pfr.canonical_bytes({k: v for k, v in value.items() if k != "payload_sha256"})):
        raise ValueError("PFR_DIGEST")
    return value


def asset_pass(row, asset):
    return row.get("lane1_liquidations", {}).get(asset, {}).get("status") == "PASS"


def window_aggregates(events, captures, end, asset, hours, baseline_windows):
    end = utc(end)
    selected = {}
    for row in events:
        if row.get("inst_id") != asset+"-USDT-SWAP":
            continue
        ident = row["event_id"]
        ts = row["event_timestamp_ms"]
        value = row["notional_usd"]
        side = row["pos_side"]
        if not isinstance(ident, str) or not ident or type(ts) != int or type(value) not in (int, float) or not math.isfinite(value) or value < 0 or side not in ("long", "short") or row.get("notional_method") != "OKX_CONTRACT_UNIT_NORMALIZATION_v1" or not is_hash(row.get("source_payload_sha256")):
            raise ValueError("OKX_EVENT_INVALID")
        data = (ts, side, value, row["source_payload_sha256"])
        if ident in selected and selected[ident] != data:
            raise ValueError("OKX_DUPLICATE_CONFLICT")
        selected[ident] = data
    pass_times = [utc(x["observed_at_utc"]) for x in captures if asset_pass(x, asset)]
    def covered(left, right):
        # One verified successful capture per 24h subwindow is a minimum
        # observability floor, NOT proof of complete venue coverage.
        cursor = left
        while cursor < right:
            next_day = min(cursor+timedelta(days=1), right)
            if not any(cursor < t <= next_day for t in pass_times):
                return False
            cursor = next_day
        return True
    def totals(left, right):
        lo, hi = int(left.timestamp()*1000), int(right.timestamp()*1000)
        return tuple(sum(x[2] for x in selected.values() if lo < x[0] <= hi and x[1] == side) for side in ("long", "short"))
    delta = timedelta(hours=hours)
    if not covered(end-delta, end):
        return {"status": "UNAVAILABLE", "reason": "OKX_CAPTURE_COVERAGE_GAP", "pressure_class": "UNAVAILABLE"}
    long, short = totals(end-delta, end)
    base = []
    for i in range(1, baseline_windows+1):
        right = end-i*delta
        if covered(right-delta, right):
            base.append(sum(totals(right-delta, right)))
    # Preregistered context-only bands: lower bound vs prior disjoint windows.
    reference = median(base) if len(base) == baseline_windows else 0
    pressure = "UNAVAILABLE" if reference <= 0 else "HIGH" if long+short >= 2*reference else "LOW" if long+short <= .5*reference else "NORMAL"
    return {"status": "AVAILABLE_LOWER_BOUND", "long_notional_usd": int(round(long,-3)),
            "short_notional_usd": int(round(short,-3)), "pressure_class": pressure,
            "baseline_windows_available": len(base), "baseline_windows_required": baseline_windows,
            "pressure_reason": "OKX_BASELINE_INCOMPLETE_OR_ZERO" if pressure == "UNAVAILABLE" else "OBSERVED_NOTIONAL_VS_TRAILING_MEDIAN"}


def liquidation_context(root, cutoff):
    cutoff = utc(cutoff)
    directory = root / "03_DAILY_CAPTURE_LOGS/pullback_forensics"
    try:
        latest_raw = (directory / "LATEST.json").read_bytes()
        latest = verified_pfr(latest_raw)
        observed = utc(latest["observed_at_utc"])
        run = latest["run_id"]
        if not re.fullmatch(r"pfr-[0-9]+-[0-9]+", run or "") or observed >= cutoff or cutoff-observed > timedelta(hours=OKX_MAX_CAPTURE_HOURS):
            return unavailable("OKX_CAPTURE_CLOCK_INVALID_OR_STALE")
        runs = directory / "runs"
        target = runs / observed.strftime("%Y/%m/%d") / run / "PULLBACK_FORENSICS.json"
        if target.read_bytes() != latest_raw:
            return unavailable("OKX_LATEST_RUN_BINDING_INVALID")
        captures = []
        for i in range(36):
            day = observed.date()-timedelta(days=i)
            for path in (runs / day.strftime("%Y/%m/%d")).glob("*/PULLBACK_FORENSICS.json"):
                try:
                    rec = verified_pfr(path.read_bytes())
                    stamp = utc(rec["observed_at_utc"])
                    if stamp <= observed and rec.get("run_id") == path.parent.name:
                        captures.append(rec)
                except (OSError, KeyError, TypeError, ValueError):
                    continue
        events = pfr.load_events_since(directory, observed, 35*24)
        assets = {}
        for asset in ("BTC", "ETH"):
            if not asset_pass(latest, asset):
                assets[asset] = {"status": "UNAVAILABLE", "reason": "OKX_LATEST_ASSET_CAPTURE_FAILED"}
                continue
            assets[asset] = {"24h": window_aggregates(events, captures, observed, asset, 24, 28),
                             "7d": window_aggregates(events, captures, observed, asset, 168, 4)}
        # Hash input identities, capture receipts and normalized event evidence;
        # only the digest and derived rounded aggregates leave this function.
        source_hash = digest({"latest": latest["payload_sha256"],
                              "capture_receipts": sorted({r["payload_sha256"] for r in captures}),
                              "event_bindings": sorted([(r["event_id"], r["event_timestamp_ms"], r["inst_id"], r["pos_side"], r["notional_usd"], r["source_payload_sha256"]) for r in events])})
        available = any(v.get(h, {}).get("status") == "AVAILABLE_LOWER_BOUND" for v in assets.values() for h in ("24h", "7d"))
        return seal({"status": "AVAILABLE_LOWER_BOUND" if available else "UNAVAILABLE",
                     "reason": "OKX_OBSERVED_LOWER_BOUND_NOT_TOTAL_MARKET" if available else "OKX_CAPTURE_COVERAGE_GAP",
                     "authority": NON_SCORING, "scoring_allowed": False,
                     "source_class": "OKX_REALIZED_CAPTURED_LIQUIDATIONS", "pit_method": "NATIVE_CAPTURE",
                     "capture_run_id": run, "source_sha256": source_hash, "as_of_utc": iso(observed), "assets": assets})
    except (OSError, TypeError, ValueError, KeyError, ArithmeticError):
        return unavailable("OKX_CAPTURE_UNVERIFIED")


def build_c5_context(root, cutoff):
    macro = latest_fred_context(root, cutoff)
    deriv = liquidation_context(root, cutoff)
    available = macro.get("status") == "AVAILABLE", deriv.get("status") == "AVAILABLE_LOWER_BOUND"
    return seal({"contract": "C5_MM_CONTEXT_v1", "status": "AVAILABLE" if all(available) else "PARTIAL" if any(available) else "UNAVAILABLE",
                 "as_of_utc": iso(cutoff), "authority": NON_SCORING, "scoring_allowed": False,
                 "macro": macro, "realized_liquidations": deriv})
