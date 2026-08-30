#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

BREADTH = Path("03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json")
PREDICTIONS = Path("04_MARKET_LEARNING/intraday_execution/direction_predictions")
OUTCOMES = Path("04_MARKET_LEARNING/intraday_execution/direction_outcomes")
CALIBRATION = Path("04_MARKET_LEARNING/intraday_execution/DIRECTION_CALIBRATION.json")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def parse_utc(value: str) -> datetime:
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result.astimezone(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _direction(value: float | None, neutral: float = 0.0) -> str:
    if value is None:
        return "MISSING"
    if value > neutral:
        return "UP"
    if value < neutral:
        return "DOWN"
    return "FLAT"


def _vote(name: str, value: float | None, neutral: float = 0.0) -> dict[str, Any]:
    return {"family": name, "direction": _direction(value, neutral), "value": value}


def build_votes(target: str, obs: dict[str, Any]) -> list[dict[str, Any]]:
    asset = obs[target.lower()]
    votes = [
        _vote("return_1h", asset.get("return_1h_pct")),
        _vote("return_4h", asset.get("return_4h_pct")),
        _vote("session_vwap", asset.get("vwap_deviation_pct")),
        _vote("momentum_acceleration", asset.get("momentum_acceleration_1h_vs_prior3h_pp")),
        _vote("taker_balance", asset.get("taker_buy_quote_share"), 0.5),
        _vote("taker_change", asset.get("taker_buy_share_delta_vs_prior3h")),
    ]
    if target == "ETH":
        votes.extend(
            [
                _vote("ethbtc_1h", (obs.get("ethbtc") or {}).get("return_1h_pct")),
                _vote("breadth_balance", (obs.get("breadth") or {}).get("advance_ratio"), 0.5),
            ]
        )
    return votes


def summarize_votes(votes: list[dict[str, Any]], cfg: dict[str, Any]) -> dict[str, Any]:
    eligible = [v for v in votes if v["direction"] in {"UP", "DOWN"}]
    up = sum(v["direction"] == "UP" for v in eligible)
    down = sum(v["direction"] == "DOWN" for v in eligible)
    available = len(eligible)
    winner = max(up, down)
    agreement = (winner / available) if available else None
    minimum = int(cfg.get("minimum_direction_families", 4))
    minimum_margin = int(cfg.get("minimum_vote_margin", 2))
    if available < minimum or abs(up - down) < minimum_margin or up == down:
        direction = "NO_EDGE"
    else:
        direction = "UP" if up > down else "DOWN"
    key = f"{winner}_of_{available}" if available else "0_of_0"
    return {
        "direction": direction,
        "evidence_agreement": agreement,
        "evidence_agreement_pct": round(agreement * 100.0, 2) if agreement is not None else None,
        "up_votes": up,
        "down_votes": down,
        "available_directional_families": available,
        "calibration_key": key,
        "votes": votes,
    }


def _tier_row(rows: list[dict[str, Any]], low_rank: int, high_rank: int) -> dict[str, Any]:
    selected = [
        row
        for row in rows
        if isinstance(row.get("filtered_rank"), int)
        and low_rank <= int(row["filtered_rank"]) <= high_rank
        and isinstance(row.get("change_24h_pct"), (int, float))
    ]
    changes = [float(row["change_24h_pct"]) for row in selected]
    if not changes:
        return {
            "direction": "NO_EDGE",
            "constituent_count": 0,
            "advance_ratio": None,
            "median_return_24h_pct": None,
            "evidence_class": "DATA_UNAVAILABLE",
        }
    advance_ratio = sum(value > 0 for value in changes) / len(changes)
    med = statistics.median(changes)
    if advance_ratio > 0.5 and med > 0:
        direction = "UP"
    elif advance_ratio < 0.5 and med < 0:
        direction = "DOWN"
    else:
        direction = "NO_EDGE"
    return {
        "direction": direction,
        "constituent_count": len(changes),
        "advance_ratio": round(advance_ratio, 6),
        "median_return_24h_pct": round(med, 6),
        "evidence_class": "TOP100_RANK_SEGMENT_PROXY_ONLY",
    }


def build_market_cap_transmission() -> dict[str, Any]:
    breadth = read_json(BREADTH) or {}
    rows = breadth.get("constituents") if isinstance(breadth.get("constituents"), list) else []
    return {
        "large_cap_proxy": {
            **_tier_row(rows, 3, 25),
            "rank_segment": "filtered_rank_3_25",
        },
        "mid_cap_proxy": {
            **_tier_row(rows, 26, 50),
            "rank_segment": "filtered_rank_26_50",
        },
        "small_cap_proxy": {
            **_tier_row(rows, 51, 100),
            "rank_segment": "filtered_rank_51_100",
        },
        "microcap": {
            "direction": "NO_EDGE",
            "evidence_class": "DATA_UNAVAILABLE",
            "reason": "CURRENT_BREADTH_OWNER_STOPS_AT_TOP100",
            "calibrated_probability": None,
        },
        "warning": "Rank segments are transmission proxies, not canonical market-cap bands.",
    }


def _prediction_paths():
    return sorted(PREDICTIONS.rglob("*.json")) if PREDICTIONS.exists() else []


def _outcome_paths():
    return sorted(OUTCOMES.rglob("*.json")) if OUTCOMES.exists() else []


def _wilson_lower(hits: int, total: int, z: float = 1.959963984540054) -> float | None:
    if total <= 0:
        return None
    p = hits / total
    den = 1 + z * z / total
    center = p + z * z / (2 * total)
    radius = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total)
    return max(0.0, (center - radius) / den)


def _independent_rows(rows: list[dict[str, Any]], horizon_hours: int) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    last: datetime | None = None
    for row in sorted(rows, key=lambda item: item["issued_at_utc"]):
        issued = parse_utc(row["issued_at_utc"])
        if last is None or issued - last >= timedelta(hours=horizon_hours):
            chosen.append(row)
            last = issued
    return chosen


def build_calibration_summary(cfg: dict[str, Any], now: datetime) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    for path in _outcome_paths():
        row = read_json(path)
        if not row or row.get("contract") != "INTRADAY_DIRECTION_OUTCOME_v1":
            continue
        if row.get("status") != "MATURED" or row.get("result") not in {"HIT", "MISS"}:
            continue
        scored.append(row)

    grouped: dict[str, list[dict[str, Any]]] = {}
    family_rows: dict[str, dict[str, int]] = {}
    for row in scored:
        group_id = row["calibration_group"]
        grouped.setdefault(group_id, []).append(row)
        actual = row.get("actual_direction")
        for vote in row.get("votes", []):
            family = vote.get("family")
            vote_dir = vote.get("direction")
            if not family or vote_dir not in {"UP", "DOWN"} or actual not in {"UP", "DOWN"}:
                continue
            bucket = family_rows.setdefault(f"{row['target']}:{row['horizon_hours']}H:{family}", {"hit": 0, "miss": 0})
            bucket["hit" if vote_dir == actual else "miss"] += 1

    groups: dict[str, Any] = {}
    min_samples = int(cfg.get("minimum_independent_calibration_samples", 20))
    strong_samples = int(cfg.get("strong_calibration_samples", 50))
    assurance_samples = int(cfg.get("high_assurance_minimum_independent_samples", 300))
    for group_id, rows in grouped.items():
        horizon = int(rows[0]["horizon_hours"])
        independent = _independent_rows(rows, horizon)
        hits = sum(row["result"] == "HIT" for row in independent)
        total = len(independent)
        raw_rate = hits / total if total else None
        estimate = (hits + 1) / (total + 2) if total else None
        wilson = _wilson_lower(hits, total)
        briers = [row.get("brier_score") for row in independent if isinstance(row.get("brier_score"), (int, float))]
        if total < min_samples:
            maturity = "WARMUP"
            display_probability = None
        elif total < strong_samples:
            maturity = "EARLY_CALIBRATION"
            display_probability = estimate
        elif total < assurance_samples:
            maturity = "CALIBRATED"
            display_probability = estimate
        else:
            eligible_99 = (
                estimate is not None
                and estimate >= 0.99
                and wilson is not None
                and wilson >= float(cfg.get("high_assurance_wilson_floor", 0.97))
            )
            maturity = "HIGH_ASSURANCE_99_ELIGIBLE" if eligible_99 else "CALIBRATED_STRONG"
            display_probability = estimate
        groups[group_id] = {
            "total_scored_rows": len(rows),
            "independent_count": total,
            "hits": hits,
            "misses": total - hits,
            "empirical_hit_rate": round(raw_rate, 6) if raw_rate is not None else None,
            "laplace_calibrated_estimate": round(estimate, 6) if estimate is not None else None,
            "wilson_lower_95": round(wilson, 6) if wilson is not None else None,
            "mean_brier_score": round(statistics.fmean(briers), 6) if briers else None,
            "maturity": maturity,
            "display_probability": round(display_probability, 6) if display_probability is not None else None,
            "overlap_control": f"GREEDY_NON_OVERLAP_{horizon}H",
        }

    family_reliability = {}
    for key, counts in family_rows.items():
        total = counts["hit"] + counts["miss"]
        family_reliability[key] = {
            **counts,
            "count": total,
            "hit_rate": round(counts["hit"] / total, 6) if total else None,
            "authority": "DIAGNOSTIC_ONLY_NO_AUTOMATIC_REWEIGHTING",
        }

    summary = {
        "contract": "INTRADAY_DIRECTION_CALIBRATION_v1",
        "generated_at_utc": iso(now),
        "scored_outcome_count": len(scored),
        "groups": groups,
        "family_reliability": family_reliability,
        "governance": {
            "shadow_only": True,
            "automatic_signal_reweighting": False,
            "canonical_market_state": False,
            "portfolio_execution": False,
        },
    }
    write_json(CALIBRATION, summary)
    return summary


def _group_id(target: str, horizon: int, direction: str, calibration_key: str) -> str:
    return f"{target}:{horizon}H:{direction}:{calibration_key}"


def _calibration_view(summary: dict[str, Any], target: str, horizon: int, vote_summary: dict[str, Any]) -> dict[str, Any]:
    direction = vote_summary["direction"]
    if direction == "NO_EDGE":
        return {
            "confidence_status": "ABSTAIN_NO_EDGE",
            "calibrated_probability": None,
            "independent_calibration_samples": 0,
        }
    group_id = _group_id(target, horizon, direction, vote_summary["calibration_key"])
    group = (summary.get("groups") or {}).get(group_id) or {}
    p = group.get("display_probability")
    return {
        "confidence_status": group.get("maturity", "WARMUP"),
        "calibrated_probability": round(float(p) * 100.0, 1) if isinstance(p, (int, float)) else None,
        "independent_calibration_samples": int(group.get("independent_count", 0)),
        "calibration_group": group_id,
        "wilson_lower_95_pct": round(float(group["wilson_lower_95"]) * 100.0, 1)
        if isinstance(group.get("wilson_lower_95"), (int, float))
        else None,
    }


def _prediction_path(issued_at: datetime) -> Path:
    return PREDICTIONS / f"{issued_at:%Y/%m/%d}/{issued_at:%Y%m%dT%H%M%SZ}.json"


def write_prediction(
    obs: dict[str, Any],
    cfg: dict[str, Any],
    now: datetime,
    vote_summaries: dict[str, dict[str, Any]],
    calibration: dict[str, Any],
) -> tuple[str, str | None]:
    observed_at = parse_utc(obs["price_observation_utc"])
    lag_minutes = (now - observed_at).total_seconds() / 60.0
    max_lag = float(cfg.get("max_prediction_issue_lag_minutes", 90))
    if lag_minutes < 0 or lag_minutes > max_lag:
        return "STALE_INPUT_NO_PREDICTION", None
    path = _prediction_path(now)
    if path.exists():
        return "DUPLICATE_NOOP", str(path)

    horizons = {}
    for horizon in [int(x) for x in cfg.get("direction_horizons_hours", [1, 4, 24])]:
        targets = {}
        for target in ("BTC", "ETH"):
            summary = vote_summaries[target]
            cal = _calibration_view(calibration, target, horizon, summary)
            targets[target] = {
                "direction": summary["direction"],
                "start_value": obs[target.lower()].get("close"),
                "evidence_agreement_pct": summary["evidence_agreement_pct"],
                "calibration_key": summary["calibration_key"],
                "votes": summary["votes"],
                "frozen_calibrated_probability_pct": cal["calibrated_probability"],
                "confidence_status_at_issue": cal["confidence_status"],
            }
        horizons[f"{horizon}H"] = {
            "horizon_hours": horizon,
            "due_at_utc": iso(now + timedelta(hours=horizon)),
            "targets": targets,
        }

    prediction = {
        "contract": "INTRADAY_DIRECTION_PREDICTION_v1",
        "issued_at_utc": iso(now),
        "source_price_observation_utc": iso(observed_at),
        "source_lag_minutes": round(lag_minutes, 3),
        "hourly_sequence_run_id": obs.get("hourly_sequence_run_id"),
        "horizons": horizons,
        "authority": {
            "shadow_only": True,
            "candidate_is_portfolio_action": False,
            "canonical_market_state": False,
            "automatic_rule_changes": False,
        },
    }
    write_json(path, prediction)
    return "PREDICTION_FROZEN", str(path)


def mature_predictions(obs: dict[str, Any], cfg: dict[str, Any], now: datetime) -> dict[str, int]:
    current_obs_time = parse_utc(obs["price_observation_utc"])
    counts = {"matured": 0, "censored": 0, "abstained": 0, "pending": 0}
    max_lag = float(cfg.get("max_outcome_evidence_lag_hours", 1.5))
    for path in _prediction_paths():
        pred = read_json(path)
        if not pred or pred.get("contract") != "INTRADAY_DIRECTION_PREDICTION_v1":
            continue
        issued = parse_utc(pred["issued_at_utc"])
        for horizon_key, horizon_row in (pred.get("horizons") or {}).items():
            horizon = int(horizon_row["horizon_hours"])
            due = parse_utc(horizon_row["due_at_utc"])
            for target, target_row in (horizon_row.get("targets") or {}).items():
                outcome_path = OUTCOMES / f"{issued:%Y/%m/%d}/{issued:%Y%m%dT%H%M%SZ}_{horizon_key}_{target}.json"
                if outcome_path.exists():
                    continue
                if now < due or current_obs_time < due:
                    counts["pending"] += 1
                    continue
                lag_hours = (current_obs_time - due).total_seconds() / 3600.0
                predicted = target_row.get("direction")
                group_id = _group_id(target, horizon, predicted, target_row.get("calibration_key"))
                common = {
                    "contract": "INTRADAY_DIRECTION_OUTCOME_v1",
                    "issued_at_utc": pred["issued_at_utc"],
                    "due_at_utc": horizon_row["due_at_utc"],
                    "measured_at_utc": iso(now),
                    "evidence_observation_utc": iso(current_obs_time),
                    "evidence_lag_hours": round(lag_hours, 6),
                    "target": target,
                    "horizon_hours": horizon,
                    "predicted_direction": predicted,
                    "calibration_key": target_row.get("calibration_key"),
                    "calibration_group": group_id,
                    "votes": target_row.get("votes", []),
                    "frozen_calibrated_probability_pct": target_row.get("frozen_calibrated_probability_pct"),
                    "authority": {
                        "shadow_only": True,
                        "automatic_rule_changes": False,
                        "portfolio_execution": False,
                    },
                }
                if lag_hours < -1e-9 or lag_hours > max_lag:
                    write_json(
                        outcome_path,
                        {
                            **common,
                            "status": "CENSORED",
                            "reason": "OUTCOME_EVIDENCE_LAG_OUTSIDE_FROZEN_WINDOW",
                        },
                    )
                    counts["censored"] += 1
                    continue
                start = target_row.get("start_value")
                end = (obs.get(target.lower()) or {}).get("close")
                if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or float(start) == 0:
                    write_json(outcome_path, {**common, "status": "CENSORED", "reason": "PRICE_EVIDENCE_MISSING"})
                    counts["censored"] += 1
                    continue
                ret = (float(end) / float(start) - 1.0) * 100.0
                actual = "UP" if ret > 0 else ("DOWN" if ret < 0 else "FLAT")
                if predicted == "NO_EDGE":
                    result = "ABSTAINED"
                    brier = None
                    counts["abstained"] += 1
                else:
                    result = "HIT" if actual == predicted else "MISS"
                    p_pct = target_row.get("frozen_calibrated_probability_pct")
                    p = float(p_pct) / 100.0 if isinstance(p_pct, (int, float)) else None
                    brier = (p - (1.0 if result == "HIT" else 0.0)) ** 2 if p is not None else None
                    counts["matured"] += 1
                aligned = [
                    vote["family"]
                    for vote in target_row.get("votes", [])
                    if vote.get("direction") == actual and actual in {"UP", "DOWN"}
                ]
                opposed = [
                    vote["family"]
                    for vote in target_row.get("votes", [])
                    if vote.get("direction") in {"UP", "DOWN"} and vote.get("direction") != actual
                ]
                write_json(
                    outcome_path,
                    {
                        **common,
                        "status": "MATURED",
                        "result": result,
                        "start_value": start,
                        "end_value": end,
                        "return_pct": round(ret, 8),
                        "actual_direction": actual,
                        "brier_score": round(brier, 8) if brier is not None else None,
                        "miss_analysis": {
                            "families_aligned_with_actual": aligned,
                            "families_opposed_to_actual": opposed,
                        },
                    },
                )
    return counts


def update_shadow_direction_confidence(
    obs: dict[str, Any],
    cfg: dict[str, Any],
    now: datetime,
    *,
    new_prediction: bool,
) -> dict[str, Any]:
    direction_cfg = cfg.get("shadow_direction_confidence") or {}
    maturity = mature_predictions(obs, direction_cfg, now)
    calibration = build_calibration_summary(direction_cfg, now)
    vote_summaries = {target: summarize_votes(build_votes(target, obs), direction_cfg) for target in ("BTC", "ETH")}

    horizons = {}
    for horizon in [int(x) for x in direction_cfg.get("direction_horizons_hours", [1, 4, 24])]:
        targets = {}
        for target in ("BTC", "ETH"):
            base = vote_summaries[target]
            targets[target] = {
                "direction": base["direction"],
                "evidence_agreement_pct": base["evidence_agreement_pct"],
                "up_votes": base["up_votes"],
                "down_votes": base["down_votes"],
                **_calibration_view(calibration, target, horizon, base),
            }
        horizons[f"{horizon}H"] = {"horizon_hours": horizon, "targets": targets}

    prediction_status = "DUPLICATE_PRICE_OBSERVATION_NO_NEW_PREDICTION"
    prediction_path = None
    if new_prediction:
        prediction_status, prediction_path = write_prediction(
            obs, direction_cfg, now, vote_summaries, calibration
        )

    tier = build_market_cap_transmission()
    one_hour = horizons.get("1H", {}).get("targets", {})
    btc = one_hour.get("BTC", {})
    eth = one_hour.get("ETH", {})
    display = (
        "SHADOW DIRECTION: "
        f"BTC {btc.get('direction')} "
        f"({btc.get('calibrated_probability') if btc.get('calibrated_probability') is not None else 'UNCALIBRATED'}"
        f", n={btc.get('independent_calibration_samples', 0)}) | "
        f"ETH {eth.get('direction')} "
        f"({eth.get('calibrated_probability') if eth.get('calibrated_probability') is not None else 'UNCALIBRATED'}"
        f", n={eth.get('independent_calibration_samples', 0)}) | "
        f"Large {tier['large_cap_proxy']['direction']} | Mid {tier['mid_cap_proxy']['direction']} | "
        f"Small {tier['small_cap_proxy']['direction']} | Micro NO_EDGE(DATA_GAP)"
    )
    return {
        "contract": "SHADOW_DIRECTION_CONFIDENCE_v1",
        "generated_at_utc": iso(now),
        "status": "SHADOW_ONLY",
        "horizons": horizons,
        "market_cap_transmission": tier,
        "prediction_freeze": {
            "status": prediction_status,
            "path": prediction_path,
        },
        "outcome_maturation": maturity,
        "calibration": {
            "contract": calibration["contract"],
            "scored_outcome_count": calibration["scored_outcome_count"],
            "path": str(CALIBRATION),
            "automatic_signal_reweighting": False,
        },
        "data_ping_bridge": {"display_line": display},
        "authority": {
            "shadow_only": True,
            "canonical_market_state": False,
            "portfolio_execution": False,
            "automatic_rule_changes": False,
            "probability_must_be_empirically_calibrated": True,
        },
    }
