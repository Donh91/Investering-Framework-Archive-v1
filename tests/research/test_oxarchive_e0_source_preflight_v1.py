"""Synthetic adversarial tests: 0xArchive E0 source/PIT metadata preflight.

All hashes and identifiers below are dummy fixtures. NO actual provider data,
vendor authentication, first-known proof or claims of profitable results.
"""
from __future__ import annotations

import copy
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts.research.oxarchive_e0_source_preflight_v1 import inspect, main


def fixture():
    return {
        "contract": "OXARCHIVE_E0_SOURCE_RECEIPT_V1",
        "study_id": "OXA-E0-SYNTHETIC-001",
        "purpose": "SHADOW_SOURCE_FEASIBILITY",
        "data_placement": "PRIVATE_REFERENCED_ONLY",
        "rights_state": "INTERNAL_RESEARCH_RIGHTS_REVIEWED",
        "decision_cutoff_utc": "2026-11-01T12:00:00Z",
        "receipts": [{
            "receipt_id": "synthetic-1",
            "provider": "0xarchive",
            "family": "hyperliquid_core",
            "market_id": "BTC",
            "datatype": "trades",
            "source_id": "synthetic-metadata-source",
            "api_version": "2026-10-01",
            "provider_request_id": "synthetic-id",
            "schema_sha256": "a" * 64,
            "window_start_utc": "2026-11-01T10:00:00Z",
            "window_end_utc": "2026-11-01T11:00:00Z",
            "event_max_utc": "2026-11-01T10:59:00Z",
            "source_first_known_utc": "2026-11-01T10:59:15Z",
            "availability_evidence": "IMMUTABLE_PRIOR_PUBLICATION_RECEIPT",
            "provider_available_at_utc": "2026-11-01T10:59:20Z",
            "retrieved_at_utc": "2026-11-02T13:00:00Z",
            "quality_state": "COMPLETE_WINDOW",
            "gap_count": 0,
            "row_count": 100,
            "finality": "FINALIZED",
            "binding": {
                "repository": "Donh91/secrets",
                "private_commit_sha": "b" * 40,
                "path": "data/synthetic/2026-11-01.json",
                "sha256": "c" * 64,
                "bytes": 8192,
            },
        }],
    }


class E0Preflight(unittest.TestCase):
    def test_clean_metadata_never_proves_real_world(self):
        out = inspect(fixture())
        self.assertEqual(out["status"], "SCHEMA_ONLY_PASS")
        self.assertEqual(out["errors"], [])
        for key in ("external_source_authenticated", "raw_dataset_bytes_verified",
                    "first_known_proof_independently_verified", "trading_edge_proven",
                    "production_admitted", "publication_authorized"):
            self.assertFalse(out[key])

    def check_bad(self, changes, code, *, in_receipt=True):
        d = fixture()
        dest = d["receipts"][0] if in_receipt else d
        dest.update(changes)
        out = inspect(d)
        self.assertEqual(out["status"], "HOLD", out)
        self.assertIn(code, out["errors"])
        self.assertFalse(out["production_admitted"])

    def test_no_raw_in_public_metadata(self):
        self.check_bad({"raw_rows": [{"price": 1.0}]}, "UNKNOWN_RECEIPT_FIELDS")

    def test_no_secrets_in_unrecognized_root(self):
        self.check_bad({"api_key": "do-not-print"}, "UNKNOWN_ROOT_FIELDS", in_receipt=False)
        out = inspect({**fixture(), "api_key": "TEST-SENSITIVE-INPUT"})
        self.assertNotIn("TEST-SENSITIVE-INPUT", str(out))

    def test_no_authority_escalation(self):
        self.check_bad({"purpose": "LIVE_TRADING"}, "PURPOSE_UNAUTHORIZED", in_receipt=False)

    def test_data_rights_pending_is_hold(self):
        self.check_bad({"rights_state": "UNKNOWN"}, "DATA_RIGHTS_UNRESOLVED", in_receipt=False)

    def test_restricted_data_boundary(self):
        self.check_bad({"data_placement": "PUBLIC_GITHUB"}, "PRIVATE_DATA_BOUNDARY_INVALID", in_receipt=False)

    def test_future_event_rejected(self):
        self.check_bad({"event_max_utc": "2026-11-02T11:00:00Z"}, "FUTURE_OR_EMPTY_EVENT_WINDOW")

    def test_cutoff_boundary_strict(self):
        self.check_bad({"window_end_utc": "2026-11-01T12:00:01Z"}, "FUTURE_OR_EMPTY_EVENT_WINDOW")

    def test_first_known_after_cutoff(self):
        self.check_bad({"source_first_known_utc": "2026-11-02T00:00:00Z"}, "SOURCE_FIRST_KNOWN_AFTER_CUTOFF")

    def test_first_known_before_event(self):
        self.check_bad({"source_first_known_utc": "2026-11-01T10:58:59Z"}, "SOURCE_FIRST_KNOWN_AFTER_CUTOFF")

    def test_provider_available_after_cutoff(self):
        self.check_bad({"provider_available_at_utc": "2026-11-03T00:00:00Z"}, "SOURCE_AVAILABLE_AFTER_CUTOFF")

    def test_missing_first_known_proof(self):
        self.check_bad({"availability_evidence": "VENDOR_RETROSPECTIVE"}, "FIRST_KNOWN_PROVENANCE_UNVERIFIED")

    def test_wrong_timestamp_type(self):
        self.check_bad({"retrieved_at_utc": 1793530000000}, "SOURCE_CLOCK_INVALID")

    def test_unpinned_version(self):
        self.check_bad({"api_version": "legacy"}, "API_VERSION_UNPINNED")

    def test_non_utc_offset(self):
        self.check_bad({"source_first_known_utc": "2026-11-01T11:59:15+01:00"}, "SOURCE_CLOCK_INVALID")

    def test_missing_window_coverage(self):
        self.check_bad({"quality_state": "GAP"}, "COVERAGE_NOT_COMPLETE")
        self.check_bad({"gap_count": 2}, "GAPS_OR_INVALID_GAP_COUNT")

    def test_boolean_count_does_not_pass(self):
        self.check_bad({"gap_count": False}, "GAPS_OR_INVALID_GAP_COUNT")
        self.check_bad({"row_count": True}, "ROW_COUNT_INVALID")

    def test_finality_unresolved(self):
        self.check_bad({"finality": "PRELIMINARY"}, "FINALITY_UNRESOLVED")

    def test_empty_rows_do_not_pass(self):
        self.check_bad({"row_count": 0}, "ROW_COUNT_INVALID")

    def test_retrieval_after_cutoff_alone_is_not_proof(self):
        d = fixture()
        d["receipts"][0]["availability_evidence"] = "RETRIEVED_ONLY"
        d["receipts"][0]["retrieved_at_utc"] = "2026-12-01T00:00:00Z"
        self.assertIn("FIRST_KNOWN_PROVENANCE_UNVERIFIED", inspect(d)["errors"])

    def test_family_symbol_required(self):
        self.check_bad({"market_id": ""}, "SOURCE_IDENTITY_INCOMPLETE")
        self.check_bad({"family": "unknown_market"}, "FAMILY_INVALID")
        self.check_bad({"datatype": "news"}, "DATATYPE_INVALID")

    def test_hyperliquid_spot_cannot_have_funding(self):
        self.check_bad({"family": "hyperliquid_spot", "datatype": "funding"}, "FAMILY_DATATYPE_INCOMPATIBLE")

    def test_lighter_l3_only_on_mainnet(self):
        self.check_bad({"family": "lighter_robinhood_chain", "datatype": "l3_orderbook"}, "FAMILY_DATATYPE_INCOMPATIBLE")

    def test_lighter_no_l4_book(self):
        self.check_bad({"family": "lighter_mainnet", "datatype": "l4_orderbook"}, "FAMILY_DATATYPE_INCOMPATIBLE")

    def test_unhashable_family_and_type_do_not_crash(self):
        self.check_bad({"family": []}, "FAMILY_INVALID")
        self.check_bad({"datatype": {}}, "DATATYPE_INVALID")

    def test_duplicate_receipt_ids(self):
        d = fixture()
        d["receipts"].append(copy.deepcopy(d["receipts"][0]))
        self.assertIn("DUPLICATE_RECEIPT_ID", inspect(d)["errors"])

    def test_oversized_receipt_list(self):
        d = fixture()
        d["receipts"] = d["receipts"] * 26
        self.assertIn("RECEIPTS_COUNT_INVALID", inspect(d)["errors"])

    def test_unknown_binding_field(self):
        d = fixture()
        d["receipts"][0]["binding"]["secret"] = "DONT_ECHO"
        out = inspect(d)
        self.assertIn("UNKNOWN_BINDING_FIELDS", out["errors"])
        self.assertNotIn("DONT_ECHO", str(out))

    def test_private_hashes_and_path(self):
        d = fixture()
        d["receipts"][0]["binding"]["sha256"] = ""
        self.assertIn("DATA_DIGEST_INVALID", inspect(d)["errors"])
        d = fixture()
        d["receipts"][0]["binding"]["path"] = "../outside"
        self.assertIn("PRIVATE_PATH_INVALID", inspect(d)["errors"])
        d = fixture()
        d["receipts"][0]["binding"]["repository"] = "Donh91/Investering-Framework-Archive-v1"
        self.assertIn("RESTRICTED_REPOSITORY_REQUIRED", inspect(d)["errors"])

    def test_missing_binding(self):
        self.check_bad({"binding": None}, "PRIVATE_BINDING_MISSING")

    def test_cli_synthetic_pass_and_no_echo(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "meta.json"
            p.write_text(json.dumps(fixture()), encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                code = main([str(p)])
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(out.getvalue())["status"], "SCHEMA_ONLY_PASS")

    def test_cli_symlink_refusal(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "meta.json"
            link = Path(root) / "link.json"
            p.write_text(json.dumps(fixture()), encoding="utf-8")
            link.symlink_to(p)
            out = io.StringIO()
            with redirect_stdout(out):
                code = main([str(link)])
            self.assertEqual(code, 1)
            self.assertIn("MANIFEST_UNREADABLE_OR_UNSAFE", out.getvalue())

    def test_nonobject_document_holds(self):
        self.assertEqual(inspect([])["status"], "HOLD")


if __name__ == "__main__":
    unittest.main()
