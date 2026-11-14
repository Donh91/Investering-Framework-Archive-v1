#!/usr/bin/env python3
"""Master Monday weekly idempotency: one paid calibration and one publication per frozen ISO week.

Why: GitHub delays this account's schedules by about 7 h. Once the Framework Metronome dispatches
Master Monday on time, the late `40 2 * * 1` cron fires a SECOND run for the same week. Without
this guard that second run makes a second paid Terra call and re-publishes (overwrites) the
week's finished outputs with a new delivery pointer (FRAMEWORK_INCIDENT_LEARNING_v1 rule 4:
a clock tick alone must never create new work).

Decision (deterministic, read-only):
  - week already published  -> skip=true  (no freeze commit, no paid call, no re-publication)
  - first run for the week  -> skip=false
  - owner force_reissue     -> skip=false (explicit, owner-initiated workflow_dispatch input only)
Prints GitHub step outputs: skip=<true|false> and reason=<CODE>.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FROZEN_PREFIX = "research/master_monday_preflight/frozen/"
OUTPUT_ROOT = "research/api_agent/outputs/weekly"
POINTER_NAME = "MASTER_MONDAY_DELIVERY_POINTER.json"
WEEK_DIR = re.compile(r"^research/master_monday_preflight/frozen/(\d{4})/W(\d{2})$")


def decide(repo_root: Path, week_dir: str, force_reissue: bool) -> dict:
    match = WEEK_DIR.match(week_dir.strip().rstrip("/"))
    if not match:
        # Fail closed and visibly: an unknown layout must never silently allow a paid call.
        raise ValueError(f"MASTER_MONDAY_WEEK_DIR_UNRECOGNIZED:{week_dir!r}")
    year, week = match.groups()
    pointer = repo_root / OUTPUT_ROOT / year / f"W{week}" / POINTER_NAME
    if force_reissue:
        return {"skip": False, "reason": "OWNER_FORCE_REISSUE", "pointer": pointer.relative_to(repo_root).as_posix()}
    if pointer.is_file():
        return {"skip": True, "reason": "WEEK_ALREADY_PUBLISHED", "pointer": pointer.relative_to(repo_root).as_posix()}
    return {"skip": False, "reason": "FIRST_PUBLICATION_FOR_WEEK", "pointer": pointer.relative_to(repo_root).as_posix()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--week-dir", required=True)
    ap.add_argument("--force-reissue", default="false", help="'true' only from the owner's workflow_dispatch input")
    a = ap.parse_args(argv)
    result = decide(a.repo_root, a.week_dir, str(a.force_reissue).strip().lower() == "true")
    print(f"skip={'true' if result['skip'] else 'false'}")
    print(f"reason={result['reason']}")
    print(f"MASTER_MONDAY_IDEMPOTENCY {result['reason']} {result['pointer']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
