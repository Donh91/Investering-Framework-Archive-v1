from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

try:
    from scripts.api_agent import meme_alpha_runtime as base
    from scripts.api_agent import meme_alpha_url_provenance as url_provenance
except ModuleNotFoundError:
    import meme_alpha_runtime as base
    import meme_alpha_url_provenance as url_provenance


def analyze(
    task_path: Path,
    policy: dict[str, Any],
    output_dir: Path,
    *,
    dry_run: bool,
    enable_web: bool,
    model: str | None,
) -> dict[str, Any]:
    """Compatibility hardening for hosted web-search call-count overshoot.

    The Responses API is asked for the policy maximum. In production it has
    occasionally returned one additional web_search_call. That provider-side
    overshoot must be costed and surfaced, not turn an otherwise valid paid
    research response into a retry loop. Overshoots beyond the explicit
    tolerance remain fatal.

    Web provenance is reconciled by canonical URL identity so benign tracking
    parameters, fragments and trailing slashes cannot cause a retrieved source
    to be falsely dropped. Host and path identity remain strict.
    """
    task_bytes = task_path.read_bytes()
    task = json.loads(task_bytes)
    if not isinstance(task, dict):
        raise ValueError("task_must_be_object")
    task_hash = base.sha256_bytes(task_bytes)
    task_id = "MAL-" + task_hash[:16]
    selected_model = model or policy["model_policy"]["default_model"]
    effort = policy["model_policy"]["default_reasoning_effort"]
    max_output_tokens = int(policy["model_policy"].get("max_output_tokens", 3600))
    if max_output_tokens < 1800 or max_output_tokens > 8000:
        raise ValueError("invalid_max_output_tokens")

    requested_web_calls = int(policy["budget"].get("max_web_search_calls_per_task", 2))
    if requested_web_calls < 0 or requested_web_calls > 4:
        raise ValueError("invalid_max_web_search_calls_per_task")
    overrun_tolerance = int(policy["budget"].get("provider_web_search_overrun_tolerance", 0))
    if overrun_tolerance < 0 or overrun_tolerance > 1:
        raise ValueError("invalid_provider_web_search_overrun_tolerance")

    request_payload = base.build_request(
        selected_model,
        effort,
        task_id,
        task,
        enable_web=enable_web,
        max_web_search_calls=requested_web_calls,
        max_output_tokens=max_output_tokens,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    request_hash = base.sha256_bytes(base.canonical_bytes(request_payload))

    if dry_run:
        output = {
            "status": "BLOCKED",
            "task_id": task_id,
            "summary": "Dry run, no model call.",
            "verified_findings": [],
            "disconfirming_evidence": [],
            "uncertainties": ["DRY_RUN"],
            "wallet_candidates": [],
            "network_connections": [],
            "next_research_steps": [],
            "development_candidates": [],
            "source_urls": [],
            "priority_after_run": "LOW",
        }
        response: dict[str, Any] = {
            "id": "dry-run",
            "usage": {"input_tokens": 0, "output_tokens": 0},
            "output": [],
        }
    else:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("OPENAI_API_KEY_missing")
        response = base.call_api(api_key, request_payload)
        if response.get("status") == "incomplete":
            details = response.get("incomplete_details") if isinstance(response.get("incomplete_details"), dict) else {}
            raise ValueError("model_output_incomplete:" + str(details.get("reason") or "unknown"))
        text = base.extract_output_text(response)
        if not text:
            raise ValueError("missing_output_text")
        try:
            output = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"model_output_invalid_json:{exc.msg}") from exc
        base.validate_output(output)

    observed_urls = base.collect_urls(response)
    claimed_urls = {x for x in output.get("source_urls", []) if isinstance(x, str)}
    supported_urls, unsupported_urls = (
        url_provenance.reconcile_source_urls(claimed_urls, observed_urls)
        if enable_web and not dry_run
        else (sorted(claimed_urls), [])
    )
    if enable_web and not dry_run:
        output["source_urls"] = supported_urls
    if unsupported_urls:
        output.setdefault("uncertainties", []).append(
            "Dropped source URLs not present in web-search provenance after canonical normalization: "
            + ", ".join(unsupported_urls[:5])
        )

    input_tokens, output_tokens = base.usage_of(response)
    model_cost = base.estimate_model_cost(selected_model, input_tokens, output_tokens)
    observed_web_calls = base.count_web_search_calls(response)
    max_observed_calls = requested_web_calls + overrun_tolerance
    if observed_web_calls > max_observed_calls:
        raise SystemExit(
            f"web_search_call_limit_exceeded:{observed_web_calls}:requested={requested_web_calls}:tolerance={overrun_tolerance}"
        )
    web_overrun = max(0, observed_web_calls - requested_web_calls)
    if web_overrun:
        output.setdefault("uncertainties", []).append(
            f"Hosted provider returned {observed_web_calls} web-search calls despite requested max {requested_web_calls}; "
            "the one-call provider overrun was accepted, fully costed and recorded."
        )

    web_call_cost = float(policy["budget"].get("web_search_tool_call_cost_usd_snapshot", 0.01))
    web_tool_cost = round(observed_web_calls * web_call_cost, 8)
    total_cost = round(model_cost + web_tool_cost, 8)
    hard_cap = float(policy["budget"]["single_task_hard_cap_usd"])
    if total_cost > hard_cap:
        raise SystemExit(f"single_task_total_cost_exceeded:{total_cost}")

    receipt = {
        "contract": "MEME_ALPHA_RESEARCH_RECEIPT_v1",
        "task_id": task_id,
        "task_path": str(task_path),
        "input_sha256": task_hash,
        "request_sha256": request_hash,
        "output_sha256": base.sha256_bytes(base.canonical_bytes(output)),
        "response_id": response.get("id"),
        "model": selected_model,
        "reasoning_effort": effort,
        "max_output_tokens": max_output_tokens,
        "web_search_enabled": enable_web,
        "web_source_count": len(observed_urls),
        "web_search_call_count": observed_web_calls,
        "web_search_call_limit_requested": requested_web_calls,
        "web_search_call_overrun_tolerance": overrun_tolerance,
        "web_search_call_overrun": web_overrun,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_model_cost_usd": model_cost,
        "estimated_web_tool_cost_usd": web_tool_cost,
        "estimated_total_cost_usd": total_cost,
        "hosted_tool_cost_in_estimate": True,
        "created_unix": int(time.time()),
        "authority": policy["authority"],
    }
    (output_dir / "output.json").write_bytes(base.canonical_bytes(output))
    (output_dir / "receipt.json").write_bytes(base.canonical_bytes(receipt))
    (output_dir / "web_sources.json").write_bytes(base.canonical_bytes({"urls": sorted(observed_urls)}))
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Meme Alpha runtime v1.1 with bounded provider web-call overshoot handling.")
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
