#!/usr/bin/env python3
"""Read-only research replay of ORIGINAL Official Compass source-age metadata.

Pinned Git objects only; no network, no market forecasts, no signal or trading.
See Task 2 scientific owner #1596 / source-integrity owner #1827.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

COMMIT = "ef896285328cb0f8ae27f8ddd0eaa38fdc16a5e3"
MONTH_TREE = "5185a933dbc1bd72bfe8fe0e397c292a908f2a71"
MONTH_PATH = "04_MARKET_LEARNING/handlekompas/official/daily/2026/10"
FILE_PATTERN = re.compile(r"^(0[1-9]|[12][0-9]|30)/CMP-202610\1-[a-f0-9]+\.json$")
EXPECTED = {
    "files_read": 257,
    "older_than_30m": 169,
    "older_than_60m": 77,
    "older_than_120m": 37,
    "older_than_180m": 19,
    "official_OK": 225,
    "official_DEGRADED": 32,
    "freshness_PASS": 238,
    "packet_within_30m_source_older_30m": 108,
    "official_OK_source_older_30m": 143,
}


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def original_records(repo: Path) -> list[dict]:
    """Verify pinned commit-to-month-tree identity; read only immutable Git blobs."""
    actual_tree = git(repo, "rev-parse", f"{COMMIT}:{MONTH_PATH}").decode().strip()
    if actual_tree != MONTH_TREE:
        raise ValueError("frozen_october_tree_sha_mismatch")
    records = []
    seen = set()
    invalid_metadata = []
    for entry in git(repo, "ls-tree", "-r", "-z", MONTH_TREE).split(b"\0"):
        if not entry:
            continue
        header, raw_path = entry.split(b"\t", 1)
        mode, kind, raw_sha = header.decode().split(" ")
        rel_path = raw_path.decode()
        if not FILE_PATTERN.fullmatch(rel_path):
            continue
        if kind != "blob" or mode != "100644":
            raise ValueError("unexpected_original_file_type")
        if rel_path in seen:
            raise ValueError("duplicate_original_path")
        seen.add(rel_path)
        content = git(repo, "cat-file", "blob", raw_sha)
        doc = json.loads(content)
        if not isinstance(doc, dict):
            raise ValueError("invalid_official_json")
        # Inspect every original immutable record, and report exactly which
        # paths fail before scoring any aggregate. Never fill missing ages.
        try:
            summarize([doc])
        except (KeyError, TypeError, ValueError) as exc:
            invalid_metadata.append({
                "path": rel_path,
                "error_type": type(exc).__name__,
                "reason": str(exc)[:120],
            })
        records.append(doc)
    if len(records) != 257:
        raise ValueError(f"original_population_changed:{len(records)}")
    if invalid_metadata:
        raise ValueError(
            "original_official_metadata_invalid:" +
            json.dumps({
                "count": len(invalid_metadata),
                "examples": invalid_metadata[:32],
            }, sort_keys=True)
        )
    return records


def age(checks: list[dict], lane: str) -> int:
    found = [c.get("age_seconds") for c in checks if c.get("lane") == lane]
    if len(found) != 1 or type(found[0]) is not int or found[0] < 0:
        raise ValueError(f"missing_or_invalid_age:{lane}")
    return found[0]


def summarize(records: list[dict]) -> dict:
    """Shadow threshold quality coverage, NOT a forecast or counterfactual policy."""
    r = {key: 0 for key in EXPECTED}
    for doc in records:
        freshness = doc["source_bindings"]["auto_market_state"]["freshness"]
        checks = freshness["checks"]
        src = age(checks, "source_observation_freshness")
        pkt = age(checks, "auto_market_state_packet")
        status = doc["data_status"]
        if status not in ("OK", "DEGRADED"):
            raise ValueError(f"unexpected_official_status:{status}")
        r["files_read"] += 1
        for minutes in (30, 60, 120, 180):
            r[f"older_than_{minutes}m"] += int(src > minutes * 60)
        r[f"official_{status}"] += 1
        r["freshness_PASS"] += int(freshness["status"] == "PASS")
        r["packet_within_30m_source_older_30m"] += int(pkt <= 1800 and src > 1800)
        r["official_OK_source_older_30m"] += int(status == "OK" and src > 1800)
    return r


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--verify", action="store_true",
                        help="fail if snapshot counts differ from published immutable census")
    args = parser.parse_args()
    counts = summarize(original_records(args.repo))
    if args.verify and counts != EXPECTED:
        raise SystemExit(f"FROZEN_CENSUS_MISMATCH: {counts!r}")
    out = {
        "contract": "TASK2_COMPASS_OFFICIAL_SOURCE_AGE_REPLAY_v1",
        "evidence_class": "PUBLIC_RESEARCH_SOURCE_QUALITY_ONLY",
        "source_commit": COMMIT,
        "source_tree": MONTH_TREE,
        "counts": counts,
        "source_age_only_eligible": {
            "30m": counts["files_read"] - counts["older_than_30m"],
            "60m": counts["files_read"] - counts["older_than_60m"],
            "120m": counts["files_read"] - counts["older_than_120m"],
            "180m": counts["files_read"] - counts["older_than_180m"],
        },
        "original_pit_admitted": False,
        "trade_permission": "NONE",
        "warning": "Descriptive original source age only. No true first-known, no investor delivery, no predictive skill or causal gate benefit.",
    }
    print(json.dumps(out, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
