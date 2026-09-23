from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from statistics import median
from typing import Any

# Importable as a module, runnable as a script and collectable in isolation.
# experiment_lifecycle_scientific_admission does a bare import of
# experiment_lifecycle, so scripts/experiments must be available on sys.path.
# Direct script execution additionally needs the repository root.
_REPO_ROOT = Path(__file__).resolve().parents[2]
_EXPERIMENTS_DIR = Path(__file__).resolve().parent
for _path in (str(_REPO_ROOT), str(_EXPERIMENTS_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

from scripts.experiments.experiment_lifecycle_scientific_admission import semantic_spec  # noqa: E402

ALLOWED_RECOMMENDATIONS = {
    "KEEP",
    "MERGE_REVIEW",
    "RETIRE_REVIEW",
    "WAIT_FOR_DATA",
    "WAIT_FOR_MAPPING",
    "NEEDS_MORE_OUTCOMES",
}


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_candidates(root: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted(root.rglob("*.json")):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(value, dict) or value.get("contract") != "EXPERIMENT_CANDIDATE_v1":
            continue
        cid = str(value.get("candidate_id") or "")
        if cid:
            rows[cid] = value
    return rows


def strict_semantic_key(candidate: dict[str, Any]) -> str:
    spec = candidate.get("spec")
    if not isinstance(spec, dict):
        return ""
    return digest(semantic_spec(spec))


def review_key(candidate: dict[str, Any]) -> dict[str, Any]:
    spec = candidate.get("spec") if isinstance(candidate.get("spec"), dict) else {}
    semantic = semantic_spec(spec) if spec else {}
    return {
        "kind": semantic.get("kind"),
        "target_metric_path": semantic.get("target_metric_path"),
        "target_direction": semantic.get("target_direction"),
        "horizon_days": semantic.get("horizon_days"),
        "target_threshold_pct": semantic.get("target_threshold_pct"),
        "target_range_lower_pct": semantic.get("target_range_lower_pct"),
        "target_range_upper_pct": semantic.get("target_range_upper_pct"),
        "components": semantic.get("components") or [],
        "regime_dependency": semantic.get("regime_dependency"),
    }


def recommendation(row: dict[str, Any], semantic_group_size: int, high_zero_outcome_cutoff: int) -> str:
    state = str(row.get("state") or "")
    observations = int(row.get("observation_count") or 0)
    outcomes = int(row.get("matured_outcome_count") or 0)
    admission = str(row.get("scientific_admission_status") or "")
    if state == "WAITING_FOR_DATA":
        return "WAIT_FOR_DATA"
    if state == "WAITING_FOR_MAPPING":
        return "WAIT_FOR_MAPPING"
    if semantic_group_size > 1 or admission == "SEMANTIC_DUPLICATE_KEEP_SHADOW":
        return "MERGE_REVIEW"
    if state == "MATURED_INCONCLUSIVE":
        return "NEEDS_MORE_OUTCOMES"
    if state == "INCUBATING" and outcomes == 0 and observations >= high_zero_outcome_cutoff:
        return "NEEDS_MORE_OUTCOMES"
    if state == "MATURED_NOT_SUPPORTED":
        return "RETIRE_REVIEW"
    return "KEEP"


def build_review(registry: dict[str, Any], candidates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    rows = [row for row in registry.get("candidates", []) if isinstance(row, dict)]
    by_id = {str(row.get("candidate_id")): row for row in rows if row.get("candidate_id")}
    registry_id_rows: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        cid = str(row.get("candidate_id") or "")
        if cid:
            registry_id_rows.setdefault(cid, []).append(row)
    duplicate_candidate_id_rows = [
        {
            "candidate_id": cid,
            "row_count": len(items),
            "created_at_utc_values": sorted({str(item.get("created_at_utc") or "") for item in items}),
            "states": sorted({str(item.get("state") or "") for item in items}),
            "titles": sorted({str(item.get("title") or "") for item in items}),
            "review": "REGISTRY_DUPLICATE_ID_READ_ONLY_REVIEW",
            "automatic_action": False,
        }
        for cid, items in sorted(registry_id_rows.items())
        if len(items) > 1
    ]

    semantic_groups: dict[str, list[str]] = {}
    for cid, candidate in candidates.items():
        key = strict_semantic_key(candidate)
        if key and cid in by_id:
            semantic_groups.setdefault(key, []).append(cid)

    zero_outcome_incubating = sorted(
        [
            int(row.get("observation_count") or 0)
            for row in rows
            if row.get("state") == "INCUBATING" and int(row.get("matured_outcome_count") or 0) == 0
        ]
    )
    if zero_outcome_incubating:
        mid = median(zero_outcome_incubating)
        high_cutoff = max(1, int(mid))
    else:
        high_cutoff = 1

    reviewed = []
    for cid, row in sorted(by_id.items()):
        candidate = candidates.get(cid)
        semantic_key = strict_semantic_key(candidate) if candidate else ""
        group_size = len(semantic_groups.get(semantic_key, [])) if semantic_key else 1
        rec = recommendation(row, group_size, high_cutoff)
        if rec not in ALLOWED_RECOMMENDATIONS:
            raise ValueError("invalid recommendation")
        reviewed.append({
            "candidate_id": cid,
            "state": row.get("state"),
            "scientific_admission_status": row.get("scientific_admission_status"),
            "observation_count": int(row.get("observation_count") or 0),
            "matured_outcome_count": int(row.get("matured_outcome_count") or 0),
            "semantic_fingerprint": row.get("semantic_fingerprint"),
            "strict_semantic_key": semantic_key or None,
            "strict_semantic_group_size": group_size,
            "review_key": review_key(candidate) if candidate else None,
            "recommendation": rec,
        })

    exact_groups = []
    for key, ids in sorted(semantic_groups.items()):
        if len(ids) < 2:
            continue
        exact_groups.append({
            "strict_semantic_key": key,
            "candidate_ids": sorted(ids),
            "recommendation": "MERGE_REVIEW",
            "automatic_merge": False,
            "automatic_retirement": False,
        })

    target_families: dict[str, list[str]] = {}
    for cid, candidate in candidates.items():
        if cid not in by_id:
            continue
        spec = candidate.get("spec")
        if not isinstance(spec, dict):
            continue
        key = review_key(candidate)
        target_only = {
            "kind": key.get("kind"),
            "target_metric_path": key.get("target_metric_path"),
            "target_direction": key.get("target_direction"),
            "horizon_days": key.get("horizon_days"),
        }
        target_families.setdefault(digest(target_only), []).append(cid)

    inspection_families = []
    for key, ids in sorted(target_families.items()):
        if len(ids) < 2:
            continue
        semantic_keys = sorted({strict_semantic_key(candidates[cid]) for cid in ids if strict_semantic_key(candidates[cid])})
        inspection_families.append({
            "target_family_key": key,
            "candidate_ids": sorted(ids),
            "strict_semantic_keys": semantic_keys,
            "same_target_is_not_merge_authority": True,
            "distinct_hypotheses_preserved": len(semantic_keys) > 1,
        })

    repeated_inconclusive = []
    for group in inspection_families:
        ids = group["candidate_ids"]
        inconclusive = [cid for cid in ids if by_id[cid].get("state") == "MATURED_INCONCLUSIVE"]
        if len(inconclusive) > 1:
            repeated_inconclusive.append({
                "target_family_key": group["target_family_key"],
                "candidate_ids": sorted(inconclusive),
                "recommendation": "MERGE_REVIEW" if len(group["strict_semantic_keys"]) == 1 else "NEEDS_MORE_OUTCOMES",
                "automatic_action": False,
            })

    high_zero = [
        {
            "candidate_id": row["candidate_id"],
            "observation_count": row["observation_count"],
            "recommendation": row["recommendation"],
        }
        for row in reviewed
        if row["state"] == "INCUBATING"
        and row["matured_outcome_count"] == 0
        and row["observation_count"] >= high_cutoff
    ]

    counts: dict[str, int] = {}
    for row in reviewed:
        counts[row["recommendation"]] = counts.get(row["recommendation"], 0) + 1

    return {
        "contract": "EXPERIMENT_SIMPLIFICATION_REVIEW_v1",
        "generated_from_registry_at_utc": registry.get("generated_at_utc"),
        "authority": {
            "research_only": True,
            "binding": False,
            "automatic_merge": False,
            "automatic_retirement": False,
            "automatic_promotion": False,
            "model_weight_change": False,
            "market_gate_change": False,
            "portfolio_action": False,
            "candidate_history_mutation": False,
        },
        "recommendation_vocabulary": sorted(ALLOWED_RECOMMENDATIONS),
        "registry_row_count": len(rows),
        "candidate_count": len(reviewed),
        "unique_candidate_count": len(by_id),
        "duplicate_candidate_id_rows": duplicate_candidate_id_rows,
        "review_counts": counts,
        "high_observation_zero_outcome_definition": {
            "population": "INCUBATING_WITH_ZERO_MATURED_OUTCOMES",
            "method": "CURRENT_POPULATION_MEDIAN_OBSERVATION_COUNT",
            "cutoff_observation_count": high_cutoff,
            "authority": "DESCRIPTIVE_REVIEW_ONLY",
        },
        "exact_semantic_alias_groups": exact_groups,
        "target_family_inspection_groups": inspection_families,
        "repeated_matured_inconclusive_families": repeated_inconclusive,
        "high_observation_zero_outcome_incubating": high_zero,
        "candidates": reviewed,
        "rules": {
            "same_metric_path_alone_can_merge": False,
            "strict_semantic_equivalence_can_only_trigger_merge_review": True,
            "review_can_delete_candidate": False,
            "review_can_rewrite_history": False,
            "review_can_promote_candidate": False,
            "review_can_change_weight": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=Path("research/experiment_lifecycle/LATEST_EXPERIMENT_REGISTRY.json"))
    parser.add_argument("--candidate-root", type=Path, default=Path("research/experiment_lifecycle/candidates"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    result = build_review(registry, load_candidates(args.candidate_root))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "candidate_count": result["candidate_count"],
        "semantic_alias_groups": len(result["exact_semantic_alias_groups"]),
        "target_family_groups": len(result["target_family_inspection_groups"]),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
