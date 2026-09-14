from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.strip().upper() != "UNAVAILABLE"


def expected_parameter_ids(freeze: dict[str, Any]) -> list[str]:
    result: list[str] = []
    if freeze.get("btc_range_low") is not None and freeze.get("btc_range_high") is not None:
        result.append("btc_range")
    if freeze.get("eth_range_low") is not None and freeze.get("eth_range_high") is not None:
        result.append("eth_range")
    if nonempty(freeze.get("ethbtc_condition")):
        result.append("ethbtc_condition")
    if nonempty(freeze.get("breadth_condition")):
        result.append("breadth_condition")
    for i, call in enumerate(freeze.get("structural_calls") or [], start=1):
        if nonempty(call):
            result.append(f"structural_call_{i}")
    intraday = freeze.get("intraday_map")
    if isinstance(intraday, dict):
        for bucket in ("day_1_2", "day_3_4", "day_5_7"):
            if nonempty(intraday.get(bucket)):
                result.append(f"intraday_{bucket}")
    return result


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    ptr = read_json(repo / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
    root = repo / ptr["week_dir"]
    required = [
        "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json",
        "CYCLE_NAVIGATOR_INTERNAL_PRECISION_SCORECARD.json",
        "CYCLE_NAVIGATOR_INTERNAL_PRECISION_BOX.md",
        "CYCLE_NAVIGATOR_INTERNAL.md",
    ]
    missing = [name for name in required if not (root / name).exists()]
    if missing:
        raise SystemExit("INTERNAL_PRECISION_MISSING_ARTIFACTS:" + ",".join(missing))

    score = read_json(root / "CYCLE_NAVIGATOR_INTERNAL_PRECISION_SCORECARD.json")
    current = read_json(root / "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json")
    public = read_json(root / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json")
    if current.get("source_public_freeze_sha256") != sha256_path(root / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"):
        raise SystemExit("INTERNAL_PRECISION_CURRENT_FREEZE_HASH_MISMATCH")
    ids = [c.get("claim_id") for c in current.get("claims", [])]
    if not ids or len(ids) != len(set(ids)) or any(not x for x in ids):
        raise SystemExit("INTERNAL_PRECISION_CURRENT_CLAIM_IDS_INVALID")
    current_param_ids = {c.get("source_parameter_id") for c in current.get("claims", [])}
    missing_current = [p for p in expected_parameter_ids(public) if p not in current_param_ids]
    if missing_current:
        raise SystemExit("INTERNAL_PRECISION_CURRENT_FREEZE_COVERAGE_MISSING:" + ",".join(missing_current))

    completed_week = int(ptr["completed_source_week"])
    target_year = int(ptr["iso_year"])
    prior = repo / "05_CYCLE_NAVIGATOR/weekly" / str(target_year) / f"W{completed_week:02d}" / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    if not prior.exists():
        raise SystemExit("INTERNAL_PRECISION_PRIOR_FREEZE_MISSING")
    expected = expected_parameter_ids(read_json(prior))
    rows = score.get("parameter_scores") or []
    got = [r.get("parameter_id") for r in rows]
    if got != expected:
        raise SystemExit(f"INTERNAL_PRECISION_SCORE_COVERAGE_ORDER_MISMATCH:{got}!={expected}")
    if int(score.get("mature_parameter_count", -1)) != len(expected) or int(score.get("accounted_parameter_count", -1)) != len(expected):
        raise SystemExit("INTERNAL_PRECISION_MATURE_COUNT_MISMATCH")
    if float(score.get("mature_coverage_pct", -1)) != 100.0:
        raise SystemExit("INTERNAL_PRECISION_COVERAGE_NOT_100")
    for row in rows:
        if row.get("status") not in {"SUPPORTED", "MIXED", "CONTRADICTED", "NOT_EVALUABLE"}:
            raise SystemExit("INTERNAL_PRECISION_BAD_STATUS")
        expected_score = {"SUPPORTED": 100.0, "MIXED": 50.0, "CONTRADICTED": 0.0, "NOT_EVALUABLE": None}[row["status"]]
        if expected_score is None:
            if row.get("score") is not None:
                raise SystemExit("INTERNAL_PRECISION_NULL_SCORE_REQUIRED")
        elif float(row.get("score")) != expected_score:
            raise SystemExit("INTERNAL_PRECISION_SCORE_STATUS_MISMATCH")
    if any("alias" in key for key in (score.get("family_scores") or {})):
        raise SystemExit("INTERNAL_PRECISION_ALIAS_LEAKED_TO_FAMILY_HEADLINE")

    box = (root / "CYCLE_NAVIGATOR_INTERNAL_PRECISION_BOX.md").read_text().splitlines()
    if len(box) > 9:
        raise SystemExit("INTERNAL_PRECISION_BOX_TOO_LONG")
    for token in ("Weekly structural", "Regime", "ETH/BTC", "Breadth", "Rotation", "Altseason", "D1–2", "D3–4", "D5–7", "Self-critique"):
        if not any(token in line for line in box):
            raise SystemExit("INTERNAL_PRECISION_BOX_TOKEN_MISSING:" + token)

    summary_path = repo / "05_CYCLE_NAVIGATOR/track_record/CN_INTERNAL_PRECISION_LEDGER.jsonl"
    param_path = repo / "05_CYCLE_NAVIGATOR/track_record/CN_INTERNAL_PARAMETER_LEDGER.jsonl"
    if not summary_path.exists() or not param_path.exists():
        raise SystemExit("INTERNAL_PRECISION_LEDGER_MISSING")
    summary = read_jsonl(summary_path)
    params = read_jsonl(param_path)
    score_keys = [r.get("score_key") for r in summary]
    claim_keys = [r.get("claim_id") for r in params]
    if len(score_keys) != len(set(score_keys)):
        raise SystemExit("INTERNAL_PRECISION_SUMMARY_LEDGER_DUPLICATE")
    if len(claim_keys) != len(set(claim_keys)):
        raise SystemExit("INTERNAL_PRECISION_PARAMETER_LEDGER_DUPLICATE")
    current_score_key = f"Y{score['completed_iso_year']}-W{int(score['completed_iso_week']):02d}-CN{score['issue_scored']}"
    if current_score_key not in score_keys:
        raise SystemExit("INTERNAL_PRECISION_SUMMARY_ROW_MISSING")
    prior_sha = sha256_path(prior)
    current_param_rows = [r for r in params if int(r.get("completed_iso_week", -1)) == completed_week and int(r.get("issue_scored", -1)) == int(score["issue_scored"])]
    if len(current_param_rows) != len(expected):
        raise SystemExit("INTERNAL_PRECISION_PARAMETER_LEDGER_WEEK_COVERAGE_MISMATCH")
    if any(r.get("source_prior_public_freeze_sha256") != prior_sha for r in current_param_rows):
        raise SystemExit("INTERNAL_PRECISION_PARAMETER_SOURCE_HASH_MISMATCH")

    print(json.dumps({
        "status": "PASS",
        "week_dir": ptr["week_dir"],
        "issue": ptr["issue_number"],
        "mature_parameter_count": len(expected),
        "parameter_ledger_rows": len(params),
        "summary_ledger_rows": len(summary),
        "box_lines": len(box),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
