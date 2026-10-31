"""Strict public metadata receipts for Compass Research Engine.

This module MUST NOT receive restricted market values. It is a second-line
schema guard, not an authorization to move private data into public Actions.
"""
from __future__ import annotations

import json
import re
from collections.abc import Mapping

CONTRACT = "CRE_PUBLIC_EVIDENCE_RECEIPT_V1"
ALLOWED_FIELDS = frozenset({"contract", "request_alias", "disclosure_state", "evidence_alias", "research_lane"})
DISCLOSURE_STATES = frozenset({"METADATA_ONLY", "NO_PUBLIC_DISCLOSURE"})
RESEARCH_LANES = frozenset({"PUBLIC_ONLY", "PRIVATE_SOURCE_HEALTH"})
ALIAS = re.compile(r"^[0-9a-f]{24}$", re.ASCII)


class PublicReceiptError(ValueError):
    pass


def validate_receipt(document: Mapping[str, object]) -> dict[str, str]:
    """Return a validated, copy-safe record or refuse it entirely.

    Deliberately disallows hashes of individual provider values, timestamps,
    counts, metrics, comments, free text, confidence and pass/fail findings.
    Exact private bindings remain stored and verified privately.
    """
    if not isinstance(document, Mapping):
        raise PublicReceiptError("OBJECT_REQUIRED")
    if set(document) != ALLOWED_FIELDS:
        raise PublicReceiptError("UNEXPECTED_OR_MISSING_FIELD")
    if any(type(value) is not str for value in document.values()):
        raise PublicReceiptError("STRING_FIELDS_ONLY")
    if document["contract"] != CONTRACT:
        raise PublicReceiptError("WRONG_CONTRACT")
    if document["disclosure_state"] not in DISCLOSURE_STATES:
        raise PublicReceiptError("WRONG_DISCLOSURE_STATE")
    if document["research_lane"] not in RESEARCH_LANES:
        raise PublicReceiptError("UNAUTHORIZED_RESEARCH_LANE")
    for key in ("request_alias", "evidence_alias"):
        if not isinstance(document[key], str) or not document[key].startswith(key.split("_")[0] + "_") or not ALIAS.fullmatch(document[key].split("_", 1)[1]):
            raise PublicReceiptError("INVALID_OPAQUE_ALIAS")
    return {key: document[key] for key in sorted(ALLOWED_FIELDS)}


def dumps_receipt(document: Mapping[str, object]) -> str:
    return json.dumps(validate_receipt(document), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
