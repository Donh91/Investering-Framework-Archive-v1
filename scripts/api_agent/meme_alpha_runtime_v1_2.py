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
        plan = base.build_plan(args.workspace, policy, state)
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
