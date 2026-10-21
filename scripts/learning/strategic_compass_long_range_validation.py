#!/usr/bin/env python3
"""Research-only candidate long-range scenario validation for Strategic Compass.

Deterministic, source-call-free and without producer/consumer or trading authority.
This validates *candidate* data, not forecast accuracy or original source custody.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "LONG_RANGE_SCENARIO_v0_1_CANDIDATE"
SHA = re.compile(r"^[0-9a-f]{64}$")
UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
HORIZONS = {"1_3M", "3_6M", "6_9M", "9_12M"}
CLOCKS = {"MACRO_CYCLE_CLOCK", "HALVING_CALENDAR_CLOCK", "TACTICAL_TRANSMISSION_CLOCK"}
ASSETS = {"bitcoin", "ethereum", "ROTATION_ENVIRONMENT"}


def _fail(reason: str) -> None:
    raise ValueError(reason)


def _obj(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{name}: expected object")
    return value


def _keys(obj: Mapping[str, Any], required: set[str], optional: set[str], where: str) -> None:
    missing, extra = required - obj.keys(), obj.keys() - required - optional
    if missing or extra:
        _fail(f"{where}: missing={sorted(missing)} unknown={sorted(extra)}")


def _string(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(f"{where}: non-empty string required")
    return value


def _ts(value: Any, where: str) -> datetime:
    if not isinstance(value, str) or not UTC.fullmatch(value):
        _fail(f"{where}: exact UTC ISO-8601 required")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _fail(f"{where}: invalid date")


def _hash(value: Any, where: str) -> None:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        _fail(f"{where}: sha256 hex required")


def _price(value: Any, where: str) -> None:
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value <= 0:
        _fail(f"{where}: positive finite numeric price required")


def _strings(values: Any, where: str, minimum: int = 0) -> None:
    if not isinstance(values, list) or len(values) < minimum:
        _fail(f"{where}: array length invalid")
    for i, value in enumerate(values):
        _string(value, f"{where}[{i}]")


def validate_candidate(value: Mapping[str, Any], *, prior_issues: Mapping[str, Mapping[str, Any]] | None = None) -> None:
    """Raise ValueError on unsafe research scenario. Never grants publication authority."""
    v = _obj(value, "root")
    _keys(v, {"contract", "authority", "status", "frozen_issue", "observation", "hypothesis_families"}, {"afterwards_actual"}, "root")
    if v["contract"] != CONTRACT or v["authority"] != "SHADOW_SCENARIO_ONLY":
        _fail("contract/authority: candidate shadow only")
    status = v["status"]
    if status not in {"SCENARIO_ONLY", "UNAVAILABLE", "ABSTAIN"}:
        _fail("status: unsupported")
    if v.get("afterwards_actual") is not None:
        _fail("issued object cannot contain matured actuals")

    frozen = _obj(v["frozen_issue"], "frozen_issue")
    _keys(frozen,
          {"forecast_id", "issued_at_utc", "cutoff_utc", "source_manifest_sha256", "model_policy_version", "freeze_content_sha256"},
          {"freeze_git_sha", "revision_of", "revision_cost"}, "frozen_issue")
    issue_id = _string(frozen["forecast_id"], "forecast_id")
    issued = _ts(frozen["issued_at_utc"], "issued_at_utc")
    cutoff = _ts(frozen["cutoff_utc"], "cutoff_utc")
    if cutoff > issued:
        _fail("cutoff must be no later than issue")
    _hash(frozen["source_manifest_sha256"], "source_manifest_sha256")
    _hash(frozen["freeze_content_sha256"], "freeze_content_sha256")
    _string(frozen["model_policy_version"], "model_policy_version")
    if frozen.get("freeze_git_sha") is not None:
        if not isinstance(frozen["freeze_git_sha"], str) or not re.fullmatch(r"[0-9a-f]{40}", frozen["freeze_git_sha"]):
            _fail("freeze_git_sha: full Git SHA required")
    if frozen.get("revision_cost") is not None:
        _fail("revision cost must be measured after maturation, not issued")
    revision = frozen.get("revision_of")
    if revision is not None:
        _string(revision, "revision_of")
        if revision == issue_id:
            _fail("self revision forbidden")
        if prior_issues is None or revision not in prior_issues:
            _fail("revision requires independently supplied original issue")
        parent = _obj(prior_issues[revision], "prior_issue")
        if parent.get("forecast_id") != revision or _ts(parent.get("issued_at_utc"), "prior_issued_at_utc") >= issued:
            _fail("revision parent invalid or not earlier")
        if parent.get("freeze_content_sha256") is None:
            _fail("revision parent must be hash-bound")
        _hash(parent["freeze_content_sha256"], "prior_sha256")
        visited = {issue_id}
        node = revision
        while node is not None:
            if node in visited or node not in prior_issues:
                _fail("revision cycle or unknown ancestor")
            visited.add(node)
            previous = _obj(prior_issues[node], "revision_ancestor")
            node = previous.get("revision_of")

    observation = _obj(v["observation"], "observation")
    _keys(observation, {"as_of_utc", "items"}, set(), "observation")
    as_of = _ts(observation["as_of_utc"], "observation.as_of_utc")
    if as_of > cutoff:
        _fail("observation is newer than issue cutoff")
    items = observation["items"]
    if not isinstance(items, list):
        _fail("observation.items: array required")
    seen_items: set[str] = set()
    for item in items:
        item = _obj(item, "observation.item")
        _keys(item, {"id", "value_state", "settled", "source_first_known_utc"}, {"margin_note"}, "observation.item")
        item_id = _string(item["id"], "observation.id")
        if item_id in seen_items:
            _fail("duplicate observation identity")
        seen_items.add(item_id)
        _string(item["value_state"], "observation.value_state")
        if type(item["settled"]) is not bool:
            _fail("settled must be boolean")
        known = item["source_first_known_utc"]
        if status == "SCENARIO_ONLY" and (known is None or not item["settled"]):
            _fail("supported scenario cannot depend on unknown-time or unsettled observation")
        if known is not None:
            known_time = _ts(known, "source_first_known_utc")
            if known_time > as_of:
                _fail("source was not knowable by observation as_of")
            if known_time > cutoff:
                _fail("source was not knowable by cutoff")
        if item.get("margin_note") is not None:
            _string(item["margin_note"], "margin_note")

    families = v["hypothesis_families"]
    if not isinstance(families, list) or not families:
        _fail("hypothesis_families must be nonempty")
    seen_families: set[str] = set()
    for family in families:
        family = _obj(family, "family")
        _keys(family,
              {"family_id", "clock", "asset_id", "horizon", "scenarios", "invalidation", "falsifier_dates", "probability", "evidence_quality", "source_available"},
              {"contradiction_policy"}, "family")
        family_id = _string(family["family_id"], "family_id")
        if family_id in seen_families:
            _fail("duplicate family_id")
        seen_families.add(family_id)
        if family["clock"] not in CLOCKS or family["asset_id"] not in ASSETS or family["horizon"] not in HORIZONS:
            _fail("unsupported clock/asset/horizon")
        if family["probability"] is not None:
            _fail("no calibrated probabilities in candidate contract")
        if family["evidence_quality"] not in {"UNKNOWN", "LOW", "MEDIUM", "HIGH"}:
            _fail("invalid evidence_quality")
        if type(family["source_available"]) is not bool:
            _fail("source_available must be bool")
        if (status == "UNAVAILABLE" and family["source_available"]) or (status in {"ABSTAIN", "SCENARIO_ONLY"} and not family["source_available"]):
            _fail("inconsistent source availability and status")
        if family.get("contradiction_policy") is not None:
            _string(family["contradiction_policy"], "contradiction_policy")
        scenario_rows = family["scenarios"]
        if not isinstance(scenario_rows, list) or not (1 <= len(scenario_rows) <= 3):
            _fail("scenarios: 1 to 3 rows required")
        labels: set[str] = set()
        for row in scenario_rows:
            row = _obj(row, "scenario")
            _keys(row, {"scenario", "window_start_utc", "window_end_utc", "price_band_low", "price_band_high", "confirmation"}, set(), "scenario")
            label = row["scenario"]
            if label not in {"BASE", "DOWNSIDE", "UPSIDE"} or label in labels:
                _fail("scenario label invalid/duplicate")
            labels.add(label)
            start, end = _ts(row["window_start_utc"], "window_start_utc"), _ts(row["window_end_utc"], "window_end_utc")
            if start < issued or end <= start:
                _fail("scenario window must be future and strictly ordered")
            low, high = row["price_band_low"], row["price_band_high"]
            if (low is None) != (high is None):
                _fail("price band must be both present or both absent")
            if low is not None:
                if family["asset_id"] == "ROTATION_ENVIRONMENT" or status != "SCENARIO_ONLY":
                    _fail("unsupported prices in abstract/abstaining scenario")
                _price(low, "price_band_low")
                _price(high, "price_band_high")
                if low > high:
                    _fail("inverted price band")
            _strings(row["confirmation"], "confirmation")
        inval = family["invalidation"]
        if not isinstance(inval, list):
            _fail("invalidation must be array")
        if status == "SCENARIO_ONLY" and not inval:
            _fail("supported scenarios need explicit invalidation")
        for inv in inval:
            inv = _obj(inv, "invalidation")
            _keys(inv, {"rule", "settled_only"}, set(), "invalidation")
            _string(inv["rule"], "invalidation.rule")
            if inv["settled_only"] is not True:
                _fail("invalidation must be settled-only")
        falsifiers = family["falsifier_dates"]
        if not isinstance(falsifiers, list):
            _fail("falsifier_dates must be array")
        if status == "SCENARIO_ONLY" and not falsifiers:
            _fail("supported scenarios need dated falsifier")
        for falsifier in falsifiers:
            f = _obj(falsifier, "falsifier")
            _keys(f, {"date_utc", "test", "derived_from"}, set(), "falsifier")
            if _ts(f["date_utc"], "falsifier.date_utc") < issued:
                _fail("falsifier cannot predate issued forecast")
            _string(f["test"], "falsifier.test")
            if f["derived_from"] not in {"SOURCE_OWN_CLOCK", "PREREGISTERED_BY_OWNER", "HISTORICAL_INTERVAL_DESCRIPTIVE"}:
                _fail("falsifier provenance unsupported")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate shadow-only long-range candidate JSON; no writes or model calls")
    parser.add_argument("scenario", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.scenario.read_text(encoding="utf-8"), parse_constant=lambda x: _fail("nonfinite JSON constant"))
    validate_candidate(payload)
    print(json.dumps({"status": "PASS", "authority": "SHADOW_SCENARIO_ONLY", "forecast_id": payload["frozen_issue"]["forecast_id"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
