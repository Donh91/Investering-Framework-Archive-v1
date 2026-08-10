#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CONTROL_PATH = ".github/workflows/daily-capture-architecture-gate.yml"
HOURLY_SOURCE_PATHS = {
    "scripts/daily_capture/build_hourly_sequence.py",
    ".github/workflows/hourly-sequence-capture.yml",
}
FARSIDE_SOURCE_PATHS = {
    "scripts/data_terminal/farside_etf_owner.py",
    ".github/workflows/daily-settled-etf-calibration.yml",
}


def normalize(path: str) -> str:
    value = path.strip()
    return value[2:] if value.startswith("./") else value


def classify(paths: list[str]) -> dict[str, bool]:
    normalized = {normalize(path) for path in paths if path.strip()}
    control_changed = CONTROL_PATH in normalized
    return {
        "hourly_source": control_changed or bool(normalized & HOURLY_SOURCE_PATHS),
        "farside_source": control_changed or bool(normalized & FARSIDE_SOURCE_PATHS),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Enable all live source scopes for manual verification.")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()

    paths = [] if args.all else [line.rstrip("\n") for line in sys.stdin]
    result = {"hourly_source": True, "farside_source": True} if args.all else classify(paths)
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as handle:
            for key, value in result.items():
                handle.write(f"{key}={'true' if value else 'false'}\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
