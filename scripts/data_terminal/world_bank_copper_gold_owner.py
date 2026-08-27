#!/usr/bin/env python3
"""World Bank Copper/Gold slow-cycle shadow owner.

The source publishes monthly period averages. Daily invocation only detects a
new publication or source revision. No missing month is interpolated or
forward-filled and all derived states remain non-binding shadow context.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import io
import json
import math
import re
import statistics
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree


SOURCE_ID = "WORLD_BANK_PINK_SHEET_COPPER_GOLD_MONTHLY"
SOURCE_URL = (
    "https://thedocs.worldbank.org/en/doc/"
    "74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/"
    "CMO-Historical-Data-Monthly.xlsx"
)
SOURCE_SHEET = "Monthly Prices"
COPPER_SOURCE_UNIT = "USD_PER_METRIC_TON"
GOLD_SOURCE_UNIT = "USD_PER_TROY_OUNCE"
COPPER_NORMALIZED_UNIT = "USD_PER_KILOGRAM"
GOLD_NORMALIZED_UNIT = "USD_PER_KILOGRAM"
TROY_OUNCE_KILOGRAMS = 0.0311034768
DEFAULT_STALE_AFTER_SECONDS = 75 * 24 * 60 * 60
AUTHORITY = {
    "binding": False,
    "canonical_acceptance": False,
    "state_change": False,
    "framework_state_change": False,
    "portfolio_action": False,
    "execution_authority": False,
}
XML_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
USER_AGENT = (
    "Investering-Framework-Shadow/2.0 "
    "(+https://github.com/Donh91/Investering-Framework-Archive-v1)"
)


class OwnerError(RuntimeError):
    def __init__(self, status: str, message: str):
        super().__init__(message)
        self.status = status


@dataclass(frozen=True)
class SourceObservation:
    period: str
    copper_usd_per_metric_ton: float
    gold_usd_per_troy_ounce: float


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def utc_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_timestamp(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise OwnerError("MALFORMED_TIMESTAMP", f"Invalid ISO-8601 timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise OwnerError("MALFORMED_TIMESTAMP", "Timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def fetch_payload(url: str, timeout: float, retries: int, backoff: float) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        },
    )
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                payload = response.read()
            if not payload:
                raise OwnerError("EMPTY_RESPONSE", "World Bank returned an empty payload")
            if payload[:2] != b"PK":
                raise OwnerError("SCHEMA_DRIFT", "World Bank response is not an XLSX ZIP payload")
            return payload
        except OwnerError:
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(backoff * (2**attempt))
    raise OwnerError("NETWORK_ERROR", f"World Bank retrieval failed: {last_error}")


def _column_index(reference: str) -> int:
    letters = "".join(character for character in reference if character.isalpha()).upper()
    if not letters:
        raise OwnerError("SCHEMA_DRIFT", f"Invalid XLSX cell reference: {reference}")
    result = 0
    for letter in letters:
        result = result * 26 + ord(letter) - 64
    return result - 1


def _shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    try:
        root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    except ElementTree.ParseError as exc:
        raise OwnerError("SCHEMA_DRIFT", "Invalid sharedStrings.xml") from exc
    return ["".join(node.text or "" for node in item.iter(f"{XML_NS}t")) for item in root.findall(f"{XML_NS}si")]


def _cell_value(cell: ElementTree.Element, shared: list[str]) -> Any:
    if cell.attrib.get("t") == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(f"{XML_NS}t"))
    node = cell.find(f"{XML_NS}v")
    if node is None or node.text is None:
        return None
    raw = node.text
    if cell.attrib.get("t") == "s":
        try:
            return shared[int(raw)]
        except (ValueError, IndexError) as exc:
            raise OwnerError("SCHEMA_DRIFT", "Invalid shared string reference") from exc
    try:
        return float(raw)
    except ValueError:
        return raw


def _workbook_rows(payload: bytes) -> list[list[Any]]:
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            shared = _shared_strings(archive)
            candidates = [
                name for name in archive.namelist()
                if name.startswith("xl/worksheets/") and name.endswith(".xml")
            ]
            for name in sorted(candidates):
                root = ElementTree.fromstring(archive.read(name))
                rows: list[list[Any]] = []
                for row in root.findall(f".//{XML_NS}row"):
                    cells = {
                        _column_index(cell.attrib.get("r", "")): _cell_value(cell, shared)
                        for cell in row.findall(f"{XML_NS}c")
                    }
                    rows.append([cells.get(index) for index in range(max(cells) + 1)] if cells else [])
                labels = {str(value or "").strip().casefold() for row in rows[:20] for value in row}
                if "copper" in labels and "gold" in labels:
                    return rows
    except (zipfile.BadZipFile, KeyError, ElementTree.ParseError) as exc:
        raise OwnerError("SCHEMA_DRIFT", "Invalid XLSX workbook") from exc
    raise OwnerError("SCHEMA_DRIFT", "Copper/Gold worksheet not found")


def _numeric(value: Any, field: str, period: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise OwnerError("MISSING_OBSERVATION", f"Missing or non-numeric {field} for {period}") from exc
    if not math.isfinite(result) or result <= 0:
        raise OwnerError("INVALID_OBSERVATION", f"Invalid {field} for {period}")
    return result


def parse_workbook(payload: bytes) -> tuple[list[SourceObservation], dict[str, Any]]:
    rows = _workbook_rows(payload)
    header_index = copper_index = gold_index = None
    for row_index, row in enumerate(rows):
        labels = [str(value or "").strip().casefold() for value in row]
        if "copper" in labels and "gold" in labels:
            header_index = row_index
            copper_index = labels.index("copper")
            gold_index = labels.index("gold")
            break
    if header_index is None or copper_index is None or gold_index is None:
        raise OwnerError("SCHEMA_DRIFT", "Copper and Gold columns not found")
    units = rows[header_index + 1] if header_index + 1 < len(rows) else []
    copper_unit = str(units[copper_index] if copper_index < len(units) else "").strip().casefold()
    gold_unit = str(units[gold_index] if gold_index < len(units) else "").strip().casefold()
    if copper_unit != "($/mt)" or gold_unit != "($/troy oz)":
        raise OwnerError("UNIT_DRIFT", f"Unexpected units: copper={copper_unit!r}, gold={gold_unit!r}")
    workbook_updated_on = None
    for row in rows[: header_index + 1]:
        for value in row:
            match = re.search(r"Updated on\s+(.+)", str(value or ""), flags=re.IGNORECASE)
            if match:
                workbook_updated_on = match.group(1).strip()
                break
        if workbook_updated_on:
            break
    observations: list[SourceObservation] = []
    seen: set[str] = set()
    expected_ordinal = None
    for row in rows[header_index + 2 :]:
        raw_period = str(row[0] if row else "").strip()
        match = re.fullmatch(r"(\d{4})M(\d{2})", raw_period)
        if not match:
            continue
        year, month = int(match.group(1)), int(match.group(2))
        if not 1 <= month <= 12:
            raise OwnerError("MALFORMED_TIMESTAMP", f"Invalid source period: {raw_period}")
        period = f"{year:04d}-{month:02d}"
        if period in seen:
            raise OwnerError("DUPLICATE_TIMESTAMP", f"Duplicate source period: {period}")
        ordinal = year * 12 + month
        if expected_ordinal is not None and ordinal != expected_ordinal:
            raise OwnerError("HISTORICAL_GAP", f"Non-contiguous source period at {period}")
        expected_ordinal = ordinal + 1
        copper = row[copper_index] if copper_index < len(row) else None
        gold = row[gold_index] if gold_index < len(row) else None
        observations.append(SourceObservation(period, _numeric(copper, "Copper", period), _numeric(gold, "Gold", period)))
        seen.add(period)
    if len(observations) < 100:
        raise OwnerError("INSUFFICIENT_HISTORY", f"Only {len(observations)} monthly observations")
    return observations, {"workbook_updated_on": workbook_updated_on, "sheet": SOURCE_SHEET}


def period_end_iso(period: str) -> str:
    year, month = (int(value) for value in period.split("-"))
    day = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-{day:02d}T23:59:59Z"


def _rounded(value: float | None, digits: int = 12) -> float | None:
    return round(value, digits) if value is not None and math.isfinite(value) else None


def percentage_change(values: list[float], index: int, lag: int) -> float | None:
    return None if index < lag else (values[index] / values[index - lag] - 1) * 100


def rolling_mean(values: list[float], index: int, window: int) -> float | None:
    return None if index + 1 < window else statistics.fmean(values[index + 1 - window : index + 1])


def rolling_zscore(values: list[float], index: int, window: int) -> float | None:
    if index + 1 < window:
        return None
    sample = values[index + 1 - window : index + 1]
    deviation = statistics.pstdev(sample)
    return (values[index] - statistics.fmean(sample)) / deviation if deviation else 0.0


def ema(values: Iterable[float], span: int) -> list[float]:
    sequence = list(values)
    if not sequence:
        return []
    alpha = 2 / (span + 1)
    result = [sequence[0]]
    for value in sequence[1:]:
        result.append(alpha * value + (1 - alpha) * result[-1])
    return result


def rsi_wilder(values: list[float], period: int = 14) -> list[float | None]:
    result: list[float | None] = [None] * len(values)
    if len(values) <= period:
        return result
    changes = [values[index] - values[index - 1] for index in range(1, len(values))]
    gains = [max(change, 0.0) for change in changes]
    losses = [max(-change, 0.0) for change in changes]
    average_gain = sum(gains[:period]) / period
    average_loss = sum(losses[:period]) / period
    for index in range(period, len(values)):
        if index > period:
            average_gain = (average_gain * (period - 1) + gains[index - 1]) / period
            average_loss = (average_loss * (period - 1) + losses[index - 1]) / period
        result[index] = 100.0 if average_loss == 0 and average_gain > 0 else 50.0 if average_loss == 0 else 100 - 100 / (1 + average_gain / average_loss)
    return result


def monthly_features(observations: list[SourceObservation]) -> list[dict[str, Any]]:
    ratios = [
        (row.copper_usd_per_metric_ton / 1000.0) / (row.gold_usd_per_troy_ounce / TROY_OUNCE_KILOGRAMS)
        for row in observations
    ]
    rsi = rsi_wilder(ratios)
    rows = []
    for index, source in enumerate(observations):
        ma12 = rolling_mean(ratios, index, 12)
        rows.append({
            "period": source.period,
            "source_timestamp": period_end_iso(source.period),
            "copper_source_value": source.copper_usd_per_metric_ton,
            "copper_source_unit": COPPER_SOURCE_UNIT,
            "gold_source_value": source.gold_usd_per_troy_ounce,
            "gold_source_unit": GOLD_SOURCE_UNIT,
            "copper_normalized_value": _rounded(source.copper_usd_per_metric_ton / 1000.0),
            "copper_normalized_unit": COPPER_NORMALIZED_UNIT,
            "gold_normalized_value": _rounded(source.gold_usd_per_troy_ounce / TROY_OUNCE_KILOGRAMS),
            "gold_normalized_unit": GOLD_NORMALIZED_UNIT,
            "ratio": _rounded(ratios[index]),
            "change_1m_pct": _rounded(percentage_change(ratios, index, 1)),
            "change_2m_pct": _rounded(percentage_change(ratios, index, 2)),
            "change_6m_pct": _rounded(percentage_change(ratios, index, 6)),
            "ma_3m": _rounded(rolling_mean(ratios, index, 3)),
            "ma_6m": _rounded(rolling_mean(ratios, index, 6)),
            "ma_12m": _rounded(ma12),
            "ma_24m": _rounded(rolling_mean(ratios, index, 24)),
            "distance_ma_12m_pct": _rounded((ratios[index] / ma12 - 1) * 100 if ma12 else None),
            "roc_12m_pct": _rounded(percentage_change(ratios, index, 12)),
            "rsi_14m_wilder": _rounded(rsi[index]),
            "zscore_24m_population": _rounded(rolling_zscore(ratios, index, 24)),
        })
    return rows


def classify_regime(histogram: float, prior: float | None) -> str:
    if prior is None:
        return "UNCLEAR"
    if histogram >= 0 > prior:
        return "TURNING_POSITIVE"
    if histogram < 0 <= prior:
        return "TURNING_NEGATIVE"
    if histogram >= 0:
        return "ACCELERATING" if histogram > prior else "EXPANSION"
    return "DECELERATING" if histogram < prior else "CONTRACTION"


def settled_2m_features(monthly: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    anchors = {"JAN_FEB": 0, "FEB_MAR": 1}
    output: dict[str, list[dict[str, Any]]] = {}
    for anchor, close_month_parity in anchors.items():
        selected = []
        for index, row in enumerate(monthly):
            month = int(row["period"][-2:])
            if index > 0 and month % 2 == close_month_parity:
                selected.append(row)
        values = [float(row["ratio"]) for row in selected]
        fast, slow = ema(values, 12), ema(values, 26)
        macd = [fast[index] - slow[index] for index in range(len(values))]
        signal = ema(macd, 9)
        histogram = [macd[index] - signal[index] for index in range(len(values))]
        rsi = rsi_wilder(values)
        rows = []
        for index, row in enumerate(selected):
            rows.append({
                "anchor_id": anchor,
                "bar_end_period": row["period"],
                "bar_end_timestamp": row["source_timestamp"],
                "settled": True,
                "ratio_close_proxy": row["ratio"],
                "macd_12_26": _rounded(macd[index]),
                "macd_signal_9": _rounded(signal[index]),
                "macd_histogram": _rounded(histogram[index]),
                "rsi_14_wilder": _rounded(rsi[index]),
                "regime_state": classify_regime(histogram[index], histogram[index - 1] if index else None),
                "state_authority": "SHADOW_CONTEXT_ONLY",
            })
        output[anchor] = rows
    return output


def build(payload: bytes, retrieved_at_utc: str, source_url: str = SOURCE_URL, stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS) -> dict[str, Any]:
    retrieval = parse_timestamp(retrieved_at_utc)
    observations, metadata = parse_workbook(payload)
    monthly = monthly_features(observations)
    features_2m = settled_2m_features(monthly)
    source_timestamp = parse_timestamp(monthly[-1]["source_timestamp"])
    if source_timestamp > retrieval:
        raise OwnerError("FUTURE_SOURCE_TIMESTAMP", "Latest source month ends after retrieval time")
    freshness_seconds = int((retrieval - source_timestamp).total_seconds())
    status = "PASS" if freshness_seconds <= stale_after_seconds else "STALE"
    latest_by_anchor = {anchor: rows[-1] for anchor, rows in features_2m.items()}
    states = {row["regime_state"] for row in latest_by_anchor.values()}
    consensus = next(iter(states)) if len(states) == 1 else "UNCLEAR_SPECIFICATION_DISPERSION"
    return {
        "contract": "WORLD_BANK_COPPER_GOLD_SHADOW_v2",
        "status": status,
        "retrieved_at_utc": utc_iso(retrieval),
        "source": {
            "source_id": SOURCE_ID,
            "provider": "World Bank Prospects Group",
            "product": "Commodity Price Data, The Pink Sheet",
            "sheet": SOURCE_SHEET,
            "url": source_url,
            "payload_sha256": sha256_bytes(payload),
            "workbook_updated_on": metadata["workbook_updated_on"],
            "source_substitution": False,
            "source_convention": "MONTHLY_PERIOD_AVERAGE_MACRO_PROXY_NOT_FUTURES_CONTINUOUS_CONTRACT_CLOSE",
        },
        "coverage": {"first_period": monthly[0]["period"], "last_period": monthly[-1]["period"], "observations": len(monthly)},
        "freshness": {
            "latest_source_timestamp": monthly[-1]["source_timestamp"],
            "freshness_seconds": freshness_seconds,
            "stale_after_seconds": stale_after_seconds,
            "status": status,
        },
        "validation": {
            "contiguous_monthly_periods": True,
            "duplicate_periods": 0,
            "missing_component_values": 0,
            "interpolation_used": False,
            "forward_fill_used": False,
            "in_progress_2m_bar_used": False,
        },
        "normalization": {
            "copper_formula": "copper_usd_per_metric_ton / 1000",
            "gold_formula": f"gold_usd_per_troy_ounce / {TROY_OUNCE_KILOGRAMS}",
            "ratio_formula": "copper_usd_per_kg / gold_usd_per_kg",
        },
        "monthly": monthly,
        "settled_2m": features_2m,
        "latest_monthly": monthly[-1],
        "latest_settled_2m_by_anchor": latest_by_anchor,
        "regime_consensus": consensus,
        "authority": AUTHORITY,
    }


def write_artifacts(output_root: Path, data: dict[str, Any]) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    payload_hash = data["source"]["payload_sha256"]
    revision = output_root / "revisions" / f"{payload_hash}.json"
    revision.parent.mkdir(parents=True, exist_ok=True)
    monthly_path = output_root / "normalized" / "monthly_observations.csv"
    derived_path = output_root / "derived" / "settled_2m_features.csv"
    monthly_path.parent.mkdir(parents=True, exist_ok=True)
    derived_path.parent.mkdir(parents=True, exist_ok=True)

    previous_rows: list[dict[str, str]] = []
    if monthly_path.exists():
        with monthly_path.open(newline="", encoding="utf-8") as handle:
            previous_rows = list(csv.DictReader(handle))
    previous_by_period = {row["period"]: row for row in previous_rows}
    current_by_period = {row["period"]: row for row in data["monthly"]}
    component_deltas = []
    for period in sorted(set(previous_by_period) | set(current_by_period)):
        previous = previous_by_period.get(period)
        current = current_by_period.get(period)
        previous_copper = previous.get("copper_source_value") if previous else None
        previous_gold = previous.get("gold_source_value") if previous else None
        current_copper = str(current.get("copper_source_value")) if current else None
        current_gold = str(current.get("gold_source_value")) if current else None
        if previous_copper == current_copper and previous_gold == current_gold:
            continue
        component_deltas.append({
            "period": period,
            "change_type": "ADDED" if previous is None else "REMOVED" if current is None else "REVISED",
            "previous_copper_source_value": previous_copper,
            "current_copper_source_value": current_copper,
            "previous_gold_source_value": previous_gold,
            "current_gold_source_value": current_gold,
        })

    with monthly_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data["monthly"][0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(data["monthly"])
    derived_rows = [row for anchor in ("JAN_FEB", "FEB_MAR") for row in data["settled_2m"][anchor]]
    with derived_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(derived_rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(derived_rows)

    if not revision.exists():
        initial_backfill = not previous_rows
        revision_receipt = {
            "contract": "WORLD_BANK_COPPER_GOLD_SOURCE_REVISION_v2",
            "status": data["status"],
            "retrieved_at_utc": data["retrieved_at_utc"],
            "source": data["source"],
            "coverage": data["coverage"],
            "freshness": data["freshness"],
            "validation": data["validation"],
            "revision_kind": "INITIAL_BACKFILL" if initial_backfill else "SOURCE_PAYLOAD_CHANGE",
            "component_deltas": [] if initial_backfill else component_deltas,
            "initial_backfill_observation_count": len(data["monthly"]) if initial_backfill else None,
            "normalized_history": {
                "path": str(monthly_path.relative_to(output_root)),
                "sha256": sha256_bytes(monthly_path.read_bytes()),
            },
            "derived_history": {
                "path": str(derived_path.relative_to(output_root)),
                "sha256": sha256_bytes(derived_path.read_bytes()),
            },
            "latest_monthly": data["latest_monthly"],
            "latest_settled_2m_by_anchor": data["latest_settled_2m_by_anchor"],
            "regime_consensus": data["regime_consensus"],
            "authority": AUTHORITY,
        }
        revision.write_bytes(canonical_bytes(revision_receipt))
    latest = {
        "contract": "WORLD_BANK_COPPER_GOLD_LATEST_v2",
        "status": data["status"],
        "revision_path": str(revision.relative_to(output_root)),
        "payload_sha256": payload_hash,
        "retrieved_at_utc": data["retrieved_at_utc"],
        "last_period": data["coverage"]["last_period"],
        "freshness": data["freshness"],
        "latest_monthly": data["latest_monthly"],
        "latest_settled_2m_by_anchor": data["latest_settled_2m_by_anchor"],
        "regime_consensus": data["regime_consensus"],
        "authority": AUTHORITY,
    }
    latest_path = output_root / "LATEST.json"
    latest_path.write_text(json.dumps(latest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {
        "contract": "WORLD_BANK_COPPER_GOLD_ARTIFACT_MANIFEST_v1",
        "members": {
            str(revision.relative_to(output_root)): sha256_bytes(revision.read_bytes()),
            str(monthly_path.relative_to(output_root)): sha256_bytes(monthly_path.read_bytes()),
            str(derived_path.relative_to(output_root)): sha256_bytes(derived_path.read_bytes()),
            "LATEST.json": sha256_bytes(latest_path.read_bytes()),
        },
        "authority": AUTHORITY,
    }
    (output_root / "ARTIFACT_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return latest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--source-url", default=SOURCE_URL)
    parser.add_argument("--retrieval-timestamp")
    parser.add_argument("--stale-after-seconds", type=int, default=DEFAULT_STALE_AFTER_SECONDS)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--backoff", type=float, default=0.5)
    args = parser.parse_args()
    retrieval = parse_timestamp(args.retrieval_timestamp) if args.retrieval_timestamp else datetime.now(timezone.utc)
    try:
        payload = args.fixture.read_bytes() if args.fixture else fetch_payload(args.source_url, args.timeout, args.retries, args.backoff)
        data = build(payload, utc_iso(retrieval), args.source_url, args.stale_after_seconds)
        latest = write_artifacts(args.output_root, data)
        print(json.dumps({"status": data["status"], "revision": latest["revision_path"], "coverage": data["coverage"], "freshness": data["freshness"]}, sort_keys=True))
        return 0 if data["status"] == "PASS" else 3
    except OwnerError as exc:
        print(json.dumps({"contract": "WORLD_BANK_COPPER_GOLD_ERROR_v1", "status": exc.status, "error": str(exc), "retrieved_at_utc": utc_iso(retrieval), "authority": AUTHORITY}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
