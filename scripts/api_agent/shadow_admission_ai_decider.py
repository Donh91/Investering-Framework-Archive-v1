from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.api_agent.api_gateway import (
    call_api,
    canonical_bytes,
    estimate_cost,
    sha256_bytes,
    usage_of,
)

DECISION_TO_STATE = {
    "PROMOTE_OPERATIONAL_HELPER": "OPERATIONAL_HELPER",
    "KEEP_SHADOW": "SHADOW_TESTING",
    "ARCHIVE_ONLY": "ARCHIVE_ONLY",
    "RETIRED": "RETIRED",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def output_schema(candidate_ids: list[str], allowed_decisions: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["contract", "overall_status", "candidate_decisions", "master_monday_summary"],
        "properties": {
            "contract": {"type": "string", "const": "SHADOW_ADMISSION_AI_DECISION_v1"},
            "overall_status": {"type": "string", "enum": ["DECIDED", "EVIDENCE_LIMITED"]},
            "candidate_decisions": {
                "type": "array",
                "minItems": len(candidate_ids),
                "maxItems": len(candidate_ids),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "candidate_id",
                        "decision",
                        "resulting_state",
                        "evidence_sufficiency",
                        "confidence",
                        "incremental_value_assessment",
                        "complexity_tax_assessment",
                        "rationale",
                        "implementation_status",
                        "rollback_path",
                        "master_monday_note",
                    ],
                    "properties": {
                        "candidate_id": {"type": "string", "enum": candidate_ids},
                        "decision": {"type": "string", "enum": allowed_decisions},
                        "resulting_state": {
                            "type": "string",
                            "enum": ["OPERATIONAL_HELPER", "SHADOW_TESTING", "ARCHIVE_ONLY", "RETIRED"],
                        },
                        "evidence_sufficiency": {"type": "string", "enum": ["SUFFICIENT", "MIXED", "INSUFFICIENT"]},
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                        "incremental_value_assessment": {"type": "string"},
                        "complexity_tax_assessment": {"type": "string"},
                        "rationale": {"type": "string"},
                        "implementation_status": {
                            "type": "string",
                            "enum": ["ENABLE_AUTOMATICALLY", "KEEP_OBSERVING", "DISABLE_AUTOMATICALLY"],
                        },
                        "rollback_path": {"type": "string"},
                        "master_monday_note": {"type": "string"},
                    },
                },
            },
            "master_monday_summary": {"type": "string"},
        },
    }


def validate_decision(value: dict[str, Any], candidate_ids: list[str], allowed_decisions: list[str]) -> None:
    if value.get("contract") != "SHADOW_ADMISSION_AI_DECISION_v1":
        raise ValueError("invalid_contract")
    if value.get("overall_status") not in {"DECIDED", "EVIDENCE_LIMITED"}:
        raise ValueError("invalid_overall_status")
    rows = value.get("candidate_decisions")
    if not isinstance(rows, list) or len(rows) != len(candidate_ids):
        raise ValueError("candidate_decision_count_mismatch")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("invalid_candidate_row")
        cid = row.get("candidate_id")
        if cid not in candidate_ids or cid in seen:
            raise ValueError("candidate_identity_invalid_or_duplicate")
        seen.add(cid)
        decision = row.get("decision")
        if decision not in allowed_decisions:
            raise ValueError("decision_outside_policy")
        if row.get("resulting_state") != DECISION_TO_STATE[decision]:
            raise ValueError("decision_state_mismatch")
        if row.get("evidence_sufficiency") not in {"SUFFICIENT", "MIXED", "INSUFFICIENT"}:
            raise ValueError("invalid_evidence_sufficiency")
        confidence = row.get("confidence")
        if not isinstance(confidence, (int, float)) or not 0 <= float(confidence) <= 1:
            raise ValueError("invalid_confidence")
        expected_impl = {
            "PROMOTE_OPERATIONAL_HELPER": "ENABLE_AUTOMATICALLY",
            "KEEP_SHADOW": "KEEP_OBSERVING",
            "ARCHIVE_ONLY": "DISABLE_AUTOMATICALLY",
            "RETIRED": "DISABLE_AUTOMATICALLY",
        }[decision]
        if row.get("implementation_status") != expected_impl:
            raise ValueError("decision_implementation_mismatch")
        for field in (
            "incremental_value_assessment",
            "complexity_tax_assessment",
            "rationale",
            "rollback_path",
            "master_monday_note",
        ):
            if not str(row.get(field) or "").strip():
                raise ValueError(f"missing_text:{field}")
    if seen != set(candidate_ids):
        raise ValueError("candidate_set_mismatch")
    if not str(value.get("master_monday_summary") or "").strip():
        raise ValueError("missing_master_monday_summary")


def extract_output(response: dict[str, Any], candidate_ids: list[str], allowed_decisions: list[str]) -> dict[str, Any]:
    if response.get("status") == "incomplete":
        raise ValueError("response_incomplete")
    text = response.get("output_text")
    if not text:
        parts: list[str] = []
        for item in response.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    parts.append(content.get("text", ""))
        text = "".join(parts)
    if not text:
        raise ValueError("missing_output_text")
    value = json.loads(text)
    validate_decision(value, candidate_ids, allowed_decisions)
    return value


def load_evidence(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.json")):
        try:
            value = load_json(path)
        except Exception:
            continue
        rows.append({"path": str(path), "sha256": sha256_bytes(path.read_bytes()), "value": value})
    return rows


def initial_state(candidate_registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract": "SHADOW_CANDIDATE_LIFECYCLE_STATE_v1",
        "updated_at_utc": None,
        "decision_authority": "OPENAI_API_AUTONOMOUS",
        "human_confirmation_required": False,
        "candidates": {
            row["id"]: {
                "name": row["name"],
                "state": "SHADOW_TESTING",
                "operational_enabled": False,
                "authority_ceiling": "OPERATIONAL_HELPER",
                "last_decision": None,
                "last_decision_hash": None,
            }
            for row in candidate_registry["candidates"]
        },
    }


def apply_ai_decision(
    prior_state: dict[str, Any], decision: dict[str, Any], decision_hash: str, candidate_registry: dict[str, Any]
) -> dict[str, Any]:
    state = json.loads(json.dumps(prior_state))
    state["contract"] = "SHADOW_CANDIDATE_LIFECYCLE_STATE_v1"
    state["decision_authority"] = "OPENAI_API_AUTONOMOUS"
    state["human_confirmation_required"] = False
    state["updated_at_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    known = {row["id"]: row for row in candidate_registry["candidates"]}
    state.setdefault("candidates", {})
    for row in decision["candidate_decisions"]:
        cid = row["candidate_id"]
        if cid not in known:
            raise ValueError("unknown_candidate_during_apply")
        state["candidates"].setdefault(cid, {})
        state["candidates"][cid].update(
            {
                "name": known[cid]["name"],
                "state": row["resulting_state"],
                "operational_enabled": row["resulting_state"] == "OPERATIONAL_HELPER",
                "authority_ceiling": "OPERATIONAL_HELPER",
                "last_decision": row["decision"],
                "last_decision_hash": decision_hash,
                "evidence_sufficiency": row["evidence_sufficiency"],
                "confidence": row["confidence"],
                "implementation_status": row["implementation_status"],
                "rollback_path": row["rollback_path"],
            }
        )
    return state


def dry_run_decision(candidate_registry: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract": "SHADOW_ADMISSION_AI_DECISION_v1",
        "overall_status": "EVIDENCE_LIMITED",
        "candidate_decisions": [
            {
                "candidate_id": row["id"],
                "decision": "KEEP_SHADOW",
                "resulting_state": "SHADOW_TESTING",
                "evidence_sufficiency": "INSUFFICIENT",
                "confidence": 1.0,
                "incremental_value_assessment": "Dry run does not contain an authoritative API judgment.",
                "complexity_tax_assessment": "Not evaluated in dry run.",
                "rationale": "Dry-run safety path keeps the candidate in shadow.",
                "implementation_status": "KEEP_OBSERVING",
                "rollback_path": row["rollback_criteria"][0],
                "master_monday_note": "Dry run only, no lifecycle promotion.",
            }
            for row in candidate_registry["candidates"]
        ],
        "master_monday_summary": "Dry run completed. No candidate lifecycle promotion was attempted.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--candidate-registry", type=Path, required=True)
    parser.add_argument("--prospective-policy", type=Path, required=True)
    parser.add_argument("--evidence-root", type=Path, required=True)
    parser.add_argument("--state-file", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    policy = load_json(args.policy)
    if policy.get("status") != "ACTIVE" or policy.get("decision_authority") != "OPENAI_API_AUTONOMOUS":
        raise SystemExit("autonomous_policy_not_active")
    if policy.get("human_confirmation_required") is not False:
        raise SystemExit("human_confirmation_policy_mismatch")
    if policy.get("authority_ceiling") != "OPERATIONAL_HELPER":
        raise SystemExit("authority_ceiling_invalid")

    candidate_registry = load_json(args.candidate_registry)
    candidate_ids = [row["id"] for row in candidate_registry.get("candidates", [])]
    if len(candidate_ids) != 4 or len(set(candidate_ids)) != 4:
        raise SystemExit("unexpected_candidate_registry")
    allowed_decisions = list(policy["allowed_decisions"])
    if set(allowed_decisions) != set(DECISION_TO_STATE):
        raise SystemExit("decision_policy_mismatch")

    evidence = load_evidence(args.evidence_root)
    prior_state = (
        load_json(args.state_file)
        if args.state_file and args.state_file.exists()
        else initial_state(candidate_registry)
    )
    prospective_policy_text = args.prospective_policy.read_text(encoding="utf-8")

    context = {
        "contract": "SHADOW_ADMISSION_AI_CONTEXT_v1",
        "candidate_registry": candidate_registry,
        "prospective_policy": prospective_policy_text,
        "evidence_rows": evidence,
        "prior_lifecycle_state": prior_state,
        "decision_policy": {
            "allowed_decisions": allowed_decisions,
            "authority_ceiling": policy["authority_ceiling"],
            "human_confirmation_required": False,
            "deterministic_validator_may_override_substantive_decision": False,
        },
    }

    instructions = (
        "You are the authoritative lifecycle decision-maker for isolated engineering candidates in an audited investment research framework. "
        "The framework owner has explicitly delegated substantive PASS/FAIL lifecycle judgment to you and does not require human confirmation. "
        "Use only the supplied frozen candidate contracts and evidence. Preserve preregistered promotion gates and complexity-tax requirements. "
        "Do not lower a candidate's evidence bar because early results are promising. If evidence is insufficient or mixed, choose KEEP_SHADOW. "
        "Synthetic/laboratory evidence alone cannot satisfy a promotion gate that requires repeated real-change evidence. "
        "Choose PROMOTE_OPERATIONAL_HELPER only when the evidence supports measurable incremental workflow value after complexity tax. "
        "Choose ARCHIVE_ONLY or RETIRED when value does not justify complexity. "
        "This round has an OPERATIONAL_HELPER authority ceiling and cannot alter market semantics, thresholds, model weights, canonical truth, portfolio execution, prospective floors, outcome labels or protected objectives. "
        "Do not ask the owner for approval. Master Monday is reporting-only. Return exactly one decision for every registered candidate."
    )
    payload = {
        "model": policy["model"],
        "reasoning": {"effort": policy["reasoning_effort"], "context": "current_turn"},
        "store": False,
        "max_output_tokens": int(policy["max_output_tokens"]),
        "instructions": instructions,
        "input": [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": json.dumps(context, sort_keys=True)}],
            }
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "shadow_admission_ai_decision_v1",
                "strict": True,
                "schema": output_schema(candidate_ids, allowed_decisions),
            }
        },
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    request_hash = sha256_bytes(canonical_bytes(payload))
    context_hash = sha256_bytes(canonical_bytes(context))

    responses: list[dict[str, Any]] = []
    parse_errors: list[str] = []
    decision: dict[str, Any] | None = None
    if args.dry_run:
        decision = dry_run_decision(candidate_registry)
        validate_decision(decision, candidate_ids, allowed_decisions)
    else:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY_missing")
        for attempt in range(2):
            attempt_payload = dict(payload)
            if attempt == 1:
                attempt_payload["max_output_tokens"] = min(max(int(policy["max_output_tokens"]) * 2, 4000), 6000)
            response = call_api(api_key, attempt_payload)
            responses.append(response)
            try:
                decision = extract_output(response, candidate_ids, allowed_decisions)
                break
            except (ValueError, json.JSONDecodeError) as exc:
                parse_errors.append(f"attempt_{attempt + 1}:{type(exc).__name__}:{str(exc)[:240]}")
        if decision is None:
            raise SystemExit("AI_DECISION_INVALID_AFTER_BOUNDED_RETRY")

    input_tokens = output_tokens = 0
    for response in responses:
        i, o = usage_of(response)
        input_tokens += i
        output_tokens += o
    cost = estimate_cost(policy["model"], input_tokens, output_tokens)
    if cost > float(policy["single_run_hard_stop_usd"]):
        raise SystemExit(f"single_run_cost_exceeded:{cost}")

    decision_bytes = canonical_bytes(decision)
    decision_hash = sha256_bytes(decision_bytes)
    next_state = apply_ai_decision(prior_state, decision, decision_hash, candidate_registry)
    receipt = {
        "contract": "SHADOW_ADMISSION_AI_RECEIPT_v1",
        "decision_authority": "OPENAI_API_AUTONOMOUS",
        "human_confirmation_required": False,
        "model": policy["model"],
        "reasoning_effort": policy["reasoning_effort"],
        "request_hash": request_hash,
        "context_hash": context_hash,
        "decision_hash": decision_hash,
        "candidate_registry_hash": sha256_bytes(args.candidate_registry.read_bytes()),
        "prospective_policy_hash": sha256_bytes(args.prospective_policy.read_bytes()),
        "evidence_row_count": len(evidence),
        "evidence_hashes": [row["sha256"] for row in evidence],
        "response_ids": [r.get("id") for r in responses],
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": cost,
        "parse_errors": parse_errors,
        "created_unix": int(time.time()),
        "status": "DRY_RUN" if args.dry_run else "PASS",
        "authority_ceiling": "OPERATIONAL_HELPER",
        "deterministic_validator_role": "SCHEMA_IDENTITY_EVIDENCE_BINDING_AUTHORITY_CEILING_ONLY",
        "deterministic_validator_overrode_substantive_decision": False,
    }

    (args.output_dir / "decision.json").write_bytes(decision_bytes)
    (args.output_dir / "receipt.json").write_bytes(canonical_bytes(receipt))
    (args.output_dir / "candidate_lifecycle_state.json").write_bytes(canonical_bytes(next_state))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
