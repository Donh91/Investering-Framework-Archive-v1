from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


FORMULA = "70pct_containment_plus_30pct_jaccard"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n")


def interval_score(fl: float, fh: float, al: float, ah: float) -> float:
    inter = max(0.0, min(fh, ah) - max(fl, al))
    actual_width = ah - al
    union = max(fh, ah) - min(fl, al)
    containment = inter / actual_width if actual_width > 0 else 0.0
    jaccard = inter / union if union > 0 else 0.0
    return round(100.0 * (0.7 * containment + 0.3 * jaccard), 2)


def parse_utc(value: str) -> datetime:
    stamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if stamp.utcoffset() is None:
        raise ValueError("timezone_required")
    return stamp.astimezone(timezone.utc)


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
                    y, w, _ = stamp.isocalendar()
                    if y != iso_year or w != iso_week:
                        continue
                    if str(row.get("spot_status") or "").upper() not in {"PASS", "OK"}:
                        continue
                    rows[stamp] = row
        except (OSError, csv.Error):
            continue
    return [rows[k] for k in sorted(rows)]


def score_window_bounds(year: int, week: int, receipt: dict[str, Any] | None) -> dict[str, tuple[datetime, datetime]]:
    monday = datetime.combine(date.fromisocalendar(year, week, 1), datetime.min.time(), tzinfo=timezone.utc)
    bounds = {
        "day_1_2": (monday, monday + timedelta(days=2)),
        "day_3_4": (monday + timedelta(days=2), monday + timedelta(days=4)),
        "day_5_7": (monday + timedelta(days=4), monday + timedelta(days=7)),
    }
    if not receipt or str(receipt.get("score_window_policy") or "") != "FIRST_COMPLETE_UTC_HOUR_AT_OR_AFTER_FREEZE_v1":
        return bounds
    valid = str(receipt.get("scoring_valid_from_utc") or "")
    if not valid:
        raise SystemExit("site_public_freeze_receipt_scoring_valid_from_missing")
    start, end = bounds["day_1_2"]
    bounds["day_1_2"] = (max(start, parse_utc(valid)), end)
    return bounds


def hourly_realized(rows: list[dict[str, str]], start: datetime, end: datetime, asset: str) -> dict[str, float]:
    subset = [r for r in rows if start <= parse_utc(r["timestamp_utc"]) < end]
    expected = int((end - start).total_seconds() // 3600)
    if len(subset) != expected:
        raise SystemExit(f"public_scorecard_post_freeze_hourly_coverage_mismatch:{asset}:{len(subset)}/{expected}")
    lows = [float(r[f"{asset.lower()}_low"]) for r in subset]
    highs = [float(r[f"{asset.lower()}_high"]) for r in subset]
    return {"low": min(lows), "high": max(highs)}

MARKET_STRUCTURE_V2_IDS = [
    "REGIME_RESILIENCE",
    "LEADERSHIP",
    "ROTATION_TRANSMISSION",
    "BREADTH_PERSISTENCE",
    "FLOW_QUALITY_FRAGILITY",
]
MARKET_STRUCTURE_STATUS_MAP = {
    "SUPPORTED": ("HIT", 100.0),
    "MIXED": ("MIXED", 50.0),
    "CONTRADICTED": ("MISS", 0.0),
    "NOT_EVALUABLE": ("NOT_EVALUABLE", None),
}


def score_market_structure_v2(prior_freeze: dict[str, Any], machine_score: dict[str, Any]) -> dict[str, Any] | None:
    ms2 = prior_freeze.get("market_structure_v2")
    if not isinstance(ms2, dict) or ms2.get("contract") != "CN_PUBLIC_MARKET_STRUCTURE_V2":
        return None

    dimensions = ms2.get("dimensions")
    if not isinstance(dimensions, list) or len(dimensions) != 5:
        raise SystemExit("market_structure_v2_requires_five_dimensions")
    ids = [str(d.get("id") or "") for d in dimensions]
    if ids != MARKET_STRUCTURE_V2_IDS:
        raise SystemExit("market_structure_v2_dimension_identity_mismatch")

    parameter_scores = machine_score.get("parameter_scores") or []
    by_id = {
        str(row.get("parameter_id")): row
        for row in parameter_scores
        if isinstance(row, dict) and str(row.get("parameter_id", "")).startswith("structural_call_")
    }
    expected_parameter_ids = [f"structural_call_{i}" for i in range(1, 6)]
    if any(pid not in by_id for pid in expected_parameter_ids):
        missing = [pid for pid in expected_parameter_ids if pid not in by_id]
        raise SystemExit("market_structure_v2_component_missing:" + ",".join(missing))

    results = []
    evaluable_scores: list[float] = []
    for index, dimension in enumerate(dimensions, start=1):
        pid = f"structural_call_{index}"
        row = by_id[pid]
        status = str(row.get("status") or "")
        if status not in MARKET_STRUCTURE_STATUS_MAP:
            raise SystemExit(f"market_structure_v2_invalid_status:{pid}:{status}")
        public_status, expected_score = MARKET_STRUCTURE_STATUS_MAP[status]
        raw_score = row.get("score")
        if expected_score is None:
            if raw_score is not None:
                raise SystemExit(f"market_structure_v2_not_evaluable_score_must_be_null:{pid}")
        else:
            if raw_score is None or abs(float(raw_score) - expected_score) > 1e-9:
                raise SystemExit(f"market_structure_v2_status_score_mismatch:{pid}")
            evaluable_scores.append(expected_score)

        results.append({
            "dimension_id": dimension["id"],
            "label": dimension.get("label"),
            "forecast": dimension.get("forecast"),
            "expected_state": dimension.get("expected_state"),
            "expected_change": dimension.get("expected_change"),
            "parameter_id": pid,
            "status": public_status,
            "score": expected_score,
            "actual": row.get("evidence"),
            "evidence": row.get("evidence"),
        })

    coverage_count = len(evaluable_scores)
    full_coverage = coverage_count == 5
    score = round(sum(evaluable_scores) / 5.0, 2) if full_coverage else None
    return {
        "contract": "CN_PUBLIC_MARKET_STRUCTURE_V2_SCORE_v1",
        "score": score,
        "score_status": "FINAL" if full_coverage else "INCOMPLETE_EVIDENCE",
        "coverage_count": coverage_count,
        "coverage_total": 5,
        "coverage_pct": round(coverage_count / 5.0 * 100.0, 2),
        "aggregation": "EQUAL_WEIGHT_MEAN_REQUIRES_5_OF_5_EVALUABLE",
        "rubric": {"HIT": 100, "MIXED": 50, "MISS": 0, "NOT_EVALUABLE": None},
        "dimensions": results,
        "evidence_source": "CYCLE_NAVIGATOR_SCORECARD.parameter_scores.structural_call_1..5",
        "legacy_machine_structural_score": machine_score.get("structural_score"),
        "legacy_machine_structural_score_authority": False,
    }



def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    args = ap.parse_args()
    root = args.repo_root.resolve()

    pointer = read_json(root / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
    year = int(pointer["iso_year"])
    completed_week = int(pointer["completed_source_week"])
    current_week_dir = root / str(pointer["week_dir"])

    binding_path = root / "05_CYCLE_NAVIGATOR/weekly" / str(year) / f"W{completed_week:02d}" / "CYCLE_NAVIGATOR_PUBLIC_SERIES_BINDING.json"
    if not binding_path.exists():
        print(json.dumps({"status": "NOOP", "reason": "NO_PUBLIC_BINDING_FOR_COMPLETED_WEEK", "completed_week": completed_week}, sort_keys=True))
        return

    binding = read_json(binding_path)
    public_issue = int(binding["public_issue_number"])
    machine_issue = int(binding["machine_issue_number"])
    forecast_week = str(binding["forecast_week"])

    prior_freeze_path = root / "05_CYCLE_NAVIGATOR/weekly" / str(year) / f"W{completed_week:02d}" / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    if not prior_freeze_path.is_file():
        raise SystemExit("public_market_structure_prior_freeze_missing")
    prior_freeze = read_json(prior_freeze_path)

    # Public Proof is publication accountability, not merely machine calibration.
    # The public site freeze is a first-class source-of-record. X remains optional
    # downstream distribution for new issues and a valid legacy proof for older ones.
    index_path = root / "05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json"
    index = read_json(index_path)
    site_receipt_path = binding_path.parent / "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json"
    public_proof = None
    site_receipt = None
    if site_receipt_path.is_file():
        site_receipt = read_json(site_receipt_path)
        freeze_digest = hashlib.sha256(prior_freeze_path.read_bytes()).hexdigest()
        if site_receipt.get("contract") != "CN_SITE_PUBLIC_FREEZE_RECEIPT_v1":
            raise SystemExit("site_public_freeze_receipt_contract_invalid")
        if int(site_receipt.get("public_issue_number", -1)) != public_issue:
            raise SystemExit("site_public_freeze_receipt_issue_mismatch")
        if str(site_receipt.get("forecast_week") or "") != forecast_week:
            raise SystemExit("site_public_freeze_receipt_week_mismatch")
        if str(site_receipt.get("source_forecast_freeze_sha256") or "") != freeze_digest:
            raise SystemExit("site_public_freeze_receipt_hash_mismatch")
        public_proof = {
            "channel": "SITE_SOURCE_OF_RECORD",
            "receipt": str(site_receipt_path.relative_to(root)),
            "freeze_sha256": freeze_digest,
        }
    else:
        latest_pub = index.get("latest_published") or {}
        if (
            int(latest_pub.get("public_issue_number", -1)) != public_issue
            or str(latest_pub.get("forecast_week", "")) != forecast_week
        ):
            print(json.dumps({
                "status": "NOOP",
                "reason": "NO_PUBLIC_FREEZE_PROOF_FOR_COMPLETED_WEEK",
                "public_issue_number": public_issue,
                "forecast_week": forecast_week,
            }, sort_keys=True))
            return
        for field in ("published_path", "publication_receipt"):
            rel = str(latest_pub.get(field) or "")
            if not rel or ".." in rel or not (root / rel).is_file():
                raise SystemExit(f"latest_published_{field}_missing_or_invalid")
        public_proof = {
            "channel": "LEGACY_X_PUBLICATION",
            "published_path": str(latest_pub.get("published_path")),
            "receipt": str(latest_pub.get("publication_receipt")),
        }

    machine_score = read_json(current_week_dir / "CYCLE_NAVIGATOR_SCORECARD.json")
    if int(machine_score.get("issue_scored") or -1) != machine_issue:
        raise SystemExit("public_binding_machine_score_mismatch")
    if int(machine_score.get("completed_iso_week") or -1) != completed_week:
        raise SystemExit("public_binding_completed_week_mismatch")

    actual_path = root / "03_DAILY_CAPTURE_LOGS/weekly" / str(year) / f"W{completed_week:02d}.json"
    actual = read_json(actual_path)
    if actual.get("readiness") != "READY" or int((actual.get("hourly_gap_diagnostics") or {}).get("observed_hours", 0) or 0) != 168:
        raise SystemExit("public_scorecard_requires_168h_actuals")

    ledger_path = root / "05_CYCLE_NAVIGATOR/forward_range_ledger/CN_FORWARD_RANGE_LEDGER_v2.jsonl"
    ledger_rows = []
    for line in ledger_path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if int(row.get("public_issue_number", -1)) == public_issue and str(row.get("forecast_week")) == forecast_week:
            ledger_rows.append(row)

    intraday_rows = [r for r in ledger_rows if r.get("window") in {"day_1_2", "day_3_4", "day_5_7"}]
    expected = {(a, w) for a in ("BTC", "ETH") for w in ("day_1_2", "day_3_4", "day_5_7")}
    actual_keys = {(str(r.get("asset")), str(r.get("window"))) for r in intraday_rows}
    if actual_keys != expected:
        raise SystemExit("public_range_freeze_incomplete:" + json.dumps({"expected": sorted(expected), "actual": sorted(actual_keys)}))

    windows = actual["day_window_actuals"]["windows"]
    keymap = {"day_1_2": "DAY1_2", "day_3_4": "DAY3_4", "day_5_7": "DAY5_7"}
    score_window_policy = str((site_receipt or {}).get("score_window_policy") or "LEGACY_WEEK_BOUNDARY_v1")
    score_bounds = score_window_bounds(year, completed_week, site_receipt)
    hourly_rows = load_hourly_rows(root, year, completed_week) if score_window_policy == "FIRST_COMPLETE_UTC_HOUR_AT_OR_AFTER_FREEZE_v1" else []
    scored = []
    by_asset = {"BTC": [], "ETH": []}
    by_window = {k: [] for k in keymap}
    for row in intraday_rows:
        asset = str(row["asset"])
        window = str(row["window"])
        if score_window_policy == "FIRST_COMPLETE_UTC_HOUR_AT_OR_AFTER_FREEZE_v1":
            start, end = score_bounds[window]
            realized = hourly_realized(hourly_rows, start, end, asset)
        else:
            realized = windows[keymap[window]][asset.lower()]
        score = interval_score(
            float(row["forecast_low"]),
            float(row["forecast_high"]),
            float(realized["low"]),
            float(realized["high"]),
        )
        scored_row = {
            "asset": asset,
            "window": window,
            "forecast_low": float(row["forecast_low"]),
            "forecast_high": float(row["forecast_high"]),
            "actual_low": float(realized["low"]),
            "actual_high": float(realized["high"]),
            "score": score,
            "score_window_policy": score_window_policy,
        }
        scored.append(scored_row)
        by_asset[asset].append(score)
        by_window[window].append(score)

    asset_scores = {k: round(sum(v) / len(v), 2) for k, v in by_asset.items()}
    window_scores = {k: round(sum(v) / len(v), 2) for k, v in by_window.items()}
    price_score = round(sum(r["score"] for r in scored) / len(scored), 2)

    frozen_claim_score = machine_score.get("public_continuity_score")
    if frozen_claim_score is None:
        raise SystemExit("public_frozen_claim_precision_missing")

    market_analysis = prior_freeze.get("market_structure_analysis")
    # Public scoring cutover is governed by public-series issue identity, not by
    # whether an already-frozen migration-week file contains the newer analysis block.
    market_analysis_status = (
        "ANALYSIS_ONLY_NOT_SCORED"
        if public_issue >= 27
        else ("ANALYSIS_ONLY_NOT_SCORED" if isinstance(market_analysis, dict) else "LEGACY_OR_UNAVAILABLE")
    )

    out = {
        "contract": "CN_PUBLIC_WEEKLY_SCORECARD_v1",
        "authority": "PUBLIC_FORECAST_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY",
        "public_issue_number": public_issue,
        "forecast_week": forecast_week,
        "outcome_week": forecast_week,
        "status": "FINAL_DUAL_TRACK",
        "public_series_binding": str(binding_path.relative_to(root)),
        "price_range_precision": {
            "score": price_score,
            "btc_score": asset_scores["BTC"],
            "eth_score": asset_scores["ETH"],
            "intraday_window_scores": window_scores,
            "formula": FORMULA,
            "score_window_policy": score_window_policy,
            "scoring_valid_from_utc": (site_receipt or {}).get("scoring_valid_from_utc"),
            "rows": scored,
            "source": str(ledger_path.relative_to(root)),
            "actuals": str(actual_path.relative_to(root)),
            "actuals_hourly_coverage": 168,
        },
        "frozen_claim_precision": {
            "score": float(frozen_claim_score),
            "parameter_coverage_pct": machine_score.get("parameter_coverage_pct"),
            "scored_parameter_count": len([r for r in (machine_score.get("parameter_scores") or []) if r.get("score") is not None]),
            "method": "canonical_public_continuity_score_from_frozen_parameters",
            "source": str((current_week_dir / "CYCLE_NAVIGATOR_SCORECARD.json").relative_to(root)),
            "note": "Official reproducible score across the frozen weekly claim set. It is not blended with price-range precision.",
        },
        "market_structure_precision": None,
        "market_structure_status": market_analysis_status,
        "combined_score": None,
        "combined_score_status": "NOT_DEFINED",
        "combined_score_reason": "Price Range precision is the public score family. Market Structure is analysis-only; Bull/Bear is an evidence-balance forecast, not a precision score.",
        "lineage": {
            "public_series_key": f"PUBLIC_CN{public_issue}__{forecast_week}",
            "machine_issue_number": machine_issue,
            "valid_join_key": ["series", "issue_number", "forecast_week", "immutable_source"],
            "public_proof": public_proof,
        },
    }

    target = root / "05_CYCLE_NAVIGATOR/public_scorecards" / str(year) / f"W{completed_week:02d}" / f"CN{public_issue}_PUBLIC_SCORECARD.json"
    write_json(target, out)

    latest = {
        "contract": "CN_LATEST_PUBLIC_SCORECARD_POINTER_v1",
        "public_issue_number": public_issue,
        "forecast_week": forecast_week,
        "scorecard_path": str(target.relative_to(root)),
        "frozen_claim_score": float(frozen_claim_score),
        "market_structure_score": None,
        "market_structure_status": market_analysis_status,
        "price_range_score": price_score,
        "combined_score": None,
        "status": "FINAL_DUAL_TRACK",
    }
    write_json(root / "05_CYCLE_NAVIGATOR/LATEST_PUBLIC_SCORECARD.json", latest)

    index["latest_completed_score"] = dict(latest)
    index["latest_completed_score"].pop("contract", None)
    write_json(index_path, index)

    history_path = root / "05_CYCLE_NAVIGATOR/site/history-scoreboard.json"
    if history_path.exists():
        history = read_json(history_path)
        records = history.setdefault("records", [])
        row = next((r for r in records if int(r.get("cn", -1)) == public_issue), None)
        if row is None:
            row = {"cn": public_issue, "evaluated_in": public_issue + 1}
            records.append(row)
        row["era"] = "PRICE_PRECISION_PLUS_STRUCTURE_ANALYSIS"
        row["overall"] = None
        row["range_display"] = f"Combined {price_score:g} · BTC {asset_scores['BTC']:g} · ETH {asset_scores['ETH']:g}"
        row["intraday_display"] = (
            f"D1–2 {window_scores['day_1_2']:g} · "
            f"D3–4 {window_scores['day_3_4']:g} · "
            f"D5–7 {window_scores['day_5_7']:g}"
        )
        row["structure_method"] = "ANALYSIS_ONLY_NOT_SCORED"
        row["structure_display"] = None
        row["provenance"] = f"PUBLIC_CN{public_issue}_{forecast_week}_DUAL_TRACK_SCORECARD"
        row["allow_derived_overall"] = False
        records.sort(key=lambda r: int(r.get("cn", 0)))
        coverage = history.setdefault("coverage", {})
        coverage["completed_issues"] = max(int(r.get("cn", 0)) for r in records)
        coverage["rows_with_published_or_canonical_score_evidence"] = len(records)
        coverage["latest_open_issue"] = coverage["completed_issues"] + 1
        history["provenance_note"] = (
            "Recent dual-track records are resolved by public forecast week plus immutable publication lineage. "
            "Machine issue numbers are not public-series join keys during the September migration offset. "
            "From CN27 onward Market Structure is qualitative analysis only and carries no public accuracy score. Price Range precision remains the scored public forecast family."
        )
        write_json(history_path, history)

    print(json.dumps({"status": "PASS", **latest}, sort_keys=True))


if __name__ == "__main__":
    main()
