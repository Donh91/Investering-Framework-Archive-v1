"""Adversarial pure-unit tests: a matching narrative is never model skill."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.research.w46_independent_research_comparator_v1 import (
    CLAIMS, compare, read_sealed_report,
)

SOURCE = "a4504580273bc4396f20395ac9cd272656dc4454"


def payload(reviewer="GROK", claim_id="WARNING_LEAD_TIME",
            verdict="INSUFFICIENT_EVIDENCE", clock="PARTIAL_PIT"):
    return {
        "contract": "W46_REVIEW_RESULT_V1",
        "reviewer": reviewer, "status": "SUBMITTED",
        "native_run_id": reviewer + "-native-123",
        "source_snapshot_sha": SOURCE,
        "claims": [
            {"claim_id": claim_id, "verdict": verdict,
             "first_known_status": clock,
             "evidence_refs": [
                 "Archive #1596 original PIT publication receipt"]}
        ],
    }


class SealedReports(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "report.json"

    def seal(self, data):
        raw = (json.dumps(data, sort_keys=True) + "\n").encode()
        self.path.write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def load(self, data, reviewer="GROK", override_digest=None):
        digest = self.seal(data)
        return read_sealed_report(
            self.path, expected_sha256=override_digest or digest,
            reviewer=reviewer, source_snapshot_sha=SOURCE)

    def test_positive_sealed_bytes_and_identity(self):
        data, digest = self.load(payload())
        self.assertEqual(data["reviewer"], "GROK")
        self.assertEqual(len(digest), 64)

    def test_mutated_report_digest_refused(self):
        with self.assertRaisesRegex(ValueError, "REPORT_DIGEST_MISMATCH"):
            self.load(payload(), override_digest="0" * 64)

    def test_wrong_source_timestamp_fingerprint_refused(self):
        data = payload()
        data["source_snapshot_sha"] = "f" * 40
        with self.assertRaisesRegex(ValueError, "SOURCE_SNAPSHOT_MISMATCH"):
            self.load(data)

    def test_missing_real_run_refused(self):
        data = payload()
        data["native_run_id"] = ""
        with self.assertRaisesRegex(ValueError, "MISSING_NATIVE_RUN_RECEIPT"):
            self.load(data)

    def test_duplicate_claim_id_refused(self):
        data = payload()
        data["claims"].append(data["claims"][0].copy())
        with self.assertRaisesRegex(ValueError, "UNKNOWN_OR_DUPLICATE_CLAIM"):
            self.load(data)

    def test_wrong_reviewer_and_unsealed_refused(self):
        with self.assertRaisesRegex(ValueError, "REPORT_REVIEWER_MISMATCH"):
            self.load(payload("SOL61_MAX"))
        data = payload()
        data["status"] = "PLANNED"
        with self.assertRaisesRegex(ValueError, "REPORT_NOT_SEALED"):
            self.load(data)

    def test_no_evidence_ref_refused(self):
        data = payload()
        data["claims"][0]["evidence_refs"] = []
        with self.assertRaisesRegex(ValueError, "MISSING_OR_INSUFFICIENT"):
            self.load(data)

    def test_comparator_requires_two_distinct_reviewers(self):
        with self.assertRaisesRegex(ValueError, "BOTH_GROK_AND_SOL_REQUIRED"):
            compare({"GROK": payload()}, source_snapshot_sha=SOURCE,
                    source_digests={"GROK": "x"})

    def test_agreement_is_advisory_not_edge(self):
        a, b = payload(), payload("SOL61_MAX")
        result = compare({"GROK": a, "SOL61_MAX": b},
                         source_snapshot_sha=SOURCE,
                         source_digests={"GROK": "a" * 64,
                                         "SOL61_MAX": "b" * 64})
        rows = {x["claim_id"]: x for x in result["rows"]}
        self.assertEqual(rows["WARNING_LEAD_TIME"]["comparison_state"],
                         "AGREEMENT_ADVISORY_ONLY")
        self.assertFalse(rows["WARNING_LEAD_TIME"]["causal_or_economic_edge_proven"])
        self.assertFalse(result["scientific_edge_proven"])
        self.assertFalse(result["automatic_promotion"])
        self.assertEqual(len(rows), len(CLAIMS))

    def test_disagreement_stays_unresolved(self):
        a, b = payload(), payload("SOL61_MAX", verdict="SUPPORTED")
        result = compare({"GROK": a, "SOL61_MAX": b},
                         source_snapshot_sha=SOURCE,
                         source_digests={"GROK": "a" * 64,
                                         "SOL61_MAX": "b" * 64})
        row = next(x for x in result["rows"] if x["claim_id"] == "WARNING_LEAD_TIME")
        self.assertEqual(row["comparison_state"],
                         "DISAGREEMENT_REQUIRES_SOURCE_ADJUDICATION")

    def test_unknown_clock_blocks_positive_agreement(self):
        a, b = payload(clock="UNKNOWN"), payload("SOL61_MAX", clock="UNKNOWN")
        r = compare({"GROK": a, "SOL61_MAX": b},
                    source_snapshot_sha=SOURCE,
                    source_digests={"GROK": "a" * 64, "SOL61_MAX": "b" * 64})
        w = next(x for x in r["rows"] if x["claim_id"] == "WARNING_LEAD_TIME")
        self.assertEqual(w["comparison_state"], "SOURCE_BLOCKED")

    def test_optional_fable_does_not_auto_promote(self):
        a = payload()
        b = payload("SOL61_MAX")
        c = payload("FABLE52", verdict="REFUTED")
        r = compare({"GROK": a, "SOL61_MAX": b, "FABLE52": c},
                    source_snapshot_sha=SOURCE,
                    source_digests={"GROK": "a", "SOL61_MAX": "b", "FABLE52": "c"})
        w = next(x for x in r["rows"] if x["claim_id"] == "WARNING_LEAD_TIME")
        self.assertEqual(w["comparison_state"],
                         "DISAGREEMENT_REQUIRES_SOURCE_ADJUDICATION")
        self.assertFalse(r["scientific_edge_proven"])


if __name__ == "__main__":
    unittest.main()
