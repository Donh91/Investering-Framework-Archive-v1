"""Non-vacuous negative controls: each gate stops on ITS OWN reason; a positive control passes."""
import unittest
from datetime import timedelta
import test_s1_executor_v1 as T
import test_s1_review_dispatch_v1 as R
import s1_tick_brief_v1 as B
import check_codex_review_finality as F


def aged(minutes):
    return lambda w, gh, n: [c["commit"]["committer"].update(date=B.iso(T.NOW - timedelta(minutes=minutes)))
                             for c in w["pr"][7]["commits"] if c.get("sha") == T.HEAD]


def with_path(path):
    def live(w, gh, n):
        w["pr"][7]["files"].append(dict(w["pr"][7]["files"][0], filename=path))
        gh.pull.update(changed_files=len(w["pr"][7]["files"]))
    return live


class ReviewDispatchGatesStopOnTheirOwnReason(unittest.TestCase):
    def assert_skipped(self, live, reason):
        out, gh, lines = R._probe("LIVE", live=live)
        self.assertNotIn("issues/7/comments", [x[1] for x in gh.writes])
        self.assertIn(f"S1_EXECUTOR_REVIEW SKIPPED({reason})", lines, lines)

    def test_positive_control_requests(self):
        out, gh, _l = R._probe("LIVE")
        self.assertTrue(out["result"].startswith("REQUESTED_REVIEW"), out["result"])

    def test_head_between_quiet_window_and_two_hours_waits(self):
        self.assert_skipped(aged(90), "review_wait_2h")          # 60 min quiet window passed, 2 h not

    def test_workflow_path_is_owner_gated(self):
        self.assert_skipped(with_path(".github/workflows/x.yml"), "review_owner_gated")

    def test_agents_path_is_owner_gated(self):
        self.assert_skipped(with_path("AGENTS.md"), "review_owner_gated")


class LaterBotRequestRemovesFinality(unittest.TestCase):
    def test_non_vacuous(self):
        head = T.HEAD
        cx = {"login": "chatgpt-codex-connector[bot]", "type": "Bot", "id": 199175422}
        state = '<!-- codex-review-state:v1 {"code_review": {"commit_sha": "%s", "status": "completed", "has_unresolved_findings": false}} -->' % head
        ok = "Codex Review: Didn't find any major issues.\n**Reviewed commit:** `%s`" % head[:10]
        rows = [{"id": 1, "user": {"login": "Donh91", "type": "User"}, "body": "@codex review", "created_at": "2026-11-18T09:00:00Z", "updated_at": "2026-11-18T09:00:00Z"},
                {"id": 2, "user": dict(cx), "body": state, "created_at": "2026-11-18T09:30:00Z", "updated_at": "2026-11-18T09:30:00Z"},
                {"id": 3, "user": dict(cx), "body": ok, "created_at": "2026-11-18T09:31:00Z", "updated_at": "2026-11-18T09:31:00Z"}]
        bot = {"id": 4, "user": dict(B.ACTIONS_BOT), "body": "@codex review", "created_at": "2026-11-18T10:00:00Z", "updated_at": "2026-11-18T10:00:00Z"}
        self.assertIs(F.decision(head, rows, [], []).get("technical_review_accepted"), True)
        self.assertIsNot(F.decision(head, rows + [bot], [], []).get("technical_review_accepted"), True)
