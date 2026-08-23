#!/usr/bin/env python3
"""Materialize one causally bound prospective shared row.

The materializer is deliberately fail closed. It reads only immutable, dated owner
artifacts, requires every source to have been available by the row cutoff, binds the
exact Git bytes used for every transform, and refuses to run while the P0 quarantine
or containment sentinel is active.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(".")
ROOT = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
CONTRACT = ROOT / "CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json"
FREEZE = ROOT / "TRANSFORM_FREEZE_REGISTRY.json"
CATALYST = ROOT / "data/CATALYST_LEDGER.csv"
LEDGER = ROOT / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv"
HOURLY = Path("03_DAILY_CAPTURE_LOGS/hourly")
BREADTH_ROOT = Path("03_DAILY_CAPTURE_LOGS/breadth_rich")
BTCD = Path("03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv")

ROW_INTEGRITY_CONTRACT = "SHARED_ROW_P0_BINDING_v1"
SOURCE_BINDING_CONTRACT = "SHARED_ROW_SOURCE_BINDING_MANIFEST_v1"
ACTIVE_COLLECTION_STATE = "ACTIVE_POST_REPAIR_PROSPECTIVE_COLLECTION"
HOUR = timedelta(hours=1)


class Ineligible(RuntimeError):
    def __init__(self, reason: str, detail: str | None = None):
        super().__init__(reason if detail is None else f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


def parse_ts(value: str) -> datetime:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("empty timestamp")
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp lacks timezone")
    return parsed.astimezone(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha_json(value: Any) -> str:
    return sha_bytes(canon(value).encode("utf-8"))


def _repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError as exc:
        raise Ineligible("SOURCE_PATH_OUTSIDE_REPOSITORY", str(path)) from exc


def git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception as exc:
        raise Ineligible("SOURCE_COMMIT_UNAVAILABLE") from exc


def git_blob(commit: str, path: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "show", f"{commit}:{path}"], stderr=subprocess.DEVNULL
        )
    except Exception as exc:
        raise Ineligible("SOURCE_BINDING_COMMIT_OR_PATH_UNREACHABLE", f"{commit}:{path}") from exc


def bind_paths(
    paths: Iterable[Path], *, commit: str, owner_contract: str, provider: str
) -> list[dict[str, Any]]:
    bindings = []
    for path in sorted(set(paths), key=lambda item: _repo_path(item)):
        rel = _repo_path(path)
        current = path.read_bytes()
        frozen = git_blob(commit, rel)
        if current != frozen:
            raise Ineligible("SOURCE_BYTES_NOT_FROZEN_AT_COMMIT", rel)
        bindings.append(
            {
                "path": rel,
                "sha256": sha_bytes(current),
                "bytes": len(current),
                "source_commit": commit,
                "owner_contract": owner_contract,
                "provider": provider,
            }
        )
    if not bindings:
        raise Ineligible("SOURCE_BINDING_PATHS_EMPTY")
    return bindings


def _csv_rows(payload: bytes) -> list[dict[str, str]]:
    text = payload.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def parse_hourly_payloads(payloads: Iterable[tuple[str, bytes]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    required = {
        "timestamp_utc",
        "source_window_end_utc",
        "btc_close",
        "eth_close",
        "ethbtc_close",
        "spot_status",
    }
    for source_path, payload in payloads:
        rows = _csv_rows(payload)
        if rows and not required.issubset(rows[0]):
            raise Ineligible("ETHBTC_DIRECT_PROVIDER_OR_SCHEMA_MISSING", source_path)
        for row in rows:
            try:
                ts = parse_ts(row["timestamp_utc"])
                available = parse_ts(row["source_window_end_utc"])
                if ts.minute or ts.second or ts.microsecond:
                    raise ValueError("not hour aligned")
                if available < ts + HOUR:
                    raise ValueError("unsettled hour")
                if row.get("spot_status") != "PASS":
                    raise ValueError("spot owner did not pass")
                records.append(
                    {
                        "ts": ts,
                        "available": available,
                        "ethbtc": float(row["ethbtc_close"]),
                        "btc": float(row["btc_close"]),
                        "eth": float(row["eth_close"]),
                        "path": source_path,
                    }
                )
            except Exception as exc:
                timestamp = str(row.get("timestamp_utc") or "UNKNOWN")
                raise Ineligible("ETHBTC_DIRECT_ROW_INVALID", f"{source_path}:{timestamp}") from exc
    return records


def select_ethbtc_window(records: list[dict[str, Any]], cutoff: datetime) -> list[dict[str, Any]]:
    eligible = [row for row in records if row["ts"] <= cutoff and row["available"] <= cutoff]
    by_ts: dict[datetime, list[dict[str, Any]]] = {}
    for row in eligible:
        by_ts.setdefault(row["ts"], []).append(row)
    duplicates = sorted(ts for ts, values in by_ts.items() if len(values) != 1)
    if duplicates:
        raise Ineligible("ETHBTC_DUPLICATE_TIMESTAMP", iso(duplicates[-1]))
    ordered = [by_ts[ts][0] for ts in sorted(by_ts)]
    if len(ordered) < 168:
        raise Ineligible("ETHBTC_EXACT_168_HOURS_MISSING", f"available={len(ordered)}")
    window = ordered[-168:]
    for left, right in zip(window, window[1:]):
        if right["ts"] - left["ts"] != HOUR:
            raise Ineligible("ETHBTC_168_HOUR_CONTINUITY_GAP", f"{iso(left['ts'])}->{iso(right['ts'])}")
    if window[-1]["ts"] - window[0]["ts"] != timedelta(hours=167):
        raise Ineligible("ETHBTC_168_HOUR_COVERAGE_INVALID")
    return window


def load_ethbtc_window(cutoff: datetime) -> tuple[list[dict[str, Any]], list[Path]]:
    paths = sorted(HOURLY.rglob("*.csv"))
    payloads = [(_repo_path(path), path.read_bytes()) for path in paths]
    records = parse_hourly_payloads(payloads)
    window = select_ethbtc_window(records, cutoff)
    selected = sorted({Path(row["path"]) for row in window})
    absolute = [REPO_ROOT / path for path in selected]
    return window, absolute


def _dated_breadth_snapshots() -> list[Path]:
    pattern = re.compile(r"^\d{4}/\d{2}/\d{4}-\d{2}-\d{2}/owner_snapshot\.json$")
    out = []
    for path in BREADTH_ROOT.rglob("owner_snapshot.json"):
        try:
            rel = path.relative_to(BREADTH_ROOT).as_posix()
        except ValueError:
            continue
        if pattern.fullmatch(rel):
            out.append(path)
    return sorted(out)


def _membership_hash(owner: dict[str, Any]) -> str:
    membership = [
        {"filtered_rank": row["filtered_rank"], "asset_id": row["asset_id"]}
        for row in owner.get("constituents", [])
    ]
    return sha_json(membership)


def validate_breadth_bundle(
    bundle: dict[str, bytes], *, cutoff: datetime, not_before: datetime | None
) -> tuple[dict[str, Any], datetime]:
    required = {"owner_snapshot.json", "receipt.json", "artifact_manifest.json", "raw_source_payload.json"}
    if not required.issubset(bundle):
        raise Ineligible("BREADTH_OWNER_BUNDLE_INCOMPLETE", ",".join(sorted(required - set(bundle))))
    try:
        owner = json.loads(bundle["owner_snapshot.json"])
        receipt = json.loads(bundle["receipt.json"])
        manifest = json.loads(bundle["artifact_manifest.json"])
    except Exception as exc:
        raise Ineligible("BREADTH_OWNER_BUNDLE_INVALID_JSON") from exc
    if owner.get("contract") != "C5E_TOP100_BREADTH_OWNER_v1_2":
        raise Ineligible("BREADTH_OWNER_CONTRACT_MISMATCH")
    if owner.get("method_version") != "TOP100_FILTERED_STABLE_EXCLUSION_RICH_BREADTH_v1_2":
        raise Ineligible("BREADTH_OWNER_METHOD_VERSION_MISMATCH")
    if owner.get("source") != "COINGECKO_MARKET_CAP":
        raise Ineligible("BREADTH_OWNER_PROVIDER_MISMATCH")
    retrieval = parse_ts(owner.get("retrieval_timestamp"))
    if owner.get("freeze_timestamp") != owner.get("retrieval_timestamp"):
        raise Ineligible("BREADTH_OWNER_FREEZE_TIMESTAMP_MISMATCH")
    if retrieval > cutoff:
        raise Ineligible("BREADTH_OWNER_AFTER_INFORMATION_CUTOFF")
    if not_before and retrieval < not_before:
        raise Ineligible("BREADTH_OWNER_BEFORE_POST_REPAIR_CAPTURE_BOUNDARY")
    run_id = owner.get("run_id")
    if not run_id or receipt.get("run_id") != run_id or manifest.get("run_id") != run_id:
        raise Ineligible("BREADTH_OWNER_RUN_ID_MISMATCH")
    if manifest.get("contract") != "C5E_ARTIFACT_MANIFEST_v1":
        raise Ineligible("BREADTH_ARTIFACT_MANIFEST_CONTRACT_MISMATCH")
    members = {item.get("path"): item for item in manifest.get("members", [])}
    for name in {"owner_snapshot.json", "receipt.json", "raw_source_payload.json"}:
        item = members.get(name)
        if not item or item.get("sha256") != sha_bytes(bundle[name]) or item.get("bytes") != len(bundle[name]):
            raise Ineligible("BREADTH_ARTIFACT_MANIFEST_HASH_MISMATCH", name)
    aggregate = owner.get("aggregate") or {}
    membership_hash = aggregate.get("membership_hash")
    if not membership_hash or membership_hash != _membership_hash(owner):
        raise Ineligible("BREADTH_MEMBERSHIP_REPLAY_MISMATCH")
    if aggregate.get("constituent_count") != 100 or len(owner.get("constituents", [])) != 100:
        raise Ineligible("BREADTH_CONSTITUENT_COUNT_MISMATCH")
    if (
        receipt.get("status") != "PASS"
        or receipt.get("aggregate_replay") != "PASS"
        or receipt.get("membership_hash") != membership_hash
        or receipt.get("constituent_count") != 100
        or receipt.get("raw_sha256") != sha_bytes(bundle["raw_source_payload.json"])
    ):
        raise Ineligible("BREADTH_OWNER_RECEIPT_MISMATCH")
    return owner, retrieval


def load_breadth(cutoff: datetime, not_before: datetime | None) -> tuple[dict[str, Any], datetime, list[Path]]:
    candidates: list[tuple[datetime, Path]] = []
    for path in _dated_breadth_snapshots():
        try:
            owner = json.loads(path.read_text(encoding="utf-8"))
            retrieval = parse_ts(owner.get("retrieval_timestamp"))
        except Exception:
            continue
        if retrieval <= cutoff:
            candidates.append((retrieval, path))
    if not candidates:
        raise Ineligible("BREADTH_IMMUTABLE_DATED_OWNER_MISSING")
    _, owner_path = max(candidates, key=lambda item: item[0])
    directory = owner_path.parent
    paths = [directory / name for name in ["owner_snapshot.json", "receipt.json", "artifact_manifest.json", "raw_source_payload.json"]]
    bundle = {path.name: path.read_bytes() for path in paths if path.is_file()}
    owner, retrieval = validate_breadth_bundle(bundle, cutoff=cutoff, not_before=not_before)
    return owner, retrieval, paths


def parse_btcd_payload(
    payload: bytes, *, cutoff: datetime, not_before: datetime | None
) -> tuple[list[dict[str, Any]], datetime]:
    rows = _csv_rows(payload)
    required = {
        "date_utc",
        "btc_d_close",
        "source_symbol",
        "source_provider",
        "source_convention",
        "settled_timezone",
        "source_timestamp",
        "source_verified_timestamp",
        "print_status",
        "data_quality",
        "source_status",
    }
    if rows and not required.issubset(rows[0]):
        raise Ineligible("BTCD_PROVIDER_OR_SCHEMA_MISSING")
    parsed: list[dict[str, Any]] = []
    last_date = None
    seen_dates: set[str] = set()
    for row in rows:
        try:
            if row.get("source_status") != "PUBLIC_SOURCE_BACKED":
                raise ValueError("source status")
            if row.get("data_quality") != "PASS" or row.get("print_status") != "SETTLED_COMPLETE_DATE":
                raise ValueError("settlement")
            if row.get("source_provider") != "CoinMarketCap":
                raise ValueError("provider")
            if row.get("source_symbol") != "CMC_GLOBAL_METRICS_BTC_DOMINANCE":
                raise ValueError("symbol")
            if row.get("settled_timezone") != "UTC":
                raise ValueError("timezone")
            if not str(row.get("source_convention", "")).startswith("CMC_DIRECT_SOURCE_CONVENTION:"):
                raise ValueError("convention")
            date_value = str(row["date_utc"])
            source_ts = parse_ts(row["source_timestamp"])
            verified = parse_ts(row["source_verified_timestamp"])
            if source_ts.date().isoformat() != date_value or source_ts > cutoff:
                raise ValueError("date/source timestamp")
            if date_value in seen_dates:
                raise Ineligible("BTCD_DUPLICATE_SETTLED_DATE", date_value)
            if last_date is not None and date_value <= last_date:
                raise Ineligible("BTCD_FILE_ORDER_NOT_STRICTLY_CHRONOLOGICAL", date_value)
            seen_dates.add(date_value)
            last_date = date_value
            if verified > cutoff:
                continue
            parsed.append(
                {
                    "date": date_value,
                    "value": float(row["btc_d_close"]),
                    "provider": row["source_provider"],
                    "convention": row["source_convention"],
                    "source_timestamp_utc": iso(source_ts),
                    "verified_at_utc": iso(verified),
                }
            )
        except Ineligible:
            raise
        except Exception as exc:
            raise Ineligible("BTCD_SETTLED_ROW_INVALID", str(row.get("date_utc") or "UNKNOWN")) from exc
    if len(parsed) < 3:
        raise Ineligible("BTCD_THREE_SETTLED_PRINTS_AVAILABLE_BY_CUTOFF_MISSING")
    selected = parsed[-3:]
    dates = [row["date"] for row in selected]
    if len(set(dates)) != 3 or dates != sorted(dates):
        raise Ineligible("BTCD_THREE_PRINT_CHRONOLOGY_INVALID")
    verified = [parse_ts(row["verified_at_utc"]) for row in selected]
    if not_before and any(value < not_before for value in verified):
        raise Ineligible("BTCD_OWNER_BEFORE_POST_REPAIR_CAPTURE_BOUNDARY")
    return selected, max(verified)


def load_btcd(cutoff: datetime, not_before: datetime | None) -> tuple[list[dict[str, Any]], datetime, list[Path]]:
    if not BTCD.is_file():
        raise Ineligible("BTCD_OWNER_SOURCE_MISSING")
    selected, verified = parse_btcd_payload(BTCD.read_bytes(), cutoff=cutoff, not_before=not_before)
    return selected, verified, [BTCD]


def read_ledger_ids() -> set[str]:
    if not LEDGER.exists():
        return set()
    with LEDGER.open(newline="", encoding="utf-8-sig") as handle:
        return {row["event_id"] for row in csv.DictReader(handle)}


def catalyst_tags(observation: datetime) -> tuple[str, str, str]:
    regime = "POST_CAT_STRUCT_ETF_2024" if observation >= datetime(2024, 2, 1, tzinfo=timezone.utc) else "PRE_CAT_STRUCT_ETF_2024"
    date = observation.date().isoformat()
    if CATALYST.exists():
        with CATALYST.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                if row.get("tag_type") == "VERIFIED_EXOGENOUS_SHOCK" and row.get("timestamp_or_period") == date:
                    return regime, "VERIFIED_EXOGENOUS_SHOCK", row["catalyst_evidence_id"]
    return regime, "NO_VERIFIED_EXOGENOUS_CATALYST_MATCH", "NONE_VERIFIED_AT_CUTOFF"


def collection_gate(contract: dict[str, Any], freeze: dict[str, Any]) -> tuple[datetime, datetime | None]:
    rule = freeze.get("core_activation_rule", {})
    if (
        rule.get("collection_state") != ACTIVE_COLLECTION_STATE
        or rule.get("containment_floor_sentinel") is not False
        or contract.get("prospective_eligibility_status") != "ACTIVE_POST_REPAIR_FLOOR"
    ):
        raise Ineligible("P0_REPAIR_QUARANTINE_ACTIVE")
    floor = parse_ts(contract["prospective_eligibility_start"])
    activation = contract.get("prospective_activation") or {}
    boundary_raw = activation.get("post_repair_source_capture_not_before_utc")
    if not boundary_raw:
        raise Ineligible("POST_REPAIR_SOURCE_CAPTURE_BOUNDARY_MISSING")
    return floor, parse_ts(boundary_raw)


def context_block(observation: datetime, floor: datetime, width_days: int = 28) -> str:
    if observation < floor:
        raise Ineligible("OBSERVATION_PRECEDES_ACTIVE_FLOOR")
    index = int((observation - floor).total_seconds() // timedelta(days=width_days).total_seconds())
    return f"P{width_days}D_{index:04d}"


def _not_eligible(exc: Ineligible, **extra: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"status": "NOT_ELIGIBLE", "reason": exc.reason}
    if exc.detail:
        result["detail"] = exc.detail
    result.update(extra)
    return result


def build(now_override: str | None = None) -> dict[str, Any]:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    try:
        floor, not_before = collection_gate(contract, freeze)
    except Ineligible as exc:
        return _not_eligible(exc)
    wall = parse_ts(now_override) if now_override else datetime.now(timezone.utc)
    wall = wall.replace(microsecond=0)
    if wall < floor:
        return {"status": "NOT_ELIGIBLE", "reason": "BEFORE_PROSPECTIVE_ELIGIBILITY_START", "prospective_eligibility_start": iso(floor)}
    families = {row["family_id"]: row for row in freeze["families"]}
    core = ["ETHBTC_PERSISTENCE", "BREADTH_SURVIVAL", "BTCD_PATH_RECLAIM"]
    if not all(
        families[family].get("status") == "READY"
        and families[family].get("candidate_decision_contract_status") == "READY"
        and families[family].get("repair_state") == "P0_REPAIRED_AWAITING_ACTIVATION_OR_ACTIVE"
        for family in core
    ):
        return {"status": "NOT_ELIGIBLE", "reason": "CORE_P0_CONTRACT_NOT_READY"}
    try:
        source_commit = git_sha()
        window, hourly_paths = load_ethbtc_window(wall)
        if not_before and min(row["available"] for row in window) < not_before:
            raise Ineligible("ETHBTC_WINDOW_BEFORE_POST_REPAIR_CAPTURE_BOUNDARY")
        breadth, breadth_time, breadth_paths = load_breadth(wall, not_before)
        btcd, btcd_time, btcd_paths = load_btcd(wall, not_before)
        hourly_bindings = bind_paths(
            hourly_paths,
            commit=source_commit,
            owner_contract="HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT",
            provider="Binance spot",
        )
        breadth_bindings = bind_paths(
            breadth_paths,
            commit=source_commit,
            owner_contract="C5E_TOP100_BREADTH_OWNER_v1_2",
            provider="CoinGecko market-cap markets endpoint",
        )
        btcd_bindings = bind_paths(
            btcd_paths,
            commit=source_commit,
            owner_contract="CMC_DIRECT_SOURCE_CONVENTION",
            provider="CoinMarketCap",
        )
    except Ineligible as exc:
        return _not_eligible(exc)

    baseline = window[-1]
    latest = float(baseline["ethbtc"])
    side = "ABOVE" if latest > 0.03 else "BELOW" if latest < 0.03 else "AT"
    consecutive = 0
    for row in reversed(window):
        row_side = "ABOVE" if row["ethbtc"] > 0.03 else "BELOW" if row["ethbtc"] < 0.03 else "AT"
        if row_side != side:
            break
        consecutive += 1

    aggregate = breadth["aggregate"]
    advancers, decliners = aggregate["advancers"], aggregate["decliners"]
    breadth_state = "BROAD_MAJORITY" if advancers > decliners else "NON_BROAD_MAJORITY"
    a, b_value, c = [row["value"] for row in btcd]
    if c < b_value < a:
        btcd_state = "FALLING_PATH"
    elif b_value < a and c > b_value:
        btcd_state = "RISING_RECLAIM"
    else:
        btcd_state = "MIXED_PATH"

    ethbtc_permission = side == "ABOVE"
    breadth_permission = breadth_state == "BROAD_MAJORITY"
    btcd_permission = btcd_state == "FALLING_PATH"
    decisions = {
        "C01_ETHBTC": ethbtc_permission,
        "C02_BREADTH": breadth_permission,
        "C03_BTCD": btcd_permission,
        "C04_ETHBTC_BREADTH": ethbtc_permission and breadth_permission,
        "C05_ETHBTC_BTCD": ethbtc_permission and btcd_permission,
        "C06_BREADTH_BTCD": breadth_permission and btcd_permission,
        "C07_SIMPLE_3": ethbtc_permission and breadth_permission and btcd_permission,
    }

    window_digest_payload = [
        {
            "timestamp_utc": iso(row["ts"]),
            "source_window_end_utc": iso(row["available"]),
            "ethbtc_close": row["ethbtc"],
            "btc_close": row["btc"],
            "eth_close": row["eth"],
            "path": row["path"],
        }
        for row in window
    ]
    source_manifest = {
        "contract": SOURCE_BINDING_CONTRACT,
        "source_commit": source_commit,
        "families": {
            "ETHBTC_PERSISTENCE": {
                "owner_contract": "HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT",
                "provider": "Binance spot",
                "transform_version": "ETHBTC_0_0300_PERSISTENCE_PROSPECTIVE_v1",
                "capture_min_utc": iso(min(row["available"] for row in window)),
                "capture_max_utc": iso(max(row["available"] for row in window)),
                "window_start_utc": iso(window[0]["ts"]),
                "window_end_utc": iso(window[-1]["ts"]),
                "sample_count": 168,
                "window_rows_sha256": sha_json(window_digest_payload),
                "baseline": {
                    "timestamp_utc": iso(baseline["ts"]),
                    "source_window_end_utc": iso(baseline["available"]),
                    "ethbtc_close": baseline["ethbtc"],
                    "btc_close": baseline["btc"],
                    "eth_close": baseline["eth"],
                },
                "path_bindings": hourly_bindings,
            },
            "BREADTH_SURVIVAL": {
                "owner_contract": "C5E_TOP100_BREADTH_OWNER_v1_2",
                "provider": "CoinGecko market-cap markets endpoint",
                "transform_version": "BREADTH_MAJORITY_SURVIVAL_PROSPECTIVE_v1",
                "capture_min_utc": iso(breadth_time),
                "capture_max_utc": iso(breadth_time),
                "run_id": breadth["run_id"],
                "membership_hash": aggregate["membership_hash"],
                "path_bindings": breadth_bindings,
            },
            "BTCD_PATH_RECLAIM": {
                "owner_contract": "CMC_DIRECT_SOURCE_CONVENTION",
                "provider": "CoinMarketCap",
                "transform_version": "BTCD_CMC_THREE_PRINT_PATH_PROSPECTIVE_v1",
                "capture_min_utc": iso(min(parse_ts(row["verified_at_utc"]) for row in btcd)),
                "capture_max_utc": iso(btcd_time),
                "settled_dates": [row["date"] for row in btcd],
                "path_bindings": btcd_bindings,
            },
        },
    }
    source_manifest_hash = sha_json(source_manifest)
    regime, catalyst, catalyst_evidence_id = catalyst_tags(wall)
    event_id = "PSR_" + wall.strftime("%Y%m%dT%H%M%SZ")
    if event_id in read_ledger_ids():
        return {"status": "NOOP", "reason": "EVENT_ALREADY_FROZEN", "event_id": event_id}
    row = {
        "event_id": event_id,
        "observation_timestamp_utc": iso(wall),
        "information_cutoff_utc": iso(wall),
        "source_version_commit": source_commit,
        "row_integrity_contract": ROW_INTEGRITY_CONTRACT,
        "source_binding_manifest": canon(source_manifest),
        "source_binding_manifest_sha256": source_manifest_hash,
        "prospective_context_block": context_block(wall, floor),
        "regime_tag": regime,
        "catalyst_tag": catalyst,
        "catalyst_evidence_id": catalyst_evidence_id,
        "ethbtc_raw_source": "BINANCE_DIRECT_ETHBTC_HOURLY",
        "ethbtc_raw_value": latest,
        "ethbtc_window_inputs": canon(
            {
                "lookback_rows": 168,
                "sample_count": 168,
                "continuous_hours": 168,
                "window_start_utc": iso(window[0]["ts"]),
                "window_end_utc": iso(window[-1]["ts"]),
                "window_rows_sha256": sha_json(window_digest_payload),
                "consecutive_same_side": consecutive,
                "method": "DIRECT_ETHBTC_HOURLY_CLOSES_NO_RATIO_SYNTHESIS",
            }
        ),
        "ethbtc_derived_state": side,
        "ethbtc_missing": False,
        "breadth_membership_version": breadth["contract"],
        "breadth_membership_hash": aggregate["membership_hash"],
        "breadth_raw_inputs": canon(
            {
                "retrieved_at_utc": iso(breadth_time),
                "run_id": breadth["run_id"],
                "advancers": advancers,
                "decliners": decliners,
                "flat": aggregate.get("flat"),
                "advance_ratio": aggregate.get("advance_ratio"),
            }
        ),
        "breadth_derived_state": breadth_state,
        "breadth_missing": False,
        "btcd_provider": "CoinMarketCap",
        "btcd_denominator_version": "CMC_DIRECT_SOURCE_CONVENTION",
        "btcd_raw_inputs": canon(btcd),
        "btcd_derived_state": btcd_state,
        "btcd_missing": False,
        "etf_missing": True,
        "leverage_missing": True,
        "stablecoin_missing": True,
        "cfgi_missing": True,
        "full_stack_missingness": canon(
            {"status": "NOT_YET_ELIGIBLE", "reason": "FULL_STACK_DECISION_CONTRACT_BLOCKED"}
        ),
        "candidate_decisions": decisions,
        "preexisting_registered_outcomes": "ETHBTC_FORWARD_RELATIVE_RETURN_OUTCOME_v1",
    }
    return {"status": "ELIGIBLE_SHARED_ROW", "row": row, "event_id": event_id, "candidate_decisions": decisions}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--now-utc")
    parser.add_argument("--status-only", action="store_true")
    args = parser.parse_args()
    result = build(args.now_utc)
    if args.output and result.get("row") is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result["row"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "row"}, sort_keys=True))


if __name__ == "__main__":
    main()
