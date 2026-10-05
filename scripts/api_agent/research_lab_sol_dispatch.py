#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

QUEUE_PATH = Path("research/api_agent/research_lab_sol/RESEARCH_LAB_SOL_QUEUE_v1.json")
TASK_NAME = "RESEARCH_LAB_SOL_ANALYSIS"
MODEL = "gpt-6.1-sol"
MAX_CONTEXT_BYTES = 480_000
PER_FILE_CLIP_CHARS = 36_000
ACTIVE_STATES = {"ACTIVE_RELEASED"}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def zero_authority(authority: Any) -> bool:
    return isinstance(authority, dict) and authority and all(v is False for v in authority.values())


def current_head(repo_root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(repo_root), "rev-parse", "HEAD"], text=True).strip()


def parse_mission(comment_body: str) -> str:
    matches = re.findall(r"\[RESEARCH_LAB_SOL\]\s+mission=([A-Z0-9-]+)", comment_body)
    if len(matches) != 1:
        raise ValueError("exactly_one_research_lab_sol_mission_required")
    return matches[0]


def mission_row(queue: dict[str, Any], mission_id: str) -> dict[str, Any]:
    rows = [row for row in queue.get("missions", []) if isinstance(row, dict) and row.get("mission_id") == mission_id]
    if len(rows) != 1:
        raise ValueError("mission_not_whitelisted")
    row = rows[0]
    if row.get("state") not in ACTIVE_STATES:
        raise ValueError(f"mission_not_released:{row.get('state')}")
    return row


def clipped_file(repo_root: Path, rel: str) -> dict[str, Any]:
    path = repo_root / rel
    if not path.is_file():
        raise ValueError(f"context_path_missing:{rel}")
    raw = path.read_bytes()
    text = raw.decode(errors="replace")
    clipped = text if len(text) <= PER_FILE_CLIP_CHARS else text[:PER_FILE_CLIP_CHARS] + "\n[TRUNCATED_AT_BOUND]\n"
    return {
        "path": rel,
        "sha256": sha256_bytes(raw),
        "bytes": len(raw),
        "content": clipped,
    }


def build(repo_root: Path, output_dir: Path, mission_id: str, issue_number: int, comment_id: str) -> dict[str, Any]:
    queue = load_json(repo_root / QUEUE_PATH)
    if queue.get("status") != "ACTIVE":
        raise ValueError("research_lab_sol_queue_not_active")
    if int(queue.get("trigger_issue", -1)) != issue_number:
        raise ValueError("wrong_trigger_issue")
    if queue.get("task_name") != TASK_NAME or queue.get("model") != MODEL:
        raise ValueError("queue_task_or_model_binding_invalid")
    if not zero_authority(queue.get("authority")):
        raise ValueError("queue_authority_not_zero")

    row = mission_row(queue, mission_id)
    packet_path = str(row.get("mission_packet") or "")
    packet = load_json(repo_root / packet_path)
    if packet.get("mission_id") != mission_id:
        raise ValueError("mission_packet_identity_mismatch")
    if not zero_authority(packet.get("authority")):
        raise ValueError("mission_packet_authority_not_zero")

    evidence = [clipped_file(repo_root, rel) for rel in row.get("context_paths", [])]
    head = current_head(repo_root)
    context = {
        "contract": "RESEARCH_LAB_SOL_CONTEXT_v1",
        "authority": "ADVISORY_READ_ONLY",
        "task": TASK_NAME,
        "model": MODEL,
        "mission_id": mission_id,
        "trigger": {"issue_number": issue_number, "comment_id": comment_id},
        "current_main_sha": head,
        "queue_path": str(QUEUE_PATH),
        "queue_sha256": sha256_bytes((repo_root / QUEUE_PATH).read_bytes()),
        "mission_packet_path": packet_path,
        "mission_packet_sha256": sha256_bytes((repo_root / packet_path).read_bytes()),
        "mission_packet": packet,
        "evidence_files": evidence,
        "hard_boundaries": {
            "code_write": False,
            "automatic_merge": False,
            "canonical_promotion": False,
            "market_rule_change": False,
            "threshold_change": False,
            "weight_change": False,
            "budget_change": False,
            "portfolio_action": False,
            "trading_instruction": False,
            "forecast_candidates_required_empty": True,
        },
    }
    payload = canonical_bytes(context)
    if len(payload) > MAX_CONTEXT_BYTES:
        raise ValueError(f"context_too_large:{len(payload)}>{MAX_CONTEXT_BYTES}")

    required_outputs = packet.get("required_outputs", [])
    prompt = "\n".join([
        f"Research Lab mission: {mission_id}",
        f"Question: {packet.get('question')}",
        f"Hypothesis: {packet.get('hypothesis')}",
        f"Baseline: {packet.get('baseline')}",
        f"Falsifier: {packet.get('falsifier')}",
        f"Kill condition: {packet.get('kill_condition')}",
        "",
        "Perform the independent GPT-6.1 Sol scientific/economic arm only.",
        "Try to falsify the hypothesis before preserving it.",
        "Use only the supplied point-in-time evidence package. Do not infer missing rows.",
        "Distinguish source/provenance defects from signal/economic defects.",
        "Quantify decision divergence, false-positive cost, false-negative cost and incremental value versus baseline where the evidence permits it.",
        "If a required calculation cannot be reproduced from supplied evidence, mark it UNKNOWN rather than guessing.",
        "Do not adopt ChatGPT's interim verdict as an answer. Treat it as a claim to attack.",
        f"Required mission outputs: {json.dumps(required_outputs, sort_keys=True)}",
        "",
        "Encode the result in the gateway schema.",
        "summary must start exactly with one of:",
        "VERDICT=VERIFIED; MODEL_USED=gpt-6.1-sol; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;",
        "VERDICT=WEAKENED; MODEL_USED=gpt-6.1-sol; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;",
        "VERDICT=REJECTED; MODEL_USED=gpt-6.1-sol; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;",
        "VERDICT=INSUFFICIENT_EVIDENCE; MODEL_USED=gpt-6.1-sol; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;",
        "Use evidence_for for claims surviving attack, evidence_against for falsification/adverse evidence, uncertainties for UNKNOWNs, hypotheses only for bounded next research tests.",
        "forecast_candidates must be [].",
    ])

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "context.json").write_bytes(payload)
    (output_dir / "prompt.txt").write_text(prompt)
    manifest = {
        "contract": "RESEARCH_LAB_SOL_CONTEXT_MANIFEST_v1",
        "mission_id": mission_id,
        "current_main_sha": head,
        "issue_number": issue_number,
        "comment_id": comment_id,
        "context_sha256": sha256_bytes(payload),
        "context_bytes": len(payload),
        "context_byte_limit": MAX_CONTEXT_BYTES,
        "mission_packet_path": packet_path,
        "evidence_paths": [row["path"] for row in evidence],
        "private_data_included": False,
        "authority": {
            "framework_state_change": False,
            "portfolio_action": False,
            "market_rule_change": False,
            "canonical_promotion": False,
        },
    }
    (output_dir / "context_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def validate(output_dir: Path) -> dict[str, Any]:
    receipt = load_json(output_dir / "output" / "receipt.json")
    output = load_json(output_dir / "output" / "output.json")
    if receipt.get("status") != "PASS":
        raise ValueError("research_lab_sol_receipt_not_pass")
    if receipt.get("task") != TASK_NAME:
        raise ValueError("research_lab_sol_task_binding_invalid")
    if receipt.get("model") != MODEL or receipt.get("reasoning_effort") != "high":
        raise ValueError("research_lab_sol_model_binding_invalid")
    cost = receipt.get("estimated_cost_usd")
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not 0 <= float(cost) <= 3.0:
        raise ValueError("research_lab_sol_cost_invalid")
    if receipt.get("forecast_candidate_count") != 0 or output.get("forecast_candidates") != []:
        raise ValueError("research_lab_sol_forecast_candidates_forbidden")
    summary = str(output.get("summary") or "")
    valid_prefixes = tuple(
        f"VERDICT={verdict}; MODEL_USED=gpt-6.1-sol; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;"
        for verdict in ("VERIFIED", "WEAKENED", "REJECTED", "INSUFFICIENT_EVIDENCE")
    )
    if not summary.startswith(valid_prefixes):
        raise ValueError("research_lab_sol_summary_binding_invalid")
    authority = receipt.get("authority")
    if not zero_authority(authority):
        raise ValueError("research_lab_sol_receipt_authority_not_zero")
    return {"receipt": receipt, "output": output}


def report(output_dir: Path, mission_id: str, comment_id: str, persisted_path: str) -> str:
    result = validate(output_dir)
    receipt = result["receipt"]
    output = result["output"]
    lines = [
        "## RESEARCH_LAB_SOL completed",
        "",
        f"Mission: \`{mission_id}\`",
        f"Trigger comment: {comment_id}",
        f"Model: {receipt['model']}, reasoning: {receipt['reasoning_effort']}",
        f"Tokens: input={receipt['input_tokens']}, output={receipt['output_tokens']}",
        f"Estimated API cost: {float(receipt['estimated_cost_usd']):.6f} USD",
        "",
        str(output["summary"]),
        "",
        "Strongest evidence against / falsification:",
    ]
    evidence_against = output.get("evidence_against") or []
    lines.extend([f"- {item}" for item in evidence_against[:6]] or ["- none"])
    lines += ["", f"Immutable output + receipt: \`{persisted_path}\`.", "", "No authority change was performed."]
    return "\n".join(lines) + "\n"


def failure_report(output_dir: Path, mission_id: str, comment_id: str) -> str:
    receipt_path = output_dir / "output" / "receipt.json"
    lines = [
        "## RESEARCH_LAB_SOL failed closed",
        "",
        f"Mission: \`{mission_id}\`",
        f"Trigger comment: {comment_id}",
    ]
    if receipt_path.exists():
        receipt = load_json(receipt_path)
        lines += [
            f"Model: {receipt.get('model')}",
            f"Receipt status: {receipt.get('status')}",
            f"Estimated API cost: {float(receipt.get('estimated_cost_usd') or 0.0):.6f} USD",
            f"Parse errors: {json.dumps(receipt.get('parse_errors') or [], sort_keys=True)}",
        ]
    else:
        lines.append("No durable paid-call receipt was produced.")
    lines += ["", "No research conclusion was accepted and no authority changed."]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    parse = sub.add_parser("parse-comment")
    parse.add_argument("--comment-body", required=True)
    parse.add_argument("--output", type=Path, required=True)

    build_p = sub.add_parser("build")
    build_p.add_argument("--repo-root", type=Path, default=Path("."))
    build_p.add_argument("--output-dir", type=Path, required=True)
    build_p.add_argument("--mission-id", required=True)
    build_p.add_argument("--issue-number", type=int, required=True)
    build_p.add_argument("--comment-id", required=True)

    val = sub.add_parser("validate")
    val.add_argument("--output-dir", type=Path, required=True)

    rep = sub.add_parser("report")
    rep.add_argument("--output-dir", type=Path, required=True)
    rep.add_argument("--mission-id", required=True)
    rep.add_argument("--comment-id", required=True)
    rep.add_argument("--persisted-path", required=True)
    rep.add_argument("--output", type=Path, required=True)

    fail = sub.add_parser("failure-report")
    fail.add_argument("--output-dir", type=Path, required=True)
    fail.add_argument("--mission-id", required=True)
    fail.add_argument("--comment-id", required=True)
    fail.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()
    if args.cmd == "parse-comment":
        mission = parse_mission(args.comment_body)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(mission + "\n")
        print(mission)
    elif args.cmd == "build":
        print(json.dumps(build(args.repo_root, args.output_dir, args.mission_id, args.issue_number, args.comment_id), sort_keys=True))
    elif args.cmd == "validate":
        result = validate(args.output_dir)
        print(json.dumps({
            "status": "PASS",
            "model": result["receipt"]["model"],
            "estimated_cost_usd": result["receipt"]["estimated_cost_usd"],
        }, sort_keys=True))
    elif args.cmd == "report":
        body = report(args.output_dir, args.mission_id, args.comment_id, args.persisted_path)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body)
        print(json.dumps({"status": "PASS", "output": str(args.output)}, sort_keys=True))
    else:
        body = failure_report(args.output_dir, args.mission_id, args.comment_id)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body)
        print(json.dumps({"status": "PASS", "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
