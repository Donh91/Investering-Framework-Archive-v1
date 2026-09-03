from __future__ import annotations

import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any

from forecast_study_common_v1_3_2 import (
    ALPHA, BLOCK_DAYS, STUDY_ID, parse_dt, verify_self_hash, with_self_hash,
)

def _betainc(a: float, b: float, x: float) -> float:
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    front = math.exp(math.log(x) * a + math.log1p(-x) * b - lbeta) / a
    f, c, d = 1.0, 1.0, 0.0
    for i in range(300):
        m = i // 2
        if i == 0:
            num = 1.0
        elif i % 2 == 0:
            num = (m * (b - m) * x) / ((a + 2 * m - 1) * (a + 2 * m))
        else:
            num = -((a + m) * (a + b + m) * x) / ((a + 2 * m) * (a + 2 * m + 1))
        d = 1.0 + num * d
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        c = 1.0 + num / c
        if abs(c) < 1e-30:
            c = 1e-30
        f *= c * d
        if abs(1.0 - c * d) < 1e-13:
            break
    return front * (f - 1.0)


def t_cdf(x: float, nu: float) -> float:
    ib = _betainc(nu / 2.0, 0.5, nu / (nu + x * x))
    return 1.0 - 0.5 * ib if x > 0 else 0.5 * ib


def t_ppf(p: float, nu: float) -> float:
    lo, hi = -60.0, 60.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, nu) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def accrual_gates(admissions: list[dict[str, Any]]) -> tuple[dict[str, bool], dict[str, Any] | None]:
    n_rows = len(admissions)
    if not n_rows:
        return {}, None
    due_counts = Counter(row["outcome_due_day_utc"] for row in admissions)
    freeze_counts = Counter(row["freeze_day_utc"] for row in admissions)
    first_due = min(parse_dt(row["outcome_due_utc"]).date() for row in admissions)
    block_counts = Counter(
        (parse_dt(row["outcome_due_utc"]).date() - first_due).days // BLOCK_DAYS
        for row in admissions
    )
    gates = {
        "min_admitted_F1_rows": n_rows >= 200,
        "min_UNIQUE_OUTCOME_DUE_DAYS": len(due_counts) >= 85,
        "min_UNIQUE_FREEZE_DAYS": len(freeze_counts) >= 50,
        "max_share_rows_on_any_OUTCOME_DUE_calendar_day": max(due_counts.values()) / n_rows <= 0.06,
        "max_share_rows_in_any_28_calendar_day_block": max(block_counts.values()) / n_rows <= 0.23,
    }
    return gates, {
        "N": n_rows,
        "due_counts": due_counts,
        "freeze_counts": freeze_counts,
        "block_counts": block_counts,
        "first_due": first_due,
    }


def confirmatory_readiness(
    admissions: list[dict[str, Any]],
    revalidations: dict[str, dict[str, Any]],
    activation: dict[str, Any],
    now_utc: str,
) -> dict[str, Any]:
    now = parse_dt(now_utc)
    cohort_end = parse_dt(str(activation["cohort_end_utc_exclusive"]))
    base = {"contract": "FORECAST_SKILL_CONFIRMATORY_READINESS_v1_3_2", "outcome_data_read": False}
    if now < cohort_end:
        return {**base, "status": "ACCRUING"}
    if not admissions:
        return {**base, "status": "INSUFFICIENT_PROSPECTIVE_EVIDENCE", "reason": "NO_ADMISSIONS"}
    for row in admissions:
        verify_self_hash(row, "admission_sha256")
    if any(now < parse_dt(row["outcome_due_utc"]) for row in admissions):
        return {**base, "status": "WAITING_FOR_DUE_TIMES"}
    if any(row["forecast_id"] not in revalidations for row in admissions):
        return {**base, "status": "WAITING_FOR_TECHNICAL_REVALIDATION"}
    for row in admissions:
        revalidation = revalidations[row["forecast_id"]]
        verify_self_hash(revalidation, "revalidation_sha256")
        if revalidation.get("status") != "PASS" or revalidation.get("outcome_data_read") is not False:
            return {
                **base,
                "status": "INSUFFICIENT_PROSPECTIVE_EVIDENCE",
                "reason": "TECHNICAL_REVALIDATION_FAILURE",
            }
    gates, _meta = accrual_gates(admissions)
    if not all(gates.values()):
        return {
            **base,
            "status": "INSUFFICIENT_PROSPECTIVE_EVIDENCE",
            "reason": "ACCRUAL_OR_CONCENTRATION_GATE",
            "gates": gates,
        }
    max_due = max(parse_dt(row["outcome_due_utc"]) for row in admissions)
    if now < max_due + timedelta(hours=24):
        return {**base, "status": "WAITING_FOR_SETTLEMENT_PUBLICATION_GRACE", "gates": gates}
    return {**base, "status": "READY_FOR_SINGLE_OUTCOME_READ", "gates": gates}


def confirmatory(
    admissions: list[dict[str, Any]],
    revalidations: dict[str, dict[str, Any]],
    outcomes: dict[str, dict[str, Any]],
    activation: dict[str, Any],
    now_utc: str,
) -> dict[str, Any]:
    base = {
        "contract": "FORECAST_SKILL_CONFIRMATORY_RESULT_v1_3_2",
        "study_id": STUDY_ID,
        "forecast_skill_status": "UNPROVEN",
        "authority": {
            "portfolio_action": False,
            "model_weight_change": False,
            "automatic_promotion": False,
        },
    }
    ready = confirmatory_readiness(admissions, revalidations, activation, now_utc)
    if ready["status"] != "READY_FOR_SINGLE_OUTCOME_READ":
        return {**base, **{key: value for key, value in ready.items() if key != "contract"}}

    rows: list[dict[str, Any]] = []
    for admission in admissions:
        outcome = outcomes.get(admission["forecast_id"])
        if (
            not outcome
            or outcome.get("contract") != "MATURED_OUTCOME_v3"
            or outcome.get("status") != "MATURED"
            or outcome.get("scientific_score_eligible") is not True
        ):
            return {
                **base,
                "status": "INSUFFICIENT_PROSPECTIVE_EVIDENCE",
                "reason": "OUTCOME_UNAVAILABLE",
                "outcome_data_read": True,
                "confirmatory_test_executed": False,
                "max_OUTCOME_UNAVAILABLE_share_gate": False,
            }
        if outcome.get("forecast_sha256") != admission.get("forecast_sha256"):
            return {
                **base,
                "status": "INSUFFICIENT_PROSPECTIVE_EVIDENCE",
                "reason": "OUTCOME_FORECAST_BINDING_MISMATCH",
                "outcome_data_read": True,
                "confirmatory_test_executed": False,
            }
        if outcome.get("result") == "HIT":
            hit = 1.0
        elif outcome.get("result") == "MISS":
            hit = 0.0
        else:
            return {
                **base,
                "status": "INSUFFICIENT_PROSPECTIVE_EVIDENCE",
                "reason": "OUTCOME_RESULT_INVALID",
                "outcome_data_read": True,
                "confirmatory_test_executed": False,
            }
        rows.append({**admission, "d": hit - float(admission["p_clim"])})

    gates, meta = accrual_gates(admissions)
    assert meta is not None
    by_day: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_day[row["outcome_due_day_utc"]].append(float(row["d"]))
    days = sorted(by_day)
    daily_mean = {day: sum(by_day[day]) / len(by_day[day]) for day in days}
    origin = datetime.fromisoformat(days[0]).date()
    block_sum: dict[int, float] = defaultdict(float)
    block_days: dict[int, int] = defaultdict(int)
    for day in days:
        block = (datetime.fromisoformat(day).date() - origin).days // BLOCK_DAYS
        block_sum[block] += daily_mean[day]
        block_days[block] += 1
    live = sorted(block for block, count in block_days.items() if count > 0)
    G = len(live)
    observed_days = sum(block_days[block] for block in live)
    theta = sum(block_sum[block] for block in live) / observed_days
    if G < 2:
        return {
            **base,
            "status": "INSUFFICIENT_PROSPECTIVE_EVIDENCE",
            "reason": "INSUFFICIENT_OCCUPIED_BLOCKS",
            "outcome_data_read": True,
            "confirmatory_test_executed": False,
        }
    variance = (G / (G - 1.0)) * sum(
        (block_sum[block] - theta * block_days[block]) ** 2 for block in live
    ) / (observed_days**2)
    standard_error = math.sqrt(variance)
    if not (math.isfinite(standard_error) and standard_error > 0):
        return {
            **base,
            "status": "INSUFFICIENT_PROSPECTIVE_EVIDENCE",
            "reason": "NONPOSITIVE_STANDARD_ERROR",
            "outcome_data_read": True,
            "confirmatory_test_executed": False,
        }
    statistic = theta / standard_error
    critical = t_ppf(1.0 - ALPHA, G - 1)
    p_value = 1.0 - t_cdf(statistic, G - 1)
    reject = statistic > critical
    verdict = "WEAK_PROSPECTIVE_EDGE" if reject else "ADEQUATE_SAMPLE_NO_DEMONSTRATED_EDGE"
    result = {
        **base,
        "status": verdict,
        "confirmatory_verdict": verdict,
        "forecast_skill_status": "UNPROVEN",
        "outcome_data_read": True,
        "confirmatory_test_executed": True,
        "test_count": 1,
        "N_rows": meta["N"],
        "unique_due_days": len(meta["due_counts"]),
        "unique_freeze_days": len(meta["freeze_counts"]),
        "G": G,
        "theta_hat": theta,
        "standard_error": standard_error,
        "t_statistic": statistic,
        "critical_value": critical,
        "p_value_one_sided": p_value,
        "df": G - 1,
        "alpha_one_sided": ALPHA,
        "reject_null": reject,
        "gates": {**gates, "max_OUTCOME_UNAVAILABLE_share": True},
        "endpoint_weighting": "EACH_OBSERVED_OUTCOME_DUE_CALENDAR_DAY_EQUAL_WEIGHT",
        "calendar_block_length_days": BLOCK_DAYS,
    }
    return with_self_hash(result, "result_sha256")
