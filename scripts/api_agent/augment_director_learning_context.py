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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--context", type=Path, required=True)
    parser.add_argument("--experiment-registry", type=Path, default=DEFAULT_EXPERIMENT_REGISTRY)
    parser.add_argument("--btcd", type=Path, default=DEFAULT_BTCD)
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

    context["learning_context_provenance"] = provenance
    context["context_routing_contract"] = {
        "contract": "DIRECTOR_CONTEXT_ROUTING_v1",
        "principle": "COLLECTED_DATA_IS_NOT_AVAILABLE_TO_AN_AGENT_UNLESS_PRESENT_IN_CONTEXT",
        "required_context_families": [
            "latest_capture", "api_intelligence_v2", "btc_dominance", "experiment_learning"
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
