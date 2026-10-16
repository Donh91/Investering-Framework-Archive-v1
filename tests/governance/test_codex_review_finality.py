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

    def test_positive_before_exact_state_completion_is_not_verified(self):
        rows = [request(), positive(at="2026-10-15T23:01:00Z"),
                summary(at="2026-10-15T23:02:00Z")]
        self.assertEqual(gate.decision(HEAD, rows, [], [])["status"],
                         "POSITIVE_WITHOUT_EXACT_HEAD_COMPLETION")

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


if __name__ == "__main__":
    unittest.main()
