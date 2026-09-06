from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

COPENHAGEN = ZoneInfo("Europe/Copenhagen")
DIRECTOR_TIME_FIELDS = (
    "captured_at_utc",
    "created_at_utc",
    "generated_at_utc",
    "freeze_utc",
    "response_created_at_utc",
    "created_unix",
)
DIRECTOR_COMPACT_EVIDENCE_LIMIT = 2
DIRECTOR_COMPACT_FORECAST_LIMIT = 8


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load_json(path: Path) -> Any:
    def finite_float(raw: str) -> float:
        value = float(raw)
        if not math.isfinite(value):
            raise ValueError('NON_FINITE_JSON_NUMBER')
        return value
    def invalid_constant(raw: str) -> None:
        raise ValueError('NON_FINITE_JSON_NUMBER')
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    return json.loads(path.read_text(), parse_float=finite_float, parse_constant=invalid_constant,
                      object_pairs_hook=unique_object)


def ts(raw: Any) -> datetime:
    if type(raw) in (int, float):
        return datetime.fromtimestamp(raw, timezone.utc)
    if not isinstance(raw, str):
        raise ValueError('TIMESTAMP_TYPE_INVALID')
    value = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if value.utcoffset() is None:
        raise ValueError('TIMESTAMP_TIMEZONE_REQUIRED')
    return value.astimezone(timezone.utc)


def find_time_with_source(output: dict[str, Any], receipt: dict[str, Any] | None) -> tuple[datetime | None, str | None]:
    for source_name, source in (("receipt", receipt or {}), ("output", output)):
        if not isinstance(source, dict):
            continue
        for key in DIRECTOR_TIME_FIELDS:
            if source.get(key) is not None:
                try:
                    return ts(source[key]), f"{source_name}.{key}"
                except Exception:
                    pass
    return None, None


def find_time(output: dict[str, Any], receipt: dict[str, Any] | None) -> datetime | None:
    return find_time_with_source(output, receipt)[0]


def compact_text_items(value: Any, *, limit: int = DIRECTOR_COMPACT_EVIDENCE_LIMIT) -> tuple[list[str], int, bool]:
    if not isinstance(value, list):
        return [], 0, False
    items = [item for item in value if isinstance(item, str)]
    return items[:limit], len(items), len(items) > limit


def compact_forecast_candidates(value: Any) -> tuple[list[dict[str, Any]], int, bool]:
    if not isinstance(value, list):
        return [], 0, False
    allowed = (
        "metric_path",
        "horizon_days",
        "direction",
        "target_mode",
        "target_value",
        "threshold_pct",
        "range_low",
        "range_high",
    )
    rows = []
    for item in value:
        if not isinstance(item, dict):
            continue
        rows.append({key: item.get(key) for key in allowed if key in item})
    return rows[:DIRECTOR_COMPACT_FORECAST_LIMIT], len(rows), len(rows) > DIRECTOR_COMPACT_FORECAST_LIMIT


def parse_cycle_header(output: dict[str, Any]) -> dict[str, Any]:
    summary = output.get("summary")
    result = {
        "cycle_header": None,
        "phase": None,
        "warning": None,
        "direction": None,
        "confidence": None,
    }
    if not isinstance(summary, str) or not summary:
        return result
    header = summary.splitlines()[0].strip()
    if not header.startswith("CYCLE_HEADER"):
        return result
    result["cycle_header"] = header
    allowed = {
        "PHASE": "phase",
        "WARNING": "warning",
        "DIRECTION": "direction",
        "CONFIDENCE": "confidence",
    }
    for part in header.split("|")[1:]:
        if "=" not in part:
            continue
        key, value = part.strip().split("=", 1)
        target = allowed.get(key.strip())
        if target:
            result[target] = value.strip() or None
    return result


def compact_director_row(row: dict[str, Any]) -> dict[str, Any]:
    when = row["when"]
    output = row["output"]
    receipt = row["receipt"]
    evidence_for, evidence_for_count, evidence_for_truncated = compact_text_items(output.get("evidence_for"))
    evidence_against, evidence_against_count, evidence_against_truncated = compact_text_items(output.get("evidence_against"))
    uncertainties, uncertainty_count, uncertainties_truncated = compact_text_items(output.get("uncertainties"))
    forecasts, forecast_count, forecasts_truncated = compact_forecast_candidates(output.get("forecast_candidates"))
    header = parse_cycle_header(output)
    binding_status = "PASS" if isinstance(receipt, dict) and row["receipt_sha256"] else "INCOMPLETE"
    return {
        "local_day_key": when.astimezone(COPENHAGEN).date().isoformat(),
        "timezone": "Europe/Copenhagen",
        "source_timestamp_utc": when.isoformat().replace("+00:00", "Z"),
        "source_timestamp_local": when.astimezone(COPENHAGEN).isoformat(),
        "source_timestamp_origin": row["timestamp_origin"],
        "path": str(row["path"]),
        "receipt_path": str(row["receipt_path"]),
        "output_sha256": row["output_sha256"],
        "receipt_sha256": row["receipt_sha256"],
        "declared_output_hash": (receipt or {}).get("output_hash") if isinstance(receipt, dict) else output.get("output_hash"),
        "binding_status": binding_status,
        "receipt_status": (receipt or {}).get("status") if isinstance(receipt, dict) else None,
        "task": (receipt or {}).get("task") if isinstance(receipt, dict) else None,
        **header,
        "forecast_candidate_count": forecast_count,
        "forecast_candidates": forecasts,
        "forecast_candidates_truncated": forecasts_truncated,
        "evidence_for_count": evidence_for_count,
        "key_evidence_for": evidence_for,
        "key_evidence_for_truncated": evidence_for_truncated,
        "evidence_against_count": evidence_against_count,
        "key_evidence_against": evidence_against,
        "key_evidence_against_truncated": evidence_against_truncated,
        "uncertainty_count": uncertainty_count,
        "key_uncertainties": uncertainties,
        "key_uncertainties_truncated": uncertainties_truncated,
    }


def collect_director_context(daily_output_root: Path, start: datetime, end: datetime) -> dict[str, Any]:
    raw_candidates: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    for path in sorted(daily_output_root.rglob("DAILY_DIRECTOR_OUTPUT.json")):
        try:
            output = load_json(path)
        except Exception:
            continue
        if not isinstance(output, dict):
            continue
        receipt_path = path.with_name("DAILY_DIRECTOR_RECEIPT.json")
        receipt: dict[str, Any] | None = None
        receipt_problem = None
        if receipt_path.exists():
            try:
                receipt_value = load_json(receipt_path)
                if isinstance(receipt_value, dict):
                    receipt = receipt_value
                else:
                    receipt_problem = "RECEIPT_INVALID"
            except Exception:
                receipt_problem = "RECEIPT_UNREADABLE"
        else:
            receipt_problem = "RECEIPT_MISSING"
        when, timestamp_origin = find_time_with_source(output, receipt)
        if not when or not (start <= when < end):
            continue
        output_sha256 = hashlib.sha256(canonical(output)).hexdigest()
        receipt_sha256 = hashlib.sha256(canonical(receipt)).hexdigest() if receipt else None
        row = {
            "when": when,
            "timestamp_origin": timestamp_origin,
            "path": path,
            "receipt_path": receipt_path,
            "output": output,
            "receipt": receipt,
            "output_sha256": output_sha256,
            "receipt_sha256": receipt_sha256,
            "legacy_output_hash": output.get("output_hash") or output_sha256,
        }
        raw_candidates.append(row)
        if receipt_problem:
            diagnostics.append({
                "path": str(path),
                "receipt_path": str(receipt_path),
                "source_timestamp_utc": when.isoformat().replace("+00:00", "Z"),
                "output_sha256": output_sha256,
                "reason": receipt_problem,
            })

    raw_candidates.sort(key=lambda row: (
        row["when"],
        row["output_sha256"],
        row["receipt_sha256"] or "",
        str(row["path"]),
    ))

    legacy_candidates = []
    legacy_seen = set()
    for row in raw_candidates:
        key = (row["when"].isoformat(), row["legacy_output_hash"])
        if key in legacy_seen:
            continue
        legacy_seen.add(key)
        legacy_candidates.append(row)

    by_day: dict[str, dict[str, Any]] = {}
    for row in legacy_candidates:
        local_day = row["when"].astimezone(COPENHAGEN).date().isoformat()
        by_day[local_day] = row
    outputs = []
    for day, row in sorted(by_day.items()):
        when = row["when"]
        outputs.append({
            "local_day_key": day,
            "timezone": "Europe/Copenhagen",
            "captured_at_utc": when.isoformat().replace("+00:00", "Z"),
            "captured_at_local": when.astimezone(COPENHAGEN).isoformat(),
            "path": str(row["path"]),
            "output_sha256": row["output_sha256"],
            "receipt_sha256": row["receipt_sha256"],
            "output": row["output"],
            "receipt": row["receipt"],
        })

    sequence = []
    intraday_seen = set()
    exact_duplicate_count = 0
    for row in raw_candidates:
        key = (row["when"].isoformat(), row["output_sha256"], row["receipt_sha256"])
        if key in intraday_seen:
            exact_duplicate_count += 1
            continue
        intraday_seen.add(key)
        sequence.append(compact_director_row(row))

    return {
        "daily_director_rows": outputs,
        "daily_director_count": len(outputs),
        "daily_director_intraday_sequence": sequence,
        "daily_director_intraday_count": len(sequence),
        "daily_director_intraday_source_count": len(raw_candidates),
        "daily_director_intraday_exact_duplicate_count": exact_duplicate_count,
        "daily_director_intraday_status": "COMPLETE" if not diagnostics else "INCOMPLETE",
        "daily_director_intraday_diagnostics": diagnostics,
        "daily_director_intraday_selection_rule": (
            "all eligible Director runs within the frozen UTC window, ordered by immutable source timestamp UTC "
            "with deterministic output-hash, receipt-hash and path tie-breakers; only exact "
            "timestamp+output_sha256+receipt_sha256 duplicates are collapsed"
        ),
    }


def load_legacy_context(root: Path | None) -> dict[str, Any]:
    unavailable = {
        "status": "UNAVAILABLE",
        "authority": "RESEARCH_CONTEXT_ONLY",
        "canonical_evidence": False,
        "hypotheses": [],
        "validation_queue": [],
    }
    if root is None or not root.exists():
        return unavailable
    try:
        hypotheses = []
        for raw in (root / "02_HYPOTHESIS_REGISTRY/ACTIVE_LEGACY_HYPOTHESES.jsonl").read_text(encoding="utf-8").splitlines():
            if not raw.strip():
                continue
            row = json.loads(raw)
            hypotheses.append({
                "hypothesis_id": row.get("legacy_observation_id"),
                "topic": row.get("topic"),
                "claim": row.get("claim"),
                "sensors": row.get("sensors", []),
                "horizon_claimed": row.get("horizon_claimed"),
                "legacy_ruling": row.get("legacy_ruling"),
                "canonical_evidence": False,
            })
        queue_value = load_json(root / "05_NEW_SYSTEM_CROSSWALK/PROSPECTIVE_VALIDATION_QUEUE.json")
        queue = [{
            "hypothesis_id": item.get("hypothesis_id"),
            "target_event": item.get("target_event"),
            "priority": item.get("priority"),
            "current_status": item.get("current_status"),
            "candidate_freeze_allowed": False,
            "automatic_promotion": False,
        } for item in queue_value.get("queue", []) if isinstance(item, dict)]
    except Exception:
        return {**unavailable, "status": "INVALID"}
    return {
        "status": "AVAILABLE_RESEARCH_ONLY",
        "authority": "RESEARCH_CONTEXT_ONLY",
        "canonical_evidence": False,
        "hypotheses": hypotheses,
        "validation_queue": queue,
        "weekly_review_rule": "For each hypothesis report MATCH, PARTIAL_MATCH, CONTRADICTION or NOT_EVALUABLE using current frozen evidence only.",
    }


def load_experiment_learning(registry_path: Path, outcome_root: Path, start: datetime, end: datetime,
                             *, repo_root: Path | None = None, forecast_root: Path | None = None) -> dict[str, Any]:
    repo_root = (repo_root or Path.cwd()).resolve()
    forecast_root = forecast_root or repo_root / 'research/framework_memory/forecast_memory'
    forecast_paths = None
    binding_cache = {}

    def bound_document(path: Path, expected: Any):
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in '0123456789abcdef' for c in expected):
            raise ValueError('BINDING_HASH_INVALID')
        path = path.resolve()
        if not path.is_relative_to(repo_root):
            raise ValueError('BINDING_PATH_OUTSIDE_REPOSITORY')
        if path not in binding_cache:
            document = load_json(path)
            binding_cache[path] = (document, hashlib.sha256(canonical(document)).hexdigest())
        document, actual = binding_cache[path]
        if actual != expected:
            raise ValueError('BINDING_HASH_MISMATCH_CURRENT_FILE')
        return document

    def verify_bindings(value):
        nonlocal forecast_paths
        if forecast_paths is None:
            forecast_paths = {}
            if not forecast_root.is_dir():
                raise ValueError('FORECAST_ROOT_UNAVAILABLE')
            def walk_error(exc):
                raise ValueError('FORECAST_DIRECTORY_UNREADABLE') from exc
            for directory, _, filenames in os.walk(forecast_root, onerror=walk_error):
                for filename in filenames:
                    if filename.endswith('.json'):
                        forecast_paths.setdefault(Path(filename).stem, []).append(Path(directory) / filename)
        candidates = forecast_paths.get(value['forecast_id'], [])
        if len(candidates) != 1:
            raise ValueError('FORECAST_BINDING_MISSING_OR_AMBIGUOUS')
        forecast = bound_document(candidates[0], value.get('forecast_sha256'))
        if not isinstance(forecast, dict) or forecast.get('contract') != 'FROZEN_FORECAST_v1' or forecast.get('forecast_id') != value['forecast_id']:
            raise ValueError('FORECAST_BINDING_CONTRACT_INVALID')
        path, digest = value.get('evidence_path'), value.get('evidence_sha256')
        if value['status'] == 'MATURED' or path is not None or digest is not None:
            if not isinstance(path, str) or not path or Path(path).name == 'LATEST.json':
                raise ValueError('EVIDENCE_BINDING_PATH_INVALID')
            bound_document(repo_root / path, digest)
        return str(candidates[0])

    def unavailable(status: str, reason: str) -> dict[str, Any]:
        return {
            "status": status,
            "unavailable_reason": reason,
            "authority": "SHADOW_ONLY_NO_AUTOMATIC_PROMOTION",
            "candidate_count": 0,
            "state_counts": {},
            "active_candidates": [],
            "latent_candidate_count": 0,
            "new_matured_outcomes": None,
            "matured_outcome_evidence_available": False,
        }

    if not registry_path.exists():
        return unavailable("UNAVAILABLE_REGISTRY_MISSING", "Experiment lifecycle registry does not exist.")
    try:
        registry = load_json(registry_path)
    except Exception:
        return unavailable("UNAVAILABLE_REGISTRY_UNREADABLE", "Experiment lifecycle registry is unreadable JSON.")
    if (
        not isinstance(registry, dict)
        or registry.get("contract") != "EXPERIMENT_LIFECYCLE_REGISTRY_v1"
        or not isinstance(registry.get("candidates"), list)
    ):
        return unavailable("UNAVAILABLE_REGISTRY_CONTRACT_INVALID", "Experiment lifecycle registry contract or candidates payload is invalid.")
    active_states = {
        "WAITING_FOR_MATURITY",
        "FIRED_NO_TARGET",
        "MATURED_SUPPORTED",
        "MATURED_NOT_SUPPORTED",
        "MATURED_INCONCLUSIVE",
        "GOVERNANCE_REVIEW_PERMITTED",
    }
    candidates = [row for row in registry.get("candidates", []) if isinstance(row, dict)]
    active = [row for row in candidates if isinstance(row.get("state"), str) and row['state'] in active_states]
    active.sort(key=lambda row: (str(row.get("state")), str(row.get("created_at_utc"))), reverse=True)
    outcomes = []
    diagnostics = []
    outcome_root_available = outcome_root.is_dir()
    if not outcome_root_available:
        diagnostics.append({'path': str(outcome_root), 'reason': 'OUTCOME_ROOT_UNAVAILABLE'})
    paths = []
    if outcome_root_available:
        def scan_error(exc):
            diagnostics.append({'path': str(exc.filename or outcome_root), 'reason': 'OUTCOME_DIRECTORY_UNREADABLE'})
        for directory, _, filenames in os.walk(outcome_root, onerror=scan_error):
            paths.extend(Path(directory) / name for name in filenames if name.endswith('.json'))
    for path in sorted(paths):
        try:
            value = load_json(path)
        except (OSError, UnicodeError, ValueError, RecursionError):
            diagnostics.append({'path': str(path), 'reason': 'OUTCOME_UNREADABLE'})
            continue
        if not isinstance(value, dict) or value.get("contract") not in ("MATURED_OUTCOME_v2", "MATURED_OUTCOME_v3"):
            diagnostics.append({'path': str(path), 'reason': 'OUTCOME_CONTRACT_UNSUPPORTED'})
            continue
        created = value.get("created_at_utc")
        try:
            when = ts(created)
        except (ValueError, OverflowError, OSError):
            diagnostics.append({'path': str(path), 'reason': 'OUTCOME_TIMESTAMP_INVALID'})
            continue
        if not (start <= when < end):
            continue
        if not isinstance(value.get('forecast_id'), str) or not value['forecast_id']:
            diagnostics.append({'path': str(path), 'reason': 'OUTCOME_FORECAST_ID_MISSING'})
            continue
        if value.get('status') == 'MATURED':
            measured = value.get('return_pct')
            try:
                valid_return = type(measured) in (int, float) and math.isfinite(measured)
            except OverflowError:
                valid_return = False
            if not valid_return or value.get('result') not in ('HIT', 'MISS'):
                diagnostics.append({'path': str(path), 'reason': 'MATURED_OUTCOME_FIELDS_INVALID'})
                continue
        elif value.get('status') == 'CENSORED':
            if not isinstance(value.get('reason'), str) or not value['reason'] or value.get('return_pct') is not None or value.get('result') is not None:
                diagnostics.append({'path': str(path), 'reason': 'CENSORED_OUTCOME_FIELDS_INVALID'})
                continue
        else:
            diagnostics.append({'path': str(path), 'reason': 'OUTCOME_STATUS_UNSUPPORTED'})
            continue
        try:
            forecast_path = verify_bindings(value)
        except (OSError, UnicodeError, ValueError, RecursionError) as exc:
            reason = str(exc) if isinstance(exc, ValueError) and str(exc).startswith(('BINDING_', 'FORECAST_', 'EVIDENCE_')) else 'BINDING_EVIDENCE_UNREADABLE'
            diagnostics.append({'path': str(path), 'reason': reason})
            continue
        outcomes.append({
            "source_contract": value['contract'],
            "source_authority": value.get('authority'),
            "forecast_id": value.get("forecast_id"),
            "forecast_sha256": value.get("forecast_sha256"),
            "forecast_path": forecast_path,
            "source_binding_verification": "CURRENT_FILE_CANONICAL_JSON_SHA256",
            "evidence_path": value.get("evidence_path"),
            "evidence_sha256": value.get("evidence_sha256"),
            "status": value.get("status"),
            "result": value.get("result"),
            "reason": value.get("reason"),
            "return_pct": value.get("return_pct"),
            "evidence_lag_hours": value.get("evidence_lag_hours"),
            "created_at_utc": when.isoformat().replace('+00:00', 'Z'),
            "path": str(path),
            "outcome_sha256": hashlib.sha256(canonical(value)).hexdigest(),
        })
    outcomes.sort(key=lambda row: str(row.get("created_at_utc")))
    latent = sum(row.get("state") in ("PROPOSED", "WAITING_FOR_DATA", "WAITING_FOR_MAPPING", "INCUBATING") for row in candidates)
    return {
        "status": "AVAILABLE",
        "authority": "SHADOW_ONLY_NO_AUTOMATIC_PROMOTION",
        "registry_generated_at_utc": registry.get("generated_at_utc"),
        "registry_sha256": hashlib.sha256(canonical(registry)).hexdigest(),
        "candidate_count": registry.get("candidate_count", len(candidates)),
        "state_counts": registry.get("state_counts", {}),
        "active_candidates": active[:50],
        "active_candidates_truncated": len(active) > 50,
        "latent_candidate_count": latent,
        "new_matured_outcomes": outcomes if outcome_root_available else None,
        "matured_outcome_evidence_available": outcome_root_available and not diagnostics,
        "outcome_ingestion_diagnostics": diagnostics,
        "outcome_ingestion_status": 'COMPLETE' if outcome_root_available and not diagnostics else 'INCOMPLETE',
        "outcome_scoring_performed": False,
        "weekly_review_rule": "Review new prospective outcomes, severe failures, censored evidence and control comparisons. Strange or dormant hypotheses remain retained but receive no authority without mature evidence.",
    }


def resolve_capture_path(capture_root: Path, value: Any) -> Path | None:
    if not value:
        return None
    path = Path(str(value))
    if path.is_absolute():
        return path
    if path.parts[:1] == (capture_root.name,):
        return capture_root.parent / path
    return capture_root / path


def unavailable_weekly_owned(pointer: dict[str, Any]) -> dict[str, Any]:
    return {
        "weekly_capture_pointer": pointer,
        "weekly_capture_pack": None,
        "weekly_sequence_facts": None,
        "master_monday_preflight": {
            "status": "UNAVAILABLE_NOT_SUPPLIED",
            "packet": None,
            "meta": None,
            "required_capabilities": None,
            "settled_week": None,
            "final_168h_market_close_available": False,
            "breadth": None,
            "derivatives": None,
            "etf": None,
            "cfgi": None,
            "macro": None,
            "missing": [{"field": "master_monday_preflight", "blocking_level": "UNAVAILABLE_IN_CALLER_CONTEXT"}],
            "package_sha256": None,
        },
    }


def load_weekly_owned_context(weekly_pointer_path: Path, capture_root: Path, preflight_path: Path, *, require_preflight: bool = False) -> dict[str, Any]:
    pointer = load_json(weekly_pointer_path)
    if not preflight_path.exists():
        if require_preflight:
            raise FileNotFoundError(f"REQUIRED_MASTER_MONDAY_PREFLIGHT_MISSING:{preflight_path}")
        return unavailable_weekly_owned(pointer)
    preflight = load_json(preflight_path)
    pack_path = resolve_capture_path(capture_root, pointer.get("path"))
    facts_path = resolve_capture_path(capture_root, pointer.get("sequence_facts_path"))
    pack = load_json(pack_path) if pack_path and pack_path.exists() else None
    facts = load_json(facts_path) if facts_path and facts_path.exists() else None
    settled_week = preflight.get("settled_week")
    final_168h = bool(
        isinstance(settled_week, dict)
        and settled_week.get("final") is True
        and settled_week.get("close_mode") == "FINAL_COMPLETED_ISO_WEEK"
        and settled_week.get("completeness") == "COMPLETE"
        and all(((settled_week.get("symbols") or {}).get(asset) or {}).get("hour_count") == 168 for asset in ("BTCUSDT", "ETHUSDT", "ETHBTC"))
    )
    return {
        "weekly_capture_pointer": pointer,
        "weekly_capture_pack": pack,
        "weekly_sequence_facts": facts,
        "master_monday_preflight": {
            "status": "AVAILABLE",
            "packet": preflight.get("packet"),
            "meta": preflight.get("meta"),
            "required_capabilities": (preflight.get("quality") or {}).get("required_capabilities"),
            "settled_week": settled_week,
            "final_168h_market_close_available": final_168h,
            "breadth": preflight.get("breadth"),
            "derivatives": preflight.get("derivatives"),
            "etf": preflight.get("etf"),
            "cfgi": preflight.get("cfgi"),
            "macro": preflight.get("macro"),
            "missing": preflight.get("missing", []),
            "package_sha256": preflight.get("package_sha256"),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weekly-pointer", type=Path, required=True)
    ap.add_argument("--capture-root", type=Path, default=Path("03_DAILY_CAPTURE_LOGS"))
    ap.add_argument("--preflight-file", type=Path)
    ap.add_argument("--require-preflight", action="store_true")
    ap.add_argument("--daily-output-root", type=Path, required=True)
    ap.add_argument("--freeze-file", type=Path, required=True)
    ap.add_argument("--legacy-root", type=Path)
    ap.add_argument("--experiment-registry", type=Path, default=Path("research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"))
    ap.add_argument("--experiment-outcome-root", type=Path, default=Path("research/framework_memory/outcome_memory"))
    ap.add_argument("--experiment-forecast-root", type=Path)
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    freeze = load_json(args.freeze_file)
    preflight_file = args.preflight_file or args.freeze_file.with_name("MASTER_MONDAY_GAP_FILL_PACKAGE.json")
    weekly_owned = load_weekly_owned_context(args.weekly_pointer, args.capture_root, preflight_file, require_preflight=args.require_preflight)
    start = ts(freeze["window_start_utc"])
    end = ts(freeze["window_end_utc"])
    director_context = collect_director_context(args.daily_output_root, start, end)
    context = {
        "contract": "WEEKLY_API_CALIBRATION_CONTEXT_v6",
        "authority": "SHADOW_ONLY",
        "iso_year": freeze["iso_year"],
        "iso_week": freeze["iso_week"],
        "evidence_timezone": "Europe/Copenhagen",
        "window_start_utc": freeze["window_start_utc"],
        "window_end_utc": freeze["window_end_utc"],
        "freeze_sha256": freeze["freeze_sha256"],
        **weekly_owned,
        **director_context,
        "legacy_research_context": load_legacy_context(args.legacy_root),
        "experiment_learning": load_experiment_learning(args.experiment_registry, args.experiment_outcome_root, start, end,
            repo_root=args.repo_root, forecast_root=args.experiment_forecast_root),
        "selection_rule": "latest eligible row per Europe/Copenhagen local date within frozen local week, deduplicated by timestamp and output hash",
        "handoff_targets": ["RAW_WEEKLY_CALIBRATION", "FORECAST_LEDGER", "MASTER_MONDAY_PREP", "SPECIALIST_REVIEW", "EXPERIMENT_GOVERNANCE_REVIEW"],
        "rules": [
            "Do not rewrite frozen forecasts.",
            "Separate data quality from market evidence.",
            "The preflight settled_week object is the authoritative completed-week price-path source when final_168h_market_close_available=true.",
            "A pre-v2.2 enriched-hourly gap must not be misreported as missing final price-path evidence when the final 168h market close is complete.",
            "Preserve the enriched sequence gap itself; do not fabricate retrospective OI, taker-flow or other non-price rows.",
            "Preserve disagreement, missingness and censored outcomes.",
            "Evaluate analysis and operational translation separately.",
            "Legacy research is a hypothesis prior only and cannot count as prospective evidence.",
            "Experiment learning may report evidence and review candidates but cannot promote rules automatically.",
            "Latent or strange hypotheses remain retained without affecting weekly conclusions unless new mature evidence exists.",
            "daily_director_rows remains latest-per-local-day for compatibility; daily_director_intraday_sequence is the compact ex-ante calibration timeline.",
            "The intraday Director sequence is shadow calibration context only and carries no framework-state, model-weight or portfolio authority.",
            "No framework-state, model-weight or portfolio authority.",
        ],
    }
    context["context_hash"] = hashlib.sha256(canonical(context)).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical(context))
    print(json.dumps({
        "status": "PASS",
        "daily_rows": director_context["daily_director_count"],
        "daily_intraday_rows": director_context["daily_director_intraday_count"],
        "daily_intraday_status": director_context["daily_director_intraday_status"],
        "preflight_context_status": weekly_owned["master_monday_preflight"].get("status"),
        "final_168h_market_close_available": weekly_owned["master_monday_preflight"]["final_168h_market_close_available"],
        "weekly_sequence_readiness": weekly_owned["weekly_capture_pointer"].get("readiness"),
        "legacy_hypotheses": len(context["legacy_research_context"]["hypotheses"]),
        "experiment_candidates": context["experiment_learning"]["candidate_count"],
        "new_matured_experiment_outcomes": len(context["experiment_learning"]["new_matured_outcomes"]) if isinstance(context["experiment_learning"].get("new_matured_outcomes"), list) else None,
        "context_hash": context["context_hash"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
