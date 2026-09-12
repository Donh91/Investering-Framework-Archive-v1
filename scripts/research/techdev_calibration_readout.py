#!/usr/bin/env python3
"""Report existing T7 calibration evidence without rescoring or changing owners."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

BASE = "06_RESEARCH_LAB/audit_summaries/techdev_calibration_v1/"
OWNERS = {
    "historical_ledger": "06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-claim-ledger__operational.md",
    "calibration": "06_RESEARCH_LAB/forward_tests/2026-07-13__techdev-category-outcome-calibration-v1__canonical-addendum.md",
    "anchors": BASE + "TECHDEV_ANCHOR_CLAIM_OUTCOME_ROWS.csv",
    "categories": BASE + "TECHDEV_CATEGORY_OUTCOME_SUMMARY.csv",
    "revisions": BASE + "TECHDEV_REVISION_VALUE_AND_COST.csv",
}


def _scalar(text: str, field: str) -> int:
    matches = re.findall(rf"^{re.escape(field)}:\s*(\d+)\s*$", text, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError(f"OWNER_COUNT_MISSING_OR_AMBIGUOUS:{field}")
    return int(matches[0])


def _rows(raw: bytes, required: set[str]) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8")), strict=True)
    if not required.issubset(reader.fieldnames or []):
        raise ValueError("OWNER_CSV_REQUIRED_FIELDS_MISSING")
    rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("OWNER_CSV_ROW_WIDTH_INVALID")
    return rows


def build_readout(root: Path, source_commit: str | None = None) -> dict:
    raw = {key: (root / path).read_bytes() for key, path in OWNERS.items()}
    if source_commit is not None:
        if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
            raise ValueError("SOURCE_COMMIT_INVALID")
        for key, path in OWNERS.items():
            pinned = subprocess.run(
                ["git", "show", f"{source_commit}:{path}"], cwd=root,
                capture_output=True, check=True,
            ).stdout
            if pinned != raw[key]:
                raise ValueError(f"SOURCE_COMMIT_BYTES_MISMATCH:{path}")

    owner = raw["calibration"].decode("utf-8")
    historical = raw["historical_ledger"].decode("utf-8")
    historical = historical.split("## Current status\n", 1)[1].split("```yaml\n", 1)[1].split("```", 1)[0]
    anchors = _rows(raw["anchors"], {"claim_id", "category", "scoring_eligibility", "outcome_status"})
    categories = _rows(raw["categories"], {"category", "eligible_n", "SUPPORTED", "NOT_SUPPORTED", "PARTIAL_OR_NEAR_MISS"})
    revisions = _rows(raw["revisions"], {"chain", "original_result", "latest_result", "revision_count", "revision_value", "revision_cost"})
    for rows, key in ((anchors, "claim_id"), (categories, "category"), (revisions, "chain")):
        if any(not row[key] for row in rows) or len({row[key] for row in rows}) != len(rows):
            raise ValueError(f"OWNER_DUPLICATE_OR_EMPTY_ID:{key}")
    eligible = [row for row in anchors if row["scoring_eligibility"] == "ELIGIBLE"]
    if len(anchors) != _scalar(owner, "anchor_outcome_rows_created"):
        raise ValueError("ANCHOR_COUNT_DOES_NOT_RECONCILE")
    if len(eligible) != _scalar(owner, "outcome_eligible_anchor_rows"):
        raise ValueError("ELIGIBLE_COUNT_DOES_NOT_RECONCILE")
    actual = Counter(row["category"] for row in eligible)
    declared = {row["category"]: int(row["eligible_n"]) for row in categories}
    if dict(actual) != declared:
        raise ValueError("CATEGORY_ELIGIBLE_COUNTS_DO_NOT_RECONCILE")
    for row in categories:
        counts = [int(row[field]) for field in ("SUPPORTED", "NOT_SUPPORTED", "PARTIAL_OR_NEAR_MISS")]
        if any(count < 0 for count in counts) or sum(counts) != int(row["eligible_n"]):
            raise ValueError("CATEGORY_STATUS_COUNTS_DO_NOT_RECONCILE")

    verdict_section = owner.split("## Category verdicts\n", 1)
    if len(verdict_section) != 2:
        raise ValueError("CATEGORY_VERDICTS_MISSING")
    verdict_match = re.search(r"```text\n(.*?)\n```", verdict_section[1], re.DOTALL)
    if verdict_match is None:
        raise ValueError("CATEGORY_VERDICTS_MISSING")
    verdicts = dict(line.split(": ", 1) for line in verdict_match.group(1).splitlines())

    return {
        "test_id": "TECHDEV_CLAIM_LEDGER",
        "status": "EXISTING_CALIBRATION_RECONCILED_READOUT_ONLY",
        "authority": "OBSERVABILITY_ONLY",
        "source_commit": source_commit,
        "binding_status": "COMMIT_BYTES_VERIFIED" if source_commit else "WORKTREE_HASHES_ONLY",
        "owners": {key: {"path": path, "bytes": len(raw[key]), "sha256": hashlib.sha256(raw[key]).hexdigest()} for key, path in OWNERS.items()},
        "historical_ledger_counts_preserved": {
            field: _scalar(historical, field) for field in ("source_backed_claim_rows", "valid_outcome_rows", "scored_rows")
        },
        "historical_calibration": {
            "corpus_counts_as_of": "2026-07-13",
            "source_documents": _scalar(owner, "unique_source_documents_at_2026_07_13_audit"),
            "source_claim_rows": _scalar(owner, "source_backed_claim_rows_at_2026_07_13_audit"),
            "anchor_rows": len(anchors),
            "outcome_eligible_anchors": len(eligible),
            "eligibility_counts": dict(sorted(Counter(row["scoring_eligibility"] for row in anchors).items())),
            "anchor_outcome_status_counts": dict(sorted(Counter(row["outcome_status"] for row in anchors).items())),
            "category_summary_as_published": categories,
            "category_verdicts_as_published": verdicts,
            "full_corpus_exhaustive_scoring_claimed": False,
            "historical_rows_promoted_to_prospective_evidence": 0,
        },
        "first_call_and_revision_channels": [
            {field: row[field] for field in ("chain", "original_result", "latest_result", "revision_count", "revision_value", "revision_cost")}
            for row in revisions
        ],
        "limitations": [
            "Navigation and count reconciliation only; underlying historical outcomes were not independently rescored.",
            "Corpus counts belong to the 2026-07-13 audit and are not a census of later prospective claims.",
            "The 44 eligible anchors do not represent exhaustive scoring of all 257 source claims.",
            "Later revision results never replace original claim results.",
        ],
        "authority_firewall": {"market_weight_change": False, "portfolio_action": False, "standalone_execution_authority": "ZERO", "rotation_authority": "SHADOW_ONLY"},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--source-commit")
    args = parser.parse_args()
    print(json.dumps(build_readout(args.repo_root, args.source_commit), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
