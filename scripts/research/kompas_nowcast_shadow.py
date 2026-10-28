"""Fail-closed Kompas 12h point-in-time SHADOW comparator.

Evidence supplied to this function is NOT independently authenticated here.
No original historical scientific admission, forecast revision, or trading authority.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timedelta, timezone
from typing import Mapping

from scripts.learning.compass_outcomes import canon, reference_close_time


def _clock(value: object) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("MISSING_CLOCK")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("NAIVE_CLOCK")
    return parsed.astimezone(timezone.utc)


def _original(blob: object, sha: object) -> dict:
    if not isinstance(blob, str) or not isinstance(sha, str):
        raise ValueError("SOURCE_BYTES_OR_DIGEST_MISSING")
    if hashlib.sha256(blob.encode("utf-8")).hexdigest() != sha:
        raise ValueError("SOURCE_BLOB_SHA_MISMATCH")
    obj = json.loads(blob)
    if not isinstance(obj, dict):
        raise ValueError("SOURCE_NOT_OBJECT")
    return obj


def _self_digest(obj: dict, field: str) -> None:
    declared = obj.get(field)
    if not isinstance(declared, str) or len(declared) != 64:
        raise ValueError("CANONICAL_SELF_DIGEST_MISSING")
    actual = hashlib.sha256(canon({k: v for k, v in obj.items() if k != field})).hexdigest()
    if actual != declared:
        raise ValueError("CANONICAL_SELF_DIGEST_MISMATCH")


def _direction(value: object) -> str:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError("RETURN_MISSING_OR_NONFINITE")
    if value == 0:
        raise ValueError("ZERO_RETURN_DIRECTION_UNSCORABLE")
    return "UP" if value > 0 else "DOWN"


def compare_shadow_12h(attempts: list[Mapping[str, object]]) -> dict:
    """Compare strictly paired ORIGINAL 12h vs 1h persistence, without promotion.

    Inputs must include externally audited first-known flags and immutable bytes;
    caller-supplied attestations are *not* an independent proof by themselves.
    Distinct issuance and (original forecast-bound source packet SHA256,target)\n    dedup both apply; caller source_event_id is an unauthenticated display tag.
    """
    if not isinstance(attempts, list):
        raise ValueError("ATTEMPT_LIST_REQUIRED")
    rows = []
    seen_issuances: set[str] = set()
    seen_events: set[tuple[str, str]] = set()
    for attempt in attempts:
        decision = {"status": "EXCLUDED", "reason": "UNVERIFIED_OR_INVALID"}
        try:
            if not isinstance(attempt, Mapping):
                raise ValueError("NOT_MAPPING")
            forecast = _original(attempt.get("forecast_original_json"), attempt.get("forecast_blob_sha256"))
            outcome = _original(attempt.get("outcome_original_json"), attempt.get("outcome_blob_sha256"))
            if (forecast.get("contract") != "OFFICIAL_DAILY_COMPASS_v1"
                or outcome.get("contract") != "OFFICIAL_DAILY_COMPASS_OUTCOME_v1"
                or forecast.get("scoring_contract") != "OFFICIAL_DAILY_COMPASS_SCORING_v3"
                or outcome.get("scoring_contract") != "OFFICIAL_DAILY_COMPASS_SCORING_v3"):
                raise ValueError("UNSUPPORTED_OR_UNBOUND_CONTRACT")
            _self_digest(forecast, "compass_sha256")
            _self_digest(outcome, "outcome_sha256")
            ident = forecast.get("compass_id")
            if not isinstance(ident, str) or not ident or ident in seen_issuances:
                raise ValueError("DUPLICATE_OR_MISSING_ISSUANCE")
            decision["compass_id"] = ident
            if not all(attempt.get(field) is True for field in (
                "forecast_first_known_verified", "source_first_known_verified",
                "outcome_custody_verified", "prior_hour_custody_verified"
            )):
                raise ValueError("INDEPENDENT_FIRST_KNOWN_OR_CUSTODY_NOT_PROVEN")
            if not all(isinstance(attempt.get(field), str) and attempt[field] for field in (
                "forecast_receipt_ref", "source_receipt_ref", "outcome_receipt_ref",
                "prior_hour_receipt_ref", "source_event_id"
            )):
                raise ValueError("INDEPENDENT_RECEIPT_REFERENCE_MISSING")
            issued = _clock(forecast["issued_at_utc"])
            first = _clock(attempt["forecast_first_known_at_utc"])
            source_first = _clock(attempt["source_first_known_at_utc"])
            prior_first = _clock(attempt["prior_hour_first_known_at_utc"])
            prior_end = _clock(attempt["prior_hour_end_at_utc"])
            target = _clock(outcome["target_at_utc"])
            matured = _clock(outcome["matured_at_utc"])
            reference_data = forecast.get("market_reference")
            if not isinstance(reference_data, Mapping):
                raise ValueError("SCORER_REFERENCE_NOT_MAPPING")
            reference = reference_close_time(reference_data)
            if reference is None:
                raise ValueError("REFERENCE_CLOSE_NOT_BOUND")
            if source_first > issued or prior_first > issued or prior_end > issued:
                raise ValueError("LOOKAHEAD_SOURCE_OR_PRIOR_HOUR")
            if prior_end > prior_first:
                raise ValueError("PRIOR_HOUR_FIRST_KNOWN_BEFORE_CLOSE")
            if reference > issued or target != reference + timedelta(hours=12):
                raise ValueError("SCORER_REFERENCE_PLUS_12H_MISMATCH")
            time_basis = outcome.get("time_basis")
            if not isinstance(time_basis, Mapping):
                raise ValueError("SCORER_TIME_BASIS_NOT_MAPPING")
            if (_clock(time_basis.get("start_reference_at_utc")) != reference
                or time_basis.get("nominal_horizon_hours") != 12):
                raise ValueError("SCORER_REFERENCE_TIME_BASIS_MISMATCH")
            selected = _clock(outcome.get("target_observation_at_utc"))
            if not (issued < selected <= matured and
                    abs((selected - target).total_seconds()) <= 3600):
                raise ValueError("TARGET_OBSERVATION_OUTSIDE_SCORER_TOLERANCE")
            # Validate the ORIGINAL chosen hourly candle, not merely the
            # claimed target close. The scorer records its real open as well
            # as its close; missing/mismatched opens must not be inferred.
            target_open = _clock(outcome.get("target_observation_open_at_utc"))
            if target_open + timedelta(hours=1) != selected:
                raise ValueError("TARGET_OBSERVATION_OPEN_CLOSE_MISMATCH")
            if target_open < issued:
                raise ValueError("TARGET_CANDLE_OPEN_BEFORE_ISSUANCE")
            # A rehashed issuance many hours after the scorer reference can
            # otherwise inherit the frozen reference+12h close and be scored
            # as a nominal 12h forecast, despite being issued near maturity.
            nominal_from_issuance = issued + timedelta(hours=12)
            if (abs((target - nominal_from_issuance).total_seconds()) > 3600
                or abs((selected - nominal_from_issuance).total_seconds()) > 3600):
                raise ValueError("ISSUANCE_TO_12H_TARGET_DRIFT")
            # Strict as-issued research eligibility: an independently first-known
            # forecast receipt AFTER the declared issuance cannot prove the
            # direction existed at issuance, even if only seconds later.
            if first > issued:
                raise ValueError("FORECAST_FIRST_KNOWN_AFTER_ISSUANCE")
            if not (issued < target <= matured):
                raise ValueError("NONPROSPECTIVE_ISSUER_TARGET_OR_OUTCOME")
            # The canonical scorer anchors to the hourly close. An original
            # source packet first known before that close cannot attest to a
            # completed reference candle; no future-bar proxy admission.
            if source_first < reference:
                raise ValueError("SOURCE_FIRST_KNOWN_BEFORE_SCORER_REFERENCE_CLOSE")
            # A caller-labelled prior-hour comparator must be adjacent to the
            # original scorer reference, not an arbitrarily stale candle.
            if not (reference - timedelta(hours=1) <= prior_end <= reference):
                raise ValueError("PRIOR_HOUR_BASELINE_STALE_OR_FUTURE")
            if (outcome.get("compass_id") != ident or outcome.get("horizon") != "12h"
                or outcome.get("issued_at_utc") != forecast["issued_at_utc"]
                or outcome.get("compass_sha256") != forecast.get("compass_sha256")):
                raise ValueError("FORECAST_OUTCOME_CUSTODY_UNBOUND")
            # Actual OFFICIAL_DAILY_COMPASS_v1 producer stores this binding
            # under source_bindings.auto_market_state, NOT at forecast top level.
            # The synthetic fixture must match that real producer contract.
            bindings = forecast.get("source_bindings")
            auto_binding = bindings.get("auto_market_state") if isinstance(bindings, Mapping) else None
            source_sha = auto_binding.get("packet_sha256") if isinstance(auto_binding, Mapping) else None
            if not isinstance(source_sha, str) or re.fullmatch(r"[a-f0-9]{64}", source_sha) is None:
                raise ValueError("FORECAST_SOURCE_PACKET_SHA_UNBOUND")
            # Never use an externally supplied source_event_id as the cluster
            # identity: relabeling the same packet could inflate scientific N.
            group = (source_sha, target.isoformat())
            if group in seen_events:
                raise ValueError("DUPLICATE_SOURCE_PACKET_TARGET")
            expected = forecast["horizons"]["NEXT_12H"]["expected_direction"]
            if expected not in ("UP", "DOWN"):
                raise ValueError("NON_DIRECTIONAL_FORECAST")
            btc_real = outcome["direction_accuracy"]["btc"]["realized_pct"]
            eth_real = outcome["direction_accuracy"]["eth"]["realized_pct"]
            btc_actual, eth_actual = _direction(btc_real), _direction(eth_real)
            btc_persist = _direction(attempt["prior_hour_btc_delta_pct"])
            eth_persist = _direction(attempt["prior_hour_eth_delta_pct"])
            seen_issuances.add(ident)
            seen_events.add(group)
            decision = {
                "compass_id": ident, "status": "PROVISIONAL_RESEARCH_ONLY",
                "reason": "EXTERNALLY_ATTESTED_FIELDS_NOT_INDEPENDENTLY_VALIDATED_HERE",
                "source_event_id": str(attempt["source_event_id"]),
                "source_packet_sha256": source_sha,
                "target_at_utc": outcome["target_at_utc"],
                "issued_direction": expected,
                "btc_correct": expected == btc_actual, "eth_correct": expected == eth_actual,
                "persistence_btc_correct": btc_persist == btc_actual,
                "persistence_eth_correct": eth_persist == eth_actual,
            }
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            decision["reason"] = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        rows.append(decision)
    scored = [x for x in rows if x["status"] == "PROVISIONAL_RESEARCH_ONLY"]
    return {
        "contract": "KOMPAS_12H_PIT_SHADOW_RESEARCH_v1",
        "mode": "SHADOW_ONLY_NO_SCIENTIFIC_ADMISSION",
        "attempted": len(attempts), "provisional_paired": len(scored),
        "excluded": len(attempts) - len(scored),
        "provisional_coverage": len(scored) / len(attempts) if attempts else None,
        "scientific_edge_verified": False, "trading_authority": False,
        "baseline": "INDEPENDENT_PRIOR_HOUR_SIGN_NOT_TRADE_RETURN",
        "rows": rows,
    }
