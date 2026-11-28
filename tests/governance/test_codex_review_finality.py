"""Adversarial, offline regression of the in-house Codex review finality gate."""
from __future__ import annotations

import importlib.util
import inspect
import json
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path("scripts/governance/check_codex_review_finality.py")
SPEC = importlib.util.spec_from_file_location("check_codex_review_finality", SOURCE)
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)

HEAD = "a" * 40
BOT = {"login": "chatgpt-codex-connector[bot]", "type": "Bot", "id": 199175422}
HUMAN = {"login": "Donh91"}


def request(at="2026-10-15T23:00:00Z"):
    return {"user": HUMAN, "body": "@codex review", "created_at": at}


def summary(at="2026-10-15T23:01:00Z", head=HEAD, unresolved=False):
    state = {"code_review": {"commit_sha": head, "status": "completed",
                             "has_unresolved_findings": unresolved}}
    return {"user": BOT, "created_at": at, "updated_at": at,
            "body": "<!-- codex-review-state:v1 " + json.dumps(state) + " -->"}


def positive(at="2026-10-15T23:02:00Z", head=HEAD):
    return {"user": BOT, "created_at": at, "updated_at": at,
            "body": "Codex Review: Didn't find any major issues.\n\n"
                    + "**Reviewed commit:** " + chr(96) + head[:10] + chr(96)}


class ReviewFinalityTests(unittest.TestCase):
    def test_exact_head_review_after_latest_request_is_only_technical_acceptance(self):
        result = gate.decision(HEAD, [request(), summary(), positive()], [], [])
        self.assertEqual(result["status"], "FINAL_TECHNICAL_REVIEW")
        self.assertTrue(result["technical_review_accepted"])
        self.assertTrue(result["not_formal_github_approved"])

    def test_lookalike_bot_cannot_forge_positive_or_completed_state(self):
        fake = {"login": "chatgpt-codex-connector-fake", "type": "User", "id": 999}
        rows = [request(), {**summary(), "user": fake}, {**positive(), "user": fake}]
        self.assertEqual(gate.decision(HEAD, rows, [], [])["status"],
                         "REVIEW_IN_PROGRESS_OR_UNVERIFIED")

    def test_same_bot_name_wrong_identity_is_untrusted(self):
        wrong = {"login": "chatgpt-codex-connector[bot]", "type": "Bot", "id": 999}
        rows = [request(), {**summary(), "user": wrong}, {**positive(), "user": wrong}]
        self.assertFalse(gate.decision(HEAD, rows, [], [])["technical_review_accepted"])

    def test_positive_requires_exact_matching_completed_state(self):
        other = "a" * 10 + "b" * 30
        rows = [request(), summary(head=other), positive(head=other)]
        self.assertFalse(gate.decision(HEAD, rows, [], [])["technical_review_accepted"])

    def test_positive_before_exact_state_completion_is_the_native_order(self):
        # Was refused on the false model that Codex completes its state before
        # the receipt. Natively the receipt comes first and the exact full-SHA
        # completion is recorded after it (see NativeLifecycleTests).
        rows = [request(), positive(at="2026-10-15T23:01:00Z"),
                summary(at="2026-10-15T23:02:00Z")]
        self.assertEqual(gate.decision(HEAD, rows, [], [])["status"],
                         "FINAL_TECHNICAL_REVIEW")

    def test_newer_running_state_blocks_prior_positive_on_same_head(self):
        running = summary(at="2026-10-15T23:03:00Z")
        state = {"code_review": {"commit_sha": HEAD, "status": "running",
                                 "has_unresolved_findings": None}}
        running["body"] = "<!-- codex-review-state:v1 " + json.dumps(state) + " -->"
        result = gate.decision(HEAD, [request(), summary(), positive(), running], [], [])
        self.assertEqual(result["status"], "NEWER_CODEX_REVIEW_NOT_COMPLETE")

    def test_same_second_prior_receipts_do_not_clear_newer_request(self):
        # The earlier review belongs to a first request, but all timestamps
        # round to the second of a second, newer request. Temporal tie != later.
        when = "2026-10-15T23:01:00Z"
        rows = [request(when), summary(at=when), positive(at=when), request(when)]
        result = gate.decision(HEAD, rows, [], [])
        self.assertEqual(result["status"], "REVIEW_IN_PROGRESS_OR_UNVERIFIED")
        self.assertFalse(result["technical_review_accepted"])

    def test_same_second_completion_and_request_is_not_order_proof(self):
        when = "2026-10-15T23:01:00Z"
        rows = [summary(at=when), positive(at=when), request(when)]
        self.assertFalse(gate.decision(HEAD, rows, [], [])["technical_review_accepted"])

    def test_same_second_conflicting_codex_states_are_order_independent_blockers(self):
        completed = summary(at="2026-10-15T23:01:00Z")
        running = summary(at="2026-10-15T23:01:00Z")
        running["body"] = "<!-- codex-review-state:v1 " + json.dumps({
            "code_review": {"commit_sha": HEAD, "status": "running",
                            "has_unresolved_findings": None}}) + " -->"
        adverse = summary(at="2026-10-15T23:01:00Z", unresolved=True)
        for other in (running, adverse):
            for pair in ([completed, other], [other, completed]):
                with self.subTest(other=other["body"], pair=pair):
                    result = gate.decision(HEAD, [request(), *pair, positive()], [], [])
                    self.assertEqual(result["status"], "AMBIGUOUS_CODEX_STATE_SEQUENCE")
                    self.assertFalse(result["technical_review_accepted"])

    def test_later_unambiguous_completion_can_close_previous_state_timestamp_tie(self):
        earlier = summary(at="2026-10-15T23:01:00Z")
        running = summary(at="2026-10-15T23:01:00Z")
        running["body"] = "<!-- codex-review-state:v1 " + json.dumps({
            "code_review": {"commit_sha": HEAD, "status": "running",
                            "has_unresolved_findings": None}}) + " -->"
        later = summary(at="2026-10-15T23:03:00Z")
        result = gate.decision(HEAD, [request(), earlier, running, later,
                                      positive(at="2026-10-15T23:04:00Z")], [], [])
        self.assertEqual(result["status"], "FINAL_TECHNICAL_REVIEW")

    def test_positive_at_same_second_as_completion_has_no_temporal_proof(self):
        rows = [request(), summary(at="2026-10-15T23:01:00Z"),
                positive(at="2026-10-15T23:01:00Z")]
        self.assertEqual(gate.decision(HEAD, rows, [], [])["status"],
                         "POSITIVE_WITHOUT_EXACT_HEAD_COMPLETION")

    def test_edited_request_requires_later_review(self):
        earlier = [request(), summary(), positive()]
        edited = {"user": HUMAN, "created_at": "2026-10-15T22:30:00Z",
                  "updated_at": "2026-10-15T23:03:00Z", "body": "@codex review"}
        self.assertEqual(gate.decision(HEAD, earlier + [edited], [], [])["status"],
                         "REVIEW_IN_PROGRESS_OR_UNVERIFIED")

    def test_positive_review_is_not_merge_authorization(self):
        result = gate.decision(HEAD, [request(), summary(), positive()], [], [])
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["atomic_review_merge_binding"])

    def test_review_race_negative_control_detects_mutated_missing_guard(self):
        # Remove the consequence of the actual pending-review guard in an
        # isolated copy of the function. The same negative acceptance test
        # MUST fail against the mutant rather than merely pass on good code.
        source = inspect.getsource(gate.decision)
        original = 'if not completed or not positive:\n            return fail("REVIEW_IN_PROGRESS_OR_UNVERIFIED")'
        bad_guard = ('if not completed or not positive:\n'
                     '            return {"status": "FINAL_TECHNICAL_REVIEW", "technical_review_accepted": True}')
        self.assertIn(original, source)
        env = dict(vars(gate))
        exec(compile(source.replace(original, bad_guard), "<mutated-review-finality>", "exec"), env)
        latest_request = request("2026-10-15T22:30:00Z")
        earlier = [request("2026-10-15T22:27:00Z"),
                   summary("2026-10-15T22:27:30Z"),
                   positive("2026-10-15T22:28:00Z"), latest_request]
        self.assertFalse(gate.decision(HEAD, earlier, [], [])["technical_review_accepted"])
        with self.assertRaises(AssertionError):
            self.assertFalse(env["decision"](HEAD, earlier, [], [])["technical_review_accepted"])

    def test_review_requested_after_positive_must_remain_pending(self):
        rows = [request("2026-10-15T22:27:00Z"),
                summary("2026-10-15T22:27:45Z"), positive("2026-10-15T22:28:00Z"),
                request("2026-10-15T22:28:45Z")]
        result = gate.decision(HEAD, rows, [], [])
        self.assertEqual(result["status"], "REVIEW_IN_PROGRESS_OR_UNVERIFIED")
        self.assertFalse(result["technical_review_accepted"])

    def test_prior_review_positive_does_not_clear_current_head(self):
        rows = [request(), summary(head="b" * 40), positive(head="b" * 40)]
        self.assertFalse(gate.decision(HEAD, rows, [], [])["technical_review_accepted"])

    def test_substantive_inline_current_head_blocks_even_after_positive(self):
        rows = [request(), summary(), positive()]
        finding = {"user": BOT, "commit_id": HEAD, "created_at": "2026-10-15T23:03:00Z",
                   "body": "P1: reused evidence can bypass this gate"}
        result = gate.decision(HEAD, rows, [], [finding])
        self.assertEqual(result["status"], "CURRENT_HEAD_INLINE_FINDING")

    def test_unresolved_codex_summary_fails(self):
        result = gate.decision(HEAD, [request(), summary(unresolved=True), positive()], [], [])
        self.assertEqual(result["status"], "UNRESOLVED_CODEX_FINDINGS")

    def test_bot_footer_does_not_look_like_a_human_request(self):
        bot = {"user": BOT, "created_at": "2026-10-15T23:00:00Z",
               "body": "To run, comment @codex review."}
        result = gate.decision(HEAD, [bot, summary(), positive()], [], [])
        self.assertEqual(result["status"], "REVIEW_NOT_REQUESTED")

    def test_new_review_request_during_live_census_blocks_release(self):
        pr = {"head": {"sha": HEAD}, "state": "open", "draft": False,
              "updated_at": "2026-10-15T23:00:00Z"}
        stable = [request(), summary(), positive()]
        changed = stable + [request("2026-10-15T23:03:00Z")]
        with patch.object(gate, "gh_get", return_value=pr), \
             patch.object(gate, "paged", side_effect=[
                 stable, [], [], changed, [], [],
             ]) as fetched:
            with self.assertRaisesRegex(ValueError, "REVIEW_SNAPSHOT_CHANGED_DURING_CENSUS"):
                gate.consistent_live_snapshot("owner/repo", 1650, HEAD)
            self.assertEqual(fetched.call_count, 6)

    def test_head_update_during_live_census_blocks_release(self):
        first = {"head": {"sha": HEAD}, "state": "open", "draft": False}
        second = {"head": {"sha": "b" * 40}, "state": "open", "draft": False}
        with patch.object(gate, "gh_get", side_effect=[first, second]), \
             patch.object(gate, "paged", return_value=[]):
            with self.assertRaisesRegex(ValueError, "PR_HEAD_OR_STATE_CHANGED"):
                gate.consistent_live_snapshot("owner/repo", 1650, HEAD)

    def test_stable_two_pass_live_census_can_pass_technical_only(self):
        pr = {"head": {"sha": HEAD}, "state": "open", "draft": False}
        known = [request(), summary(), positive()]
        with patch.object(gate, "gh_get", return_value=pr), \
             patch.object(gate, "paged", side_effect=[
                 known, [], [], known, [], [],
             ]):
            result = gate.consistent_live_snapshot("owner/repo", 1650, HEAD)
            self.assertEqual(result["status"], "FINAL_TECHNICAL_REVIEW")
            self.assertTrue(result["not_formal_github_approved"])

    def test_incomplete_event_pagination_fails_closed(self):
        batch = [{"id": i} for i in range(100)]
        with patch.object(gate, "gh_get", return_value=batch) as source:
            with self.assertRaisesRegex(ValueError, "PAGINATION_NOT_EXHAUSTIVE"):
                gate.paged("owner/repo", "issues/5/comments")
            self.assertEqual(source.call_count, 10)

    def test_missing_or_bad_timestamp_fails_closed(self):
        bad = request()
        bad.pop("created_at")
        result = gate.decision(HEAD, [bad, summary(), positive()], [], [])
        self.assertEqual(result["status"], "REVIEW_FINALITY_UNVERIFIED")

    def test_old_positive_after_newer_request_fails_even_same_head(self):
        rows = [request("2026-10-15T22:27:00Z"), summary("2026-10-15T22:27:10Z"),
                positive("2026-10-15T22:27:20Z"), request("2026-10-15T22:27:30Z")]
        self.assertFalse(gate.decision(HEAD, rows, [], [])["technical_review_accepted"])


NATIVE = json.loads((Path(__file__).resolve().parent / "test_codex_review_finality_native.json").read_text(encoding="utf-8"))


def native(n):
    case = NATIVE["cases"][str(n)]
    return case["head"], [dict(r) for r in case["comments"]], case["reviews"], case["inline"]


def state(created, updated, head=HEAD, status="completed", unresolved=False):
    """Codex's ONE review-state comment, created at one time and edited in place later."""
    body = {"code_review": {"commit_sha": head, "status": status, "has_any_findings": unresolved,
                            "has_unresolved_findings": unresolved}}
    return {"user": BOT, "created_at": created, "updated_at": updated,
            "body": "<!-- codex-review-state:v1 " + json.dumps(body) + " -->"}


class NativeLifecycleTests(unittest.TestCase):
    """REVIEW ADMISSION RECOVERY 2026-11-27: Codex keeps one state comment per PR, edits it in place, and posts the
    receipt BEFORE the completion edit. Real comment histories of #2323, #2324 and #2325 replayed verbatim."""

    REQ = "2026-11-27T20:50:54Z"
    RECEIPT = "2026-11-27T20:52:20Z"

    def native_rows(self, completed_at="2026-11-27T21:01:39Z", **kw):
        return [request(self.REQ), state("2026-11-27T20:51:10Z", completed_at, **kw), positive(self.RECEIPT)]

    def test_native_convergence_heads_are_final_after_in_place_auto_rereview(self):
        for n, receipt_id, state_id in ((2323, 7227919184, 7227901605), (2324, 7227917055, 7227901638),
                                        (2325, 7227935769, 7227901744)):
            with self.subTest(pr=n):
                head, comments, reviews, inline = native(n)
                by_id = {c["id"]: c for c in comments}
                st, rc = by_id[state_id], by_id[receipt_id]
                # the native facts the old rule misread: created before the receipt, content dated after it
                self.assertLess(st["created_at"], rc["created_at"])
                self.assertGreater(st["updated_at"], rc["created_at"])
                self.assertEqual(rc["created_at"], rc["updated_at"])
                result = gate.decision(head, comments, reviews, inline)
                self.assertEqual(result["status"], "FINAL_TECHNICAL_REVIEW")
                self.assertFalse(result["merge_authorized"])
                # one more request on the unchanged head takes finality away again
                again = comments + [{"user": HUMAN, "body": "@codex review", "created_at": "2026-11-27T22:00:00Z",
                                     "updated_at": "2026-11-27T22:00:00Z"}]
                self.assertEqual(gate.decision(head, again, reviews, inline)["status"],
                                 "REVIEW_IN_PROGRESS_OR_UNVERIFIED")

    def test_native_first_manual_pair_completion_seconds_after_receipt_is_final(self):
        for seconds in ("21", "22", "23"):
            with self.subTest(completed=seconds):
                rows = self.native_rows(completed_at="2026-11-27T20:52:" + seconds + "Z")
                self.assertEqual(gate.decision(HEAD, rows, [], [])["status"], "FINAL_TECHNICAL_REVIEW")

    def test_native_refusals_replayed(self):
        expected = {2308: "UNRESOLVED_CODEX_FINDINGS", 1850: "REVIEW_IN_PROGRESS_OR_UNVERIFIED",
                    1788: "REVIEW_IN_PROGRESS_OR_UNVERIFIED"}
        for n, status in expected.items():
            with self.subTest(pr=n):
                result = gate.decision(*native(n))
                self.assertEqual(result["status"], status)
                self.assertFalse(result["technical_review_accepted"])

    def test_in_place_completion_in_the_receipt_second_has_no_order(self):
        result = gate.decision(HEAD, self.native_rows(completed_at=self.RECEIPT), [], [])
        self.assertEqual(result["status"], "POSITIVE_WITHOUT_EXACT_HEAD_COMPLETION")

    def test_the_newest_receipt_must_be_ordered_against_the_completion_edit(self):
        # an older receipt strictly before the edit does not rescue a newer receipt in the edit's own second
        rows = self.native_rows(completed_at="2026-11-27T20:53:00Z") + [positive("2026-11-27T20:53:00Z")]
        self.assertEqual(gate.decision(HEAD, rows, [], [])["status"], "POSITIVE_WITHOUT_EXACT_HEAD_COMPLETION")

    def test_state_is_dated_by_native_updated_at_never_created_at(self):
        rows = self.native_rows()
        rows[1] = dict(rows[1])
        rows[1].pop("updated_at")
        self.assertEqual(gate.decision(HEAD, rows, [], [])["status"], "REVIEW_FINALITY_UNVERIFIED")
        rows[1]["updated_at"] = "2026-11-27T20:51:09Z"      # edited "before" it was created
        self.assertEqual(gate.decision(HEAD, rows, [], [])["status"], "REVIEW_FINALITY_UNVERIFIED")
        receipt_missing_clock = self.native_rows()
        receipt_missing_clock[2] = {k: v for k, v in receipt_missing_clock[2].items() if k != "updated_at"}
        self.assertEqual(gate.decision(HEAD, receipt_missing_clock, [], [])["status"], "REVIEW_FINALITY_UNVERIFIED")

    def test_newer_running_failed_or_unresolved_edit_after_receipt_blocks(self):
        for status, unresolved in (("running", None), ("failed", True), ("cancelled", None), ("completed", True)):
            with self.subTest(status=status):
                rows = self.native_rows(status=status, unresolved=unresolved)
                self.assertFalse(gate.decision(HEAD, rows, [], [])["technical_review_accepted"])
        quota = self.native_rows(status="failed", unresolved=True) + [{
            "user": BOT, "created_at": "2026-11-27T21:01:45Z", "updated_at": "2026-11-27T21:01:45Z",
            "body": "You have reached your Codex usage limits for code reviews."}]
        self.assertFalse(gate.decision(HEAD, quota, [], [])["technical_review_accepted"])
        separate = self.native_rows() + [state("2026-11-27T21:05:00Z", "2026-11-27T21:05:00Z", status="running",
                                               unresolved=None)]
        self.assertEqual(gate.decision(HEAD, separate, [], [])["status"], "NEWER_CODEX_REVIEW_NOT_COMPLETE")

    def test_material_finding_between_receipt_and_completion_edit_blocks(self):
        for state_name, body in (("COMMENTED", "Codex Review: Here are some automated review suggestions"),
                                 ("CHANGES_REQUESTED", "P1: reused evidence")):
            with self.subTest(review=state_name):
                review = {"user": BOT, "commit_id": HEAD, "state": state_name,
                          "submitted_at": "2026-11-27T21:01:00Z", "body": body}
                self.assertEqual(gate.decision(HEAD, self.native_rows(), [review], [])["status"],
                                 "LATER_MATERIAL_REVIEW_FINDINGS")
        inline = {"user": BOT, "commit_id": HEAD, "original_commit_id": HEAD, "created_at": "2026-11-27T21:01:00Z",
                  "body": "**![P1 Badge](https://img.shields.io/badge/P1-orange?style=flat)** gate bypass"}
        self.assertEqual(gate.decision(HEAD, self.native_rows(), [], [inline])["status"], "CURRENT_HEAD_INLINE_FINDING")

    def test_receipt_reused_from_an_earlier_request_window_is_not_counted(self):
        rows = [request("2026-11-27T20:40:00Z"), positive("2026-11-27T20:41:00Z"), request(self.REQ),
                state("2026-11-27T20:39:00Z", "2026-11-27T21:01:39Z")]
        self.assertEqual(gate.decision(HEAD, rows, [], [])["status"], "REVIEW_IN_PROGRESS_OR_UNVERIFIED")

    def test_stale_receipt_or_state_from_another_head_is_refused(self):
        other = "b" * 40
        for rows in ([request(self.REQ), state("2026-11-27T20:51:10Z", "2026-11-27T21:01:39Z"), positive(self.RECEIPT, head=other)],
                     [request(self.REQ), state("2026-11-27T20:51:10Z", "2026-11-27T21:01:39Z", head=other), positive(self.RECEIPT)]):
            self.assertFalse(gate.decision(HEAD, rows, [], [])["technical_review_accepted"])
        # head drift: the head moved after the native review; the old evidence never clears the new head
        head, comments, reviews, inline = native(2323)
        self.assertFalse(gate.decision("c" * 40, comments, reviews, inline)["technical_review_accepted"])

    def test_forged_identities_and_the_author_never_review_in_native_order(self):
        for user in ({"login": "chatgpt-codex-connector[bot]", "type": "Bot", "id": 999},
                     {"login": "chatgpt-codex-connector[bot]", "type": "User", "id": 199175422},
                     {"login": "chatgpt-codex-connector-fake", "type": "Bot", "id": 199175422},
                     HUMAN):
            with self.subTest(user=user):
                rows = self.native_rows()
                rows[1], rows[2] = dict(rows[1], user=user), dict(rows[2], user=user)
                self.assertEqual(gate.decision(HEAD, rows, [], [])["status"], "REVIEW_IN_PROGRESS_OR_UNVERIFIED")
        # Codex's own "@codex review" line is never the request that opens the window
        bot_only = [dict(request(self.REQ), user=BOT, updated_at=self.REQ)] + self.native_rows()[1:]
        self.assertEqual(gate.decision(HEAD, bot_only, [], [])["status"], "REVIEW_NOT_REQUESTED")
        # any non-Codex request (#2377: an unproven bot request) can only take finality away
        actions = {"login": "github-actions[bot]", "type": "Bot", "id": 41898282}
        later_bot = self.native_rows() + [{"user": actions, "body": "@codex review", "created_at": "2026-11-27T21:02:00Z",
                                            "updated_at": "2026-11-27T21:02:00Z"}]
        self.assertFalse(gate.decision(HEAD, later_bot, [], [])["technical_review_accepted"])

    def test_conflicting_states_in_the_latest_second_stay_ambiguous(self):
        rows = self.native_rows() + [state("2026-11-27T21:01:39Z", "2026-11-27T21:01:39Z", status="running", unresolved=None)]
        for order in (rows, list(reversed(rows))):
            self.assertEqual(gate.decision(HEAD, order, [], [])["status"], "AMBIGUOUS_CODEX_STATE_SEQUENCE")

    def test_in_place_state_edit_during_live_census_blocks_release(self):
        head, comments, reviews, inline = native(2324)
        pr = {"head": {"sha": head}, "state": "open", "draft": False, "updated_at": "2026-11-27T21:01:27Z"}
        edited = [dict(c) for c in comments]
        for c in edited:
            if c["id"] == 7227901638:
                c["updated_at"] = "2026-11-27T21:30:00Z"
        with patch.object(gate, "gh_get", return_value=pr), \
             patch.object(gate, "paged", side_effect=[comments, reviews, inline, edited, reviews, inline]):
            with self.assertRaisesRegex(ValueError, "REVIEW_SNAPSHOT_CHANGED_DURING_CENSUS"):
                gate.consistent_live_snapshot("owner/repo", 2324, head)
        with patch.object(gate, "gh_get", return_value=pr), \
             patch.object(gate, "paged", side_effect=[comments, reviews, inline, comments, reviews, inline]):
            self.assertEqual(gate.consistent_live_snapshot("owner/repo", 2324, head)["status"], "FINAL_TECHNICAL_REVIEW")

    def test_incomplete_native_comment_pages_fail_closed(self):
        head, comments, _reviews, _inline = native(2325)
        full_page = (comments * 20)[:100]
        with patch.object(gate, "gh_get", return_value=full_page) as source:
            with self.assertRaisesRegex(ValueError, "PAGINATION_NOT_EXHAUSTIVE"):
                gate.paged("owner/repo", "issues/2325/comments")
            self.assertEqual(source.call_count, 10)


if __name__ == "__main__":
    unittest.main()
