#!/usr/bin/env python3
"""Deterministically pair matured Shadow Compass v2 and Official Compass outcomes.

Pair selection is outcome-blind: it uses only frozen horizon/time-basis/issue metadata.
Correctness and realized returns are disclosed only after the pair is selected.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

OFFICIAL_ROOT = Path("04_MARKET_LEARNING/handlekompas/official/outcomes")
SHADOW_ROOT = Path("04_MARKET_LEARNING/handlekompas/shadow_v2/outcomes")
OFFICIAL_CONTRACT = "OFFICIAL_DAILY_COMPASS_OUTCOME_v1"
SHADOW_CONTRACT = "SHADOW_COMPASS_V2_OUTCOME_v1"
REPORT_CONTRACT = "SHADOW_OFFICIAL_COMPASS_COMPARISON_REPORT_v1"
PAIRING_CONTRACT = "SHADOW_OFFICIAL_PAIRING_v1"


def parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.utcoffset() is None:
        return None
    return dt.astimezone(timezone.utc)


def _pair_key(row: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    tb = row.get("time_basis") or {}
    return (
        row.get("horizon"),
        tb.get("start_reference_at_utc"),
        row.get("target_at_utc"),
        row.get("target_observation_at_utc"),
    )


def _row_id(row: dict[str, Any], shadow: bool) -> str:
    key = "forecast_id" if shadow else "compass_id"
    return str(row.get(key) or row.get("source_path") or "UNKNOWN")


def _result_category(shadow_result: Any, official_result: Any) -> str:
    if shadow_result == "CORRECT" and official_result == "CORRECT":
        return "BOTH_CORRECT"
    if shadow_result == "INCORRECT" and official_result == "INCORRECT":
        return "BOTH_INCORRECT"
    if shadow_result == "CORRECT" and official_result == "INCORRECT":
        return "SHADOW_CORRECT_OFFICIAL_INCORRECT"
    if shadow_result == "INCORRECT" and official_result == "CORRECT":
        return "OFFICIAL_CORRECT_SHADOW_INCORRECT"
    if shadow_result == "CORRECT" and official_result == "ABSTAINED":
        return "SHADOW_CORRECT_OFFICIAL_ABSTAINED"
    if shadow_result == "INCORRECT" and official_result == "ABSTAINED":
        return "SHADOW_INCORRECT_OFFICIAL_ABSTAINED"
    if shadow_result == "ABSTAINED" and official_result == "CORRECT":
        return "OFFICIAL_CORRECT_SHADOW_ABSTAINED"
    if shadow_result == "ABSTAINED" and official_result == "INCORRECT":
        return "OFFICIAL_INCORRECT_SHADOW_ABSTAINED"
    if shadow_result == "ABSTAINED" and official_result == "ABSTAINED":
        return "BOTH_ABSTAINED"
    return "NON_COMPARABLE_RESULT_STATE"


def _realized_match(shadow: dict[str, Any], official: dict[str, Any]) -> bool:
    sr = shadow.get("realized") or {}
    orow = official.get("realized") or {}
    for key in (
        "btc_return_pct",
        "eth_return_pct",
        "ethbtc_return_pct",
        "btc_mfe_pct",
        "btc_mae_pct",
        "eth_mfe_pct",
        "eth_mae_pct",
    ):
        a, b = sr.get(key), orow.get(key)
        if a is None and b is None:
            continue
        if not isinstance(a, (int, float)) or isinstance(a, bool):
            return False
        if not isinstance(b, (int, float)) or isinstance(b, bool):
            return False
        if not math.isfinite(float(a)) or not math.isfinite(float(b)):
            return False
        if not math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12):
            return False
    return True


def pair_outcomes(
    official_rows: Iterable[dict[str, Any]],
    shadow_rows: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    official = [dict(row) for row in official_rows]
    shadow = [
        dict(row)
        for row in shadow_rows
        if ((row.get("comparison_metadata") or {}).get("official_comparison_eligible") is not False)
    ]

    candidates: list[tuple[float, str, str, int, int]] = []
    for si, srow in enumerate(shadow):
        s_issue = parse_utc(srow.get("issued_at_utc"))
        if s_issue is None or any(value in (None, "") for value in _pair_key(srow)):
            continue
        for oi, orow in enumerate(official):
            o_issue = parse_utc(orow.get("issued_at_utc"))
            if o_issue is None or _pair_key(srow) != _pair_key(orow):
                continue
            distance = abs((s_issue - o_issue).total_seconds())
            candidates.append(
                (
                    distance,
                    _row_id(srow, True),
                    _row_id(orow, False),
                    si,
                    oi,
                )
            )

    used_shadow: set[int] = set()
    used_official: set[int] = set()
    selected: list[tuple[int, int, float]] = []
    for distance, _, _, si, oi in sorted(candidates):
        if si in used_shadow or oi in used_official:
            continue
        used_shadow.add(si)
        used_official.add(oi)
        selected.append((si, oi, distance))

    pairs: list[dict[str, Any]] = []
    for si, oi, distance in sorted(
        selected,
        key=lambda item: (_row_id(shadow[item[0]], True), _row_id(official[item[1]], False)),
    ):
        srow, orow = shadow[si], official[oi]
        s_issue, o_issue = parse_utc(srow.get("issued_at_utc")), parse_utc(orow.get("issued_at_utc"))
        realized_match = _realized_match(srow, orow)
        asset_comparisons: dict[str, Any] = {}
        for asset in ("btc", "eth"):
            s_acc = ((srow.get("direction_accuracy") or {}).get(asset) or {})
            o_acc = ((orow.get("direction_accuracy") or {}).get(asset) or {})
            s_result, o_result = s_acc.get("result"), o_acc.get("result")
            asset_comparisons[asset] = {
                "shadow_result": s_result,
                "official_result": o_result,
                "comparison_state": (
                    _result_category(s_result, o_result)
                    if realized_match
                    else "PAIR_INTEGRITY_FAIL"
                ),
                "shadow_predicted": s_acc.get("predicted"),
                "official_predicted": o_acc.get("predicted"),
            }
        signed_minutes = (
            (s_issue - o_issue).total_seconds() / 60.0
            if s_issue is not None and o_issue is not None
            else None
        )
        pairs.append(
            {
                "pairing_contract": PAIRING_CONTRACT,
                "shadow_forecast_id": srow.get("forecast_id"),
                "official_compass_id": orow.get("compass_id"),
                "horizon": srow.get("horizon"),
                "time_basis": {
                    "start_reference_at_utc": (srow.get("time_basis") or {}).get(
                        "start_reference_at_utc"
                    ),
                    "target_at_utc": srow.get("target_at_utc"),
                    "target_observation_at_utc": srow.get("target_observation_at_utc"),
                    "issue_delta_shadow_minus_official_minutes": (
                        round(signed_minutes, 6) if signed_minutes is not None else None
                    ),
                    "absolute_issue_delta_minutes": round(distance / 60.0, 6),
                },
                "integrity": {
                    "status": "PASS" if realized_match else "FAIL",
                    "same_frozen_window": True,
                    "realized_path_matches": realized_match,
                    "selection_used_outcome_correctness": False,
                    "selection_used_realized_return": False,
                },
                "asset_comparisons": asset_comparisons,
                "baselines": {
                    "shadow": srow.get("baselines"),
                    "official": orow.get("baselines"),
                },
                "provenance": {
                    "shadow_outcome_path": srow.get("source_path"),
                    "official_outcome_path": orow.get("source_path"),
                    "shadow_forecast_path": srow.get("forecast_path"),
                    "official_forecast_path": orow.get("forecast_path"),
                    "shadow_outcome_sha256": srow.get("outcome_sha256"),
                    "official_outcome_sha256": orow.get("outcome_sha256"),
                    "different_forecast_families_disclosed": True,
                },
                "cautions": {
                    "overlap_is_not_independence": True,
                    "serial_correlation_possible": True,
                    "aggregate_winner_authorized": False,
                },
            }
        )

    unpaired_shadow = [
        {
            "forecast_id": row.get("forecast_id"),
            "horizon": row.get("horizon"),
            "issued_at_utc": row.get("issued_at_utc"),
            "source_path": row.get("source_path"),
            "reason": "NO_UNUSED_OFFICIAL_OUTCOME_WITH_IDENTICAL_FROZEN_WINDOW",
        }
        for i, row in enumerate(shadow)
        if i not in used_shadow
    ]

    return {
        "contract": REPORT_CONTRACT,
        "pairing_contract": PAIRING_CONTRACT,
        "pair_count": len(pairs),
        "eligible_shadow_count": len(shadow),
        "official_outcome_count": len(official),
        "unpaired_shadow_count": len(unpaired_shadow),
        "pairs": pairs,
        "unpaired_shadow": unpaired_shadow,
        "rules": [
            "Pair selection is outcome-blind.",
            "Pairs require identical horizon, start reference, target time, and target observation.",
            "Each Shadow and Official outcome may be used at most once.",
            "Nearest issue time breaks ties among otherwise comparable rows.",
            "Realized returns are checked only after pairing as an integrity assertion.",
            "No aggregate winner, model promotion, threshold change, or portfolio authority is created.",
        ],
        "authority": {
            "research_only": True,
            "official_compass_override": False,
            "automatic_promotion": False,
            "portfolio_execution": False,
        },
    }


def _load_rows(root: Path, contract: str, repo_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not root.exists():
        return rows
    for path in sorted(root.rglob("*.json")):
        try:
            row = json.loads(path.read_text())
        except Exception:
            continue
        if not isinstance(row, dict) or row.get("contract") != contract:
            continue
        row = dict(row)
        row["source_path"] = path.relative_to(repo_root).as_posix()
        rows.append(row)
    return rows


def build_report(repo_root: Path) -> dict[str, Any]:
    official = _load_rows(repo_root / OFFICIAL_ROOT, OFFICIAL_CONTRACT, repo_root)
    shadow = _load_rows(repo_root / SHADOW_ROOT, SHADOW_CONTRACT, repo_root)
    return pair_outcomes(official, shadow)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = ap.parse_args()
    print(json.dumps(build_report(args.repo_root.resolve()), sort_keys=True))


if __name__ == "__main__":
    main()
