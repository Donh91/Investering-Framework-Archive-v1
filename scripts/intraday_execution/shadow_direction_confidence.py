#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import os
import statistics
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

BREADTH = Path("03_DAILY_CAPTURE_LOGS/breadth_rich/LATEST.json")
HOURLY_ROOT = Path("03_DAILY_CAPTURE_LOGS/hourly")
PREDICTIONS = Path("04_MARKET_LEARNING/intraday_execution/direction_predictions")
OUTCOMES = Path("04_MARKET_LEARNING/intraday_execution/direction_outcomes")
CALIBRATION = Path("04_MARKET_LEARNING/intraday_execution/DIRECTION_CALIBRATION.json")
REGISTRATION = Path("04_MARKET_LEARNING/intraday_execution/DIRECTION_REGISTRATION.json")
TEST_ID = "INTRADAY_DIRECTION_CONFIDENCE_V1"
REPOSITORY = "Donh91/Investering-Framework-Archive-v1"


def content_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def production_context() -> dict[str, Any] | None:
    """Only the existing canonical-main Actions writer can create forward rows."""
    if (
        os.environ.get("GITHUB_ACTIONS") != "true"
        or os.environ.get("GITHUB_REPOSITORY") != REPOSITORY
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
        or os.environ.get("GITHUB_EVENT_NAME") not in {"schedule", "workflow_dispatch"}
        or not os.environ.get("GITHUB_RUN_ID", "").isdigit()
    ):
        return None
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    subprocess.run(["git", "merge-base", "--is-ancestor", head, "origin/main"], check=True)
    return {
        "repository": REPOSITORY,
        "ref": "refs/heads/main",
        "event": os.environ["GITHUB_EVENT_NAME"],
        "run_id": os.environ["GITHUB_RUN_ID"],
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "1"),
        "commit_sha": head,
    }


def ensure_registration(cfg: dict[str, Any], now: datetime, context: dict[str, Any] | None) -> dict[str, Any] | None:
    if not context:
        return None
    if REGISTRATION.exists():
        return read_json(REGISTRATION)
    if _prediction_paths() or _outcome_paths():
        raise RuntimeError("REGISTRATION_CANNOT_ADOPT_PREEXISTING_ROWS")
    try:
        from scripts.intraday_execution.validate_direction_confidence import registry_binding_hash
    except ModuleNotFoundError:
        from validate_direction_confidence import registry_binding_hash
    receipt = {
        "contract": "INTRADAY_DIRECTION_REGISTRATION_v1",
        "registered_test_id": TEST_ID,
        "registered_at_utc": iso(now),
        "production_context": context,
        "registry_binding_sha256": registry_binding_hash(Path(".")),
        "configuration_sha256": content_hash(cfg),
        "forward_eligibility": "POST_REGISTRATION_CANONICAL_MAIN_ONLY",
        "prior_rows_adopted": 0,
    }
    receipt["receipt_sha256"] = content_hash(receipt)
    write_json(REGISTRATION, receipt)
    return receipt


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def parse_utc(value: str) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _source_price_observation_time(obs: dict[str, Any]) -> datetime:
    """Return when the source close used by the forecast was actually observable.

    The canonical hourly owner labels each closed 1H row with the candle *open*
    timestamp. Its close is only knowable one hour later. Keep the legacy
    intraday `price_observation_utc` field unchanged for the existing research
    owner, but shift it by one hour for shadow forecasting whenever the snapshot
    is bound to the hourly-sequence owner. An explicit close timestamp takes
    precedence for future-compatible callers.
    """
    explicit = obs.get("price_close_observation_utc")
    if explicit:
        return parse_utc(str(explicit))
    base = parse_utc(str(obs["price_observation_utc"]))
    if obs.get("hourly_sequence_run_id"):
        return base + timedelta(hours=1)
    return base


def _direction(value: float | None, neutral: float = 0.0) -> str:
    if not finite_number(value):
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
    agreement = winner / available if available else None
    minimum = int(cfg.get("minimum_direction_families", 4))
    margin = int(cfg.get("minimum_vote_margin", 2))
    if available < minimum or up == down or abs(up - down) < margin:
        direction = "NO_EDGE"
    else:
        direction = "UP" if up > down else "DOWN"
    return {
        "direction": direction,
        "evidence_agreement": agreement,
        "evidence_agreement_pct": round(agreement * 100.0, 2) if agreement is not None else None,
        "up_votes": up,
        "down_votes": down,
        "available_directional_families": available,
        "calibration_key": f"{winner}_of_{available}" if available else "0_of_0",
        "votes": votes,
    }


def _tier_row(rows: list[dict[str, Any]], low: int, high: int) -> dict[str, Any]:
    selected = [
        row
        for row in rows
        if isinstance(row.get("filtered_rank"), int)
        and low <= int(row["filtered_rank"]) <= high
        and finite_number(row.get("change_24h_pct"))
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
    advance = sum(v > 0 for v in changes) / len(changes)
    med = statistics.median(changes)
    direction = "UP" if advance > 0.5 and med > 0 else ("DOWN" if advance < 0.5 and med < 0 else "NO_EDGE")
    return {
        "direction": direction,
        "constituent_count": len(changes),
        "advance_ratio": round(advance, 6),
        "median_return_24h_pct": round(med, 6),
        "evidence_class": "TOP100_RANK_SEGMENT_PROXY_ONLY",
    }


def build_market_cap_transmission() -> dict[str, Any]:
    breadth = read_json(BREADTH) or {}
    rows = breadth.get("constituents") if isinstance(breadth.get("constituents"), list) else []
    return {
        "large_cap_proxy": {**_tier_row(rows, 3, 25), "rank_segment": "filtered_rank_3_25"},
        "mid_cap_proxy": {**_tier_row(rows, 26, 50), "rank_segment": "filtered_rank_26_50"},
        "small_cap_proxy": {**_tier_row(rows, 51, 100), "rank_segment": "filtered_rank_51_100"},
        "microcap": {
            "direction": "NO_EDGE",
            "evidence_class": "DATA_UNAVAILABLE",
            "reason": "CURRENT_BREADTH_OWNER_STOPS_AT_TOP100",
            "calibrated_probability": None,
        },
        "warning": "Rank segments are transmission proxies, not canonical market-cap bands.",
    }


def _prediction_paths() -> list[Path]:
    return sorted(PREDICTIONS.rglob("*.json")) if PREDICTIONS.exists() else []


def _outcome_paths() -> list[Path]:
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
    last_cutoff: datetime | None = None
    for row in sorted(rows, key=lambda item: item.get("source_price_observation_utc") or item["issued_at_utc"]):
        cutoff = parse_utc(row.get("source_price_observation_utc") or row["issued_at_utc"])
        if last_cutoff is None or cutoff - last_cutoff >= timedelta(hours=horizon_hours):
            chosen.append(row)
            last_cutoff = cutoff
    return chosen


def build_calibration_summary(cfg: dict[str, Any], now: datetime, *, persist: bool = True) -> dict[str, Any]:
    scored = []
    for path in _outcome_paths():
        row = read_json(path)
        if (
            row
            and row.get("contract") == "INTRADAY_DIRECTION_OUTCOME_v1"
            and row.get("status") == "MATURED"
            and row.get("result") in {"HIT", "MISS"}
        ):
            scored.append(row)

    summary = calibration_summary_from_rows(scored, cfg, now)
    if persist:
        write_json(CALIBRATION, summary)
    return summary


def calibration_summary_from_rows(scored: list[dict[str, Any]], cfg: dict[str, Any], now: datetime) -> dict[str, Any]:
    """Pure owner scorer, also used to verify persisted calibration receipts."""
    scored = [row for row in scored if row.get("status") == "MATURED" and row.get("result") in {"HIT", "MISS"}]
    groups: dict[str, list[dict[str, Any]]] = {}
    family_counts: dict[str, dict[str, int]] = {}
    for row in scored:
        groups.setdefault(row["calibration_group"], []).append(row)
        actual = row.get("actual_direction")
        for vote in row.get("votes", []):
            family = vote.get("family")
            vote_direction = vote.get("direction")
            if not family or vote_direction not in {"UP", "DOWN"} or actual not in {"UP", "DOWN"}:
                continue
            key = f"{row['target']}:{row['horizon_hours']}H:{family}"
            bucket = family_counts.setdefault(key, {"hit": 0, "miss": 0})
            bucket["hit" if vote_direction == actual else "miss"] += 1

    min_n = int(cfg.get("minimum_independent_calibration_samples", 20))
    strong_n = int(cfg.get("strong_calibration_samples", 50))
    assurance_n = int(cfg.get("high_assurance_minimum_independent_samples", 300))
    rendered_groups: dict[str, Any] = {}
    for group_id, rows in groups.items():
        horizon = int(rows[0]["horizon_hours"])
        independent = _independent_rows(rows, horizon)
        hits = sum(row["result"] == "HIT" for row in independent)
        total = len(independent)
        empirical = hits / total if total else None
        estimate = (hits + 1) / (total + 2) if total else None
        wilson = _wilson_lower(hits, total)
        briers = [
            float(row["brier_score"])
            for row in independent
            if isinstance(row.get("brier_score"), (int, float))
        ]
        if total < min_n:
            maturity, display = "WARMUP", None
        elif total < strong_n:
            maturity, display = "EARLY_CALIBRATION", estimate
        elif total < assurance_n:
            maturity, display = "CALIBRATED", estimate
        else:
            eligible_99 = bool(
                estimate is not None
                and estimate >= 0.99
                and wilson is not None
                and wilson >= float(cfg.get("high_assurance_wilson_floor", 0.97))
            )
            maturity = "HIGH_ASSURANCE_99_ELIGIBLE" if eligible_99 else "CALIBRATED_STRONG"
            display = estimate
        # Rounding must not create a 99% claim before the separate assurance gate.
        if display is not None and round(display * 100.0, 1) >= 99.0 and maturity != "HIGH_ASSURANCE_99_ELIGIBLE":
            display = None
        rendered_groups[group_id] = {
            "total_scored_rows": len(rows),
            "independent_count": total,
            "hits": hits,
            "misses": total - hits,
            "empirical_hit_rate": round(empirical, 6) if empirical is not None else None,
            "laplace_calibrated_estimate": round(estimate, 6) if estimate is not None else None,
            "wilson_lower_95": round(wilson, 6) if wilson is not None else None,
            "mean_brier_score": round(statistics.fmean(briers), 6) if briers else None,
            "maturity": maturity,
            "display_probability": round(display, 6) if display is not None else None,
            "overlap_control": f"GREEDY_NON_OVERLAP_{horizon}H",
        }

    reliability = {}
    for key, counts in family_counts.items():
        total = counts["hit"] + counts["miss"]
        reliability[key] = {
            **counts,
            "count": total,
            "hit_rate": round(counts["hit"] / total, 6) if total else None,
            "independence_control": "NONE_DIAGNOSTIC_ONLY",
            "authority": "DIAGNOSTIC_ONLY_NO_AUTOMATIC_REWEIGHTING",
        }

    summary = {
        "contract": "INTRADAY_DIRECTION_CALIBRATION_v1",
        "generated_at_utc": iso(now),
        "scored_outcome_count": len(scored),
        "groups": rendered_groups,
        "family_reliability": reliability,
        "governance": {
            "shadow_only": True,
            "automatic_signal_reweighting": False,
            "canonical_market_state": False,
            "portfolio_execution": False,
        },
    }
    return summary


def _group_id(target: str, horizon: int, direction: str, key: str) -> str:
    return f"{target}:{horizon}H:{direction}:{key}"


def _calibration_view(
    summary: dict[str, Any], target: str, horizon: int, vote_summary: dict[str, Any]
) -> dict[str, Any]:
    direction = vote_summary["direction"]
    if direction == "NO_EDGE":
        return {
            "confidence_status": "ABSTAIN_NO_EDGE",
            "calibrated_probability": None,
            "independent_calibration_samples": 0,
        }
    group_id = _group_id(target, horizon, direction, vote_summary["calibration_key"])
    group = (summary.get("groups") or {}).get(group_id) or {}
    probability = group.get("display_probability")
    if finite_number(probability) and round(float(probability) * 100.0, 1) >= 99.0 and group.get("maturity") != "HIGH_ASSURANCE_99_ELIGIBLE":
        probability = None
    return {
        "confidence_status": group.get("maturity", "WARMUP"),
        "calibrated_probability": round(float(probability) * 100.0, 1)
        if isinstance(probability, (int, float))
        else None,
        "independent_calibration_samples": int(group.get("independent_count", 0)),
        "calibration_group": group_id,
        "wilson_lower_95_pct": round(float(group["wilson_lower_95"]) * 100.0, 1)
        if isinstance(group.get("wilson_lower_95"), (int, float))
        else None,
    }


def _horizon_eligibility(
    obs: dict[str, Any], now: datetime, horizon: int, cfg: dict[str, Any]
) -> dict[str, Any]:
    observed_at = _source_price_observation_time(obs)
    due = observed_at + timedelta(hours=horizon)
    remaining = (due - now).total_seconds() / 3600.0
    minimum = horizon * float(cfg.get("minimum_remaining_fraction_of_horizon", 0.5))
    lag_minutes = (now - observed_at).total_seconds() / 60.0
    if lag_minutes < 0:
        status = "SOURCE_CLOSE_NOT_YET_OBSERVABLE"
    elif lag_minutes > float(cfg.get("max_prediction_issue_lag_minutes", 90)):
        status = "SOURCE_TOO_STALE"
    else:
        status = "ELIGIBLE" if remaining >= minimum else "INSUFFICIENT_REMAINING_FORWARD_SPAN"
    return {
        "status": status,
        "source_cutoff_utc": iso(observed_at),
        "due_at_utc": iso(due),
        "remaining_forward_hours_at_issue": round(remaining, 6),
        "minimum_remaining_forward_hours": round(minimum, 6),
    }


def _prediction_path(issued_at: datetime) -> Path:
    return PREDICTIONS / f"{issued_at:%Y/%m/%d}/{issued_at:%Y%m%dT%H%M%SZ}.json"


def write_prediction(
    obs: dict[str, Any],
    cfg: dict[str, Any],
    now: datetime,
    vote_summaries: dict[str, dict[str, Any]],
    calibration: dict[str, Any],
    *,
    registration: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> tuple[str, str | None]:
    if not registration or not context:
        return "NO_CANONICAL_REGISTRATION_NO_PREDICTION", None
    prices = [(obs.get(asset) or {}).get("close") for asset in ("btc", "eth", "ethbtc")]
    if not obs.get("hourly_sequence_run_id") or not all(finite_number(price) and price > 0 for price in prices):
        return "INVALID_SOURCE_PRICE_NO_PREDICTION", None
    observed_at = _source_price_observation_time(obs)
    lag_minutes = (now - observed_at).total_seconds() / 60.0
    max_lag = float(cfg.get("max_prediction_issue_lag_minutes", 90))
    if lag_minutes < 0 or lag_minutes > max_lag:
        return "STALE_INPUT_NO_PREDICTION", None
    # Identity belongs to the source candle, not a retry's wall-clock timestamp.
    for existing_path in _prediction_paths():
        existing = read_json(existing_path) or {}
        if existing.get("source_price_observation_utc") == iso(observed_at):
            return "DUPLICATE_NOOP", str(existing_path)

    horizons: dict[str, Any] = {}
    for horizon in [int(v) for v in cfg.get("direction_horizons_hours", [1, 4, 24])]:
        eligibility = _horizon_eligibility(obs, now, horizon, cfg)
        if eligibility["status"] != "ELIGIBLE":
            continue
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
                "independent_calibration_samples_at_issue": cal["independent_calibration_samples"],
                "wilson_lower_95_pct_at_issue": cal.get("wilson_lower_95_pct"),
            }
        horizons[f"{horizon}H"] = {
            "horizon_hours": horizon,
            **eligibility,
            "targets": targets,
        }

    if not horizons:
        return "NO_ELIGIBLE_FORWARD_HORIZON", None
    path = _prediction_path(now)
    if path.exists():
        return "DUPLICATE_NOOP", str(path)
    prediction = {
        "contract": "INTRADAY_DIRECTION_PREDICTION_v1",
        "registered_test_id": TEST_ID,
        "registration_receipt_sha256": registration["receipt_sha256"],
        "production_context": context,
        "issued_at_utc": iso(now),
        "source_candle_open_utc": obs.get("price_observation_utc"),
        "source_price_observation_utc": iso(observed_at),
        "source_observation_semantics": "CLOSED_1H_CANDLE_CLOSE_OBSERVABLE_TIME",
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


def _hourly_source_path(due: datetime) -> Path:
    candle_open = due - timedelta(hours=1)
    return HOURLY_ROOT / f"{candle_open:%Y/%m/%Y-%m-%d}.csv"


def _close_from_csv(raw_csv: str, due: datetime, target: str, logical_path: Path) -> dict[str, Any] | None:
    candle_open = due - timedelta(hours=1)
    try:
        rows = [row for row in csv.DictReader(io.StringIO(raw_csv))
                if row.get("timestamp_utc") and parse_utc(row["timestamp_utc"]) == candle_open]
        if len(rows) != 1 or rows[0].get("spot_status") != "PASS":
            return None
        close = float(rows[0][f"{target.lower()}_close"])
        if not finite_number(close) or close <= 0:
            return None
    except (csv.Error, KeyError, TypeError, ValueError):
        return None
    binding = {"source_path": logical_path.as_posix(), "candle_open_utc": iso(candle_open),
               "target": target, "close": close, "spot_status": "PASS"}
    return {**binding, "price_observation_utc": iso(due),
            "semantics": "EXACT_DUE_CLOSED_1H_OWNER_CANDLE",
            "source_binding_sha256": content_hash(binding)}


def _exact_hourly_close(due: datetime, target: str, *, root: Path = Path(".")) -> dict[str, Any] | None:
    """Read the exact closed owner candle ending at `due`.

    Hourly CSV timestamps are candle-open timestamps, therefore the row whose
    timestamp is `due - 1h` supplies the close observed exactly at `due`.
    Later closes are never substituted for a missing exact-horizon close.
    """
    logical_path = _hourly_source_path(due)
    path = root / logical_path
    try:
        return _close_from_csv(path.read_text(encoding="utf-8"), due, target, logical_path)
    except (OSError, UnicodeError):
        return None


def exact_hourly_close_at_commit(root: Path, commit: str, due: datetime, target: str) -> dict[str, Any] | None:
    """Verify censoring against the source snapshot the production run observed.

    A later legitimate backfill must neither erase a frozen censor nor make a
    MISS eligible for censorship. Git is the existing immutable source archive.
    Shallow CI may fetch the one recorded commit into its object cache; no
    checkout, tracked-file write, market API request or ref update is performed.
    """
    def git(*args):
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=60)
    try:
        if git("cat-file", "-e", commit + "^{commit}").returncode:
            if git("fetch", "--quiet", "--no-tags", "--no-write-fetch-head", "--depth=1", "origin", commit).returncode:
                raise RuntimeError("CENSOR_SOURCE_COMMIT_UNAVAILABLE")
        path = _hourly_source_path(due).as_posix()
        entry = git("ls-tree", commit, "--", path)
        if entry.returncode:
            raise RuntimeError("CENSOR_SOURCE_TREE_UNREADABLE")
        if not entry.stdout.strip():
            return None
        source = git("show", f"{commit}:{path}")
        if source.returncode:
            raise RuntimeError("CENSOR_SOURCE_BLOB_UNREADABLE")
        return _close_from_csv(source.stdout, due, target, Path(path))
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("CENSOR_SOURCE_HISTORY_UNAVAILABLE") from exc


def mature_predictions(
    obs: dict[str, Any], cfg: dict[str, Any], now: datetime,
    *, context: dict[str, Any] | None = None,
) -> dict[str, int]:
    counts = {"matured": 0, "censored": 0, "abstained": 0, "pending": 0}
    max_wait = float(cfg.get("max_outcome_evidence_lag_hours", 1.5))
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
                if now < due:
                    counts["pending"] += 1
                    continue

                evidence = _exact_hourly_close(due, target)
                predicted = target_row.get("direction")
                common = {
                    "contract": "INTRADAY_DIRECTION_OUTCOME_v1",
                    "registered_test_id": pred.get("registered_test_id"),
                    "registration_receipt_sha256": pred.get("registration_receipt_sha256"),
                    "production_context": context,
                    "prediction_path": path.as_posix(),
                    "prediction_sha256": file_hash(path),
                    "issued_at_utc": pred["issued_at_utc"],
                    "source_price_observation_utc": pred["source_price_observation_utc"],
                    "source_candle_open_utc": pred.get("source_candle_open_utc"),
                    "due_at_utc": horizon_row["due_at_utc"],
                    "measured_at_utc": iso(now),
                    "target": target,
                    "horizon_hours": horizon,
                    "predicted_direction": predicted,
                    "start_value": target_row.get("start_value"),
                    "calibration_key": target_row.get("calibration_key"),
                    "calibration_group": _group_id(
                        target, horizon, predicted, target_row.get("calibration_key")
                    ),
                    "votes": target_row.get("votes", []),
                    "frozen_calibrated_probability_pct": target_row.get(
                        "frozen_calibrated_probability_pct"
                    ),
                    "authority": {
                        "shadow_only": True,
                        "automatic_rule_changes": False,
                        "portfolio_execution": False,
                    },
                }

                if evidence is None:
                    wait_hours = (now - due).total_seconds() / 3600.0
                    if wait_hours <= max_wait:
                        counts["pending"] += 1
                        continue
                    write_json(
                        outcome_path,
                        {
                            **common,
                            "status": "CENSORED",
                            "reason": "EXACT_DUE_OWNER_CANDLE_MISSING_AFTER_GRACE",
                            "evidence_wait_hours": round(wait_hours, 6),
                            "substitute_later_price_forbidden": True,
                        },
                    )
                    counts["censored"] += 1
                    continue

                start = target_row.get("start_value")
                end = evidence["close"]
                if not finite_number(start) or float(start) <= 0:
                    raise RuntimeError("INVALID_FROZEN_START_PRICE")

                ret = (float(end) / float(start) - 1.0) * 100.0
                actual = "UP" if ret > 0 else ("DOWN" if ret < 0 else "FLAT")
                if predicted == "NO_EDGE":
                    result, brier = "ABSTAINED", None
                    counts["abstained"] += 1
                else:
                    result = "HIT" if actual == predicted else "MISS"
                    p_pct = target_row.get("frozen_calibrated_probability_pct")
                    p = float(p_pct) / 100.0 if isinstance(p_pct, (int, float)) else None
                    brier = (p - (1.0 if result == "HIT" else 0.0)) ** 2 if p is not None else None
                    counts["matured"] += 1
                aligned = [
                    v["family"]
                    for v in target_row.get("votes", [])
                    if v.get("direction") == actual and actual in {"UP", "DOWN"}
                ]
                opposed = [
                    v["family"]
                    for v in target_row.get("votes", [])
                    if v.get("direction") in {"UP", "DOWN"} and v.get("direction") != actual
                ]
                adjudication_delay = max(0.0, (now - due).total_seconds() / 3600.0)
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
                        "evidence_observation_utc": evidence["price_observation_utc"],
                        "evidence_candle_open_utc": evidence["candle_open_utc"],
                        "evidence_source_path": evidence["source_path"],
                        "evidence_semantics": evidence["semantics"],
                        "evidence_source_binding_sha256": evidence["source_binding_sha256"],
                        "evidence_horizon_error_hours": 0.0,
                        "adjudication_delay_hours": round(adjudication_delay, 6),
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
    research_eligible: bool = True,
) -> dict[str, Any]:
    direction_cfg = cfg.get("shadow_direction_confidence") or {}
    try:
        from scripts.intraday_execution.validate_direction_confidence import validate_repository
    except ModuleNotFoundError:
        from validate_direction_confidence import validate_repository
    # Invalid or unregistered historical rows must not seed new probabilities.
    validate_repository(Path("."), now=now)
    context = production_context()
    registration = ensure_registration(direction_cfg, now, context)
    maturation = (
        mature_predictions(obs, direction_cfg, now, context=context)
        if context else {"matured": 0, "censored": 0, "abstained": 0, "pending": 0}
    )
    calibration = build_calibration_summary(direction_cfg, now, persist=context is not None)
    vote_summaries = {
        target: summarize_votes(build_votes(target, obs), direction_cfg)
        for target in ("BTC", "ETH")
    }

    horizons = {}
    for horizon in [
        int(v) for v in direction_cfg.get("direction_horizons_hours", [1, 4, 24])
    ]:
        eligibility = _horizon_eligibility(obs, now, horizon, direction_cfg)
        targets = {}
        for target in ("BTC", "ETH"):
            base = vote_summaries[target]
            cal = _calibration_view(calibration, target, horizon, base)
            if eligibility["status"] != "ELIGIBLE":
                cal = {
                    **cal,
                    "confidence_status": "NO_PROSPECTIVE_FREEZE_" + eligibility["status"],
                    "calibrated_probability": None,
                }
            targets[target] = {
                "direction": base["direction"] if eligibility["status"] == "ELIGIBLE" else "NO_EDGE",
                "evidence_agreement_pct": base["evidence_agreement_pct"],
                "up_votes": base["up_votes"],
                "down_votes": base["down_votes"],
                **cal,
            }
            if not research_eligible:
                targets[target].update(direction="NO_EDGE", calibrated_probability=None, confidence_status="RESEARCH_CONTEXT_INELIGIBLE")
        horizons[f"{horizon}H"] = {
            "horizon_hours": horizon,
            "prediction_eligibility": eligibility,
            "targets": targets,
        }

    prediction_status = "DUPLICATE_PRICE_OBSERVATION_NO_NEW_PREDICTION"
    prediction_path = None
    if new_prediction and research_eligible:
        prediction_status, prediction_path = write_prediction(
            obs, direction_cfg, now, vote_summaries, calibration,
            registration=registration, context=context,
        )
    elif not research_eligible:
        prediction_status = "RESEARCH_CONTEXT_INELIGIBLE_NO_PREDICTION"

    frozen = read_json(Path(prediction_path)) if prediction_path else None
    if frozen is None:
        cutoff = iso(_source_price_observation_time(obs))
        frozen = next((row for path in _prediction_paths()
                       if (row := read_json(path)) and row.get("source_price_observation_utc") == cutoff), None)
    for key, horizon_row in horizons.items():
        eligible = research_eligible and horizon_row["prediction_eligibility"]["status"] == "ELIGIBLE"
        frozen_horizon = ((frozen or {}).get("horizons") or {}).get(key) or {}
        horizon_row["display_basis"] = "FROZEN_PREDICTION" if eligible and frozen_horizon else "NO_ELIGIBLE_FROZEN_PREDICTION"
        horizon_row["frozen_issued_at_utc"] = (frozen or {}).get("issued_at_utc") if frozen_horizon else None
        for target, row in horizon_row["targets"].items():
            fixed = (frozen_horizon.get("targets") or {}).get(target)
            if eligible and fixed:
                row.update(
                    direction=fixed["direction"], evidence_agreement_pct=fixed["evidence_agreement_pct"],
                    up_votes=sum(v.get("direction") == "UP" for v in fixed["votes"]),
                    down_votes=sum(v.get("direction") == "DOWN" for v in fixed["votes"]),
                    calibrated_probability=fixed.get("frozen_calibrated_probability_pct"),
                    confidence_status=fixed.get("confidence_status_at_issue"),
                    independent_calibration_samples=fixed.get("independent_calibration_samples_at_issue", 0),
                    calibration_group=_group_id(target, horizon_row["horizon_hours"], fixed["direction"], fixed["calibration_key"]),
                    wilson_lower_95_pct=fixed.get("wilson_lower_95_pct_at_issue"),
                )
            else:
                row.update(direction="NO_EDGE", calibrated_probability=None,
                           independent_calibration_samples=0, calibration_group=None, wilson_lower_95_pct=None)
                if eligible:
                    row["confidence_status"] = "NO_FROZEN_PREDICTION"

    transmission = build_market_cap_transmission()
    pieces = []
    for key in ("1H", "4H", "24H"):
        for target in ("BTC", "ETH"):
            row = horizons.get(key, {}).get("targets", {}).get(target, {})
            if row:
                p = row.get("calibrated_probability")
                unavailable = horizons[key]["display_basis"] != "FROZEN_PREDICTION"
                label = "UNAVAILABLE" if unavailable else (p if p is not None else "UNCAL")
                pieces.append(f"{key} {target} {row.get('direction')}({label})")
    display = (
        "SHADOW DIRECTION: "
        + " | ".join(pieces)
        + f" | Large {transmission['large_cap_proxy']['direction']}"
        + f" | Mid {transmission['mid_cap_proxy']['direction']}"
        + f" | Small {transmission['small_cap_proxy']['direction']}"
        + " | Micro NO_EDGE(DATA_GAP)"
    )
    return {
        "contract": "SHADOW_DIRECTION_CONFIDENCE_v1",
        "generated_at_utc": iso(now),
        "source_price_observation_utc": iso(_source_price_observation_time(obs)),
        "source_observation_semantics": "CLOSED_1H_CANDLE_CLOSE_OBSERVABLE_TIME",
        "status": "SHADOW_ONLY",
        "horizons": horizons,
        "market_cap_transmission": transmission,
        "prediction_freeze": {"status": prediction_status, "path": prediction_path},
        "outcome_maturation": maturation,
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
            "later_price_substitution_for_exact_horizon": False,
        },
    }
