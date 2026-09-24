#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def test_files(repo_root: Path, roots: list[str]) -> list[str]:
    files: list[str] = []
    for root in roots:
        base = repo_root / root
        if not base.exists():
            continue
        files.extend(path.relative_to(repo_root).as_posix() for path in base.rglob("test_*.py") if path.is_file())
    return sorted(set(files))


def collected_files(collection_text: str) -> set[str]:
    found: set[str] = set()
    for raw in collection_text.splitlines():
        line = raw.strip().replace("\\", "/")
        if "::" not in line:
            continue
        path = line.split("::", 1)[0].lstrip("./")
        if path.endswith(".py"):
            found.add(path)
    return found


def missing_files(repo_root: Path, roots: list[str], collection_text: str) -> list[str]:
    collected = collected_files(collection_text)
    return [path for path in test_files(repo_root, roots) if path not in collected]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--collection-file", type=Path, required=True)
    parser.add_argument("--root", action="append", dest="roots", required=True)
    args = parser.parse_args()
    text = args.collection_file.read_text(encoding="utf-8")
    expected = test_files(args.repo_root, args.roots)
    missing = missing_files(args.repo_root, args.roots, text)
    if missing:
        print("TEST_COLLECTION_TRUTH_FAIL")
        for path in missing:
            print(path)
        raise SystemExit(1)
    print(f"TEST_COLLECTION_TRUTH_PASS files={len(expected)}")


if __name__ == "__main__":
    main()
