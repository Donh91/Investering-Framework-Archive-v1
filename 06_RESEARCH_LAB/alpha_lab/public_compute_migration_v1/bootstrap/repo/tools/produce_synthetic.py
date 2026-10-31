"""Issue a SYNTHETIC-ONLY test receipt. No market data, no network, no keys.

The output is local to the runner (/tmp). It is never a chain receipt, original
first-known attestation, canonical Alpha source or trading decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

REPO = "Donh91/investering-public-compute"
TEST_DATA = b"SYNTHETIC_ONLY_NO_CHAIN_DATA_V1"
DEFAULT_SCHEMA = Path(__file__).resolve().parents[1] / "contracts/public_receipt_v1.schema.json"


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def issue_receipt(schema_path: Path = DEFAULT_SCHEMA) -> dict:
    """A self-asserted test object; actual GitHub job metadata is NOT certified."""
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    sha = os.environ.get("GITHUB_SHA", "a" * 40)
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise ValueError("github sha not a lowercase SHA40")
    repo = os.environ.get("GITHUB_REPOSITORY", REPO)
    if repo != REPO:
        raise ValueError("synthetic-only W1 cannot execute for another repo")
    event = os.environ.get("GITHUB_EVENT_NAME", "workflow_dispatch")
    if event != "workflow_dispatch":
        raise ValueError("synthetic issuer allows only direct trusted dispatch")
    run_id = int(os.environ.get("GITHUB_RUN_ID", "1"))
    attempt = int(os.environ.get("GITHUB_RUN_ATTEMPT", "1"))
    return {
        "contract": "ALPHA_PUBLIC_SOURCE_RECEIPT_V1",
        "authority": "RESEARCH_ONLY_NO_PRIVATE_SOURCE_OR_TRADING_AUTHORITY",
        "deployment_stage": "SYNTHETIC_TEST",
        "privacy": {
            "data_class": "EXHAUSTIVE_APPROVED_PUBLIC_SOURCE",
            "universe_policy": "APPROVED_SYNTHETIC_FIXTURE",
            "restricted_payload_present": False,
            "user_selected_watchlist_present": False,
            "private_query_response_present": False,
        },
        "source_class": "SYNTHETIC_FIXTURE",
        "source_id": "SYNTHETIC_FIXTURE_V1",
        "chain_id": 4663,
        "mode": "SYNTHETIC_TEST",
        "status": "SYNTHETIC_COMPLETE",
        "collector": {
            "public_repo": REPO,
            "code_commit_sha40": sha,
            "source_contract_id": "PUBLIC_SYNTHETIC_FACTORY_TEST_V1",
            "schema_sha256": sha256(schema_path.read_bytes()),
        },
        "github": {
            "run_id": run_id,
            "run_attempt": attempt,
            "head_sha40": sha,
            "workflow_ref": "refs/heads/main",
            "event": event,
            "runner_class": "STANDARD_GITHUB_HOSTED_UBUNTU",
            "job_started_at_utc": now,
            "job_completed_at_utc": now,
        },
        "clock": {
            "source_observation_started_at_utc": now,
            "source_observation_completed_at_utc": now,
            "first_observed_at_utc": now,
            "receipt_available_at_utc": now,
            "independent_source_first_known_verified": False,
            "clock_limitations": "SYNTHETIC_NOT_MARKET_PROOF",
        },
        "coverage": {
            "start_block": 1,
            "end_block": 4,
            "safe_head_block": 6,
            "blocks_requested": 4,
            "blocks_completed": 4,
            "missing_ranges_count": 0,
            "contiguous": True,
            "reorg_suspected": False,
            "has_all_original_ranges": True,
        },
        "event_count": 0,
        "source_data_sha256": sha256(TEST_DATA),
        "provenance_claims": {
            "public_source_only": True,
            "original_machine_first_known_certified": False,
            "canonical_alpha_census_recovered": False,
            "private_signal_or_trade_permission": False,
            "safe_for_private_import": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    if out.is_symlink() or out.resolve().is_relative_to(Path.cwd().resolve()):
        raise ValueError("synthetic receipt must be ephemeral outside the Git checkout")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(issue_receipt(), sort_keys=True, indent=2) + "\n")
    print("W1_SYNTHETIC_RECEIPT_CREATED_NOT_PUBLIC_SOURCE")


if __name__ == "__main__":
    main()
