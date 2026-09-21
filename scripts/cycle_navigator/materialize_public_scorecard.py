from __future__ import annotations

import argparse
import json
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
    scored = []
    by_asset = {"BTC": [], "ETH": []}
    by_window = {k: [] for k in keymap}
    for row in intraday_rows:
        asset = str(row["asset"])
        window = str(row["window"])
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
        }
        scored.append(scored_row)
        by_asset[asset].append(score)
        by_window[window].append(score)

    asset_scores = {k: round(sum(v) / len(v), 2) for k, v in by_asset.items()}
    window_scores = {k: round(sum(v) / len(v), 2) for k, v in by_window.items()}
    price_score = round(sum(r["score"] for r in scored) / len(scored), 2)

    market_score = machine_score.get("structural_score")
    frozen_claim_score = machine_score.get("public_continuity_score")
    if market_score is None:
        raise SystemExit("public_market_structure_score_missing")
    if frozen_claim_score is None:
        raise SystemExit("public_frozen_claim_precision_missing")

    components = [
        row for row in (machine_score.get("parameter_scores") or [])
        if str(row.get("parameter_id", "")).startswith("structural_call_")
    ]

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
        "market_structure_precision": {
            "score": float(market_score),
            "aggregation": "canonical_machine_structural_score_bound_to_public_series_binding",
            "components": components,
            "evidence_source": str((current_week_dir / "CYCLE_NAVIGATOR_SCORECARD.json").relative_to(root)),
        },
        "combined_score": None,
        "combined_score_status": "NOT_DEFINED",
        "combined_score_reason": "Price-range and market/structure tracks remain separate unless a stable prospective aggregation contract exists.",
        "lineage": {
            "public_series_key": f"PUBLIC_CN{public_issue}__{forecast_week}",
            "machine_issue_number": machine_issue,
            "valid_join_key": ["series", "issue_number", "forecast_week", "immutable_source"],
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
        "market_structure_score": float(market_score),
        "price_range_score": price_score,
        "combined_score": None,
        "status": "FINAL_DUAL_TRACK",
    }
    write_json(root / "05_CYCLE_NAVIGATOR/LATEST_PUBLIC_SCORECARD.json", latest)

    index_path = root / "05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json"
    index = read_json(index_path)
    index["latest_completed_score"] = dict(latest)
    index["latest_completed_score"].pop("contract", None)
    write_json(index_path, index)

    history_path = root / "05_CYCLE_NAVIGATOR/site/history-scoreboard.json"
    if history_path.exists():
        history = read_json(history_path)
        for row in history.get("records", []):
            if int(row.get("cn", -1)) == public_issue:
                row["era"] = "DUAL_TRACK_CANONICAL"
                row["overall"] = None
                row["range_display"] = f"Combined {price_score:g} · BTC {asset_scores['BTC']:g} · ETH {asset_scores['ETH']:g}"
                row["intraday_display"] = (
                    f"D1–2 {window_scores['day_1_2']:g} · "
                    f"D3–4 {window_scores['day_3_4']:g} · "
                    f"D5–7 {window_scores['day_5_7']:g}"
                )
                row["structure_display"] = (
                    f"Frozen claims {float(frozen_claim_score):g} · "
                    f"Market/Structure {float(market_score):g}"
                )
                row["provenance"] = f"PUBLIC_CN{public_issue}_{forecast_week}_DUAL_TRACK_SCORECARD"
                row["allow_derived_overall"] = False
                break
        history["provenance_note"] = (
            "Recent dual-track records are resolved by public forecast week plus immutable publication lineage. "
            "Machine issue numbers are not public-series join keys during the September migration offset."
        )
        write_json(history_path, history)

    print(json.dumps({"status": "PASS", **latest}, sort_keys=True))


if __name__ == "__main__":
    main()
