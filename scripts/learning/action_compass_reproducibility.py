from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.learning import action_compass_accountability as owner  # noqa: E402

FIXTURE_CONTRACT = "ACTION_COMPASS_REPRO_FIXTURE_v1"
RESULT_CONTRACT = "ACTION_COMPASS_REPRO_RESULT_v1"
FIXTURE_CLASSES = {"SYNTHETIC_CONTROLLED", "POST_ACTIVATION_FROZEN_RECEIPT"}
INPUT_BINDING_FIELDS = (
    "input_packet_sha256",
    "input_binding_status",
    "input_contract",
    "source_reference",
    "source_timestamp_utc",
    "canonical_repository",
    "canonical_commit_sha",
    "owner_contract",
)
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.:-]{2,100}$")
RECEIPT_ROOT = Path("research/framework_memory/action_compass_receipts")


def exact_keys(value: dict[str, Any], required: set[str], label: str) -> None:
    missing = sorted(required - set(value))
    extra = sorted(set(value) - required)
    if missing:
        raise ValueError(f"{label}_missing:{','.join(missing)}")
    if extra:
        raise ValueError(f"{label}_extra:{','.join(extra)}")


def validate_relative_source(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value) > 320:
        raise ValueError("fixture_source_reference_invalid")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("fixture_source_reference_unsafe")
    lowered = value.lower()
    if "chat" in lowered or "conversation" in lowered or "transcript" in lowered:
        raise ValueError("historical_chat_fixture_forbidden")
    if any(part.upper() == "LATEST.JSON" or part.upper().startswith("LATEST.") for part in path.parts):
        raise ValueError("mutable_latest_fixture_forbidden")
    return value


def validate_fixture(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("fixture_object_required")
    exact_keys(
        value,
        {
            "contract",
            "fixture_id",
            "fixture_class",
            "source_reference",
            "frozen_at_utc",
            "activation_utc",
            "frozen_input_sha256",
            "frozen_input",
        },
        "fixture",
    )
    if value["contract"] != FIXTURE_CONTRACT:
        raise ValueError("fixture_contract_invalid")
    if not isinstance(value["fixture_id"], str) or not SAFE_ID_RE.fullmatch(value["fixture_id"]):
        raise ValueError("fixture_id_invalid")

    fixture_class = value["fixture_class"]
    if fixture_class not in FIXTURE_CLASSES:
        raise ValueError("fixture_class_invalid")
    source = validate_relative_source(value["source_reference"])
    frozen_at = owner.parse_time(value["frozen_at_utc"])
    activation = owner.parse_time(value["activation_utc"])
    if frozen_at < activation:
        raise ValueError("pre_activation_fixture_forbidden")

    frozen = value["frozen_input"]
    if not isinstance(frozen, dict):
        raise ValueError("frozen_input_object_required")
    exact_keys(frozen, set(INPUT_BINDING_FIELDS), "frozen_input")
    sha = value["frozen_input_sha256"]
    if not isinstance(sha, str) or not SHA256_RE.fullmatch(sha):
        raise ValueError("frozen_input_sha256_invalid")
    if owner.digest(frozen) != sha:
        raise ValueError("frozen_input_hash_mismatch")

    source_time = owner.parse_time(frozen["source_timestamp_utc"])
    if source_time < activation:
        raise ValueError("pre_activation_input_forbidden")
    if source_time > frozen_at:
        raise ValueError("frozen_input_after_fixture_freeze")

    if fixture_class == "SYNTHETIC_CONTROLLED":
        if not source.startswith("tests/fixtures/action_compass_reproducibility/"):
            raise ValueError("synthetic_fixture_source_invalid")
        eligible = False
    else:
        if not source.startswith(RECEIPT_ROOT.as_posix() + "/"):
            raise ValueError("post_activation_receipt_source_invalid")
        eligible = frozen["input_binding_status"] == "VERIFIED_REPO_FILE"

    return {
        "fixture_id": value["fixture_id"],
        "fixture_class": fixture_class,
        "source_reference": source,
        "frozen_input_sha256": sha,
        "frozen_input": frozen,
        "activation_utc": value["activation_utc"],
        "eligible_replay": eligible,
    }


def semantic_projection(candidate: dict[str, Any]) -> dict[str, Any]:
    # T01 explicitly freezes machine actions/state/warning, horizons/validity
    # semantics and data-quality classification. Rationale/model metadata is
    # intentionally outside this projection.
    return {
        "action_compass": candidate["action_compass"],
        "data_quality_tags": sorted(candidate["data_quality_tags"]),
    }


def metadata_projection(candidate: dict[str, Any]) -> dict[str, Any]:
    return {
        "interpreted_at_utc": candidate["interpreted_at_utc"],
        "producer_model": candidate["producer_model"],
        "rationale_tags": sorted(candidate["rationale_tags"]),
        "baseline_observer": candidate["baseline_observer"],
    }


def diff_paths(left: Any, right: Any, prefix: str = "") -> list[str]:
    if type(left) is not type(right):
        return [prefix or "$"]
    if isinstance(left, dict):
        keys = sorted(set(left) | set(right))
        out: list[str] = []
        for key in keys:
            child = f"{prefix}.{key}" if prefix else key
            if key not in left or key not in right:
                out.append(child)
            else:
                out.extend(diff_paths(left[key], right[key], child))
        return out
    if isinstance(left, list):
        if len(left) != len(right):
            return [prefix or "$"]
        out: list[str] = []
        for index, (a, b) in enumerate(zip(left, right)):
            out.extend(diff_paths(a, b, f"{prefix}[{index}]"))
        return out
    return [] if left == right else [prefix or "$"]


def validate_replay(candidate: Any, frozen_input: dict[str, Any], activation_utc: str) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        raise ValueError("replay_candidate_object_required")
    owner.validate_candidate(candidate)
    mismatched = [field for field in INPUT_BINDING_FIELDS if candidate.get(field) != frozen_input[field]]
    if mismatched:
        raise ValueError("replay_input_binding_mismatch:" + ",".join(mismatched))
    if owner.parse_time(candidate["interpreted_at_utc"]) < owner.parse_time(activation_utc):
        raise ValueError("pre_activation_interpretation_forbidden")
    return {
        "semantic": semantic_projection(candidate),
        "metadata": metadata_projection(candidate),
    }


def compare_replays(fixture: dict[str, Any], outputs: list[Any]) -> dict[str, Any]:
    fixture_info = validate_fixture(fixture)
    if not isinstance(outputs, list) or len(outputs) < 2:
        raise ValueError("at_least_two_replay_outputs_required")

    validated: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    for index, raw in enumerate(outputs):
        try:
            validated.append(
                validate_replay(raw, fixture_info["frozen_input"], fixture_info["activation_utc"])
            )
        except (ValueError, KeyError, TypeError) as exc:
            invalid.append({"index": index, "error": str(exc)})

    disagreements: list[dict[str, Any]] = []
    metadata_variance = False
    reference = validated[0] if validated else None
    if reference is not None:
        for index, row in enumerate(validated[1:], start=1):
            paths = diff_paths(reference["semantic"], row["semantic"])
            if paths:
                disagreements.append({"replay_index": index, "paths": paths})
            if row["metadata"] != reference["metadata"]:
                metadata_variance = True

    if invalid:
        status = "INVALID_OUTPUT"
    elif disagreements:
        status = "SEMANTIC_DISAGREEMENT"
    else:
        status = "SEMANTIC_MATCH"

    eligible_replay_count = (
        len(validated)
        if fixture_info["eligible_replay"] and status in {"SEMANTIC_MATCH", "SEMANTIC_DISAGREEMENT"}
        else 0
    )
    return {
        "contract": RESULT_CONTRACT,
        "fixture_id": fixture_info["fixture_id"],
        "fixture_class": fixture_info["fixture_class"],
        "source_reference": fixture_info["source_reference"],
        "frozen_input_sha256": fixture_info["frozen_input_sha256"],
        "status": status,
        "replay_count": len(outputs),
        "valid_replay_count": len(validated),
        "eligible_replay_count": eligible_replay_count,
        "synthetic_replay_count": len(validated) if not fixture_info["eligible_replay"] else 0,
        "semantic_reference_sha256": owner.digest(reference["semantic"]) if reference else None,
        "semantic_disagreements": disagreements,
        "invalid_outputs": invalid,
        "metadata_variance_observed": metadata_variance,
        "prospective_action_compass_receipt_created": False,
        "reproducibility_conclusion_authorized": False,
        "reproducibility_conclusion_minimum_eligible_replays": 10,
        "authority": {
            "research_only": True,
            "binding": False,
            "canonical_market_state": False,
            "market_gate_change": False,
            "model_weight_change": False,
            "portfolio_action": False,
            "automatic_promotion": False,
            "new_market_engine": False,
        },
    }


def output_is_inside_receipt_root(output: Path, repo_root: Path) -> bool:
    target = output.resolve()
    root = (repo_root / RECEIPT_ROOT).resolve()
    return target == root or root in target.parents


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    args = parser.parse_args()

    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    outputs = json.loads(args.outputs.read_text(encoding="utf-8"))
    result = compare_replays(fixture, outputs)
    raw = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        if output_is_inside_receipt_root(args.output, args.repo_root):
            raise SystemExit("ACTION_COMPASS_REPRO_ERROR:receipt_root_output_forbidden")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(raw, encoding="utf-8")
    print(raw, end="")
    if result["status"] == "INVALID_OUTPUT":
        raise SystemExit(2)
    if result["status"] == "SEMANTIC_DISAGREEMENT":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
