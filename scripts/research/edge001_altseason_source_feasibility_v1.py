#!/usr/bin/env python3
"""Altseason M1-M3 P0-B: value-free source feasibility adjudication.

This structural preflight does NOT open providers, fetch live data, verify
original publication, certify historical PIT, score signals, infer executable
capacity or authorize trades. The registry contains public-safe source
pointers and proof gaps only. It must never carry private provider values.
Original source owner/PIT #1596 and EDGE-001 #1530 retain admission authority.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from datetime import date
from re import fullmatch

CONTRACT = "EDGE001_ALTSEASON_SOURCE_FEASIBILITY_v1"
STATUSES = frozenset({"AVAILABLE_VERIFIED", "AVAILABLE_NOT_PIT", "MISSING", "UNSAFE"})
ACCESS = frozenset({"PUBLIC_METADATA", "PRIVATE_METADATA_ONLY", "RESTRICTED_ANALYSIS_OFF"})
ROLES = frozenset({"SOURCE_REFERENCE", "SOURCE_CODE", "HISTORICAL_RESEARCH", "GAP_RECEIPT", "RESTRICTED_GATE"})
PROOF_KEYS = frozenset({
    "provider_first_publication", "original_investor_delivery",
    "vintage_token_universe", "executable_bid_ask_and_capacity",
    "full_position_sellability",
})
REASONS = frozenset({
    "PROVIDER_FIRST_PUBLICATION", "ORIGINAL_DELIVERY", "VINTAGE_UNIVERSE",
    "EXECUTABLE_DEPTH", "FULL_SELL_EXIT", "INDEPENDENT_EVENT_N",
    "LICENSED_ACCESS", "DATA_COLLECTION", "SOURCE_MEANING",
    "ANALYSIS_FIREWALL", "PROVIDER_SELF_ATTESTATION",
    "HISTORICAL_BACKFILL", "FILL_CONFIRMATION",
})
REQUIRED = frozenset({
    "id", "topic", "owner_issue", "status", "access_class",
    "source_role", "source_repo", "source_path", "source_blob_sha",
    "source_is_documentary", "capability_proof", "binding_receipts",
    "blocking_reasons", "next_reactivation_trigger", "private_values_in_public",
})


def _fail(reason: str) -> None:
    # Never echo arbitrary values/IDs/paths from potentially private input.
    raise ValueError("ALTSEASON_FEASIBILITY_" + reason)


def _safe_locator(row: Mapping) -> None:
    repo = row["source_repo"]
    path = row["source_path"]
    if (repo not in (
        "Donh91/Investering-Framework-Archive-v1", "Donh91/Meme-Alpha-Lab"
    ) or not isinstance(path, str) or not path or path.startswith("/")
        or "\\" in path or any(p in ("", ".", "..") for p in path.split("/"))
        or any(p.lower() in ("secrets", ".env") for p in path.split("/"))):
        _fail("SOURCE_LOCATOR_UNSAFE")
    if not isinstance(row["source_blob_sha"], str) or not fullmatch(
        r"[0-9a-f]{40}", row["source_blob_sha"]
    ):
        _fail("SOURCE_BLOB_SHA40_REQUIRED")
    if repo == "Donh91/Meme-Alpha-Lab" and row["access_class"] != "PRIVATE_METADATA_ONLY":
        _fail("PRIVATE_REPO_MUST_REMAIN_METADATA_ONLY")
    if row["access_class"] == "PRIVATE_METADATA_ONLY" and repo != "Donh91/Meme-Alpha-Lab":
        _fail("UNEXPECTED_PRIVATE_SOURCE_REPO")


def validate_source_feasibility_registry(registry: Mapping) -> dict:
    """Validate public-safe typed source gaps; return status counts only.

    A true capability Boolean here is STILL NOT authenticated proof: the
    external owner must separately bind raw source receipts and make the
    scientific admission decision. This method NEVER returns ADMITTED.
    """
    if not isinstance(registry, Mapping) or set(registry) != {
        "contract", "snapshot_date", "classification", "public_values_copied",
        "original_owner", "rows", "explicit_authority",
    }:
        _fail("TOP_LEVEL_CONTRACT")
    if registry["contract"] != CONTRACT or registry["classification"] != "PUBLIC_SAFE_METADATA_ONLY":
        _fail("DECLARED_SCOPE")
    if registry["public_values_copied"] is not False:
        _fail("PRIVATE_VALUE_EXPORT_FORBIDDEN")
    if registry["original_owner"] != "Donh91/Investering-Framework-Archive-v1#1596":
        _fail("SOURCE_OWNER_MISMATCH")
    try:
        if not isinstance(registry["snapshot_date"], str):
            _fail("SNAPSHOT_DATE")
        date.fromisoformat(registry["snapshot_date"])
    except ValueError:
        _fail("SNAPSHOT_DATE")
    authority = registry["explicit_authority"]
    if not isinstance(authority, Mapping) or set(authority) != {
        "historical_pit_admitted", "market_prediction_authority",
        "live_buy_sell_authority", "portfolio_economic_edge_claim",
        "round3_analysis_authorized",
    } or any(value is not False for value in authority.values()):
        _fail("AUTHORITY_MUST_REMAIN_FALSE")
    rows = registry["rows"]
    if not isinstance(rows, list) or not rows:
        _fail("NONEMPTY_SOURCE_ROWS_REQUIRED")
    seen = set()
    counts = Counter()
    blocked = set()
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != REQUIRED:
            _fail("SOURCE_FIELD_SET")
        item = row["id"]
        if (not isinstance(item, str) or not fullmatch(r"[A-Z0-9_]{4,70}", item)
                or item in seen):
            _fail("DUPLICATE_OR_INVALID_SOURCE_ID")
        seen.add(item)
        for key in ("topic", "owner_issue", "next_reactivation_trigger"):
            if not isinstance(row[key], str) or not row[key].strip():
                _fail("EMPTY_OWNER_TOPIC_OR_TRIGGER")
        if not fullmatch(r"Donh91/[A-Za-z0-9_.-]+#\d+", row["owner_issue"]):
            _fail("SOURCE_OWNER_ISSUE_FORMAT")
        if (not isinstance(row["status"], str) or not isinstance(row["access_class"], str)
                or not isinstance(row["source_role"], str) or row["status"] not in STATUSES
                or row["access_class"] not in ACCESS or row["source_role"] not in ROLES):
            _fail("UNRECOGNIZED_STATE")
        if type(row["source_is_documentary"]) is not bool or row["private_values_in_public"] is not False:
            _fail("SOURCE_PRIVATE_OR_DOC_FLAG")
        _safe_locator(row)
        proof = row["capability_proof"]
        if (not isinstance(proof, Mapping) or set(proof) != PROOF_KEYS
                or any(type(v) is not bool for v in proof.values())):
            _fail("PROOF_FIELDS_REQUIRED")
        receipts = row["binding_receipts"]
        if (not isinstance(receipts, Mapping) or set(receipts) != PROOF_KEYS
                or any(v is not None and
                       (not isinstance(v, str) or not fullmatch(r"[0-9a-f]{64}", v))
                       for v in receipts.values())):
            _fail("BOUND_RECEIPT_SHA256_REQUIRED")
        # Self asserted proof must never gain a decision without an exact immutable
        # separate evidence binding. Even all five bindings do NOT authenticate them.
        if any(proof[k] and receipts[k] is None for k in PROOF_KEYS):
            _fail("CLAIMED_PROOF_WITHOUT_RECEIPT")
        reasons = row["blocking_reasons"]
        if (not isinstance(reasons, list) or not reasons
                or any(not isinstance(v, str) or v not in REASONS for v in reasons)
                or len(reasons) != len(set(reasons))):
            _fail("BLOCKING_REASON_CLASS")
        if row["status"] == "AVAILABLE_VERIFIED":
            if not all(proof.values()) or any(receipts[k] is None for k in PROOF_KEYS):
                _fail("AVAILABLE_VERIFIED_LAUNDERED")
            if row["source_is_documentary"] or row["access_class"] != "PUBLIC_METADATA":
                _fail("DOCUMENTARY_OR_PRIVATE_NOT_VERIFIED")
        if row["status"] == "AVAILABLE_NOT_PIT" and not row["source_is_documentary"] and row["source_role"] == "GAP_RECEIPT":
            _fail("GAP_RECEIPT_CANNOT_BE_AVAILABLE")
        if row["status"] == "UNSAFE":
            if row["access_class"] != "RESTRICTED_ANALYSIS_OFF" or "ANALYSIS_FIREWALL" not in reasons:
                _fail("UNSAFE_FIREWALL_REQUIRED")
        elif row["access_class"] == "RESTRICTED_ANALYSIS_OFF":
            _fail("RESTRICTED_MUST_BE_UNSAFE")
        # A negative source feasibility snapshot cannot authorize action.
        counts[row["status"]] += 1
        if row["status"] != "AVAILABLE_VERIFIED":
            blocked.add(item)
    return {
        "contract": CONTRACT,
        "snapshot_date": registry["snapshot_date"],
        "rows_n": len(rows),
        "counts": {key: counts[key] for key in sorted(STATUSES)},
        "blocked_source_ids": sorted(blocked),
        "source_feasibility_only": True,
        "exact_source_bytes_independently_verified": False,
        "historical_pit_admitted": False,
        "historical_portfolio_tournament_authorized": False,
        "research_claim_of_edge_allowed": False,
        "live_portfolio_action_authorized": False,
        "private_values_echoed": False,
    }
