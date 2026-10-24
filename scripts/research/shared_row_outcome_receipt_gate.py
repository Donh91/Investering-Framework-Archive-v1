"""Validate existing Shared Row matured-outcome receipts before research scoring.

Pure, fail-closed admission only. The existing outcome owner remains the sole
producer; this does NOT generate prices, forecast outcomes or new collectors.
Git source-byte reproduction remains independently governed by outcome owner.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Any

HORIZONS = {"24h": 24, "72h": 72, "7d": 168}
FLOAT_FIELDS = (
    "ethbtc_baseline", "ethbtc_end", "ethbtc_forward_return_pct",
    "ethbtc_mae_pct", "ethbtc_mfe_pct", "btc_baseline", "btc_end",
    "btc_forward_return_pct", "btc_mae_pct", "btc_mfe_pct",
    "eth_baseline", "eth_end", "eth_forward_return_pct",
    "eth_mae_pct", "eth_mfe_pct",
)
SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def stamp(value: Any) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("outcome timestamp must be explicit UTC")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo != timezone.utc:
        raise ValueError("outcome timestamp offset not UTC")
    return result


def canonical(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def detail_index(rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for detail in rows:
        grouped.setdefault((str(detail.get("event_id", "")), str(detail.get("horizon", ""))), []).append(detail)
    return grouped


def receipt_payload(detail: dict[str, Any]) -> dict[str, Any]:
    payload = {k: v for k, v in detail.items() if k != "provenance_hash"}
    for field in FLOAT_FIELDS:
        if field not in payload or str(payload[field]).strip() == "":
            raise ValueError("outcome numeric field missing: " + field)
        payload[field] = float(payload[field])
        if not math.isfinite(payload[field]):
            raise ValueError("nonfinite outcome value: " + field)
    payload["sample_count"] = int(payload["sample_count"])
    if payload["sample_count"] < 2:
        raise ValueError("outcome sample count invalid")
    if str(payload["baseline_reconciled"]).strip().lower() != "true":
        raise ValueError("outcome baseline not reconciled")
    payload["baseline_reconciled"] = True
    return payload


def verify_receipt(row: dict[str, Any], detail: dict[str, Any], horizon: str) -> None:
    """Match frozen decision and matured result; raise for any inconsistency.

    The receipt's checksum is checked against the *typed* original detail
    construction (floats/bool/int), not against arbitrary CSV string JSON.
    """
    payload = receipt_payload(detail)
    digest = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    if not SHA256.fullmatch(str(detail.get("provenance_hash", ""))) or digest != detail["provenance_hash"]:
        raise ValueError("outcome immutable receipt digest mismatch")
    if detail.get("event_id") != row.get("event_id") or detail.get("horizon") != horizon:
        raise ValueError("outcome event/horizon mismatch")
    for key, row_key in (
        ("observation_timestamp_utc", "observation_timestamp_utc"),
        ("information_cutoff_utc", "information_cutoff_utc"),
        ("row_source_commit", "source_version_commit"),
        ("row_source_binding_sha256", "source_binding_manifest_sha256"),
    ):
        if detail.get(key) != row.get(row_key):
            raise ValueError("outcome frozen parent/source mismatch: " + key)
    if detail.get("source_contract") != "HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT":
        raise ValueError("outcome source contract mismatch")
    if not SHA.fullmatch(str(detail.get("outcome_source_commit", ""))):
        raise ValueError("outcome source Git commit missing")
    bindings = json.loads(detail.get("outcome_source_bindings", ""))
    if not isinstance(bindings, list) or not bindings:
        raise ValueError("outcome Git-source bindings missing")
    for source in bindings:
        if (
            not str(source.get("path", "")).startswith("03_DAILY_CAPTURE_LOGS/hourly/")
            or ".." in str(source.get("path", ""))
            or source.get("provider") != "Binance spot"
            or source.get("owner_contract") != "HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT"
            or source.get("source_commit") != detail["outcome_source_commit"]
            or not SHA256.fullmatch(str(source.get("sha256", "")))
            or not isinstance(source.get("bytes"), int)
            or source["bytes"] <= 0
        ):
            raise ValueError("outcome original source binding malformed")
    obs = stamp(str(row["information_cutoff_utc"]))
    baseline = stamp(str(detail["baseline_timestamp_utc"]))
    target = stamp(str(detail["target_timestamp_utc"]))
    selected = stamp(str(detail["selected_end_timestamp_utc"]))
    matured = stamp(str(detail["matured_at_utc"]))
    if (
        target != obs + timedelta(hours=HORIZONS[horizon])
        or baseline > obs
        or selected < target
        or selected > target + timedelta(hours=1)
        or matured < selected + timedelta(hours=1)
        or baseline > selected
    ):
        raise ValueError("outcome target, availability or maturity clock mismatch")
    delta = selected - baseline
    if delta.total_seconds() % 3600 != 0 or payload["sample_count"] != int(delta.total_seconds() / 3600) + 1:
        raise ValueError("outcome continuous-path count inconsistent with clocks")
    label = "1" if payload["ethbtc_forward_return_pct"] > 0 else "0"
    if str(row.get(f"outcome_{horizon}", "")) != label:
        raise ValueError("outcome direction differs from frozen detail")
    for key in ("mae", "mfe"):
        expected = f"{payload[f'ethbtc_{key}_pct']:.8f}"
        if str(row.get(f"{key}_{horizon}", "")) != expected:
            raise ValueError("outcome path statistic differs from frozen detail")
    for asset in ("ethbtc", "btc", "eth"):
        base, end = payload[f"{asset}_baseline"], payload[f"{asset}_end"]
        if base <= 0 or end <= 0:
            raise ValueError("nonpositive source price in outcome")
        actual = (end / base - 1) * 100
        if not math.isclose(actual, payload[f"{asset}_forward_return_pct"], rel_tol=1e-10, abs_tol=1e-10):
            raise ValueError("outcome return does not reconcile with frozen prices")
        if payload[f"{asset}_mae_pct"] > payload[f"{asset}_mfe_pct"]:
            raise ValueError("outcome MAE greater than MFE")


def verify_row_outcomes(
    row: dict[str, Any],
    indexed: dict[tuple[str, str], list[dict[str, Any]]],
) -> None:
    for horizon in HORIZONS:
        label = str(row.get(f"outcome_{horizon}", "")).strip()
        mae = str(row.get(f"mae_{horizon}", "")).strip()
        mfe = str(row.get(f"mfe_{horizon}", "")).strip()
        receipts = indexed.get((str(row.get("event_id", "")), horizon), [])
        if not label and not mae and not mfe:
            if receipts:
                raise ValueError("outcome detail present before matured parent fields")
            continue
        if label not in {"0", "1"} or len(receipts) != 1:
            raise ValueError("matured outcome missing unique immutable detail")
        verify_receipt(row, receipts[0], horizon)
