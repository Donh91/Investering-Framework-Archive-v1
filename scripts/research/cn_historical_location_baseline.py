#!/usr/bin/env python3
"""Read-only, fail-closed CN original-text *descriptive* location/width replay.

This does NOT produce an R1/PIT-admitted or proper joint probabilistic score.
Same-width control borrows CN forecast width (not an independent forecaster).
The fixed +/-15% comparator is a width/stress negative control, not a winner.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

MATRIX_PATH = "06_RESEARCH_LAB/audit_summaries/2026-10-25__task2_cn_weekly_retrospective_originals_v1.json"
CONTRACT = "TASK2_CN_POSITION_SHARPNESS_CONTROL_v1"
# Archive versions pinned BEFORE evaluating this original nine-week case cohort.
MATRIX_GIT_BLOB_SHA1 = "185c324b78434e4c02e8de6dd7a481df8109854a"
PRIOR_PACK_GIT_BLOBS = {
    "2026-W32": "5181268d563fee7227ff1b0c9f1bba27a1cf0edc",
    "2026-W33": "c204f7e249a635982780c49a3c53e17a5636927f",
    "2026-W35": "52ae3711204ea78be0d15b62187f9a10f8d9cefe",
    "2026-W36": "335060bbef0b1d7dc8bf90e40a84574ca34fccdb",
    "2026-W37": "7a0fd1ba70dfad2d2ac5c2981c69fe477aa0fd4c",
    "2026-W38": "186eccaeecb338aa8e1cad6c3ef21727c2556093",
    "2026-W39": "57c74653e29999008a30f53a90233d2bd21ee38c",
    "2026-W40": "8d7f0ac227a250c9e71af68e063800b7f80979c2",
    "2026-W41": "7d77c1b18bc792a787a9f09cf3468fe226ec6efd",
}


def _utc(s: str) -> datetime:
    t = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError("timezone_required")
    return t.astimezone(timezone.utc)


def _read_verified(root: Path, rel: str, expected_sha: str | None = None) -> dict:
    p = root / rel
    if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):
        raise ValueError("source_missing_or_outside_root:" + rel)
    raw = p.read_bytes()
    blob_sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if expected_sha is not None and blob_sha != expected_sha:
        raise ValueError("immutable_source_sha_mismatch:" + rel)
    return json.loads(raw)


def _positive(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("not_numeric:" + name)
    v = float(value)
    if not math.isfinite(v) or v <= 0:
        raise ValueError("invalid_positive:" + name)
    return v


def _score(lo: float, hi: float, actual_low: float, actual_high: float, anchor: float) -> dict:
    for v in (lo, hi, actual_low, actual_high, anchor):
        _positive(v, "boundary")
    if lo >= hi or actual_low > actual_high:
        raise ValueError("inverted_range")
    lower = max(0.0, lo - actual_low)
    upper = max(0.0, actual_high - hi)
    intersection = max(0.0, min(hi, actual_high) - max(lo, actual_low))
    union = max(hi, actual_high) - min(lo, actual_low)
    return {
        "joint_contained": actual_low >= lo and actual_high <= hi,
        "width_pct_of_previous_close": round((hi-lo)/anchor*100, 6),
        "lower_breach_pct_of_previous_close": round(lower/anchor*100, 6),
        "upper_breach_pct_of_previous_close": round(upper/anchor*100, 6),
        "total_breach_pct_of_previous_close": round((lower+upper)/anchor*100, 6),
        "jaccard_overlap": round(intersection/union, 6),
    }


def _mean(items: list[dict], method: str, key: str) -> float | None:
    return round(sum(x[method][key] for x in items)/len(items), 6) if items else None


def _summary(rows: list[dict]) -> dict:
    methods = ("cn_original", "same_width_prior_close", "fixed_15pct_prior_close")
    return {
        "n_asset_windows": len(rows),
        "n_distinct_weeks": len({x["week"] for x in rows}),
        "methods": {
            k: {
                "joint_contained": sum(x[k]["joint_contained"] for x in rows),
                "mean_width_pct": _mean(rows, k, "width_pct_of_previous_close"),
                "mean_breach_pct": _mean(rows, k, "total_breach_pct_of_previous_close"),
                "mean_jaccard": _mean(rows, k, "jaccard_overlap"),
            } for k in methods
        },
    }


def build(repo_root: Path, matrix_path: str = MATRIX_PATH, *,
          matrix_sha: str = MATRIX_GIT_BLOB_SHA1,
          previous_shas: dict[str, str] | None = None) -> dict:
    root = repo_root.resolve()
    pinned_prior = PRIOR_PACK_GIT_BLOBS if previous_shas is None else previous_shas
    panel = _read_verified(root, matrix_path, matrix_sha)
    if panel.get("contract") != "TASK2_CN_RETROSPECTIVE_ORIGINAL_TEXT_V1" or panel.get("authority") != "RESEARCH_ONLY_NOT_SOURCE_ADMITTED":
        raise ValueError("unapproved_input_contract")
    if panel.get("summary", {}).get("science_admitted_pairs") != 0:
        raise ValueError("input_science_scope_changed")
    all_rows = []
    excluded = []
    anchors = []
    seen = set()
    for week in panel["weeks"]:
        key = week["forecast_week"]
        year, number = (int(z) for z in key.replace("-W", "-").split("-"))
        original_monday = date.fromisocalendar(year, number, 1)
        prior = (original_monday - timedelta(days=7)).isocalendar()
        prior_path = f"03_DAILY_CAPTURE_LOGS/weekly/{prior.year}/W{prior.week:02d}.json"
        actual_pack = _read_verified(root, week["weekly_actuals_path"], week["weekly_actuals_git_blob_sha1"])
        if (actual_pack.get("iso_year"), actual_pack.get("iso_week")) != (year, number):
            raise ValueError("actual_week_identity_mismatch")
        if actual_pack.get("readiness") != "READY" or (actual_pack.get("hourly_gap_diagnostics") or {}).get("observed_hours") != 168:
            raise ValueError("actual_week_not_complete")
        original_source = root / week["source_path"]
        if not original_source.is_file() or original_source.is_symlink() or not original_source.resolve().is_relative_to(root):
            raise ValueError("forecast_origin_missing_or_outside_root")
        blob = original_source.read_bytes()
        expected_blob = hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()
        if expected_blob != week["source_git_blob_sha1"]:
            raise ValueError("forecast_origin_blob_mismatch")
        prior_key = f"{prior.year}-W{prior.week:02d}"
        if prior_key not in pinned_prior:
            raise ValueError("prior_pack_immutable_binding_missing:" + prior_key)
        prior_pack = _read_verified(root, prior_path, pinned_prior[prior_key])
        if (prior_pack.get("iso_year"), prior_pack.get("iso_week")) != (prior.year, prior.week):
            raise ValueError("prior_week_identity_mismatch")
        has_complete_anchor = prior_pack.get("readiness") == "READY" and (prior_pack.get("hourly_gap_diagnostics") or {}).get("observed_hours") == 168
        freeze = week.get("freeze_recorded_at_utc")
        if freeze:
            issued = _utc(freeze)
            generated = _utc(prior_pack["generated_at_utc"])
            if generated > issued:
                raise ValueError("prior_pack_published_after_issue:" + key)
        else:
            issued = None
        if not has_complete_anchor:
            excluded.append({"week": key, "reason": "PREVIOUS_WEEK_NOT_FULLY_READY", "prior_path": prior_path})
            continue
        prices = {}
        for asset in ("BTC", "ETH"):
            prices[asset] = _positive(prior_pack["day_window_actuals"]["windows"]["DAY5_7"][asset.lower()]["close"], asset)
        anchors.append({"week": key, "source_path": prior_path, "previous_close": prices,
                        "issue_clock": freeze or "UNKNOWN", "issue_clock_verified": issued is not None,
                        "original_window_policy": "FULL_ISO_STRADDLES_MON_ISSUE" if issued and issued.date()==original_monday else "ISSUE_TIME_NOT_FULLY_PROVEN"})
        for row in week["windows"]:
            identity = (key, row["window"], row["asset"])
            if identity in seen:
                raise ValueError("duplicate_original_forecast_row")
            seen.add(identity)
            asset = row["asset"]
            window_hours = {"DAY1_2": 48, "DAY3_4": 48, "DAY5_7": 72}
            if asset not in prices or row["window"] not in window_hours or row.get("observed_hours") != window_hours.get(row["window"]):
                raise ValueError("unsupported_row_or_partial_window")
            archived_window = actual_pack["day_window_actuals"]["windows"][row["window"]]
            if archived_window.get("observed_hours") != window_hours[row["window"]]:
                raise ValueError("actual_window_not_complete")
            archived_asset = archived_window[asset.lower()]
            for field in ("low", "high"):
                actual_value = _positive(archived_asset[field], "original_actual_" + field)
                matrix_value = _positive(row["actual_" + field], "matrix_actual_" + field)
                if not math.isclose(actual_value, matrix_value, rel_tol=0.0, abs_tol=0.000001):
                    raise ValueError("archived_outcome_disagrees_with_matrix:" + field)
            a = prices[asset]
            low, high = float(row["forecast_low"]), float(row["forecast_high"])
            al, ah = float(row["actual_low"]), float(row["actual_high"])
            original = _score(low, high, al, ah, a)
            if original["joint_contained"] != row["joint_contained"]:
                raise ValueError("original_containment_changed")
            width = high-low
            same = _score(a-width/2, a+width/2, al, ah, a)
            wide = _score(a*.85, a*1.15, al, ah, a)
            all_rows.append({"week": key, "asset": asset, "window": row["window"], "anchor": a,
                "original_forecast_low": low, "original_forecast_high": high,
                "actual_low": al, "actual_high": ah,
                "issue_clock_known": issued is not None,
                "full_iso_first_window_straddles_issue": bool(issued and row["window"]=="DAY1_2" and issued.date()==original_monday),
                "cn_original": original, "same_width_prior_close": same, "fixed_15pct_prior_close": wide})
    return {
        "contract": CONTRACT,
        "authority": "RESEARCH_ONLY_DIAGNOSTIC_NOT_PIT_ADMITTED",
        "scientifically_admitted_n": 0,
        "assertions": ["BASIC_BOUNDS_AND_GIT_BLOBS_VERIFIED", "PREVIOUS_WEEK_168H_READY_REQUIRED", "WIDE_BOX_NOT_TREATED_AS_SKILL"],
        "caveats": ["Forecast dollar labels versus archived Binance USDT proxy",
                    "Published/frozen weekday windows can precede actual issue time",
                    "Provider vendor first-known not proven; no science admission",
                    "Same-width baseline inherits CN forecast width, hence NOT an independent forecast",
                    "Fixed 15 pct range is a width stress control, not a trading signal",
                    "BTC/ETH and within-week windows correlated; raw count is not independent N",
                    "No arbitrary scalar Winkler score applied to joint LOW/HIGH events"],
        "input_matrix": matrix_path,
        "excluded": excluded,
        "anchors": anchors,
        "summary": _summary(all_rows),
        "by_week": {w: _summary([z for z in all_rows if z["week"]==w]) for w in sorted({x["week"] for x in all_rows})},
        "rows": all_rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--matrix", default=MATRIX_PATH)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = build(args.repo_root, args.matrix)
    data = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)
    else:
        print(data)


if __name__ == "__main__":
    main()
