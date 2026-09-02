#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_EXPERIMENT_REGISTRY = Path("research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json")
DEFAULT_BTCD = Path("03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv")
DEFAULT_EXIT_CALIBRATION = Path("research/framework_memory/action_compass_calibration/LATEST_EXIT_WARNING_CALIBRATION.json")
DEFAULT_RESEARCH_META = Path("00_ARCHIVE_CONTROL/research_governance_v1/meta_orchestrator_v1/STATE.json")
DEFAULT_RESEARCH_MEMORY = Path("00_ARCHIVE_CONTROL/research_governance_v1/memory_novelty_v1/STATE.json")
DEFAULT_RESEARCH_VOI = Path("00_ARCHIVE_CONTROL/research_governance_v1/decision_impact_v1/STATE.json")


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def experiment_learning(path: Path) -> dict[str, Any]:
    value = load_json(path)
    rows = value.get("candidates") if isinstance(value.get("candidates"), list) else []
    counts: Counter[str] = Counter()
    matured: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        state = str(row.get("state") or "UNKNOWN")
        counts[state] += 1
        if state in {"MATURED_SUPPORTED", "MATURED_NOT_SUPPORTED", "MATURED_INCONCLUSIVE"}:
            matured.append({
                "candidate_id": row.get("candidate_id"),
                "kind": row.get("kind"),
                "state": state,
                "title": row.get("title"),
                "matured_outcome_count": row.get("matured_outcome_count"),
                "observation_count": row.get("observation_count"),
            })
    rank = {"MATURED_SUPPORTED": 0, "MATURED_NOT_SUPPORTED": 1, "MATURED_INCONCLUSIVE": 2}
    matured.sort(key=lambda row: (rank.get(str(row.get("state")), 9), str(row.get("candidate_id") or "")))
    return {
        "authority": value.get("authority"),
        "candidate_count": value.get("candidate_count", len(rows)),
        "state_counts": dict(sorted(counts.items())),
        "decision_relevant_matured_examples": matured[:20],
        "instruction": "SUPPORTED and NOT_SUPPORTED outcomes are prior learning/counterevidence only. INCONCLUSIVE is never support. No automatic promotion.",
    }


def btc_dominance(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("BTC dominance owner CSV is empty")
    return {
        "status": "READY",
        "row_count": len(rows),
        "latest": rows[-1],
        "authority": "RESEARCH_CONTEXT_ONLY_NO_PORTFOLIO_AUTHORITY",
    }


def exit_warning_calibration(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "UNAVAILABLE_NO_MATERIALIZED_REPORT"}
    try:
        value = load_json(path)
    except Exception:
        return {"status": "UNAVAILABLE_INVALID"}
    return value


def _research_firewall_valid(value: dict[str, Any]) -> bool:
    if value.get("authority") != "RESEARCH_ONLY_NON_CANONICAL":
        return False
    for key in (
        "canonical_effect",
        "portfolio_execution",
        "paid_data_authorized",
        "deep_research_authorized",
        "external_provider_calls_authorized",
    ):
        if value.get(key) is True:
            return False
    return True


def _compact_queue(rows: Any, limit: int = 8) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    allowed = (
        "orchestrator_action", "source", "specialist_action", "action", "target",
        "impact_tier", "decision_surface", "execution_mode", "novelty_verdict", "reason",
    )
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        out.append({key: row.get(key) for key in allowed if key in row})
        if len(out) >= limit:
            break
    return out


def research_governance_learning(meta_path: Path, memory_path: Path, voi_path: Path) -> dict[str, Any]:
    paths = {"meta": meta_path, "memory": memory_path, "decision_impact": voi_path}
    missing = [name for name, path in paths.items() if not path.exists()]
    if missing:
        return {
            "status": "UNAVAILABLE",
            "reason": "RESEARCH_GOVERNANCE_STATE_MISSING",
            "missing": sorted(missing),
        }
    try:
        meta = load_json(meta_path)
        memory = load_json(memory_path)
        voi = load_json(voi_path)
    except Exception as exc:
        return {
            "status": "BLOCKED_INVALID_STATE",
            "reason": str(exc),
        }
    invalid = [name for name, value in (("meta", meta), ("memory", memory), ("decision_impact", voi)) if not _research_firewall_valid(value)]
    if invalid:
        return {
            "status": "BLOCKED_AUTHORITY_FIREWALL",
            "invalid_states": invalid,
            "instruction": "Do not use research-governance state when research-only authority invariants fail.",
        }
    return {
        "status": "READY",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "canonical_effect": False,
        "portfolio_execution": False,
        "meta_orchestrator": {
            "primary_action": meta.get("primary_action"),
            "primary_source": meta.get("primary_source"),
            "primary_target": meta.get("primary_target"),
            "primary_execution_mode": meta.get("primary_execution_mode"),
            "reason": meta.get("reason"),
            "sentinel_verdict": meta.get("sentinel_verdict"),
            "binding_integrity": meta.get("binding_integrity"),
            "active_heavy_workstreams": _compact_queue(meta.get("active_heavy_workstreams"), 3),
            "queue": _compact_queue(meta.get("queue"), 8),
        },
        "memory_novelty": {
            "selected_verdict": memory.get("selected_verdict"),
            "selected_source": memory.get("selected_source"),
            "selected_action": memory.get("selected_action"),
            "selected_target": memory.get("selected_target"),
            "reason": memory.get("reason"),
            "proposal_n": memory.get("proposal_n"),
        },
        "decision_impact": {
            "selected_source": voi.get("selected_source"),
            "selected_action": voi.get("selected_action"),
            "selected_target": voi.get("selected_target"),
            "selected_impact_tier": voi.get("selected_impact_tier"),
            "selected_decision_surface": voi.get("selected_decision_surface"),
            "reason": voi.get("reason"),
            "queue": _compact_queue(voi.get("queue"), 8),
        },
        "instruction": (
            "Treat this as prior research/falsification and research-priority context only. "
            "It may change which questions deserve attention or provide counterevidence, but it has no automatic canonical, market-rule, or portfolio authority. "
            "Duplicate/blocked research states are negative routing evidence, not support."
        ),
        "closure": "ROUTED_TO_FUTURE_DIRECTOR_CONTEXT",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--experiment-registry", type=Path, default=DEFAULT_EXPERIMENT_REGISTRY)
    parser.add_argument("--btcd", type=Path, default=DEFAULT_BTCD)
    parser.add_argument("--exit-calibration", type=Path, default=DEFAULT_EXIT_CALIBRATION)
    parser.add_argument("--research-meta", type=Path, default=DEFAULT_RESEARCH_META)
    parser.add_argument("--research-memory", type=Path, default=DEFAULT_RESEARCH_MEMORY)
    parser.add_argument("--research-voi", type=Path, default=DEFAULT_RESEARCH_VOI)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    context = load_json(args.context)
    provenance: list[dict[str, str]] = []

    if args.experiment_registry.exists():
        context["experiment_learning"] = experiment_learning(args.experiment_registry)
        provenance.append({"field": "experiment_learning", "path": str(args.experiment_registry), "sha256": sha256(args.experiment_registry)})
    else:
        context["experiment_learning"] = {"status": "UNAVAILABLE", "reason": "EXPERIMENT_REGISTRY_MISSING"}

    if args.btcd.exists():
        context["btc_dominance"] = btc_dominance(args.btcd)
        provenance.append({"field": "btc_dominance", "path": str(args.btcd), "sha256": sha256(args.btcd)})
    else:
        context["btc_dominance"] = {"status": "UNAVAILABLE", "reason": "BTCD_OWNER_MISSING"}

    context["action_compass_exit_calibration"] = exit_warning_calibration(args.exit_calibration)
    if args.exit_calibration.exists():
        try:
            load_json(args.exit_calibration)
        except Exception:
            pass
        else:
            provenance.append({"field": "action_compass_exit_calibration", "path": str(args.exit_calibration), "sha256": sha256(args.exit_calibration)})

    context["research_governance_learning"] = research_governance_learning(args.research_meta, args.research_memory, args.research_voi)
    for name, path in (("research_meta", args.research_meta), ("research_memory", args.research_memory), ("research_voi", args.research_voi)):
        if path.exists():
            provenance.append({"field": name, "path": str(path), "sha256": sha256(path)})

    context["learning_context_provenance"] = provenance
    context["context_routing_contract"] = {
        "contract": "DIRECTOR_CONTEXT_ROUTING_v1",
        "principle": "COLLECTED_DATA_IS_NOT_AVAILABLE_TO_AN_AGENT_UNLESS_PRESENT_IN_CONTEXT",
        "required_context_families": [
            "latest_capture", "api_intelligence_v2", "btc_dominance", "experiment_learning",
            "action_compass_exit_calibration", "research_governance_learning"
        ],
        "no_automatic_authority_promotion": True,
        "missingness_rule": "NEVER_DESCRIBE_A_PRESENT_CONTEXT_FAMILY_AS_MISSING",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(context, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "routed": [row["field"] for row in provenance]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
