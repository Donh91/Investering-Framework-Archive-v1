from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

try:
    from scripts.api_agent import meme_alpha_runtime as base
    from scripts.api_agent import meme_alpha_runtime_v1_1 as v11
    from scripts.api_agent import meme_alpha_source_auth as source_auth
except ModuleNotFoundError:
    import meme_alpha_runtime as base
    import meme_alpha_runtime_v1_1 as v11
    import meme_alpha_source_auth as source_auth


def _augmented_output_schema(original_schema: Any) -> dict[str, Any]:
    schema = copy.deepcopy(original_schema())
    if "source_authentication" not in schema["required"]:
        schema["required"].append("source_authentication")
    schema["properties"]["source_authentication"] = source_auth.source_authentication_schema()
    return schema


def _bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def _cap_array(schema: dict[str, Any], key: str, cap: int) -> None:
    properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    node = properties.get(key)
    if not isinstance(node, dict) or node.get("type") != "array":
        return
    existing = node.get("maxItems")
    if isinstance(existing, int):
        node["maxItems"] = min(existing, cap)
    else:
        node["maxItems"] = cap


def _apply_output_compaction(payload: dict[str, Any], task: dict[str, Any]) -> bool:
    """Make task-local compact-output requests enforceable by the structured schema.

    The task may request fewer items than the generic runtime permits. The runtime
    never expands a schema here; it only tightens list cardinality and adds a strong
    non-repetition instruction. Global model/token budgets remain unchanged.
    """
    cfg = task.get("output_compaction")
    if not isinstance(cfg, dict):
        return False
    text = payload.get("text") if isinstance(payload.get("text"), dict) else {}
    fmt = text.get("format") if isinstance(text.get("format"), dict) else {}
    schema = fmt.get("schema") if isinstance(fmt.get("schema"), dict) else None
    if schema is None:
        return False

    caps = {
        "verified_findings": _bounded_int(cfg.get("max_verified_findings"), 6, 1, 10),
        "disconfirming_evidence": _bounded_int(cfg.get("max_disconfirming_evidence"), 5, 1, 8),
        "uncertainties": _bounded_int(cfg.get("max_uncertainties"), 5, 1, 8),
        "wallet_candidates": _bounded_int(cfg.get("max_wallet_candidates"), 4, 0, 8),
        "network_connections": _bounded_int(cfg.get("max_network_connections"), 6, 0, 10),
        "next_research_steps": _bounded_int(cfg.get("max_next_research_steps"), 4, 1, 6),
        "development_candidates": _bounded_int(cfg.get("max_development_candidates"), 2, 0, 4),
        "source_urls": _bounded_int(cfg.get("max_source_urls"), 12, 1, 20),
    }
    for key, cap in caps.items():
        _cap_array(schema, key, cap)

    properties = schema.get("properties") if isinstance(schema.get("properties"), dict) else {}
    auth = properties.get("source_authentication")
    if isinstance(auth, dict):
        for key, cap in {
            "external_trust_anchors": 4,
            "repository_forensics": 4,
            "onchain_bindings": 4,
            "red_team_findings": 4,
            "gate_reasons": 6,
            "claim_types": 6,
        }.items():
            _cap_array(auth, key, cap)

    target = _bounded_int(cfg.get("target_max_output_tokens"), 3000, 1800, 3400)
    instruction = str(cfg.get("instruction") or "").strip()
    payload["instructions"] = (
        str(payload.get("instructions") or "")
        + " OUTPUT_COMPACTION is binding for this task. Fit the complete structured response comfortably below "
        + str(target)
        + " output tokens. Obey every schema maxItems limit, use one evidence-dense sentence per item, and never repeat the same evidence across summary, findings, uncertainties, connections, or source-authentication fields. "
        + instruction
    ).strip()
    return True


def _build_exact_plan(workspace: Path, policy: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    """Reuse the existing deterministic ranker while requiring exact queue states.

    The legacy planner used substring admission, so a state such as
    RESEARCH_CANDIDATE_NOT_ACTIVATED could accidentally match RESEARCH. We do not
    fork the ranking algorithm. Instead, inadmissible selections are marked only in
    an in-memory shadow state and the same ranker is asked for the next candidate.
    """
    shadow_state = copy.deepcopy(state)
    processed = shadow_state.get("processed_inputs")
    if not isinstance(processed, dict):
        processed = {}
        shadow_state["processed_inputs"] = processed
    eligible = {str(item).strip().upper() for item in policy["queue"]["eligible_status_tokens"]}
    rejected: list[dict[str, Any]] = []

    while True:
        plan = base.build_plan(workspace, policy, shadow_state)
        selected = plan.get("selected") if isinstance(plan.get("selected"), dict) else None
        if selected is None:
            if rejected:
                plan["rejected_non_exact_status_count"] = len(rejected)
                plan["rejected_non_exact_statuses"] = rejected[:10]
                plan["selection_rule"] = "existing deterministic ranking with exact eligible status admission"
            return plan

        rel = str(selected.get("path") or "")
        path = workspace / rel
        try:
            value = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            processed[rel] = str(selected.get("input_sha256") or "")
            rejected.append({"path": rel, "status_tokens": ["UNREADABLE_AFTER_SELECTION"]})
            continue
        if not isinstance(value, dict):
            processed[rel] = str(selected.get("input_sha256") or "")
            rejected.append({"path": rel, "status_tokens": ["NON_OBJECT_AFTER_SELECTION"]})
            continue

        tokens = base.status_tokens(value)
        if not tokens or tokens.intersection(eligible):
            plan["rejected_non_exact_status_count"] = len(rejected)
            if rejected:
                plan["rejected_non_exact_statuses"] = rejected[:10]
            plan["selection_rule"] = "existing deterministic ranking with exact eligible status admission"
            return plan

        processed[rel] = str(selected.get("input_sha256") or "")
        rejected.append({"path": rel, "status_tokens": sorted(tokens)})


def analyze(
    task_path: Path,
    policy: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool,
    enable_web: bool,
    model: str | None,
) -> dict[str, Any]:
    """Run v1.1 research with a deterministic post-model source-authentication gate.

    v1.2 preserves v1.1 budget and hosted web-call semantics. It adds a required
    structured source-authentication packet to model outputs, then deterministically
    prevents first-party promotion when external trust anchors, red-team clearance,
    repository forensics or token/on-chain binding are insufficient.
    """
    task = json.loads(task_path.read_text())
    if not isinstance(task, dict):
        raise ValueError("task_must_be_object")

    original_schema = base.output_schema
    original_build_request = base.build_request

    def patched_schema() -> dict[str, Any]:
        return _augmented_output_schema(original_schema)

    def patched_build_request(*args: Any, **kwargs: Any) -> dict[str, Any]:
        payload = original_build_request(*args, **kwargs)
        payload["instructions"] = str(payload.get("instructions") or "") + " " + source_auth.source_authentication_instruction(policy)
        _apply_output_compaction(payload, task)
        return payload

    base.output_schema = patched_schema
    base.build_request = patched_build_request
    try:
        receipt = v11.analyze(
            task_path,
            policy,
            output_dir,
            dry_run=dry_run,
            enable_web=enable_web,
            model=model,
        )
    finally:
        base.output_schema = original_schema
        base.build_request = original_build_request

    output_path = output_dir / "output.json"
    output = json.loads(output_path.read_text())
    if not isinstance(output, dict):
        raise ValueError("output_must_be_object")
    output = source_auth.apply_source_authentication_gate(output, task, policy)
    output_path.write_bytes(base.canonical_bytes(output))

    receipt_path = output_dir / "receipt.json"
    persisted_receipt = json.loads(receipt_path.read_text())
    auth_packet = output.get("source_authentication") if isinstance(output.get("source_authentication"), dict) else {}
    persisted_receipt["runtime_contract"] = "MEME_ALPHA_RUNTIME_v1_2_SOURCE_AUTH"
    persisted_receipt["output_sha256"] = base.sha256_bytes(base.canonical_bytes(output))
    persisted_receipt["source_authentication_state"] = auth_packet.get("state")
    persisted_receipt["source_authentication_scope"] = auth_packet.get("scope")
    persisted_receipt["first_party_claim_allowed"] = bool(auth_packet.get("first_party_claim_allowed"))
    persisted_receipt["source_authentication_gate_reasons"] = auth_packet.get("gate_reasons") or []
    persisted_receipt["output_compaction_applied"] = isinstance(task.get("output_compaction"), dict)
    if isinstance(task.get("output_compaction"), dict):
        persisted_receipt["output_compaction_target_tokens"] = _bounded_int(
            task["output_compaction"].get("target_max_output_tokens"), 3000, 1800, 3400
        )
    receipt_path.write_bytes(base.canonical_bytes(persisted_receipt))
    return persisted_receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Meme Alpha runtime v1.2 with deterministic source-authentication admission gate.")
    sub = parser.add_subparsers(dest="command", required=True)
    p_plan = sub.add_parser("plan")
    p_plan.add_argument("--workspace", type=Path, required=True)
    p_plan.add_argument("--policy", type=Path, required=True)
    p_plan.add_argument("--state", type=Path, required=True)
    p_plan.add_argument("--output", type=Path, required=True)
    p_analyze = sub.add_parser("analyze")
    p_analyze.add_argument("--task", type=Path, required=True)
    p_analyze.add_argument("--policy", type=Path, required=True)
    p_analyze.add_argument("--output-dir", type=Path, required=True)
    p_analyze.add_argument("--dry-run", action="store_true")
    p_analyze.add_argument("--no-web", action="store_true")
    p_analyze.add_argument("--model", choices=sorted(base.PRICES_PER_MILLION))
    args = parser.parse_args()
    policy = base.load_object(args.policy)
    if policy.get("contract") != "MEME_ALPHA_RUNTIME_POLICY_v1":
        raise SystemExit("invalid_policy_contract")
    if args.command == "plan":
        state = base.load_object(args.state)
        plan = _build_exact_plan(args.workspace, policy, state)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(base.canonical_bytes(plan))
        print(json.dumps(plan, sort_keys=True))
        return 0
    receipt = analyze(
        args.task,
        policy,
        args.output_dir,
        dry_run=args.dry_run,
        enable_web=not args.no_web,
        model=args.model,
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
