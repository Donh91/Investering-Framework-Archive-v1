from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from scripts.learning.action_compass_accountability import (
    DATA_QUALITY_TAGS,
    digest,
    parse_time,
    validate_action_compass,
    validate_tags,
)

FIXTURE_CONTRACT = "ACTION_COMPASS_REPRO_FIXTURE_v1"
RESULT_CONTRACT = "ACTION_COMPASS_REPRO_RESULT_v1"
FIXTURE_CLASSES = {"SYNTHETIC_CONTROLLED", "POST_ACTIVATION_FROZEN_RECEIPT"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID_RE = re.compile(r"^[A-Z0-9][A-Z0-9_.:-]{2,100}$")


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
    if "chat" in lowered or "conversation" in lowered:
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
    frozen_at = parse_time(value["frozen_at_utc"])
    activation = parse_time(value["activation_utc"])
    if frozen_at < activation:
        raise ValueError("pre_activation_fixture_forbidden")
    if not isinstance(value["frozen_input"], dict):
        raise ValueError("frozen_input_object_required")
    sha = value["frozen_input_sha256"]
    if not isinstance(sha, str) or not SHA256_RE.fullmatch(sha):
        raise ValueError("frozen_input_sha256_invalid")
    if digest(value["frozen_input"]) != sha:
        raise ValueError("frozen_input_hash_mismatch")
    if fixture_class == "SYNTHETIC_CONTROLLED":
        if not source.startswith("tests/fixtures/action_compass_reproducibility/"):
            raise ValueError("synthetic_fixture_source_invalid")
        eligible = False
    else:
        if not source.startswith("research/framework_memory/action_compass_receipts/"):
            raise ValueError("post_activation_receipt_source_invalid")
        eligible = True
    return {
        "fixture_id": value["fixture_id"],
        "fixture_class": fixture_class,
        "source_reference": source,
        "frozen_input_sha256": sha,
        "frozen_at_utc": value["frozen_at_utc"],
        "activation_utc": value["activation_utc"],
        "eligible_replay": eligible,
    }


def validate_output(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("replay_output_object_required")
    exact_keys(
        value,
        {"replay_id", "interpreted_at_utc", "producer_model", "wording", "data_quality_tags", "action_compass"},
        "replay_output",
    )
    replay_id = value["replay_id"]
    if not isinstance(replay_id, str) or not SAFE_ID_RE.fullmatch(replay_id):
        raise ValueError("replay_id_invalid")
    interpreted = parse_time(value["interpreted_at_utc"])
    model = value["producer_model"]
    if not isinstance(model, str) or not 1 <= len(model) <= 100:
        raise ValueError("producer_model_invalid")
    wording = value["wording"]
    if not isinstance(wording, str) or len(wording) > 2000:
        raise ValueError("wording_invalid")
    validate_tags(value["data_quality_tags"], "data_quality_tags", DATA_QUALITY_TAGS, 8)
    validate_action_compass(value["action_compass"], interpreted)
    return {
        "replay_id": replay_id,
        "semantic": {
            "action_compass": value["action_compass"],
            "data_quality_tags": sorted(value["data_quality_tags"]),
        },
        "metadata": {
            "interpreted_at_utc": value["interpreted_at_utc"],
            "producer_model": model,
            "wording": wording,
        },
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


def compare_replays(fixture: dict[str, Any], outputs: list[Any]) -> dict[str, Any]:
    fixture_info = validate_fixture(fixture)
    if not isinstance(outputs, list) or len(outputs) < 2:
        raise ValueError("at_least_two_replay_outputs_required")

    validated: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(outputs):
        try:
            row = validate_output(raw)
            if row["replay_id"] in seen_ids:
                raise ValueError("duplicate_replay_id")
            seen_ids.add(row["replay_id"])
            validated.append(row)
        except (ValueError, KeyError, TypeError) as exc:
            invalid.append({"index": index, "error": str(exc)})

    disagreements: list[dict[str, Any]] = []
    metadata_variance = False
    reference = validated[0] if validated else None
    if reference is not None:
        for row in validated[1:]:
            paths = diff_paths(reference["semantic"], row["semantic"])
            if paths:
                disagreements.append({"replay_id": row["replay_id"], "paths": paths})
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
        "semantic_reference_sha256": digest(reference["semantic"]) if reference else None,
        "semantic_disagreements": disagreements,
        "invalid_outputs": invalid,
        "metadata_or_wording_variance_observed": metadata_variance,
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--outputs", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    fixture = json.loads(args.fixture.read_text(encoding="utf-8"))
    outputs = json.loads(args.outputs.read_text(encoding="utf-8"))
    result = compare_replays(fixture, outputs)
    raw = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(raw, encoding="utf-8")
    print(raw, end="")
    if result["status"] == "INVALID_OUTPUT":
        raise SystemExit(2)
    if result["status"] == "SEMANTIC_DISAGREEMENT":
        raise SystemExit(3)


if __name__ == "__main__":
    main()
