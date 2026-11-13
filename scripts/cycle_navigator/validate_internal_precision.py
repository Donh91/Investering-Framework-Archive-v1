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



def authorized_w46_reissue_preserving_original_claims(
    repo: Path, root: Path, internal: dict[str, Any],
    public_freeze_path: Path, machine_path: Path,
) -> bool:
    """Accept only W46's original, immutable internal claims after its approved
    same-Monday public daily-path repair. Never rewrite the historical freeze,
    treat a new issue as its predecessor, or use this for any other week.
    """
    try:
        expected_root = repo / "05_CYCLE_NAVIGATOR/weekly/2026/W46"
        if root.resolve() != expected_root.resolve():
            return False
        base = root / "revisions/2026-11-09-first-unavailable"
        request = read_json(root / "W46_OWNER_REISSUE_REQUEST.json")
        source = read_json(root / "CYCLE_NAVIGATOR_SOURCE_MANIFEST.json")
        archive = read_json(base / "BEFORE_INTEGRITY_MANIFEST.json")
        old_public_path = base / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
        old_machine_path = base / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
        old_public = read_json(old_public_path)
        new_public = read_json(public_freeze_path)
        old_machine = read_json(old_machine_path)
        new_machine = read_json(machine_path)
        amendment = source.get("owner_approved_same_day_revision")
        if not isinstance(amendment, dict):
            return False
        if (
            request.get("contract") != "CN_OWNER_APPROVED_W46_SAME_DAY_REISSUE_v1"
            or request.get("owner_scope") != "2026-W46"
            or request.get("original_machine_issue_number") != 34
            or request.get("original_public_issue_number") != 33
            or request.get("original_daily_product_status") != "INCOMPLETE"
            or request.get("keep_original_revision") is not True
            or request.get("no_backdating") is not True
            or request.get("no_hindsight") is not True
            or request.get("only_before_2026_11_10_utc") is not True
            or amendment.get("contract") != request["contract"]
            or amendment.get("forecast_week") != "2026-W46"
            or amendment.get("machine_issue_number") != 34
            or amendment.get("public_issue_number") != 33
            or amendment.get("no_api_request") is not True
            or amendment.get("no_portfolio_execution") is not True
            or amendment.get("scoring_policy") != "FIRST_KNOWN_AMENDED_ISSUANCE_NO_HINDSIGHT_OR_RESCORING"
            or archive.get("contract") != "CN_W46_BEFORE_ARCHIVE_v1"
            or internal.get("contract") != "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE_v2"
            or internal.get("issue_number") != 34
            or internal.get("iso_year") != 2026
            or internal.get("iso_week") != 46
            or internal.get("rules", {}).get("no_hindsight_rewrite") is not True
        ):
            return False
        before = amendment.get("before_forecast_sha256")
        after = amendment.get("after_forecast_sha256")
        if (
            not isinstance(before, str) or len(before) != 64
            or not isinstance(after, str) or len(after) != 64
            or before == after
            or before != request.get("original_forecast_sha256")
            or before != internal.get("source_public_freeze_sha256")
            or before != archive.get("original_revision_sha256")
            or before != archive.get("files", {}).get("CYCLE_NAVIGATOR_FORECAST_FREEZE.json")
            or before != sha256_path(old_public_path)
            or after != sha256_path(public_freeze_path)
            or after != source.get("owner_approved_same_day_revision", {}).get("after_forecast_sha256")
            or archive.get("files", {}).get("CYCLE_NAVIGATOR_MACHINE_PACKAGE.json") != sha256_path(old_machine_path)
            or internal.get("source_machine_package_sha256_at_materialization") != sha256_path(old_machine_path)
            or amendment.get("before_issued_utc") != "2026-11-09T10:33:42Z"
            or amendment.get("after_issued_utc") != "2026-11-09T10:52:34.925867Z"
        ):
            return False

        # The exact original scientific claims must be unchanged. The amendment
        # issued previously unavailable DAILY points, not a new risk thesis.
        public_claim_fields = (
            "btc_range_low", "btc_range_high", "eth_range_low",
            "eth_range_high", "ethbtc_condition", "breadth_condition",
            "structural_calls", "intraday_map",
        )
        machine_claim_fields = ("base_case_2_3_weeks", "base_case_4_8_weeks")
        if any(old_public.get(k) != new_public.get(k) for k in public_claim_fields):
            return False
        if any(old_machine.get(k) != new_machine.get(k) for k in machine_claim_fields):
            return False
        for asset in ("BTC", "ETH"):
            old_path = (old_public.get("daily_price_path") or {}).get(asset) or {}
            new_path = (new_public.get("daily_price_path") or {}).get(asset) or {}
            if (
                old_path.get("status") != "UNAVAILABLE"
                or old_path.get("points") != []
                or new_path.get("status") != "PUBLISHED"
                or not isinstance(new_path.get("points"), list)
                or len(new_path["points"]) != 7
            ):
                return False
        claims = internal.get("claims")
        if not isinstance(claims, list) or len(claims) != 14:
            return False
        ids = [c.get("claim_id") for c in claims if isinstance(c, dict)]
        if len(ids) != 14 or len(set(ids)) != 14:
            return False
        if any(
            not c["claim_id"].startswith("CN34-Y2026-W46-")
            or c.get("source_public_freeze_sha256") != before
            or c.get("source_machine_package_sha256_at_materialization") != sha256_path(old_machine_path)
            for c in claims
        ):
            return False
        return True
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return False



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
        if not authorized_w46_reissue_preserving_original_claims(
            repo, root, current,
            root / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json",
            root / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json",
        ):
            raise SystemExit("INTERNAL_PRECISION_CURRENT_FREEZE_HASH_MISMATCH")
        # Historical CN34 internal claims are the first-issued science record.
        # Do not silently rebind their source hash to the revised public path.
        print("INTERNAL_PRECISION_W46_REISSUE_ORIGINAL_CLAIMS_RETAINED")
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
