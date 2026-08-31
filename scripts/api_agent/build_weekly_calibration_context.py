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


def find_time(output: dict[str, Any], receipt: dict[str, Any] | None) -> datetime | None:
    for source in (receipt or {}, output):
        for key in ("captured_at_utc", "created_at_utc", "generated_at_utc", "freeze_utc", "response_created_at_utc", "created_unix"):
            if source.get(key) is not None:
                try:
                    return ts(source[key])
                except Exception:
                    pass
    return None


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
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    freeze = load_json(args.freeze_file)
    preflight_file = args.preflight_file or args.freeze_file.with_name("MASTER_MONDAY_GAP_FILL_PACKAGE.json")
    weekly_owned = load_weekly_owned_context(args.weekly_pointer, args.capture_root, preflight_file, require_preflight=args.require_preflight)
    start = ts(freeze["window_start_utc"])
    end = ts(freeze["window_end_utc"])
    candidates = []
    seen = set()
    for path in args.daily_output_root.rglob("DAILY_DIRECTOR_OUTPUT.json"):
        try:
            output = load_json(path)
        except Exception:
            continue
        receipt_path = path.with_name("DAILY_DIRECTOR_RECEIPT.json")
        receipt = load_json(receipt_path) if receipt_path.exists() else None
        when = find_time(output, receipt)
        if not when or not (start <= when < end):
            continue
        output_hash = output.get("output_hash") or hashlib.sha256(canonical(output)).hexdigest()
        key = (when.isoformat(), output_hash)
        if key in seen:
            continue
        seen.add(key)
        candidates.append((when, path, output, receipt, output_hash))
    candidates.sort(key=lambda row: row[0])
    by_day = {}
    for row in candidates:
        local_day = row[0].astimezone(COPENHAGEN).date().isoformat()
        by_day[local_day] = row
    outputs = []
    for day, row in sorted(by_day.items()):
        when, path, output, receipt, _ = row
        outputs.append({
            "local_day_key": day,
            "timezone": "Europe/Copenhagen",
            "captured_at_utc": when.isoformat().replace("+00:00", "Z"),
            "captured_at_local": when.astimezone(COPENHAGEN).isoformat(),
            "path": str(path),
            "output_sha256": hashlib.sha256(canonical(output)).hexdigest(),
            "receipt_sha256": hashlib.sha256(canonical(receipt)).hexdigest() if receipt else None,
            "output": output,
            "receipt": receipt,
        })
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
        "daily_director_rows": outputs,
        "daily_director_count": len(outputs),
        "legacy_research_context": load_legacy_context(args.legacy_root),
        "experiment_learning": load_experiment_learning(args.experiment_registry, args.experiment_outcome_root, start, end),
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
            "No framework-state, model-weight or portfolio authority.",
        ],
    }
    context["context_hash"] = hashlib.sha256(canonical(context)).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical(context))
    print(json.dumps({
        "status": "PASS",
        "daily_rows": len(outputs),
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
