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


def _scoring_revision(row: dict[str, Any], *, shadow: bool) -> str | None:
    # Only exact owner contracts are eligible. A foreign "_v3" suffix is not proof.
    prefix = "SHADOW_COMPASS_V2_SCORING_v" if shadow else "OFFICIAL_DAILY_COMPASS_SCORING_v"
    for revision in ("2", "3"):
        if row.get("scoring_contract") == prefix + revision:
            return revision
    return None


def _v3_time_basis_valid(row: dict[str, Any], *, shadow: bool) -> bool:
    """Validate the outcome's recorded candle clock, not unproven source PIT."""
    if _scoring_revision(row, shadow=shadow) != "3":
        return False
    tb = row.get("time_basis")
    if not isinstance(tb, dict):
        return False
    if (
        tb.get("status") != "PASS"
        or tb.get("endpoint_semantics") != "HOURLY_CLOSE_TIME_NEAREST_TO_REFERENCE_PLUS_HORIZON"
        or tb.get("source_window_end_semantics") != "COLLECTION_BOUNDARY_NOT_CANDLE_CLOSE"
        or tb.get("source_first_knowledge_status") != "UNKNOWN_NOT_PROVEN_BY_BATCH_END"
    ):
        return False
    opened = parse_utc(row.get("target_observation_open_at_utc"))
    closed = parse_utc(row.get("target_observation_at_utc"))
    collected = parse_utc(row.get("target_source_window_end_utc"))
    matured = parse_utc(row.get("matured_at_utc"))
    reference = parse_utc(tb.get("start_reference_at_utc"))
    issued = parse_utc(row.get("issued_at_utc"))
    target = parse_utc(row.get("target_at_utc"))
    if None in (opened, closed, collected, matured, reference, issued, target):
        return False
    # An outcome can describe a nominal reference-based window without being
    # a prospective issued forecast. Keep its immutable row, but quarantine it
    # from comparison when the reference is future-dated or the target is due.
    if not reference <= issued < target:
        return False
    if opened.minute or opened.second or opened.microsecond:
        return False
    if (closed - opened).total_seconds() != 3600:
        return False
    if collected < closed or collected > matured or matured < target:
        return False
    horizon_hours = {"12h": 12, "72h": 72, "168h": 168}.get(row.get("horizon"))
    if horizon_hours is None:
        return False
    if abs((target - reference).total_seconds() / 3600 - horizon_hours) > 1e-6:
        return False
    effective = (closed - reference).total_seconds() / 3600
    deviation = abs(effective - horizon_hours)
    if deviation > 1.0:
        return False
    for key, expected in (
        ("nominal_horizon_hours", horizon_hours),
        ("effective_window_hours", effective),
        ("window_deviation_hours", deviation),
    ):
        value = tb.get(key)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False
        if not math.isfinite(value) or not math.isclose(value, expected, rel_tol=0, abs_tol=1e-5):
            return False
    return True


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
    quarantined_candidates: list[dict[str, Any]] = []
    for si, srow in enumerate(shadow):
        s_issue = parse_utc(srow.get("issued_at_utc"))
        if s_issue is None or any(value in (None, "") for value in _pair_key(srow)):
            continue
        for oi, orow in enumerate(official):
            o_issue = parse_utc(orow.get("issued_at_utc"))
            if o_issue is None or _pair_key(srow) != _pair_key(orow):
                continue
            revision = _scoring_revision(srow, shadow=True)
            if revision is None or revision != _scoring_revision(orow, shadow=False):
                continue  # Fail closed across incompatible/unknown scoring versions.
            if revision == "3" and not (
                _v3_time_basis_valid(srow, shadow=True)
                and _v3_time_basis_valid(orow, shadow=False)
            ):
                # Exclude invalid clocks BEFORE greedy matching. Otherwise a
                # malformed nearest candidate steals the only valid slot.
                quarantined_candidates.append({
                    "shadow_forecast_id": _row_id(srow, True),
                    "official_compass_id": _row_id(orow, False),
                    "horizon": srow.get("horizon"),
                    "reason": "V3_TIME_BASIS_INVALID_PRE_SELECTION",
                    "selection_used_outcome_correctness": False,
                    "selection_used_realized_return": False,
                })
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
        clock_validated = _v3_time_basis_valid(srow, shadow=True) and _v3_time_basis_valid(orow, shadow=False)
        asset_comparisons: dict[str, Any] = {}
        for asset in ("btc", "eth"):
            s_acc = ((srow.get("direction_accuracy") or {}).get(asset) or {})
            o_acc = ((orow.get("direction_accuracy") or {}).get(asset) or {})
            s_result, o_result = s_acc.get("result"), o_acc.get("result")
            asset_comparisons[asset] = {
                "shadow_result": s_result,
                "official_result": o_result,
                "comparison_state": (
                    "PAIR_INTEGRITY_FAIL"
                    if not realized_match
                    else "PAIR_TIME_BASIS_UNVERIFIED" if not clock_validated
                    else _result_category(s_result, o_result)
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
                    "status": "FAIL" if not realized_match else ("PASS" if clock_validated else "LEGACY_TIME_BASIS_UNVERIFIED"),
                    "scoring_revision": _scoring_revision(srow, shadow=True),
                    "candle_close_semantics_v3": clock_validated,
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

    # Existing CI and consumers require every published pair to be fully
    # admitted. Preserve legacy/mismatched evidence separately, not as PASS.
    quarantined_pairs = [pair for pair in pairs if pair["integrity"]["status"] != "PASS"]
    admitted_pairs = [pair for pair in pairs if pair["integrity"]["status"] == "PASS"]
    return {
        "contract": REPORT_CONTRACT,
        "pairing_contract": PAIRING_CONTRACT,
        "pair_count": len(admitted_pairs),
        "quarantined_pair_count": len(quarantined_pairs),
        "quarantined_pairs": quarantined_pairs,
        "quarantined_candidate_count": len(quarantined_candidates),
        "quarantined_candidates": quarantined_candidates,
        "eligible_shadow_count": len(shadow),
        "official_outcome_count": len(official),
        "unpaired_shadow_count": len(unpaired_shadow),
        "pairs": admitted_pairs,
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
