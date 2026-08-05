from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

COPENHAGEN = ZoneInfo("Europe/Copenhagen")


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def ts(raw: Any) -> datetime:
    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(raw, timezone.utc)
    return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).astimezone(timezone.utc)


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


def load_experiment_learning(registry_path: Path, outcome_root: Path, start: datetime, end: datetime) -> dict[str, Any]:
    unavailable = {
        "status": "UNAVAILABLE",
        "authority": "SHADOW_ONLY_NO_AUTOMATIC_PROMOTION",
        "candidate_count": 0,
        "state_counts": {},
        "active_candidates": [],
        "latent_candidate_count": 0,
        "new_matured_outcomes": [],
    }
    if not registry_path.exists():
        return unavailable
    try:
        registry = load_json(registry_path)
    except Exception:
        return {**unavailable, "status": "INVALID_REGISTRY"}
    active_states = {
        "WAITING_FOR_MATURITY",
        "FIRED_NO_TARGET",
        "MATURED_SUPPORTED",
        "MATURED_NOT_SUPPORTED",
        "MATURED_INCONCLUSIVE",
        "GOVERNANCE_REVIEW_PERMITTED",
    }
    candidates = [row for row in registry.get("candidates", []) if isinstance(row, dict)]
    active = [row for row in candidates if row.get("state") in active_states]
    active.sort(key=lambda row: (str(row.get("state")), str(row.get("created_at_utc"))), reverse=True)
    outcomes = []
    for path in outcome_root.rglob("*.json") if outcome_root.exists() else []:
        try:
            value = load_json(path)
        except Exception:
            continue
        if value.get("contract") != "MATURED_OUTCOME_v2":
            continue
        created = value.get("created_at_utc")
        if created is None:
            continue
        try:
            when = ts(created)
        except Exception:
            continue
        if not (start <= when < end):
            continue
        outcomes.append({
            "forecast_id": value.get("forecast_id"),
            "status": value.get("status"),
            "result": value.get("result"),
            "reason": value.get("reason"),
            "return_pct": value.get("return_pct"),
            "evidence_lag_hours": value.get("evidence_lag_hours"),
            "created_at_utc": created,
            "path": str(path),
            "outcome_sha256": hashlib.sha256(canonical(value)).hexdigest(),
        })
    outcomes.sort(key=lambda row: str(row.get("created_at_utc")))
    latent = sum(row.get("state") in {"PROPOSED", "WAITING_FOR_DATA", "WAITING_FOR_MAPPING", "INCUBATING"} for row in candidates)
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
        "new_matured_outcomes": outcomes,
        "weekly_review_rule": "Review new prospective outcomes, severe failures, censored evidence and control comparisons. Strange or dormant hypotheses remain retained but receive no authority without mature evidence.",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weekly-pointer", type=Path, required=True)
    ap.add_argument("--daily-output-root", type=Path, required=True)
    ap.add_argument("--freeze-file", type=Path, required=True)
    ap.add_argument("--legacy-root", type=Path)
    ap.add_argument("--experiment-registry", type=Path, default=Path("research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"))
    ap.add_argument("--experiment-outcome-root", type=Path, default=Path("research/framework_memory/outcome_memory"))
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    weekly = load_json(args.weekly_pointer)
    freeze = load_json(args.freeze_file)
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
        "contract": "WEEKLY_API_CALIBRATION_CONTEXT_v5",
        "authority": "SHADOW_ONLY",
        "iso_year": freeze["iso_year"],
        "iso_week": freeze["iso_week"],
        "evidence_timezone": "Europe/Copenhagen",
        "window_start_utc": freeze["window_start_utc"],
        "window_end_utc": freeze["window_end_utc"],
        "freeze_sha256": freeze["freeze_sha256"],
        "weekly_capture_pack": weekly,
        "daily_director_rows": outputs,
        "daily_director_count": len(outputs),
        "legacy_research_context": load_legacy_context(args.legacy_root),
        "experiment_learning": load_experiment_learning(args.experiment_registry, args.experiment_outcome_root, start, end),
        "selection_rule": "latest eligible row per Europe/Copenhagen local date within frozen local week, deduplicated by timestamp and output hash",
        "handoff_targets": ["RAW_WEEKLY_CALIBRATION", "FORECAST_LEDGER", "MASTER_MONDAY_PREP", "SPECIALIST_REVIEW", "EXPERIMENT_GOVERNANCE_REVIEW"],
        "rules": [
            "Do not rewrite frozen forecasts.",
            "Separate data quality from market evidence.",
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
        "legacy_hypotheses": len(context["legacy_research_context"]["hypotheses"]),
        "experiment_candidates": context["experiment_learning"]["candidate_count"],
        "new_matured_experiment_outcomes": len(context["experiment_learning"]["new_matured_outcomes"]),
        "context_hash": context["context_hash"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
