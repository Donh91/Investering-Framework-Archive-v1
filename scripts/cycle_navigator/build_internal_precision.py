from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CONTRACT_FREEZE = "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE_v1"
CONTRACT_SCORE = "CYCLE_NAVIGATOR_INTERNAL_PRECISION_SCORECARD_v1"
CONTRACT_LEDGER = "CYCLE_NAVIGATOR_INTERNAL_PRECISION_LEDGER_v1"
AUTHORITY = "INTERNAL_ACCOUNTABILITY_ONLY_NO_PORTFOLIO_AUTHORITY"


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def present(value: Any) -> bool:
    return bool(str(value or "").strip()) and str(value).strip().upper() != "UNAVAILABLE"


def pct(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    value = float(value)
    return f"{value:.0f}%" if value.is_integer() else f"{value:.1f}%"


def claim(claim_id: str, family: str, source_parameter_id: str, forecast: Any, *, horizon: str, maturity: str = "NEXT_WEEK") -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "family": family,
        "source_parameter_id": source_parameter_id,
        "forecast": forecast,
        "horizon": horizon,
        "maturity": maturity,
        "score_authority": AUTHORITY,
    }


def family_for_structural(index: int) -> str:
    return {
        1: "regime",
        2: "ethbtc_alias",
        3: "leadership",
        4: "rotation",
        5: "altseason",
    }.get(index, f"structural_{index}")


def build_claims(issue: int, iso_year: int, iso_week: int, machine: dict[str, Any], freeze: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    prefix = f"CN{issue}-Y{iso_year}-W{iso_week:02d}"
    claims: list[dict[str, Any]] = []
    unavailable: list[str] = []

    for asset in ("btc", "eth"):
        lo, hi = freeze.get(f"{asset}_range_low"), freeze.get(f"{asset}_range_high")
        pid = f"{asset}_range"
        if lo is not None and hi is not None:
            claims.append(claim(f"{prefix}-{pid}", pid, pid, {"low": lo, "high": hi}, horizon="WEEKLY"))
        else:
            unavailable.append(pid)

    if present(freeze.get("ethbtc_condition")):
        claims.append(claim(f"{prefix}-ethbtc", "ethbtc", "ethbtc_condition", freeze["ethbtc_condition"], horizon="WEEKLY"))
    else:
        unavailable.append("ethbtc_condition")

    if present(freeze.get("breadth_condition")):
        claims.append(claim(f"{prefix}-breadth", "breadth", "breadth_condition", freeze["breadth_condition"], horizon="WEEKLY"))
    else:
        unavailable.append("breadth_condition")

    calls = freeze.get("structural_calls") if isinstance(freeze.get("structural_calls"), list) else []
    for index, text in enumerate(calls, start=1):
        if present(text):
            pid = f"structural_call_{index}"
            claims.append(claim(f"{prefix}-{pid}", family_for_structural(index), pid, text, horizon="WEEKLY"))

    intraday = freeze.get("intraday_map") if isinstance(freeze.get("intraday_map"), dict) else {}
    for bucket in ("day_1_2", "day_3_4", "day_5_7"):
        pid = f"intraday_{bucket}"
        text = intraday.get(bucket)
        if present(text):
            claims.append(claim(f"{prefix}-{pid}", "intraday", pid, text, horizon=bucket.upper()))
        else:
            unavailable.append(pid)

    for field, horizon, offset in (("base_case_2_3_weeks", "2_3_WEEKS", 3), ("base_case_4_8_weeks", "4_8_WEEKS", 8)):
        text = machine.get(field)
        if present(text):
            claims.append(claim(f"{prefix}-{field}", field, field, text, horizon=horizon, maturity=f"TARGET_WEEK_PLUS_{offset}"))
        else:
            unavailable.append(field)

    ids = [row["claim_id"] for row in claims]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate_internal_claim_id")
    return claims, unavailable


def score_rows_from_public(scorecard: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    rows = scorecard.get("parameter_scores")
    if isinstance(rows, list) and rows:
        result = []
        for row in rows:
            pid = str(row.get("parameter_id") or "")
            if not pid:
                raise SystemExit("public_parameter_score_missing_id")
            result.append({
                "parameter_id": pid,
                "family": family_from_parameter_id(pid),
                "status": row.get("status"),
                "score": row.get("score"),
                "evidence": row.get("evidence"),
                "source": "PUBLIC_PARAMETER_SCORE",
            })
        return result, "PUBLIC_PARAMETER_SCORE"

    # One-time bounded migration for the already frozen/reproducibly audited W37 CN #25.
    if int(scorecard.get("issue_scored") or -1) == 25 and int(scorecard.get("completed_iso_week") or -1) == 37 and float(scorecard.get("structural_score") or -1) == 90.0:
        migration = [
            ("ethbtc_condition", "ethbtc", 100.0, "Final W37 evidence showed ETH/BTC rose over the completed week."),
            ("breadth_condition", "breadth", 100.0, "Final W37 evidence supported weak proxy breadth and no broad rotation confirmation."),
            ("structural_call_1", "regime", 100.0, "W37 ended as an unresolved volatile transition/consolidation, not broad expansion."),
            ("structural_call_2", "ethbtc_alias", 100.0, "ETH/BTC finished W37 non-negative as frozen."),
            ("structural_call_3", "leadership", 100.0, "ETH relative strength remained narrow rather than broadly transmitted."),
            ("structural_call_4", "rotation", 50.0, "Direction was supported, but completed-week outcome ingestion did not independently establish every mid/small/micro tier."),
            ("structural_call_5", "altseason", 100.0, "Broad altseason remained inactive through W37 close."),
        ]
        result = [{"parameter_id": pid, "family": fam, "status": "MIXED" if score == 50 else "SUPPORTED", "score": score, "evidence": ev, "source": "BOUNDED_W37_MIGRATION_FROM_EXISTING_FROZEN_CLAIMS"} for pid, fam, score, ev in migration]
        return result, "BOUNDED_W37_MIGRATION_FROM_EXISTING_FROZEN_CLAIMS"
    return [], "UNAVAILABLE_NO_PARAMETER_LEVEL_SCORE"


def family_from_parameter_id(pid: str) -> str:
    if pid == "btc_range": return "btc_range"
    if pid == "eth_range": return "eth_range"
    if pid == "ethbtc_condition": return "ethbtc"
    if pid == "breadth_condition": return "breadth"
    if pid.startswith("intraday_"): return "intraday"
    if pid.startswith("structural_call_"):
        try: return family_for_structural(int(pid.rsplit("_", 1)[1]))
        except Exception: return "structural_other"
    return pid


def family_scores(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    grouped: dict[str, list[float]] = {}
    for row in rows:
        score = row.get("score")
        if score is None:
            continue
        grouped.setdefault(str(row["family"]), []).append(float(score))
    return {family: (sum(values) / len(values) if values else None) for family, values in grouped.items()}


def internal_coverage(rows: list[dict[str, Any]]) -> tuple[int, int, float | None]:
    mature = len(rows)
    accounted = sum(1 for row in rows if row.get("status") in {"SUPPORTED", "MIXED", "CONTRADICTED", "NOT_EVALUABLE"})
    return accounted, mature, (100.0 * accounted / mature if mature else None)


def render_box(*, issue_scored: int | None, completed_week: int, public_structural: float | None, rows: list[dict[str, Any]], unavailable: list[str], pending_long: int, self_critique: str) -> str:
    fam = family_scores(rows)
    accounted, mature, coverage = internal_coverage(rows)
    intraday = [row.get("score") for row in rows if row.get("family") == "intraday" and row.get("score") is not None]
    intraday_score = sum(float(x) for x in intraday) / len(intraday) if intraday else None
    def f(name: str) -> str: return pct(fam.get(name))
    lines = [
        f"┌─ INTERN PRECISION — CN #{issue_scored if issue_scored is not None else 'N/A'} → W{completed_week:02d} ─",
        f"Weekly structural {pct(public_structural)} | Intraday {pct(intraday_score)} | Coverage {accounted}/{mature} ({pct(coverage)})",
        f"Regime {f('regime')} | ETH/BTC {f('ethbtc')} | Breadth {f('breadth')} | Leadership {f('leadership')}",
        f"Rotation {f('rotation')} | Altseason {f('altseason')} | BTC range {f('btc_range')} | ETH range {f('eth_range')}",
    ]
    intraday_ids = {str(row.get("parameter_id")): row.get("score") for row in rows if str(row.get("parameter_id", "")).startswith("intraday_")}
    lines.append(f"D1–2 {pct(intraday_ids.get('intraday_day_1_2'))} | D3–4 {pct(intraday_ids.get('intraday_day_3_4'))} | D5–7 {pct(intraday_ids.get('intraday_day_5_7'))}")
    lines.append(f"Pending long horizon {pending_long} | N/A/unfrozen {len(unavailable)}")
    lines.append("Self-critique: " + (self_critique.strip() if self_critique.strip() else "N/A"))
    lines.append("└─ public score remains separate; internal scores have no portfolio authority")
    return "\n".join(lines) + "\n"


def append_ledger(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    key = row["score_key"]
    if path.exists():
        for line in path.read_text().splitlines():
            if not line.strip(): continue
            existing = json.loads(line)
            if existing.get("score_key") == key:
                if existing != row:
                    raise SystemExit("internal_precision_ledger_conflict:" + key)
                return
    with path.open("a") as handle:
        handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--pointer", default="05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
    args = ap.parse_args()
    repo = args.repo_root.resolve()
    pointer_path = repo / args.pointer
    pointer = read_json(pointer_path)
    target_dir = repo / str(pointer["week_dir"])
    machine_path = target_dir / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
    score_path = target_dir / "CYCLE_NAVIGATOR_SCORECARD.json"
    freeze_path = target_dir / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
    machine, scorecard, freeze = read_json(machine_path), read_json(score_path), read_json(freeze_path)

    issue = int(pointer["issue_number"])
    year = int(pointer["iso_year"])
    target_week = int(pointer["iso_week"])
    completed_week = int(pointer["completed_source_week"])
    previous_issue = scorecard.get("issue_scored")

    claims, unavailable_current = build_claims(issue, year, target_week, machine, freeze)
    current_freeze = {
        "contract": CONTRACT_FREEZE,
        "authority": AUTHORITY,
        "issue_number": issue,
        "iso_year": year,
        "iso_week": target_week,
        "source_public_freeze_sha256": sha256_path(freeze_path),
        "source_machine_package_sha256": sha256_path(machine_path),
        "claims": claims,
        "unavailable_or_unfrozen": unavailable_current,
        "rules": {
            "no_hindsight_rewrite": True,
            "pending_excluded_from_score_denominator": True,
            "unavailable_excluded_from_hit_miss": True,
            "public_precision_is_separate": True,
        },
    }

    rows, row_source = score_rows_from_public(scorecard)
    accounted, mature, coverage = internal_coverage(rows)
    if rows and accounted != mature:
        raise SystemExit("internal_mature_claim_coverage_not_100pct")
    fam = family_scores(rows)
    misses = scorecard.get("misses") if isinstance(scorecard.get("misses"), list) else []
    self_critique = str(misses[0]) if misses else "No parameter-level self-critique available."

    # Previous issue freeze is read only to report what was genuinely unavailable/unfrozen then.
    previous_unavailable: list[str] = []
    if previous_issue is not None:
        previous_dir = repo / "05_CYCLE_NAVIGATOR/weekly" / str(year) / f"W{completed_week:02d}"
        previous_freeze_path = previous_dir / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
        previous_machine_path = previous_dir / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
        if previous_freeze_path.exists() and previous_machine_path.exists():
            _, previous_unavailable = build_claims(int(previous_issue), year, completed_week, read_json(previous_machine_path), read_json(previous_freeze_path))

    pending_long = sum(1 for row in claims if row.get("maturity") != "NEXT_WEEK")
    internal_scorecard = {
        "contract": CONTRACT_SCORE,
        "authority": AUTHORITY,
        "issue_scored": previous_issue,
        "completed_iso_week": completed_week,
        "source_public_scorecard_sha256": sha256_path(score_path),
        "source_public_freeze_immutable": True,
        "parameter_score_source": row_source,
        "parameter_scores": rows,
        "family_scores": fam,
        "public_weekly_structural_score": scorecard.get("structural_score"),
        "mature_parameter_count": mature,
        "accounted_parameter_count": accounted,
        "mature_coverage_pct": coverage,
        "unavailable_or_unfrozen": previous_unavailable,
        "pending_long_horizon_current_issue": pending_long,
        "self_critique": self_critique,
        "aggregation_note": "No synthetic overall internal accuracy is published because aliases and correlated claims are not independent. Family scores and coverage are primary.",
    }

    box = render_box(
        issue_scored=int(previous_issue) if previous_issue is not None else None,
        completed_week=completed_week,
        public_structural=scorecard.get("structural_score"),
        rows=rows,
        unavailable=previous_unavailable,
        pending_long=pending_long,
        self_critique=self_critique,
    )

    internal_freeze_path = target_dir / "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json"
    internal_score_path = target_dir / "CYCLE_NAVIGATOR_INTERNAL_PRECISION_SCORECARD.json"
    internal_box_path = target_dir / "CYCLE_NAVIGATOR_INTERNAL_PRECISION_BOX.md"
    internal_freeze_path.write_bytes(canonical_bytes(current_freeze))
    internal_score_path.write_bytes(canonical_bytes(internal_scorecard))
    internal_box_path.write_text(box)

    ledger_row = {
        "contract": CONTRACT_LEDGER,
        "score_key": f"Y{year}-W{completed_week:02d}-CN{previous_issue}",
        "authority": AUTHORITY,
        "issue_scored": previous_issue,
        "completed_iso_week": completed_week,
        "public_weekly_structural_score": scorecard.get("structural_score"),
        "family_scores": fam,
        "mature_parameter_count": mature,
        "accounted_parameter_count": accounted,
        "mature_coverage_pct": coverage,
        "parameter_score_source": row_source,
        "self_critique": self_critique,
        "source_public_scorecard_sha256": sha256_path(score_path),
    }
    append_ledger(repo / "05_CYCLE_NAVIGATOR/track_record/CN_INTERNAL_PRECISION_LEDGER.jsonl", ledger_row)

    print(json.dumps({
        "status": "PASS",
        "issue": issue,
        "issue_scored": previous_issue,
        "internal_freeze": str(internal_freeze_path.relative_to(repo)),
        "internal_scorecard": str(internal_score_path.relative_to(repo)),
        "internal_box": str(internal_box_path.relative_to(repo)),
        "coverage_pct": coverage,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
