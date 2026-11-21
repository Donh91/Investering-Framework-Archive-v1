"""S1 v3.3 W2b (D1, D4, D5): the producer's C1b halt test (B.c1b), the ledger hint (B.ledger) and the rubric_blobs
verdict reason. Fixtures only, no network: a fake REST reader serves a synthetic first-parent history of main."""
import hashlib
import json
import sys
import unittest
from datetime import timedelta
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "scripts" / "governance", ROOT / "tests" / "governance"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import s1_tick_brief_v1 as B  # noqa: E402
import test_s1_tick_brief_v1 as TB  # noqa: E402  (module import: its TestCases are not collected twice)

NOW = TB.NOW


def sha(label):
    return hashlib.sha1(str(label).encode()).hexdigest()


class History:
    """main's first-parent chain, oldest first. Each commit has a subject, its parents and five root entries; a data
    commit changes the root tree only. commit(...) appends one commit on top of main."""

    def __init__(self):
        self.entries = {d: f"tree:{sha(d + '@0')}" for d in B.T3_TREE_DIRS}
        self.data = 0
        self.base = self._add("base", None)
        self.rows = []                                         # newest first, as GET /commits answers

    def _add(self, subject, parent, extra_parent=None):
        n = len(getattr(self, "rows", [])) + 1
        commit = sha(f"commit{n}:{subject}")
        tree = sha(json.dumps([self.entries, self.data]))
        parents = [{"sha": p} for p in (parent, extra_parent) if p]
        row = {"sha": commit, "parents": parents, "commit": {"message": subject + "\n\nbody", "tree": {"sha": tree}}}
        self.trees = getattr(self, "trees", {})
        self.trees[tree] = dict(self.entries)
        self.trees[commit] = dict(self.entries)              # GitHub resolves a commit SHA to its tree as well
        self.row_of = getattr(self, "row_of", {})
        self.row_of[commit] = row
        return commit

    @property
    def main(self):
        return self.rows[0]["sha"] if self.rows else self.base

    def commit(self, subject, code=(), merge=False):
        self.data += 1
        for d in code:
            self.entries[d] = f"tree:{sha(d + str(self.data))}"
        c = self._add(subject, self.main, extra_parent=sha(f"side{self.data}") if merge else None)
        self.rows.insert(0, self.row_of[c])
        return c

    def page(self):
        return self.rows + [self.row_of[self.base]]


class Gh:
    def __init__(self, history, prev_issue=None, prev_run=None, fail=(), truncated=(), stop_on=None):
        self.h, self.calls, self.paths = history, 0, []
        self.prev_issue, self.prev_run, self.fail, self.truncated, self.stop_on = prev_issue, prev_run, set(fail), set(truncated), stop_on

    def get(self, path, params=None):
        self.calls += 1
        self.paths.append(path)
        if self.stop_on and path.startswith(self.stop_on):
            raise B.ApiBudget("API_BUDGET_EXHAUSTED")
        if any(path.startswith(f) for f in self.fail):
            raise OSError("boom")
        if path == "issues":
            return [self.prev_issue] if self.prev_issue else []
        if path.startswith("actions/runs/"):
            return self.prev_run
        if path == "commits":
            assert params == {"sha": self.h.main, "per_page": B.C1B_WINDOW}, params
            return self.h.page()
        if path.startswith("git/trees/"):
            key = path.split("/")[-1]
            entries = self.h.trees[key]
            doc = {"sha": key, "tree": [{"path": d, "type": v.split(":")[0], "sha": v.split(":")[1]} for d, v in entries.items()]
                   + [{"path": "data", "type": "tree", "sha": sha(key)}], "truncated": key in self.truncated}
            return doc
        raise AssertionError(path)

    def tree_reads(self):
        return sum(1 for p in self.paths if p.startswith("git/trees/"))


def previous(main, c1b="checked", run_id=554, edited=False, halt=None):
    """The published issue and its run: a W2b brief whose c1b.checked_through is `main` (c1b=None: a W2-era brief
    without a c1b block; c1b=<sha>: that checked_through)."""
    w = dict(TB.world(), main_sha=main, run={"id": run_id, "attempt": 1, "event": "schedule"})
    w["c1b"] = {"checked_through": main if c1b == "checked" else c1b, "from": main, "halt": halt, "complete": True}
    brief = B.build_brief(w)
    if c1b is None:
        brief.pop("c1b")
    brief["generated_at"] = TB.ts(65)
    issue = {"number": 3, "user": dict(TB.BOT), "body": B.render(brief), "updated_at": TB.ts(30 if edited else 64)}
    run = {"id": run_id, "path": B.WORKFLOW_PATH, "repository": {"full_name": B.REPO}, "head_branch": "main", "head_sha": main,
           "status": "completed", "conclusion": "success", "run_started_at": TB.ts(70), "updated_at": TB.ts(60)}
    return issue, run


def c1b(history, anchor, ledger=(), max_calls=B.C1B_MAX_CALLS, **kw):
    issue, run = previous(anchor, **{k: kw.pop(k) for k in ("c1b", "edited", "halt") if k in kw}) if anchor else (None, None)
    gh = Gh(history, issue, run, **kw)
    return B.read_c1b(gh, history.main, list(ledger) if ledger is not None else None, NOW, max_calls=max_calls), gh


def brief_with(record, **change):
    w = TB.world()
    w["c1b"] = record
    w.update(change)
    return B.build_brief(w)


class Range(unittest.TestCase):
    def test_no_drift_reads_no_commit_and_no_tree(self):
        h = History()
        h.commit("data: x")
        out, gh = c1b(h, h.main)
        self.assertEqual((out["complete"], out["reason"], out["checked_through"], out["from"], out["halt"]), (True, None, h.main, h.main, None))
        self.assertEqual(gh.paths, ["issues", "actions/runs/554"])

    def test_data_only_commits_are_fine(self):
        h = History()
        anchor = h.commit("data: a")
        for i in range(6):
            h.commit(f"data: capture {i}")
        out, gh = c1b(h, anchor)
        self.assertEqual((out["complete"], out["halt"], out["checked_through"], out["from"]), (True, None, h.main, anchor))
        self.assertEqual(gh.tree_reads(), 2)                                     # one segment: its two ends
        b = brief_with(out)
        self.assertTrue(b["complete"])
        self.assertEqual(b["c1b"], {"checked_through": h.main, "from": anchor, "halt": None, "gap": None})

    def test_a_squash_merge_that_touches_code_is_no_halt(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        h.commit("S1 v3.3 W2 (#1201)", code=("scripts", "tests", "00_FMOS"))
        h.commit("data: c")
        h.commit("Another (#1202)", code=(".github",))
        out, _gh = c1b(h, anchor)
        self.assertEqual((out["complete"], out["halt"]), (True, None))

    def test_a_non_squash_code_commit_is_a_halt_naming_the_first_differing_commit(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("Reviewed (#1201)", code=("scripts",))
        h.commit("data: b")
        bad = h.commit("direct push", code=("scripts", ".agents"))
        h.commit("data: c")
        h.commit("direct push 2", code=("tests",))
        out, _gh = c1b(h, anchor)
        self.assertTrue(out["complete"])
        self.assertEqual(out["halt"], {"commit": bad, "parent": h.row_of[bad]["parents"][0]["sha"], "entries": ["scripts", ".agents"], "capped": False})
        b = brief_with(out)
        self.assertEqual(b["next"][0], {"action": "HALT", "rule": "C1b", "source": "C1B", "commit": bad, "parent": out["halt"]["parent"],
                                        "entries": ["scripts", ".agents"], "verify": ["commit", "parent", "trees"], "rank": 1,
                                        "why": b["next"][0]["why"]})
        self.assertEqual((b["next"][1]["action"], b["next"][1]["pr"]), ("MERGE", 7))  # the rest keeps its order
        self.assertEqual(B.parse_body(B.render(b))["next"][0]["commit"], bad)

    def test_a_code_commit_right_after_the_anchor_and_one_before_main(self):
        for where in ("first", "last"):
            with self.subTest(where):
                h = History()
                anchor = h.commit("data: a")
                if where == "first":
                    bad = h.commit("direct", code=("00_FMOS",))
                    h.commit("data: b")
                else:
                    h.commit("data: b")
                    bad = h.commit("direct", code=("00_FMOS",))
                out, _gh = c1b(h, anchor)
                self.assertEqual(out["halt"]["commit"], bad)

    def test_a_two_parent_commit_with_a_pr_subject_is_not_a_squash_merge(self):
        h = History()
        anchor = h.commit("data: a")
        bad = h.commit("Merge pull request (#77)", code=("scripts",), merge=True)
        out, _gh = c1b(h, anchor)
        self.assertEqual(out["halt"]["commit"], bad)

    def test_past_the_search_reads_the_segment_last_commit_is_named(self):
        h = History()
        anchor = h.commit("data: a")
        for i in range(B.C1B_SEARCH_READS + 3):
            h.commit(f"data: {i}")
        h.commit("direct", code=("scripts",))
        last = h.commit("data: z")
        out, gh = c1b(h, anchor)
        self.assertEqual((out["halt"]["commit"], out["halt"]["capped"], out["halt"]["entries"]), (last, True, ["scripts"]))
        # capped: the parent is the segment START, the pair proven to differ (S1's HALT step compares parent and commit)
        self.assertEqual(out["halt"]["parent"], anchor)
        self.assertNotEqual(out["halt"]["parent"], h.row_of[last]["parents"][0]["sha"])
        self.assertLessEqual(gh.tree_reads(), B.C1B_SEARCH_READS + 3)

    def test_a_capped_halt_after_a_squash_merge_names_the_squash_merge_as_parent(self):
        h = History()
        anchor = h.commit("data: a")
        squash = h.commit("Reviewed (#1201)", code=("tests",))
        for i in range(B.C1B_SEARCH_READS + 1):
            h.commit(f"data: {i}")
        h.commit("direct", code=(".github",))
        last = h.commit("data: z")
        out, _gh = c1b(h, anchor)
        self.assertEqual((out["halt"]["commit"], out["halt"]["parent"], out["halt"]["entries"], out["halt"]["capped"]),
                         (last, squash, [".github"], True))

    def test_a_plain_halt_keeps_its_first_parent(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        bad = h.commit("direct", code=("tests",))
        h.commit("data: c")
        out, _gh = c1b(h, anchor)
        self.assertEqual((out["halt"]["commit"], out["halt"]["parent"], out["halt"]["capped"]),
                         (bad, h.row_of[bad]["parents"][0]["sha"], False))
        self.assertNotEqual(out["halt"]["parent"], anchor)


class FailClosed(unittest.TestCase):
    def test_no_previous_brief_scans_the_window_and_is_incomplete(self):
        h = History()
        h.commit("data: a")
        bad = h.commit("direct", code=("scripts",))
        h.commit("data: b")
        out, _gh = c1b(h, None)
        self.assertFalse(out["complete"])
        self.assertTrue(out["reason"].startswith("C1b:range"), out["reason"])
        self.assertEqual((out["halt"]["commit"], out["checked_through"]), (bad, h.main))   # scanned to B.main: the next build recovers
        b = brief_with(out)
        self.assertEqual((b["complete"], b["incomplete"]), (False, out["reason"]))
        self.assertEqual(b["next"][0]["commit"], bad)

    def test_a_checked_through_off_the_first_parent_chain_is_incomplete(self):
        h = History()
        for i in range(4):
            h.commit(f"data: {i}")
        out, _gh = c1b(h, h.main, c1b=sha("rewritten history"))
        self.assertEqual((out["complete"], out["reason"]), (False, "C1b:range"))
        self.assertEqual(out["from"], h.base)                                        # the whole page was scanned

    def test_an_anchor_beyond_the_window_is_incomplete(self):
        h = History()
        anchor = h.commit("data: a")
        for i in range(B.C1B_WINDOW + 2):
            h.commit(f"data: {i}")
        out, _gh = c1b(h, anchor)
        self.assertEqual((out["complete"], out["reason"]), (False, "C1b:range"))

    def test_an_edited_or_unbound_previous_brief_is_no_anchor(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        out, _gh = c1b(h, anchor, edited=True)
        self.assertEqual((out["complete"], out["reason"]), (False, "C1b:range:no_anchor:edited_outside_run"))
        issue, run = previous(anchor)
        for change, why in (({"head_sha": sha("x")}, "run_binding"), ({"path": ".github/workflows/x.yml"}, "run_binding"),
                            ({"conclusion": "failure"}, "run_not_success")):
            with self.subTest(why):
                got = B.read_c1b(Gh(h, issue, dict(run, **change)), h.main, [], NOW)
                self.assertEqual(got["reason"], f"C1b:range:no_anchor:{why}")
        foreign = dict(issue, user=dict(TB.OWNER))
        self.assertEqual(B.read_c1b(Gh(h, foreign, run), h.main, [], NOW)["reason"], "C1b:range:no_anchor:author")

    def test_a_w2_brief_without_c1b_anchors_at_its_main(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        out, _gh = c1b(h, anchor, c1b=None)
        self.assertEqual((out["complete"], out["from"]), (True, anchor))
        out, _gh = c1b(h, anchor, c1b="0" * 39)                                      # a c1b block without a usable point
        self.assertEqual(out["reason"], "C1b:range:no_anchor:no_checked_through")

    def test_an_unreadable_tree_is_incomplete_and_carries_the_anchor(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        main_tree = h.rows[0]["commit"]["tree"]["sha"]
        for kw in ({"fail": ["git/trees/"]}, {"truncated": [main_tree]}):
            with self.subTest(kw):
                out, _gh = c1b(h, anchor, **kw)
                self.assertEqual((out["complete"], out["reason"], out["checked_through"]), (False, "C1b:tree_read", anchor))
                b = brief_with(out)
                self.assertEqual((b["complete"], b["incomplete"]), (False, "C1b:tree_read"))

    def test_other_unreadable_reads(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        for fail, why in (("issues", "issues_unreadable"), ("actions/runs/", "run_unreadable"), ("commits", "commits_unreadable")):
            with self.subTest(why):
                out, _gh = c1b(h, anchor, fail=[fail])
                self.assertEqual((out["complete"], out["reason"]), (False, f"C1b:{why}"))
                self.assertNotEqual(out["checked_through"], h.main)

    def test_main_not_on_the_commit_page_is_unreadable(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        h.page = lambda: [h.row_of[anchor]]
        out, _gh = c1b(h, anchor)
        self.assertEqual((out["complete"], out["reason"], out["checked_through"]), (False, "C1b:commits_unreadable", anchor))

    def test_its_own_call_budget(self):
        h = History()
        anchor = h.commit("data: a")
        for i in range(8):
            h.commit(f"direct {i}" if i == 6 else f"data: {i}", code=("scripts",) if i == 6 else ())
        out, gh = c1b(h, anchor, max_calls=5)
        self.assertEqual((out["complete"], out["reason"], out["checked_through"], out["stop"]), (False, "C1b:budget", anchor, None))
        self.assertEqual(gh.calls, 5)

    def test_the_global_cap_stops_the_build(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        out, _gh = c1b(h, anchor, stop_on="git/trees/")
        self.assertEqual((out["complete"], out["reason"], out["stop"]), (False, "C1b:api_budget", "api_budget"))

    def test_collect_stops_every_pr_read_after_a_cap_in_c1b(self):
        def mutate(fake):
            plain = fake.get

            def get(path, params=None):
                if path == "issues":
                    fake.calls += 1
                    raise B.ApiBudget("API_BUDGET_EXHAUSTED")
                return plain(path, params)
            fake.get = get
        snap, fake, _seen = TB.CollectReplay("test_replay_builds_a_complete_brief_from_this_checkout").run_collect(mutate)
        self.assertEqual(snap["c1b"]["reason"], "C1b:api_budget")
        self.assertEqual(snap["pr"][7], {"error": "api_budget"})
        self.assertEqual(snap["errors"][0], "api_budget")
        b = B.build_brief(snap)
        self.assertEqual((b["complete"], b["incomplete"]), (False, "C1b:api_budget"))

    def test_collect_reads_c1b_before_the_pr_depth_reads(self):
        snap, fake, _seen = TB.CollectReplay("test_replay_builds_a_complete_brief_from_this_checkout").run_collect()
        self.assertEqual((snap["c1b"]["complete"], snap["c1b"]["checked_through"]), (True, fake.main))
        self.assertLess(fake.paths.index("issues"), fake.paths.index("pulls/7"))

    def test_a_missing_or_foreign_record_is_never_complete(self):
        for record in (None, "x", {}, {"complete": True, "reason": "oops"}, {"complete": "yes"}):
            with self.subTest(record):
                b = brief_with(record)
                self.assertFalse(b["complete"])
                self.assertTrue(b["incomplete"].startswith("C1b:"), b["incomplete"])
        b = brief_with({"checked_through": "x", "from": None, "halt": {"commit": "y"}, "complete": True})
        self.assertEqual(b["c1b"], {"checked_through": None, "from": None, "halt": None, "gap": None})


class CarriedHalt(unittest.TestCase):
    def test_an_unnamed_halt_of_the_previous_brief_is_carried_until_a_halt_names_it(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        old = {"commit": sha("old"), "parent": sha("old parent"), "entries": ["tests"], "capped": False}
        out, _gh = c1b(h, anchor, halt=old)
        self.assertEqual((out["complete"], out["halt"]["commit"]), (True, old["commit"]))
        named = TB.comment(90, f"S1_LANE_HALTED\nPR=- head=-\ncommit: {old['commit']}", minutes_ago=20)
        out, _gh = c1b(h, anchor, halt=old, ledger=[named])
        self.assertIsNone(out["halt"])
        out, _gh = c1b(h, anchor, halt=old, ledger=None)                           # ledger unread: carried
        self.assertEqual(out["halt"]["commit"], old["commit"])
        bad = h.commit("direct", code=("scripts",))
        out, _gh = c1b(h, anchor, halt=old)
        self.assertEqual(out["halt"]["commit"], old["commit"])                      # the older halt stays first
        out, _gh = c1b(h, anchor, halt=old, ledger=[named])
        self.assertEqual(out["halt"]["commit"], bad)


class CarriedHaltWithoutBinding(unittest.TestCase):
    """F2 (detached review of 3385c74e): the previous brief's halt is carried whenever it is a valid halt, even when that
    brief's binding fails or a later read fails; its checked_through never is. TICK HALT rule C1b re-verifies natively."""

    OLD = {"commit": sha("old"), "parent": sha("old parent"), "entries": ["tests"], "capped": False}

    def setUp(self):
        self.h = History()
        self.anchor = self.h.commit("data: a")
        self.h.commit("data: b")
        self.issue, self.run = previous(self.anchor, halt=self.OLD)

    def check(self, out, reason):
        self.assertEqual(out["halt"]["commit"], self.OLD["commit"])
        self.assertTrue(out["reason"].startswith(reason), out["reason"])
        self.assertNotEqual(out["checked_through"], self.anchor)                 # the anchor is never trusted here
        b = brief_with(out)
        self.assertEqual(b["c1b"]["halt"]["commit"], self.OLD["commit"])
        self.assertEqual((b["next"][0]["action"], b["next"][0]["source"], b["next"][0]["commit"]), ("HALT", "C1B", self.OLD["commit"]))

    def test_each_binding_failure_keeps_the_halt(self):
        cases = {"run_not_success": dict(self.run, conclusion="failure"), "run_binding": dict(self.run, head_sha=sha("x")),
                 "edited_outside_run": self.run}
        for why, run in cases.items():
            with self.subTest(why):
                issue = dict(self.issue, updated_at=TB.ts(30)) if why == "edited_outside_run" else self.issue
                out = B.read_c1b(Gh(self.h, issue, run), self.h.main, [], NOW)
                self.check(out, f"C1b:range:no_anchor:{why}")

    def test_an_unreadable_run_keeps_the_halt(self):
        out = B.read_c1b(Gh(self.h, self.issue, self.run, fail=["actions/runs/"]), self.h.main, [], NOW)
        self.assertEqual(out["checked_through"], None)
        self.check(out, "C1b:run_unreadable")

    def test_a_later_read_failure_keeps_the_halt(self):
        for fail, why in ((["commits"], "C1b:commits_unreadable"), (["git/trees/"], "C1b:tree_read")):
            with self.subTest(why):
                out = B.read_c1b(Gh(self.h, self.issue, dict(self.run, conclusion="failure"), fail=fail), self.h.main, [], NOW)
                self.check(out, why)

    def test_a_body_not_written_by_the_actions_bot_carries_neither_halt_nor_anchor(self):
        # phase 5: bot authorship is the floor (T1 author rule); a forged parent could make S1 post a false halt
        for user in (dict(TB.OWNER), {"login": "github-actions[bot]"}, dict(TB.BOT, id=1)):
            with self.subTest(user):
                out = B.read_c1b(Gh(self.h, dict(self.issue, user=user), self.run), self.h.main, [], NOW)
                self.assertIsNone(out["halt"])
                self.assertEqual(out["reason"], "C1b:range:no_anchor:author")
                self.assertNotEqual(out["checked_through"], self.anchor)
                self.assertNotEqual(out["from"], self.anchor)
                b = brief_with(out)
                self.assertFalse(any(x.get("source") == "C1B" for x in b["next"]))

    def test_a_named_or_invalid_halt_is_not_carried(self):
        named = TB.comment(90, f"S1_LANE_HALTED\nPR=- head=-\ncommit: {self.OLD['commit']}", minutes_ago=20)
        self.assertIsNone(B.read_c1b(Gh(self.h, self.issue, dict(self.run, conclusion="failure")), self.h.main, [named], NOW)["halt"])
        bad_issue, _run = previous(self.anchor, halt=dict(self.OLD, entries=["docs"]))
        self.assertIsNone(B.read_c1b(Gh(self.h, bad_issue, dict(self.run, conclusion="failure")), self.h.main, [], NOW)["halt"])


class Gap(unittest.TestCase):
    """F3: the no-anchor fallback moves checked_through past history nobody scanned: B.c1b.gap says so (owner-visible;
    S1 needs no action, the brief is already incomplete with a C1b:range reason)."""

    def test_the_fallback_publishes_a_gap(self):
        h = History()
        h.commit("data: a")
        h.commit("data: b")
        out, _gh = c1b(h, None)
        b = brief_with(out)
        self.assertEqual(b["c1b"]["gap"], {"from_unknown": True, "window": B.C1B_WINDOW, "reason": "C1b:range:no_anchor:issues=0"})
        self.assertEqual((b["complete"], b["incomplete"]), (False, "C1b:range:no_anchor:issues=0"))
        self.assertEqual(b["c1b"]["checked_through"], h.main)
        doc = B.parse_body(B.render(b))
        self.assertEqual(doc["c1b"]["gap"]["from_unknown"], True)

    def test_a_reached_anchor_or_a_failed_read_has_no_gap(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        self.assertIsNone(brief_with(c1b(h, anchor)[0])["c1b"]["gap"])
        self.assertIsNone(brief_with(c1b(h, anchor, fail=["git/trees/"])[0])["c1b"]["gap"])
        off_chain = brief_with(c1b(h, anchor, c1b=sha("rewritten"))[0])["c1b"]["gap"]           # an anchor not reached: a gap too
        self.assertEqual(off_chain, {"from_unknown": True, "window": B.C1B_WINDOW, "reason": "C1b:range"})


class Ledger(unittest.TestCase):
    def test_last_heartbeat_and_open_intents(self):
        beats = [TB.comment(60, "S1_HEARTBEAT_v1\nmain=x", minutes_ago=1500), TB.comment(61, "S1_HEARTBEAT_v1\nmain=y", minutes_ago=200),
                 TB.comment(62, "S1_HEARTBEAT_v1\nmain=z", minutes_ago=100, edited=True),          # edited: not authentic
                 TB.comment(63, "S1_HEARTBEAT_v1\nmain=z", user=TB.CODEX, minutes_ago=50)]         # foreign
        intents = [TB.comment(80, "S1_LANE_MERGE_INTENT_v1\npr: 7\nloop: " + "4" * 40, minutes_ago=90),
                   TB.comment(81, "S1_OP_INTENT_v1\nop: PUSH\npr: 8\nloop: " + "4" * 40, minutes_ago=10)]
        b = TB.brief_of(lambda w: w.update(issue_comments=beats + intents))
        self.assertEqual(b["ledger"], {"read": True, "last_heartbeat_at": TB.ts(200), "open_intents": {"count": 2, "ids": [80, 81]}})
        self.assertEqual(TB.brief_of()["ledger"], {"read": True, "last_heartbeat_at": None, "open_intents": {"count": 0, "ids": []}})
        unread = TB.brief_of(lambda w: w.update(issue_comments=beats, issue_comments_complete=False))
        self.assertEqual(unread["ledger"], {"read": False, "last_heartbeat_at": None, "open_intents": {"count": None, "ids": []}})

    def test_it_is_a_hint_only(self):
        self.assertIn("HINT ONLY", B.ledger_hint.__doc__)


class Render(unittest.TestCase):
    def test_c1b_and_ledger_survive_every_shrink_level(self):
        h = History()
        anchor = h.commit("data: a")
        h.commit("direct", code=("scripts",))
        out, _gh = c1b(h, anchor)
        import test_s1_brief_verdict_v1 as V
        for name, mutate in V.SIZES.items():
            with self.subTest(name):
                w = TB.world()
                if mutate:
                    mutate(w)
                w["c1b"] = out
                brief = B.build_brief(w)
                doc = B.parse_body(B.render(brief))
                self.assertEqual(doc["c1b"], json.loads(json.dumps(brief["c1b"])))
                self.assertEqual(doc["ledger"], json.loads(json.dumps(brief["ledger"])))
                self.assertIsNotNone(doc["c1b"]["halt"])


class RubricBlobs(unittest.TestCase):
    def test_missing_or_not_a_map_is_not_ok(self):
        w = TB.world()
        for value in ("missing", None, ["x"], "x", 7):
            with self.subTest(value):
                contract = dict(w["contract"], bootstrap_version="S1_BOOTSTRAP_v8")
                if value == "missing":
                    contract.pop("rubric_blobs")
                else:
                    contract["rubric_blobs"] = value
                v = B.brief_verdict(TB.MAIN, contract, w["pins_actual"], "bootstrap_version must be S1_BOOTSTRAP_v8.", {}, {})
                self.assertIn("3:rubric_blobs", v["reasons"])
                self.assertNotEqual(v["source"], "OK")
        ok = B.brief_verdict(TB.MAIN, dict(w["contract"], rubric_blobs={}), w["pins_actual"], "", {}, {})
        self.assertNotIn("3:rubric_blobs", ok["reasons"])                           # an empty map: nothing listed, nothing missing


if __name__ == "__main__":
    unittest.main()
