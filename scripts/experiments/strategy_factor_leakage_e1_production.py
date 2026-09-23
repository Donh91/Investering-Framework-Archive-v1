#!/usr/bin/env python3
"""E1X - production temporal-integrity kill test.

Extends the existing AT-E1 owner ``strategy_factor_leakage_e1.py`` (which proves the
right/left-truncation detector on toy trailing features only) to REAL production
computations. It creates no signal engine, no canonical source and no market
semantics. It only re-executes existing production functions on point-in-time
views of their own inputs and compares the results.

Invariant under test
--------------------
For every output the producer claims is available at time ``t``, recomputing the
producer with every input record whose *knowledge time* is after ``t`` physically
removed (or, for records a label legitimately needs, value-poisoned) must yield the
same value.

The single most important design rule, learned in this audit: truncation must be
keyed by KNOWLEDGE time (when the value could have been known), never by the
record's label time (candle open, period start, period end). A detector that
truncates by label time is blind to publication-lag and incomplete-bar leaks.

Separately, left-truncation / warm-up convergence measures how much a recursive or
start-anchored output at a fixed target depends on how much history precedes it.

Classification vocabulary (never collapsed):
TRUE_FUTURE_LEAKAGE, INSUFFICIENT_WARMUP, RECURSIVE_CONVERGENCE_DRIFT,
EXPECTED_CROSS_SECTIONAL_DIFFERENCE, SOURCE_VINTAGE_RISK, NONDETERMINISM, NO_ISSUE.
Anything that could not be executed is NOT_RUN / UNKNOWN, never PASS.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import csv
import hashlib
import importlib.util
import io
import json
import math
import os
import random
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

REPO = Path(__file__).resolve().parents[2]
for _p in (REPO, REPO / "scripts", REPO / "scripts" / "experiments", REPO / "scripts" / "research"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import strategy_factor_leakage_e1 as e1  # noqa: E402  (existing owner; reused, not duplicated)

UTC = timezone.utc
CONTRACT = "AUTO_TRADING_E1X_PRODUCTION_TEMPORAL_INTEGRITY_v1"
EXPERIMENT_ID = "AT-E1X-0001"
PARENT_EXPERIMENT_ID = e1.EXPERIMENT_ID
CLASSES = (
    "TRUE_FUTURE_LEAKAGE",
    "INSUFFICIENT_WARMUP",
    "RECURSIVE_CONVERGENCE_DRIFT",
    "EXPECTED_CROSS_SECTIONAL_DIFFERENCE",
    "SOURCE_VINTAGE_RISK",
    "NONDETERMINISM",
    "NO_ISSUE",
)
ABS_TOL = 1e-9
REL_TOL = 1e-9
MAX_MINIMIZATIONS_PER_CASE = 6
AUTHORITY = {
    "research_only": True,
    "canonical_effect": False,
    "framework_state_change": False,
    "portfolio_execution": False,
    "threshold_change": False,
    "weight_change": False,
    "automatic_promotion": False,
    "historical_rewrite": False,
}


# --------------------------------------------------------------------------- utils
def ts(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise e1.TemporalIntegrityError("AMBIGUOUS_TIMESTAMP_TIMEZONE_REQUIRED")
        return value.astimezone(UTC)
    return e1.parse_timestamp(value)


def iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=_json_default) + "\n").encode()


def sha(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return iso(value)
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    raise TypeError(type(value).__name__)


_MODULE_CACHE: dict[str, Any] = {}


def load_module(name: str, relative_path: str):
    """Load a production module from its file path exactly once (registered for dataclasses)."""
    if name in _MODULE_CACHE:
        return _MODULE_CACHE[name]
    path = REPO / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    _MODULE_CACHE[name] = module
    return module


@contextlib.contextmanager
def patched(module: Any, **attributes: Any):
    """Temporarily rebind module globals (paths, loaders) and always restore them."""
    missing = object()
    saved = {k: getattr(module, k, missing) for k in attributes}
    for k, v in attributes.items():
        setattr(module, k, v)
    try:
        yield module
    finally:
        for k, v in saved.items():
            if v is missing:
                delattr(module, k)
            else:
                setattr(module, k, v)


@contextlib.contextmanager
def chdir(path: Path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    if isinstance(value, dict):
        for key in sorted(value):
            out.update(flatten(value[key], f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            out.update(flatten(item, f"{prefix}[{index}]"))
    else:
        out[prefix] = value
    return out


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def values_equal(left: Any, right: Any) -> bool:
    if _is_number(left) and _is_number(right):
        lf, rf = float(left), float(right)
        if math.isnan(lf) and math.isnan(rf):
            return True
        return math.isclose(lf, rf, rel_tol=REL_TOL, abs_tol=ABS_TOL)
    if isinstance(left, datetime) or isinstance(right, datetime):
        return str(left) == str(right)
    return left == right


def delta(left: Any, right: Any) -> float | None:
    if _is_number(left) and _is_number(right) and math.isfinite(float(left)) and math.isfinite(float(right)):
        return float(left) - float(right)
    return None


# --------------------------------------------------------------------------- data model
@dataclass(frozen=True)
class Record:
    """One input observation with its KNOWLEDGE time.

    kind: VALUE (first knowable observation), REVISION (later vintage of an existing
    observation), MEMBERSHIP (universe definition), VINTAGE (whole-file re-publication),
    PRICE / OUTCOME_SOURCE (inputs that a label legitimately needs after t).
    """

    available_at: datetime
    kind: str
    key: str
    payload: Any


@dataclass
class Output:
    claimed_available_at: datetime
    fields: dict[str, Any]


Computation = Callable[[list[Record]], dict[str, Output]]


@dataclass
class RightTruncationCase:
    case_id: str
    owner: str
    production_path: str
    production_callable: str
    description: str
    records: list[Record]
    compute: Computation
    targets: list[datetime] | str = "PER_OUTPUT"
    max_targets: int = 24
    decision_fields: Callable[[str], bool] | None = None
    excluded_field_reason: dict[str, str] = field(default_factory=dict)
    censor_future: Callable[[Record], Record | None] | None = None
    kind_classification: dict[str, str] = field(default_factory=dict)
    downstream: list[str] = field(default_factory=list)
    expected: str | None = None
    notes: list[str] = field(default_factory=list)
    knowledge_time_rule: str = ""
    data_binding: dict[str, Any] = field(default_factory=dict)
    expected_classification: str | None = None


@dataclass
class WarmupCase:
    case_id: str
    owner: str
    production_path: str
    production_callable: str
    description: str
    records: list[Record]
    compute: Computation
    target_keys: list[str]
    warmups: list[int]
    production_history_records: int | None
    numeric_fields: list[str]
    categorical_fields: list[str] = field(default_factory=list)
    tolerance_abs: float = ABS_TOL
    tolerance_rel: float = REL_TOL
    tolerance_reason: str = "floating-point identity"
    downstream: list[str] = field(default_factory=list)
    expected: str | None = None
    notes: list[str] = field(default_factory=list)
    data_binding: dict[str, Any] = field(default_factory=dict)
    start_anchored_fields: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- right truncation
def _default_decision_field(_: str) -> bool:
    return True


def point_in_time_view(case: RightTruncationCase, t: datetime, keep_first_future: int = 0) -> list[Record]:
    ordered = sorted(case.records, key=lambda r: (r.available_at, r.key, r.kind))
    base = [r for r in ordered if r.available_at <= t]
    future = [r for r in ordered if r.available_at > t]
    kept = future[:keep_first_future]
    rest = future[keep_first_future:]
    censored: list[Record] = []
    if case.censor_future is not None:
        for record in rest:
            replacement = case.censor_future(record)
            if replacement is not None:
                censored.append(replacement)
    return base + kept + censored


def _compare_outputs(case: RightTruncationCase, full: Output, trunc: Output | None) -> list[dict[str, Any]]:
    keep = case.decision_fields or _default_decision_field
    if trunc is None:
        return [{"field": "__OUTPUT__", "full": "PRESENT", "truncated": "MISSING_IN_TRUNCATED", "delta": None}]
    full_flat = {k: v for k, v in flatten(full.fields).items() if keep(k)}
    trunc_flat = {k: v for k, v in flatten(trunc.fields).items() if keep(k)}
    diffs = []
    for name in sorted(set(full_flat) | set(trunc_flat)):
        left, right = full_flat.get(name, "__ABSENT__"), trunc_flat.get(name, "__ABSENT__")
        if not values_equal(left, right):
            diffs.append({"field": name, "full": left, "truncated": right, "delta": delta(left, right)})
    return diffs


def _minimize(case: RightTruncationCase, key: str, t: datetime, reference: Output | None) -> dict[str, Any]:
    ordered = sorted(case.records, key=lambda r: (r.available_at, r.key, r.kind))
    future = [r for r in ordered if r.available_at > t]

    def changed(k: int) -> bool:
        out = case.compute(point_in_time_view(case, t, keep_first_future=k)).get(key)
        if reference is None:
            return out is not None
        if out is None:
            return True
        return bool(_compare_outputs(case, out, reference))

    if not future:
        return {"status": "NO_FUTURE_RECORDS"}
    if not changed(len(future)):
        return {"status": "NOT_REPRODUCED_WITH_ALL_FUTURE"}
    lo, hi = 0, 1
    while hi < len(future) and not changed(hi):
        lo, hi = hi, min(len(future), hi * 2)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if changed(mid):
            hi = mid
        else:
            lo = mid
    culprit = future[hi - 1]
    return {
        "status": "MINIMIZED",
        "minimal_future_suffix_records": hi,
        "search": "exponential_then_binary_first_change",
        "first_contaminating_record": {
            "key": culprit.key,
            "kind": culprit.kind,
            "available_at_utc": iso(culprit.available_at),
            "lead_after_target_seconds": int((culprit.available_at - t).total_seconds()),
        },
    }


def _targets(case: RightTruncationCase, full: dict[str, Output]) -> list[datetime]:
    if isinstance(case.targets, list):
        return sorted(set(case.targets))
    claimed = sorted({out.claimed_available_at for out in full.values()})
    if len(claimed) <= case.max_targets:
        return claimed
    step = (len(claimed) - 1) / float(case.max_targets - 1)
    return sorted({claimed[round(i * step)] for i in range(case.max_targets)})


def classify_mismatch(case: RightTruncationCase, minimization: dict[str, Any]) -> str:
    culprit = minimization.get("first_contaminating_record") or {}
    kind = culprit.get("kind")
    if kind in case.kind_classification:
        return case.kind_classification[kind]
    if kind in ("REVISION", "VINTAGE"):
        return "SOURCE_VINTAGE_RISK"
    return "TRUE_FUTURE_LEAKAGE"


def run_right_truncation(case: RightTruncationCase) -> dict[str, Any]:
    full = case.compute(list(case.records))
    nondeterministic_set: set[str] = set()
    for _ in range(2):  # identical input, repeated: any difference is NONDETERMINISM
        repeat = case.compute(list(case.records))
        nondeterministic_set |= {
            key for key in set(full) | set(repeat)
            if key not in full or key not in repeat or _compare_outputs(case, full[key], repeat[key])
        }
    nondeterministic = sorted(nondeterministic_set)
    targets = _targets(case, full)
    mismatches: list[dict[str, Any]] = []
    compared = 0
    for t in targets:
        view = case.compute(point_in_time_view(case, t))
        for key, out in sorted(full.items()):
            if out.claimed_available_at > t:
                continue
            if isinstance(case.targets, str) and out.claimed_available_at != t:
                continue
            compared += 1
            diffs = _compare_outputs(case, out, view.get(key))
            if diffs:
                mismatches.append({"target_utc": iso(t), "output_key": key,
                                   "claimed_available_at_utc": iso(out.claimed_available_at),
                                   "field_differences": diffs[:12], "field_difference_count": len(diffs),
                                   "_t": t, "_trunc": view.get(key)})
    # Attribution: a mismatch on an output that is not even reproducible run-to-run is
    # NONDETERMINISM, never leakage. Otherwise minimise the first mismatch of each distinct
    # target first (diversity), then the rest, within budget. Unminimised mismatches are
    # counted but never classified by assumption.
    # If the computation is not reproducible on identical input, no truncation difference
    # in this case can be attributed to future data: every mismatch is NONDETERMINISM.
    nondet_case = bool(nondeterministic)
    order = []
    seen_targets: set[str] = set()
    for index, item in enumerate(mismatches):
        if item["target_utc"] not in seen_targets:
            seen_targets.add(item["target_utc"])
            order.append(index)
    order += [i for i in range(len(mismatches)) if i not in set(order)]
    minimized = 0
    for index in order:
        item = mismatches[index]
        if nondet_case:
            item["minimization"] = {"status": "SKIPPED_NONDETERMINISTIC_COMPUTATION"}
            item["classification"] = "NONDETERMINISM"
            continue
        if minimized >= MAX_MINIMIZATIONS_PER_CASE:
            item["minimization"] = {"status": "NOT_RUN_BUDGET"}
            item["classification"] = "NOT_MINIMIZED"
            continue
        item["minimization"] = _minimize(case, item["output_key"], item["_t"], item["_trunc"])
        item["classification"] = classify_mismatch(case, item["minimization"])
        minimized += 1
    for item in mismatches:
        item.pop("_t", None)
        item.pop("_trunc", None)
    classes = sorted({m["classification"] for m in mismatches} - {"NOT_MINIMIZED"})
    if nondeterministic:
        classes = sorted(set(classes) | {"NONDETERMINISM"})
    lead_seconds = [m["minimization"]["first_contaminating_record"]["lead_after_target_seconds"]
                    for m in mismatches if m.get("minimization", {}).get("status") == "MINIMIZED"]
    if mismatches or nondeterministic:
        observed = "FAIL"
    elif compared == 0:
        observed = "NOT_RUN"  # nothing was compared: never PASS
        classes = ["UNKNOWN"]
    else:
        observed = "PASS"
    return {
        "case_id": case.case_id,
        "test": "RIGHT_TRUNCATION_INVARIANCE",
        "owner": case.owner,
        "production_path": case.production_path,
        "production_callable": case.production_callable,
        "description": case.description,
        "knowledge_time_rule": case.knowledge_time_rule,
        "records": len(case.records),
        "record_kinds": dict(sorted(_count(r.kind for r in case.records).items())),
        "outputs_full": len(full),
        "targets_tested": len(targets),
        "output_comparisons": compared,
        "mismatch_count": len(mismatches),
        "minimized_mismatch_count": len(lead_seconds),
        "unminimized_mismatch_count": sum(1 for m in mismatches if m["classification"] == "NOT_MINIMIZED"),
        "contaminating_lead_seconds": {"min": min(lead_seconds), "max": max(lead_seconds)} if lead_seconds else None,
        "mismatches": [mismatches[i] for i in order][:40],
        "nondeterministic_outputs": nondeterministic[:20],
        "observed": observed,
        "classifications": classes or ["NO_ISSUE"],
        "expected": case.expected,
        "expected_classification": case.expected_classification,
        "expectation_met": None if case.expected is None else (
            case.expected == observed and (case.expected_classification is None or classes == [case.expected_classification])),
        "excluded_fields": case.excluded_field_reason,
        "downstream": case.downstream,
        "notes": case.notes,
        "data_binding": case.data_binding,
    }


def _count(items: Iterable[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for item in items:
        out[item] = out.get(item, 0) + 1
    return out


# --------------------------------------------------------------------------- warm-up
def run_warmup(case: WarmupCase) -> dict[str, Any]:
    ordered = sorted(case.records, key=lambda r: (r.available_at, r.key))
    reference_all = case.compute(ordered)
    rows = []
    for key in case.target_keys:
        if key not in reference_all:
            rows.append({"target_key": key, "status": "TARGET_NOT_PRODUCED"})
            continue
        t = reference_all[key].claimed_available_at
        history = [r for r in ordered if r.available_at <= t]
        reference = case.compute(history)[key]
        ref_flat = flatten(reference.fields)
        per_w = []
        for w in sorted(case.warmups):
            if w >= len(history):
                continue
            sub = history[len(history) - w - 1:] if w + 1 <= len(history) else history
            out = case.compute(sub).get(key)
            if out is None:
                per_w.append({"warmup_records": w, "status": "NOT_PRODUCED"})
                continue
            flat = flatten(out.fields)
            numeric = {}
            for f in case.numeric_fields:
                a, b = flat.get(f), ref_flat.get(f)
                d = delta(a, b)
                rel = None if d is None or not b else abs(d) / abs(float(b))
                if a is None and b is None:
                    status = "EQUAL"
                elif a is None:
                    status = "NULL_INSUFFICIENT_HISTORY"  # honest fail-closed null, not a wrong value
                elif d is not None and (abs(d) <= case.tolerance_abs or (rel is not None and rel <= case.tolerance_rel)):
                    status = "EQUAL"
                else:
                    status = "DRIFT"
                numeric[f] = {"value": a, "reference": b, "abs_delta": None if d is None else abs(d), "rel_delta": rel, "status": status}
            categorical = {}
            for f in case.categorical_fields:
                a, b = flat.get(f), ref_flat.get(f)
                status = "EQUAL" if a == b else ("NULL_INSUFFICIENT_HISTORY" if a is None else "DRIFT")
                categorical[f] = {"value": a, "reference": b, "status": status}
            statuses = [v["status"] for v in numeric.values()] + [v["status"] for v in categorical.values()]
            per_w.append({"warmup_records": w, "converged": all(s == "EQUAL" for s in statuses),
                          "drift": any(s == "DRIFT" for s in statuses), "numeric": numeric, "categorical": categorical})
        converged_from = None
        for index in range(len(per_w)):
            if all(item.get("converged") for item in per_w[index:]):
                converged_from = per_w[index]["warmup_records"]
                break
        rows.append({"target_key": key, "target_claimed_available_at_utc": iso(t), "reference_history_records": len(history) - 1,
                     "per_warmup": per_w, "converged_from_warmup_records": converged_from})
    needed = [row.get("converged_from_warmup_records") for row in rows if "per_warmup" in row]
    worst = None if not needed or any(n is None for n in needed) else max(needed)
    categorical_flips = sum(1 for row in rows for item in row.get("per_warmup", []) for v in item.get("categorical", {}).values() if v["status"] == "DRIFT")
    max_rel = {}
    for row in rows:
        for item in row.get("per_warmup", []):
            for f, v in item.get("numeric", {}).items():
                w = item["warmup_records"]
                if v["rel_delta"] is not None:
                    max_rel.setdefault(f, {}).setdefault(w, 0.0)
                    max_rel[f][w] = max(max_rel[f][w], v["rel_delta"])
    any_drift = any(item.get("drift", False) for row in rows for item in row.get("per_warmup", []))
    drift_at_production = None
    if case.production_history_records is not None:
        drift_at_production = any(
            item.get("drift", False)
            for row in rows for item in row.get("per_warmup", [])
            if item["warmup_records"] <= case.production_history_records
            and not any(o["warmup_records"] <= case.production_history_records and o["warmup_records"] > item["warmup_records"] for o in row.get("per_warmup", []))
        )
    if not any_drift:
        classification = "NO_ISSUE"
    elif worst is None:
        classification = "INSUFFICIENT_WARMUP"
    elif case.production_history_records is not None and case.production_history_records < worst:
        classification = "INSUFFICIENT_WARMUP"
    else:
        classification = "RECURSIVE_CONVERGENCE_DRIFT"
    observed = "DRIFT_DETECTED" if any_drift else "NO_DRIFT"
    return {
        "case_id": case.case_id,
        "test": "LEFT_TRUNCATION_WARMUP_CONVERGENCE",
        "owner": case.owner,
        "production_path": case.production_path,
        "production_callable": case.production_callable,
        "description": case.description,
        "warmups_tested": sorted(case.warmups),
        "production_history_records": case.production_history_records,
        "tolerance": {"abs": case.tolerance_abs, "rel": case.tolerance_rel, "reason": case.tolerance_reason},
        "targets": rows,
        "worst_case_converged_from_warmup_records": worst,
        "categorical_flip_count": categorical_flips,
        "drift_at_production_history": drift_at_production,
        "max_rel_delta_by_field_and_warmup": {f: {str(w): v for w, v in sorted(ws.items())} for f, ws in sorted(max_rel.items())},
        "start_anchored_fields": case.start_anchored_fields,
        "observed": observed,
        "classification": classification,
        "expected": case.expected,
        "expectation_met": None if case.expected is None else case.expected == classification,
        "downstream": case.downstream,
        "notes": case.notes,
        "data_binding": case.data_binding,
    }


# =========================================================================== loaders
H1 = timedelta(hours=1)
H4 = timedelta(hours=4)
D1 = timedelta(days=1)
HOURLY_ROOT = "03_DAILY_CAPTURE_LOGS/hourly"
CAPTURE_ROOT = "03_DAILY_CAPTURE_LOGS/captures"
CG_MONTHLY = "03_DAILY_CAPTURE_LOGS/slow_cycle/copper_gold/normalized/monthly_observations.csv"
CG_FEATURES = "03_DAILY_CAPTURE_LOGS/slow_cycle/copper_gold/derived/settled_2m_features.csv"
CG_REVISIONS = "03_DAILY_CAPTURE_LOGS/slow_cycle/copper_gold/revisions"
ETF_PACK = "04_MARKET_LEARNING/truth_layer/etf_flows/2026-07-26__us-spot-crypto-etf-flow-history"
ETF_FEATURE_SCRIPT = ETF_PACK + "/scripts/build_etf_flow_features.py"
PULLBACK_OBS = "04_MARKET_LEARNING/pullback_learning/observations"
BTCD_LATEST = "03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv"
EVENT_STUDY = "research/experiments/copper_gold_slow_cycle_shadow_v1/HISTORICAL_EVENT_STUDY_v2.json"


def _files_binding(paths: list[Path]) -> dict[str, Any]:
    return {"file_count": len(paths), "files_sha256_digest": sha([[p.relative_to(REPO).as_posix(), sha_file(p)] for p in paths])}


def load_hourly_rows(repo: Path = REPO) -> tuple[list[dict[str, str]], dict[str, Any]]:
    files = sorted((repo / HOURLY_ROOT).glob("20??/??/*.csv"))
    rows: dict[str, dict[str, str]] = {}
    for path in files:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                if row.get("spot_status") != "PASS" or not row.get("btc_close") or not row.get("eth_close"):
                    continue
                rows[row["timestamp_utc"]] = row
    ordered = [rows[key] for key in sorted(rows)]
    return ordered, {"path_glob": HOURLY_ROOT + "/20??/??/*.csv", **_files_binding(files), "rows": len(ordered)}


def hourly_records(rows: list[dict[str, str]]) -> list[Record]:
    """Completed 1h candle labelled by its OPEN time is knowable at open + 1h."""
    return [Record(ts(r["timestamp_utc"]) + H1, "VALUE", r["timestamp_utc"], r) for r in rows]


def us_session_close_utc(day: date) -> datetime:
    from zoneinfo import ZoneInfo
    return datetime(day.year, day.month, day.day, 16, 0, tzinfo=ZoneInfo("America/New_York")).astimezone(UTC)


def load_etf_pack(asset: str, repo: Path = REPO) -> tuple[list[dict[str, str]], dict[str, Any]]:
    files = sorted((repo / ETF_PACK / "data").glob(f"us_spot_{asset}_etf_flows_daily_*.csv"))
    rows: list[dict[str, str]] = []
    for path in files:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows.extend(csv.DictReader(handle))
    rows.sort(key=lambda r: r["date"])
    return rows, {"path": ETF_PACK + f"/data/us_spot_{asset}_etf_flows_daily_*.csv", **_files_binding(files), "rows": len(rows),
                  "malformed_rows_excluded_by_backtest_adapter": etf_malformed(rows),
                  "nyse_closed_dates_present_as_rows_not_excluded": etf_non_session_rows(rows)}


# Documented Farside timing evidence already in the repository (not inferred):
#  - DATA_PING_V5_20260717T034148Z accepted BTC 2026-07-16 total 45.7 with IBIT NOT_REPORTED;
#  - 02_DATA_PING/.../2026-07-17T063400Z__farside-post-acceptance-source-revision.json
#    verified the completed row (IBIT 33.4, total 79.1) at 2026-07-17T06:34:00Z.
FARSIDE_EVIDENCE = {
    "session": "2026-07-16",
    "provisional_seen_at_utc": "2026-07-17T03:41:48Z",
    "provisional_total_usd_m": 45.7,
    "provisional_missing_fund": "IBIT",
    "final_verified_at_utc": "2026-07-17T06:34:00Z",
    "final_total_usd_m": 79.1,
    "evidence_paths": [
        "02_DATA_PING/operational_handoffs/accepted_logs/supplements/2026-07-17T063400Z__farside-post-acceptance-source-revision.json",
        ETF_PACK + "/README.md",
    ],
}


# =========================================================================== production RT cases
def _w30():
    import backtest_engine.w30_replay as w30  # production package import (relative imports inside)
    return w30


VOL_FIELDS = ("log_return_1h", "realized_vol_24h_annualized", "realized_vol_72h_annualized", "running_high_close", "drawdown_from_running_high")


def compute_backtest_hourly_volatility(records: list[Record], close_transform: Callable[[list[float]], list[float]] | None = None) -> dict[str, Output]:
    w30 = _w30()
    ordered = sorted(records, key=lambda r: r.payload["timestamp_utc"])
    out: dict[str, Output] = {}
    for asset in ("BTC", "ETH"):
        closes = [float(r.payload[f"{asset.lower()}_close"]) for r in ordered]
        if close_transform is not None:
            closes = close_transform(closes)
        src = [{"timestamp_utc": r.payload["timestamp_utc"], "close": c, "settled": "True"}
               for r, c in zip(ordered, closes) if c is not None]
        for row in w30.build_hourly_volatility(src, asset):
            out[f"{asset}|{iso(ts(row['timestamp_utc']))}"] = Output(ts(row["timestamp_utc"]) + H1, {k: row[k] for k in VOL_FIELDS})
    return out


def case_backtest_hourly_volatility(rows, binding) -> RightTruncationCase:
    return RightTruncationCase(
        case_id="RT-A01-BACKTEST-HOURLY-VOLATILITY",
        owner="backtest_engine (FRAMEWORK_BACKTEST_READINESS_BUILD_v1)",
        production_path="backtest_engine/w30_replay.py",
        production_callable="build_hourly_volatility",
        description="Hourly log return, 24h/72h realized vol, running high and drawdown on the real public hourly archive.",
        records=hourly_records(rows), compute=compute_backtest_hourly_volatility,
        knowledge_time_rule="completed 1h candle labelled by open time is knowable at open+1h",
        downstream=["backtest_engine W30 golden replay", "run-engineering-gates"], expected="PASS",
        data_binding=binding)


def compute_backtest_daily_utc(records: list[Record]) -> dict[str, Output]:
    w30 = _w30()
    ordered = sorted(records, key=lambda r: r.payload["timestamp_utc"])
    out: dict[str, Output] = {}
    for asset in ("BTC", "ETH"):
        p = asset.lower()
        src = [{"timestamp_utc": r.payload["timestamp_utc"], "open": r.payload[f"{p}_open"], "high": r.payload[f"{p}_high"],
                "low": r.payload[f"{p}_low"], "close": r.payload[f"{p}_close"], "volume_contracts": r.payload.get(f"{p}_volume") or "0",
                "volume_coin": r.payload.get(f"{p}_volume") or "0", "volume_quote_usd": r.payload.get(f"{p}_quote_volume") or "0",
                "settled": "True"} for r in ordered]
        for row in w30.build_daily_utc(src, asset):
            day = date.fromisoformat(row["date_utc"])
            claimed = datetime(day.year, day.month, day.day, tzinfo=UTC) + D1
            out[f"{asset}|{row['date_utc']}"] = Output(claimed, {k: row[k] for k in ("open", "high", "low", "close", "volume_asset", "quote_volume_usd", "settled_hour_count", "day_complete_24h")})
    return out


def case_backtest_daily_utc(rows, binding) -> RightTruncationCase:
    return RightTruncationCase(
        case_id="RT-A02-BACKTEST-DAILY-UTC-AGGREGATION",
        owner="backtest_engine (FRAMEWORK_BACKTEST_READINESS_BUILD_v1)",
        production_path="backtest_engine/w30_replay.py",
        production_callable="build_daily_utc",
        description="UTC daily OHLC aggregation from settled hourly candles; a day row is claimed at the following 00:00Z.",
        records=hourly_records(rows), compute=compute_backtest_daily_utc,
        knowledge_time_rule="daily row knowable at date+1 00:00Z (last hourly candle closes then)",
        downstream=["backtest_engine W30 golden replay"], expected="PASS", data_binding=binding)


def _etf_row(asset: str, raw: dict[str, str]) -> dict[str, Any]:
    day = date.fromisoformat(raw["date"])
    close = us_session_close_utc(day)
    row = {k: v for k, v in raw.items() if k not in ("date", "Total")}
    row.update({"date": raw["date"], "total_usd_millions": raw["Total"], "not_before_session_close_utc": iso(close),
                "publication_timestamp_verified": "False", "asset": asset, "source": "FARSIDE_HISTORY_PACK_2026_07_26",
                "method_id": "E1X_ADAPTER"})
    return row


def compute_backtest_etf_trailing(records: list[Record]) -> dict[str, Output]:
    w30 = _w30()
    latest: dict[str, Record] = {}
    for record in sorted(records, key=lambda r: (r.available_at, r.kind)):
        latest[record.key] = record  # later vintage of the same session supersedes earlier
    out: dict[str, Output] = {}
    by_asset: dict[str, list[dict[str, Any]]] = {}
    for record in latest.values():
        by_asset.setdefault(record.payload["asset"], []).append(record.payload)
    for asset, rows in by_asset.items():
        rows.sort(key=lambda r: r["date"])
        for row in w30.build_etf_trailing(rows, asset):
            fields = {k: v for k, v in row.items() if k not in ("asset", "date", "not_before_session_close_utc", "feature_knowledge_available_at_utc", "feature_method_id")}
            out[f"{asset}|{row['date']}"] = Output(ts(row["feature_knowledge_available_at_utc"]), fields)
    return out


NYSE_CLOSED_2024_2026 = frozenset({
    "2024-01-15", "2024-02-19", "2024-03-29", "2024-05-27", "2024-06-19", "2024-07-04", "2024-09-02", "2024-11-28", "2024-12-25",
    "2025-01-01", "2025-01-09", "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26", "2025-06-19", "2025-07-04", "2025-09-01",
    "2025-11-27", "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25", "2026-06-19", "2026-07-03",
})


def etf_non_session_rows(raw_rows: list[dict[str, str]]) -> list[str]:
    """Rows dated on NYSE full closures: not trading sessions, recorded as flows."""
    return [r["date"] for r in raw_rows if r["date"] in NYSE_CLOSED_2024_2026]


def etf_malformed(raw_rows: list[dict[str, str]]) -> list[str]:
    """Rows whose field count is short by one (Total missing, fund columns shifted). Excluded, never repaired."""
    return [r["date"] for r in raw_rows if r.get("Total") in (None, "")]


def etf_records(asset: str, raw_rows: list[dict[str, str]], with_farside_evidence: bool) -> list[Record]:
    records = []
    malformed = set(etf_malformed(raw_rows))
    for raw in raw_rows:
        if raw["date"] in malformed:
            continue
        row = _etf_row(asset, raw)
        key = f"{asset}|{raw['date']}"
        if with_farside_evidence and asset == "BTC" and raw["date"] == FARSIDE_EVIDENCE["session"]:
            provisional = dict(row)
            provisional[FARSIDE_EVIDENCE["provisional_missing_fund"]] = ""
            provisional["total_usd_millions"] = str(FARSIDE_EVIDENCE["provisional_total_usd_m"])
            records.append(Record(ts(FARSIDE_EVIDENCE["provisional_seen_at_utc"]), "VALUE", key, provisional))
            records.append(Record(ts(FARSIDE_EVIDENCE["final_verified_at_utc"]), "REVISION", key, row))
        else:
            records.append(Record(ts(row["not_before_session_close_utc"]), "VALUE", key, row))
    return records


def case_backtest_etf_trailing_claimed(asset_rows, binding) -> RightTruncationCase:
    records = [r for asset, rows in asset_rows.items() for r in etf_records(asset, rows, False)]
    return RightTruncationCase(
        case_id="RT-A03a-BACKTEST-ETF-TRAILING-CLAIMED-KNOWLEDGE",
        owner="backtest_engine (FRAMEWORK_BACKTEST_READINESS_BUILD_v1)",
        production_path="backtest_engine/w30_replay.py", production_callable="build_etf_trailing",
        description="ETF trailing features with knowledge time taken exactly as claimed (not_before_session_close_utc).",
        records=records, compute=compute_backtest_etf_trailing,
        knowledge_time_rule="as claimed by the producer: feature_knowledge_available_at_utc = not_before_session_close_utc",
        downstream=["backtest_engine W30 replay", "ETF flow-leg research using the 2026-07-26 history pack"],
        expected="PASS", data_binding=binding)


def case_backtest_etf_trailing_documented_publication(asset_rows, binding) -> RightTruncationCase:
    records = [r for asset, rows in asset_rows.items() for r in etf_records(asset, rows, True)]
    t_claim = us_session_close_utc(date.fromisoformat(FARSIDE_EVIDENCE["session"]))
    return RightTruncationCase(
        case_id="RT-A03b-BACKTEST-ETF-TRAILING-DOCUMENTED-FARSIDE-TIMING",
        owner="backtest_engine (FRAMEWORK_BACKTEST_READINESS_BUILD_v1) + truth_layer ETF history pack",
        production_path="backtest_engine/w30_replay.py", production_callable="build_etf_trailing",
        description="Same production function, but the one session with in-repo publication evidence (BTC 2026-07-16) carries its documented provisional and completed vintages.",
        records=records, compute=compute_backtest_etf_trailing,
        targets=[t_claim, ts("2026-07-17T05:00:00Z"), ts("2026-07-17T12:00:00Z")],
        knowledge_time_rule="documented: provisional row seen 2026-07-17T03:41:48Z, completed row verified 2026-07-17T06:34:00Z; all other sessions as claimed (UNKNOWN actual publication)",
        downstream=["backtest_engine W30 replay", "Stage-1 ETF flow leg (3 consecutive positive sessions with IBIT positive)", "ETF flow-leg research"],
        expected="FAIL", data_binding={**binding, "farside_evidence": FARSIDE_EVIDENCE},
        notes=["Only one session in the pack has publication-time evidence; every other session's true publication time is UNKNOWN and is not guessed."])


def compute_truth_layer_etf_features(records: list[Record]) -> dict[str, Output]:
    mod = load_module("e1x_etf_feature_builder", ETF_FEATURE_SCRIPT)
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        (root / "data").mkdir()
        grouped: dict[tuple[str, str], list[dict[str, str]]] = {}
        latest: dict[str, Record] = {}
        for record in sorted(records, key=lambda r: (r.available_at, r.kind)):
            latest[record.key] = record
        for record in latest.values():
            asset, raw = record.payload
            grouped.setdefault((asset, raw["date"][:4]), []).append(raw)
        for (asset, year), rows in grouped.items():
            rows.sort(key=lambda r: r["date"])
            with (root / "data" / f"us_spot_{asset.lower()}_etf_flows_daily_{year}.csv").open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
        # The script requires a partition per asset. Before an asset's first session the
        # point-in-time partition is a header-only file (zero rows), never invented data.
        for asset, header in ETF_HEADERS.items():
            if not any(a == asset for a, _ in grouped):
                with (root / "data" / f"us_spot_{asset.lower()}_etf_flows_daily_0000.csv").open("w", newline="") as handle:
                    csv.writer(handle).writerow(header)
        with patched(mod, ROOT=root, DATA=root / "data"):
            mod.main()
        out: dict[str, Output] = {}
        with (root / "generated" / "us_spot_btc_eth_etf_flow_trailing_features.csv").open(newline="") as handle:
            for row in csv.DictReader(handle):
                fields = {}
                for k, v in row.items():
                    if k in ("date", "asset"):
                        continue
                    try:
                        fields[k] = float(v) if v != "" else None
                    except ValueError:
                        fields[k] = v
                out[f"{row['asset']}|{row['date']}"] = Output(us_session_close_utc(date.fromisoformat(row["date"])), fields)
        return out


ETF_HEADERS: dict[str, list[str]] = {}


def case_truth_layer_etf_features(asset_rows, binding) -> RightTruncationCase:
    for asset, rows in asset_rows.items():
        ETF_HEADERS[asset] = [k for k in rows[0].keys()]
    records = []
    for asset, rows in asset_rows.items():
        for raw in rows:
            records.append(Record(us_session_close_utc(date.fromisoformat(raw["date"])), "VALUE", f"{asset}|{raw['date']}", (asset, raw)))
    return RightTruncationCase(
        case_id="RT-A04-TRUTH-LAYER-ETF-FLOW-FEATURES",
        owner="04_MARKET_LEARNING truth_layer ETF flow history",
        production_path=ETF_FEATURE_SCRIPT, production_callable="main (pandas rolling/zscore/streak/cumsum)",
        description="The pack's own feature builder executed end-to-end on point-in-time partitions.",
        records=records, compute=compute_truth_layer_etf_features, max_targets=16,
        knowledge_time_rule="as claimed: AVAILABLE_AFTER_US_SESSION_CLOSE",
        downstream=["us_spot_btc_eth_etf_flow_trailing_features.csv consumers (ETF research)"], expected="PASS",
        data_binding=binding)


def _cg():
    return load_module("e1x_world_bank_copper_gold_owner", "scripts/data_terminal/world_bank_copper_gold_owner.py")


def load_cg_monthly(repo: Path = REPO) -> tuple[list[tuple[str, float, float]], dict[str, Any]]:
    path = repo / CG_MONTHLY
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [(r["period"], float(r["copper_source_value"]), float(r["gold_source_value"])) for r in csv.DictReader(handle)]
    return rows, {"path": CG_MONTHLY, "sha256": sha_file(path), "rows": len(rows)}


CG_MONTHLY_FIELDS = ("ratio", "change_1m_pct", "change_6m_pct", "ma_12m", "ma_24m", "distance_ma_12m_pct", "roc_12m_pct", "rsi_14m_wilder", "zscore_24m_population")
CG_2M_FIELDS = ("ratio_close_proxy", "macd_12_26", "macd_signal_9", "macd_histogram", "rsi_14_wilder", "regime_state")


def compute_cg(records: list[Record], ratio_transform: Callable[[list[dict[str, Any]]], None] | None = None) -> dict[str, Output]:
    cg = _cg()
    latest: dict[str, Record] = {}
    for record in sorted(records, key=lambda r: (r.available_at, r.kind)):
        latest[record.key] = record
    obs = [cg.SourceObservation(*latest[k].payload) for k in sorted(latest)]
    if not obs:
        return {}
    monthly = cg.monthly_features(obs)
    if ratio_transform is not None:
        ratio_transform(monthly)
    out: dict[str, Output] = {}
    for row in monthly:
        out[f"M|{row['period']}"] = Output(ts(row["source_timestamp"]), {k: row.get(k) for k in CG_MONTHLY_FIELDS + ("seeded",) if k in row})
    for anchor, rows in cg.settled_2m_features(monthly).items():
        for row in rows:
            out[f"2M|{anchor}|{row['bar_end_period']}"] = Output(ts(row["bar_end_timestamp"]), {k: row[k] for k in CG_2M_FIELDS})
    return out


def cg_records(rows, availability: Callable[[str], datetime] | None = None) -> list[Record]:
    cg = _cg()
    out = []
    for period, copper, gold in rows:
        when = availability(period) if availability else ts(cg.period_end_iso(period))
        out.append(Record(when, "VALUE", period, (period, copper, gold)))
    return out


def case_copper_gold_owner(rows, binding) -> RightTruncationCase:
    return RightTruncationCase(
        case_id="RT-A05-DATA-TERMINAL-COPPER-GOLD-OWNER",
        owner="data_terminal World Bank Copper/Gold slow-cycle shadow owner",
        production_path="scripts/data_terminal/world_bank_copper_gold_owner.py",
        production_callable="monthly_features + settled_2m_features (MA/ROC/RSI-Wilder/z-score, 2M MACD 12/26/9, regime_state)",
        description="Owner-level causality of every monthly and settled 2M feature, knowledge time as the owner labels it (period end).",
        records=cg_records(rows), compute=compute_cg, max_targets=30,
        knowledge_time_rule="owner label: source_timestamp / bar_end_timestamp = period end 23:59:59Z (see RT-A06 for publication time)",
        downstream=["03_DAILY_CAPTURE_LOGS/slow_cycle/copper_gold/LATEST.json", "settled_2m_features.csv", "copper/gold event study"],
        expected="PASS", data_binding=binding)


# ----------------------------------------------------------------- copper/gold event study (consumer)
def _es():
    return load_module("e1x_copper_gold_event_study", "scripts/research/copper_gold_slow_cycle_event_study.py")


def cg_publication_evidence(repo: Path = REPO) -> dict[str, Any]:
    """Publication dates recorded by the owner itself (workbook 'updated on', date-only lower bound)."""
    evidence = {}
    for path in sorted((repo / CG_REVISIONS).glob("*.json")):
        receipt = json.loads(path.read_text())
        last = receipt["coverage"]["last_period"]
        published = datetime.strptime(receipt["source"]["workbook_updated_on"], "%B %d, %Y").replace(tzinfo=UTC)
        evidence[last] = {"workbook_updated_on_utc_lower_bound": iso(published), "retrieved_at_utc": receipt["retrieved_at_utc"],
                          "receipt": path.relative_to(repo).as_posix()}
    return evidence


def cg_knowledge_time_factory(repo: Path = REPO) -> tuple[Callable[[str], datetime], dict[str, Any]]:
    cg = _cg()
    evidence = cg_publication_evidence(repo)
    lags = []
    for period, item in evidence.items():
        lags.append((ts(item["workbook_updated_on_utc_lower_bound"]) - ts(cg.period_end_iso(period))).total_seconds())
    min_lag = timedelta(seconds=min(lags)) if lags else None

    def knowledge(period: str) -> datetime:
        if period in evidence:
            return ts(evidence[period]["workbook_updated_on_utc_lower_bound"])
        return ts(cg.period_end_iso(period)) + min_lag

    rule = {
        "rule": "documented publication date where the owner recorded one; otherwise period_end + minimum observed publication lag (charitable lower bound, never a guess of the real date)",
        "documented": evidence,
        "minimum_observed_lag_seconds": None if min_lag is None else int(min_lag.total_seconds()),
    }
    return knowledge, rule


def load_btc_coinmetrics(path: Path) -> list[tuple[date, float]]:
    return _es().load_btc(path)


def event_study_records(features_path: Path, btc: list[tuple[date, float]], knowledge: Callable[[str], datetime] | None) -> list[Record]:
    es = _es()
    anchors = es.load_features(features_path)
    records = []
    for anchor, rows in anchors.items():
        for row in rows:
            when = knowledge(row["bar_end_period"]) if knowledge else ts(row["bar_end_timestamp"])
            records.append(Record(when, "VALUE", f"{anchor}|{row['bar_end_period']}", ("FEATURE", anchor, row)))
    for day, price in btc:
        # Coin Metrics PriceUSD for date d is the end-of-day d reference rate.
        records.append(Record(datetime(day.year, day.month, day.day, tzinfo=UTC) + D1, "OUTCOME_SOURCE", f"BTC|{day.isoformat()}", ("BTC", day, price)))
    return records


def poison_outcome_source(record: Record) -> Record | None:
    if record.kind == "OUTCOME_SOURCE":
        tag, day, price = record.payload
        return Record(record.available_at, record.kind, record.key, (tag, day, price * 1.37 + 11.0))
    if record.kind == "PRICE":
        row = dict(record.payload)
        for k in ("open", "high", "low", "close"):
            if k in row:
                row[k] = float(row[k]) * 1.37 + 11.0
        return Record(record.available_at, record.kind, record.key, row)
    return None  # every other future record is physically removed


def compute_event_study(records: list[Record], peak_days: list[date]) -> dict[str, Output]:
    es = _es()
    anchors: dict[str, list[dict[str, Any]]] = {}
    btc: list[tuple[date, float]] = []
    for record in records:
        if record.payload[0] == "FEATURE":
            anchors.setdefault(record.payload[1], []).append(record.payload[2])
        else:
            btc.append((record.payload[1], record.payload[2]))
    for rows in anchors.values():
        rows.sort(key=lambda r: r["bar_end_day"])
    btc.sort()
    out: dict[str, Output] = {}
    for day in peak_days:
        claimed = datetime(day.year, day.month, day.day, tzinfo=UTC) + D1
        for anchor in ("JAN_FEB", "FEB_MAR"):
            state = es.latest_settled_state(anchors.get(anchor, []), day)
            out[f"PEAK|{day.isoformat()}|{anchor}"] = Output(claimed, {"state": state})
    if btc:
        for anchor, rows in sorted(anchors.items()):
            for regime in ("TURNING_NEGATIVE", "TURNING_POSITIVE"):
                for event in es.signal_events(rows, regime, btc):
                    day = date.fromisoformat(event["event_date"])
                    claimed = datetime(day.year, day.month, day.day, tzinfo=UTC) + D1
                    out[f"SIG|{anchor}|{regime}|{event['source_bar_end_period']}"] = Output(claimed, event)
    return out


EVENT_OUTCOME_FIELDS = ("return_60d_pct", "return_120d_pct", "return_240d_pct", "return_365d_pct",
                        "max_drawdown_60d_pct", "max_drawdown_120d_pct", "max_drawdown_240d_pct", "max_drawdown_365d_pct")


def _event_decision_field(name: str) -> bool:
    return not any(name.endswith(f) for f in EVENT_OUTCOME_FIELDS)


def case_event_study(features_path: Path, btc: list[tuple[date, float]], peak_days: list[date], knowledge, rule, binding, claimed_only: bool) -> RightTruncationCase:
    records = event_study_records(features_path, btc, None if claimed_only else knowledge)
    return RightTruncationCase(
        case_id="RT-A06a-RESEARCH-COPPER-GOLD-EVENT-STUDY-CLAIMED-KNOWLEDGE" if claimed_only else "RT-A06b-RESEARCH-COPPER-GOLD-EVENT-STUDY-PUBLICATION-KNOWLEDGE",
        owner="Research Lab copper/gold slow-cycle event study (COPPER_GOLD_SLOW_CYCLE_SHADOW_v1)",
        production_path="scripts/research/copper_gold_slow_cycle_event_study.py",
        production_callable="latest_settled_state + signal_events (as used by build_study)",
        description=("Event study with feature knowledge time as the code assumes (bar end)." if claimed_only else
                     "Event study with feature knowledge time = World Bank publication (owner-recorded dates; otherwise minimum observed lag)."),
        records=records, compute=lambda recs: compute_event_study(recs, peak_days), max_targets=40,
        decision_fields=_event_decision_field, censor_future=poison_outcome_source,
        excluded_field_reason={f: "OUTCOME_LABEL_BY_DESIGN (forward BTC path)" for f in EVENT_OUTCOME_FIELDS},
        knowledge_time_rule="bar_end_timestamp (code assumption)" if claimed_only else json.dumps(rule, sort_keys=True),
        downstream=["research/experiments/copper_gold_slow_cycle_shadow_v1/HISTORICAL_EVENT_STUDY_v2.json",
                    "COPPER_GOLD_SLOW_CYCLE_SHADOW_v1 kill criterion K02", "TDBC / slow-cycle context interpretation"],
        expected="PASS" if claimed_only else "FAIL", data_binding=binding,
        notes=["Future BTC prices are value-poisoned, never removed, because forward returns are declared outcome labels; decision fields (event existence, event_date, entry btc_price, joined state) must not move."])


def event_study_impact(features_path: Path, btc: list[tuple[date, float]], published: dict[str, Any], lags_days: Iterable[int]) -> dict[str, Any]:
    """Re-run the unchanged production signal_events with the production shift_days argument."""
    es = _es()
    anchors = es.load_features(features_path)
    result = {"published_summaries": {a: {k: v["summary"] for k, v in r.items()} for a, r in published["anchor_results"].items()}, "by_lag": {}}
    for lag in lags_days:
        by_anchor = {}
        for anchor, rows in sorted(anchors.items()):
            neg = es.signal_events(rows, "TURNING_NEGATIVE", btc, lag)
            pos = es.signal_events(rows, "TURNING_POSITIVE", btc, lag)
            by_anchor[anchor] = {"turning_negative": es.summarize(neg), "control_turning_positive": es.summarize(pos),
                                 "turning_negative_event_dates": [e["event_date"] for e in neg]}
        result["by_lag"][str(lag)] = by_anchor
    return result


# ----------------------------------------------------------------- PDLT discovery (AT research)
def _pdlt():
    return load_module("e1x_pdlt_discovery", "scripts/experiments/pdlt_discovery.py")


def pdlt_synthetic(seed: int = 20260922, aligned: bool = False, n_candles: int = 720) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Production-shaped synthetic inputs (the real PDLT inputs live in the restricted plane).

    CFGI timestamps default to the real observed pattern: NOT aligned to 4h boundaries
    (live captures show e.g. 21:19:14Z) and captured minutes after their timestamp.
    """
    pd_mod = _pdlt()
    rng = random.Random(seed)
    start = datetime(2026, 5, 1, tzinfo=UTC)
    candles, price = [], 60000.0
    for i in range(n_candles):
        o = price
        c = o * math.exp(rng.gauss(0, 0.012))
        h = max(o, c) * (1 + abs(rng.gauss(0, 0.004)))
        low = min(o, c) * (1 - abs(rng.gauss(0, 0.004)))
        candles.append({"open_time": iso(start + i * H4), "open": o, "high": h, "low": low, "close": c})
        price = c
    cfgi, comps = [], {f: 50.0 for f in pd_mod.FIELDS}
    offset = timedelta(0) if aligned else timedelta(minutes=19, seconds=14)
    for i in range(n_candles - 90):
        for f in comps:
            comps[f] = min(100.0, max(0.0, comps[f] + rng.gauss(0, 4)))
        row = {"timestamp": iso(start + i * H4 + offset), "symbol": "MARKET", "pdlt_engine_epoch": pd_mod.EPOCH,
               "score": comps["score"], "components": {f: v for f, v in comps.items() if f != "score"}}
        cfgi.append(row)
    return cfgi, candles


PDLT_OUTCOME_SUFFIXES = ("adverse_pct", "favorable_pct", "end_close")


def compute_pdlt(records: list[Record], locate_override: Callable | None = None) -> dict[str, Output]:
    pd_mod = _pdlt()
    cfgi = [r.payload for r in records if r.kind == "VALUE"]
    candles = [r.payload for r in records if r.kind == "PRICE"]
    with patched(pd_mod, **({"locate": locate_override} if locate_override is not None else {})):
        rows = pd_mod.build_dataset({"rows": cfgi}, {"candles": {"BTCUSDT": candles}})
    out = {}
    for row in rows:
        fields = {"deltas": row["deltas"]}
        for horizon in ("72h", "7d", "14d"):
            stats = row.get(horizon)
            fields[horizon] = None if stats is None else {k: v for k, v in stats.items()}
        out[row["timestamp"]] = Output(ts(row["timestamp"]), fields)
    return out


def pdlt_records(cfgi, candles, candle_knowledge: str = "CLOSE") -> list[Record]:
    records = [Record(ts(r["timestamp"]), "VALUE", r["timestamp"], r) for r in cfgi]
    for c in candles:
        when = ts(c["open_time"]) + (H4 if candle_knowledge == "CLOSE" else timedelta(0))
        records.append(Record(when, "PRICE", c["open_time"], c))
    return records


def completed_candle_locate(candles: list[dict[str, Any]], when: datetime) -> int | None:
    """Completed-candle anchor: last candle whose CLOSE is <= when (production since PR #1214)."""
    idx = None
    for i, row in enumerate(candles):
        if row["dt"] + H4 <= when:
            idx = i
        else:
            break
    return idx


def legacy_open_time_locate(candles: list[dict[str, Any]], when: datetime) -> int | None:
    """Seeded negative control: the pre-#1214 production anchor (candle OPEN <= when)."""
    idx = None
    for i, row in enumerate(candles):
        if row["dt"] <= when:
            idx = i
        else:
            break
    return idx


def case_pdlt(variant: str) -> RightTruncationCase:
    aligned = variant == "ALIGNED_TIMESTAMPS"
    cfgi, candles = pdlt_synthetic(aligned=aligned)
    knowledge = "OPEN" if variant == "LABEL_TIME_TRUNCATION_CONTROL" else "CLOSE"
    override = {"REPAIR_CANDIDATE_COMPLETED_CANDLE": completed_candle_locate,
                "SEEDED_LEGACY_OPEN_TIME_ANCHOR": legacy_open_time_locate}.get(variant)
    # PRODUCTION anchors on completed 4h candles since PR #1214; the legacy
    # open-time anchor is kept as a seeded negative so the detector stays proven.
    expected = {"PRODUCTION": "PASS", "ALIGNED_TIMESTAMPS": "PASS", "REPAIR_CANDIDATE_COMPLETED_CANDLE": "PASS",
                "SEEDED_LEGACY_OPEN_TIME_ANCHOR": "FAIL", "LABEL_TIME_TRUNCATION_CONTROL": "PASS"}[variant]
    return RightTruncationCase(
        case_id=f"RT-A07-AT-PDLT-DISCOVERY-{variant}",
        owner="AUTO_TRADING / PDLT v1.1 discovery (FROZEN_METHODS_BLOCKED)",
        production_path="scripts/experiments/pdlt_discovery.py",
        production_callable="build_dataset -> locate + forward_stats" + (f" [locate replaced by {override.__name__}]" if override else ""),
        description={"PRODUCTION": "Production dataset builder; 4h candle knowable at open+4h; CFGI knowable at its timestamp (observed live semantics).",
                     "ALIGNED_TIMESTAMPS": "Same, CFGI timestamps aligned to 4h boundaries.",
                     "REPAIR_CANDIDATE_COMPLETED_CANDLE": "Same inputs; locate() restricted to candles closed by the CFGI timestamp.",
                     "SEEDED_LEGACY_OPEN_TIME_ANCHOR": "Seeded negative: locate() replaced by the pre-#1214 open-time anchor.",
                     "LABEL_TIME_TRUNCATION_CONTROL": "Detector-blindness control: candles truncated by OPEN (label) time instead of knowledge time."}[variant],
        records=pdlt_records(cfgi, candles, knowledge), compute=lambda recs: compute_pdlt(recs, override), max_targets=20,
        decision_fields=lambda name: not name.endswith(PDLT_OUTCOME_SUFFIXES), censor_future=poison_outcome_source,
        excluded_field_reason={s: "OUTCOME_LABEL_BY_DESIGN" for s in PDLT_OUTCOME_SUFFIXES},
        knowledge_time_rule=("candle knowable at open_time (LABEL TIME - deliberately wrong)" if knowledge == "OPEN" else "candle knowable at open_time+4h; CFGI at timestamp"),
        downstream=["PDLT discovery event labels (event72/event7d/event14d)", "PDLT historical holdout screening", "PDLT reopen requirement INDEPENDENT_REVIEW_OF_DISCOVERY_REPAIR"],
        expected=expected, data_binding={"inputs": "SYNTHETIC_PRODUCTION_SHAPED (restricted-plane PDLT inputs not available)", "seed": 20260922, "aligned": aligned})


# ----------------------------------------------------------------- AT E2 features
def case_e2_features(rows, binding) -> RightTruncationCase:
    base = load_module("ai_compiler_vs_policy_e2", "scripts/experiments/ai_compiler_vs_policy_e2.py")
    sys.modules["ai_compiler_vs_policy_e2"] = base
    adapter = load_module("e1x_e2_hourly_adapter", "scripts/experiments/ai_compiler_vs_policy_e2_hourly_adapter.py")
    raw, _ = adapter.load_raw_close_rows(REPO / HOURLY_ROOT, "2100-01-01T00:00:00Z")
    block = base.latest_contiguous_block(raw, min(240, len(raw)))
    records = [Record(ts(r["timestamp"]) + H1, "VALUE", r["timestamp"], r) for r in block]

    def compute(recs: list[Record]) -> dict[str, Output]:
        b = [r.payload for r in sorted(recs, key=lambda r: r.payload["timestamp"])]
        out = {}
        for idx in range(12, len(b)):
            for asset in ("BTC", "ETH"):
                out[f"{asset}|{b[idx]['timestamp']}"] = Output(ts(b[idx]["timestamp"]) + H1, base.feature_row(b, idx, asset))
        return out

    return RightTruncationCase(
        case_id="RT-A08-AT-E2-POLICY-FEATURES", owner="AUTO_TRADING E2 (AT-E2-911 compiler vs direct policy)",
        production_path="scripts/experiments/ai_compiler_vs_policy_e2.py (+ _hourly_adapter.load_raw_close_rows)",
        production_callable="feature_row (ret1/ret4/ret12/vol6/cross_ret4)",
        description="Point-in-time features shown to the LLM policy/compiler, on the latest contiguous real hourly block.",
        records=records, compute=compute, knowledge_time_rule="completed 1h candle knowable at open+1h",
        downstream=["AT-E2-911-v1 result", "E2 candidate-selection experiments"], expected="PASS", data_binding=binding)


# ----------------------------------------------------------------- AT E3 N5 factor examples
def case_n5(anchor: str) -> RightTruncationCase:
    n5 = load_module("e1x_factor_test_n5", "scripts/experiments/factor_test_n5_independent.py")
    rows, manifest = n5.extract_rows(REPO / CAPTURE_ROOT)
    capture_by_key = {(r["symbol"], r["event_timestamp"]): r["capture_dt"] for r in rows}
    records = [Record(r["capture_dt"], "VALUE", f"{r['symbol']}|{r['event_timestamp']}", r) for r in rows]

    def censor(record: Record) -> Record | None:
        row = dict(record.payload)
        row["score"] = row["score"] + 37.0
        row["price"] = row["price"] * 1.5
        return Record(record.available_at, "OUTCOME_SOURCE", record.key, row)

    def compute(recs: list[Record]) -> dict[str, Output]:
        ex = n5.build_examples(sorted((r.payload for r in recs), key=lambda r: (r["symbol"], r["event_dt"])))
        out = {}
        for e in ex:
            claimed = e["event_dt"] if anchor == "EVENT_TIME" else capture_by_key[(e["symbol"], e["event_timestamp"])]
            out[f"{e['symbol']}|{e['event_timestamp']}"] = Output(claimed, {"features": e["features"], "window_observations": e["window_observations"],
                                                                         "window_span_hours": e["window_span_hours"], "future_return": e["future_return"]})
        return out

    return RightTruncationCase(
        case_id=f"RT-A09-AT-E3-N5-FACTOR-EXAMPLES-{anchor}", owner="AUTO_TRADING E3 trial N5 (AT-E3-0019 / AT-HYP-0019)",
        production_path="scripts/experiments/factor_test_n5_independent.py", production_callable="extract_rows + build_examples (window_transform)",
        description=("Examples anchored at CFGI event time, as the code anchors entry price and features." if anchor == "EVENT_TIME" else
                     "Same examples with the decision time moved to the capture time at which the row was actually known."),
        records=records, compute=compute, max_targets=24, decision_fields=lambda n: not n.startswith("future_return"),
        excluded_field_reason={"future_return": "OUTCOME_LABEL_BY_DESIGN"}, censor_future=censor,
        kind_classification={"OUTCOME_SOURCE": "TRUE_FUTURE_LEAKAGE"},
        knowledge_time_rule="CFGI row knowable at its first capture time (captured_at_utc)",
        downstream=["04_RESEARCH_LAB/auto_trading/experiments/E3_TRIAL_N5_INDEPENDENT_RESULT.json"],
        expected="FAIL" if anchor == "EVENT_TIME" else "PASS",
        data_binding={"capture_root": CAPTURE_ROOT, "rows": len(rows), "file_manifest_sha256": manifest["file_manifest_sha256"]})


# ----------------------------------------------------------------- intraday execution snapshot
def case_intraday(rows, binding) -> RightTruncationCase:
    ie = load_module("e1x_intraday_core", "scripts/intraday_execution/intraday_execution_research_core.py")
    fieldnames = list(rows[0].keys())
    records = hourly_records(rows)
    opens = [ts(r["timestamp_utc"]) for r in rows]
    candidates = [t + H1 for t in opens[80:]]
    step = max(1, len(candidates) // 10)
    targets = [candidates[i] for i in range(0, len(candidates), step)][:10]

    def compute(recs: list[Record]) -> dict[str, Output]:
        out = {}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            by_day: dict[str, list[dict[str, str]]] = {}
            for r in recs:
                by_day.setdefault(r.payload["timestamp_utc"][:10], []).append(r.payload)
            for day, day_rows in by_day.items():
                p = root / HOURLY_ROOT / day[:4] / day[5:7] / f"{day}.csv"
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open("w", newline="") as handle:
                    w = csv.DictWriter(handle, fieldnames=fieldnames)
                    w.writeheader()
                    w.writerows(sorted(day_rows, key=lambda x: x["timestamp_utc"]))
            pointer = root / "pointer.json"
            with chdir(root), patched(ie, HOURLY_POINTER=Path("pointer.json")):
                for t in targets:
                    pointer.write_text(json.dumps({"status": "COMPLETE", "window_end_utc": iso(t), "requested_hours": 24, "run_id": "E1X"}))
                    try:
                        _, pairs = ie.hourly_rows()
                        fields = {"btc": ie.asset_features("btc", pairs), "eth": ie.asset_features("eth", pairs),
                                  "ethbtc": ie.ethbtc_features(pairs), "latest_ts": iso(pairs[-1][0]), "pairs": len(pairs)}
                    except RuntimeError as exc:
                        fields = {"error": str(exc)}
                    out[f"SNAPSHOT|{iso(t)}"] = Output(t, fields)
        return out

    return RightTruncationCase(
        case_id="RT-A10-INTRADAY-EXECUTION-SNAPSHOT-FEATURES", owner="04_MARKET_LEARNING intraday_execution research core (feeds shadow direction confidence)",
        production_path="scripts/intraday_execution/intraday_execution_research_core.py", production_callable="hourly_rows + asset_features + ethbtc_features",
        description="Live snapshot builder replayed at historical pointer times against archives that also contain later rows.",
        records=records, compute=compute, targets=targets, knowledge_time_rule="completed 1h candle knowable at open+1h; pointer window_end = decision time",
        downstream=["04_MARKET_LEARNING/intraday_execution observations", "shadow_direction_confidence"], expected="PASS", data_binding=binding,
        notes=["Tests the production window filter (ts < window_end) and all trailing features, not the AT-EXP-004 derived-column quarantine, which is separately owned."])


# ----------------------------------------------------------------- pullback learning
def load_pullback_observations(repo: Path = REPO) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    files = sorted((repo / PULLBACK_OBS).rglob("*.json"))
    obs = [json.loads(p.read_text()) | {"_path": p.relative_to(repo).as_posix()} for p in files]
    return obs, {"path": PULLBACK_OBS, **_files_binding(files)}


def pullback_stored_vs_pit(obs: list[dict[str, Any]]) -> dict[str, Any]:
    """Recompute each stored live adaptive rank with only observations captured before it."""
    pl = load_module("e1x_pullback_ledger", "scripts/pullback_learning/pullback_learning_ledger.py")
    ordered = sorted(obs, key=lambda o: (o["captured_at_utc"], o["price_observation_utc"]))
    compared, mismatches, skipped = 0, [], 0
    for i, o in enumerate(ordered):
        stored = o.get("adaptive_evidence") or {}
        if not stored.get("adaptive_percentiles_ready"):
            skipped += 1
            continue
        binding = stored.get("eligibility_status") or {
            # legacy observations written before the eligibility binding existed
            "adaptive_descriptive_statistics": True,
            "classification_reason": stored.get("classification_reason", "LEGACY_OBSERVATION_WITHOUT_BINDING"),
        }
        prior = [p for p in ordered[:i]][-pl.TRAILING_OBS:]
        with patched(pl, eligibility_binding=lambda b=binding: b):
            _, evidence = pl.classify(prior, o, None)
        compared += 1
        diffs = {k: {"stored": stored.get(k), "pit": evidence.get(k)} for k in ("drawdown_percentile_rank", "breadth_percentile_rank", "step_return_percentile_rank", "observation_count")
                 if not values_equal(stored.get(k), evidence.get(k))}
        if diffs:
            mismatches.append({"price_observation_utc": o["price_observation_utc"], "captured_at_utc": o["captured_at_utc"], "diffs": diffs})
    return {"check": "LIVE_STORED_VS_PIT_RECOMPUTATION", "owner": "scripts/pullback_learning/pullback_learning_ledger.py::classify",
            "observations": len(obs), "compared": compared, "skipped_not_ready": skipped, "mismatch_count": len(mismatches),
            "mismatches": mismatches[:10], "observed": "PASS" if not mismatches else "FAIL"}


def case_pullback_replay_loader(obs, binding) -> RightTruncationCase:
    pl = load_module("e1x_pullback_ledger_loader", "scripts/pullback_learning/pullback_learning_ledger.py")
    records = [Record(ts(o["captured_at_utc"]), "VALUE", o["price_observation_utc"], o) for o in obs]
    ordered_obs = sorted(obs, key=lambda o: o["captured_at_utc"])
    targets = [ts(ordered_obs[i]["captured_at_utc"]) for i in range(30, len(ordered_obs), max(1, (len(ordered_obs) - 30) // 8))][:8]

    def compute(recs: list[Record]) -> dict[str, Output]:
        out = {}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for r in recs:
                t_obs = ts(r.payload["price_observation_utc"])
                p = root / f"{t_obs:%Y/%m/%d}/{t_obs:%Y%m%dT%H%M%SZ}.json"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps({k: v for k, v in r.payload.items() if k != "_path"}))
            by_capture = {r.payload["captured_at_utc"]: r.payload for r in recs}
            for t in targets:
                current = by_capture.get(next((c for c in by_capture if ts(c) == t), ""), None)
                if current is None:
                    continue
                binding_ = (current.get("adaptive_evidence") or {}).get("eligibility_status") or {"adaptive_descriptive_statistics": True, "classification_reason": "E1X"}
                with patched(pl, OBS=root, eligibility_binding=lambda b=binding_: b):
                    recent = [o for o in pl.load_recent_observations() if o.get("price_observation_utc") != current["price_observation_utc"]]
                    _, evidence = pl.classify(recent, current, None)
                out[f"REPLAY|{current['price_observation_utc']}"] = Output(t, {k: evidence.get(k) for k in ("drawdown_percentile_rank", "breadth_percentile_rank", "step_return_percentile_rank", "observation_count")})
        return out

    return RightTruncationCase(
        case_id="RT-A11-PULLBACK-LEDGER-REPLAY-LOADER-LATENT", owner="04_MARKET_LEARNING pullback_learning ledger",
        production_path="scripts/pullback_learning/pullback_learning_ledger.py", production_callable="load_recent_observations + classify (replayed over the current archive)",
        description="Latent-path probe: what the production loader returns if anyone replays a historical observation over today's archive.",
        records=records, compute=compute, targets=targets, knowledge_time_rule="observation knowable at captured_at_utc",
        downstream=["none - no production caller replays history (live path verified separately by LIVE_STORED_VS_PIT_RECOMPUTATION)"],
        expected="FAIL", data_binding=binding,
        notes=["Expected to FAIL: load_recent_observations() returns the last 180 files present on disk, so a historical replay would rank against later observations. The live writer only ever sees files that already exist."])


# ----------------------------------------------------------------- DATA PING auto market state BTC.D
def btcd_vintages(repo: Path = REPO) -> list[tuple[str, datetime]]:
    log = subprocess.check_output(["git", "log", "--format=%H %cI", "--", BTCD_LATEST], cwd=repo, text=True).split("\n")
    return sorted(((line.split()[0], ts(line.split()[1])) for line in log if line.strip()), key=lambda x: x[1])


def case_btcd_asof(repo: Path = REPO) -> RightTruncationCase:
    ams = importlib.import_module("scripts.data_ping.auto_market_state")
    vintages = btcd_vintages(repo)
    records = [Record(when, "VINTAGE", sha_, sha_) for sha_, when in vintages]
    sample = vintages[1:-1:max(1, (len(vintages) - 2) // 8)][:8]
    targets = [when + timedelta(minutes=30) for _, when in sample]

    def compute(recs: list[Record]) -> dict[str, Output]:
        if not recs:
            return {}
        latest = max(recs, key=lambda r: r.available_at)
        out = {}
        for t in targets:
            value, health = ams.btc_d(repo, latest.payload, t)
            out[f"BTCD|{iso(t)}"] = Output(t, {"value_pct": (value or {}).get("value_pct"), "date_utc": (value or {}).get("date_utc"),
                                               "status": health.get("status"), "classification": health.get("classification")})
        return out

    return RightTruncationCase(
        case_id="RT-A12-DATA-PING-AUTO-MARKET-STATE-BTC-D-ASOF", owner="02_DATA_PING auto_market_state (non-binding state assembly)",
        production_path="scripts/data_ping/auto_market_state.py", production_callable="btc_d(repo_root, sha, now)",
        description="As-of BTC.D selection replayed with the latest file vintage versus the vintage that existed at the decision time.",
        records=records, compute=compute, targets=targets, knowledge_time_rule="file vintage knowable at its commit time",
        downstream=["AUTO_MARKET_STATE_PACKET_v1 btc_dominance lane", "entry_signal_ledger"], expected="FAIL",
        data_binding={"path": BTCD_LATEST, "vintages": len(vintages), "first": iso(vintages[0][1]) if vintages else None, "last": iso(vintages[-1][1]) if vintages else None},
        notes=["Each re-publication rewrites source_verified_timestamp for every historical row; the harness classifies the resulting replay difference by the contaminating record kind (VINTAGE)."])


# ----------------------------------------------------------------- Master Monday preflight selectors (latent replay path)
def case_master_monday_selectors(rows, binding) -> RightTruncationCase:
    mm = load_module("e1x_master_monday_preflight_v3", "scripts/master_monday/build_preflight_package_v3.py")
    captures = []
    for path in sorted((REPO / CAPTURE_ROOT).rglob("*.json")):
        if path.name == "LATEST.json":
            continue
        try:
            value = json.loads(path.read_text())
        except Exception:
            continue
        if value.get("contract") != "DAILY_LIVE_ANCHOR_INDEX_v3" or not value.get("captured_at_utc"):
            continue
        captures.append(Record(ts(value["captured_at_utc"]), "VALUE", "CAPTURE|" + path.relative_to(REPO / CAPTURE_ROOT).as_posix(), ("CAPTURE", path.relative_to(REPO / CAPTURE_ROOT).as_posix(), path.read_bytes())))
    hourly = [Record(r.available_at, r.kind, "HOURLY|" + r.key, ("HOURLY", r.payload)) for r in hourly_records(rows)]
    fieldnames = list(rows[0].keys())
    cap_times = sorted(r.available_at for r in captures)
    targets = [cap_times[i] + timedelta(minutes=5) for i in range(20, len(cap_times) - 1, max(1, (len(cap_times) - 21) // 6))][:6]

    def compute(recs: list[Record]) -> dict[str, Output]:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            by_day: dict[str, list[dict[str, str]]] = {}
            for r in recs:
                if r.payload[0] == "CAPTURE":
                    p = root / "captures" / r.payload[1]
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(r.payload[2])
                else:
                    by_day.setdefault(r.payload[1]["timestamp_utc"][:10], []).append(r.payload[1])
            for day, day_rows in by_day.items():
                p = root / "hourly" / day[:4] / day[5:7] / f"{day}.csv"
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open("w", newline="") as handle:
                    w = csv.DictWriter(handle, fieldnames=fieldnames)
                    w.writeheader()
                    w.writerows(sorted(day_rows, key=lambda x: x["timestamp_utc"]))
            _, cap = mm.latest_capture(root / "captures")
            _, hour = mm.latest_hourly(root / "hourly")
            fields = {"latest_capture_captured_at_utc": (cap or {}).get("captured_at_utc"), "latest_hourly_timestamp_utc": (hour or {}).get("timestamp_utc")}
            return {f"PREFLIGHT_AS_OF|{iso(t)}": Output(t, fields) for t in targets}

    return RightTruncationCase(
        case_id="RT-A14-MASTER-MONDAY-PREFLIGHT-SELECTORS-LATENT", owner="Master Monday preflight v3 (weekly-api-calibration-shadow / master-monday-remaining-gaps)",
        production_path="scripts/master_monday/build_preflight_package_v3.py", production_callable="latest_capture + latest_hourly",
        description="Latent-path probe: the CLI accepts --freeze-start/--freeze-end but applies them only to accepted DATA PING packets, not to the capture/hourly selectors.",
        records=captures + hourly, compute=compute, targets=targets, knowledge_time_rule="capture knowable at captured_at_utc; hourly row at open+1h",
        downstream=["none in current workflows (both callers run live at freeze time without freeze arguments)"], expected="FAIL",
        data_binding={**binding, "captures": len(captures)},
        notes=["Expected to FAIL on replay. Live callers run at the freeze moment, so the selectors see only already-existing files."])


# ----------------------------------------------------------------- SPAR
def case_spar() -> RightTruncationCase:
    spar = load_module("e1x_spar_v1", "scripts/experiments/spar_v1.py")
    snaps, audit = spar.load_snapshots_audit(REPO / CAPTURE_ROOT)
    records = [Record(s.t, "VALUE", iso(s.t), s) for s in snaps]

    def compute(recs: list[Record]) -> dict[str, Output]:
        ordered = [r.payload for r in sorted(recs, key=lambda r: r.available_at)]
        out = {}
        for pattern, idxs in spar.detect_events(ordered).items():
            for i in idxs:
                out[f"{pattern}|{iso(ordered[i].t)}"] = Output(ordered[i].t, {"event": 1, "source_path": ordered[i].p})
        return out

    return RightTruncationCase(
        case_id="RT-A13-AT-SPAR-EVENT-DETECTION", owner="AUTO_TRADING SPAR-v1 (sequence pattern replay)",
        production_path="scripts/experiments/spar_v1.py", production_callable="load_snapshots_audit + detect_events",
        description="Event existence and timing for SPAR-P1/P2/P3 on the real capture archive.", records=records, compute=compute,
        max_targets=40, knowledge_time_rule="snapshot knowable at captured_at_utc (V3 spot = previous completed hour)",
        downstream=["SPAR-v1 replay / fragility reports"], expected="PASS", data_binding={"capture_root": CAPTURE_ROOT, **audit})


# =========================================================================== warm-up cases
def warmup_copper_gold_2m(rows, binding) -> WarmupCase:
    records = cg_records(rows)
    periods = [p for p, _, _ in rows]
    targets = []
    for anchor, parity in (("JAN_FEB", 0), ("FEB_MAR", 1)):
        bars = [p for p in periods if int(p[-2:]) % 2 == parity and p >= "2011-01"]
        step = max(1, len(bars) // 6)
        targets += [f"2M|{anchor}|{p}" for p in bars[::step]][:6] + [f"2M|{anchor}|{bars[-1]}"]
    first_target = min(t.split("|")[2] for t in targets)
    return WarmupCase(
        case_id="WU-W01-COPPER-GOLD-2M-MACD-RSI", owner="data_terminal World Bank Copper/Gold owner",
        production_path="scripts/data_terminal/world_bank_copper_gold_owner.py", production_callable="settled_2m_features (EMA seeded at first bar; Wilder RSI seeded by SMA)",
        description="How much the settled 2M MACD(12,26,9)/RSI14 and regime_state at a fixed bar depend on history length (monthly records).",
        records=records, compute=compute_cg, target_keys=targets, warmups=[48, 96, 144, 192, 240, 360, 480, 600],
        production_history_records=periods.index(first_target),
        numeric_fields=["macd_12_26", "macd_signal_9", "macd_histogram", "rsi_14_wilder"], categorical_fields=["regime_state"],
        tolerance_abs=1e-12, tolerance_rel=1e-6,
        tolerance_reason="convergence declared below 1 ppm relative drift; every raw delta is still reported and regime_state flips are counted separately as categorical drift",
        downstream=["copper/gold LATEST regime_consensus", "event study", "any TDBC reproduction from a shorter history"],
        data_binding=binding)


def warmup_copper_gold_monthly(rows, binding) -> WarmupCase:
    records = cg_records(rows)
    periods = [p for p, _, _ in rows]
    targets = [f"M|{p}" for p in ("2017-12", "2021-11", "2024-06", periods[-1])]
    return WarmupCase(
        case_id="WU-W02-COPPER-GOLD-MONTHLY-RSI-ZSCORE", owner="data_terminal World Bank Copper/Gold owner",
        production_path="scripts/data_terminal/world_bank_copper_gold_owner.py", production_callable="monthly_features",
        description="Monthly Wilder RSI14 (recursive) versus fixed-window MA/z-score at fixed months.",
        records=records, compute=compute_cg, target_keys=targets, warmups=[14, 24, 36, 60, 120, 240, 480],
        production_history_records=periods.index("2017-12"),
        numeric_fields=["rsi_14m_wilder", "ma_24m", "zscore_24m_population", "roc_12m_pct"],
        tolerance_abs=1e-12, tolerance_rel=1e-9, tolerance_reason="owner rounds derived values to 12 decimals", data_binding=binding)


def warmup_backtest_hourly(rows, binding) -> WarmupCase:
    records = hourly_records(rows)
    keys = [f"BTC|{iso(ts(rows[i]['timestamp_utc']))}" for i in (len(rows) - 1, len(rows) - 200, len(rows) - 400)]
    return WarmupCase(
        case_id="WU-W03-BACKTEST-HOURLY-VOL-AND-RUNNING-HIGH", owner="backtest_engine",
        production_path="backtest_engine/w30_replay.py", production_callable="build_hourly_volatility",
        description="Fixed-window realized vol versus start-anchored running high / drawdown at fixed hours.",
        records=records, compute=compute_backtest_hourly_volatility, target_keys=keys, warmups=[24, 72, 73, 168, 336, 720],
        production_history_records=167, numeric_fields=["realized_vol_24h_annualized", "realized_vol_72h_annualized", "running_high_close", "drawdown_from_running_high"],
        start_anchored_fields=["running_high_close", "drawdown_from_running_high"], downstream=["W30 golden fixture (one week = 168 hourly rows)"],
        notes=["production_history_records=167 is the W30 fixture length (one week of hourly rows)."], data_binding=binding)


def warmup_backtest_etf(asset_rows, binding) -> WarmupCase:
    records = [r for asset, rows in asset_rows.items() for r in etf_records(asset, rows, False)]
    btc_dates = [r["date"] for r in asset_rows["BTC"]]
    keys = [f"BTC|{d}" for d in (btc_dates[-1], btc_dates[-60], btc_dates[-250])]
    return WarmupCase(
        case_id="WU-W04-BACKTEST-ETF-STREAK-AND-ROLLING", owner="backtest_engine",
        production_path="backtest_engine/w30_replay.py", production_callable="build_etf_trailing",
        description="Rolling 20-session windows versus the signed-flow streak (start-anchored until the first sign change).",
        records=[r for r in records if r.payload["asset"] == "BTC"], compute=compute_backtest_etf_trailing, target_keys=keys,
        warmups=[5, 10, 20, 30, 60, 250], production_history_records=4,
        numeric_fields=["rolling_net_flow_20s_usd_millions", "signed_flow_streak_sessions", "flow_acceleration_3s_usd_millions"],
        start_anchored_fields=["signed_flow_streak_sessions"], notes=["production_history_records=4: the W30 golden fixture contains one ETF week (5 sessions)."],
        data_binding=binding)


def load_kraken_daily(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    key = [k for k in payload["result"] if k != "last"][0]
    rows = [{"open_time": datetime.fromtimestamp(int(r[0]), UTC), "high": float(r[2]), "low": float(r[3]), "close": float(r[4])} for r in payload["result"][key]]
    rows.sort(key=lambda r: r["open_time"])
    return rows


def protocol_wilder_atr14(candles: list[dict[str, Any]]) -> list[float | None]:
    """Canonical formula B4 of 2026-07-08__forward-range-ledger-protocol-v0-1 (no executable owner exists on main).

    TR=max(H-L, |H-Cprev|, |L-Cprev|); seed = SMA of first 14 TR; Wilder smoothing thereafter.
    """
    tr: list[float | None] = [None]
    for prev, cur in zip(candles, candles[1:]):
        tr.append(max(cur["high"] - cur["low"], abs(cur["high"] - prev["close"]), abs(cur["low"] - prev["close"])))
    atr: list[float | None] = [None] * len(candles)
    if len(candles) < 15:
        return atr
    value = sum(tr[1:15]) / 14.0
    atr[14] = value
    for i in range(15, len(candles)):
        value = (value * 13 + tr[i]) / 14.0
        atr[i] = value
    return atr


def warmup_cn_atr(kraken_path: Path) -> WarmupCase:
    candles = load_kraken_daily(kraken_path)
    now_day = candles[-1]["open_time"]
    settled = candles[:-1]  # Kraken's final OHLC element is the in-progress interval; never a settled row
    records = [Record(c["open_time"] + D1, "VALUE", iso(c["open_time"]), c) for c in settled]

    def compute(recs: list[Record]) -> dict[str, Output]:
        cs = [r.payload for r in sorted(recs, key=lambda r: r.available_at)]
        atr = protocol_wilder_atr14(cs)
        return {f"ATR14|{iso(c['open_time'])[:10]}": Output(c["open_time"] + D1, {"atr14": a, "atr14_whole_usd": round(a), "dumb15_width_usd": round(3.0 * a)})
                for c, a in zip(cs, atr) if a is not None}

    keys = [f"ATR14|{iso(settled[i]['open_time'])[:10]}" for i in (len(settled) - 1, len(settled) - 8, len(settled) - 30, len(settled) - 90)]
    return WarmupCase(
        case_id="WU-W05-CN-FORWARD-RANGE-PROTOCOL-WILDER-ATR14", owner="05_CYCLE_NAVIGATOR forward range ledger protocol v0.1 (DUMB_1.5 / DUMB_2.0 baselines)",
        production_path="05_CYCLE_NAVIGATOR/protocols/2026-07-08__forward-range-ledger-protocol-v0-1__canonical.md#B4 (PROTOCOL_ONLY - no executable owner on main)",
        production_callable="Wilder ATR14, SMA seed, minimum 60 settled daily candles, whole-USD rounding",
        description="Protocol-minimum history (60 candles) versus long history for the ATR that sizes the dumb baselines.",
        records=records, compute=compute, target_keys=keys, warmups=[59, 90, 120, 250, 500, 700],
        production_history_records=59, numeric_fields=["atr14"], categorical_fields=["atr14_whole_usd"],
        tolerance_abs=0.5, tolerance_rel=0.0, tolerance_reason="protocol B4 whole-USD rounding: a difference >= 0.5 USD changes the published integer ATR",
        downstream=["CN DUMB_1.5 / DUMB_2.0 baseline widths", "adjustment alpha vs DUMB", "kill criteria K1/K2"],
        data_binding={"source": "Kraken public OHLC XBTUSD 1440", "sha256": sha_file(kraken_path), "settled_candles": len(settled),
                      "first": iso(settled[0]["open_time"]), "last": iso(settled[-1]["open_time"]), "retrieved_last_open": iso(now_day)})


def warmup_e2(rows, binding) -> WarmupCase:
    case = case_e2_features(rows, binding)
    keys = sorted(case.compute(case.records))[-3:]
    return WarmupCase(
        case_id="WU-W06-AT-E2-FEATURE-WINDOWS", owner="AUTO_TRADING E2", production_path=case.production_path,
        production_callable="feature_row", description="Fixed 12-bar windows must be exact once 12 preceding rows exist (E2 warmup=12).",
        records=case.records, compute=case.compute, target_keys=keys, warmups=[4, 8, 11, 12, 13, 24, 48], production_history_records=12,
        numeric_fields=["ret1_pct", "ret4_pct", "ret12_pct", "vol6_pct", "cross_ret4_pct"], data_binding=binding)


# =========================================================================== detector controls
def control_clean_trailing_mean(rows) -> RightTruncationCase:
    def compute(recs: list[Record]) -> dict[str, Output]:
        ordered = sorted(recs, key=lambda r: r.payload["timestamp_utc"])
        norm = [{"timestamp": r.payload["timestamp_utc"], "value": float(r.payload["btc_close"])} for r in ordered]
        values = e1.trailing_mean(norm, 24)
        return {f"BTC|{n['timestamp']}": Output(ts(n["timestamp"]) + H1, {"trailing_mean_24": v}) for n, v in zip(norm, values)}
    return RightTruncationCase("CTRL-C01-CLEAN-E1-TRAILING-MEAN-ON-REAL-HOURLY", "E1X detector control", "scripts/experiments/strategy_factor_leakage_e1.py",
                               "trailing_mean(window=24)", "Known-clean causal feature on real data must PASS.", hourly_records(rows), compute, expected="PASS",
                               knowledge_time_rule="open+1h")


def control_seeded_negative_shift(rows) -> RightTruncationCase:
    return RightTruncationCase("CTRL-C02-SEEDED-NEGATIVE-SHIFT-INTO-PRODUCTION", "E1X detector control", "backtest_engine/w30_replay.py",
                               "build_hourly_volatility fed close[i+1] (seeded shift(-1))", "Seeded one-step future leak routed through a real production function must FAIL with a 1-record minimal suffix.",
                               hourly_records(rows), lambda recs: compute_backtest_hourly_volatility(recs, lambda c: c[1:] + [None]),
                               expected="FAIL", expected_classification="TRUE_FUTURE_LEAKAGE", knowledge_time_rule="open+1h", max_targets=12)


def control_seeded_full_sample_zscore(cg_rows) -> RightTruncationCase:
    def transform(monthly: list[dict[str, Any]]) -> None:
        ratios = [float(r["ratio"]) for r in monthly]
        mu = sum(ratios) / len(ratios)
        sd = math.sqrt(sum((x - mu) ** 2 for x in ratios) / len(ratios))
        for r in monthly:
            r["seeded"] = 0.0 if sd == 0 else (float(r["ratio"]) - mu) / sd
    return RightTruncationCase("CTRL-C03-SEEDED-FULL-SAMPLE-ZSCORE", "E1X detector control", "scripts/data_terminal/world_bank_copper_gold_owner.py",
                               "monthly_features + seeded whole-series z-score", "Seeded full-sample normalization must FAIL.",
                               cg_records(cg_rows), lambda recs: compute_cg(recs, transform), expected="FAIL", expected_classification="TRUE_FUTURE_LEAKAGE",
                               knowledge_time_rule="owner label (period end)", max_targets=12)


def control_seeded_centered_rolling(etf_rows) -> RightTruncationCase:
    import pandas as pd
    records = [Record(us_session_close_utc(date.fromisoformat(r["date"])), "VALUE", r["date"], r) for r in etf_rows["BTC"] if r.get("Total") not in (None, "")]

    def compute(recs: list[Record]) -> dict[str, Output]:
        ordered = sorted(recs, key=lambda r: r.key)
        s = pd.Series([float(r.payload["Total"]) for r in ordered])
        centered = s.rolling(5, center=True).mean()
        return {r.key: Output(r.available_at, {"centered_mean_5": None if pd.isna(v) else float(v)}) for r, v in zip(ordered, centered)}
    return RightTruncationCase("CTRL-C04-SEEDED-CENTERED-ROLLING", "E1X detector control", "pandas", "Series.rolling(5, center=True)",
                               "Seeded centered window must FAIL with a 2-record minimal suffix.", records, compute, expected="FAIL",
                               expected_classification="TRUE_FUTURE_LEAKAGE", knowledge_time_rule="session close", max_targets=12)


def control_seeded_bfill(rows) -> RightTruncationCase:
    import pandas as pd

    def compute(recs: list[Record]) -> dict[str, Output]:
        ordered = sorted(recs, key=lambda r: r.payload["timestamp_utc"])
        values = [None if i % 7 == 3 else float(r.payload["btc_close"]) for i, r in enumerate(ordered)]
        filled = pd.Series(values, dtype="float64").bfill()
        return {r.payload["timestamp_utc"]: Output(r.available_at, {"close_bfilled": None if pd.isna(v) else float(v)}) for r, v in zip(ordered, filled)}
    return RightTruncationCase("CTRL-C05-SEEDED-BFILL", "E1X detector control", "pandas", "Series.bfill() over deliberately missing closes",
                               "Seeded backward fill must FAIL exactly at the missing rows.", hourly_records(rows), compute, expected="FAIL",
                               expected_classification="TRUE_FUTURE_LEAKAGE", knowledge_time_rule="open+1h", max_targets=21)


def _ema_seeded(values: list[float], span: int) -> list[float]:
    alpha, out = 2.0 / (span + 1.0), []
    for i, v in enumerate(values):
        out.append(v if i == 0 else alpha * v + (1 - alpha) * out[-1])
    return out


def _compute_seeded_ema(recs: list[Record]) -> dict[str, Output]:
    ordered = sorted(recs, key=lambda r: r.payload["timestamp_utc"])
    ema = _ema_seeded([float(r.payload["btc_close"]) for r in ordered], 100)
    return {r.payload["timestamp_utc"]: Output(r.available_at, {"ema100": v}) for r, v in zip(ordered, ema)}


def control_seeded_ema_right(rows) -> RightTruncationCase:
    return RightTruncationCase("CTRL-C06a-SEEDED-EMA-IS-CAUSAL", "E1X detector control", "control", "EMA(span=100) seeded at first value",
                               "A recursive but causal indicator must PASS right truncation (warm-up drift is not leakage).", hourly_records(rows),
                               _compute_seeded_ema, expected="PASS", knowledge_time_rule="open+1h", max_targets=12)


def control_seeded_ema_warmup(rows, production_history: int) -> WarmupCase:
    keys = [rows[-1]["timestamp_utc"], rows[-50]["timestamp_utc"]]
    expected = "INSUFFICIENT_WARMUP" if production_history < 600 else "RECURSIVE_CONVERGENCE_DRIFT"
    return WarmupCase(f"CTRL-C06{'b' if production_history < 600 else 'c'}-SEEDED-EMA-WARMUP-PRODUCTION-{production_history}", "E1X detector control", "control",
                      "EMA(span=100) seeded at first value", "Seeded warm-up drift must be detected and classified by declared production history.",
                      hourly_records(rows), _compute_seeded_ema, keys, [50, 150, 300, 600, 900], production_history, ["ema100"],
                      tolerance_abs=0.0, tolerance_rel=1e-6, tolerance_reason="control tolerance 1e-6 relative", expected=expected)


def control_seeded_nondeterminism(rows) -> RightTruncationCase:
    rng = random.SystemRandom()

    def compute(recs: list[Record]) -> dict[str, Output]:
        ordered = sorted(recs, key=lambda r: r.payload["timestamp_utc"])
        return {r.payload["timestamp_utc"]: Output(r.available_at, {"noisy_close": float(r.payload["btc_close"]) + rng.random()}) for r in ordered}
    return RightTruncationCase("CTRL-C07-SEEDED-NONDETERMINISM", "E1X detector control", "control", "close + unseeded noise",
                               "Unseeded randomness must be reported as NONDETERMINISM, not as leakage.", hourly_records(rows), compute, expected="FAIL",
                               expected_classification="NONDETERMINISM", knowledge_time_rule="open+1h", max_targets=4)


def _membership_records(obs: list[dict[str, Any]]) -> list[Record]:
    records = []
    for o in obs:
        t = ts(o["captured_at_utc"])
        records.append(Record(t, "VALUE", o["price_observation_utc"], o))
        records.append(Record(t, "MEMBERSHIP", "UNIVERSE", sorted(o.get("constituents", {}))))
    return records


def control_late_listing(obs) -> RightTruncationCase:
    pl = load_module("e1x_pullback_ledger_ctrl", "scripts/pullback_learning/pullback_learning_ledger.py")

    def compute(recs: list[Record]) -> dict[str, Output]:
        ordered = sorted((r for r in recs if r.kind == "VALUE"), key=lambda r: r.available_at)
        out = {}
        for prev, cur in zip(ordered, ordered[1:]):
            step, n = pl.matched_return(prev.payload, cur.payload)
            out[cur.key] = Output(cur.available_at, {"matched_step_return_pct": step, "matched_count": n})
        return out
    return RightTruncationCase("CTRL-C08-FALSE-POSITIVE-LATE-LISTING", "E1X false-positive control", "scripts/pullback_learning/pullback_learning_ledger.py",
                               "matched_return (cross-sectional, membership changes over time)", "Assets entering the universe later must not produce a false positive.",
                               [r for r in _membership_records(obs) if r.kind == "VALUE"], compute, expected="PASS", knowledge_time_rule="captured_at_utc", max_targets=16)


def control_membership(obs, live_only: bool) -> RightTruncationCase:
    def compute(recs: list[Record]) -> dict[str, Output]:
        values = sorted((r for r in recs if r.kind == "VALUE"), key=lambda r: r.available_at)
        members = max((r for r in recs if r.kind == "MEMBERSHIP"), key=lambda r: r.available_at).payload
        out = {}
        for prev, cur in zip(values, values[1:]):
            p, c = prev.payload.get("constituents", {}), cur.payload.get("constituents", {})
            moves = [c[m] > p[m] for m in members if m in p and m in c]
            out[cur.key] = Output(cur.available_at, {"breadth_under_latest_membership": None if not moves else sum(moves) / len(moves), "n": len(moves)})
        return out
    return RightTruncationCase(
        f"CTRL-C09{'a' if live_only else 'b'}-MEMBERSHIP-{'LIVE-ONLY-OWNER' if live_only else 'HISTORICAL-RECOMPUTATION'}", "E1X classification control",
        "control over real pullback constituent prices", "breadth under the latest available membership snapshot",
        ("Live-only owner (membership = current universe by design, no historical recomputation is claimed): difference must be EXPECTED_CROSS_SECTIONAL_DIFFERENCE." if live_only else
         "Historical recomputation with a later universe (survivorship): identical difference must be TRUE_FUTURE_LEAKAGE."),
        _membership_records(obs), compute, expected="FAIL", knowledge_time_rule="captured_at_utc", max_targets=10,
        kind_classification={"MEMBERSHIP": "EXPECTED_CROSS_SECTIONAL_DIFFERENCE"} if live_only else {},
        expected_classification="EXPECTED_CROSS_SECTIONAL_DIFFERENCE" if live_only else "TRUE_FUTURE_LEAKAGE")


def control_source_revision(cg_rows) -> RightTruncationCase:
    records = cg_records(cg_rows)
    target = next(r for r in records if r.key == "2025-06")
    period, copper, gold = target.payload
    records.append(Record(ts("2026-09-10T00:00:00Z"), "REVISION", "2025-06", (period, copper * 1.01, gold)))
    return RightTruncationCase("CTRL-C10-SOURCE-REVISION-CLASSIFICATION", "E1X classification control", "scripts/data_terminal/world_bank_copper_gold_owner.py",
                               "monthly_features with an injected later vintage of 2025-06", "A later source revision must be SOURCE_VINTAGE_RISK, not TRUE_FUTURE_LEAKAGE.",
                               records, compute_cg, targets=[ts("2026-01-01T00:00:00Z"), ts("2026-08-31T23:59:59Z")], expected="FAIL",
                               expected_classification="SOURCE_VINTAGE_RISK", knowledge_time_rule="owner label; injected revision at 2026-09-10")


# =========================================================================== source-vintage probes (git history)
def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL)


def _git_bytes(repo: Path, sha_: str, path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{sha_}:{path}"], cwd=repo, stderr=subprocess.DEVNULL)


def probe_hourly_vintages(repo: Path = REPO) -> dict[str, Any]:
    meta = {"source_window_end_utc", "timestamp_copenhagen"}
    files = sorted((repo / HOURLY_ROOT).glob("20??/??/*.csv"))
    classes: dict[str, int] = {}
    field_changes: dict[str, int] = {}
    change_commit_days: dict[str, int] = {}
    rows_seen, rows_value_changed, versions = 0, 0, 0
    examples = []
    for f in files:
        rel = f.relative_to(repo).as_posix()
        log = [l.split() for l in _git(repo, "log", "--reverse", "--format=%H %cI", "--", rel).splitlines() if l.strip()]
        history: dict[str, list[tuple[str, dict[str, str]]]] = {}
        for sha_, when in log:
            versions += 1
            for row in csv.DictReader(io.StringIO(_git_bytes(repo, sha_, rel).decode("utf-8-sig"))):
                history.setdefault(row["timestamp_utc"], []).append((when, row))
        for key, vs in history.items():
            rows_seen += 1
            changed = False
            for (w0, a), (w1, b) in zip(vs, vs[1:]):
                for name in sorted((set(a) & set(b)) - meta):
                    if a[name] == b[name]:
                        continue
                    try:
                        if a[name] and b[name] and math.isclose(float(a[name]), float(b[name]), rel_tol=1e-12, abs_tol=1e-15):
                            continue
                    except ValueError:
                        pass
                    changed = True
                    field_changes[name] = field_changes.get(name, 0) + 1
                    change_commit_days[w1[:10]] = change_commit_days.get(w1[:10], 0) + 1
                    if len(examples) < 5:
                        examples.append({"timestamp_utc": key, "field": name, "first_persisted": a[name], "later_persisted": b[name], "first_commit_utc": w0, "later_commit_utc": w1})
            rows_value_changed += int(changed)
    return {
        "probe": "SV-HOURLY-DERIVED-COLUMN-VINTAGES", "path": HOURLY_ROOT, "files": len(files), "versions_read": versions,
        "rows_seen": rows_seen, "rows_with_post_persistence_value_change": rows_value_changed,
        "field_change_counts": dict(sorted(field_changes.items(), key=lambda kv: -kv[1])),
        "last_change_commit_day": max(change_commit_days) if change_commit_days else None,
        "change_commit_days": dict(sorted(change_commit_days.items())), "examples": examples,
        "previously_known_as": "AT-EXP-004 (interval-keyed downgrade / schedule dependence), remediation merged 2026-09-14 in c180d3ca5",
    }


def probe_btcd_vintages(repo: Path = REPO) -> dict[str, Any]:
    vintages = btcd_vintages(repo)
    values: list[tuple[str, dict[str, float], set[str]]] = []
    for sha_, when in vintages:
        rows = list(csv.DictReader(io.StringIO(_git_bytes(repo, sha_, BTCD_LATEST).decode("utf-8-sig"))))
        values.append((iso(when), {r["date_utc"]: float(r["btc_d_close"]) for r in rows if r.get("btc_d_close")},
                       {r.get("source_verified_timestamp") for r in rows}))
    revised = 0
    for (_, a, _), (_, b, _) in zip(values, values[1:]):
        revised += sum(1 for k in sorted(set(a) & set(b)) if not math.isclose(a[k], b[k], abs_tol=1e-9))
    return {"probe": "SV-BTC-D-CMC-VINTAGES", "path": BTCD_LATEST, "vintages": len(vintages),
            "first_vintage_utc": values[0][0] if values else None, "last_vintage_utc": values[-1][0] if values else None,
            "historical_value_revisions_between_consecutive_vintages": revised,
            "distinct_verified_timestamps_per_vintage": sorted({len(v[2]) for v in values}),
            "interpretation": "values stable; every vintage stamps every historical row with the run's verification time"}


def probe_etf_pack(repo: Path = REPO) -> dict[str, Any]:
    files = sorted((repo / ETF_PACK / "data").glob("*.csv"))
    commits = {f.name: len([l for l in _git(repo, "log", "--format=%H", "--", f.relative_to(repo).as_posix()).splitlines() if l.strip()]) for f in files}
    readme = (repo / ETF_PACK / "README.md").read_text()
    pack_btc = {r["date"]: r for r in load_etf_pack("btc", repo)[0]}
    row = pack_btc.get(FARSIDE_EVIDENCE["session"], {})
    return {"probe": "SV-ETF-HISTORY-PACK-VINTAGE", "path": ETF_PACK, "commits_per_partition": commits,
            "readme_states_no_publication_timestamps": "no per-row publication timestamps" in readme,
            "pack_value_for_documented_session": {"date": FARSIDE_EVIDENCE["session"], "Total": row.get("Total"), "IBIT": row.get("IBIT")},
            "documented_timing": FARSIDE_EVIDENCE}


def probe_copper_gold_revisions(repo: Path = REPO) -> dict[str, Any]:
    receipts = []
    for path in sorted((repo / CG_REVISIONS).glob("*.json")):
        r = json.loads(path.read_text())
        receipts.append({"receipt": path.name, "retrieved_at_utc": r["retrieved_at_utc"], "workbook_updated_on": r["source"]["workbook_updated_on"],
                         "last_period": r["coverage"]["last_period"], "revision_kind": r["revision_kind"],
                         "component_delta_types": sorted({d["change_type"] for d in r["component_deltas"]})})
    return {"probe": "SV-COPPER-GOLD-REVISION-RECEIPTS", "path": CG_REVISIONS, "receipts": receipts,
            "publication_evidence": cg_publication_evidence(repo)}


# =========================================================================== findings adjudication
# Mechanical results above are pure. The table below is the auditor's adjudication of
# them (severity, downstream, remediation route). It never changes a mechanical verdict.
ADJUDICATION: dict[str, dict[str, Any]] = {
    "RT-A06b-RESEARCH-COPPER-GOLD-EVENT-STUDY-PUBLICATION-KNOWLEDGE": {
        "finding_id": "E1X-F01", "severity": "MEDIUM",
        "feature": "copper/gold 2M regime signal events (existence, event_date, entry btc_price)",
        "causal_mechanism": "latest_settled_state/signal_events treat bar_end_timestamp (period end 23:59:59Z) as knowledge time and enter BTC at the end of the bar-end day; the World Bank monthly average is published later (owner receipts: July 2026 data on 2026-08-04, August 2026 data on 2026-09-02), so every signal event is anchored 1-4+ days before its input was knowable.",
        "affected_downstream": ["research/experiments/copper_gold_slow_cycle_shadow_v1/HISTORICAL_EVENT_STUDY_v2.json", "COPPER_GOLD_SLOW_CYCLE_SHADOW_v1 kill criterion K02", "any interpretation of turning_negative vs controls"],
        "historical_contamination": "HISTORICAL_EVENT_STUDY_v2.json signal-event summaries (anchor_results) are contaminated; objective_btc_peak_episodes state joins are NOT (24/24 invariant). Preserve v2; regenerate as a new version with a knowledge-time join.",
        "remediation_status": "NOT_IMPLEMENTED_CODEX_CANDIDATE_PREPARED",
        "remediation_route": "codex-research-copper-gold-event-study-knowledge-time-join-v1 (NOT_PERSISTED)",
    },
    "RT-A07-AT-PDLT-DISCOVERY-PRODUCTION": {
        "finding_id": "E1X-F02", "severity": "MEDIUM",
        "feature": "PDLT discovery label anchor 72h.start / 7d.start / 14d.start",
        "causal_mechanism": "locate() returns the last 4h candle whose OPEN is <= the CFGI timestamp and forward_stats() uses that candle's CLOSE (open+4h) as the decision-time start price, so the anchor is 0-4h after the signal (exactly 4h when timestamps are 4h-aligned). Live CFGI 4h rows are captured 1-15 minutes after their timestamp, i.e. the timestamp is the knowledge time.",
        "affected_downstream": ["PDLT discovery labels event72/event7d/event14d and fixed-calendar holdout screen", "any PDLT discovery report or frozen model derived from build_dataset", "PDLT reopen requirement INDEPENDENT_REVIEW_OF_DISCOVERY_REPAIR"],
        "historical_contamination": "Every historical PDLT discovery label ever produced by build_dataset. Real-data magnitude UNKNOWN (inputs in restricted plane; no discovery report or frozen model is present on main).",
        "remediation_status": "NOT_IMPLEMENTED_LANE_FROZEN_CODEX_CANDIDATE_PREPARED",
        "remediation_route": "codex-research-pdlt-discovery-completed-candle-anchor-v1 (NOT_PERSISTED); repair candidate proven in RT-A07-...-REPAIR_CANDIDATE_COMPLETED_CANDLE",
    },
    "RT-A09-AT-E3-N5-FACTOR-EXAMPLES-EVENT_TIME": {
        "finding_id": "E1X-F03", "severity": "LOW",
        "feature": "AT-E3-0019 N5 window features and entry anchor",
        "causal_mechanism": "examples are anchored at the CFGI event timestamp (features and entry price) while the row only became knowable at its first capture, 72-879 s later.",
        "affected_downstream": ["04_RESEARCH_LAB/auto_trading/experiments/E3_TRIAL_N5_INDEPENDENT_RESULT.json"],
        "historical_contamination": "N5 metrics carry a <=15 minute entry lookahead on a 24h horizon; the adjudication was INDEPENDENT_NOT_SUPPORTED, which a lookahead can only have biased toward support, so the conclusion stands.",
        "remediation_status": "NO_ACTION_CLOSED_TRIAL; anchor future factor tests at capture time (CAPTURE_TIME variant passes)",
        "remediation_route": "none",
    },
    "RT-A03b-BACKTEST-ETF-TRAILING-DOCUMENTED-FARSIDE-TIMING": {
        "finding_id": "E1X-F04", "severity": "MEDIUM",
        "feature": "backtest_engine ETF trailing features: feature_knowledge_available_at_utc",
        "causal_mechanism": "build_etf_trailing sets feature_knowledge_available_at_utc = not_before_session_close_utc, a lower bound. Documented case BTC 2026-07-16: at 03:41:48Z next day only 45.7 (IBIT not reported) was known; the complete 79.1 was verified at 06:34:00Z. The row claimed at 20:00Z is not knowable for >=7.7h (TRUE_FUTURE_LEAKAGE vs the claim) and its first value is later revised (SOURCE_VINTAGE_RISK).",
        "affected_downstream": ["backtest_engine W30 replay / run-engineering-gates", "any backtest that consumes the 2026-07-26 ETF history pack at session-close knowledge time"],
        "historical_contamination": "The ETF history pack is a single retrospective vintage without per-row publication times; only one session has in-repo publication evidence. Other sessions: UNKNOWN, not guessed. The pack README's own next-session labelling rule is consistent with the evidence; the W30 knowledge claim is not.",
        "remediation_status": "NOT_IMPLEMENTED_GOVERNANCE_CHOICE",
        "remediation_route": "framework owner: ETF knowledge-time policy (next-session rule or first verified complete retrieval)",
    },
    "RT-A12-DATA-PING-AUTO-MARKET-STATE-BTC-D-ASOF": {
        "finding_id": "E1X-F05", "severity": "LOW",
        "feature": "auto_market_state btc_dominance lane",
        "causal_mechanism": "each re-publication of BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv stamps every historical row with the run's source_verified_timestamp, so btc_d(now=t) over a later vintage fails closed (UNAVAILABLE) where the point-in-time vintage returns a value. Values: 0 revisions across 31 vintages.",
        "affected_downstream": ["historical replays of AUTO_MARKET_STATE_PACKET_v1 that do not pin the vintage commit"],
        "historical_contamination": "none (fail-closed; live path reads the pinned commit)",
        "remediation_status": "NO_ACTION; replays must bind the vintage commit",
        "remediation_route": "none",
    },
    "RT-A11-PULLBACK-LEDGER-REPLAY-LOADER-LATENT": {
        "finding_id": "E1X-F06", "severity": "INFO",
        "feature": "pullback_learning load_recent_observations (replay path only)",
        "causal_mechanism": "the loader returns the last 180 observation files on disk; replaying a historical observation over today's archive ranks it against later observations. The live writer only sees already-written files: 113/113 stored live ranks reproduce exactly from prior observations.",
        "affected_downstream": ["none (no replay caller)"], "historical_contamination": "none",
        "remediation_status": "NO_ACTION_LATENT", "remediation_route": "document: any future replay must pass an as-of directory view",
    },
    "RT-A14-MASTER-MONDAY-PREFLIGHT-SELECTORS-LATENT": {
        "finding_id": "E1X-F07", "severity": "INFO",
        "feature": "Master Monday preflight v3 latest_capture/latest_hourly",
        "causal_mechanism": "--freeze-start/--freeze-end are applied only to accepted DATA PING packets; the capture and hourly selectors always take the newest file. Both production workflows run live at freeze time without freeze arguments.",
        "affected_downstream": ["none today; any future historical Master Monday regeneration"], "historical_contamination": "none",
        "remediation_status": "NO_ACTION_LATENT", "remediation_route": "optional bounded candidate: apply the freeze window to both selectors or remove the unused arguments",
    },
    "WU-W05-CN-FORWARD-RANGE-PROTOCOL-WILDER-ATR14": {
        "finding_id": "E1X-W01", "severity": "LOW",
        "feature": "CN forward-range DUMB_1.5 / DUMB_2.0 baseline ATR14 (protocol B4)",
        "causal_mechanism": "Wilder ATR14 with an SMA seed is recursive; at the protocol minimum of 60 settled candles it differs from a long-history ATR by 1.9-6.4 USD (0.08-0.29%) on real Kraken data, changing the whole-USD ATR at every tested date; drift < 0.5 USD from about 120 candles.",
        "affected_downstream": ["CN forward range ledger baselines", "adjustment alpha vs DUMB", "kill criteria K1/K2"],
        "historical_contamination": "no executable owner on main; the FORWARD_RANGE_LEDGER_v0_1.csv holds only an example row",
        "remediation_status": "PROTOCOL_RECOMMENDATION", "remediation_route": "framework owner: pin the ATR history length (e.g. >=250 candles, drift 4e-9)",
    },
    "WU-W03-BACKTEST-HOURLY-VOL-AND-RUNNING-HIGH": {
        "finding_id": "E1X-W02", "severity": "LOW",
        "feature": "backtest_engine running_high_close / drawdown_from_running_high",
        "causal_mechanism": "start-anchored running maximum: with the W30 fixture length (168 hourly rows) the drawdown at 2026-09-14T06:00Z is -2.64% versus -5.09% with >=336 rows; realized vol windows converge exactly at 24/72 rows.",
        "affected_downstream": ["W30 golden fixture semantics"], "historical_contamination": "none (engineering fixture only)",
        "remediation_status": "DOCUMENT_SEMANTICS", "remediation_route": "label as drawdown since fixture start",
    },
    "WU-W01-COPPER-GOLD-2M-MACD-RSI": {
        "finding_id": "E1X-W03", "severity": "INFO",
        "feature": "copper/gold settled 2M MACD(12,26,9), RSI14, regime_state",
        "causal_mechanism": "EMA seeded at the first bar and Wilder RSI: production (history from 1960, >=612 months before any crypto-era bar) is converged below 1 ppm; a reproduction with 48 months flips regime_state (3 flips in 14 targets) and 192 months still drifts MACD by up to 5.7%.",
        "affected_downstream": ["any TDBC reproduction from a shorter history"], "historical_contamination": "none in production",
        "remediation_status": "NO_ACTION", "remediation_route": "none",
    },
}


def build_findings(report: dict[str, Any]) -> list[dict[str, Any]]:
    findings = []
    for result in report.get("right_truncation", []) + report.get("warmup", []):
        adj = ADJUDICATION.get(result["case_id"])
        if adj is None:
            continue
        example = None
        if result["test"] == "RIGHT_TRUNCATION_INVARIANCE" and result["mismatches"]:
            m = next((x for x in result["mismatches"] if x.get("minimization", {}).get("status") == "MINIMIZED"), result["mismatches"][0])
            diff = m["field_differences"][0]
            example = {"target_timestamp": m["target_utc"], "output_key": m["output_key"], "field": diff["field"],
                       "full_data_value": diff["full"], "truncated_data_value": diff["truncated"], "delta": diff["delta"],
                       "minimization": m.get("minimization")}
            classification = result["classifications"]
        else:
            classification = [result["classification"]]
        findings.append({
            "finding_id": adj["finding_id"], "case_id": result["case_id"], "test": result["test"],
            "feature_output": adj["feature"], "owner": result["owner"], "path": result["production_path"],
            "callable": result["production_callable"], "classification": classification, "severity": adj["severity"],
            "target_timestamp": example["target_timestamp"] if example else None,
            "full_data_value": example["full_data_value"] if example else None,
            "truncated_data_value": example["truncated_data_value"] if example else None,
            "delta": example["delta"] if example else None, "example": example,
            "mismatch_count": result.get("mismatch_count"), "contaminating_lead_seconds": result.get("contaminating_lead_seconds"),
            "warmup": None if result["test"] != "LEFT_TRUNCATION_WARMUP_CONVERGENCE" else {
                "worst_case_converged_from_warmup_records": result["worst_case_converged_from_warmup_records"],
                "production_history_records": result["production_history_records"],
                "categorical_flip_count": result["categorical_flip_count"],
                "max_rel_delta_by_field_and_warmup": result["max_rel_delta_by_field_and_warmup"]},
            "causal_mechanism": adj["causal_mechanism"], "affected_downstream_owners": adj["affected_downstream"],
            "historical_contamination": adj["historical_contamination"], "remediation_status": adj["remediation_status"],
            "remediation_route": adj["remediation_route"],
            "evidence_refs": [f"E1X_PRODUCTION_TEMPORAL_INTEGRITY_RESULT_v1.json#{result['case_id']}", result["production_path"]],
            "audited_main_sha": report.get("audited_main_sha"),
        })
    hourly = (report.get("source_vintage_probes") or {}).get("hourly") or {}
    if hourly.get("rows_seen"):
        findings.append({
            "finding_id": "E1X-S01", "case_id": "SV-HOURLY-DERIVED-COLUMN-VINTAGES", "test": "GIT_VINTAGE_PROBE",
            "feature_output": "hourly sequence derived columns (*_return_1h_pct, *_price_oi_state, long/short fields)",
            "owner": "daily_capture hourly sequence owner", "path": "scripts/daily_capture/build_hourly_sequence.py", "callable": "build_rows + merge_rows",
            "classification": ["SOURCE_VINTAGE_RISK"], "severity": "MEDIUM",
            "target_timestamp": None, "full_data_value": None, "truncated_data_value": None, "delta": None,
            "example": (hourly.get("examples") or [None])[0], "mismatch_count": hourly.get("rows_with_post_persistence_value_change"),
            "contaminating_lead_seconds": None, "warmup": None,
            "causal_mechanism": f"{hourly.get('rows_with_post_persistence_value_change')} of {hourly.get('rows_seen')} persisted hourly rows changed derived values after first persistence (last change on {hourly.get('last_change_commit_day')}); a historical replay of the working tree sees later vintages, not what consumers saw live.",
            "affected_downstream_owners": ["intraday_execution observations derived from return/oi columns", "any replay reading 03_DAILY_CAPTURE_LOGS/hourly derived columns for 2026-08-08..2026-09-13"],
            "historical_contamination": "PREVIOUSLY_KNOWN: AT-EXP-004 quarantine of *_return_1h_pct / *_oi_change_1h_pct / *_price_oi_state; remediation c180d3ca5 (2026-09-14) - no value change observed after it. Raw OHLCV unaffected.",
            "remediation_status": "DEDUPED_TO_AT_EXP_004_REMEDIATED_FORWARD", "remediation_route": "none new",
            "evidence_refs": ["E1X_PRODUCTION_TEMPORAL_INTEGRITY_RESULT_v1.json#source_vintage_probes.hourly", HOURLY_ROOT],
            "audited_main_sha": report.get("audited_main_sha"),
        })
    etf_case = next((r for r in report.get("right_truncation", []) if r["case_id"] == "RT-A03a-BACKTEST-ETF-TRAILING-CLAIMED-KNOWLEDGE"), None)
    if etf_case:
        malformed = {k: v.get("malformed_rows_excluded_by_backtest_adapter") for k, v in etf_case["data_binding"].items() if isinstance(v, dict)}
        closed = {k: v.get("nyse_closed_dates_present_as_rows_not_excluded") for k, v in etf_case["data_binding"].items() if isinstance(v, dict)}
        count = sum(len(v or []) for v in malformed.values()) + sum(len(v or []) for v in closed.values())
        if count:
            findings.append({
                "finding_id": "E1X-D01", "case_id": "INCIDENTAL-ETF-PACK-ROW-INTEGRITY", "test": "INCIDENTAL_DATA_INTEGRITY",
                "feature_output": "ETF history pack partitions (Total / fund columns)", "owner": "04_MARKET_LEARNING truth_layer ETF history pack",
                "path": ETF_PACK + "/data", "callable": "n/a", "classification": ["OUT_OF_TEMPORAL_SCOPE_DATA_INTEGRITY"], "severity": "MEDIUM",
                "target_timestamp": None, "full_data_value": None, "truncated_data_value": None, "delta": None,
                "example": {"malformed_rows": malformed, "nyse_closed_dates_recorded_as_sessions": closed}, "mismatch_count": count,
                "contaminating_lead_seconds": None, "warmup": None,
                "causal_mechanism": "(a) malformed rows carry one value fewer than the header: Total is missing and the last fund column holds the total, so fund attribution is shifted; the pack feature builder silently computes rolling features over NaN totals and backtest_engine.build_etf_trailing cannot consume them. (b) NYSE full-closure dates are recorded as 0.0-flow rows, so 'N-session' windows and streaks count non-sessions (a zero resets the signed streak).",
                "affected_downstream_owners": ["us_spot_btc_eth_etf_flow_trailing_features.csv", "any ETF-flow research using the pack"],
                "historical_contamination": "affected sessions only; not a temporal defect",
                "remediation_status": "OWNER_DATA_FIX_REQUIRED_NOT_IMPLEMENTED", "remediation_route": "pack owner: re-extract affected sessions from the source with provenance",
                "evidence_refs": [ETF_PACK + "/data"], "audited_main_sha": report.get("audited_main_sha"),
            })
    return sorted(findings, key=lambda f: f["finding_id"])


# =========================================================================== runner
def git_head(repo: Path = REPO) -> str | None:
    try:
        return _git(repo, "rev-parse", "HEAD").strip()
    except Exception:
        return None


def git_audited_main(repo: Path = REPO) -> str | None:
    """The main commit the audited code/data descend from (merge-base with origin/main, else HEAD)."""
    try:
        return _git(repo, "merge-base", "HEAD", "origin/main").strip()
    except Exception:
        return git_head(repo)


def build_cases(repo: Path = REPO, coinmetrics: Path | None = None, event_features: Path | None = None) -> tuple[list[RightTruncationCase], list[WarmupCase], list[RightTruncationCase], list[WarmupCase], dict[str, Any]]:
    rows, hb = load_hourly_rows(repo)
    etf = {"BTC": load_etf_pack("btc", repo)[0], "ETH": load_etf_pack("eth", repo)[0]}
    etf_b = {"btc": load_etf_pack("btc", repo)[1], "eth": load_etf_pack("eth", repo)[1]}
    cg_rows, cgb = load_cg_monthly(repo)
    obs, pb = load_pullback_observations(repo)
    notes: dict[str, Any] = {}
    production = [
        case_backtest_hourly_volatility(rows, hb), case_backtest_daily_utc(rows, hb),
        case_backtest_etf_trailing_claimed(etf, etf_b), case_backtest_etf_trailing_documented_publication(etf, etf_b),
        case_truth_layer_etf_features(etf, etf_b), case_copper_gold_owner(cg_rows, cgb),
    ]
    if coinmetrics is not None and coinmetrics.exists():
        es = _es()
        btc = es.load_btc(coinmetrics)
        published = json.loads((repo / EVENT_STUDY).read_text())
        peaks = [date.fromisoformat(p["event_day"]) for p in published["objective_btc_peak_episodes"]]
        features = event_features if event_features is not None else repo / CG_FEATURES
        knowledge, rule = cg_knowledge_time_factory(repo)
        binding = {"features_path": str(features.relative_to(repo)) if features.is_relative_to(repo) else features.name, "features_sha256": sha_file(features),
                   "btc_path": coinmetrics.name, "btc_sha256": sha_file(coinmetrics), "published_study": EVENT_STUDY}
        production.append(case_event_study(features, btc, peaks, knowledge, rule, binding, claimed_only=True))
        production.append(case_event_study(features, btc, peaks, knowledge, rule, binding, claimed_only=False))
        notes["event_study_impact"] = event_study_impact(features, btc, published, [0, 1, 2, 3, 4, 5, 7])
        notes["event_study_knowledge_rule"] = rule
    else:
        notes["event_study"] = "NOT_RUN: Coin Metrics btc.csv (pinned revision f1a36afb) not supplied"
    production += [case_pdlt("PRODUCTION"), case_pdlt("ALIGNED_TIMESTAMPS"), case_pdlt("REPAIR_CANDIDATE_COMPLETED_CANDLE"), case_pdlt("SEEDED_LEGACY_OPEN_TIME_ANCHOR"),
                   case_e2_features(rows, hb), case_n5("EVENT_TIME"), case_n5("CAPTURE_TIME"), case_intraday(rows, hb),
                   case_pullback_replay_loader(obs, pb), case_master_monday_selectors(rows, hb), case_spar()]
    try:
        production.append(case_btcd_asof(repo))
    except Exception as exc:  # git history unavailable (e.g. shallow clone)
        notes["btc_d_asof"] = f"NOT_RUN: {type(exc).__name__}: {exc}"
    warmups = [warmup_copper_gold_2m(cg_rows, cgb), warmup_copper_gold_monthly(cg_rows, cgb), warmup_backtest_hourly(rows, hb),
               warmup_backtest_etf(etf, etf_b), warmup_e2(rows, hb)]
    controls = [control_clean_trailing_mean(rows), control_seeded_negative_shift(rows), control_seeded_full_sample_zscore(cg_rows),
                control_seeded_centered_rolling(etf), control_seeded_bfill(rows), control_seeded_ema_right(rows),
                control_seeded_nondeterminism(rows), control_late_listing(obs), control_membership(obs, True), control_membership(obs, False),
                control_source_revision(cg_rows), case_pdlt("LABEL_TIME_TRUNCATION_CONTROL")]
    warmup_controls = [control_seeded_ema_warmup(rows, 150), control_seeded_ema_warmup(rows, 1000)]
    notes["pullback_live_stored_vs_pit"] = pullback_stored_vs_pit(obs)
    return production, warmups, controls, warmup_controls, notes


def run_all(repo: Path = REPO, coinmetrics: Path | None = None, kraken: Path | None = None, event_features: Path | None = None,
            git_probes: bool = True) -> dict[str, Any]:
    production, warmups, controls, warmup_controls, notes = build_cases(repo, coinmetrics, event_features)
    if kraken is not None and kraken.exists():
        warmups.append(warmup_cn_atr(kraken))
    else:
        notes["cn_atr_warmup"] = "NOT_RUN: Kraken OHLC payload not supplied"
    control_results = [run_right_truncation(c) for c in controls] + [run_warmup(c) for c in warmup_controls]
    suite_valid = all(r["expectation_met"] for r in control_results)
    production_results = [run_right_truncation(c) for c in production] if suite_valid else []
    warmup_results = [run_warmup(c) for c in warmups] if suite_valid else []
    probes = {}
    if git_probes and suite_valid:
        for name, fn in (("hourly", probe_hourly_vintages), ("btc_d", probe_btcd_vintages), ("etf_pack", probe_etf_pack), ("copper_gold", probe_copper_gold_revisions)):
            try:
                probes[name] = fn(repo)
            except Exception as exc:
                probes[name] = {"status": "NOT_RUN", "reason": f"{type(exc).__name__}: {exc}"}
    return {
        "contract": CONTRACT, "experiment_id": EXPERIMENT_ID, "parent_experiment_id": PARENT_EXPERIMENT_ID,
        "existing_owner_extended": "scripts/experiments/strategy_factor_leakage_e1.py", "parallel_engine_created": False,
        "audited_main_sha": git_audited_main(repo),
        "suite_validity": "SUITE_VALID" if suite_valid else "SUITE_INVALID",
        "controls": control_results, "right_truncation": production_results, "warmup": warmup_results,
        "source_vintage_probes": probes, "notes": notes, "authority": AUTHORITY,
        "classification_vocabulary": list(CLASSES),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--coinmetrics-btc", type=Path, help="csv/btc.csv from coinmetrics/data@f1a36afb962731c387bb03982758ab0103063da5")
    parser.add_argument("--event-features", type=Path, help="settled_2m_features.csv vintage used by the published event study")
    parser.add_argument("--kraken-ohlc", type=Path, help="Kraken public OHLC XBTUSD interval=1440 JSON payload")
    parser.add_argument("--no-git-probes", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--findings-output", type=Path, help="JSONL: one adjudicated finding per line")
    args = parser.parse_args()
    report = run_all(REPO, args.coinmetrics_btc, args.kraken_ohlc, args.event_features, not args.no_git_probes)
    payload = json.dumps(report, sort_keys=True, indent=1, default=_json_default)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n")
    if args.findings_output:
        args.findings_output.parent.mkdir(parents=True, exist_ok=True)
        args.findings_output.write_text("".join(json.dumps(f, sort_keys=True, default=_json_default) + "\n" for f in build_findings(report)))
    summary = {"suite_validity": report["suite_validity"], "audited_main_sha": report["audited_main_sha"],
               "controls": {r["case_id"]: r.get("expectation_met") for r in report["controls"]},
               "right_truncation": {r["case_id"]: [r["observed"], r["classifications"]] for r in report["right_truncation"]},
               "warmup": {r["case_id"]: r["classification"] for r in report["warmup"]}}
    print(json.dumps(summary, indent=1, sort_keys=True))
    if report["suite_validity"] != "SUITE_VALID":
        raise SystemExit(2)


if __name__ == "__main__":
    main()