#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from scripts.remediation import merge_codex_research_intake as base
    from scripts.remediation.mission_convergence import completion_requires_convergence, validate_receipt
except ModuleNotFoundError:  # direct execution via `python scripts/remediation/...`
    import merge_codex_research_intake as base
    from mission_convergence import completion_requires_convergence, validate_receipt

_BASE_VALID_COMPLETION = base.valid_completion


def valid_completion(repo: Path, task: dict[str, Any]) -> dict[str, Any] | None:
    completion = _BASE_VALID_COMPLETION(repo, task)
    if completion is None:
        return None
    if not completion_requires_convergence(completion):
        return completion
    return completion if validate_receipt(repo, task, completion) is not None else None


def merge(repo: Path, output_dir: Path) -> dict[str, Any]:
    original = base.valid_completion
    base.valid_completion = valid_completion
    try:
        return base.merge(repo, output_dir)
    finally:
        base.valid_completion = original


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("research/remediation"))
    args = parser.parse_args()
    print(json.dumps(merge(args.repo_root, args.output_dir), sort_keys=True))


if __name__ == "__main__":
    main()
