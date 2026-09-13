#!/usr/bin/env python3
"""Validate repository-local skill routing metadata without external dependencies.

This validator is intentionally narrow. It checks discoverability, metadata alignment,
side-effect safety, registry linkage and context-size pressure. It does not interpret
market rules, canonical truth, scoring logic or portfolio authority.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = ROOT / "00_ARCHIVE_CONTROL" / "SKILL_ROUTING_INDEX.json"
CANONICAL_REGISTRY = ROOT / "00_ARCHIVE_CONTROL" / "SKILL_REGISTRY.md"
WARN_SKILL_BYTES = 10_000
FAIL_SKILL_BYTES = 20_000


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def warn(warnings: list[str], message: str) -> None:
    warnings.append(message)


def parse_implicit_policy(path: Path) -> bool | None:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^\s*allow_implicit_invocation:\s*(true|false)\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not match:
        return None
    return match.group(1).lower() == "true"


def has_frontmatter(skill_text: str) -> bool:
    return skill_text.startswith("---\n") and "\n---\n" in skill_text[4:]


def parse_active_skill_names(registry_text: str) -> set[str]:
    """Return exact skill names from the canonical ``## 2. Active stack`` table."""
    section_match = re.search(
        r"^## 2\. Active stack\s*$([\s\S]*?)(?=^##\s|\Z)",
        registry_text,
        re.MULTILINE,
    )
    if not section_match:
        raise ValueError("canonical registry missing '## 2. Active stack' section")

    names: list[str] = []
    for line in section_match.group(1).splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells:
            continue
        name = cells[0]
        if name == "Skill" or re.fullmatch(r":?-{3,}:?", name):
            continue
        if name:
            names.append(name)

    if not names:
        raise ValueError("canonical active stack contains no skill rows")
    if len(names) != len(set(names)):
        duplicates = sorted({name for name in names if names.count(name) > 1})
        raise ValueError(f"duplicate canonical active skill rows: {', '.join(duplicates)}")
    return set(names)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    if not INDEX_PATH.exists():
        print(f"ERROR: missing {INDEX_PATH.relative_to(ROOT)}")
        return 1
    if not CANONICAL_REGISTRY.exists():
        print(f"ERROR: missing {CANONICAL_REGISTRY.relative_to(ROOT)}")
        return 1

    try:
        index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {INDEX_PATH.relative_to(ROOT)}: {exc}")
        return 1

    if index.get("status") != "DERIVED_ROUTING_ONLY":
        fail(errors, "routing index must declare status DERIVED_ROUTING_ONLY")
    if index.get("authority") != "NONE_BY_ITSELF":
        fail(errors, "routing index must declare authority NONE_BY_ITSELF")
    if index.get("canonical_owner") != "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md":
        fail(errors, "routing index canonical_owner must remain SKILL_REGISTRY.md")

    registry_text = CANONICAL_REGISTRY.read_text(encoding="utf-8")
    try:
        canonical_active_names = parse_active_skill_names(registry_text)
    except ValueError as exc:
        fail(errors, str(exc))
        canonical_active_names = set()

    skills = index.get("skills")
    if not isinstance(skills, list) or not skills:
        fail(errors, "routing index must contain a non-empty skills list")
        skills = []

    seen: set[str] = set()
    required_fields = {
        "name",
        "category",
        "maturity",
        "skill_path",
        "agents_metadata_path",
        "purpose",
        "triggers",
        "do_not_use_for",
        "default_side_effect_level",
        "side_effect_level",
        "requires_credentials",
        "primary_outputs",
        "validation_expectations",
        "allow_implicit_invocation",
        "portability_notes",
    }

    for entry in skills:
        if not isinstance(entry, dict):
            fail(errors, "every skill entry must be an object")
            continue

        missing = sorted(required_fields - entry.keys())
        name = entry.get("name", "<unnamed>")
        if missing:
            fail(errors, f"{name}: missing routing fields: {', '.join(missing)}")

        if not isinstance(name, str) or not name:
            fail(errors, "every skill entry must have a non-empty string name")
            continue
        if name in seen:
            fail(errors, f"duplicate skill name: {name}")
        seen.add(name)

        if canonical_active_names and name not in canonical_active_names:
            fail(errors, f"{name}: absent from canonical active skill stack")

        skill_rel = entry.get("skill_path")
        meta_rel = entry.get("agents_metadata_path")
        if not isinstance(skill_rel, str) or not skill_rel:
            fail(errors, f"{name}: invalid skill_path")
            continue
        if not isinstance(meta_rel, str) or not meta_rel:
            fail(errors, f"{name}: invalid agents_metadata_path")
            continue

        skill_path = ROOT / skill_rel
        meta_path = ROOT / meta_rel
        if not skill_path.exists():
            fail(errors, f"{name}: missing {skill_rel}")
            continue
        if not meta_path.exists():
            fail(errors, f"{name}: missing {meta_rel}")
            continue

        skill_text = skill_path.read_text(encoding="utf-8")
        skill_size = len(skill_text.encode("utf-8"))
        if skill_size > FAIL_SKILL_BYTES:
            fail(errors, f"{name}: SKILL.md is {skill_size} bytes, above fail threshold {FAIL_SKILL_BYTES}")
        elif skill_size > WARN_SKILL_BYTES:
            warn(warnings, f"{name}: SKILL.md is {skill_size} bytes, progressive-disclosure candidate")

        if not has_frontmatter(skill_text):
            warn(warnings, f"{name}: SKILL.md has no YAML frontmatter; normalize only if a bounded refactor preserves semantics")

        routing_policy = entry.get("allow_implicit_invocation")
        if type(routing_policy) is not bool:
            fail(errors, f"{name}: allow_implicit_invocation must be a JSON boolean")
            routing_policy = None

        metadata_policy = parse_implicit_policy(meta_path)
        if metadata_policy is None:
            fail(errors, f"{name}: agents/openai.yaml lacks allow_implicit_invocation")
        elif routing_policy is not None and metadata_policy != routing_policy:
            fail(errors, f"{name}: implicit invocation differs between routing index and openai.yaml")

        side_effect = str(entry.get("side_effect_level", "")).upper()
        if metadata_policy and any(token in side_effect for token in ("WRITE", "QUEUE")):
            fail(errors, f"{name}: write/queue-capable skill must not allow implicit invocation")

        references_dir = skill_path.parent / "references"
        if references_dir.exists():
            nested_dirs = [p for p in references_dir.rglob("*") if p.is_dir() and p.parent != references_dir]
            if nested_dirs:
                fail(errors, f"{name}: references must remain shallow; nested directories found")

    if canonical_active_names:
        missing_from_index = sorted(canonical_active_names - seen)
        unexpected_in_index = sorted(seen - canonical_active_names)
        if missing_from_index:
            fail(errors, f"routing index omits canonical active skills: {', '.join(missing_from_index)}")
        if unexpected_in_index:
            fail(errors, f"routing index contains non-active skills: {', '.join(unexpected_in_index)}")

    print(f"skill_architecture: skills={len(skills)} errors={len(errors)} warnings={len(warnings)}")
    for message in warnings:
        print(f"WARNING: {message}")
    for message in errors:
        print(f"ERROR: {message}")

    if errors:
        return 1
    print("PASS: derived routing metadata is internally consistent and authority-bounded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
