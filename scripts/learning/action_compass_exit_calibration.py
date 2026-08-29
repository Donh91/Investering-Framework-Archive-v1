from __future__ import annotations

import argparse
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OUTCOME_CONTRACT = "ACTION_COMPASS_OUTCOME_SIDECAR_v1_1"
REPORT_CONTRACT = "ACTION_COMPASS_EXIT_WARNING_CALIBRATION_v1"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def finite_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def median(values: list[float]) -> float | None:
    if not values:
        return None
    return round(float(statistics.median(values)), 10)


def iso_now(value: str | None) -> str:
    if value:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("generated_at_utc_timezone_required")
        return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def collect_rows(outcome_root: Path) -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    sidecar_count = 0
    if not outcome_root.exists():
        return rows, sidecar_count
    for path in sorted(outcome_root.rglob("*.json")):
        try:
            sidecar = read_json(path)
        except Exception:
            continue
        if sidecar.get("contract") != OUTCOME_CONTRACT:
            continue
        sidecar_count += 1
        if sidecar.get("status") not in {"MATURED", "PARTIAL"}:
            continue
        decision = sidecar.get("decision_snapshot")
        if not isinstance(decision, dict):
            continue
        state = str(decision.get("lane_3_state") or "UNKNOWN")
        warning = str(decision.get("lane_3_warning") or "UNKNOWN")
        action = str(decision.get("lane_3_action") or "UNKNOWN")
        horizon = str(sidecar.get("horizon") or "UNKNOWN")
        for series in sidecar.get("series_outcomes") or []:
            if not isinstance(series, dict) or series.get("status") != "MATURED":
                continue
            series_id = str(series.get("series_id") or "UNKNOWN")
            terminal = finite_number(series.get("terminal_return_pct"))
            upside = finite_number(series.get("max_upside_from_start_pct"))
            drawdown = finite_number(series.get("max_drawdown_from_start_pct"))
            trough_hours = finite_number(series.get("time_to_trough_hours"))
            full_exit = series.get("normalized_full_exit_counterfactual")
            preserved = foregone = None
            if isinstance(full_exit, dict):
                preserved = finite_number(full_exit.get("capital_preserved_pct"))
                foregone = finite_number(full_exit.get("upside_foregone_pct"))
            rows.append(
                {
                    "horizon": horizon,
                    "state": state,
                    "warning": warning,
                    "action": action,
                    "series_id": series_id,
                    "terminal_return_pct": terminal,
                    "max_upside_after_signal_pct": upside,
                    "max_drawdown_after_signal_pct": drawdown,
                    "time_to_trough_hours": trough_hours,
                    "full_exit_capital_preserved_reference_pct": preserved,
                    "full_exit_terminal_upside_foregone_reference_pct": foregone,
                }
            )
    return rows, sidecar_count


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        key = (row["horizon"], row["state"], row["warning"], row["series_id"])
        groups.setdefault(key, []).append(row)
    output: list[dict[str, Any]] = []
    for key in sorted(groups):
        group = groups[key]
        def numbers(field: str) -> list[float]:
            return [float(row[field]) for row in group if row.get(field) is not None]
        output.append(
            {
                "horizon": key[0],
                "lane_3_state": key[1],
                "lane_3_warning": key[2],
                "series_id": key[3],
                "observation_count": len(group),
                "actions_observed": sorted({row["action"] for row in group}),
                "median_terminal_return_pct": median(numbers("terminal_return_pct")),
                "median_max_upside_after_signal_pct": median(numbers("max_upside_after_signal_pct")),
                "median_max_drawdown_after_signal_pct": median(numbers("max_drawdown_after_signal_pct")),
                "median_time_to_trough_hours": median(numbers("time_to_trough_hours")),
                "median_full_exit_capital_preserved_reference_pct": median(numbers("full_exit_capital_preserved_reference_pct")),
                "median_full_exit_terminal_upside_foregone_reference_pct": median(numbers("full_exit_terminal_upside_foregone_reference_pct")),
            }
        )
    return output


def build_report(outcome_root: Path, generated_at_utc: str | None) -> dict[str, Any]:
    rows, sidecar_count = collect_rows(outcome_root)
    cohorts = summarize(rows)
    warning_rows = [row for row in rows if row["warning"] not in {"NONE", "UNKNOWN"}]
    return {
        "contract": REPORT_CONTRACT,
        "generated_at_utc": iso_now(generated_at_utc),
        "status": "PASS" if rows else "NO_MATURED_ROWS",
        "source_contract": OUTCOME_CONTRACT,
        "source_sidecar_count": sidecar_count,
        "matured_series_row_count": len(rows),
        "warning_series_row_count": len(warning_rows),
        "cohorts": cohorts,
        "interpretation_boundary": {
            "descriptive_only": True,
            "hit_miss_labels": False,
            "new_thresholds": False,
            "market_rule_change": False,
            "portfolio_action": False,
            "automatic_promotion": False,
            "note": "Measures post-signal upside, drawdown and full-exit reference opportunity cost without defining when to reduce or exit.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outcome-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--generated-at-utc")
    args = parser.parse_args()
    report = build_report(args.outcome_root, args.generated_at_utc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "cohort_count": len(report["cohorts"]), "row_count": report["matured_series_row_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
