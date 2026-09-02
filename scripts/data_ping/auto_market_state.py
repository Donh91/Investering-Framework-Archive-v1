#!/usr/bin/env python3
"""Non-binding automated market-state assembly from existing GitHub owners."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

from scripts.data_ping import truth_integrity as ti

REPO = "Donh91/Investering-Framework-Archive-v1"
REPOSITORY = REPO
CONTRACT = "AUTO_MARKET_STATE_PACKET_v1"
POINTER = "AUTO_MARKET_STATE_LATEST_POINTER_v1"
SCORE = "MANUAL_DATA_PING_REPLACEMENT_SCORE_v1"
REGISTRY = "02_DATA_PING/source_integrations/2026-09-02__auto-market-state-source-admission-v1_1.json"
REPLAY = "02_DATA_PING/development_validation/2026-09-01__auto-market-state-replay-report-v1.json"
BREADTH_OWNER = "03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json"
DEFAULT_ROOT = Path("04_MARKET_LEARNING/entry_signals/auto_market_state")
AUTH = {
    "binding": False,
    "canonical_acceptance": False,
    "canonical_market_state": False,
    "state_change": False,
    "portfolio_action": False,
    "model_weight_change": False,
    "market_threshold_change": False,
    "purpose": "AUTOMATED_NON_BINDING_STATE_ASSEMBLY_AND_QA",
}
AUTHORITY = AUTH
LANES = (
    "hourly_market", "live_anchor", "btc_dominance", "derivatives", "breadth", "settled_etf",
    "stablecoin_liquidity", "macro_risk", "sentiment", "altseason_context", "catalyst_context",
    "entry_signal_reference",
)


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def h(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def num(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    out = float(value)
    return out if math.isfinite(out) else None


def ptime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.utcoffset() is None:
        return None
    return stamp.astimezone(timezone.utc)


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def read_json(snapshot: Any, path: str) -> tuple[Any, dict[str, Any]]:
    try:
        value, provenance = snapshot.read_json(path)
        return value, {"status": "PASS", "path": path, "provenance": provenance}
    except Exception as exc:
        return None, {"status": "UNAVAILABLE", "path": path, "classification": getattr(exc, "classification", type(exc).__name__), "detail": getattr(exc, "detail", str(exc))}


def resolve(snapshot: Any, path: str, contract: Any, now: datetime, max_age: timedelta) -> tuple[Any, dict[str, Any]]:
    try:
        policy = ti.FreshnessPolicy("AUTO_STATE_v1", retrieval_max_age=max_age, source_observation_max_age=max_age, pointer_max_age=max_age, coverage_max_lag=max_age)
        result = ti.resolve_pointer_chain(snapshot, path, contract, now_utc=now, freshness_policy=policy)
        status = "PASS" if result["freshness"]["status"] == "PASS" else "DEGRADED"
        return result, {"status": status, "classification": result["classification"], "freshness": result["freshness"], "pointer_path": result["pointer_path"], "target_path": result["target_path"], "provenance": result["provenance"]}
    except Exception as exc:
        return None, {"status": "FAIL", "classification": getattr(exc, "classification", type(exc).__name__), "detail": getattr(exc, "detail", str(exc)), "pointer_path": path}


def git_bytes(repo_root: Path, sha: str, path: str) -> tuple[bytes, dict[str, Any]]:
    raw = subprocess.check_output(["git", "show", f"{sha}:{path}"], cwd=repo_root)
    blob = subprocess.check_output(["git", "rev-parse", "--verify", f"{sha}:{path}"], cwd=repo_root, text=True).strip()
    return raw, {"repository": REPO, "exact_commit_sha": sha, "exact_path": path, "git_blob_sha": blob, "raw_response_sha256": h(raw)}


def hourly_row(repo_root: Path, sha: str, result: Mapping[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    end = ptime(nested(result, "target", "window_end_utc"))
    if not end:
        return None, {"status": "UNAVAILABLE", "classification": "HOURLY_WINDOW_END_UNAVAILABLE"}
    candle_open = end - timedelta(hours=1)
    path = f"03_DAILY_CAPTURE_LOGS/hourly/{candle_open:%Y/%m/%Y-%m-%d}.csv"
    try:
        raw, provenance = git_bytes(repo_root, sha, path)
        expected = iso(candle_open)
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
        row = next((item for item in reversed(rows) if item.get("timestamp_utc") == expected), None)
        if not row:
            return None, {"status": "UNAVAILABLE", "classification": "HOURLY_EXACT_ROW_MISSING", "expected": expected, "provenance": provenance}
        return row, {"status": "PASS", "classification": "HOURLY_EXACT_ROW_BOUND", "timestamp_utc": expected, "provenance": provenance}
    except Exception as exc:
        return None, {"status": "UNAVAILABLE", "classification": type(exc).__name__, "detail": str(exc), "path": path}


def btc_d(repo_root: Path, sha: str, now: datetime) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    path = "03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv"
    try:
        raw, provenance = git_bytes(repo_root, sha, path)
        rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
        eligible = [row for row in rows if row.get("data_quality") == "PASS" and row.get("source_status") == "PUBLIC_SOURCE_BACKED" and ptime(row.get("source_timestamp")) and ptime(row["source_timestamp"]) <= now]
        if not eligible:
            return None, {"status": "UNAVAILABLE", "classification": "BTC_D_NO_ELIGIBLE_ROW"}
        row = max(eligible, key=lambda item: item["source_timestamp"])
        source_stamp = ptime(row["source_timestamp"])
        verified_stamp = ptime(row.get("source_verified_timestamp"))
        if source_stamp is None or verified_stamp is None or verified_stamp > now:
            return None, {"status": "UNAVAILABLE", "classification": "BTC_D_FRESHNESS_TIMESTAMP_INVALID", "provenance": provenance}
        try:
            settled_date = datetime.fromisoformat(row["date_utc"]).date()
        except (KeyError, ValueError):
            return None, {"status": "UNAVAILABLE", "classification": "BTC_D_SETTLED_DATE_INVALID", "provenance": provenance}
        calendar_lag_days = (now.date() - settled_date).days
        verification_age = (now - verified_stamp).total_seconds()
        freshness_ok = 0 <= calendar_lag_days <= 2 and 0 <= verification_age <= timedelta(hours=36).total_seconds()
        return {"value_pct": float(row["btc_d_close"]), "date_utc": row["date_utc"], "source_timestamp": row["source_timestamp"], "source_verified_timestamp": row["source_verified_timestamp"], "source_provider": row["source_provider"], "source_convention": row["source_convention"], "settlement_semantics": "LATEST_COMPLETE_DAILY_ROW_NOT_INTRADAY_POINT"}, {"status": "PASS" if freshness_ok else "DEGRADED", "classification": "BTC_D_LATEST_ELIGIBLE_SETTLED_ROW" if freshness_ok else "BTC_D_SETTLED_OWNER_STALE", "calendar_lag_days": calendar_lag_days, "verification_age_seconds": verification_age, "freshness_semantics": "SOURCE_VERIFICATION_FRESHNESS_PLUS_SETTLED_CALENDAR_LAG", "provenance": provenance}
    except Exception as exc:
        return None, {"status": "UNAVAILABLE", "classification": type(exc).__name__, "detail": str(exc)}


def stablecoin(value: Any) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if not isinstance(value, Mapping) or value.get("contract") != "DEFILLAMA_STABLECOIN_LIQUIDITY_OWNER_v1_1":
        return None, {"status": "UNAVAILABLE", "classification": "STABLECOIN_CONTRACT_UNAVAILABLE"}
    global_state = value.get("global") or {}
    semantics = value.get("evidence_semantics") or {}
    authority = value.get("authority") or {}
    if num(global_state.get("total_usd")) is None:
        return None, {"status": "UNAVAILABLE", "classification": "STABLECOIN_NON_NORMALIZABLE_GLOBAL"}
    if semantics.get("evidence_role") != "SUPPLY_LIQUIDITY" or semantics.get("deployment_confirmation") != "NOT_ESTABLISHED":
        return None, {"status": "FAIL", "classification": "STABLECOIN_SEMANTICS_ESCALATED"}
    if any(authority.get(key) is True for key in ("binding", "canonical_acceptance", "state_change", "portfolio_action")):
        return None, {"status": "FAIL", "classification": "STABLECOIN_AUTHORITY_ESCALATION"}
    return {"total_usd": num(global_state.get("total_usd")), "change_1d_pct": num(global_state.get("change_1d_pct")), "change_7d_pct": num(global_state.get("change_7d_pct")), "change_30d_pct": num(global_state.get("change_30d_pct")), "evidence_role": "SUPPLY_LIQUIDITY", "deployment_confirmation": "NOT_ESTABLISHED"}, {"status": "PASS", "classification": "STABLECOIN_SUPPLY_LIQUIDITY_NORMALIZED"}


def etf(value: Any) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if not isinstance(value, Mapping) or value.get("contract") != "DAILY_SETTLED_ETF_CALIBRATION_v2":
        return None, {"status": "UNAVAILABLE", "classification": "ETF_CONTRACT_UNAVAILABLE"}
    rows = {row.get("asset"): row for row in value.get("rows", []) if isinstance(row, Mapping)}
    valid = all(asset in rows and rows[asset].get("session_final") is True and rows[asset].get("total_parity") is True and num(rows[asset].get("reported_total")) is not None for asset in ("BTC", "ETH"))
    if not valid:
        return None, {"status": "UNAVAILABLE", "classification": "ETF_FINALITY_OR_PARITY_UNAVAILABLE"}
    return {"session_date": value.get("session_date"), "btc_reported_total_musd": num(rows["BTC"]["reported_total"]), "eth_reported_total_musd": num(rows["ETH"]["reported_total"]), "session_final": True, "total_parity": True}, {"status": "PASS", "classification": "ETF_SETTLED_FINAL_PARITY"}


def read_json_lane(snapshot: Any, path: str) -> tuple[Any, dict[str, Any]]:
    return read_json(snapshot, path)


def normalize_stablecoin(value: Any, *, now_utc: datetime | None = None) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    out, health = stablecoin(value)
    if out is not None:
        out = {**out, "evidence_semantics": {"evidence_role": "SUPPLY_LIQUIDITY", "deployment_confirmation": "NOT_ESTABLISHED"}}
    return out, health


def normalize_crosscheck(primary: Any, crosscheck: Any, *, primary_family: str, crosscheck_family: str, comparable: bool = True, tolerance_pct: float = 0.25) -> dict[str, Any]:
    base = {"primary_family": primary_family, "crosscheck_family": crosscheck_family, "independent": primary_family != crosscheck_family, "independent_source_family": primary_family != crosscheck_family, "comparable": comparable, "owner_switch_permitted": False, "market_interpretation": "NONE", "difference_pct": None}
    if primary is None:
        return {**base, "status": "STALE_PRIMARY"}
    if crosscheck is None:
        return {**base, "status": "STALE_CROSSCHECK"}
    if not comparable:
        return {**base, "status": "NOT_COMPARABLE"}
    try:
        difference = abs(float(primary) - float(crosscheck)) / max(abs(float(primary)), 1e-12) * 100
    except Exception:
        return {**base, "status": "SCHEMA_MISMATCH"}
    return {**base, "status": "AGREE" if difference <= tolerance_pct else "TRUE_CONFLICT", "difference_pct": difference, "relative_difference_pct": difference}


def normalize_etf(result: Any, *, now_utc: datetime | None = None) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    value = result.get("target") if isinstance(result, Mapping) and isinstance(result.get("target"), Mapping) else result
    out, health = etf(value)
    if out is None and isinstance(value, Mapping) and value.get("contract") == "DAILY_SETTLED_ETF_CALIBRATION_v2":
        rows = {row.get("asset"): row for row in value.get("rows", []) if isinstance(row, Mapping)}
        if any(rows.get(asset, {}).get("session_final") is not True for asset in ("BTC", "ETH")):
            health = {"status": "UNAVAILABLE", "classification": "ETF_SESSION_NOT_FINAL"}
    return out, health


def normalize_breadth(value: Any, *, now_utc: datetime, max_age: timedelta = timedelta(hours=8)) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    if not isinstance(value, Mapping):
        return None, {"status": "UNAVAILABLE", "classification": "BREADTH_OWNER_UNAVAILABLE"}
    if value.get("contract") != "RICH_BREADTH_CHECKPOINT_v1":
        return None, {"status": "UNAVAILABLE", "classification": "BREADTH_CONTRACT_UNAVAILABLE"}
    try:
        validated = ti.validate_breadth_owner_interface(value)
    except Exception as exc:
        return None, {"status": "FAIL", "classification": getattr(exc, "classification", "BREADTH_OWNER_INTERFACE_FAIL"), "detail": getattr(exc, "detail", str(exc))}
    stamp = ptime(value.get("retrieved_at_utc"))
    if stamp is None:
        return None, {"status": "UNAVAILABLE", "classification": "BREADTH_TIMESTAMP_UNAVAILABLE"}
    if stamp > now_utc:
        return None, {"status": "FAIL", "classification": "BREADTH_FUTURE_TIMESTAMP", "retrieved_at_utc": value.get("retrieved_at_utc")}
    age = now_utc - stamp
    if age > max_age:
        return None, {"status": "DEGRADED", "classification": "BREADTH_OWNER_STALE", "age_seconds": age.total_seconds()}
    return dict(value), {"status": "PASS", "classification": validated["classification"], "evidence_role": validated["evidence_role"], "canonical_large_cap_breadth": validated["canonical_large_cap_breadth"], "canonical_broad_alt_breadth": validated["canonical_broad_alt_breadth"], "retrieved_at_utc": value.get("retrieved_at_utc"), "age_seconds": age.total_seconds()}


def latest_macro(repo_root: Path, sha: str, now: datetime, *, max_age: timedelta = timedelta(hours=36)) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    prefix = "03_DAILY_CAPTURE_LOGS/captures"
    try:
        names = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", sha, "--", prefix], cwd=repo_root, text=True).splitlines()
    except Exception as exc:
        return None, {"status": "UNAVAILABLE", "classification": "MACRO_CAPTURE_ENUMERATION_FAILED", "detail": str(exc)}
    candidates = [path for path in names if path.endswith(".json") and "/20" in path and not path.endswith("/LATEST.json")]
    for path in reversed(sorted(candidates)[-48:]):
        try:
            raw, provenance = git_bytes(repo_root, sha, path)
            value = json.loads(raw)
        except Exception:
            continue
        if not isinstance(value, Mapping) or value.get("contract") != "DAILY_LIVE_ANCHOR_INDEX_v3":
            continue
        macro = nested(value, "market_metrics", "macro")
        if not isinstance(macro, Mapping) or not macro:
            continue
        stamp = ptime(value.get("captured_at_utc"))
        if stamp is None or stamp > now:
            continue
        age = now - stamp
        if age > max_age:
            return None, {"status": "UNAVAILABLE", "classification": "MACRO_OWNER_STALE", "source_capture_path": path, "source_capture_utc": value.get("captured_at_utc"), "age_seconds": age.total_seconds(), "provenance": provenance}
        return dict(macro), {"status": "PASS", "classification": "LATEST_ELIGIBLE_SLOW_MACRO_CONTEXT", "source_capture_path": path, "source_capture_utc": value.get("captured_at_utc"), "age_seconds": age.total_seconds(), "reuse_semantics": "SOURCE_CADENCE_CONTEXT_REUSE_NOT_FORWARD_FILL", "provenance": provenance}
    return None, {"status": "UNAVAILABLE", "classification": "NO_ELIGIBLE_SLOW_MACRO_CAPTURE", "reuse_semantics": "SOURCE_CADENCE_CONTEXT_REUSE_NOT_FORWARD_FILL"}


def decision_lanes(registry: Any) -> tuple[str, ...]:
    if not isinstance(registry, Mapping):
        return LANES
    by_lane = {row.get("manual_replacement_lane"): row for row in registry.get("sources", []) if isinstance(row, Mapping) and row.get("manual_replacement_lane") in LANES}
    return tuple(lane for lane in LANES if by_lane.get(lane, {}).get("decision_context_required", True) is not False)


def replacement_score(registry: Any, health: Mapping[str, Mapping[str, Any]], replay: Any) -> dict[str, Any]:
    entries = registry.get("sources", []) if isinstance(registry, Mapping) else []
    by_lane = {row.get("manual_replacement_lane"): row for row in entries if isinstance(row, Mapping)}
    total = len(LANES)
    required = decision_lanes(registry)
    acquisition = sum(bool(by_lane.get(lane, {}).get("unattended_git_owner")) for lane in LANES)
    normalization = sum(bool(by_lane.get(lane, {}).get("normalization_contract")) for lane in LANES)
    ready = sum(health.get(lane, {}).get("status") == "PASS" for lane in required)
    parity = replay.get("packet_parity_pct") if isinstance(replay, Mapping) else None
    packets = replay.get("packets_replayed", 0) if isinstance(replay, Mapping) else 0
    fields = replay.get("comparable_fields", 0) if isinstance(replay, Mapping) else 0
    a_score = round(acquisition / total * 100, 2)
    b_score = round(normalization / total * 100, 2)
    d_score = round(ready / len(required) * 100, 2) if required else 100.0
    e_score = round((total - acquisition) / total * 100, 2)
    return {"contract": SCORE, "denominator": {"functional_lanes": total, "lanes": list(LANES), "decision_context_required_lanes": len(required), "decision_context_lanes": list(required)}, "acquisition_automation_pct": a_score, "normalization_validation_automation_pct": b_score, "packet_parity_pct": parity, "packet_parity_evidence": {"status": "MEASURED" if isinstance(parity, (int, float)) else "UNMEASURED_LINEAGE_GAP", "packets": packets, "comparable_fields": fields}, "decision_context_readiness_pct": d_score, "manual_input_residual_pct": e_score, "A_acquisition_automation_pct": a_score, "B_normalization_validation_pct": b_score, "C_packet_parity_pct": parity, "D_decision_context_readiness_pct": d_score, "E_manual_input_residual_pct": e_score, "no_blended_marketing_score": True, "blended_marketing_score": "NOT_COMPUTED"}


def prior_packet(snapshot: Any) -> tuple[Any, dict[str, Any]]:
    pointer, _ = read_json(snapshot, "04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json")
    if not pointer:
        return None, {"status": "NOT_AVAILABLE_FIRST_PACKET"}
    packet, _ = read_json(snapshot, pointer.get("packet_path", ""))
    return packet, {"status": "AVAILABLE" if packet else "UNAVAILABLE", "packet_sha256": pointer.get("packet_sha256")}


def delta(current: Any, predecessor: Any) -> dict[str, Any] | None:
    if num(current) is None or num(predecessor) is None:
        return None
    current_value = float(current)
    predecessor_value = float(predecessor)
    return {"absolute": current_value - predecessor_value, "pct": None if predecessor_value == 0 else (current_value / predecessor_value - 1) * 100}


def assemble(repo_root: Path = Path.cwd(), now_utc: datetime | None = None) -> dict[str, Any]:
    now = (now_utc or datetime.now(timezone.utc)).astimezone(timezone.utc)
    snapshot = ti.GitCliSnapshot.open_repo(repo_root, repository=REPO, ref="HEAD")
    health: dict[str, dict[str, Any]] = {}
    live, live_health = resolve(snapshot, "03_DAILY_CAPTURE_LOGS/captures/LATEST.json", ti.DAILY_POINTER, now, timedelta(hours=8))
    health["live_anchor"] = live_health
    hourly, hourly_health = resolve(snapshot, "03_DAILY_CAPTURE_LOGS/hourly/LATEST.json", ti.HOURLY_POINTER, now, timedelta(hours=3))
    row, row_health = hourly_row(repo_root, snapshot.commit_sha, hourly or {})
    health["hourly_market"] = {**hourly_health, "row": row_health, "status": "PASS" if hourly_health.get("status") == "PASS" and row_health.get("status") == "PASS" else hourly_health.get("status")}
    market_metrics = nested(live, "target", "market_metrics") or {}
    derivatives = market_metrics.get("derivatives") or {}
    live_breadth_reference = market_metrics.get("breadth") or {}
    sentiment = market_metrics.get("sentiment") or {}
    altseason = market_metrics.get("altseason_context") or market_metrics.get("rotation_context") or {}
    health["derivatives"] = {"status": "PASS" if isinstance(derivatives, Mapping) and derivatives else "UNAVAILABLE", "classification": "LIVE_ANCHOR_DERIVATIVES"}
    health["sentiment"] = {"status": "PASS" if sentiment else "UNAVAILABLE", "classification": "LIVE_ANCHOR_SENTIMENT"}
    health["altseason_context"] = {"status": "PASS" if altseason else "UNAVAILABLE", "classification": "LIVE_ANCHOR_ALTSEASON_CONTEXT"}
    breadth_raw, breadth_read_health = read_json(snapshot, BREADTH_OWNER)
    breadth, breadth_normalization_health = normalize_breadth(breadth_raw, now_utc=now)
    health["breadth"] = {**breadth_read_health, "normalization": breadth_normalization_health, "status": "PASS" if breadth_read_health.get("status") == "PASS" and breadth_normalization_health.get("status") == "PASS" else breadth_normalization_health.get("status"), "classification": breadth_normalization_health.get("classification")}
    macro, macro_health = latest_macro(repo_root, snapshot.commit_sha, now)
    health["macro_risk"] = macro_health
    dominance, dominance_health = btc_d(repo_root, snapshot.commit_sha, now)
    health["btc_dominance"] = dominance_health
    etf_pointer, etf_pointer_health = read_json(snapshot, "03_DAILY_CAPTURE_LOGS/etf/LATEST.json")
    etf_value = None
    if etf_pointer and isinstance(etf_pointer.get("path"), str):
        etf_target, etf_target_health = read_json(snapshot, etf_pointer["path"])
        etf_value, etf_normalization_health = etf(etf_target)
        health["settled_etf"] = {**etf_pointer_health, "target": etf_target_health, "normalization": etf_normalization_health, "status": "PASS" if etf_pointer_health.get("status") == etf_target_health.get("status") == etf_normalization_health.get("status") == "PASS" else etf_normalization_health.get("status")}
    else:
        health["settled_etf"] = {"status": "UNAVAILABLE", "classification": "ETF_POINTER_UNAVAILABLE"}
    stable_raw, stable_read_health = read_json(snapshot, "03_DAILY_CAPTURE_LOGS/stablecoin_liquidity/LATEST.json")
    stable_state, stable_normalization_health = stablecoin(stable_raw)
    health["stablecoin_liquidity"] = {**stable_read_health, "normalization": stable_normalization_health, "status": "PASS" if stable_read_health.get("status") == "PASS" and stable_normalization_health.get("status") == "PASS" else stable_normalization_health.get("status")}
    catalyst, catalyst_read_health = read_json(snapshot, "03_DAILY_CAPTURE_LOGS/catalyst_overlay/situation_room/LATEST.json")
    if catalyst and catalyst.get("authority") == "RESEARCH_ONLY_NON_CANONICAL" and catalyst.get("run_status") == "PASS":
        catalyst_status = "PASS"
    elif catalyst and catalyst.get("authority") == "RESEARCH_ONLY_NON_CANONICAL":
        catalyst_status = "DEGRADED"
    else:
        catalyst_status = "UNAVAILABLE"
    health["catalyst_context"] = {**catalyst_read_health, "status": catalyst_status, "classification": "CATALYST_DISCOVERY_ONLY_REFERENCE", "decision_context_required": False}
    entry, entry_read_health = read_json(snapshot, "04_MARKET_LEARNING/entry_signals/LATEST.json")
    health["entry_signal_reference"] = {**entry_read_health, "status": "PASS" if entry and entry.get("contract") == "ENTRY_SIGNAL_LATEST_v1" and nested(entry, "authority", "portfolio_execution") is False else "UNAVAILABLE", "classification": "ENTRY_SIGNAL_REFERENCE_NON_BINDING"}
    registry, _ = read_json(snapshot, REGISTRY)
    replay, _ = read_json(snapshot, REPLAY)
    live_market = None
    if row:
        live_market = {"observation_open_utc": row.get("timestamp_utc"), "observation_semantics": "COMPLETED_1H_CANDLE_CLOSE_VALUE_ON_CANDLE_OPEN_LABEL", "btc_usdt": float(row["btc_close"]) if row.get("btc_close") else None, "eth_usdt": float(row["eth_close"]) if row.get("eth_close") else None, "ethbtc": float(row["ethbtc_close"]) if row.get("ethbtc_close") else None}
    health["derivatives"]["hourly_status"] = "PASS" if row and row.get("btc_open_interest") and row.get("eth_open_interest") else "UNAVAILABLE"
    scalar_values = {"btc_usdt": nested(live_market, "btc_usdt"), "eth_usdt": nested(live_market, "eth_usdt"), "ethbtc": nested(live_market, "ethbtc"), "btc_dominance_pct": nested(dominance, "value_pct"), "breadth_advance_ratio": nested(breadth, "aggregate", "advance_ratio"), "stablecoin_total_usd": nested(stable_state, "total_usd"), "btc_etf_musd": nested(etf_value, "btc_reported_total_musd"), "eth_etf_musd": nested(etf_value, "eth_reported_total_musd")}
    prior, predecessor_status = prior_packet(snapshot)
    prior_values = nested(prior, "normalized_state", "scalar_values") or {}
    deltas = {key: delta(value, prior_values.get(key)) for key, value in scalar_values.items()}
    derived_ethbtc = None if not live_market or not live_market.get("btc_usdt") or not live_market.get("eth_usdt") else live_market["eth_usdt"] / live_market["btc_usdt"]
    crosschecks = {"ethbtc_direct_vs_derived_same_binance_family": normalize_crosscheck(nested(live_market, "ethbtc"), derived_ethbtc, primary_family="BINANCE_SPOT", crosscheck_family="BINANCE_SPOT")}
    required_lanes = decision_lanes(registry)
    blockers = [lane for lane in required_lanes if health.get(lane, {}).get("status") != "PASS"]
    optional_degraded = [lane for lane in LANES if lane not in required_lanes and health.get(lane, {}).get("status") != "PASS"]
    score = replacement_score(registry, health, replay)
    critical_fail = any(health[lane].get("status") == "FAIL" for lane in ("hourly_market", "live_anchor"))
    any_nonpass = any(health.get(lane, {}).get("status") != "PASS" for lane in LANES)
    validation_status = "FAIL" if critical_fail else "DEGRADED" if any_nonpass else "PASS"
    decision_context_status = "PASS" if not blockers else "DEGRADED"
    packet = {"contract": CONTRACT, "packet_generated_at_utc": iso(now), "source_snapshot": {"repository": REPO, "exact_commit_sha": snapshot.commit_sha, "ref_resolution_count": snapshot.resolution_count, "consistency": snapshot.consistency()}, "source_registry_path": REGISTRY, "replay_report_path": REPLAY, "source_health": health, "normalized_state": {"live_market": live_market, "btc_dominance": dominance, "derivatives": {"live_anchor": derivatives, "hourly": {"btc_open_interest": float(row["btc_open_interest"]) if row and row.get("btc_open_interest") else None, "eth_open_interest": float(row["eth_open_interest"]) if row and row.get("eth_open_interest") else None}}, "breadth": breadth, "live_anchor_breadth_reference": live_breadth_reference or None, "settled_etf": etf_value, "stablecoin_liquidity": stable_state, "macro_risk": macro, "sentiment": sentiment or None, "altseason_context": altseason or None, "catalyst_context": catalyst, "entry_signal_reference": None if not entry else {"contract": entry.get("contract"), "generated_at_utc": entry.get("generated_at_utc"), "state": entry.get("state"), "observer_state": entry.get("observer_state"), "authority": entry.get("authority")}, "scalar_values": scalar_values}, "crosschecks": crosschecks, "predecessor": predecessor_status, "deltas_since_prior_auto_packet": deltas, "replacement_score": score, "decision_context_status": decision_context_status, "blockers": blockers, "optional_degraded_lanes": optional_degraded, "validation_status": validation_status, "missingness_policy": "MISSING_IS_UNKNOWN_DEGRADED_OR_UNAVAILABLE_NEVER_BEARISH", "fallback_policy": "NO_SILENT_FALLBACK_NO_OWNER_SWITCH_FROM_CROSSCHECK", "authority": AUTH}
    packet["packet_sha256"] = h(canon({key: value for key, value in packet.items() if key != "packet_sha256"}))
    return packet


def write_packet(packet: Mapping[str, Any], root: Path) -> dict[str, Any]:
    generated = ptime(packet["packet_generated_at_utc"]) or datetime.now(timezone.utc)
    run_root = root / "runs" / generated.strftime("%Y/%m/%d")
    run_root.mkdir(parents=True, exist_ok=True)
    path = run_root / f"{generated:%H%M%S}_{packet['packet_sha256'][:12]}.json"
    path.write_bytes(canon(packet))
    root.mkdir(parents=True, exist_ok=True)
    pointer = {"contract": POINTER, "packet_path": path.as_posix(), "packet_sha256": packet["packet_sha256"], "packet_generated_at_utc": packet["packet_generated_at_utc"], "source_snapshot_commit_sha": nested(packet, "source_snapshot", "exact_commit_sha"), "validation_status": packet["validation_status"], "decision_context_status": packet.get("decision_context_status"), "manual_input_residual_pct": nested(packet, "replacement_score", "manual_input_residual_pct"), "authority": AUTH}
    (root / "LATEST.json").write_bytes(canon(pointer))
    return {"packet_path": path.as_posix(), "pointer_path": (root / "LATEST.json").as_posix(), "packet_sha256": packet["packet_sha256"], "validation_status": packet["validation_status"], "decision_context_status": packet.get("decision_context_status")}


def assemble_and_write(repo_root: Path = Path.cwd(), output_root: Path = DEFAULT_ROOT, now_utc: datetime | None = None) -> dict[str, Any]:
    packet = assemble(repo_root, now_utc)
    return {**write_packet(packet, output_root), "replacement_score": packet["replacement_score"], "blockers": packet["blockers"], "optional_degraded_lanes": packet["optional_degraded_lanes"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--now-utc")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    now = ti.parse_utc(args.now_utc, "now_utc") if args.now_utc else datetime.now(timezone.utc)
    packet = assemble(args.repo_root, now)
    output = packet if args.no_write else {**write_packet(packet, args.output_root), "replacement_score": packet["replacement_score"], "blockers": packet["blockers"], "optional_degraded_lanes": packet["optional_degraded_lanes"]}
    print(json.dumps(output, sort_keys=True))
    raise SystemExit(2 if packet["validation_status"] == "FAIL" else 0)


if __name__ == "__main__":
    main()
