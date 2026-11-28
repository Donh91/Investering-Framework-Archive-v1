"""Untrusted candidate-test XML as a BOUNDED prefilter, never CI attestation.

Only PR-native GitHub Actions on the output PR may attest actual tests.
No model stdout, model commands, credentials, GitHub write or paid API here.
"""
from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from typing import Any

MAX_JUNIT_BYTES = 3_000_000
MAX_TESTCASES = 25_000
MAX_ID_CHARS = 500

class PreflightHold(ValueError):
    """Evidence missing, malformed or not safe to interpret."""

def _require(test: bool, reason: str):
    if not test:
        raise PreflightHold(reason)

def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _census(raw: bytes) -> dict:
    _require(isinstance(raw, bytes) and 0 < len(raw) <= MAX_JUNIT_BYTES,
             "JUNIT_INPUT_BOUNDS")
    _require(b"<!DOCTYPE" not in raw.upper() and b"<!ENTITY" not in raw.upper(),
             "JUNIT_DTD_DENIED")
    try:
        root = ET.fromstring(raw)
    except (ET.ParseError, UnicodeError, ValueError) as error:
        raise PreflightHold("JUNIT_MALFORMED") from error
    _require(root.tag in {"testsuite", "testsuites"}, "JUNIT_ROOT")
    cases = root.findall(".//testcase")
    _require(0 < len(cases) <= MAX_TESTCASES, "JUNIT_TEST_COUNT")
    all_ids, unsuccessful, skipped = set(), set(), set()
    for case in cases:
        name, cls = case.attrib.get("name"), case.attrib.get("classname")
        _require(isinstance(name, str) and bool(name) and len(name) <= MAX_ID_CHARS
                 and isinstance(cls, str) and len(cls) <= MAX_ID_CHARS,
                 "JUNIT_INVALID_NODE_ID")
        key = cls + "::" + name
        _require(key not in all_ids, "JUNIT_DUPLICATE_NODE_ID")
        all_ids.add(key)
        if case.find("failure") is not None or case.find("error") is not None:
            unsuccessful.add(key)
        if case.find("skipped") is not None:
            skipped.add(key)
    return {"ids": all_ids, "failed": unsuccessful, "skipped": skipped,
            "sha256": _sha(raw), "count": len(all_ids)}

def preflight(pristine_junit: bytes, candidate_junit: bytes, *, baseline_exit: int,
              candidate_exit: int, docker_network: str, exact_main: bool) -> dict:
    """Compare two XML receipts outside the container.

    Both XML documents can be forged by candidate code. This is a pre-filter
    only, NEVER independent completion proof, merge or spending authority.
    """
    base = _census(pristine_junit)
    candidate = _census(candidate_junit)
    _require(type(baseline_exit) is int and type(candidate_exit) is int,
             "JUNIT_EXIT_NOT_INTEGER")
    _require(docker_network == "none" and exact_main is True, "SECURITY_BOUNDS")
    _require(baseline_exit == 0 and not base["failed"] and not base["skipped"],
             "BASELINE_NOT_PRISTINE_PASS")
    missed = base["ids"] - candidate["ids"]
    bad_base_nodes = candidate["failed"].intersection(base["ids"])
    skipped_base_nodes = candidate["skipped"].intersection(base["ids"])
    status = ("PREFLIGHT_FAIL" if missed or bad_base_nodes or skipped_base_nodes
              or candidate_exit != 0 or candidate["failed"] or candidate["skipped"]
              else "PREFLIGHT_PASS")
    ids_sorted = sorted(base["ids"])
    return {
        "contract": "ASTRA_BUILD_PREFLIGHT_v1",
        "status": status,
        "baseline_id_set_sha256": _sha("\n".join(ids_sorted).encode("utf-8")),
        "baseline_count": base["count"],
        "candidate_count": candidate["count"],
        "baseline_junit_sha256": base["sha256"],
        "candidate_junit_sha256": candidate["sha256"],
        "missing_baseline_nodes": len(missed),
        "failed_baseline_nodes": len(bad_base_nodes),
        "skipped_baseline_nodes": len(skipped_base_nodes),
        "candidate_exit": candidate_exit,
        "network": "none",
        "candidate_test_completion_attested": False,
        "independent_test_authority": "EXACT_HEAD_NATIVE_GITHUB_CI_ON_OUTPUT_PR",
        "paid_or_merge_authority": False,
    }

def safe_preflight(*args: Any, **kwargs: Any) -> dict:
    try:
        return preflight(*args, **kwargs)
    except PreflightHold as exc:
        return {"contract": "ASTRA_BUILD_PREFLIGHT_v1", "status": "PREFLIGHT_HOLD",
                "reason": str(exc), "candidate_test_completion_attested": False,
                "paid_or_merge_authority": False}
