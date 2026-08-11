from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROGRAM_PATH = Path("research/api_agent/mcp/MCP_CONNECTION_EVALUATION_PROGRAM_v1.json")
SCORECARD_PATH = Path("research/api_agent/mcp/evaluations/LATEST_MCP_CONNECTION_SCORECARD.json")
TERMINAL_VERDICTS = {
    "KEEP_RESEARCH_ACTIVE",
    "KEEP_CROSSCHECK_ONLY",
    "SHADOW_OBSERVATION",
    "CANDIDATE_DISCOVERY_ONLY",
    "DIAGNOSTICS_ONLY",
    "HOLD",
    "KILL",
    "DATA_BLOCKED",
}
CEILING_ALLOWED = {
    "RESEARCH_ACTIVE": {"KEEP_RESEARCH_ACTIVE", "SHADOW_OBSERVATION", "HOLD", "KILL", "DATA_BLOCKED"},
    "CROSSCHECK_ACTIVE": {"KEEP_CROSSCHECK_ONLY", "SHADOW_OBSERVATION", "HOLD", "KILL", "DATA_BLOCKED"},
    "SHADOW_OBSERVATION": {"SHADOW_OBSERVATION", "HOLD", "KILL", "DATA_BLOCKED"},
    "CANDIDATE_DISCOVERY_ACTIVE": {"CANDIDATE_DISCOVERY_ONLY", "HOLD", "KILL", "DATA_BLOCKED"},
    "DIAGNOSTICS_ACTIVE": {"DIAGNOSTICS_ONLY", "HOLD", "KILL", "DATA_BLOCKED"},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _next_queue_provider(scorecard: dict[str, Any], current_rank: int) -> str | None:
    rows = sorted((r for r in scorecard.get("providers", []) if int(r.get("queue_rank", 0) or 0) > current_rank), key=lambda r: int(r.get("queue_rank", 0)))
    for row in rows:
        if row.get("state") == "QUEUED":
            return str(row["provider"])
    return None


def apply_evaluation(program: dict[str, Any], scorecard: dict[str, Any], evaluation: dict[str, Any], ai_verdict: str | None) -> dict[str, Any]:
    provider = str(evaluation.get("provider") or "")
    row = next((r for r in scorecard.get("providers", []) if r.get("provider") == provider), None)
    if row is None:
        raise ValueError("provider_not_in_scorecard")
    deterministic = str(evaluation.get("deterministic_verdict") or "")
    if deterministic not in TERMINAL_VERDICTS:
        raise ValueError("invalid_deterministic_verdict")
    final_verdict = deterministic
    if evaluation.get("ai_red_team_required") is True:
        if not ai_verdict:
            row["state"] = "AWAITING_AI_RED_TEAM"
            row["deterministic_score"] = evaluation.get("deterministic_score")
            row["next_action"] = "Run Research Lab Red Team review. AI review cannot override hard blockers or the provider promotion ceiling."
            scorecard["status"] = "AWAITING_AI_RED_TEAM"
            scorecard["active_provider"] = provider
            scorecard["generated_at_utc"] = utc_now()
            return scorecard
        if ai_verdict not in set(program.get("ai_review", {}).get("allowed_verdicts") or []):
            raise ValueError("ai_verdict_not_allowed")
        ceiling = evaluation.get("promotion_ceiling")
        if ai_verdict not in CEILING_ALLOWED.get(str(ceiling), {"HOLD", "KILL", "DATA_BLOCKED"}):
            raise ValueError("ai_verdict_exceeds_promotion_ceiling")
        final_verdict = ai_verdict
    row["deterministic_score"] = evaluation.get("deterministic_score")
    row["ai_verdict"] = ai_verdict if evaluation.get("ai_red_team_required") is True else deterministic
    row["state"] = final_verdict
    row["next_action"] = "Terminal pilot classification recorded. No market, owner or portfolio authority is implied."
    current_rank = int(row.get("queue_rank", 0) or 0)
    next_provider = _next_queue_provider(scorecard, current_rank)
    if next_provider:
        next_row = next(r for r in scorecard["providers"] if r.get("provider") == next_provider)
        next_row["state"] = "READY_FOR_TOOL_DISCOVERY"
        next_row["next_action"] = "Run official MCP tool discovery with no provider tool execution, then enforce the read-only allowlist."
        scorecard["active_provider"] = next_provider
        scorecard["status"] = "PILOT_IN_PROGRESS"
    else:
        scorecard["active_provider"] = None
        scorecard["status"] = "QUEUE_COMPLETE_OR_EXTERNALLY_BLOCKED"
    scorecard["generated_at_utc"] = utc_now()
    return scorecard


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("evaluation", type=Path)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--ai-verdict")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    program = load_json(args.root / PROGRAM_PATH)
    scorecard = load_json(args.root / SCORECARD_PATH)
    evaluation = load_json(args.evaluation)
    updated = apply_evaluation(program, scorecard, evaluation, args.ai_verdict)
    encoded = json.dumps(updated, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
