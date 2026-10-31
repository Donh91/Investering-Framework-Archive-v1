"""Stage-one CLOCK/POLICY preflight for a prospectively frozen Kompas trial.

This module is intentionally NOT a source/provenance authenticator. In
particular, an input dict, boolean flag, Git blob or commit timestamp can
NEVER establish pre-issue public knowledge or provider first-known state.
Only a separately authorized, independently authenticated admission service
can lift scientific hold. This code does not read external data or score.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections.abc import Mapping

_PROTOCOL_PATH = Path(__file__).with_name("CRE_NEXT12H_PROSPECTIVE_PROTOCOL_v1.json")
PROTOCOL = json.loads(_PROTOCOL_PATH.read_text(encoding="utf-8"))
HOUR = timedelta(hours=1)
_SHA40 = re.compile(r"^[a-f0-9]{40}$")
_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_ALLOWED_DIRECTIONS = frozenset(("UP", "DOWN"))


def parse_utc(value):
    """Return aware UTC datetime or None. Never infer a missing zone."""
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def _valid_number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def preflight(freeze: Mapping, public_witness: Mapping | None = None,
              source_witness: Mapping | None = None) -> dict:
    """Classify temporal feasibility, NEVER scientific/PIT admissibility.

    Witness dictionaries are untrusted user data. Even if they claim
    verified=true, this module neither fetches authenticated GitHub events
    nor validates a provider source timestamp. The output is always HOLD.
    """
    errors = []
    freeze = freeze if isinstance(freeze, Mapping) else {}
    public_witness = public_witness if isinstance(public_witness, Mapping) else {}
    source_witness = source_witness if isinstance(source_witness, Mapping) else {}
    issue = parse_utc(freeze.get("issued_at_utc"))
    pub = parse_utc(public_witness.get("server_created_at_utc"))
    source_known = parse_utc(source_witness.get("market_first_known_at_utc"))
    baseline_known = parse_utc(source_witness.get("baseline_first_known_at_utc"))
    ref = freeze.get("market_reference")
    ref = ref if isinstance(ref, Mapping) else {}
    ref_open = parse_utc(ref.get("observation_open_utc"))
    ref_close = ref_open + HOUR if ref_open else None
    target = ref_close + timedelta(hours=12) if ref_close else None
    horizon = freeze.get("horizons")
    horizon = horizon if isinstance(horizon, Mapping) else {}
    h12 = horizon.get("NEXT_12H")
    h12 = h12 if isinstance(h12, Mapping) else {}
    market_now = freeze.get("market_now")
    market_now = market_now if isinstance(market_now, Mapping) else {}
    momentum = market_now.get("btc_delta_pct")
    forecast = h12.get("expected_direction")

    if freeze.get("contract") != PROTOCOL["universe"]["forecast_contract"]:
        errors.append("FORECAST_CONTRACT_MISMATCH")
    if freeze.get("scoring_contract") != PROTOCOL["universe"]["scoring_contract"]:
        errors.append("SCORING_VERSION_NOT_REGISTERED")
    if issue is None:
        errors.append("ISSUE_CLOCK_MISSING_OR_INVALID")
    else:
        phase = next((x["name"] for x in PROTOCOL["phases"]
                      if parse_utc(x["start_utc"]) <= issue < parse_utc(x["end_exclusive_utc"])), None)
        if phase is None:
            errors.append("OUTSIDE_FROZEN_COHORT")
        if not (7 <= issue.hour < 9):
            errors.append("OUTSIDE_DAILY_UTC_SELECTION_WINDOW")
    if ref_open is None or ref_open.minute or ref_open.second or ref_open.microsecond:
        errors.append("REFERENCE_NOT_WHOLE_UTC_OPEN")
    if issue is not None and ref_close is not None and ref_close > issue:
        errors.append("REFERENCE_CANDLE_FROM_FUTURE")
    if forecast not in _ALLOWED_DIRECTIONS:
        errors.append("NO_DIRECTIONAL_CALL_OR_ABSTAIN")
    if not _valid_number(momentum):
        errors.append("BASELINE_NOT_ORIGINALLY_FROZEN")
    elif momentum == 0:
        errors.append("FLAT_MOMENTUM_ABSTAINS")
    if not _valid_number(ref.get("btc_usdt")) or ref["btc_usdt"] <= 0:
        errors.append("INVALID_OR_MISSING_REFERENCE_PRICE")
    if pub is None:
        errors.append("NO_INDEPENDENT_PUBLICATION_TIME_INPUT")
    if source_known is None or baseline_known is None:
        errors.append("SOURCE_FIRST_KNOWN_CLOCKS_MISSING")
    if pub is not None and issue is not None and pub < issue:
        errors.append("PUBLICATION_BEFORE_DECLARED_ISSUANCE")
    if pub is not None and target is not None:
        if pub >= target:
            errors.append("PUBLICATION_NOT_BEFORE_TARGET")
        elif (target - pub).total_seconds() < 10 * 3600:
            errors.append("LESS_THAN_TEN_EFFECTIVE_FORECAST_HOURS")
    for known in (source_known, baseline_known):
        if known is not None and pub is not None and known > pub:
            errors.append("SOURCE_KNOWN_AFTER_PUBLICATION")
    sha = public_witness.get("original_file_sha256")
    commit = public_witness.get("first_git_commit_sha40")
    path = public_witness.get("original_path")
    if (not isinstance(sha, str) or not _SHA256.fullmatch(sha)
            or not isinstance(commit, str) or not _SHA40.fullmatch(commit)
            or not isinstance(path, str)
            or not path.startswith("04_MARKET_LEARNING/handlekompas/official/daily/")
            or not path.endswith(".json") or ".." in path.split("/")):
        errors.append("PUBLIC_BLOB_IDENTITY_UNBOUND")
    if freeze.get("pit_verified") is True or public_witness.get("scientific_approved") is True:
        errors.append("UNTRUSTED_SELF_ATTESTATION_IGNORED")

    return {
        "contract": "CRE_PROSPECTIVE_TEMPORAL_PREFLIGHT_v1",
        "study_id": PROTOCOL["study_id"],
        "issue_utc": issue.isoformat().replace("+00:00", "Z") if issue else None,
        "reference_candle_close_utc": ref_close.isoformat().replace("+00:00", "Z") if ref_close else None,
        "target_utc": target.isoformat().replace("+00:00", "Z") if target else None,
        "effective_forward_hours_from_publication": round((target-pub).total_seconds()/3600, 4)
            if target is not None and pub is not None else None,
        "temporal_preflight_pass": len(errors) == 0,
        "quarantine_reasons": sorted(set(errors)),
        "external_full_day_census_verified": False,
        "independent_publication_verified": False,
        "independent_source_first_known_verified": False,
        "scientifically_admitted": False,
        "prospective_edge_authority": "NONE",
        "evidence_state": "CLOCK_PREFLIGHT_ONLY_EXTERNAL_AUTHENTICATION_REQUIRED"
            if not errors else "QUARANTINED",
    }


def ensure_study_not_started_late(protocol_merge_time_utc):
    """Never permit retroactive cohort activation based on a moving main."""
    merged = parse_utc(protocol_merge_time_utc)
    cutoff = parse_utc(PROTOCOL["activation"]["must_merge_protocol_before"])
    return bool(merged is not None and cutoff is not None and merged < cutoff)
