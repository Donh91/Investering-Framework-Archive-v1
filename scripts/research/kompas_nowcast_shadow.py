"""Fail-closed Kompas 12h point-in-time SHADOW comparator.

Evidence supplied to this function is NOT independently authenticated here.
No original historical scientific admission, forecast revision, or trading authority.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from typing import Mapping


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
    Distinct issuance and (source_event_id,target) dedup both apply.
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
            ident = forecast.get("compass_id")
            if not isinstance(ident, str) or not ident or ident in seen_issuances:
                raise ValueError("DUPLICATE_OR_MISSING_ISSUANCE")
            seen_issuances.add(ident)
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
            if source_first > issued or prior_first > issued or prior_end > issued:
                raise ValueError("LOOKAHEAD_SOURCE_OR_PRIOR_HOUR")
            if not (issued <= first < target <= matured):
                raise ValueError("NONPROSPECTIVE_ISSUER_TARGET_OR_OUTCOME")
            if (outcome.get("compass_id") != ident or outcome.get("horizon") != "12h"
                or outcome.get("issued_at_utc") != forecast["issued_at_utc"]
                or outcome.get("compass_sha256") != forecast.get("compass_sha256")):
                raise ValueError("FORECAST_OUTCOME_CUSTODY_UNBOUND")
            group = (str(attempt["source_event_id"]), target.isoformat())
            if group in seen_events:
                raise ValueError("DUPLICATE_SOURCE_EVENT_TARGET")
            expected = forecast["horizons"]["NEXT_12H"]["expected_direction"]
            if expected not in ("UP", "DOWN"):
                raise ValueError("NON_DIRECTIONAL_FORECAST")
            btc_real = outcome["direction_accuracy"]["btc"]["realized_pct"]
            eth_real = outcome["direction_accuracy"]["eth"]["realized_pct"]
            btc_actual, eth_actual = _direction(btc_real), _direction(eth_real)
            btc_persist = _direction(attempt["prior_hour_btc_delta_pct"])
            eth_persist = _direction(attempt["prior_hour_eth_delta_pct"])
            seen_events.add(group)
            decision = {
                "compass_id": ident, "status": "PROVISIONAL_RESEARCH_ONLY",
                "reason": "EXTERNALLY_ATTESTED_FIELDS_NOT_INDEPENDENTLY_VALIDATED_HERE",
                "source_event_id": group[0], "target_at_utc": outcome["target_at_utc"],
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
