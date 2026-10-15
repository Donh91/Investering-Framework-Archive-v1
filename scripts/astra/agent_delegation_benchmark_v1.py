#!/usr/bin/env python3
"""Read-only paired comparison for existing Astra/Sol agent delegation receipts.

Never executes models, dispatches tasks, changes routes, or infers missing costs.
See 07_PROMPTS_AND_AGENTS/astra/2026-10-15__delegation_benchmark_pilot_v1.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any

HASH_RE = re.compile(r"^[a-f0-9]{64}$")
MODES = ("SOLO", "DELEGATED")
CASE_KEYS = {"case_id", "frozen_question_sha256", "frozen_question_path", "evidence_sha256", "evidence_path", "rubric_sha256", "rubric_path", "evidence_class", "variants"}
RUN_KEYS = {"mode", "run_id", "executor_id", "status", "execution_receipt_sha256", "execution_receipt_path", "verification", "usage", "outcome", "delegation"}
USAGE_KEYS = {"input_tokens", "output_tokens", "cost_usd", "wallclock_ms"}
VERIFY_KEYS = {"method", "verifier_id", "status", "verification_receipt_sha256", "verification_receipt_path"}
OUTCOME_KEYS = {"checks_passed", "checks_total", "verified_unique_evidence_count", "material_falsifier_count"}
DELEGATION_KEYS = {"agent_count", "question_hashes"}
ROOT_KEYS = {"contract", "research_only", "registered_at_utc", "task_family", "cases"}


class ContractError(ValueError):
    pass


def _object(v: Any, allowed: set[str], required: set[str], loc: str) -> dict[str, Any]:
    if not isinstance(v, dict):
        raise ContractError(f"{loc}: object required")
    if set(v) - allowed or required - set(v):
        raise ContractError(f"{loc}: invalid field set (extra={sorted(set(v)-allowed)}, missing={sorted(required-set(v))})")
    return v


def _sha(v: Any, loc: str) -> str:
    if not isinstance(v, str) or not HASH_RE.fullmatch(v):
        raise ContractError(f"{loc}: sha256 required")
    return v


def _str(v: Any, loc: str) -> str:
    if not isinstance(v, str) or not v.strip():
        raise ContractError(f"{loc}: nonempty string required")
    return v


def _identity_key(v: str) -> str:
    """Conservative alias key; identity labels are not authenticated by this tool."""
    return unicodedata.normalize("NFKC", v).strip().casefold()


def _nonnegative_int(v: Any, loc: str) -> int:
    if isinstance(v, bool) or not isinstance(v, int) or v < 0:
        raise ContractError(f"{loc}: nonnegative integer required")
    return v


def _nonnegative_num(v: Any, loc: str) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ContractError(f"{loc}: finite nonnegative number required")
    try:
        numeric = float(v)
    except (OverflowError, ValueError) as exc:
        raise ContractError(f"{loc}: finite nonnegative number required") from exc
    if not math.isfinite(numeric) or numeric < 0:
        raise ContractError(f"{loc}: finite nonnegative number required")
    return numeric


def _check_variant(value: Any, mode: str, loc: str) -> dict[str, Any]:
    v = _object(value, RUN_KEYS, RUN_KEYS, loc)
    if v["mode"] != mode or v["status"] not in {"EXECUTED", "BLOCKED", "NOT_RUN"}:
        raise ContractError(f"{loc}: unexpected mode/status")
    _str(v["run_id"], loc + ".run_id")
    executor = _str(v["executor_id"], loc + ".executor_id")
    if v["execution_receipt_sha256"] is not None:
        _sha(v["execution_receipt_sha256"], loc + ".execution_receipt_sha256")
    if v["execution_receipt_path"] is not None:
        _str(v["execution_receipt_path"], loc + ".execution_receipt_path")
    verification = _object(v["verification"], VERIFY_KEYS, VERIFY_KEYS, loc + ".verification")
    if verification["method"] not in {"DETERMINISTIC", "INDEPENDENT_REVIEW"}:
        raise ContractError(f"{loc}: invalid verification method")
    _str(verification["verifier_id"], loc + ".verifier_id")
    if verification["status"] not in {"PASS", "FAIL", "NOT_VERIFIED", "BLOCKED"}:
        raise ContractError(f"{loc}: invalid verification status")
    if verification["verification_receipt_sha256"] is not None:
        _sha(verification["verification_receipt_sha256"], loc + ".verification_receipt_sha256")
    if verification["verification_receipt_path"] is not None:
        _str(verification["verification_receipt_path"], loc + ".verification_receipt_path")
    usage = _object(v["usage"], USAGE_KEYS, USAGE_KEYS, loc + ".usage")
    for key in ("input_tokens", "output_tokens", "wallclock_ms"):
        if usage[key] is not None:
            _nonnegative_int(usage[key], loc + ".usage." + key)
    if usage["cost_usd"] is not None:
        _nonnegative_num(usage["cost_usd"], loc + ".usage.cost_usd")
    outcome = _object(v["outcome"], OUTCOME_KEYS, OUTCOME_KEYS, loc + ".outcome")
    for key in OUTCOME_KEYS:
        if outcome[key] is not None:
            _nonnegative_int(outcome[key], loc + ".outcome." + key)
    if outcome["checks_total"] is not None and outcome["checks_passed"] is not None and outcome["checks_passed"] > outcome["checks_total"]:
        raise ContractError(f"{loc}: checks_passed exceeds checks_total")
    delegation = _object(v["delegation"], DELEGATION_KEYS, DELEGATION_KEYS, loc + ".delegation")
    count = _nonnegative_int(delegation["agent_count"], loc + ".delegation.agent_count")
    if count != (1 if mode == "SOLO" else 2) and (mode == "SOLO" or count not in (2, 3)):
        raise ContractError(f"{loc}: solo must have 1 agent, delegated 2 or 3")
    qs = delegation["question_hashes"]
    if not isinstance(qs, list) or len(qs) != count:
        raise ContractError(f"{loc}: question hashes must equal agent count")
    for q in qs:
        _sha(q, loc + ".question_hashes")
    if len(qs) != len(set(qs)):
        raise ContractError(f"{loc}: duplicate question assignments; replication/adversarial requires separate governed mode")
    if verification["method"] == "INDEPENDENT_REVIEW" and verification["status"] == "PASS" and _identity_key(executor) == _identity_key(verification["verifier_id"]):
        raise ContractError(f"{loc}: self-review cannot claim independence")
    return v


def _eligibility(v: dict[str, Any]) -> list[str]:
    reasons = []
    if v["status"] != "EXECUTED":
        reasons.append("NOT_EXECUTED")
    if v["execution_receipt_sha256"] is None:
        reasons.append("MISSING_EXECUTION_RECEIPT")
    ver = v["verification"]
    if ver["status"] != "PASS" or ver["verification_receipt_sha256"] is None:
        reasons.append("MISSING_PASS_VERIFICATION_RECEIPT")
    # Deterministic tests or a distinctly identified independent verifier are acceptable;
    # no model self-judgement may count as an outcome.
    usage = v["usage"]
    if any(usage[k] is None for k in USAGE_KEYS):
        reasons.append("MISSING_REAL_USAGE_OR_COST")
    outcome = v["outcome"]
    if any(outcome[k] is None for k in OUTCOME_KEYS):
        reasons.append("MISSING_VERIFIED_OUTCOME")
    return reasons


def _readback(root: Path | None, path: Any, expected_sha: Any, label: str) -> list[str]:
    """Check literal bytes, not merely a claimed digest. No network access or model calls."""
    if root is None:
        return [f"{label}:RECEIPT_ROOT_NOT_PROVIDED"]
    if path is None or expected_sha is None:
        return [f"{label}:MISSING_PATH_OR_SHA"]
    if not isinstance(path, str):
        raise ContractError(f"{label}: string path required")
    relative = PurePosixPath(path)
    if (
        not isinstance(path, str)
        or not path.strip()
        or "\\" in path
        or relative.is_absolute()
        or ".." in relative.parts
        or "." in relative.parts
    ):
        raise ContractError(f"{label}: unsafe relative path")
    base = root.resolve()
    candidate = (base / path).resolve()
    if not candidate.is_relative_to(base):
        raise ContractError(f"{label}: file outside receipt root")
    if not candidate.is_file():
        return [f"{label}:SOURCE_FILE_MISSING"]
    if candidate.stat().st_size > 8 * 1024 * 1024:
        return [f"{label}:SOURCE_FILE_TOO_LARGE"]
    h = hashlib.sha256()
    with candidate.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            h.update(chunk)
    if h.hexdigest() != expected_sha:
        return [f"{label}:HASH_MISMATCH"]
    return []


def evaluate(data: Any, *, receipt_root: Path | None = None) -> dict[str, Any]:
    root = _object(data, ROOT_KEYS, ROOT_KEYS, "root")
    if root["contract"] != "AGENT_DELEGATION_PAIRED_BENCHMARK_v1" or root["research_only"] is not True:
        raise ContractError("read-only research contract required")
    _str(root["registered_at_utc"], "registered_at_utc")
    _str(root["task_family"], "task_family")
    cases = root["cases"]
    if not isinstance(cases, list) or not cases:
        raise ContractError("cases must be nonempty")
    seen = set()
    # Cross-case uniqueness is mandatory. Case labels are not independent runs.
    seen_runs: dict[str, str] = {}
    seen_digest: dict[str, str] = {}
    seen_files: dict[str, str] = {}
    # Source bundles may legitimately recur across cases. They must never
    # masquerade as execution/review receipts anywhere in the series.
    seen_source_digest: dict[str, str] = {}
    seen_source_files: dict[str, str] = {}
    rows = []
    for case in cases:
        c = _object(case, CASE_KEYS, CASE_KEYS, "case")
        cid = _str(c["case_id"], "case_id")
        if _identity_key(cid) in seen:
            raise ContractError("duplicate case_id")
        seen.add(_identity_key(cid))
        _sha(c["frozen_question_sha256"], cid + ".frozen_question_sha256")
        _sha(c["evidence_sha256"], cid + ".evidence_sha256")
        _sha(c["rubric_sha256"], cid + ".rubric_sha256")
        _str(c["frozen_question_path"], cid + ".frozen_question_path")
        _str(c["evidence_path"], cid + ".evidence_path")
        _str(c["rubric_path"], cid + ".rubric_path")
        if c["evidence_class"] not in {"PUBLIC_IMMUTABLE_RECEIPT", "RESTRICTED_HASH_BINDING", "SYNTHETIC_FIXTURE"}:
            raise ContractError(f"{cid}: evidence_class must be explicit")
        if not isinstance(c["variants"], list) or len(c["variants"]) != 2:
            raise ContractError(f"{cid}: exactly two variants")
        variants = {}
        for v in c["variants"]:
            if not isinstance(v, dict) or v.get("mode") not in MODES or v["mode"] in variants:
                raise ContractError(f"{cid}: duplicate or unknown variant")
            mode = v["mode"]
            variants[mode] = _check_variant(v, mode, cid + "." + mode)
        if set(variants) != set(MODES):
            raise ContractError(f"{cid}: one SOLO and one DELEGATED required")
        reason = []
        reason += _readback(receipt_root, c["frozen_question_path"], c["frozen_question_sha256"], "FROZEN_QUESTION")
        reason += _readback(receipt_root, c["evidence_path"], c["evidence_sha256"], "EVIDENCE_BUNDLE")
        reason += _readback(receipt_root, c["rubric_path"], c["rubric_sha256"], "FROZEN_RUBRIC")
        for source_type, source_path, source_sha in [
            ("FROZEN_QUESTION", c["frozen_question_path"], c["frozen_question_sha256"]),
            ("EVIDENCE_BUNDLE", c["evidence_path"], c["evidence_sha256"]),
            ("FROZEN_RUBRIC", c["rubric_path"], c["rubric_sha256"]),
        ]:
            if source_sha in seen_digest and seen_digest[source_sha] != cid:
                reason.append(f"REUSED_PRIOR_RECEIPT_AS_SOURCE_DIGEST:{source_type}")
            source_file = str(((receipt_root if receipt_root is not None else Path.cwd()) / source_path).resolve())
            if source_file in seen_files and seen_files[source_file] != cid:
                reason.append(f"REUSED_PRIOR_RECEIPT_AS_SOURCE_PATH_OR_ALIAS:{source_type}")
            seen_source_digest.setdefault(source_sha, cid)
            seen_source_files.setdefault(source_file, cid)
        if _identity_key(variants["SOLO"]["run_id"]) == _identity_key(variants["DELEGATED"]["run_id"]):
            raise ContractError(f"{cid}: two arms cannot share one execution run ID")

        # Separate run IDs are insufficient: two purported independent arms
        # cannot reuse execution OR verification evidence under the same digest,
        # filepath, or filesystem alias (including crossed receipt roles).
        solo, delegated = variants["SOLO"], variants["DELEGATED"]
        pair_executors = {_identity_key(solo["executor_id"]), _identity_key(delegated["executor_id"])}
        for mode in MODES:
            review = variants[mode]["verification"]
            if review["method"] == "INDEPENDENT_REVIEW" and _identity_key(review["verifier_id"]) in pair_executors:
                reason.append(f"PAIR_EXECUTOR_USED_AS_INDEPENDENT_VERIFIER:{mode}")
        def receipts(variant: dict[str, Any]) -> list[tuple[str, str | None, str | None]]:
            ver = variant["verification"]
            return [
                ("EXECUTION", variant["execution_receipt_path"], variant["execution_receipt_sha256"]),
                ("VERIFICATION", ver["verification_receipt_path"], ver["verification_receipt_sha256"]),
            ]
        # An arm's verification cannot be the same physical evidence as its
        # execution, even when both digests are individually valid.
        for mode in MODES:
            execution, verification = receipts(variants[mode])
            _, execution_path, execution_hash = execution
            _, verification_path, verification_hash = verification
            if execution_hash is not None and execution_hash == verification_hash:
                reason.append(f"REUSED_RECEIPT_DIGEST_WITHIN_ARM:{mode}")
            if execution_path is not None and verification_path is not None:
                base = receipt_root if receipt_root is not None else Path.cwd()
                if (base / execution_path).resolve() == (base / verification_path).resolve():
                    reason.append(f"REUSED_RECEIPT_PATH_OR_ALIAS_WITHIN_ARM:{mode}")
        # Inputs are not execution or independent verification receipts.
        # Byte identity, path identity and filesystem aliases must all fail
        # closed even if every individual SHA-256 readback succeeds.
        source_artifacts = [
            ("FROZEN_QUESTION", c["frozen_question_path"], c["frozen_question_sha256"]),
            ("EVIDENCE_BUNDLE", c["evidence_path"], c["evidence_sha256"]),
            ("FROZEN_RUBRIC", c["rubric_path"], c["rubric_sha256"]),
        ]
        for source_type, source_path, source_hash in source_artifacts:
            for mode in MODES:
                for receipt_type, receipt_path, receipt_hash in receipts(variants[mode]):
                    label = f"{source_type}_AS_{receipt_type}_{mode}"
                    if source_hash is not None and source_hash == receipt_hash:
                        reason.append(f"REUSED_SOURCE_AS_RECEIPT_DIGEST:{label}")
                    if source_path is not None and receipt_path is not None:
                        base = receipt_root if receipt_root is not None else Path.cwd()
                        if (base / source_path).resolve() == (base / receipt_path).resolve():
                            reason.append(f"REUSED_SOURCE_AS_RECEIPT_PATH_OR_ALIAS:{label}")
        for solo_type, solo_path, solo_hash in receipts(solo):
            for delegated_type, delegated_path, delegated_hash in receipts(delegated):
                name = f"{solo_type}_SOLO_VS_{delegated_type}_DELEGATED"
                if solo_hash is not None and solo_hash == delegated_hash:
                    reason.append(f"REUSED_RECEIPT_DIGEST:{name}")
                if solo_path is not None and delegated_path is not None:
                    # Path(...).resolve() normalizes '.' / '..' and symlink aliases.
                    # Without receipt_root, path equality is still detectable.
                    base = receipt_root if receipt_root is not None else Path.cwd()
                    if (base / solo_path).resolve() == (base / delegated_path).resolve():
                        reason.append(f"REUSED_RECEIPT_PATH_OR_ALIAS:{name}")
        # Reusing a run or receipt across multiple cases must not inflate the
        # number of matched comparisons, even when case_id and paths differ.
        # Same-case arm collisions are already handled by the checks above.
        for mode in MODES:
            v = variants[mode]
            run_id = _identity_key(v["run_id"])
            if run_id in seen_runs and seen_runs[run_id] != cid:
                reason.append(f"REUSED_RUN_ID_ACROSS_CASES:{run_id}")
            else:
                seen_runs.setdefault(run_id, cid)
            for receipt_type, receipt_path, receipt_sha in receipts(v):
                if receipt_sha is not None and receipt_sha in seen_source_digest and seen_source_digest[receipt_sha] != cid:
                    reason.append(f"REUSED_PRIOR_SOURCE_AS_RECEIPT_DIGEST:{receipt_type}_{mode}")
                if receipt_path is not None:
                    source_path_resolved = str(((receipt_root if receipt_root is not None else Path.cwd()) / receipt_path).resolve())
                    if source_path_resolved in seen_source_files and seen_source_files[source_path_resolved] != cid:
                        reason.append(f"REUSED_PRIOR_SOURCE_AS_RECEIPT_PATH_OR_ALIAS:{receipt_type}_{mode}")
                if receipt_sha is not None:
                    if receipt_sha in seen_digest and seen_digest[receipt_sha] != cid:
                        reason.append(f"REUSED_RECEIPT_DIGEST_ACROSS_CASES:{receipt_type}_{mode}")
                    else:
                        seen_digest.setdefault(receipt_sha, cid)
                if receipt_path is not None:
                    root_dir = receipt_root if receipt_root is not None else Path.cwd()
                    resolved_path = str((root_dir / receipt_path).resolve())
                    if resolved_path in seen_files and seen_files[resolved_path] != cid:
                        reason.append(f"REUSED_RECEIPT_PATH_ACROSS_CASES:{receipt_type}_{mode}")
                    else:
                        seen_files.setdefault(resolved_path, cid)
        if c["evidence_class"] == "SYNTHETIC_FIXTURE":
            reason.append("SYNTHETIC_NOT_EMPIRICAL")
        for mode in MODES:
            reason += [f"{mode}:{v}" for v in _eligibility(variants[mode])]
            v = variants[mode]
            reason += _readback(receipt_root, v["execution_receipt_path"], v["execution_receipt_sha256"], f"{mode}_EXECUTION")
            ver = v["verification"]
            reason += _readback(receipt_root, ver["verification_receipt_path"], ver["verification_receipt_sha256"], f"{mode}_VERIFICATION")
        if any(variants[m]["outcome"]["checks_total"] == 0 for m in MODES):
            reason.append("EMPTY_CHECK_DENOMINATOR")
        if (variants["SOLO"]["outcome"]["checks_total"] is not None
                and variants["DELEGATED"]["outcome"]["checks_total"] is not None
                and variants["SOLO"]["outcome"]["checks_total"] != variants["DELEGATED"]["outcome"]["checks_total"]):
            reason.append("UNMATCHED_CHECK_DENOMINATOR")
        row: dict[str, Any] = {"case_id": cid, "eligible": False, "metadata_eligible": not reason,
                               "empirical_verification": "NOT_ESTABLISHED",
                               "reasons": sorted(set(reason + ["EXTERNAL_AUTHENTICATION_NOT_ESTABLISHED"]))}
        if not reason:
            a, b = variants["SOLO"], variants["DELEGATED"]
            row["cost_delta_usd_delegated_minus_solo"] = round(b["usage"]["cost_usd"] - a["usage"]["cost_usd"], 8)
            row["latency_delta_ms_delegated_minus_solo"] = b["usage"]["wallclock_ms"] - a["usage"]["wallclock_ms"]
            row["checks_passed_delta_delegated_minus_solo"] = b["outcome"]["checks_passed"] - a["outcome"]["checks_passed"]
            row["verified_evidence_delta_delegated_minus_solo"] = b["outcome"]["verified_unique_evidence_count"] - a["outcome"]["verified_unique_evidence_count"]
            row["falsifier_delta_delegated_minus_solo"] = b["outcome"]["material_falsifier_count"] - a["outcome"]["material_falsifier_count"]
            row["equal_validation_denominator"] = a["outcome"]["checks_total"] == b["outcome"]["checks_total"]
        rows.append(row)
    metadata_eligible = [x for x in rows if x["metadata_eligible"]]
    return {
        "contract": "AGENT_DELEGATION_PAIRED_BENCHMARK_RESULT_v1",
        "status": "NO_ELIGIBLE_REAL_PAIRS",
        "metadata_status": "BYTE_CONSISTENT_PAIRS_AVAILABLE" if metadata_eligible else "NO_BYTE_CONSISTENT_PAIRS",
        "comparison_values": "SELF_REPORTED_UNAUTHENTICATED_NOT_EMPIRICAL",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "no_model_calls_or_agent_dispatch": True,
        "paired_eligible_count": 0,
        "byte_consistent_pair_count": len(metadata_eligible),
        "attempted_case_count": len(rows),
        "causal_efficiency_improvement_established": False,
        "rows": rows,
        "note": "This comparator never establishes empirical eligibility. Delta fields are provisional self-reported metadata only. Receipt bytes were checked only when --receipt-root supplied. A matching hash cannot authenticate executor identity, independence, real billed cost, point-in-time eligibility, or causal gain. Those require independent Git/object, provider and accounting verification. Never promote routing automatically.",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Read-only matched solo/delegated receipt comparison")
    p.add_argument("--input", required=True)
    p.add_argument("--output")
    p.add_argument("--receipt-root", help="Read-only root containing exact receipt/evidence files; omitted => all pairs ineligible")
    args = p.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        result = evaluate(data, receipt_root=Path(args.receipt_root) if args.receipt_root else None)
    except (OSError, json.JSONDecodeError, ContractError) as e:
        print("INVALID_BENCHMARK: " + str(e))
        return 2
    text = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
