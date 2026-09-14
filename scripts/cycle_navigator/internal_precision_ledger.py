from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONTRACT = "CN_INTERNAL_PRECISION_v1"
FORECAST_CONTRACT = "CN_INTERNAL_FROZEN_FORECAST_SET_v1"
EVALUATION_CONTRACT = "CN_INTERNAL_EVALUATION_v1"
POINTER_CONTRACT = "CN_INTERNAL_PRECISION_POINTER_v1"
ACTIVATION_ISSUE_DEFAULT = 27


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_value(value: Any) -> float | None:
    if value is None:
        return None
    result = float(value)
    if result < 0 or result > 100:
        raise ValueError(f"score_out_of_range:{result}")
    return result


def meaningful_text(value: Any) -> bool:
    text = str(value or "").strip()
    return bool(text) and text.upper() != "UNAVAILABLE"


def family_for_parameter(parameter_id: str) -> str:
    mapping = {
        "btc_range": "btc_range",
        "eth_range": "eth_range",
        "ethbtc_condition": "ethbtc",
        "breadth_condition": "breadth",
        "structural_call_1": "regime",
        "structural_call_2": "ethbtc",
        "structural_call_3": "rotation",
        "structural_call_4": "rotation",
        "structural_call_5": "altseason",
        "intraday_day_1_2": "intraday_day_1_2",
        "intraday_day_3_4": "intraday_day_3_4",
        "intraday_day_5_7": "intraday_day_5_7",
    }
    return mapping.get(parameter_id, "other")


def build_family_scores(parameter_scores: list[dict[str, Any]]) -> dict[str, float | None]:
    buckets: dict[str, list[float]] = {}
    for row in parameter_scores:
        parameter_id = str(row.get("parameter_id") or "")
        family = family_for_parameter(parameter_id)
        value = score_value(row.get("score"))
        if value is not None:
            buckets.setdefault(family, []).append(value)
    result: dict[str, float | None] = {}
    families = [
        "regime", "ethbtc", "breadth", "rotation", "altseason",
        "btc_range", "eth_range", "intraday_day_1_2", "intraday_day_3_4", "intraday_day_5_7",
    ]
    for family in families:
        values = buckets.get(family, [])
        result[family] = round(sum(values) / len(values), 1) if values else None
    return result


def load_parameter_scores(repo: Path, completed_week: int, scorecard: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    rows = scorecard.get("parameter_scores")
    if isinstance(rows, list) and rows:
        return rows, "CYCLE_NAVIGATOR_SCORECARD"
    repair_root = repo / "research/repairs"
    candidates = sorted(repair_root.glob(f"*_w{completed_week}_precision_coverage_audit.json")) if repair_root.exists() else []
    for path in reversed(candidates):
        value = read_json(path)
        rows = value.get("parameter_scores")
        if isinstance(rows, list) and rows:
            return rows, str(path.relative_to(repo))
    return [], "UNAVAILABLE"


def freeze_inventory_rows(machine: dict[str, Any], issue: int, year: int, target_week: int) -> list[dict[str, Any]]:
    freeze = machine.get("forecast_freeze") if isinstance(machine.get("forecast_freeze"), dict) else {}
    rows: list[dict[str, Any]] = []

    def add(parameter_id: str, family: str, value: Any, horizon: str, scoring_role: str) -> None:
        if value is None or (isinstance(value, str) and not meaningful_text(value)):
            return
        rows.append({
            "forecast_id": f"CN{issue}-W{target_week:02d}-{parameter_id}",
            "parameter_id": parameter_id,
            "family": family,
            "forecast": value,
            "horizon": horizon,
            "scoring_role": scoring_role,
            "target_iso_year": year,
            "target_iso_week": target_week,
        })

    if freeze.get("btc_range_low") is not None and freeze.get("btc_range_high") is not None:
        add("btc_range", "btc_range", {"low": freeze["btc_range_low"], "high": freeze["btc_range_high"]}, "WEEK_CLOSE", "PUBLIC_WEEKLY")
    if freeze.get("eth_range_low") is not None and freeze.get("eth_range_high") is not None:
        add("eth_range", "eth_range", {"low": freeze["eth_range_low"], "high": freeze["eth_range_high"]}, "WEEK_CLOSE", "PUBLIC_WEEKLY")
    add("ethbtc_condition", "ethbtc", freeze.get("ethbtc_condition"), "WEEK_CLOSE", "PUBLIC_WEEKLY")
    add("breadth_condition", "breadth", freeze.get("breadth_condition"), "WEEK_CLOSE", "PUBLIC_WEEKLY")
    for index, call in enumerate(freeze.get("structural_calls") or [], start=1):
        add(f"structural_call_{index}", family_for_parameter(f"structural_call_{index}"), call, "WEEK_CLOSE", "PUBLIC_WEEKLY")
    intraday = freeze.get("intraday_map") if isinstance(freeze.get("intraday_map"), dict) else {}
    for key in ("day_1_2", "day_3_4", "day_5_7"):
        add(f"intraday_{key}", f"intraday_{key}", intraday.get(key), key.upper(), "INTERNAL_INTRADAY")
    add("base_case_this_week", "weekly_scenario", machine.get("base_case_this_week"), "WEEK_CLOSE", "INTERNAL_CONTEXT")
    add("base_case_2_3_weeks", "multiweek_2_3", machine.get("base_case_2_3_weeks"), "2_3_WEEKS", "INTERNAL_LONG_HORIZON_PENDING")
    add("base_case_4_8_weeks", "multiweek_4_8", machine.get("base_case_4_8_weeks"), "4_8_WEEKS", "INTERNAL_LONG_HORIZON_PENDING")
    return rows


def write_immutable_json(path: Path, value: dict[str, Any]) -> str:
    payload = canonical_bytes(value)
    if path.exists():
        if path.read_bytes() != payload:
            raise SystemExit(f"IMMUTABLE_ARTIFACT_DRIFT:{path}")
        return "UNCHANGED"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return "CREATED"


def fmt(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value:.0f}%" if float(value).is_integer() else f"{value:.1f}%"


def precision_box(completed_week: int, evaluation: dict[str, Any], current_inventory_count: int, current_registration: str) -> str:
    fam = evaluation["family_scores"]
    coverage = evaluation["coverage"]
    structural = evaluation.get("weekly_structural_score")
    misses = len(evaluation.get("self_critique", []))
    return "\n".join([
        f"┌ INTERNAL PRECISION — W{completed_week:02d} review",
        f"│ Public structural {fmt(structural)} | coverage {coverage['accounted']}/{coverage['expected']} ({fmt(coverage['pct'])})",
        f"│ Weekly {fmt(structural)} | Regime {fmt(fam['regime'])} | ETH/BTC {fmt(fam['ethbtc'])} | Breadth {fmt(fam['breadth'])}",
        f"│ Rotation {fmt(fam['rotation'])} | Altseason {fmt(fam['altseason'])} | BTC range {fmt(fam['btc_range'])} | ETH range {fmt(fam['eth_range'])}",
        f"│ Intraday D1–2 {fmt(fam['intraday_day_1_2'])} | D3–4 {fmt(fam['intraday_day_3_4'])} | D5–7 {fmt(fam['intraday_day_5_7'])}",
        f"│ Frozen inventory current: {current_inventory_count} | registration {current_registration}",
        f"│ Self-critique notes {misses} | hindsight edits 0 | missing ≠ miss",
        "└",
    ])


def rebuild_summary_ledger(root: Path) -> int:
    rows: list[dict[str, Any]] = []
    eval_root = root / "evaluations"
    for path in sorted(eval_root.rglob("*.json")) if eval_root.exists() else []:
        value = read_json(path)
        if value.get("contract") != EVALUATION_CONTRACT:
            continue
        rows.append({
            "completed_iso_year": value["completed_iso_year"],
            "completed_iso_week": value["completed_iso_week"],
            "issue_scored": value["issue_scored"],
            "weekly_structural_score": value.get("weekly_structural_score"),
            "family_scores": value.get("family_scores", {}),
            "coverage": value.get("coverage", {}),
            "evaluation_sha256": sha256_path(path),
            "evaluation_path": str(path),
        })
    rows.sort(key=lambda row: (row["completed_iso_year"], row["completed_iso_week"], row["issue_scored"]))
    ledger = root / "INTERNAL_PRECISION_LEDGER.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows))
    return len(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--master-monday-pointer", type=Path, required=True)
    ap.add_argument("--activation-issue", type=int, default=ACTIVATION_ISSUE_DEFAULT)
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    mm_ptr_path = repo / args.master_monday_pointer
    mm_ptr = read_json(mm_ptr_path)
    ptr_path = repo / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json"
    ptr = read_json(ptr_path)
    year = int(ptr["iso_year"])
    target_week = int(ptr["iso_week"])
    completed_week = int(ptr["completed_source_week"])
    issue = int(ptr["issue_number"])
    if int(mm_ptr["iso_year"]) != year or int(mm_ptr["iso_week"]) != completed_week:
        raise SystemExit("MASTER_MONDAY_CN_WEEK_IDENTITY_MISMATCH")
    target_dir = repo / str(ptr["week_dir"])
    machine_path = target_dir / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
    scorecard_path = target_dir / "CYCLE_NAVIGATOR_SCORECARD.json"
    freeze_path = target_dir / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    readable_path = target_dir / "CYCLE_NAVIGATOR_READABLE.md"
    machine = read_json(machine_path)
    scorecard = read_json(scorecard_path)
    freeze = read_json(freeze_path)

    parameter_scores, parameter_source = load_parameter_scores(repo, completed_week, scorecard)
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    for row in parameter_scores:
        pid = str(row.get("parameter_id") or "").strip()
        if not pid or pid in seen:
            raise SystemExit(f"DUPLICATE_OR_EMPTY_PARAMETER_ID:{pid}")
        seen.add(pid)
        score = score_value(row.get("score"))
        status = str(row.get("status") or "NOT_EVALUABLE")
        if status == "NOT_EVALUABLE" and score is not None:
            raise SystemExit(f"NOT_EVALUABLE_WITH_SCORE:{pid}")
        if status != "NOT_EVALUABLE" and score is None:
            raise SystemExit(f"EVALUABLE_WITHOUT_SCORE:{pid}")
        normalized.append({"parameter_id": pid, "family": family_for_parameter(pid), "status": status, "score": score, "evidence": row.get("evidence")})

    expected = len(normalized)
    accounted = len(normalized)
    coverage_pct = 100.0 if expected else 0.0
    family_scores = build_family_scores(normalized)
    evaluation = {
        "contract": EVALUATION_CONTRACT,
        "completed_iso_year": year,
        "completed_iso_week": completed_week,
        "issue_scored": int(scorecard.get("issue_scored") or max(issue - 1, 0)),
        "score_status": scorecard.get("score_status", "UNAVAILABLE"),
        "weekly_structural_score": score_value(scorecard.get("structural_score")),
        "price_range_score": score_value(scorecard.get("price_range_score")),
        "parameter_scores": normalized,
        "parameter_score_source": parameter_source,
        "family_scores": family_scores,
        "coverage": {"expected": expected, "accounted": accounted, "pct": coverage_pct, "silent_omissions": 0},
        "strengths": list(scorecard.get("strengths") or []),
        "self_critique": list(scorecard.get("misses") or []),
        "actual_evidence": {
            "master_monday_pointer_path": str(args.master_monday_pointer),
            "master_monday_pointer_sha256": sha256_path(mm_ptr_path),
            "scorecard_path": str(scorecard_path.relative_to(repo)),
            "scorecard_sha256": sha256_path(scorecard_path),
        },
        "authority": {"portfolio_action": False, "framework_state_change": False, "model_weight_change": False, "public_track_record_rewrite": False},
    }

    internal_root = repo / "05_CYCLE_NAVIGATOR/internal_precision"
    eval_path = internal_root / "evaluations" / str(year) / f"W{completed_week:02d}" / f"CN{evaluation['issue_scored']}.json"
    write_immutable_json(eval_path, evaluation)

    inventory = freeze_inventory_rows(machine, issue, year, target_week)
    registration = "PUBLIC_FREEZE_ONLY_PRE_ACTIVATION"
    forecast_path: Path | None = None
    if issue >= args.activation_issue:
        registration = "PROSPECTIVE_INTERNAL_REGISTERED"
        forecast_set = {
            "contract": FORECAST_CONTRACT,
            "issue_number": issue,
            "target_iso_year": year,
            "target_iso_week": target_week,
            "registered_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_freeze_path": str(freeze_path.relative_to(repo)),
            "source_freeze_sha256": sha256_path(freeze_path),
            "source_machine_package_sha256": sha256_path(machine_path),
            "forecasts": inventory,
            "immutability": "FORECAST_FIELDS_APPEND_NEVER_REWRITE",
            "authority": {"portfolio_action": False, "framework_state_change": False, "public_track_record_rewrite": False},
        }
        forecast_path = internal_root / "forecasts" / str(year) / f"W{target_week:02d}" / f"CN{issue}.json"
        write_immutable_json(forecast_path, forecast_set)

    box = precision_box(completed_week, evaluation, len(inventory), registration)
    original = readable_path.read_text().strip()
    internal_md = (
        f"# INTERNAL CYCLE NAVIGATOR #{issue} — {year}-W{target_week:02d}\n\n"
        "## Precision Box\n\n```text\n" + box + "\n```\n\n"
        "Full parameter rows, evidence hashes and self-critique are retained in `CYCLE_NAVIGATOR_INTERNAL_PRECISION.json`. "
        "Public CN scoring remains separate.\n\n---\n\n" + original + "\n"
    )
    internal_md_path = target_dir / "CYCLE_NAVIGATOR_INTERNAL.md"
    internal_md_path.write_text(internal_md)

    package = {
        "contract": CONTRACT,
        "issue_number": issue,
        "target_iso_year": year,
        "target_iso_week": target_week,
        "completed_source_week": completed_week,
        "evaluation": evaluation,
        "current_forecast_inventory": {
            "registration": registration,
            "count": len(inventory),
            "rows": inventory,
            "forecast_set_path": str(forecast_path.relative_to(repo)) if forecast_path else None,
        },
        "precision_box": box,
        "public_score_separation": "INTERNAL_PRECISION_DOES_NOT_REWRITE_PUBLIC_CN_TRACK_RECORD",
        "hindsight_rewrite": False,
    }
    package_path = target_dir / "CYCLE_NAVIGATOR_INTERNAL_PRECISION.json"
    package_path.write_bytes(canonical_bytes(package))

    ledger_count = rebuild_summary_ledger(internal_root)
    pointer = {
        "contract": POINTER_CONTRACT,
        "issue_number": issue,
        "iso_year": year,
        "iso_week": target_week,
        "completed_source_week": completed_week,
        "internal_markdown_path": str(internal_md_path.relative_to(repo)),
        "internal_precision_path": str(package_path.relative_to(repo)),
        "internal_precision_sha256": sha256_path(package_path),
        "evaluation_path": str(eval_path.relative_to(repo)),
        "forecast_set_path": str(forecast_path.relative_to(repo)) if forecast_path else None,
        "ledger_row_count": ledger_count,
        "status": "READY" if normalized else "DEGRADED_NO_PARAMETER_ROWS",
    }
    latest_pointer = internal_root / "LATEST_INTERNAL_PRECISION_POINTER.json"
    latest_pointer.parent.mkdir(parents=True, exist_ok=True)
    latest_pointer.write_bytes(canonical_bytes(pointer))
    print(json.dumps(pointer, sort_keys=True))


if __name__ == "__main__":
    main()
