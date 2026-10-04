from __future__ import annotations

import csv
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


FORMULA = "70pct_containment_plus_30pct_jaccard"
RECEIPT = "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json"
LEDGER = "05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_utc(value: str) -> datetime:
    stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if stamp.utcoffset() is None:
        raise ValueError("timezone_required")
    return stamp.astimezone(timezone.utc)


def interval_score(fl: float, fh: float, al: float, ah: float) -> float:
    inter = max(0.0, min(fh, ah) - max(fl, al))
    actual_width = ah - al
    union = max(fh, ah) - min(fl, al)
    containment = inter / actual_width if actual_width > 0 else 0.0
    jaccard = inter / union if union > 0 else 0.0
    return round(100.0 * (0.7 * containment + 0.3 * jaccard), 2)


def load_hourly_rows(root: Path, iso_year: int, iso_week: int) -> list[dict[str, str]]:
    rows: dict[datetime, dict[str, str]] = {}
    hourly_root = root / "03_DAILY_CAPTURE_LOGS/hourly" / str(iso_year)
    if not hourly_root.is_dir():
        return []
    for path in sorted(hourly_root.rglob("*.csv")):
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                for row in csv.DictReader(handle):
                    try:
                        stamp = parse_utc(row.get("timestamp_utc") or "")
                    except Exception:
                        continue
                    year, week, _ = stamp.isocalendar()
                    if year != iso_year or week != iso_week:
                        continue
                    if str(row.get("spot_status") or "").upper() not in {"PASS", "OK"}:
                        continue
                    rows[stamp] = row
        except (OSError, csv.Error):
            continue
    return [rows[k] for k in sorted(rows)]


def load_range_rows(root: Path, public_issue: int, forecast_week: str) -> list[dict[str, Any]]:
    path = root / LEDGER
    rows: list[dict[str, Any]] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if int(row.get("public_issue_number", -1)) != public_issue:
            continue
        if str(row.get("forecast_week")) != forecast_week:
            continue
        if str(row.get("window")) not in {"day_1_2", "day_3_4", "day_5_7"}:
            continue
        if str(row.get("asset")) not in {"BTC", "ETH"}:
            continue
        rows.append(row)
    keys = {(str(r["asset"]), str(r["window"])) for r in rows}
    expected = {(asset, window) for asset in ("BTC", "ETH") for window in ("day_1_2", "day_3_4", "day_5_7")}
    if keys != expected:
        raise SystemExit("public_live_precision_range_ledger_incomplete:" + json.dumps({
            "public_issue_number": public_issue,
            "forecast_week": forecast_week,
            "expected": sorted(expected),
            "actual": sorted(keys),
        }, sort_keys=True))
    return rows


def fmt_iso(stamp: datetime | None) -> str | None:
    if stamp is None:
        return None
    return stamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def window_bounds(year: int, week: int) -> dict[str, tuple[datetime, datetime]]:
    monday = datetime.combine(date.fromisocalendar(year, week, 1), datetime.min.time(), tzinfo=timezone.utc)
    return {
        "day_1_2": (monday, monday + timedelta(days=2)),
        "day_3_4": (monday + timedelta(days=2), monday + timedelta(days=4)),
        "day_5_7": (monday + timedelta(days=4), monday + timedelta(days=7)),
    }


def scoring_start_for_window(receipt: dict[str, Any], window: str, start: datetime) -> datetime:
    policy = str(receipt.get("score_window_policy") or "LEGACY_WEEK_BOUNDARY_v1")
    if policy != "FIRST_COMPLETE_UTC_HOUR_AT_OR_AFTER_FREEZE_v1" or window != "day_1_2":
        return start
    value = str(receipt.get("scoring_valid_from_utc") or "")
    if not value:
        raise SystemExit("public_live_precision_scoring_valid_from_missing")
    return max(start, parse_utc(value))


def numeric(row: dict[str, str], key: str) -> float | None:
    value = row.get(key)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def copy_public_freeze_archive(root: Path, dist_data: Path) -> int:
    archive = dist_data / "public-freezes"
    archive.mkdir(parents=True, exist_ok=True)
    index: list[dict[str, Any]] = []
    for receipt_path in sorted((root / "05_CYCLE_NAVIGATOR/weekly").glob("*/W*/" + RECEIPT)):
        try:
            receipt = read_json(receipt_path)
        except Exception:
            continue
        if receipt.get("contract") != "CN_SITE_PUBLIC_FREEZE_RECEIPT_v1":
            continue
        year = receipt_path.parent.parent.name
        week = receipt_path.parent.name
        issue = int(receipt.get("public_issue_number", 0) or 0)
        if issue <= 0:
            continue
        rel_dir = archive / year / week
        rel_dir.mkdir(parents=True, exist_ok=True)
        out = rel_dir / f"CN{issue}_PUBLIC_FREEZE.json"
        payload = dict(receipt)
        freeze_rel = str(receipt.get("source_forecast_freeze_path") or "")
        freeze = read_json(root / freeze_rel) if freeze_rel.startswith("05_CYCLE_NAVIGATOR/weekly/") and ".." not in freeze_rel else {}
        forecast_week = str(receipt.get("forecast_week") or "")
        range_rows = load_range_rows(root, issue, forecast_week)
        payload["public_frozen_price_ranges"] = {
            "score_family": "PRICE_RANGE_PRECISION",
            "formula": FORMULA,
            "rows": [
                {
                    "asset": str(row["asset"]),
                    "window": str(row["window"]),
                    "forecast_low": float(row["forecast_low"]),
                    "forecast_high": float(row["forecast_high"]),
                }
                for row in sorted(range_rows, key=lambda x: (str(x["window"]), str(x["asset"])))
            ],
            "weekly_envelope": {
                "BTC": {"low": freeze.get("btc_range_low"), "high": freeze.get("btc_range_high")},
                "ETH": {"low": freeze.get("eth_range_low"), "high": freeze.get("eth_range_high")},
            },
        }
        intraday = freeze.get("intraday_map") if isinstance(freeze.get("intraday_map"), dict) else {}
        payload["public_frozen_sequence"] = [
            {
                "window": window,
                "label": {"day_1_2": "DAY 1–2", "day_3_4": "DAY 3–4", "day_5_7": "DAY 5–7"}[window],
                "frozen_text": str(intraday.get(window) or "").strip() or None,
            }
            for window in ("day_1_2", "day_3_4", "day_5_7")
        ]
        payload["archive_path"] = f"data/public-freezes/{year}/{week}/CN{issue}_PUBLIC_FREEZE.json"
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        index.append({
            "public_issue_number": issue,
            "forecast_week": receipt.get("forecast_week"),
            "frozen_unix": receipt.get("frozen_unix"),
            "source_forecast_freeze_sha256": receipt.get("source_forecast_freeze_sha256"),
            "record_kind": "MIGRATED_VERIFIED_FREEZE" if receipt.get("migration_note") else "SITE_NATIVE_SOURCE_OF_RECORD",
            "path": payload["archive_path"],
        })
    (archive / "index.json").write_text(json.dumps({
        "contract": "CN_SITE_PUBLIC_FREEZE_INDEX_v1",
        "authority": "PUBLIC_FORECAST_ACCOUNTABILITY_ONLY_NO_MARKET_OR_PORTFOLIO_AUTHORITY",
        "records": index,
    }, indent=2, sort_keys=True) + "\n")
    return len(index)


def main() -> None:
    root = Path(".").resolve()
    dist_latest = root / "05_CYCLE_NAVIGATOR/site/dist/data/latest.json"
    if not dist_latest.is_file():
        raise SystemExit("public_live_precision_requires_built_site_snapshot")

    series = read_json(root / "05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json")
    current = series.get("current_public_projection") or {}
    public_issue = int(current.get("public_issue_number", 0) or 0)
    forecast_week = str(current.get("forecast_week") or "")
    binding_rel = str(current.get("binding_path") or "")
    if public_issue <= 0 or not forecast_week or not binding_rel.startswith("05_CYCLE_NAVIGATOR/weekly/") or ".." in binding_rel:
        raise SystemExit("public_live_precision_current_projection_invalid")

    binding_path = root / binding_rel
    binding = read_json(binding_path)
    if int(binding.get("public_issue_number", -1)) != public_issue or str(binding.get("forecast_week")) != forecast_week:
        raise SystemExit("public_live_precision_binding_mismatch")

    week_dir = binding_path.parent
    freeze_path = week_dir / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    freeze_bytes = freeze_path.read_bytes()
    freeze = json.loads(freeze_bytes)
    receipt_path = week_dir / RECEIPT
    if not receipt_path.is_file():
        raise SystemExit("public_live_precision_site_freeze_receipt_missing")
    receipt = read_json(receipt_path)
    if receipt.get("contract") != "CN_SITE_PUBLIC_FREEZE_RECEIPT_v1":
        raise SystemExit("public_live_precision_site_freeze_contract_invalid")
    if int(receipt.get("public_issue_number", -1)) != public_issue or str(receipt.get("forecast_week")) != forecast_week:
        raise SystemExit("public_live_precision_site_freeze_identity_mismatch")
    digest = sha256_bytes(freeze_bytes)
    if str(receipt.get("source_forecast_freeze_sha256") or "") != digest:
        raise SystemExit("public_live_precision_site_freeze_hash_mismatch")

    try:
        year_s, week_s = forecast_week.split("-W")
        iso_year, iso_week = int(year_s), int(week_s)
    except Exception as exc:
        raise SystemExit("public_live_precision_forecast_week_invalid") from exc

    ledger_rows = load_range_rows(root, public_issue, forecast_week)
    frozen_intraday = freeze.get("intraday_map") if isinstance(freeze.get("intraday_map"), dict) else {}
    hourly = load_hourly_rows(root, iso_year, iso_week)
    bounds = window_bounds(iso_year, iso_week)
    latest_open = parse_utc(hourly[-1]["timestamp_utc"]) if hourly else None
    observed_through = latest_open + timedelta(hours=1) if latest_open else None

    results: list[dict[str, Any]] = []
    window_summary: dict[str, dict[str, Any]] = {}
    completed_rows = live_rows = pending_rows = 0

    for window in ("day_1_2", "day_3_4", "day_5_7"):
        calendar_start, end = bounds[window]
        start = scoring_start_for_window(receipt, window, calendar_start)
        expected_total = max(0, int((end - start).total_seconds() // 3600))
        subset = []
        for row in hourly:
            stamp = parse_utc(row["timestamp_utc"])
            if start <= stamp < end:
                subset.append(row)

        if observed_through is None or observed_through <= start:
            expected_so_far = 0
            phase = "NOT_STARTED"
        else:
            capped = min(observed_through, end)
            expected_so_far = max(0, int((capped - start).total_seconds() // 3600))
            phase = "COMPLETE" if observed_through >= end else "LIVE"

        observed = len(subset)
        complete_coverage = expected_so_far > 0 and observed == expected_so_far
        if phase == "COMPLETE" and observed != expected_total:
            phase = "DEGRADED"
            complete_coverage = False

        row_scores: list[float] = []
        for asset in ("BTC", "ETH"):
            frozen = next(r for r in ledger_rows if str(r["window"]) == window and str(r["asset"]) == asset)
            lows = [numeric(r, f"{asset.lower()}_low") for r in subset]
            highs = [numeric(r, f"{asset.lower()}_high") for r in subset]
            lows = [x for x in lows if x is not None]
            highs = [x for x in highs if x is not None]
            actual_low = min(lows) if lows else None
            actual_high = max(highs) if highs else None
            score = None
            if complete_coverage and actual_low is not None and actual_high is not None:
                score = interval_score(
                    float(frozen["forecast_low"]),
                    float(frozen["forecast_high"]),
                    actual_low,
                    actual_high,
                )
                row_scores.append(score)
                if phase == "COMPLETE":
                    completed_rows += 1
                elif phase == "LIVE":
                    live_rows += 1
            else:
                pending_rows += 1
            results.append({
                "asset": asset,
                "window": window,
                "window_phase": phase,
                "forecast_low": float(frozen["forecast_low"]),
                "forecast_high": float(frozen["forecast_high"]),
                "actual_low_to_date": actual_low,
                "actual_high_to_date": actual_high,
                "score_to_date": score,
                "hourly_rows_observed": observed,
                "hourly_rows_expected_so_far": expected_so_far,
                "coverage_complete_to_date": complete_coverage,
            })

        window_score = round(sum(row_scores) / len(row_scores), 2) if len(row_scores) == 2 else None
        window_summary[window] = {
            "phase": phase,
            "score_to_date": window_score,
            "frozen_sequence_text": str(frozen_intraday.get(window) or "").strip() or None,
            "rows_scored": len(row_scores),
            "rows_total": 2,
            "observed_hours": observed,
            "expected_hours_so_far": expected_so_far,
            "expected_hours_final": expected_total,
            "coverage_complete_to_date": complete_coverage,
            "window_start_utc": fmt_iso(calendar_start),
            "scoring_start_utc": fmt_iso(start),
            "window_end_utc": fmt_iso(end),
        }

    scored = [float(r["score_to_date"]) for r in results if r.get("score_to_date") is not None]
    running = round(sum(scored) / len(scored), 2) if scored else None
    all_complete = completed_rows == 6 and live_rows == 0 and pending_rows == 0
    status = "READY_FOR_FINAL_WEEKLY_SETTLEMENT" if all_complete else ("PROVISIONAL_LIVE" if scored else "AWAITING_COMPLETE_OBSERVATION")

    frozen_unix = int(receipt.get("frozen_unix", 0) or 0)
    frozen_at = datetime.fromtimestamp(frozen_unix, tz=timezone.utc) if frozen_unix > 0 else None
    snapshot = read_json(dist_latest)
    snapshot["public_live_precision"] = {
        "contract": "CN_PUBLIC_LIVE_PRICE_PRECISION_v1",
        "authority": "PUBLIC_FORECAST_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY",
        "public_issue_number": public_issue,
        "forecast_week": forecast_week,
        "status": status,
        "score_family": "PRICE_RANGE_PRECISION",
        "formula": FORMULA,
        "score_window_policy": str(receipt.get("score_window_policy") or "LEGACY_WEEK_BOUNDARY_v1"),
        "scoring_valid_from_utc": receipt.get("scoring_valid_from_utc"),
        "freshness_sla_minutes": 90,
        "refresh_cadence": "HOURLY_OWNER_CHAIN",
        "freeze_record_kind": "MIGRATED_VERIFIED_FREEZE" if receipt.get("migration_note") else "SITE_NATIVE_SOURCE_OF_RECORD",
        "running_price_precision_pct": running,
        "running_score_semantics": "SAME_FORMULA_AS_FINAL_PUBLIC_PRICE_RANGE_PRECISION_APPLIED_TO_COMPLETE_OBSERVED_DATA_TO_DATE",
        "scored_rows": len(scored),
        "final_row_count": 6,
        "completed_rows": completed_rows,
        "live_rows": live_rows,
        "pending_rows": 6 - len(scored),
        "window_scores": window_summary,
        "frozen_sequence": [
            {
                "window": window,
                "label": {"day_1_2": "DAY 1–2", "day_3_4": "DAY 3–4", "day_5_7": "DAY 5–7"}[window],
                "frozen_text": window_summary[window].get("frozen_sequence_text"),
                "phase": window_summary[window].get("phase"),
                "score_to_date": window_summary[window].get("score_to_date"),
                "window_start_utc": window_summary[window].get("window_start_utc"),
                "scoring_start_utc": window_summary[window].get("scoring_start_utc"),
                "window_end_utc": window_summary[window].get("window_end_utc"),
            }
            for window in ("day_1_2", "day_3_4", "day_5_7")
        ],
        "rows": results,
        "frozen_at_utc": fmt_iso(frozen_at),
        "live_as_of_utc": fmt_iso(observed_through),
        "freeze_sha256": digest,
        "freeze_receipt_public_path": f"data/public-freezes/{iso_year}/W{iso_week:02d}/CN{public_issue}_PUBLIC_FREEZE.json",
        "final_score_destination": "CN_PUBLIC_WEEKLY_SCORECARD.price_range_precision.score",
        "finalization_rule": "Final score locks only after 168h weekly actuals and canonical weekly settlement.",
        "x_distribution_required": False,
    }
    dist_latest.write_text(json.dumps(snapshot, indent=2) + "\n")

    archive_count = copy_public_freeze_archive(root, dist_latest.parent)
    print(json.dumps({
        "status": "PASS",
        "public_issue_number": public_issue,
        "forecast_week": forecast_week,
        "running_price_precision_pct": running,
        "scored_rows": len(scored),
        "completed_rows": completed_rows,
        "live_rows": live_rows,
        "archive_count": archive_count,
        "live_as_of_utc": fmt_iso(observed_through),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
