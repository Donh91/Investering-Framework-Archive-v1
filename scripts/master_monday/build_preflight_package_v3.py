from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

STATUSES = ("PASS", "PARTIAL", "STALE", "FAIL", "UNAVAILABLE", "SKIPPED_RUNTIME_LIMIT")
CAPTURE_V22_ACTIVATION_WEEK = (2026, 32)


def load(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def parse_ts(value: Any) -> datetime | None:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None


def latest_capture(root: Path) -> tuple[Path | None, dict[str, Any] | None]:
    rows: list[tuple[datetime, Path, dict[str, Any]]] = []
    if root.exists():
        for path in root.rglob("*.json"):
            if path.name == "LATEST.json":
                continue
            value = load(path)
            if not value or value.get("contract") != "DAILY_LIVE_ANCHOR_INDEX_v3":
                continue
            stamp = parse_ts(value.get("captured_at_utc"))
            if stamp:
                rows.append((stamp, path, value))
    if not rows:
        return None, None
    rows.sort(key=lambda row: row[0])
    return rows[-1][1], rows[-1][2]


def latest_hourly(root: Path) -> tuple[Path | None, dict[str, str] | None]:
    best: tuple[datetime, Path, dict[str, str]] | None = None
    if root.exists():
        for path in root.rglob("*.csv"):
            try:
                with path.open(newline="", encoding="utf-8") as handle:
                    for row in csv.DictReader(handle):
                        stamp = parse_ts(row.get("timestamp_utc"))
                        if stamp and (best is None or stamp > best[0]):
                            best = (stamp, path, row)
            except Exception:
                continue
    return (None, None) if best is None else (best[1], best[2])


def resolve_capture_pointer(capture_root: Path, raw_path: Any) -> Path | None:
    if not raw_path:
        return None
    path = Path(str(raw_path))
    if path.is_absolute():
        return path
    if path.parts[:1] == (capture_root.name,):
        return capture_root.parent / path
    if path.parts[:2] == ("03_DAILY_CAPTURE_LOGS", "weekly_close") or path.parts[:2] == ("03_DAILY_CAPTURE_LOGS", "weekly"):
        return capture_root.parent / path
    return capture_root / path


def classify_ping(row: dict[str, Any]) -> str:
    cls = str(row.get("authority_class") or row.get("packet_class") or row.get("scope") or "").upper()
    if cls in {"CANONICAL", "CANONICAL_ACCEPTED"}:
        return "canonical_data_pings"
    if cls in {"BOUNDED", "BOUNDED_DECISION_BEARING", "DECISION_BEARING"}:
        return "bounded_decision_bearing_pings"
    if cls in {"RUNTIME_LIMITED", "RUNTIME_LIMITED_SUPPLEMENT"}:
        return "runtime_limited_supplements"
    return "qa_and_research_only"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--predecessor-registry", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--freeze-start-utc")
    ap.add_argument("--freeze-end-utc")
    args = ap.parse_args()

    root = args.repo_root
    registry = load(args.registry) or {}
    predecessor = load(args.predecessor_registry) or {}
    if registry.get("planned_core_actions") != 60:
        raise SystemExit("ACTION_REGISTRY_NOT_60")

    capture_root = root / "03_DAILY_CAPTURE_LOGS"
    cap_path, cap = latest_capture(capture_root / "captures")
    hourly_path, hourly = latest_hourly(capture_root / "hourly")
    market_metrics = (cap or {}).get("market_metrics") or {}
    breadth = market_metrics.get("breadth") or {}
    derivatives = market_metrics.get("derivatives") or {}
    macro = market_metrics.get("macro") or {}
    micro = market_metrics.get("microstructure") or {}

    close_pointer_path = capture_root / "weekly_close" / "LATEST_WEEKLY_MARKET_CLOSE.json"
    close_pointer = load(close_pointer_path) or {}
    close_package_path = resolve_capture_pointer(capture_root, close_pointer.get("path"))
    close_package = load(close_package_path) if close_package_path and close_package_path.exists() else None

    weekly_pointer_path = capture_root / "weekly" / "LATEST_WEEKLY_CALIBRATION.json"
    weekly_pointer = load(weekly_pointer_path) or {}
    weekly_pack_path = resolve_capture_pointer(capture_root, weekly_pointer.get("path"))
    weekly_pack = load(weekly_pack_path) if weekly_pack_path and weekly_pack_path.exists() else None

    etf_pointer_path = capture_root / "etf" / "LATEST.json"
    etf_pointer = load(etf_pointer_path) or {}
    etf_record_path = resolve_capture_pointer(capture_root, etf_pointer.get("path"))
    etf_record = load(etf_record_path) if etf_record_path and etf_record_path.exists() else None

    lanes = {key: [] for key in ("canonical_data_pings", "bounded_decision_bearing_pings", "runtime_limited_supplements", "qa_and_research_only")}
    seen: set[tuple[Any, Any]] = set()
    start = parse_ts(args.freeze_start_utc) if args.freeze_start_utc else None
    end = parse_ts(args.freeze_end_utc) if args.freeze_end_utc else None
    accepted_root = root / "research" / "data_ping_bridge" / "accepted"
    if accepted_root.exists():
        for path in sorted(accepted_root.rglob("*.json")):
            row = load(path)
            if not row or row.get("contract") != "ACCEPTED_DATA_PING_PACKET_v1":
                continue
            key = (row.get("run_id"), row.get("snapshot_id"))
            if key in seen:
                continue
            stamp = parse_ts(row.get("freeze_utc"))
            if not stamp or (start and stamp < start) or (end and stamp >= end):
                continue
            seen.add(key)
            bucket = classify_ping(row)
            lanes[bucket].append({
                "path": str(path), "sha256": digest(row), "run_id": row.get("run_id"),
                "snapshot_id": row.get("snapshot_id"), "freeze_utc": row.get("freeze_utc"),
            })

    ledger: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []

    def add(aid: str, group: str, name: str, status: str, field: str, existing: Any, required: str, collector: str, *, blocking: bool = False) -> None:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        ledger.append({
            "action_id": aid, "group": group, "action_name": name, "status": status, "field": field,
            "source_timestamp": None, "retrieval_timestamp": now,
            "error_evidence_id": None if status == "PASS" else f"{aid}_{status}", "optional": not blocking,
        })
        if status != "PASS":
            missing.append({
                "action_id": aid, "field": field,
                "blocking_level": "BLOCKING" if blocking and status in {"FAIL", "UNAVAILABLE", "SKIPPED_RUNTIME_LIMIT"} else "CONFIDENCE_REDUCING",
                "reason": status, "existing_evidence": existing, "required_evidence": required,
                "suggested_collector": collector,
            })

    canonical_ok = predecessor.get("status") == "ACTIVE" and predecessor.get("predecessor_scope") == "CANONICAL_ACCEPTED_MARKET_PREDECESSOR"
    add("A01", "identity_predecessor", "identity_freeze", "PASS" if cap else "UNAVAILABLE", "packet.freeze", str(cap_path) if cap_path else None, "latest durable live anchor", "Daily Live Anchor", blocking=True)
    add("A02", "identity_predecessor", "canonical_predecessor_registry", "PASS" if canonical_ok else "PARTIAL", "comparison.canonical_predecessor", predecessor or None, "active predecessor or explicit absence", "predecessor registry")
    add("A03", "identity_predecessor", "single_freeze_contract", "PASS", "packet.freeze_count", 1, "exactly one deterministic freeze", "weekly orchestration", blocking=True)
    add("A04", "identity_predecessor", "accepted_data_ping_inventory", "PASS", "meta.data_ping_lanes", sum(len(v) for v in lanes.values()), "classified inventory including zero", "DATA PING bridge")

    direct_fields = [("A05", "BTCUSDT", "btc_close"), ("A06", "ETHUSDT", "eth_close"), ("A07", "ETHBTC", "ethbtc_close")]
    for aid, name, field in direct_fields:
        value = (hourly or {}).get(field)
        add(aid, "current_spot", name, "PASS" if value not in (None, "") else "UNAVAILABLE", f"current_market.{name}", value, f"direct settled hourly {name}", "Hourly Sequence v2.2", blocking=True)
    has_micro = bool((micro.get("symbols") or {}).get("BTCUSDT")) and bool((micro.get("symbols") or {}).get("ETHUSDT"))
    add("A08", "current_spot", "order_book", "PARTIAL" if has_micro else "UNAVAILABLE", "current_market.order_book", micro.get("symbols"), "BTC/ETH microstructure; ETHBTC book optional", "Live Anchor microstructure")
    add("A09", "current_spot", "24h_ticker", "PARTIAL" if hourly else "UNAVAILABLE", "current_market.ticker_24h", {"latest_hour": (hourly or {}).get("timestamp_utc")}, "current direct market context", "Hourly Sequence v2.2")
    add("A10", "current_spot", "server_time", "PASS" if hourly and hourly.get("source_window_end_utc") else "UNAVAILABLE", "current_market.server_time", (hourly or {}).get("source_window_end_utc"), "source-window timestamp", "Hourly Sequence v2.2", blocking=True)

    symbols = (close_package or {}).get("symbols") or {}
    final_close_ok = bool(close_package and close_package.get("final") is True and close_package.get("completeness") == "COMPLETE" and close_package.get("close_mode") == "FINAL_COMPLETED_ISO_WEEK")
    for aid, asset in (("A11", "BTCUSDT"), ("A12", "ETHUSDT"), ("A13", "ETHBTC")):
        row = symbols.get(asset) or {}
        ok = final_close_ok and row.get("hour_count") == 168 and len(row.get("daily_ranges") or []) == 7
        add(aid, "settled_sessions", f"FINAL_{asset}", "PASS" if ok else "UNAVAILABLE", f"settled_sessions.{asset}", row if row else None, "7 settled UTC ISO-day rows / 168 hours", "Final Weekly Market Close", blocking=True)
    ethbtc_daily = (symbols.get("ETHBTC") or {}).get("daily_ranges") or []
    add("A14", "settled_sessions", "threshold_tests", "PASS" if ethbtc_daily else "UNAVAILABLE", "settled_sessions.threshold_tests", {"daily_rows": len(ethbtc_daily)}, "settled ETHBTC rows sufficient for frozen threshold evaluation", "Final Weekly Market Close", blocking=True)
    add("A15", "settled_sessions", "UTC_local_separation", "PASS" if final_close_ok and close_package.get("window_end_utc") else "UNAVAILABLE", "settled_sessions.session_basis", {"basis": "UTC_ISO_WEEK", "window_end_utc": (close_package or {}).get("window_end_utc")}, "explicit settled-session basis", "Final Weekly Market Close", blocking=True)

    btc_daily = (symbols.get("BTCUSDT") or {}).get("daily_ranges") or []
    eth_daily = (symbols.get("ETHUSDT") or {}).get("daily_ranges") or []
    add("A16", "weekly_daily_structure", "BTC_daily_table", "PASS" if len(btc_daily) == 7 else "UNAVAILABLE", "week_daily_intraday.BTCUSDT", btc_daily, "7 UTC daily rows", "Final Weekly Market Close", blocking=True)
    add("A17", "weekly_daily_structure", "ETH_daily_table", "PASS" if len(eth_daily) == 7 else "UNAVAILABLE", "week_daily_intraday.ETHUSDT", eth_daily, "7 UTC daily rows", "Final Weekly Market Close", blocking=True)
    tieout = final_close_ok and all((symbols.get(asset) or {}).get("hour_count") == 168 for asset in ("BTCUSDT", "ETHUSDT", "ETHBTC"))
    add("A18", "weekly_daily_structure", "weekly_tieout", "PASS" if tieout else "UNAVAILABLE", "week_daily_intraday.weekly_daily_tieout", {"all_assets_168h": tieout}, "168/168 for BTC, ETH and ETHBTC", "Final Weekly Market Close", blocking=True)
    add("A19", "weekly_daily_structure", "gap_duplicate_QA", "PASS" if tieout else "UNAVAILABLE", "week_daily_intraday.gap_duplicate_qa", {asset: (symbols.get(asset) or {}).get("hour_count") for asset in ("BTCUSDT", "ETHUSDT", "ETHBTC")}, "zero missing settled market-close hours", "Final Weekly Market Close", blocking=True)

    constituents = int(breadth.get("constituent_count") or 0)
    advancers = breadth.get("advancers")
    aggregate = None if not constituents or advancers is None else float(advancers) / float(constituents)
    add("A20", "breadth", "aggregate", "PASS" if aggregate is not None else "UNAVAILABLE", "breadth.aggregate", aggregate, "advance ratio from durable point-in-time breadth", "Live Anchor breadth", blocking=True)
    add("A21", "breadth", "membership_hash", "PASS" if breadth.get("membership_hash") else "UNAVAILABLE", "breadth.membership_hash", breadth.get("membership_hash"), "deterministic membership hash", "Live Anchor breadth", blocking=True)
    add("A22", "breadth", "constituent_sidecar", "UNAVAILABLE", "breadth.constituent_sidecar", None, "optional constituent sidecar", "breadth owner")
    add("A23", "breadth", "exclusion_sidecar", "UNAVAILABLE", "breadth.exclusion_sidecar", None, "optional exclusion sidecar", "breadth owner")
    add("A24", "breadth", "median_mean", "UNAVAILABLE", "breadth.median_mean", None, "median/equal-weight context when owner-captured", "DATA PING / breadth owner")
    add("A25", "breadth", "gates", "PARTIAL" if aggregate is not None else "UNAVAILABLE", "breadth.gates", {"advance_ratio": aggregate}, "raw breadth evidence; interpretation deferred", "main framework")
    add("A26", "breadth", "longitudinal_permission", "PASS" if cap and cap.get("weekly_calibration_eligible") else "PARTIAL", "breadth.longitudinal_permission", (cap or {}).get("weekly_calibration_eligible"), "eligible durable anchor", "Live Anchor")

    btc_deriv = derivatives.get("BTC-USDT-SWAP") or {}
    eth_deriv = derivatives.get("ETH-USDT-SWAP") or {}
    btc_funding = (btc_deriv.get("funding") or {}).get("funding_rate")
    eth_funding = (eth_deriv.get("funding") or {}).get("funding_rate")
    btc_oi = (hourly or {}).get("btc_open_interest")
    eth_oi = (hourly or {}).get("eth_open_interest")
    btc_ls = (hourly or {}).get("btc_long_short_ratio")
    eth_ls = (hourly or {}).get("eth_long_short_ratio")
    add("A27", "binance_derivatives", "BTC_funding", "PASS" if btc_funding is not None else "UNAVAILABLE", "derivatives.BTC_funding", btc_funding, "current funding", "Live Anchor derivatives", blocking=True)
    add("A28", "binance_derivatives", "ETH_funding", "PASS" if eth_funding is not None else "UNAVAILABLE", "derivatives.ETH_funding", eth_funding, "current funding", "Live Anchor derivatives", blocking=True)
    add("A29", "binance_derivatives", "funding_history", "PARTIAL" if hourly else "UNAVAILABLE", "derivatives.funding_history", {"btc_event": (hourly or {}).get("btc_funding_event_rate"), "eth_event": (hourly or {}).get("eth_funding_event_rate")}, "hourly funding-event sequence when present", "Hourly Sequence v2.2")
    add("A30", "binance_derivatives", "OI_anchors", "PASS" if btc_oi not in (None, "") and eth_oi not in (None, "") else "UNAVAILABLE", "derivatives.OI_anchors", {"BTC": btc_oi, "ETH": eth_oi}, "BTC+ETH hourly OI", "Hourly Sequence v2.2", blocking=True)
    add("A31", "binance_derivatives", "long_short", "PASS" if btc_ls not in (None, "") and eth_ls not in (None, "") else "UNAVAILABLE", "derivatives.long_short", {"BTC": btc_ls, "ETH": eth_ls}, "BTC+ETH global long/short", "Hourly Sequence v2.2", blocking=True)
    add("A32", "binance_derivatives", "top_accounts", "UNAVAILABLE", "derivatives.top_accounts", None, "optional top-account positioning", "DATA PING")
    add("A33", "binance_derivatives", "top_positions", "UNAVAILABLE", "derivatives.top_positions", None, "optional top-position positioning", "DATA PING")
    flow = {"btc_taker_buy_quote_share": (hourly or {}).get("btc_taker_buy_quote_share"), "eth_taker_buy_quote_share": (hourly or {}).get("eth_taker_buy_quote_share")}
    add("A34", "binance_derivatives", "taker_flow", "PARTIAL" if all(v not in (None, "") for v in flow.values()) else "UNAVAILABLE", "derivatives.taker_flow", flow, "spot taker share; futures taker optional", "Hourly Sequence v2.2")
    rolling = (weekly_pack or {}).get("hourly_sequence") or {}
    add("A35", "binance_derivatives", "multiwindow_price", "PARTIAL" if weekly_pack else "UNAVAILABLE", "derivatives.multiwindow_price", {"weekly_readiness": weekly_pointer.get("readiness"), "hourly_rows": weekly_pointer.get("hourly_rows")}, "4/12/24/48/72h enriched sequence where prospectively available", "Weekly Calibration v2.2")
    add("A36", "binance_derivatives", "close_location", "PASS" if final_close_ok else "UNAVAILABLE", "derivatives.close_location", {asset: (symbols.get(asset) or {}).get("weekly_close") for asset in ("BTCUSDT", "ETHUSDT")}, "final weekly closes", "Final Weekly Market Close")

    add("A37", "okx_crosscheck", "BTC_ticker", "PARTIAL" if btc_deriv.get("mark_price") else "UNAVAILABLE", "okx.BTC_ticker", btc_deriv.get("mark_price"), "OKX BTC mark/current derivatives", "Live Anchor")
    add("A38", "okx_crosscheck", "ETH_ticker", "PARTIAL" if eth_deriv.get("mark_price") else "UNAVAILABLE", "okx.ETH_ticker", eth_deriv.get("mark_price"), "OKX ETH mark/current derivatives", "Live Anchor")
    add("A39", "okx_crosscheck", "funding", "PASS" if btc_funding is not None and eth_funding is not None else "UNAVAILABLE", "okx.funding", {"BTC": btc_funding, "ETH": eth_funding}, "OKX BTC+ETH funding", "Live Anchor", blocking=True)
    oi_cross = {"BTC": (btc_deriv.get("open_interest") or {}).get("open_interest_ccy"), "ETH": (eth_deriv.get("open_interest") or {}).get("open_interest_ccy")}
    add("A40", "okx_crosscheck", "OI", "PASS" if all(value is not None for value in oi_cross.values()) else "UNAVAILABLE", "okx.open_interest", oi_cross, "OKX BTC+ETH OI", "Live Anchor", blocking=True)
    add("A41", "okx_crosscheck", "basis_divergence", "UNAVAILABLE", "okx.basis_divergence", None, "basis cross-check when index is owner-captured", "DATA PING / OKX owner")

    etf_rows = (etf_record or {}).get("rows") or []
    etf_by_asset = {row.get("asset"): row for row in etf_rows if row.get("asset") in {"BTC", "ETH"}}
    etf_pass = etf_record is not None and etf_pointer.get("status") == "PASS" and set(etf_by_asset) == {"BTC", "ETH"}
    add("A42", "etf", "BTC_sessions", "PASS" if etf_pass else "UNAVAILABLE", "etf.BTC_sessions", etf_by_asset.get("BTC"), "settled stable BTC ETF row", "Daily Settled ETF Calibration", blocking=True)
    add("A43", "etf", "ETH_sessions", "PASS" if etf_pass else "UNAVAILABLE", "etf.ETH_sessions", etf_by_asset.get("ETH"), "settled stable ETH ETF row", "Daily Settled ETF Calibration", blocking=True)
    etf_week = (weekly_pack or {}).get("settled_etf") or {}
    etf_counts = etf_week.get("session_counts") or {}
    etf_week_ok = int(etf_counts.get("BTC") or 0) >= 5 and int(etf_counts.get("ETH") or 0) >= 5
    add("A44", "etf", "rolling_sums", "PASS" if etf_week_ok else "UNAVAILABLE", "etf.rolling_sums", etf_week if etf_week else None, "completed-week settled BTC+ETH ETF sequence", "Daily Settled ETF + Weekly Calibration", blocking=True)
    add("A45", "etf", "stale_no_zero", "PASS" if etf_pass and ((etf_record or {}).get("verification") or {}).get("rows_identical_across_retrievals") else "UNAVAILABLE", "etf.stale_no_zero", (etf_record or {}).get("verification"), "two stable retrievals + parity", "Daily Settled ETF Calibration", blocking=True)

    cfgi = (market_metrics.get("sentiment") or {}).get("cfgi") or {}
    for aid, name in (("A46", "MARKET"), ("A47", "BTC"), ("A48", "ETH")):
        value = cfgi.get(name) or cfgi.get(name.lower())
        add(aid, "cfgi", name, "PASS" if value not in (None, {}, "") else "UNAVAILABLE", f"cfgi.{name}", value, "source-appropriate CFGI when captured", "DATA PING / CFGI owner")

    for aid, name in (("A49", "DGS2"), ("A50", "DGS10"), ("A51", "VIXCLS"), ("A52", "DTWEXBGS")):
        value = macro.get(name)
        add(aid, "macro", name, "PASS" if value else "UNAVAILABLE", f"macro.{name}", value, "latest source observation + date", "FRED live anchor")

    for aid, name, collector in (
        ("A53", "stablecoin_global", "DATA PING stablecoin owner"),
        ("A54", "stablecoin_chains", "DATA PING stablecoin owner"),
        ("A55", "chain_TVL", "DATA PING TVL owner"),
        ("A56", "DEX_pools", "DATA PING DEX owner"),
        ("A57", "DEX_anomaly_QA", "DATA PING DEX QA"),
        ("A58", "method_compatible_delta", "DATA PING stablecoin owner"),
    ):
        add(aid, "stablecoins_tvl_dex", name, "UNAVAILABLE", f"aux.{name}", None, "optional contextual owner evidence", collector)

    close_iso = (int(close_package.get("iso_year", -1)), int(close_package.get("iso_week", -1))) if close_package else (-1, -1)
    transition_week = close_iso <= CAPTURE_V22_ACTIVATION_WEEK
    weekly_present = bool(weekly_pointer and weekly_pointer.get("iso_year") == close_package.get("iso_year") and weekly_pointer.get("iso_week") == close_package.get("iso_week")) if close_package else False
    if weekly_present and weekly_pointer.get("readiness") != "READY":
        missing.append({
            "action_id": "V22-WEEKLY-SEQUENCE", "field": "weekly_v2_2_enriched_sequence",
            "blocking_level": "CONFIDENCE_REDUCING" if transition_week and final_close_ok else "BLOCKING",
            "reason": "PRE_ACTIVATION_HISTORICAL_GAP" if transition_week else "INCOMPLETE_PROSPECTIVE_SEQUENCE",
            "existing_evidence": {"hourly_rows": weekly_pointer.get("hourly_rows"), "missing_hour_count": weekly_pointer.get("missing_hour_count"), "max_contiguous_gap_hours": weekly_pointer.get("max_contiguous_gap_hours")},
            "required_evidence": "168 prospectively accumulated enriched hours for post-activation completed weeks",
            "suggested_collector": "Hourly Sequence v2.2",
        })

    required = {
        "direct_BTC_available": (hourly or {}).get("btc_close") not in (None, ""),
        "direct_ETH_available": (hourly or {}).get("eth_close") not in (None, ""),
        "direct_ETHBTC_available": (hourly or {}).get("ethbtc_close") not in (None, ""),
        "final_completed_iso_week_BTC_ETH_ETHBTC_available": tieout,
        "breadth_aggregate_available": aggregate is not None,
        "breadth_membership_hash_available": bool(breadth.get("membership_hash")),
        "derivatives_OI_funding_available": btc_oi not in (None, "") and eth_oi not in (None, "") and btc_funding is not None and eth_funding is not None,
        "OKX_crosscheck_available": all(value is not None for value in oi_cross.values()) and btc_funding is not None and eth_funding is not None,
        "weekly_v2_2_calibration_present": weekly_present,
        "settled_ETF_week_available": etf_week_ok,
    }

    add("A59", "receipts_acceptance", "receipt_reconciliation", "PASS", "quality.receipt_reconciliation", len(ledger), "59 pre-acceptance receipts", "preflight", blocking=True)
    blocking_missing_before_a60 = [item for item in missing if item.get("blocking_level") == "BLOCKING"]
    full = all(required.values()) and not blocking_missing_before_a60
    add("A60", "receipts_acceptance", "master_monday_acceptance", "PASS" if full else "PARTIAL", "packet.status", None, "all mandatory v2.2 capabilities; nonblocking unknowns preserved", "preflight", blocking=True)

    counts = {status: sum(row["status"] == status for row in ledger) for status in STATUSES}
    blocking_missing = [item for item in missing if item.get("blocking_level") == "BLOCKING"]
    package = {
        "root_contract": "MASTER_MONDAY_GAP_FILL_PACKAGE_v3",
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "packet": {"status": "FULL_MASTER_MONDAY_INPUT" if full else "PARTIAL_WITH_EXPLICIT_GAPS", "freeze_count": 1, "post_freeze_call_count": 0},
        "meta": {
            "planned_core_actions": 60, "attempted_core_actions": len(ledger), "counts_reconciled": len(ledger) == 60,
            "blocking_gap_count": len(blocking_missing), "confidence_reducing_gap_count": len(missing) - len(blocking_missing),
            "data_ping_lanes": lanes, "daily_capture_v2_2_activation_week": "2026-W32",
        },
        "quality": {"required_capabilities": required, **counts},
        "source_health": {
            "latest_capture_path": str(cap_path) if cap_path else None,
            "latest_hourly_path": str(hourly_path) if hourly_path else None,
            "final_week_close_pointer": str(close_pointer_path),
            "final_week_close_package": str(close_package_path) if close_package_path else None,
            "weekly_calibration_pointer": str(weekly_pointer_path),
            "settled_etf_pointer": str(etf_pointer_path) if etf_pointer_path.exists() else None,
        },
        "predecessor": {**predecessor, "comparison_status": "AVAILABLE" if canonical_ok and predecessor.get("market_metrics") else "UNAVAILABLE_CANONICAL_PREDECESSOR_VALUES_NOT_PRESENT"},
        "current_market": hourly,
        "settled_week": close_package,
        "weekly_calibration": weekly_pointer,
        "breadth": breadth,
        "derivatives": derivatives,
        "etf": {"pointer": etf_pointer, "record": etf_record, "weekly": etf_week},
        "cfgi": cfgi,
        "macro": macro,
        "missing": missing,
        "source_ledgers": ledger,
        "authority": {"framework_interpretation": False, "portfolio_action": False, "model_weight_change": False, "canonical_promotion": False},
    }
    package["package_sha256"] = digest(package)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canon(package))
    print(json.dumps({"status": package["packet"]["status"], "attempted": len(ledger), "missing": len(missing), "blocking": len(blocking_missing), "sha256": package["package_sha256"]}, sort_keys=True))


if __name__ == "__main__":
    main()
