from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.api_agent.deep_research_executor import execute, load_json, write_json, zero_authority
except ModuleNotFoundError:
    from deep_research_executor import execute, load_json, write_json, zero_authority


SUPPLEMENTAL_INDEPENDENT_EVIDENCE_TASKS = {"DRQ-CUAU-001"}


def evidence_bundle_valid(task: dict[str, Any], owner_context: dict[str, Any] | None) -> tuple[bool, list[str]]:
    if task.get("research_id") not in SUPPLEMENTAL_INDEPENDENT_EVIDENCE_TASKS:
        return True, []
    if not isinstance(owner_context, dict):
        return False, ["INDEPENDENT_EVIDENCE_BUNDLE_MISSING"]
    required = {
        "evidence_bundle_id",
        "captured_at_utc",
        "source_series",
        "source_provenance",
        "source_hashes",
    }
    missing = sorted(field for field in required if not owner_context.get(field))
    source_series = owner_context.get("source_series")
    if not missing and (not isinstance(source_series, dict) or not source_series.get("copper") or not source_series.get("gold")):
        missing.append("COPPER_AND_GOLD_SERIES_REQUIRED")
    hashes = owner_context.get("source_hashes")
    if not missing and (not isinstance(hashes, dict) or not hashes.get("copper") or not hashes.get("gold")):
        missing.append("COPPER_AND_GOLD_SOURCE_HASHES_REQUIRED")
    provenance = owner_context.get("source_provenance")
    if not missing and (not isinstance(provenance, dict) or not provenance.get("copper") or not provenance.get("gold")):
        missing.append("COPPER_AND_GOLD_PROVENANCE_REQUIRED")
    return not missing, missing


def blocked_preflight(task: dict[str, Any], reasons: list[str]) -> dict[str, Any]:
    return {
        "contract": "DEEP_RESEARCH_COMPLETION_RECEIPT_v1",
        "research_id": task.get("research_id"),
        "status": "BLOCKED",
        "reason": "INDEPENDENT_SERIES_EVIDENCE_REQUIRED",
        "preflight_reasons": reasons,
        "automatic_integration_performed": False,
        "openai_estimated_cost_usd": 0.0,
        "authority": zero_authority(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed preflight and entry point for one bounded Deep Research task.")
    parser.add_argument("--task", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--provider-scorecard", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--supplemental-task", type=Path, required=True)
    parser.add_argument("--owner-context", type=Path)
    parser.add_argument("--coverage-health", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    task = load_json(args.task)
    owner_context = load_json(args.owner_context) if args.owner_context else None
    valid, reasons = evidence_bundle_valid(task, owner_context)
    if not valid:
        completion = blocked_preflight(task, reasons)
        write_json(args.output_dir / "completion_receipt.json", completion)
        print(json.dumps(completion, sort_keys=True))
        return 78

    completion = execute(
        task,
        load_json(args.queue),
        load_json(args.state),
        load_json(args.provider_scorecard),
        load_json(args.policy),
        load_json(args.supplemental_task),
        args.output_dir,
        owner_context,
        load_json(args.coverage_health) if args.coverage_health else None,
    )
    print(json.dumps(completion, sort_keys=True))
    return 0 if completion.get("status") == "COMPLETE" else 78


if __name__ == "__main__":
    raise SystemExit(main())
