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

MAX_ONESHOT_MISSION = "S1-ELITE-REPAIR-TRIAGE-SOL61-MAX-20261106B"
LEGACY_MAX_UNCERTAIN = "SOL61-MAX-CYCLE-RECOVERY-ALTSEASON-20261105"
LEGACY_MAX_INCOMPLETE = "S1-ELITE-RESILIENCE-SOL61-MAX-20261106"
PUBLIC_CONSENT_COMMENT = 6683279250
MAX_CLAIM_PREFIX = "RL_SOL_MAX_PRE_HTTP_CLAIM_V1"

def effective_registry_for_mission(
    registry: dict, packet: dict, mission_id: str, *,
    model_available=None,
) -> dict:
    """Any new owner-bound public MAX mission, never an arbitrary owner comment.

    Model choice is pinned to the verified Sol-only source policy and current
    gateway price table. A newer Sol needs project GET proof to be promoted.
    """
    from scripts.api_agent import sol_max_shared_policy_v1 as sol_policy
    from scripts.api_agent.api_gateway import PRICES_PER_MILLION
    output = json.loads(json.dumps(registry))
    task = output.get("tasks", {}).get(TASK_NAME)
    if (not isinstance(task, dict)
            or (task.get("model"), task.get("reasoning_effort")) != ("gpt-6.1-sol", "high")):
        raise ValueError("RESEARCH_LAB_BASE_TASK_POLICY_CHANGED")
    effort = packet.get("reasoning_effort", "high")
    if effort == "max":
        if (not isinstance(mission_id, str)
                or re.fullmatch(r"[A-Z][A-Z0-9-]{15,109}", mission_id) is None
                or packet.get("mission_id") != mission_id
                or packet.get("original_owner_issue") != 1156
                or packet.get("max_runs_for_this_release") != 1
                or packet.get("review_only_no_code_write") is not True
                or not zero_authority(packet.get("authority"))):
            raise ValueError("MAX_ONE_SHOT_MANDATE_NOT_BOUND")
        if (packet.get("public_storage_consent_30_days") is not True
                or packet.get("public_source_only") is not True
                or type(packet.get("public_storage_consent_comment_id")) is not int
                or packet["public_storage_consent_comment_id"] <= 0
                or packet.get("one_shot_owner_mandate") !=
                   ("https://github.com/Donh91/Investering-Framework-Archive-v1/"
                    "issues/1156#issuecomment-"
                    + str(packet["public_storage_consent_comment_id"]))):
            raise ValueError("MAX_PUBLIC_BACKGROUND_STORAGE_CONSENT_REQUIRED")
        requested = packet.get("max_model_output_tokens_per_new_attempt")
        if (type(requested) is not int or not 2048 <= requested <=
                sol_policy.MAX_OUTPUT):
            raise ValueError("MAX_OUTPUT_LIMIT_INVALID_OR_MODEL_CAP_EXCEEDED")
        policy = load_json(Path(__file__).resolve().parents[2] /
                           sol_policy.POLICY_PATH)
        selected = sol_policy.choose_model(
            policy, PRICES_PER_MILLION, available=model_available)
        if requested > selected["max_output_tokens"]:
            raise ValueError("MAX_OUTPUT_LIMIT_INVALID_OR_MODEL_CAP_EXCEEDED")
        task["model"] = selected["id"]
        task["reasoning_effort"] = "max"
        task["max_output_tokens"] = requested
        task["max_attempts"] = 1
        task["recoverable_background"] = True
        task["public_background_storage_authorized"] = True
        instruction = task.get("governed_instruction")
        if isinstance(instruction, str):
            task["governed_instruction"] = instruction.replace(
                "MODEL_USED=gpt-6.1-sol", "MODEL_USED=" + selected["id"])
    elif effort != "high":
        raise ValueError("RESEARCH_EFFORT_NOT_ADMITTED")
    return output

def reserve_native_max_claim(root: Path, mission_id: str, issue_number: int,
                             comment_id: str) -> dict:
    """Any owner's one frozen MAX mission, same original bot claim lane.

    Conversation identity is irrelevant: only authenticated GitHub OWNER
    events, source-frozen packets and independent native pre-HTTP claims count.
    """
    import os
    from scripts.api_agent import sol_max_shared_policy_v1 as sol_policy
    from scripts.api_agent.api_gateway import PRICES_PER_MILLION
    queue = load_json(root / QUEUE_PATH)
    row = mission_row(queue, mission_id)
    packet_path = root / str(row.get("mission_packet") or "")
    packet = load_json(packet_path)
    if packet.get("reasoning_effort", "high") != "max":
        return {"state": "NORMAL_HIGH_NO_EXTRA_CLAIM"}
    if (issue_number != 1476
            or os.environ.get("GITHUB_REPOSITORY") !=
               "Donh91/Investering-Framework-Archive-v1"
            or os.environ.get("GITHUB_EVENT_NAME") != "issue_comment"
            or os.environ.get("GITHUB_ACTOR") != "Donh91"
            or os.environ.get("GITHUB_RUN_ATTEMPT") != "1"
            or not os.environ.get("GH_TOKEN")):
        raise ValueError("MAX_NATIVE_OWNER_EVENT_INVALID")
    def gh(*args):
        return subprocess.check_output(["gh", *args], text=True, timeout=90)
    head = current_head(root)
    native_head = json.loads(gh(
        "api", "repos/Donh91/Investering-Framework-Archive-v1/"
        "git/ref/heads/main")).get("object", {}).get("sha")
    if head != native_head:
        raise ValueError("MAX_NATIVE_MAIN_HEAD_DRIFT")
    event = load_json(Path(os.environ["GITHUB_EVENT_PATH"]))
    comment = event.get("comment") or {}
    if (str(comment.get("id")) != str(comment_id)
            or (comment.get("user") or {}).get("login") != "Donh91"
            or comment.get("author_association") != "OWNER"
            or (event.get("issue") or {}).get("number") != 1476):
        raise ValueError("MAX_NATIVE_OWNER_COMMENT_INVALID")
    # Recompute current *actual* model/source/price before irrevocable claim.
    effective_path = root / "runtime/research-lab-sol/effective_registry.json"
    context_path = root / "runtime/research-lab-sol/context.json"
    if not effective_path.is_file() or not context_path.is_file():
        raise ValueError("MAX_FROZEN_SOURCE_OR_MODEL_ABSENT")
    frozen = load_json(effective_path)["tasks"][TASK_NAME]
    effective = effective_registry_for_mission(
        load_json(root / "research/api_agent/API_TASK_REGISTRY_v1.json"),
        packet, mission_id, model_available=lambda name: name == frozen["model"])
    if effective["tasks"][TASK_NAME] != frozen:
        raise ValueError("MAX_FROZEN_MODEL_DRIFT")
    policy = load_json(root / sol_policy.POLICY_PATH)
    models = sol_policy.validated_models(policy, PRICES_PER_MILLION)
    selected = next((x for x in models if x["id"] == frozen["model"]), None)
    if selected is None:
        raise ValueError("MAX_MODEL_NOT_SOURCE_VERIFIED")
    quoted = sol_policy.quoted_upper_usd(
        context_path.stat().st_size, frozen["max_output_tokens"], selected)
    # The original account-wide and lane admission already reserved USD3.
    if quoted > 3.0:
        raise ValueError("MAX_PRICE_EXCEEDS_NATIVE_PAID_CLAIM")
    consent_id = packet["public_storage_consent_comment_id"]
    native_consent = json.loads(gh(
        "api", "repos/Donh91/Investering-Framework-Archive-v1/issues/comments/"
        + str(consent_id)))
    consent_body = native_consent.get("body") or ""
    if mission_id == MAX_ONESHOT_MISSION:
        # Historical original B has its own exact, already-consumed consent.
        marker = "<!-- OWNER_RELEASE_SOL_MAX_PUBLIC_30D_20261106B -->"
        allowed = (consent_id == PUBLIC_CONSENT_COMMENT and
                   isinstance(consent_body, str) and
                   consent_body.startswith(marker) and
                   mission_id in consent_body and "30 DAYS" in consent_body)
    else:
        packet_digest = sha256_bytes(packet_path.read_bytes())
        marker = ("<!-- SOL_MAX_OWNER_RELEASE_V1 mission=" + mission_id
                  + " packet_sha256=" + packet_digest + " -->")
        allowed = (isinstance(consent_body, str)
                   and consent_body.startswith(marker)
                   and "PUBLIC SOURCE ONLY" in consent_body
                   and "30 DAYS" in consent_body
                   and ("max_output_tokens="
                        + str(frozen["max_output_tokens"])) in consent_body)
    if ((native_consent.get("user") or {}).get("login") != "Donh91"
            or native_consent.get("issue_url") !=
               "https://api.github.com/repos/Donh91/Investering-Framework-Archive-v1/issues/1156"
            or not allowed):
        raise ValueError("MAX_NATIVE_PUBLIC_30D_OWNER_CONSENT_UNVERIFIED")
    def claims():
        pages = json.loads(gh("api", "--paginate", "--slurp",
            "repos/Donh91/Investering-Framework-Archive-v1/"
            "issues/1476/comments?per_page=100"))
        if not isinstance(pages, list) or any(
                not isinstance(page, list) for page in pages):
            raise ValueError("MAX_CLAIM_CENSUS_UNTRUSTED")
        return [item for page in pages for item in page
                if isinstance(item, dict)
                and str(item.get("body") or "").startswith(
                    MAX_CLAIM_PREFIX + " mission=" + mission_id + " ")]
    if claims():
        raise ValueError("MAX_CLAIM_ALREADY_EXISTS_NO_REPOST")
    body = (f"{MAX_CLAIM_PREFIX} mission={mission_id} head={head} "
            f"trigger={comment_id} max_usd=3.00")
    gh("issue", "comment", "1476", "--repo",
       "Donh91/Investering-Framework-Archive-v1", "--body", body)
    found = [item for item in claims() if item.get("body") == body
             and (item.get("user") or {}).get("login") == "github-actions[bot]"]
    if len(found) != 1:
        raise ValueError("MAX_CLAIM_NATIVE_READBACK_MISSING_NO_POST")
    return {"status": "NATIVE_PRE_HTTP_CLAIM_VERIFIED",
            "claim_id": found[0].get("id"), "mission": mission_id,
            "head": head, "max_usd": 3.0, "model": frozen["model"],
            "quoted_upper_usd": quoted}

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



def paid_attempt_admission(repo_root: Path, mission_id: str, issue_number: int) -> tuple[bool, str]:
    """Fail closed BEFORE payment on already-completed/ambiguous mission evidence.

    An issue comment is not a new owner release. Mission IDs are single paid
    attempts unless a separate new frozen mission/packet is explicitly created.
    Any prior output directory can represent an uncertain paid liability; do
    not retry until existing owner reconciles provider charges and releases a
    truly new mission identity. No provider/network calls here.
    """
    if mission_id == LEGACY_MAX_UNCERTAIN:
        return False, "LEGACY_MAX_PAID_POST_OUTCOME_UNKNOWN_NO_REPOST"
    if mission_id == LEGACY_MAX_INCOMPLETE:
        return False, "LEGACY_MAX_TERMINAL_INCOMPLETE_NO_REPOST"
    try:
        queue = load_json(repo_root / QUEUE_PATH)
    except (OSError, ValueError, TypeError):
        return False, "QUEUE_UNREADABLE"
    if (queue.get("status") != "ACTIVE" or
            queue.get("trigger_issue") != issue_number or
            queue.get("model") != MODEL or
            queue.get("task_name") != TASK_NAME or
            not zero_authority(queue.get("authority"))):
        return False, "QUEUE_AUTHORITY_NOT_VERIFIED"
    missions = queue.get("missions")
    if not isinstance(missions, list):
        return False, "MISSION_CENSUS_INVALID"
    active = [row for row in missions if isinstance(row, dict)
              and row.get("state") == "ACTIVE_RELEASED"]
    if (len(active) != 1 or queue.get("active_mission") != mission_id or
            active[0].get("mission_id") != mission_id):
        return False, "MISSION_NOT_CURRENTLY_RELEASED"
    row = active[0]
    if row.get("new_paid_attempts_authorized") is False:
        return False, "PAID_MISSION_HOLD"
    root = repo_root / "research/api_agent/outputs/research_lab_sol" / mission_id
    if root.exists():
        if not root.is_dir() or root.is_symlink():
            return False, "PRIOR_PAID_LIABILITY_AMBIGUOUS"
        # No matter which earlier comment/trigger or receipt status: an
        # existing output path can mean the provider already incurred cost.
        if any(root.rglob("*")):
            return False, "PRIOR_MISSION_ATTEMPT_OR_LIABILITY_EXISTS"
    return True, "NEW_OWNER_RELEASE"



def clipped_file(repo_root: Path, rel: str) -> dict[str, Any]:
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or any(
            part in ("", ".", "..") or part.casefold() in
            ("secrets", "vault", ".env", "private") for part in Path(rel).parts):
        raise ValueError("PUBLIC_SOURCE_PATH_NOT_ALLOWLISTED")
    path = repo_root / rel
    if (not path.is_file() or not path.resolve().is_relative_to(repo_root.resolve())):
        raise ValueError(f"context_path_missing_or_private:{rel}")
    raw = path.read_bytes()
    if re.search(rb"sk-proj-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_-]{16,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", raw):
        raise ValueError("PUBLIC_SOURCE_CONTAINS_CREDENTIAL")
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
    from scripts.api_agent import sol_max_shared_policy_v1 as sol_policy
    from scripts.api_agent.api_gateway import PRICES_PER_MILLION
    import os
    # Only approved newer Sol models receive a non-billable availability GET.
    effective = effective_registry_for_mission(
        load_json(repo_root / "research/api_agent/API_TASK_REGISTRY_v1.json"),
        packet, mission_id,
        model_available=lambda model: sol_policy.project_model_available(
            model, os.environ.get("OPENAI_API_KEY", "")))
    selected_model = effective["tasks"][TASK_NAME]["model"]
    head = current_head(repo_root)
    context = {
        "contract": "RESEARCH_LAB_SOL_CONTEXT_v1",
        "authority": "ADVISORY_READ_ONLY",
        "private_data_included": False,
        "public_source_only": True,
        "task": TASK_NAME,
        "model": selected_model,
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
    if packet.get("reasoning_effort") == "max":
        selected = next(row for row in sol_policy.validated_models(
            load_json(repo_root / sol_policy.POLICY_PATH),
            PRICES_PER_MILLION) if row["id"] == selected_model)
        sol_policy.quoted_upper_usd(
            len(payload), effective["tasks"][TASK_NAME]["max_output_tokens"],
            selected)

    required_outputs = packet.get("required_outputs", [])
    prompt = "\n".join([
        f"Research Lab mission: {mission_id}",
        f"Question: {packet.get('question')}",
        f"Hypothesis: {packet.get('hypothesis')}",
        f"Baseline: {packet.get('baseline')}",
        f"Falsifier: {packet.get('falsifier')}",
        f"Kill condition: {packet.get('kill_condition')}",
        "",
        f"Perform the independent {selected_model} scientific/economic arm only.",
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
        f"VERDICT=VERIFIED; MODEL_USED={selected_model}; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;",
        f"VERDICT=WEAKENED; MODEL_USED={selected_model}; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;",
        f"VERDICT=REJECTED; MODEL_USED={selected_model}; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;",
        f"VERDICT=INSUFFICIENT_EVIDENCE; MODEL_USED={selected_model}; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;",
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
    (output_dir / "effective_registry.json").write_text(json.dumps(effective, sort_keys=True, indent=2) + "\n")
    manifest["reasoning_effort"] = effective["tasks"][TASK_NAME]["reasoning_effort"]
    manifest["selected_model"] = selected_model
    (output_dir / "context_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return manifest


def validate(output_dir: Path) -> dict[str, Any]:
    receipt = load_json(output_dir / "output" / "receipt.json")
    output = load_json(output_dir / "output" / "output.json")
    if receipt.get("status") != "PASS":
        raise ValueError("research_lab_sol_receipt_not_pass")
    if receipt.get("task") != TASK_NAME:
        raise ValueError("research_lab_sol_task_binding_invalid")
    context = load_json(output_dir / "context.json")
    frozen = load_json(output_dir / "effective_registry.json")["tasks"][TASK_NAME]
    expected_effort = context.get("mission_packet", {}).get("reasoning_effort", "high")
    expected_model = frozen["model"]
    if (expected_effort not in ("high", "max")
            or context.get("model") != expected_model
            or receipt.get("model") != expected_model
            or receipt.get("reasoning_effort") != expected_effort):
        raise ValueError("research_lab_sol_model_binding_invalid")
    cost = receipt.get("estimated_cost_usd")
    if isinstance(cost, bool) or not isinstance(cost, (int, float)) or not 0 <= float(cost) <= 3.0:
        raise ValueError("research_lab_sol_cost_invalid")
    if receipt.get("forecast_candidate_count") != 0 or output.get("forecast_candidates") != []:
        raise ValueError("research_lab_sol_forecast_candidates_forbidden")
    summary = str(output.get("summary") or "")
    valid_prefixes = tuple(
        f"VERDICT={verdict}; MODEL_USED={expected_model}; NO_CODE_WRITE_PERFORMED; NO_AUTHORITY_CHANGE;"
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
        from os import environ
        transport = output_dir / "output" / "transport"
        handle_path = transport / "response_handle.json"
        if handle_path.is_file():
            handle = load_json(handle_path)
            origin = environ.get("GITHUB_RUN_ID", "")
            lines.append("Durable original provider response ID EXISTS; analysis is not yet accepted.")
            lines.append("GET-only recovery is possible from the original Actions artifact. No second POST.")
            if re.fullmatch(r"[1-9][0-9]{0,17}", origin):
                lines.append("Existing owner recovery marker: "
                             + "[RESEARCH_LAB_SOL_COLLECT] origin=" + origin)
        elif (transport / "attempt.json").is_file():
            lines.append("Paid POST may have reached provider but no response ID was received. "
                         "Billing UNKNOWN. No second POST or invented GET.")
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


    admission = sub.add_parser("check-paid-admission")
    admission.add_argument("--repo-root", type=Path, default=Path("."))
    admission.add_argument("--mission-id", required=True)
    admission.add_argument("--issue-number", type=int, required=True)
    admission.add_argument("--comment-id", required=True)
    admission.add_argument("--github-output", type=Path, required=True)

    build_p = sub.add_parser("build")
    build_p.add_argument("--repo-root", type=Path, default=Path("."))
    build_p.add_argument("--output-dir", type=Path, required=True)
    build_p.add_argument("--mission-id", required=True)
    build_p.add_argument("--issue-number", type=int, required=True)
    build_p.add_argument("--comment-id", required=True)

    claim = sub.add_parser("reserve-max-claim")
    claim.add_argument("--repo-root", type=Path, default=Path("."))
    claim.add_argument("--mission-id", required=True)
    claim.add_argument("--issue-number", type=int, required=True)
    claim.add_argument("--comment-id", required=True)

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
    elif args.cmd == "check-paid-admission":
        admitted, reason = paid_attempt_admission(args.repo_root, args.mission_id,
                                                  args.issue_number)
        dest = (f"research/api_agent/outputs/research_lab_sol/{args.mission_id}"
                f"/issue-{args.issue_number}/comment-{args.comment_id}")
        # Own the workflow step outputs; do not accidentally append duplicate
        # runner output names across two contradictory admissions.
        with args.github_output.open("a", encoding="utf-8") as out:
            out.write(f"run_analysis={str(admitted).lower()}\n")
            out.write(f"dest={dest}\n")
        print(json.dumps({"admitted": admitted, "reason": reason,
                          "mission": args.mission_id}, sort_keys=True))
    elif args.cmd == "build":
        print(json.dumps(build(args.repo_root, args.output_dir, args.mission_id, args.issue_number, args.comment_id), sort_keys=True))
    elif args.cmd == "reserve-max-claim":
        print(json.dumps(reserve_native_max_claim(args.repo_root, args.mission_id,
                                                  args.issue_number, args.comment_id), sort_keys=True))
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
