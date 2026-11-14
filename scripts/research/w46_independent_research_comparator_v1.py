#!/usr/bin/env python3
"""W46 research-only comparator for independently sealed model reports.

No network, API dispatch, forecasting, scoring, trading, or automatic promotion.
The reviewer reports and their expected literal-byte SHA256s must be supplied
after each independent reviewer has sealed its own result.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

CONTRACT = "W46_REVIEW_RESULT_V1"
RESULT_CONTRACT = "W46_BLIND_CROSS_MODEL_COMPARISON_V1"
REVIEWERS = ("GROK", "SOL61_MAX", "FABLE52")
CLAIMS = (
    "SOURCE_CLOCK_AND_COVERAGE",
    "RISK_STATE_ESCALATION",
    "WARNING_LEAD_TIME",
    "DOWNSIDE_RANGE_CALIBRATION",
    "ACTION_UTILITY",
    "ALPHA_INCREMENTAL_VALUE",
)
VERDICTS = {"SUPPORTED", "REFUTED", "INSUFFICIENT_EVIDENCE", "SOURCE_BLOCKED"}
CLOCK_STATES = {"ORIGINAL_PIT_VERIFIED", "PARTIAL_PIT", "UNKNOWN"}


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_sealed_report(path: Path, *, expected_sha256: str, reviewer: str,
                       source_snapshot_sha: str) -> tuple[dict, str]:
    if reviewer not in REVIEWERS:
        raise ValueError("INVALID_REVIEWER")
    raw = path.read_bytes()
    digest = _sha(raw)
    if len(expected_sha256) != 64 or digest != expected_sha256.lower():
        raise ValueError("REPORT_DIGEST_MISMATCH:" + reviewer)
    try:
        data = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("REPORT_INVALID_JSON:" + reviewer) from exc
    if not isinstance(data, dict) or data.get("contract") != CONTRACT:
        raise ValueError("REPORT_WRONG_CONTRACT:" + reviewer)
    if data.get("reviewer") != reviewer:
        raise ValueError("REPORT_REVIEWER_MISMATCH:" + reviewer)
    if data.get("source_snapshot_sha") != source_snapshot_sha:
        raise ValueError("REPORT_SOURCE_SNAPSHOT_MISMATCH:" + reviewer)
    if not isinstance(data.get("native_run_id"), str) or not data["native_run_id"].strip():
        raise ValueError("MISSING_NATIVE_RUN_RECEIPT:" + reviewer)
    if data.get("status") != "SUBMITTED":
        raise ValueError("REPORT_NOT_SEALED:" + reviewer)
    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ValueError("NO_CLAIMS:" + reviewer)
    seen = set()
    for claim in claims:
        if not isinstance(claim, dict):
            raise ValueError("MALFORMED_CLAIM:" + reviewer)
        key = claim.get("claim_id")
        if key not in CLAIMS or key in seen:
            raise ValueError("UNKNOWN_OR_DUPLICATE_CLAIM:" + reviewer)
        seen.add(key)
        if claim.get("verdict") not in VERDICTS:
            raise ValueError("INVALID_VERDICT:" + reviewer)
        if claim.get("first_known_status") not in CLOCK_STATES:
            raise ValueError("INVALID_CLOCK_STATUS:" + reviewer)
        references = claim.get("evidence_refs")
        if not isinstance(references, list) or not references or any(
            not isinstance(ref, str) or len(ref.strip()) < 12 for ref in references
        ):
            raise ValueError("MISSING_OR_INSUFFICIENT_EVIDENCE_REF:" + reviewer)
    return data, digest


def compare(reports: dict[str, dict], *, source_snapshot_sha: str,
            source_digests: dict[str, str]) -> dict:
    if not {"GROK", "SOL61_MAX"}.issubset(reports):
        raise ValueError("BOTH_GROK_AND_SOL_REQUIRED")
    matrix = {name: {c["claim_id"]: c for c in report["claims"]}
              for name, report in reports.items()}
    rows = []
    for key in CLAIMS:
        opinions = {r: matrix[r].get(key) for r in sorted(matrix)}
        values = [v["verdict"] for v in opinions.values() if v is not None]
        if len(values) < 2:
            state = "NOT_ASSESSED_BY_TWO"
        elif any(v["verdict"] == "SOURCE_BLOCKED" or
                 v["first_known_status"] == "UNKNOWN"
                 for v in opinions.values() if v):
            state = "SOURCE_BLOCKED"
        elif len(set(values)) == 1:
            state = "AGREEMENT_ADVISORY_ONLY"
        else:
            state = "DISAGREEMENT_REQUIRES_SOURCE_ADJUDICATION"
        rows.append({
            "claim_id": key, "comparison_state": state,
            "model_verdicts": {r: v["verdict"] if v else "NOT_ASSESSED"
                               for r, v in opinions.items()},
            "model_first_known": {r: v["first_known_status"] if v else "UNKNOWN"
                                  for r, v in opinions.items()},
            "evidence_refs": {r: v["evidence_refs"] if v else []
                              for r, v in opinions.items()},
            "causal_or_economic_edge_proven": False,
        })
    return {
        "contract": RESULT_CONTRACT,
        "source_snapshot_sha": source_snapshot_sha,
        "report_sha256": {r: source_digests[r] for r in sorted(source_digests)},
        "report_native_run_ids": {r: reports[r]["native_run_id"] for r in sorted(reports)},
        "advisory_only": True,
        "automatic_promotion": False,
        "scientific_edge_proven": False,
        "auto_api_runs": False,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-snapshot-sha", required=True)
    parser.add_argument("--grok", type=Path, required=True)
    parser.add_argument("--grok-sha256", required=True)
    parser.add_argument("--sol", type=Path, required=True)
    parser.add_argument("--sol-sha256", required=True)
    parser.add_argument("--fable", type=Path)
    parser.add_argument("--fable-sha256")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = args.source_snapshot_sha
    if len(source) != 40 or any(c not in "0123456789abcdef" for c in source):
        parser.error("SOURCE_MUST_BE_EXACT_40_HEX")
    if bool(args.fable) != bool(args.fable_sha256):
        parser.error("FABLE_AND_DIGEST_MUST_APPEAR_TOGETHER")
    paths = {"GROK": (args.grok, args.grok_sha256),
             "SOL61_MAX": (args.sol, args.sol_sha256)}
    if args.fable:
        paths["FABLE52"] = (args.fable, args.fable_sha256)
    try:
        seen, digests = {}, {}
        for reviewer, (path, digest) in paths.items():
            seen[reviewer], digests[reviewer] = read_sealed_report(
                path, expected_sha256=digest, reviewer=reviewer,
                source_snapshot_sha=source)
        result = compare(seen, source_snapshot_sha=source,
                         source_digests=digests)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
