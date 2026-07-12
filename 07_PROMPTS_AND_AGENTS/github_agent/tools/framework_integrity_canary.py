#!/usr/bin/env python3
"""
Deterministic integrity checks for the Investering framework repository.

No network access and no third-party packages are required.
The tool is read-only. It never writes to the repository tree.
"""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_CORE_PATHS = [
    "AGENTS.md",
    "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md",
    "00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md",
    "00_ARCHIVE_CONTROL/ARCHIVE_MAP_AND_ROUTING.md",
    "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md",
    "01_CORE_FRAMEWORK/governance/2026-07-11__repository-safety-and-backup-policy-v1__canonical.md",
    "01_CORE_FRAMEWORK/governance/2026-07-11__external-vault-activation-and-snapshot-contract-v1-1__canonical.md",
]

PATH_TOKEN_RE = re.compile(
    r"`((?:\.agents|00_ARCHIVE_CONTROL|01_CORE_FRAMEWORK|02_DATA_PING|"
    r"03_WEEKLY_OPERATIONS|04_MARKET_LEARNING|05_CYCLE_NAVIGATOR|"
    r"06_RESEARCH_LAB|07_PROMPTS_AND_AGENTS|08_SOURCE_MATERIAL|"
    r"09_ARCHIVE_INBOX|changelog|data|\.github)/[^`\n]+)`"
)


@dataclass
class Check:
    check_id: str
    status: str
    detail: str
    path: str | None = None


def _read(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def _existing_path_check(root: Path, rel_path: str, check_id: str) -> Check:
    path = root / rel_path
    if path.is_file():
        return Check(check_id, "PASS", "Path exists", rel_path)
    return Check(check_id, "FAIL", "Required path is missing", rel_path)


def _extract_path_tokens(text: str) -> list[str]:
    paths: list[str] = []
    for token in PATH_TOKEN_RE.findall(text):
        token = token.strip()
        if any(char in token for char in ("*", "{", "}", "<", ">")):
            continue
        if token.endswith("/"):
            continue
        if token not in paths:
            paths.append(token)
    return paths


def _active_skill_paths(skill_registry: str) -> list[str]:
    paths: list[str] = []
    in_active_stack = False
    for line in skill_registry.splitlines():
        if line.startswith("## 2. Active stack"):
            in_active_stack = True
            continue
        if in_active_stack and line.startswith("## "):
            break
        if not in_active_stack or not line.startswith("|"):
            continue
        for token in re.findall(r"`([^`]+)`", line):
            if token.startswith(".agents/skills/") and token.endswith("/SKILL.md"):
                paths.append(token)
    return list(dict.fromkeys(paths))


def _registered_addendum_paths(registry: str) -> list[str]:
    paths: list[str] = []
    in_active_registry = False
    for line in registry.splitlines():
        if line.startswith("## Active registry"):
            in_active_registry = True
            continue
        if in_active_registry and line.startswith("## "):
            break
        if not in_active_registry or not line.startswith("|"):
            continue
        for token in re.findall(r"`([^`]+)`", line):
            if token.startswith("00_ARCHIVE_CONTROL/") and token.endswith(".md"):
                paths.append(token)
    return list(dict.fromkeys(paths))


def run_canary(root: Path, scope: str = "core") -> dict:
    root = root.resolve()
    checks: list[Check] = []

    for index, rel_path in enumerate(REQUIRED_CORE_PATHS, start=1):
        checks.append(_existing_path_check(root, rel_path, f"CORE_{index:02d}"))

    core_missing = any(check.status == "FAIL" for check in checks)
    if not core_missing:
        agents_text = _read(root, "AGENTS.md")
        required_phrases = [
            "Mandatory branch assertion before every write",
            "WRITE_BRANCH_UNVERIFIED",
            "Never omit the branch argument",
            "No portfolio action may be produced from DATA PING alone",
        ]
        for index, phrase in enumerate(required_phrases, start=1):
            status = "PASS" if phrase in agents_text else "FAIL"
            checks.append(
                Check(
                    f"AGENTS_RULE_{index:02d}",
                    status,
                    f"Required operating rule {'found' if status == 'PASS' else 'missing'}: {phrase}",
                    "AGENTS.md",
                )
            )

        skill_registry = _read(root, "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md")
        skill_paths = _active_skill_paths(skill_registry)
        if skill_paths:
            checks.append(
                Check(
                    "SKILL_DISCOVERY",
                    "PASS",
                    f"Discovered {len(skill_paths)} active skill path(s)",
                    "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md",
                )
            )
            for index, rel_path in enumerate(skill_paths, start=1):
                checks.append(
                    _existing_path_check(root, rel_path, f"SKILL_PATH_{index:02d}")
                )
        else:
            checks.append(
                Check(
                    "SKILL_DISCOVERY",
                    "FAIL",
                    "No active skill paths were discovered in the Active stack table",
                    "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md",
                )
            )

        addendum_registry = _read(
            root, "00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md"
        )
        addendum_paths = _registered_addendum_paths(addendum_registry)
        if addendum_paths:
            checks.append(
                Check(
                    "ADDENDUM_DISCOVERY",
                    "PASS",
                    f"Discovered {len(addendum_paths)} registered addendum path(s)",
                    "00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md",
                )
            )
            for index, rel_path in enumerate(addendum_paths, start=1):
                checks.append(
                    _existing_path_check(root, rel_path, f"ADDENDUM_PATH_{index:02d}")
                )
        else:
            checks.append(
                Check(
                    "ADDENDUM_DISCOVERY",
                    "FAIL",
                    "No addendum paths were discovered in the Active registry table",
                    "00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md",
                )
            )

        if scope == "full":
            canonical_index = _read(root, "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md")
            owner_paths = _extract_path_tokens(canonical_index)
            checks.append(
                Check(
                    "CANONICAL_OWNER_DISCOVERY",
                    "PASS" if owner_paths else "FAIL",
                    f"Discovered {len(owner_paths)} explicit canonical owner path(s)",
                    "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md",
                )
            )
            for index, rel_path in enumerate(owner_paths, start=1):
                checks.append(
                    _existing_path_check(root, rel_path, f"CANONICAL_PATH_{index:03d}")
                )

    failed = [check for check in checks if check.status == "FAIL"]
    passed = [check for check in checks if check.status == "PASS"]
    result = "PASS" if not failed else "FAIL"
    now = datetime.now(timezone.utc)
    return {
        "schema_version": "1.0",
        "run_id": f"FRAMEWORK_CANARY_{now.strftime('%Y%m%dT%H%M%SZ')}",
        "run_timestamp_utc": now.isoformat(),
        "repo_root": str(root),
        "scope": scope,
        "result": result,
        "check_count": len(checks),
        "pass_count": len(passed),
        "fail_count": len(failed),
        "checks": [asdict(check) for check in checks],
    }


def _write_fixture(root: Path) -> None:
    for rel_path in REQUIRED_CORE_PATHS:
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture\n", encoding="utf-8")

    (root / "AGENTS.md").write_text(
        "\n".join(
            [
                "# Fixture",
                "Mandatory branch assertion before every write",
                "WRITE_BRANCH_UNVERIFIED",
                "Never omit the branch argument",
                "No portfolio action may be produced from DATA PING alone",
            ]
        ),
        encoding="utf-8",
    )

    skill_path = ".agents/skills/example/SKILL.md"
    (root / skill_path).parent.mkdir(parents=True, exist_ok=True)
    (root / skill_path).write_text("# skill\n", encoding="utf-8")
    (root / "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md").write_text(
        "\n".join(
            [
                "# Registry",
                "## 2. Active stack",
                "| Skill | Path |",
                "|---|---|",
                f"| example | `{skill_path}` |",
                "## 3. Next",
            ]
        ),
        encoding="utf-8",
    )

    addendum_path = "00_ARCHIVE_CONTROL/2026-07-12__fixture-index-addendum.md"
    (root / addendum_path).write_text("# addendum\n", encoding="utf-8")
    (root / "00_ARCHIVE_CONTROL/INDEX_ADDENDUM_REGISTRY.md").write_text(
        "\n".join(
            [
                "# Registry",
                "## Active registry",
                "| Addendum | Status |",
                "|---|---|",
                f"| `{addendum_path}` | REGISTRY_DISCOVERABLE |",
                "## Registration contract",
            ]
        ),
        encoding="utf-8",
    )

    canonical_target = "01_CORE_FRAMEWORK/governance/fixture-owner.md"
    (root / canonical_target).parent.mkdir(parents=True, exist_ok=True)
    (root / canonical_target).write_text("# owner\n", encoding="utf-8")
    (root / "00_ARCHIVE_CONTROL/CANONICAL_INDEX.md").write_text(
        f"# Index\n`{canonical_target}`\n", encoding="utf-8"
    )


def run_self_test() -> dict:
    with tempfile.TemporaryDirectory(prefix="framework-canary-self-test-") as temp:
        root = Path(temp)
        _write_fixture(root)

        passing = run_canary(root, scope="full")
        if passing["result"] != "PASS":
            return {
                "result": "FAIL",
                "stage": "expected_pass_fixture",
                "details": passing,
            }

        broken_skill = root / ".agents/skills/example/SKILL.md"
        broken_skill.unlink()
        failing = run_canary(root, scope="core")
        detected = any(
            item["status"] == "FAIL" and item.get("path") == ".agents/skills/example/SKILL.md"
            for item in failing["checks"]
        )
        if failing["result"] != "FAIL" or not detected:
            return {
                "result": "FAIL",
                "stage": "expected_broken_pointer_detection",
                "details": failing,
            }

        return {
            "result": "PASS",
            "pass_fixture_result": passing["result"],
            "broken_fixture_result": failing["result"],
            "broken_pointer_detected": detected,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root. Defaults to current working directory.",
    )
    parser.add_argument(
        "--scope",
        choices=("core", "full"),
        default="core",
        help="core checks fixed governance, active skills and addenda; full also checks explicit canonical-index paths.",
    )
    parser.add_argument(
        "--json-out",
        help="Optional output path. The file may be outside the repository or an approved receipt path.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run deterministic pass/fail fixture tests.",
    )
    args = parser.parse_args()

    report = run_self_test() if args.self_test else run_canary(Path(args.repo_root), args.scope)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    print(rendered)

    if args.json_out:
        Path(args.json_out).write_text(rendered + "\n", encoding="utf-8")

    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
