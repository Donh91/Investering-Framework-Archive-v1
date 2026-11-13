#!/usr/bin/env python3
"""Read-only, bounded discovery hints from the EXISTING skill routing index.

This is not an invoker, permission gate, model router, learning engine, or
independent source of truth. A skill recommendation requires current owner and
skill-file verification before any actual use. No files, tasks, or APIs are changed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
INDEX = Path("00_ARCHIVE_CONTROL/SKILL_ROUTING_INDEX.json")
CONTRACT = "SKILL_DISCOVERY_HINT_v1"
ROUTINE = {
    "thanks", "thank you", "tak", "godnat", "hello", "hej",
    "ok", "okay", "fint", "super", "perfekt", "status", "status?",
}
PILOT_MARKERS = ("CANDIDATE", "SHADOW_ONLY", "EXPERIMENTAL", "NOT_ACTIVATED")


def norm(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold().strip()


def is_routine(task: str) -> bool:
    text = norm(task).strip(" .!?")
    if text in ROUTINE:
        return True
    # A short PR-status lookup should not trigger a multi-skill research workflow.
    return bool(re.fullmatch(r"(?:status|pr status|status pr|status på pr)\s*#?\d+", text))


def phrase_matches(phrase: str, text: str) -> bool:
    candidate = norm(phrase)
    if not candidate or len(candidate) > 100:
        return False
    # Boundaries prevent "M3" matching an unrelated identifier such as "XM30".
    return re.search(r"(?<!\w)" + re.escape(candidate) + r"(?!\w)", text) is not None


def is_pilot(maturity: str) -> bool:
    upper = str(maturity).upper()
    return any(marker in upper for marker in PILOT_MARKERS)


def discover(index: dict[str, Any], task: str, *,
             include_pilot: bool = False, max_results: int = 3) -> dict[str, Any]:
    """Return at most max_results metadata hints. Never open or execute a skill."""
    if not isinstance(task, str) or not 1 <= len(task) <= 1500:
        raise ValueError("task must be a 1..1500 character sanitized description")
    if not 1 <= max_results <= 5:
        raise ValueError("max_results must be 1..5")
    if not isinstance(index, dict) or index.get("status") != "DERIVED_ROUTING_ONLY":
        raise ValueError("index is not the existing derived routing index")
    if index.get("authority") != "NONE_BY_ITSELF":
        raise ValueError("routing index cannot grant its own authority")
    if index.get("canonical_owner") != "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md":
        raise ValueError("unexpected canonical skill owner")
    skills = index.get("skills")
    if not isinstance(skills, list):
        raise ValueError("invalid skills list")
    result: dict[str, Any] = {
        "contract": CONTRACT,
        "status": "SKIPPED_ROUTINE" if is_routine(task) else "NO_MATCH",
        "authority": "ADVISORY_METADATA_ONLY",
        "skill_instruction_loaded": False,
        "auto_invocation_authorized": False,
        "recommendations": [],
    }
    if result["status"] == "SKIPPED_ROUTINE":
        return result

    text = norm(task)
    hints: list[dict[str, Any]] = []
    names: set[str] = set()
    for s in skills:
        if not isinstance(s, dict):
            raise ValueError("invalid skill entry")
        name = s.get("name")
        if not isinstance(name, str) or not name or name in names:
            raise ValueError("missing or duplicate skill name")
        names.add(name)
        if not isinstance(s.get("allow_implicit_invocation"), bool):
            raise ValueError("invalid implicit-invocation metadata")
        pilot = is_pilot(str(s.get("maturity", "")))
        if pilot and not include_pilot:
            continue
        trigger_list = s.get("triggers")
        if not isinstance(trigger_list, list) or not all(isinstance(x, str) for x in trigger_list):
            raise ValueError("invalid trigger list")
        matching = [t for t in trigger_list if phrase_matches(t, text)]
        if not matching:
            continue
        # A more specific matching phrase outranks a generic one-word keyword.
        # This is an inspectable lexical shortlist, NOT semantic authorization.
        score = max(1 + min(4, len(norm(t).split()) - 1) for t in matching)
        exclusions = s.get("do_not_use_for", [])
        if not isinstance(exclusions, list) or not all(isinstance(x, str) for x in exclusions):
            raise ValueError("invalid negative-trigger list")
        if any(phrase_matches(x, text) for x in exclusions):
            continue
        path = s.get("skill_path")
        if not isinstance(path, str) or not path.startswith(".agents/skills/") or not path.endswith("/SKILL.md"):
            raise ValueError("unsafe skill path")
        implicit = bool(s["allow_implicit_invocation"]) and not pilot
        hints.append({
            "name": name,
            "skill_path": path,
            "maturity": s.get("maturity", "UNKNOWN"),
            "matched_triggers": matching[:3],
            "score": score,
            "invocation_status": (
                "PILOT_REVIEW_ONLY" if pilot else
                "IMPLICIT_ALLOWED_BY_METADATA_NOT_EXECUTED" if implicit else
                "EXPLICIT_ADMISSION_REQUIRED"
            ),
        })
    hints.sort(key=lambda h: (-h["score"], h["name"]))
    result["recommendations"] = hints[:max_results]
    result["status"] = "SHORTLIST" if result["recommendations"] else "NO_MATCH"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, help="Sanitized task description, no secrets")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--include-pilot", action="store_true",
                        help="Show pilot ideas, NEVER activate them")
    parser.add_argument("--max-results", type=int, default=3)
    args = parser.parse_args()
    source = args.repo_root / INDEX
    try:
        raw = source.read_bytes()
        index = json.loads(raw)
        result = discover(index, args.task, include_pilot=args.include_pilot,
                          max_results=args.max_results)
        result["index_path"] = str(INDEX)
        result["index_sha256"] = hashlib.sha256(raw).hexdigest()
        result["authority_note"] = (
            "Checkout-local hint only; verify current GitHub authority, the actual "
            "skill at its immutable ref, existing owner, negative triggers and "
            "user/tool permissions. Discovery is NOT invocation or execution."
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"contract": CONTRACT, "status": "BLOCKED",
                          "reason": type(exc).__name__, "auto_invocation_authorized": False}))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
