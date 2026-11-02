"""Fail-closed, allowlisted Endgame supervisor status. Gateway PASS != model success."""
import argparse
import hashlib
import json
import math
import re
import time
from pathlib import Path

WORK_RE = re.compile(r"[A-Z][A-Z0-9_]{7,74}\Z")
DECISION = {"READY": "REVIEW_REQUIRED", "DEGRADED": "FIX_REQUIRED", "BLOCKED": "SOURCE_REQUIRED"}


def _hash(value):
    return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()


def _read(path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("NOT_OBJECT")
    return value


def report(root, work_id, run_id, attempt, now=None):
    """Never emit free-form model content, including on corrupted artifacts."""
    if not WORK_RE.fullmatch(work_id) or not run_id.isdecimal() or int(run_id) < 1:
        raise ValueError("INVALID_HOST_IDS")
    url = f"https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/{run_id}"
    prefix = f"Endgame work {work_id}, run {url}, attempt {attempt}. "
    unknown = ("gateway_status=UNVERIFIED; substantive_status=UNVERIFIED; "
               "disposition=EVIDENCE_MISSING_OR_MISMATCHED; provider_bill=UNVERIFIED; "
               "code_status=NOT_VERIFIED; merge_status=NOT_VERIFIED; NO_RETRY.")
    if attempt != 1:
        return prefix + unknown
    try:
        receipt = _read(root / "live/receipt.json")
        output = _read(root / "live/output.json")
        context = _read(root / "context.json")
        manifest = _read(root / "manifest.json")
        prompt = (root / "prompt.txt").read_bytes()
        if context.get("contract") != "TERRA_ENDGAME_PROGRESS_PACKET_v1":
            raise ValueError("CONTEXT_CONTRACT")
        if context.get("work_id") != work_id or manifest.get("work_id") != work_id:
            raise ValueError("WORK_ID_MISMATCH")
        if context.get("exact_original_main_sha") != manifest.get("main_sha"):
            raise ValueError("SOURCE_MISMATCH")
        if (receipt.get("contract"), receipt.get("task")) != ("API_AGENT_RECEIPT_v3", "TERRA_XHIGH_ENDGAME_PROGRESS_V1"):
            raise ValueError("RECEIPT_CONTRACT")
        if (receipt.get("model"), receipt.get("reasoning_effort")) != ("gpt-6.1-terra", "xhigh"):
            raise ValueError("MODEL_MISMATCH")
        if receipt.get("status") != "PASS" or receipt.get("attempt_count") != 1 or not receipt.get("response_id"):
            raise ValueError("GATEWAY_NOT_VERIFIED")
        if receipt.get("output_hash") != _hash(output) or receipt.get("context_hash") != _hash(context):
            raise ValueError("HASH_MISMATCH")
        if receipt.get("prompt_hash") != hashlib.sha256(prompt).hexdigest():
            raise ValueError("PROMPT_MISMATCH")
        created = receipt.get("created_unix")
        if type(created) is not int or not 0 <= (int(time.time()) if now is None else now) - created <= 3600:
            raise ValueError("STALE_RECEIPT")
        cost = receipt.get("estimated_cost_usd")
        if type(cost) not in (float, int) or not math.isfinite(cost) or not 0 <= cost <= 3:
            raise ValueError("COST_INVALID")
        authority = receipt.get("authority")
        if not isinstance(authority, dict) or not authority or any(v is not False for v in authority.values()):
            raise ValueError("AUTHORITY_INVALID")
        if output.get("forecast_candidates") != [] or output.get("status") not in DECISION:
            raise ValueError("OUTPUT_INVALID")
        status = output["status"]
        return (prefix + f"gateway_status=PASS; substantive_status={status}; "
                f"disposition={DECISION[status]}; estimated_usd={cost:.6f}; "
                "provider_bill=UNVERIFIED; code_status=NOT_IMPLEMENTED_BY_MODEL; "
                "merge_status=NOT_VERIFIED; run_binding=HOST_CONTEXT_ONLY; NO_RETRY. "
                "Original PR tests, independent review and recovery gates remain mandatory.")
    except (OSError, ValueError, TypeError, KeyError):
        return prefix + unknown


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--work-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-attempt", type=int, required=True)
    args = parser.parse_args()
    print(report(args.root, args.work_id, args.run_id, args.run_attempt))


if __name__ == "__main__":
    main()
