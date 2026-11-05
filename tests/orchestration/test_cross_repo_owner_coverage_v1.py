"""Source- and authority-negative controls for public cross-repo coverage."""
import copy
import unittest

from scripts.orchestration.cross_repo_owner_coverage_v1 import PUBLIC, reconcile


def fixture():
    return {
        "contract": "CROSS_REPO_PUBLIC_SNAPSHOT_v1",
        "coverage": {name: {"status": "COMPLETE", "main_sha": "a" * 40}
                     for name in PUBLIC},
        "rows": [{
            "repo": PUBLIC[0], "number": 1827, "kind": "ISSUE",
            "state": "OPEN", "priority_hint": "P0",
            "owner_ref": PUBLIC[0] + "#1156",
            "owner_decision": "NOT_ASSESSED",
        }],
    }


def row(packet):
    return packet["rows"][0]


class OwnerCoverageShadowTests(unittest.TestCase):
    def check(self, packet, disposition=None):
        report = reconcile(packet)
        self.assertFalse(report["fully_authenticated"])
        self.assertFalse(report["all_framework_P0_covered"])
        self.assertEqual(report["authority"], "READ_ONLY_ADVISORY_NO_SOURCE_AUTHENTICATION")
        self.assertEqual(report["accepted_handoff_verified"], 0)
        self.assertEqual(report["automatic_dispatch_count"], 0)
        self.assertEqual(report["s1_own_closure_count"], 0)
        for item in report["observations"]:
            self.assertFalse(item["authenticated"])
            self.assertFalse(item["automatic_dispatch"])
            self.assertFalse(item["verified_closure"])
        if disposition:
            self.assertEqual(report["observations"][0]["disposition"], disposition)
        return report

    def test_public_scope_supplied_not_native_authentication(self):
        r = self.check(fixture(), "TRACKED_NO_AUTO_DISPATCH")
        self.assertTrue(r["public_scope_complete_claim_only"])

    def test_only_priority_hint_never_merge_or_dispatch(self):
        for p in ("P0", "P1", "P2", "NONE"):
            x = fixture(); row(x)["priority_hint"] = p
            self.check(x, "TRACKED_NO_AUTO_DISPATCH")

    def test_invalid_priority_rejected(self):
        x = fixture(); row(x)["priority_hint"] = "critical"
        with self.assertRaisesRegex(ValueError, "INVALID_PRIORITY_HINT"):
            reconcile(x)

    def test_unknown_p0_owner_stays_candidate(self):
        x = fixture(); row(x).pop("owner_ref")
        self.check(x, "OWNER_UNRESOLVED")

    def test_dont_claim_owner_from_bool_flag(self):
        x = fixture(); row(x)["owner_verified"] = True
        row(x).pop("owner_ref")
        self.check(x, "OWNER_UNRESOLVED")

    def test_incubating_shadow_with_trigger_waits(self):
        x = fixture(); row(x).update(kind="SHADOW", state="INCUBATING",
                                    next_trigger="new forward outcome")
        self.check(x, "WAIT_WITH_TRIGGER")

    def test_no_data_shadow_does_not_force_work(self):
        x = fixture(); row(x).update(kind="SHADOW", state="WAITING_FOR_DATA",
                                    next_trigger="immutable source comes due")
        self.check(x, "WAIT_WITH_TRIGGER")

    def test_wait_without_trigger_is_gap_not_auto_job(self):
        x = fixture(); row(x)["state"] = "WAITING_FOR_MAPPING"
        self.check(x, "WAIT_TRIGGER_UNSPECIFIED")

    def test_quarantined_shadow_stays_quarantined(self):
        x = fixture(); row(x).update(kind="SHADOW", state="QUARANTINED",
                                    next_trigger="source custody attested")
        self.check(x, "WAIT_WITH_TRIGGER")

    def test_matured_inconclusive_not_edge(self):
        x = fixture(); row(x).update(kind="SHADOW", state="MATURED_INCONCLUSIVE",
                                    next_trigger="new independent prospective cohort")
        self.check(x, "WAIT_WITH_TRIGGER")

    def test_closed_pr_needs_actual_readback(self):
        x = fixture(); row(x).update(kind="PR", state="MERGED")
        self.check(x, "TERMINAL_READBACK_REQUIRED")

    def test_deleted_without_proof_still_unverified(self):
        x = fixture(); row(x)["state"] = "CLOSED"
        self.check(x, "TERMINAL_READBACK_REQUIRED")

    def test_accepted_science_missing_receipt(self):
        x = fixture(); row(x).update(kind="RESEARCH", owner_decision="ADMITTED")
        self.check(x, "ADMISSION_RECEIPT_MISSING")

    def test_untrusted_receipt_never_authenticates(self):
        x = fixture(); row(x).update(kind="RESEARCH", owner_decision="ADMITTED",
                                    owner_receipt_ref="owner issue comment 123")
        self.check(x, "RESEARCH_HANDOFF_REVIEW_ONLY")

    def test_shadow_admitted_still_research_only(self):
        x = fixture(); row(x).update(kind="SHADOW", owner_decision="PROSPECTIVE",
                                    owner_receipt_ref="receipt 101")
        self.check(x, "FORWARD_TEST_REVIEW_ONLY")

    def test_p0_open_source_not_force_s1_dispatch(self):
        x = fixture(); row(x).update(kind="PR", owner_decision="ADMITTED",
                                    owner_receipt_ref="issue 1156")
        self.check(x, "OWNER_EXECUTION_REVIEW_ONLY")

    def test_public_research_not_force_s1(self):
        x = fixture(); row(x)["kind"] = "RESEARCH"
        self.check(x, "RESEARCH_REVIEW_NOT_DISPATCHED")

    def test_private_row_rejected_without_leaking(self):
        x = fixture(); row(x)["repo"] = "Donh91/Meme-Alpha-Lab"
        row(x)["title"] = "confidential finding"
        with self.assertRaisesRegex(ValueError, "RESTRICTED_OR_INVALID"):
            reconcile(x)

    def test_secret_row_not_allowed(self):
        x = fixture(); row(x)["repo"] = "Donh91/secrets"
        with self.assertRaises(ValueError):
            reconcile(x)

    def test_public_payload_fields_rejected(self):
        for key in ("body", "private", "title", "payload"):
            x = fixture(); row(x)[key] = "secret"
            with self.assertRaisesRegex(ValueError, "SOURCE_PAYLOAD"):
                reconcile(x)

    def test_missing_public_repo_coverage_fails_closed(self):
        x = fixture(); x["coverage"].pop(PUBLIC[2])
        with self.assertRaisesRegex(ValueError, "EXACTLY_THREE"):
            reconcile(x)

    def test_incomplete_and_unknown_coverage_not_100_percent(self):
        x = fixture(); x["coverage"][PUBLIC[2]] = {"status": "NOT_CHECKED"}
        self.assertFalse(self.check(x)["public_scope_complete_claim_only"])

    def test_partial_coverage_can_report_supplied_issue(self):
        x = fixture(); x["coverage"][PUBLIC[0]]["status"] = "PARTIAL"
        self.assertFalse(self.check(x)["public_scope_complete_claim_only"])

    def test_rows_from_unavailable_repo_rejected(self):
        x = fixture(); x["coverage"][PUBLIC[0]] = {"status": "UNAVAILABLE"}
        with self.assertRaisesRegex(ValueError, "ROW_FROM_UNCHECKED"):
            reconcile(x)

    def test_main_sha_mandatory_for_claimed_read(self):
        x = fixture(); x["coverage"][PUBLIC[0]]["main_sha"] = "bad"
        with self.assertRaisesRegex(ValueError, "MISSING_SOURCE_MAIN_SHA"):
            reconcile(x)

    def test_stable_fingerprint_no_passive_wake(self):
        x = fixture()
        a = self.check(x)["observations"][0]["fingerprint"]
        row(x)["checked_at"] = "2026-11-05T11:10:00Z"
        self.assertEqual(a, self.check(x)["observations"][0]["fingerprint"])

    def test_material_source_owner_or_trigger_changes_fingerprint(self):
        x = fixture(); baseline = self.check(x)["observations"][0]["fingerprint"]
        for key, value in (("owner_ref", PUBLIC[0] + "#1157"),
                           ("next_trigger", "new native run"), ("state", "BLOCKED"),
                           ("priority_hint", "P1"), ("source_head_sha", "b"*40)):
            y = copy.deepcopy(x); row(y)[key] = value
            self.assertNotEqual(baseline, self.check(y)["observations"][0]["fingerprint"])

    def test_duplicate_p0_does_not_add_two_cases(self):
        x = fixture(); x["rows"].append(copy.deepcopy(row(x)))
        result = self.check(x)
        self.assertEqual(result["distinct_originals"], 1)
        self.assertEqual(result["duplicate_input_count"], 1)
        self.assertEqual(result["p0_title_or_label_candidates"], 1)

    def test_nonfinite_source_rejected(self):
        x = fixture(); row(x)["owner_receipt_ref"] = float("nan")
        with self.assertRaisesRegex(ValueError, "NON_JSON_OR_NONFINITE"):
            reconcile(x)

    def test_bounded_census_rejects_501(self):
        x = fixture(); x["rows"] = [row(x)] * 501
        with self.assertRaisesRegex(ValueError, "UNBOUNDED"):
            reconcile(x)

    def test_wrong_contract_no_promotions(self):
        x = fixture(); x["contract"] = "P0_AUTONOMOUS_EXECUTION"
        with self.assertRaisesRegex(ValueError, "WRONG_PUBLIC"):
            reconcile(x)

    def test_source_sha_malformed(self):
        x = fixture(); row(x)["source_head_sha"] = "wrong"
        self.check(x, "INVALID_SOURCE_SHA")

    def test_private_coverage_explicit_unknown(self):
        x = fixture()
        self.assertEqual(self.check(x)["private_domain_coverage"],
                         "NOT_ASSESSED_PUBLIC_BOUNDARY")


if __name__ == "__main__":
    unittest.main()
