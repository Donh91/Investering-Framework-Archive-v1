"""S1 v3.3 W5 (producer side): what the brief does so that a scheduled tick can finish and the owner can see why not.

1. OWNER ROUTE FOR A MISSING REQUIRED JOB (rule 2c). S1's connector has no update-branch call, so an entry
   "BRANCH_UPDATE" without `by` could only end as a skip, every tick, in front of every other entry. The entry now
   carries by=OWNER and its reason; it is announced once per head and the owner sees it in the FIRST LINE.
2. THE CARRY MARKER (W2b detached review, residual 1). A build that cannot read the brief issue list never saw the
   previous brief: it carries nothing. It says so (c1b.carry UNKNOWN); publish never lets it replace a brief that
   holds a C1b halt; and the next build fails closed on it (C1b:carry_unknown, with the gap published).
3. C1B_GAP in the FIRST LINE (residual 2): history the C1b halt test never scanned is owner-visible.
4. THE LEDGER HINT (W5 item 3): last_action and actions_24h from the #1156 read; a heartbeat counts only when it is
   of this task. ticks_24h stays unproven: a run that ended NOOP writes nothing.
5. B.next[].builds: in how many briefs in a row an entry has been ranked. An S1 tick that ends NOOP leaves no trace, so
   this is the one native measure of work S1 could have done and did not.

Fixtures only, no network."""
import json
import sys
import unittest
from datetime import timedelta
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "scripts" / "governance", ROOT / "tests" / "governance"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import s1_tick_brief_v1 as B  # noqa: E402
import test_s1_tick_brief_v1 as TB  # noqa: E402  (module import: its TestCases are not collected twice)
import test_s1_brief_c1b_v1 as TC  # noqa: E402

NOW = TB.NOW
CONTRACT8 = "contract=77922ae6"


def no_storage_run(w):
    """A required job that never ran on this head: the storage-health run is absent (CI MISSING); the PR is 3 behind."""
    w["pr"][7]["runs"] = [r for r in w["pr"][7]["runs"] if "storage" not in r["path"]]


class OwnerRouteForMissingCi(unittest.TestCase):
    def test_a_missing_required_job_behind_main_is_the_owner_route(self):
        b = TB.brief_of(no_storage_run)
        x = TB.top(b)
        self.assertEqual((x["action"], x["rule"], x["how"], x["by"], x["reason"], x["pr"]),
                         ("REPAIR", "2c", "BRANCH_UPDATE", "OWNER", "ci_missing", 7))
        self.assertEqual((x["missing"], x["verify"]), (["storage-health"], ["head", "no_owner_update_item"]))
        self.assertNotIn("gate_stale", x)
        self.assertIn("BRANCH_UPDATE(#7)", b["status_lines"][0])
        self.assertEqual(B.S1_BRANCH_UPDATE_ROUTE, "OWNER")

    def test_it_is_announced_once_per_head_and_the_owner_still_sees_it(self):
        def noted(w, ago):
            no_storage_run(w)
            w["pr"][7]["comments"].append(TB.comment(40, f"S1_ITEM_v1\nitem: pr:7\nstate: BUILD\nnext: OWNER_BRANCH_UPDATE\n{CONTRACT8}", minutes_ago=ago))
        b = TB.brief_of(lambda w: noted(w, 100))                  # newer than the head's commit (400 minutes ago)
        self.assertFalse(any(x.get("pr") == 7 and x["action"] == "REPAIR" for x in b["next"]))
        self.assertIn("BRANCH_UPDATE(#7)", b["status_lines"][0])
        b = TB.brief_of(lambda w: noted(w, 500))                  # an item from before this head: announced again
        self.assertEqual((TB.top(b)["by"], TB.top(b)["reason"]), ("OWNER", "ci_missing"))

    def test_the_gate_stale_route_keeps_its_own_reason(self):
        x = TB.top(TB.brief_of(TB.privacy_failed))
        self.assertEqual((x["by"], x["reason"], x["gate_stale"]), ("OWNER", "gate_stale", [B.GATE_FILES[3]]))
        self.assertNotIn("missing", x)

    def test_what_is_not_this_route(self):
        def up_to_date(w):
            no_storage_run(w)
            w["pr"][7]["compare"]["behind_by"] = 0
        def conflict(w):
            no_storage_run(w)
            w["pr"][7]["compare"]["main_changed_paths"] = ["docs/notes/a.md"]
        def unread_compare(w):
            no_storage_run(w)
            w["pr"][7]["compare"]["complete"] = False
        def writer(w):
            no_storage_run(w)
            w["pr"][7]["comments"].append(TB.comment(41, "@codex address the failing job", minutes_ago=30))
        b = TB.brief_of(up_to_date)                                # nothing to take from main: no branch update at all
        self.assertEqual(b["next"], [])
        self.assertNotIn("BRANCH_UPDATE", b["status_lines"][0])
        b = TB.brief_of(conflict)                                  # main changed a PR file: rule 2d, never an overlay
        self.assertEqual((TB.top(b)["rule"], TB.top(b)["how"]), ("2d", "CODEX_ADDRESS_MERGE_MAIN"))
        self.assertNotIn("by", TB.top(b))
        b = TB.brief_of(unread_compare)                            # the overlap is NOT_PROVEN: no entry, no owner line
        self.assertFalse(any(x["action"] == "REPAIR" for x in b["next"]))
        self.assertNotIn("BRANCH_UPDATE", b["status_lines"][0])
        b = TB.brief_of(writer)                                    # H7: another writer works on the branch
        self.assertFalse(any(x["action"] == "REPAIR" for x in b["next"]))
        self.assertNotIn("BRANCH_UPDATE", b["status_lines"][0])

    def test_a_failed_or_pending_job_is_not_a_missing_one(self):
        def failed(w):                                             # a job that ran and failed: rule 2a, a code fix
            TB.privacy_failed(w, stale=False)
        b = TB.brief_of(failed)
        self.assertEqual((TB.entry(b)["ci"]["state"], TB.top(b)["how"]), ("FAIL", "CODEX_ADDRESS"))
        self.assertNotIn("BRANCH_UPDATE", b["status_lines"][0])
        def pending(w):                                            # a job still running: nobody updates anything
            for jobs in w["pr"][7]["jobs"].values():
                for j in jobs:
                    if j["name"] == "storage-health":
                        j.update(status="in_progress", conclusion=None)
        b = TB.brief_of(pending)
        self.assertNotIn(TB.entry(b)["ci"]["state"], ("MISSING", "GREEN"))
        self.assertFalse(any(x.get("by") == "OWNER" for x in b["next"]))
        self.assertNotIn("BRANCH_UPDATE", b["status_lines"][0])

    def test_a_green_pr_behind_main_is_never_an_owner_update(self):
        b = TB.brief_of()
        self.assertNotIn("BRANCH_UPDATE", b["status_lines"][0])
        self.assertFalse(any(x.get("by") == "OWNER" for x in b["next"]))

    def test_the_switch_restores_the_entry_without_by(self):
        with mock.patch.object(B, "S1_BRANCH_UPDATE_ROUTE", "S1"):
            b = TB.brief_of(no_storage_run)
            x = TB.top(b)
            self.assertEqual((x["rule"], x["how"], x["missing"]), ("2c", "BRANCH_UPDATE", ["storage-health"]))
            self.assertNotIn("by", x)
            self.assertNotIn("BRANCH_UPDATE", b["status_lines"][0])
            self.assertEqual(TB.top(TB.brief_of(TB.privacy_failed))["by"], "OWNER")      # gate_stale never depended on it

    def test_a_merge_candidate_still_ranks_before_the_owner_entry(self):
        def two(w):
            no_storage_run(w)
            w["pulls"].append(TB.pull(n=8, head="c" * 40))
            w["pr"][8] = TB.pr_data("c" * 40)
            w["pr"][8]["detail"]["number"] = w["pr"][8]["detail2"]["number"] = 8
            w["pr"][8]["comments"] = []
        b = TB.brief_of(two)
        self.assertEqual([(x["pr"], x["action"], x.get("by")) for x in b["next"]], [(8, "MERGE_IF_CLAUDE_APPROVE", None), (7, "REPAIR", "OWNER")])


def halt(tag="old"):
    return {"commit": TC.sha(tag), "parent": TC.sha(tag + " parent"), "entries": ["tests"], "capped": False}


def body_of(record, run_id=556, minutes_ago=5):
    w = dict(TB.world(), run={"id": run_id, "attempt": 1, "event": "schedule"})
    w["c1b"] = record
    brief = B.build_brief(w)
    brief["generated_at"] = TB.ts(minutes_ago)
    return B.render(brief)


class CarryMarker(unittest.TestCase):
    def setUp(self):
        self.h = TC.History()
        self.anchor = self.h.commit("data: a")
        self.h.commit("data: b")

    def test_an_unreadable_issue_list_is_marked_and_incomplete(self):
        out, _gh = TC.c1b(self.h, self.anchor, halt=halt(), fail=["issues"])
        self.assertEqual((out["complete"], out["reason"], out["carry"], out["halt"], out["checked_through"]),
                         (False, "C1b:issues_unreadable", "UNKNOWN", None, None))
        b = TC.brief_with(out)
        self.assertEqual((b["complete"], b["incomplete"], b["c1b"]["carry"]), (False, "C1b:issues_unreadable", "UNKNOWN"))
        self.assertEqual(B.parse_body(B.render(b))["c1b"]["carry"], "UNKNOWN")

    def test_every_other_failure_is_not_marked(self):
        for fail in (["actions/runs/"], ["commits"], ["git/trees/"]):
            with self.subTest(fail):
                out, _gh = TC.c1b(self.h, self.anchor, fail=fail)
                self.assertIsNone(out["carry"])                     # the previous brief WAS read: its halt is carried as before
        out, _gh = TC.c1b(self.h, self.anchor)
        self.assertEqual((out["complete"], out["carry"]), (True, None))
        self.assertIsNone(TC.brief_with(out)["c1b"]["carry"])

    def marked_previous(self):
        """The published brief of a build that could not read its predecessor (as publish wrote it)."""
        issue, run = TC.previous(self.anchor)
        marked = B.parse_body(issue["body"])
        marked["c1b"] = {"checked_through": None, "from": None, "halt": None, "gap": None, "carry": "UNKNOWN"}
        marked.update(complete=False, incomplete="C1b:issues_unreadable")
        return dict(issue, body=B.render(marked)), run

    def test_the_next_build_fails_closed_and_publishes_the_gap(self):
        issue, run = self.marked_previous()
        out = B.read_c1b(TC.Gh(self.h, issue, run), self.h.main, [], NOW)
        self.assertEqual((out["complete"], out["reason"], out["carry"]), (False, "C1b:carry_unknown", None))
        self.assertEqual(out["checked_through"], self.h.main)       # the window WAS scanned: the build after this one recovers
        b = TC.brief_with(out)
        self.assertEqual((b["complete"], b["incomplete"]), (False, "C1b:carry_unknown"))
        gap = b["c1b"]["gap"]                                        # fix round 5: + the commit an owner disposition names, and the carry flag
        self.assertEqual({k: gap[k] for k in ("from_unknown", "window", "reason", "carried")},
                         {"from_unknown": True, "window": B.C1B_WINDOW, "reason": "C1b:carry_unknown", "carried": False})
        self.assertIn(f"C1B_GAP(window={B.C1B_WINDOW})", b["status_lines"][0])

    def test_the_marked_brief_is_never_an_anchor_even_when_it_names_one(self):
        issue, run = self.marked_previous()
        forged = B.parse_body(issue["body"])
        forged["c1b"]["checked_through"] = self.h.main            # a marked brief that claims everything was checked
        out = B.read_c1b(TC.Gh(self.h, dict(issue, body=B.render(forged)), run), self.h.main, [], NOW)
        self.assertEqual((out["complete"], out["reason"]), (False, "C1b:carry_unknown"))

    def test_a_halt_in_the_unscanned_window_is_found_again(self):
        bad = self.h.commit("direct push", code=("scripts",))
        self.h.commit("data: c")
        issue, run = self.marked_previous()
        out = B.read_c1b(TC.Gh(self.h, issue, run), self.h.main, [], NOW)
        self.assertEqual((out["halt"]["commit"], out["complete"]), (bad, False))

    def test_the_marker_stays_while_the_recovery_scan_cannot_finish(self):
        issue, run = self.marked_previous()
        for fail in (["commits"], ["git/trees/"]):
            with self.subTest(fail):
                self.h.commit("direct push", code=("scripts",))     # the scan must read a tree
                out = B.read_c1b(TC.Gh(self.h, issue, run, fail=fail), self.h.main, [], NOW)
                self.assertEqual((out["complete"], out["carry"]), (False, "UNKNOWN"))
                self.assertNotEqual(out["checked_through"], self.h.main)

    def test_the_build_after_the_recovery_is_complete_again(self):
        issue, run = self.marked_previous()
        out = B.read_c1b(TC.Gh(self.h, issue, run), self.h.main, [], NOW)
        recovered, run2 = TC.previous(self.h.main)                 # what that build published: checked_through = its main
        self.h.commit("data: d")
        out = B.read_c1b(TC.Gh(self.h, recovered, run2), self.h.main, [], NOW)
        self.assertEqual((out["complete"], out["reason"], out["carry"], out["gap"]), (True, None, None, None))


class PublishKeepsAHalt(unittest.TestCase):
    """A build that carried nothing never overwrites the only copy of an unposted halt."""

    class Fake(TB.Publish.Fake):
        pass

    def published(self, record):
        return [{"number": 3000, "user": dict(TB.BOT), "body": body_of(record, run_id=554, minutes_ago=65), "updated_at": TB.ts(64)}]

    def setUp(self):
        self.unknown = body_of({"checked_through": None, "from": None, "halt": None, "carry": "UNKNOWN", "complete": False,
                                "reason": "C1b:issues_unreadable"})
        self.with_halt = {"checked_through": TB.MAIN, "from": TB.MAIN, "halt": halt(), "complete": True, "reason": None}
        self.no_halt = {"checked_through": TB.MAIN, "from": TB.MAIN, "halt": None, "complete": True, "reason": None}

    def test_a_marked_brief_does_not_replace_a_brief_with_a_halt(self):
        gh = self.Fake(self.published(self.with_halt))
        self.assertEqual(B.publish(gh, self.unknown, NOW), 3000)
        self.assertEqual(gh.writes, [])
        self.assertEqual(B.parse_body(gh.issues[0]["body"])["c1b"]["halt"]["commit"], halt()["commit"])

    def test_a_marked_brief_replaces_a_brief_without_a_halt(self):
        gh = self.Fake(self.published(self.no_halt))
        B.publish(gh, self.unknown, NOW)
        self.assertEqual([(m, u) for m, u, _ in gh.writes], [("PATCH", "issues/3000")])

    def test_an_ordinary_brief_replaces_a_brief_with_a_halt(self):
        gh = self.Fake(self.published(self.with_halt))
        B.publish(gh, body_of(self.no_halt), NOW)                  # it read the previous brief: the halt is its own to carry
        self.assertEqual([(m, u) for m, u, _ in gh.writes], [("PATCH", "issues/3000")])

    def test_only_a_valid_halt_of_a_bot_issue_is_kept(self):
        rows = self.published(self.with_halt)                       # a published body whose halt is not one c1b_halt_ok accepts
        forged = B.parse_body(rows[0]["body"])
        forged["c1b"]["halt"] = dict(halt(), entries=["docs"])
        rows[0]["body"] = B.render(forged)
        self.assertEqual(B.parse_body(rows[0]["body"])["c1b"]["halt"]["entries"], ["docs"])
        gh = self.Fake(rows)
        B.publish(gh, self.unknown, NOW)
        self.assertEqual(len(gh.writes), 1)
        rows = self.published(self.with_halt)
        rows[0]["body"] = "not a brief"
        gh = self.Fake(rows)
        B.publish(gh, self.unknown, NOW)
        self.assertEqual(len(gh.writes), 1)
        with self.assertRaises(SystemExit):                        # a labelled issue that is not the bot's: refused as before
            B.publish(self.Fake([dict(self.published(self.with_halt)[0], user=dict(TB.OWNER))]), self.unknown, NOW)


class GapInTheFirstLine(unittest.TestCase):
    def test_a_gap_is_an_owner_entry(self):
        h = TC.History()
        h.commit("data: a")
        out, _gh = TC.c1b(h, None)                                 # no previous brief: the window fallback
        b = TC.brief_with(out)
        self.assertIn(f"C1B_GAP(window={B.C1B_WINDOW})", b["status_lines"][0])
        self.assertTrue(b["status_lines"][0].startswith("OWNER APPROVAL REQUIRED: "))

    def test_no_gap_no_entry(self):
        self.assertNotIn("C1B_GAP", TB.brief_of()["status_lines"][0])
        self.assertEqual(B.status_lines([], {"off_reasons": []}, [], NOW)[0], "OWNER APPROVAL REQUIRED: NONE")
        self.assertEqual(B.status_lines([], {"off_reasons": []}, [], NOW, {"gap": {"from_unknown": False}})[0], "OWNER APPROVAL REQUIRED: NONE")
        self.assertEqual(B.status_lines([], {"off_reasons": []}, [], NOW, {"gap": {"from_unknown": True, "window": 100}})[0],
                         "OWNER APPROVAL REQUIRED: C1B_GAP(window=100)")


class LedgerActions(unittest.TestCase):
    def ledger(self, comments):
        return TB.brief_of(lambda w: w.update(issue_comments=comments))["ledger"]

    def test_the_newest_authentic_action_receipt(self):
        rows = [TB.comment(70, f"S1_LANE_MERGE_v1\npr: 6\n{CONTRACT8}", minutes_ago=3000),
                TB.comment(71, f"REQUEST_REVIEW pr=9 head=x main=y comment=1 brief=2 {CONTRACT8}", minutes_ago=200),
                TB.comment(72, f"S1_HEARTBEAT_v1\nmain=aaaaaaaa {CONTRACT8}", minutes_ago=100),      # observability, not an action
                TB.comment(73, f"S1_LANE_MERGE_INTENT_v1\npr: 7\nloop: {'4' * 40}\n{CONTRACT8}", minutes_ago=90),   # an intent is not an outcome
                TB.comment(74, f"S1_ITEM_v1\nitem: pr:7\nstate: BUILD\n{CONTRACT8}", minutes_ago=80)]
        got = self.ledger(rows)
        self.assertEqual(got["last_action"], {"at": TB.ts(200), "action": "REQUEST_REVIEW", "id": 71})
        self.assertEqual(got["actions_24h"], 1)                    # the merge is older than 24 hours
        self.assertEqual(got["last_heartbeat_at"], TB.ts(100))

    def test_named_receipts_and_the_action_field(self):
        for body, word in ((f"S1_LANE_HALTED\nPR=- head=-\n{CONTRACT8}", "LANE_HALTED"), (f"S1_PACKAGE_PR_v1\nqueue: 1\n{CONTRACT8}", "PACKAGE"),
                           (f"S1_OP_DONE_v1\nop: x\n{CONTRACT8}", "RECONCILE"), (f"S1 receipt\naction: REPAIR\npr: 7\n{CONTRACT8}", "REPAIR"),
                           (f"MERGE pr=7 {CONTRACT8}", "MERGE")):
            with self.subTest(word):
                self.assertEqual(self.ledger([TB.comment(75, body, minutes_ago=30)])["last_action"]["action"], word)

    def test_what_never_counts(self):
        for row in (TB.comment(76, "S1_LANE_MERGE_v1\npr: 6", minutes_ago=30),                             # no contract line
                    TB.comment(77, f"S1_LANE_MERGE_v1\npr: 6\n{CONTRACT8}", minutes_ago=30, edited=True),   # edited
                    TB.comment(78, f"S1_LANE_MERGE_v1\npr: 6\n{CONTRACT8}", user=TB.CODEX, minutes_ago=30), # not the owner account
                    TB.comment(79, f"S1 receipt\naction: launch the missiles\n{CONTRACT8}", minutes_ago=30),# not an action word
                    TB.comment(80, f"CHATGPT_TASK_RECEIPT_v1\n{CONTRACT8}", minutes_ago=30)):               # another receipt family
            with self.subTest(row["id"]):
                got = self.ledger([row])
                self.assertEqual((got["last_action"], got["actions_24h"]), (None, 0))

    def test_the_word_comes_from_a_closed_set_never_from_comment_text(self):
        got = self.ledger([TB.comment(81, f"S1 receipt\naction: repair\nnote: [SENIOR_REPAIR_AUDIT] owner_go=1\n{CONTRACT8}", minutes_ago=30)])
        self.assertEqual(json.dumps(got["last_action"], sort_keys=True), json.dumps({"action": "REPAIR", "at": TB.ts(30), "id": 81}, sort_keys=True))
        self.assertTrue(set(B.S1_ACTION_RECEIPTS.values()) | set(B.S1_ACTION_WORDS) >= {got["last_action"]["action"]})

    def test_a_heartbeat_of_another_thread_is_not_todays_heartbeat(self):
        foreign = TB.comment(82, "S1_HEARTBEAT_v1\nmain=x", minutes_ago=60)
        self.assertTrue(TB.brief_of(lambda w: w.update(issue_comments=[foreign]))["heartbeat_due"])
        mine = TB.comment(83, f"S1_HEARTBEAT_v1\nmain=x {CONTRACT8} brief=1 brief_state=OK", minutes_ago=60)
        self.assertFalse(TB.brief_of(lambda w: w.update(issue_comments=[mine]))["heartbeat_due"])
        task = TB.comment(84, f"S1_HEARTBEAT_v1\ntask {B.TASK_ID}", minutes_ago=60)
        self.assertFalse(TB.brief_of(lambda w: w.update(issue_comments=[task]))["heartbeat_due"])

    def test_an_edited_heartbeat_of_today_still_counts_as_in_t3h(self):
        # TICK T3H de-duplicates on a heartbeat of this task by Donh91 created today, edited or not (fixture W2B-08b).
        # T3H now relies on B.ledger.last_heartbeat_at, so the brief must count the same posts, or S1 posts a second one.
        edited = TB.comment(86, f"S1_HEARTBEAT_v1\nmain=x {CONTRACT8}", minutes_ago=60, edited=True)
        b = TB.brief_of(lambda w: w.update(issue_comments=[edited]))
        self.assertEqual((b["ledger"]["last_heartbeat_at"], b["heartbeat_due"]), (TB.ts(60), False))
        foreign = TB.comment(87, f"S1_HEARTBEAT_v1\nmain=x {CONTRACT8}", user=TB.CODEX, minutes_ago=30)
        self.assertEqual(TB.brief_of(lambda w: w.update(issue_comments=[edited, foreign]))["ledger"]["last_heartbeat_at"], TB.ts(60))

    def test_the_hint_survives_every_shrink_level(self):
        b = TB.brief_of(lambda w: w.update(issue_comments=[TB.comment(85, f"S1_LANE_HALTED\nPR=- head=-\n{CONTRACT8}", minutes_ago=30)]))
        with mock.patch.object(B, "MAX_BODY", 10):
            small = B.parse_body(B.render(b))
        self.assertEqual((small["shrunk"], small["ledger"]["last_action"]["action"]), (3, "LANE_HALTED"))

    def test_window_edge(self):
        at = lambda minutes: TB.comment(90 + minutes % 7, f"S1_OP_DONE_v1\n{CONTRACT8}", minutes_ago=minutes)
        self.assertEqual(self.ledger([at(24 * 60)])["actions_24h"], 1)
        self.assertEqual(self.ledger([at(24 * 60 + 1)])["actions_24h"], 0)
        self.assertEqual(B.ledger_hint([at(5)], [], True)["actions_24h"], None)     # no clock, no count


class BuildsCounter(unittest.TestCase):
    def published(self, brief):
        """The brief issue and its run, as the next build reads them."""
        brief = dict(brief, generated_at=TB.ts(65))
        issue = {"number": 3, "user": dict(TB.BOT), "body": B.render(brief), "updated_at": TB.ts(64)}
        run = {"id": brief["run_id"], "path": B.WORKFLOW_PATH, "repository": {"full_name": B.REPO}, "head_branch": "main", "head_sha": brief["main"],
               "status": "completed", "conclusion": "success", "run_started_at": TB.ts(70), "updated_at": TB.ts(60)}
        return issue, run

    def next_brief(self, previous_brief, mutate=no_storage_run, **gh):
        h = TC.History()
        h.commit("data: a")
        issue, run = self.published(dict(previous_brief, main=h.main))
        record = B.read_c1b(TC.Gh(h, issue, run, **gh), h.main, [], NOW)
        w = TB.world()
        mutate(w)
        w["c1b"] = record
        return B.build_brief(w)

    def test_a_new_entry_starts_at_one_and_counts_up_brief_after_brief(self):
        first = TB.brief_of(no_storage_run)
        self.assertEqual([x["builds"] for x in first["next"]], [1])
        second = self.next_brief(first)
        self.assertEqual((TB.top(second)["by"], TB.top(second)["builds"]), ("OWNER", 2))
        third = self.next_brief(second)
        self.assertEqual(TB.top(third)["builds"], 3)

    def test_a_new_head_or_another_action_is_new_work(self):
        first = TB.brief_of(no_storage_run)
        def new_head(w):
            w["pulls"] = [TB.pull(head="d" * 40)]
            w["pr"][7] = TB.pr_data("d" * 40)
            no_storage_run(w)
        self.assertEqual(TB.top(self.next_brief(first, new_head))["builds"], 1)
        other = self.next_brief(first, TB.privacy_failed)          # the same PR and head, another reason: still the owner route
        self.assertEqual((TB.top(other)["reason"], TB.top(other)["builds"]), ("gate_stale", 2))
        review = self.next_brief(first, lambda w: w["pr"][7].update(comments=[]))
        self.assertEqual((TB.top(review)["action"], TB.top(review)["builds"]), ("MERGE_IF_CLAUDE_APPROVE", 1))

    def test_an_unread_predecessor_restarts_the_count_and_never_inflates_it(self):
        first = TB.brief_of(no_storage_run)
        first["next"][0]["builds"] = 7
        self.assertEqual(TB.top(self.next_brief(first))["builds"], 8)
        self.assertEqual(TB.top(self.next_brief(first, fail=["issues"]))["builds"], 1)
        for bad in (True, -3, "9", 10 ** 6, None):                 # a count that is not a small positive integer reads as 1
            first["next"][0]["builds"] = bad
            self.assertEqual(TB.top(self.next_brief(first))["builds"], 2, bad)
        first["next"][0]["builds"] = B.MAX_BUILDS
        self.assertEqual(TB.top(self.next_brief(first))["builds"], B.MAX_BUILDS)

    def test_a_body_not_written_by_the_actions_bot_counts_nothing(self):
        first = TB.brief_of(no_storage_run)
        first["next"][0]["builds"] = 7
        h = TC.History()
        h.commit("data: a")
        issue, run = self.published(dict(first, main=h.main))
        record = B.read_c1b(TC.Gh(h, dict(issue, user=dict(TB.OWNER)), run), h.main, [], NOW)
        self.assertEqual(record["prev_next"], {})

    def test_the_key_separates_what_must_be_separate(self):
        k = B.entry_key
        base = {"action": "REPAIR", "how": "BRANCH_UPDATE", "pr": 7, "head": "a" * 40}
        self.assertNotEqual(k(base), k(dict(base, pr=8)))
        self.assertNotEqual(k(base), k(dict(base, head="b" * 40)))
        self.assertNotEqual(k(base), k(dict(base, how="CODEX_ADDRESS")))
        self.assertNotEqual(k({"action": "HALT", "rule": "C1b", "commit": "c" * 40}), k({"action": "HALT", "rule": "C1b", "commit": "d" * 40}))
        self.assertNotEqual(k({"action": "HALT", "rule": "C7", "run": 1}), k({"action": "HALT", "rule": "C7", "run": 2}))
        self.assertIsNone(k("x"))
        self.assertEqual(B.next_builds("x"), {})

    def test_s1_never_reads_it(self):
        self.assertNotIn("builds", TB.TICK)                        # evidence for the owner and the acceptance record only
        self.assertEqual(B.parse_body(B.render(TB.brief_of(no_storage_run)))["next"][0]["builds"], 1)


if __name__ == "__main__":
    unittest.main()
