"""Fix round 6 (#2337; #173/7194141485 S1-S4, #173/7194358093 F1, #173/7194396829 S5): the C1b history ledger over
SEQUENCES of builds and publishes, not one build at a time. A fake GitHub serves one synthetic first-parent history of
main, ONE brief issue (written only through B.publish) and the brief runs; every tick builds a brief with the real
read_c1b / build_brief / render_issue / decide and publishes it with the real publish(). Fixtures only, no network.

The long-run class replays several hundred seeded ticks with read failures, budget stops, cancelled runs, publish
failures, out-of-order and concurrent publishes, owner gap acceptances (valid, forged, edited, pre-dated, wrong range)
and commit bursts, and checks the ledger invariants after EVERY tick."""
import contextlib
import copy
import io
import json
import random
import statistics
import sys
import unittest
from datetime import timedelta
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "scripts" / "governance", ROOT / "tests" / "governance"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import s1_decision_v1 as D  # noqa: E402
import s1_executor_v1 as E  # noqa: E402
import s1_tick_brief_v1 as B  # noqa: E402
import test_s1_brief_c1b_v1 as TC  # noqa: E402  (module imports: their TestCases are not collected twice)
import test_s1_decision_v1 as TD  # noqa: E402
import test_s1_tick_brief_v1 as TB  # noqa: E402

OWNER, BOT, EVE = dict(TB.OWNER), dict(TB.BOT), {"login": "eve-outsider", "id": 999, "type": "User"}
ISSUE = 3


class BuildGh:
    """The build job's reads: the brief issue as it was when the build read it, the brief runs, main's newest
    C1B_WINDOW commits, root trees. `fault` injects one failure kind."""

    def __init__(self, sim, fault):
        self.sim, self.fault, self.calls, self.trees = sim, dict(fault or {}), 0, 0
        self.issue = copy.deepcopy(sim.issue)

    def get(self, path, params=None):
        self.calls += 1
        f = self.fault
        if f.get("stop_at") == self.calls:
            raise B.ApiBudget("API_BUDGET_EXHAUSTED")
        if path == "issues":
            if f.get("issues") == "transport":
                raise OSError("boom")
            if f.get("issues") == "malformed":
                return {"message": "unreadable"}
            rows = [copy.deepcopy(self.issue)] if self.issue else []
            if f.get("issues") == "duplicate" and rows:
                rows.append(dict(rows[0], number=ISSUE + 1))
            return rows
        if path.startswith("actions/runs/"):
            if f.get("run") == "transport":
                raise OSError("boom")
            return copy.deepcopy(self.sim.runs.get(int(path.split("/")[-1]))) or {}
        if path == "commits":
            if f.get("commits"):
                raise OSError("boom")
            rows = self.sim.h.page()
            at = next(k for k, r in enumerate(rows) if r["sha"] == params["sha"])
            return rows[at:at + B.C1B_WINDOW]                         # one page of 100, from the commit asked for
        if path.startswith("git/trees/"):
            self.trees += 1
            if f.get("tree_fail_at") == self.trees:
                raise OSError("boom")
            key = path.split("/")[-1]
            entries = self.sim.h.trees[key]
            return {"sha": key, "truncated": False,
                    "tree": [{"path": d, "type": v.split(":")[0], "sha": v.split(":")[1]} for d, v in entries.items()]}
        raise AssertionError(path)


class PublishGh:
    """The publish job's reads and writes on the ONE brief issue. `view`: the issue as this publisher read it (a stale
    copy models two publishes that both read before either wrote)."""

    def __init__(self, sim, now, view=None):
        self.sim, self.now, self.view, self.writes = sim, now, view, []

    def get(self, path, params=None):
        if path == "issues":
            cur = self.view if self.view is not None else self.sim.issue
            return [copy.deepcopy(cur)] if cur else []
        if path.startswith("actions/runs/"):
            return copy.deepcopy(self.sim.runs.get(int(path.split("/")[-1]))) or {}
        raise AssertionError(path)

    def url(self, path, params=None):
        return path

    def _request(self, method, path, data=None, **kw):
        self.writes.append((method, path))
        if (method, path) == ("POST", "labels") or method == "PUT":
            return b"{}", {}
        if (method, path) == ("POST", "issues"):
            self.sim.issue = {"number": ISSUE, "user": dict(BOT), "body": data["body"], "updated_at": B.iso(self.now)}
            return json.dumps({"number": ISSUE}).encode(), {}
        if (method, path) == ("PATCH", f"issues/{ISSUE}") and "body" in data:
            self.sim.issue = dict(self.sim.issue, body=data["body"], updated_at=B.iso(self.now))
            return json.dumps(self.sim.issue).encode(), {}
        raise AssertionError((method, path))


class Sim:
    """main's history, the published issue, the runs of the brief workflow and the ledger (#1156) of one world."""

    def __init__(self, start):
        self.h, self.issue, self.runs, self.ledger = TC.History(), None, {}, []
        self.next_run, self.next_cid, self.t = 1000, 50000, start
        self.proven, self.disposed, self.halts_found, self.halts_made = set(), [], set(), set()
        self.valid_accepts = {}                                       # gap id -> creation times of VALID acceptances
        self.lines = io.StringIO()

    # ---- history
    def index(self):
        chain = [self.h.base] + [r["sha"] for r in reversed(self.h.rows)]
        return chain, {c: k for k, c in enumerate(chain)}

    def commits(self, rng, n):
        for _ in range(n):
            x = rng.random()
            if x < 0.80:
                self.h.commit(f"data: capture {len(self.h.rows)}")
            elif x < 0.95:
                self.h.commit(f"Feature (#{9000 + len(self.h.rows)})", code=(rng.choice(B.T3_TREE_DIRS),) if rng.random() < 0.7 else ())
            elif x < 0.98:
                self.halts_made.add(self.h.commit("direct push", code=("scripts",)))   # a non-squash code commit: a halt
            else:                                                       # A -> B -> A inside one segment: a halt too (A24)
                old = self.h.entries["tests"]
                self.halts_made.add(self.h.commit("direct tweak", code=("tests",)))
                self.h.entries["tests"] = old
                self.h.commit("direct revert")

    # ---- one build and its publish
    def build(self, at, fault=None, ledger=True):
        rid, self.next_run = self.next_run, self.next_run + 1
        self.runs[rid] = {"id": rid, "path": B.WORKFLOW_PATH, "repository": {"full_name": B.REPO}, "head_repository": {"full_name": B.REPO},
                          "head_branch": "main", "head_sha": self.h.main, "event": "schedule", "run_attempt": 1,
                          "status": "in_progress", "conclusion": None, "run_started_at": B.iso(at - timedelta(minutes=1)),
                          "updated_at": B.iso(at - timedelta(minutes=1))}
        gh = BuildGh(self, fault)
        record = B.read_c1b(gh, self.h.main, copy.deepcopy(self.ledger) if ledger else None, at,
                            max_calls=(fault or {}).get("max_calls", B.C1B_MAX_CALLS))
        w = TD.thin_world("SHADOW")
        w.update(main_sha=self.h.main, c1b=record, run={"id": rid, "attempt": 1, "event": "schedule"})
        w["codex_feed"] = TD.codex_feed_of(w)
        brief = B.build_brief(w)
        brief["generated_at"] = B.iso(at)
        body, decision = B.render_issue(brief)
        return {"rid": rid, "at": at, "record": record, "body": body, "decision": decision, "brief": B.parse_body(body),
                "calls": gh.calls, "trees": gh.trees, "fault": dict(fault or {})}

    def publish(self, b, at, view=None, conclusion="success"):
        """The publish job of build b at `at`; then its run ends with `conclusion`. Returns True when it wrote."""
        gh = PublishGh(self, at, view)
        with contextlib.redirect_stdout(self.lines):
            B.publish(gh, b["body"], now=at)
        wrote = any(m in ("PATCH", "POST") and p in (f"issues/{ISSUE}", "issues") for m, p in gh.writes)
        if wrote:                                                       # what this scan proved, now durable
            chain, at_of = self.index()
            rec = b["record"]
            lo, hi = at_of.get(rec.get("from"), None), at_of.get(rec.get("checked_through"), None)
            if lo is not None and hi is not None:
                self.proven.update(range(lo + 1, hi + 1))
            if rec.get("halt"):
                self.halts_found.add(rec["halt"]["commit"])
        self.end_run(b["rid"], at + timedelta(minutes=1), conclusion)
        return wrote

    def end_run(self, rid, at, conclusion):
        self.runs[rid].update(status="completed", conclusion=conclusion, updated_at=B.iso(at))

    def published(self):
        return B.parse_body(self.issue["body"]) if self.issue else None

    # ---- the owner and S1 on #1156
    def post(self, body, at, user=OWNER, edited=False):
        self.next_cid += 1
        self.ledger.append({"id": self.next_cid, "user": dict(user), "body": body, "created_at": B.iso(at),
                            "updated_at": B.iso(at + timedelta(minutes=1) if edited else at)})

    def accept(self, gap, at, kind="valid"):
        frm = gap["from"] or "-"
        if kind == "wrong_from":
            frm = TC.sha(f"other{self.next_cid}")
        when = B.stamp(gap["detected_at"]) - timedelta(minutes=1) if kind == "predated" else at
        self.post(f"{B.GAP_ACCEPTED}\nfrom: {frm}\nto: {gap['to']}", when, EVE if kind == "forged" else OWNER, edited=kind == "edited")
        if kind == "valid":
            self.valid_accepts.setdefault(gap["id"], []).append(when)

    def name_halt(self, at):
        brief = self.published()
        halt = ((brief or {}).get("c1b") or {}).get("halt")
        if halt:
            self.post(f"S1_LANE_HALTED\nPR=- head=-\nreason: unreviewed_code_on_main\ncommit: {halt['commit']}", at)


def gap_range(g, at_of):
    lo = -1 if g["from"] is None else at_of.get(g["from"], -1)
    return lo, at_of.get(g["to"], -1)


class Invariants:
    """The per-tick assertions (ChatGPT's acceptance criteria 1-5, 9, 10)."""

    def check_build(self, case, sim, b):
        rec, brief, d = b["record"], b["brief"], b["decision"]
        c1b = brief["c1b"]
        case.assertLessEqual(b["calls"], B.C1B_MAX_CALLS)                                     # 10: bounded calls
        case.assertLessEqual(len(b["body"]), 65000)                                          # 10: bounded brief
        ids = [g["id"] for g in c1b["gaps"]]
        case.assertEqual(len(ids), len(set(ids)))                                            # 1: never a duplicate range
        case.assertTrue(len(c1b["gaps"]) <= B.C1B_MAX_GAPS or brief["incomplete"] == "C1b:gaps_overflow")   # 10: surfaced, never cut
        fenced = bool(c1b["gaps"] or c1b["open"] or c1b["carry"] == "UNKNOWN" or not rec.get("complete"))
        case.assertEqual(bool(c1b["fence"]), fenced)
        if fenced or not brief["complete"]:
            case.assertNotEqual(d["action"], "MERGE")                                           # 9: no merge while any gap is open
            case.assertEqual([e for e in brief["next"] if e["action"] in B.MERGE_ACTIONS], [])   # S4: not for the ChatGPT lane either
            case.assertFalse(any(x.get("ready") for x in brief["claude_slots"]))
            health = E.health_state(d["result"], [], None, None, (), d.get("unverified") or [])
            if d["action"] == "NOOP":
                case.assertNotEqual(health, "OK", d["result"])                                   # 5: unknown is never OK
        if c1b["checked_through"]:
            case.assertIn(c1b["checked_through"], sim.index()[1])                             # never a commit off main's chain
        if rec.get("open"):
            case.assertEqual(rec["open"]["from"], rec["checked_through"])                    # 2: the proven point and the open rest agree

    def check_publish(self, case, sim, before, after, built):
        """1, 4: every gap of the brief published before this tick is still published, or an owner disposition that
        satisfies the rule from first principles (a VALID acceptance posted after its detection) cleared it. Every
        published gap is either one of those, unchanged, or newly detected by a build of this tick."""
        old = {g["id"]: g for g in ((before or {}).get("c1b") or {}).get("gaps") or []}
        new = {g["id"]: g for g in ((after or {}).get("c1b") or {}).get("gaps") or []}
        for gid, g in old.items():
            if gid not in new:
                ok = [t for t in sim.valid_accepts.get(gid, []) if t >= B.stamp(g["detected_at"])]
                case.assertTrue(ok, f"gap {gid} left the ledger without an owner disposition")
                sim.disposed.append(gap_range(g, sim.index()[1]))
        for gid, g in new.items():
            case.assertTrue(gid not in old and g["detected_at"] in {B.iso(b["at"]) for b in built} or old.get(gid) == g,
                            f"gap {gid} is neither carried unchanged nor newly found")

    def check_coverage(self, case, sim):
        """1, 2: every first-parent commit up to the published checked_through was proven by a published scan, or lies
        in a published gap, or in a range the owner disposed of. checked_through never skips unproven history."""
        brief = sim.published()
        c1b = (brief or {}).get("c1b") or {}
        chain, at_of = sim.index()
        hi = at_of.get(c1b.get("checked_through"))
        if hi is None:
            return
        ranges = [gap_range(g, at_of) for g in c1b.get("gaps") or []] + sim.disposed
        for k in range(0, hi + 1):
            if k not in sim.proven and not any(lo < k <= to for lo, to in ranges):
                case.fail(f"commit #{k} ({chain[k][:8]}) is at or before checked_through and was never proven, nor in a gap")


class Sequences(unittest.TestCase, Invariants):
    """Named correlated multi-tick scenarios."""

    def setUp(self):
        self.sim = Sim(TB.NOW - timedelta(hours=40))

    def tick(self, fault=None, conclusion="success", n=3, ledger=True):
        sim = self.sim
        sim.t += timedelta(hours=1)
        for _ in range(n):
            sim.h.commit(f"data: tick {len(sim.h.rows)}")
        before = sim.published()
        b = sim.build(sim.t, fault, ledger)
        self.check_build(self, sim, b)
        wrote = sim.publish(b, sim.t + timedelta(minutes=1), conclusion=conclusion)
        self.check_publish(self, sim, before, sim.published(), [b])
        self.check_coverage(self, sim)
        return b, wrote

    def gaps(self):
        return [(g["from"], g["to"]) for g in self.sim.published()["c1b"]["gaps"]]

    def test_a_read_failure_never_loses_a_carried_gap_across_ticks(self):
        self.tick()                                                   # the first brief: no predecessor, a gap to the window's start
        first = self.gaps()
        self.assertEqual(len(first), 1)
        for fault in ({"issues": "transport"}, {"issues": "malformed"}, {"issues": "duplicate"}, {"run": "transport"},
                      {"max_calls": 0}, {"max_calls": 1}, {"stop_at": 1}, {"stop_at": 2}):
            with self.subTest(fault):
                b, wrote = self.tick(fault)
                self.assertFalse(wrote, fault)                           # the published brief is conserved: this build never carried it
                self.assertEqual(self.gaps(), first)
        b, wrote = self.tick()                                        # the next readable tick carries it, unchanged
        self.assertTrue(wrote)
        self.assertEqual(self.gaps(), first)

    def test_two_gaps_stay_two_and_accepting_one_leaves_the_other(self):
        self.tick(n=B.C1B_WINDOW + 20)                                # longer than one window: each lost anchor is its own range
        self.tick(conclusion="cancelled")                             # the next build cannot anchor on a cancelled run
        self.tick()
        gaps = self.sim.published()["c1b"]["gaps"]
        self.assertEqual(len(gaps), 2)
        self.assertNotEqual(gaps[0]["to"], gaps[1]["to"])
        self.sim.accept(gaps[0], self.sim.t + timedelta(minutes=5))
        b, _w = self.tick()
        self.assertEqual(self.gaps(), [(gaps[1]["from"], gaps[1]["to"])])
        self.assertEqual(b["record"]["cleared"], [{"id": gaps[0]["id"], "by": f"owner:{self.sim.next_cid}"}])
        self.assertNotEqual(b["decision"]["action"], "MERGE")
        self.sim.accept(gaps[1], self.sim.t + timedelta(minutes=5))
        unread = []
        for _ in range(10):                                           # liveness: the capped rest of the long window is resumed,
            b, _w = self.tick()                                       # C1B_SEARCH_READS commits per long segment per build
            unread.append((b["brief"]["c1b"]["open"] or {}).get("unread", 0))
            if not unread[-1]:
                break
        self.assertEqual(unread, sorted(unread, reverse=True))        # monotonic progress, never a stall
        self.assertEqual((self.gaps(), unread[-1], b["decision"]["action"]), ([], 0, "MERGE"))   # no gap, no open rest: the lane decides again

    def test_forged_edited_predated_and_wrong_acceptances_clear_nothing(self):
        self.tick()
        gap = self.sim.published()["c1b"]["gaps"][0]
        for kind in ("forged", "edited", "predated", "wrong_from"):
            self.sim.accept(gap, self.sim.t + timedelta(minutes=5), kind)
            self.tick()
            self.assertEqual(self.gaps(), [(gap["from"], gap["to"])], kind)
        self.tick(ledger=False)                                       # and an unread ledger accepts nothing either
        self.assertEqual(len(self.gaps()), 1)

    def test_an_earlier_acceptance_never_clears_a_range_found_later(self):
        self.tick()
        gap = self.sim.published()["c1b"]["gaps"][0]
        self.sim.accept(gap, self.sim.t + timedelta(minutes=5))
        self.tick()
        self.assertEqual(self.gaps(), [])
        # the SAME range found again later (here: a predecessor whose binding fails, at an unchanged main) is a new item
        again = B.c1b_gap(gap["from"], gap["to"], gap["reason"], gap["window"], B.iso(self.sim.t + timedelta(hours=2)))
        self.assertIsNone(B.gap_acceptance(again, self.sim.ledger))

    def test_delayed_and_out_of_order_publishes_never_replace_a_newer_carried_brief(self):
        sim = self.sim
        self.tick()
        sim.t += timedelta(hours=1)
        sim.h.commit("data: x")
        a = sim.build(sim.t)                                          # build A
        sim.h.commit("data: y")
        b = sim.build(sim.t + timedelta(minutes=10))                  # build B starts before A's publish: it read the same brief
        before = sim.published()
        self.assertTrue(sim.publish(b, sim.t + timedelta(minutes=11)))   # B publishes first
        self.assertFalse(sim.publish(a, sim.t + timedelta(minutes=12)))  # A's late publish never replaces it (it never carried B)
        self.check_publish(self, sim, before, sim.published(), [a, b])
        self.check_coverage(self, sim)
        self.assertEqual(sim.published()["run_id"], b["rid"])
        self.assertIn("c1b_predecessor_not_carried", sim.lines.getvalue())
        sim.t += timedelta(minutes=30)
        self.tick()

    def test_two_publishes_that_read_the_same_brief_both_write_and_the_survivor_is_complete(self):
        sim = self.sim
        self.tick()
        sim.t += timedelta(hours=1)
        before = sim.published()
        stale = copy.deepcopy(sim.issue)
        sim.h.commit("data: x")
        a = sim.build(sim.t)
        sim.h.commit("data: y")
        b = sim.build(sim.t + timedelta(minutes=10))
        self.assertTrue(sim.publish(a, sim.t + timedelta(minutes=11), view=stale))
        self.assertTrue(sim.publish(b, sim.t + timedelta(minutes=12), view=stale))   # not a CAS: both read the same brief
        self.check_publish(self, sim, before, sim.published(), [a, b])
        self.check_coverage(self, sim)
        for _ in range(3):
            self.tick()                                                # the next builds resume from the survivor

    def test_s5_a_missing_range_and_a_capped_transient_in_one_tick(self):
        """#173/7194396829 S5: the anchor is absent from the page AND a segment with equal ends exceeds the per-segment
        cap, with an A -> B -> A change past the cap. Accepting the missing range alone must not mark the capped rest
        proven; the next scan resumes from the contiguous proven point and finds the halt."""
        sim = self.sim
        h = sim.h
        h.commit("Feature (#1)")
        for k in range(B.C1B_SEARCH_READS + 2):
            h.commit(f"data: {k}")
        old = h.entries["tests"]
        bad = h.commit("direct tweak", code=("tests",))               # past the cap, undone below: equal segment ends
        h.entries["tests"] = old
        h.commit("direct revert")
        for k in range(3):
            h.commit(f"data: tail {k}")
        sim.t += timedelta(hours=1)
        b = sim.build(sim.t)                                          # no predecessor: the window scan
        self.check_build(self, sim, b)
        rec = b["record"]
        self.assertEqual([(g["from"], g["to"]) for g in rec["gaps"]], [(None, h.base)])   # the history before the window
        self.assertEqual(rec["open"]["reason"], "C1b:capped_equal_ends")                # AND, separately, the capped rest
        self.assertNotEqual(rec["checked_through"], h.main)
        self.assertIsNone(rec["halt"])
        self.assertTrue(sim.publish(b, sim.t + timedelta(minutes=1)))
        sim.accept(rec["gaps"][0], sim.t + timedelta(minutes=5))      # the owner accepts the missing range only
        b2, _w = self.tick(n=0)
        self.assertEqual(b2["brief"]["c1b"]["gaps"], [])
        self.assertNotEqual(b2["decision"]["action"], "MERGE")         # the capped rest still blocks
        self.assertEqual(b2["record"]["halt"]["commit"], bad)          # and the resumed scan finds the transient change

    def test_the_c1b_budget_never_stalls_the_brief(self):
        """F1: a backlog of 5 segments x 15 data commits since the anchor (79 commits, > 78 tree reads on main's real
        history) completes within C1B_MAX_CALLS, and a budget stop is bounded progress: complete, no merge, resumed."""
        sim = self.sim
        self.tick()
        gaps = self.sim.published()["c1b"]["gaps"]
        sim.accept(gaps[0], sim.t + timedelta(minutes=5))
        for s in range(5):
            for i in range(15):
                sim.h.commit(f"data: capture {s}.{i}")
            sim.h.commit(f"Some feature (#{9100 + s})")
        b, _w = self.tick(n=0)
        self.assertTrue(b["brief"]["complete"])
        self.assertEqual(b["brief"]["c1b"]["checked_through"], sim.h.main)
        self.assertGreater(b["calls"], 60)                            # the old budget would have stopped here
        streak = 0
        for k in range(6):                                            # a tiny budget every tick: progress, never a stall
            for i in range(10):
                sim.h.commit(f"data: more {k}.{i}")
            b, _w = self.tick({"max_calls": 12}, n=0)
            self.assertTrue(b["brief"]["complete"], b["brief"]["incomplete"])
            streak = streak + 1 if b["brief"]["c1b"]["open"] else 0
        b, _w = self.tick(n=0)                                        # a full budget catches up at once
        self.assertEqual((b["brief"]["c1b"]["open"], b["decision"]["action"]), (None, "MERGE"))

    def test_every_window_shape_fits_the_c1b_budget(self):
        """F1, proven by construction (every key c1b_scan reads is the base tree or a chain commit's tree, memoised) and
        measured here on the costliest shapes: a full window costs at most 3 + C1B_WINDOW + 1 calls."""
        shapes = {"all data": lambda h, i: h.commit(f"data {i}"), "squash every other": lambda h, i: h.commit(f"F (#{i})" if i % 2 else f"data {i}"),
                  "squash every third": lambda h, i: h.commit(f"F (#{i})" if i % 3 == 0 else f"data {i}"),
                  "code squashes": lambda h, i: h.commit(f"F (#{i})", code=(B.T3_TREE_DIRS[i % 5],)) if i % 2 else h.commit(f"data {i}")}
        for name, make in shapes.items():
            for anchored in (True, False):
                with self.subTest(name=name, anchored=anchored):
                    h = TC.History()
                    anchor = h.commit("data: anchor")
                    for i in range(B.C1B_WINDOW - 1 if anchored else B.C1B_WINDOW + 20):
                        make(h, i)
                    out, gh = TC.c1b(h, anchor if anchored else None)
                    self.assertLessEqual(gh.calls, 3 + B.C1B_WINDOW + 1)
                    self.assertLessEqual(3 + B.C1B_WINDOW + 1, B.C1B_MAX_CALLS)
                    self.assertIsNone(out["stop"])
                    self.assertNotEqual(out["reason"], "C1b:budget")


class LedgerRules(unittest.TestCase):
    """The single rules of the ledger, one by one (each is also exercised by the sequences above)."""

    def published(self, main, c1b_block, minutes_ago=65):
        brief = B.build_brief(dict(TB.world(), main_sha=main, run={"id": 554, "attempt": 1, "event": "schedule"},
                                   c1b={"checked_through": main, "from": main, "complete": True}))
        brief["c1b"] = dict(brief["c1b"], **c1b_block)
        brief["generated_at"] = TB.ts(minutes_ago)
        issue = {"number": ISSUE, "user": dict(BOT), "body": B.render(brief), "updated_at": TB.ts(minutes_ago - 1)}
        run = {"id": 554, "path": B.WORKFLOW_PATH, "repository": {"full_name": B.REPO}, "head_branch": "main", "head_sha": main,
               "status": "completed", "conclusion": "success", "run_started_at": TB.ts(minutes_ago + 5), "updated_at": TB.ts(minutes_ago - 5)}
        return issue, run

    def test_a_fix_round_5_brief_migrates_its_single_gap_conservatively(self):
        h = TC.History()
        main = h.commit("data: a")
        h.commit("data: b")
        legacy = {"from_unknown": True, "window": 100, "reason": "C1b:range", "to": TC.sha("old"), "carried": True}
        issue, run = self.published(main, {"gap": legacy})
        brief = B.parse_body(issue["body"])
        brief["c1b"].pop("gaps")                                      # exactly main's/fix round 5's shape: no ledger list
        issue["body"] = B.render(brief)
        out = B.read_c1b(TC.Gh(h, issue, run), h.main, [], TB.NOW)
        self.assertEqual([(g["from"], g["to"], g["detected_at"]) for g in out["gaps"]], [(None, TC.sha("old"), TB.ts(65))])
        # a record in that shape (tests, a rollback) migrates too, dated at the build (no detection time is known)
        block, _r = B.c1b_block({"checked_through": main, "from": main, "complete": True, "gap": legacy}, TB.NOW)
        self.assertEqual([(g["from"], g["to"], g["detected_at"]) for g in block["gaps"]], [(None, TC.sha("old"), B.iso(TB.NOW))])

    def test_an_unreadable_gap_item_is_carried_as_an_unbounded_gap(self):
        h = TC.History()
        main = h.commit("data: a")
        h.commit("data: b")
        good = B.c1b_gap(TC.sha("f"), TC.sha("t"), "C1b:range", 100, TB.ts(65))
        for bad in ({"to": TC.sha("x")}, "garbage", dict(good, id="tampered"), dict(good, window="100")):
            with self.subTest(bad=bad):
                issue, run = self.published(main, {"gaps": [good]})
                brief = B.parse_body(issue["body"])
                brief["c1b"]["gaps"] = [good, bad]
                issue["body"] = B.render(brief)
                out = B.read_c1b(TC.Gh(h, issue, run), h.main, [], TB.NOW)
                self.assertEqual(out["gaps"][0], good)
                self.assertEqual((out["gaps"][1]["from"], out["gaps"][1]["reason"]), (None, "C1b:gap_unreadable"))
                self.assertEqual(out["gaps"][1]["to"], bad.get("to") if isinstance(bad, dict) else main)   # what it names, else that brief's main
        issue, run = self.published(main, {"gaps": "not a list"})
        self.assertEqual([(g["from"], g["to"]) for g in B.read_c1b(TC.Gh(h, issue, run), h.main, [], TB.NOW)["gaps"]], [(None, main)])

    def test_more_gaps_than_the_bound_are_surfaced_never_cut(self):
        h = TC.History()
        main = h.commit("data: a")
        h.commit("data: b")
        many = [B.c1b_gap(None, TC.sha(f"g{k}"), "C1b:range", 100, TB.ts(65)) for k in range(B.C1B_MAX_GAPS + 1)]
        issue, run = self.published(main, {"gaps": many})
        out = B.read_c1b(TC.Gh(h, issue, run), h.main, [], TB.NOW)
        self.assertEqual((len(out["gaps"]), out["complete"], out["reason"]), (B.C1B_MAX_GAPS + 1, False, "C1b:gaps_overflow"))
        brief = TC.brief_with(out)
        self.assertEqual((len(brief["c1b"]["gaps"]), brief["incomplete"]), (B.C1B_MAX_GAPS + 1, "C1b:gaps_overflow"))
        self.assertLess(len(B.render(brief)), B.MAX_BODY)

    def test_a_halt_behind_a_carried_halt_is_never_checkpointed_over(self):
        h = TC.History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        second = h.commit("direct push", code=("scripts",))
        h.commit("data: c")
        older = {"commit": TC.sha("old"), "parent": TC.sha("old parent"), "entries": ["tests"], "capped": False}
        out, _gh = TC.c1b(h, anchor, halt=older)
        self.assertEqual(out["halt"], older)                          # the older, unnamed halt stays first
        self.assertEqual(out["checked_through"], h.row_of[second]["parents"][0]["sha"])   # the proof stops BEFORE the second
        named = [TB.comment(70, f"S1_LANE_HALTED\nPR=- head=-\ncommit: {older['commit']}", TB.OWNER, 5)]
        again, _gh = TC.c1b(h, out["checked_through"], ledger=named)
        self.assertEqual(again["halt"]["commit"], second)             # found once the older one is named

    def test_the_publish_fence_reads_the_carried_brief_by_its_run(self):
        sim = Sim(TB.NOW - timedelta(hours=5))
        sim.t += timedelta(hours=1)
        sim.h.commit("data: a")
        first = sim.build(sim.t)
        self.assertTrue(sim.publish(first, sim.t + timedelta(minutes=1)))
        self.assertIsNone(first["record"]["prev"])                     # the very first brief creates the issue
        sim.t += timedelta(hours=1)
        nxt = sim.build(sim.t)
        self.assertEqual(nxt["record"]["prev"], {"run_id": first["rid"], "issue": ISSUE})
        forged = B.parse_body(nxt["body"])
        forged["c1b"]["prev"] = {"run_id": first["rid"] + 1, "issue": ISSUE}
        self.assertFalse(sim.publish(dict(nxt, body=B.render_issue(forged)[0]), sim.t + timedelta(minutes=1)))
        self.assertTrue(sim.publish(nxt, sim.t + timedelta(minutes=2)))


class ExecutorWorkflowWatch(unittest.TestCase):
    """F2: the watchdog reads the executor's OWN workflow and skips runs that had no decision (NO_DECISION)."""

    def test_the_newest_executor_run_with_a_decision_is_the_one_watched(self):
        line = lambda state, result: "2026-11-26T10:00:00Z S1_EXECUTOR_HEALTH " + json.dumps({"v": 1, "state": state, "result": result})
        runs = [{"id": 30, "event": "workflow_run", "status": "completed", "conclusion": "success", "created_at": TB.ts(10)},
                {"id": 29, "event": "workflow_run", "status": "completed", "conclusion": "skipped", "created_at": TB.ts(20)},
                {"id": 28, "event": "workflow_run", "status": "completed", "conclusion": "success", "created_at": TB.ts(30)},
                {"id": 27, "event": "schedule", "status": "completed", "conclusion": "success", "created_at": TB.ts(40)}]
        logs = {30: line("UNVERIFIED", "NO_DECISION(published_run=5)"), 28: line("OK", "WOULD_MERGE(pr=7)")}

        class Gh:
            reads = []

            def get(self, path, params=None):
                self.reads.append(path)
                assert path == f"actions/workflows/{Path(B.EXECUTOR_WORKFLOW_PATH).name}/runs", path
                return {"workflow_runs": runs}

            def pages(self, path, params=None, key=None, max_pages=30):
                self.reads.append(path)
                rid = int(path.split("/")[2])
                return [{"id": 9000 + rid, "name": "execute", "status": "completed", "conclusion": "success", "run_id": rid}], True

            def text(self, path):
                self.reads.append(path)
                return logs[int(path.split("/")[2]) - 9000]
        doc = B.read_executor_watch(Gh(), None)
        self.assertEqual([(r["run"], r["publish"], r.get("health")) for r in doc["runs"]], [(30, "none", "UNVERIFIED"), (28, "success", "OK")])
        self.assertEqual(B.executor_watch(doc, "SHADOW", TB.NOW)["state"], "OK")
        self.assertEqual(doc["listed"], 2)                             # skipped runs and other events are not executor runs


class SingleRuleClosers(unittest.TestCase):
    """Fix round 6 mutants Q17, Q19, Q23, Q24 survived the sequences: each rule on its own."""

    def test_no_claude_slot_is_ready_while_fenced(self):
        h = TC.History()
        anchor = h.commit("data: a")
        h.commit("data: b")
        clean, _gh = TC.c1b(h, anchor)
        def slots(record):
            w = TD.thin_world("SHADOW")
            TD.no_codex(w)
            w.update(c1b=record, codex_feed=TD.codex_feed_of(w))
            return B.build_brief(w)["claude_slots"]
        self.assertTrue(slots(clean) and all(x["ready"] for x in slots(clean)))            # the control: ready without a fence
        gapped = dict(clean, gaps=[B.c1b_gap(None, TC.sha("g"), "C1b:range", 100, TB.ts(65))])
        self.assertTrue(slots(gapped) and not any(x["ready"] for x in slots(gapped)))       # listed (no review request), never ready

    def test_a_listed_gap_alone_stops_the_decision(self):
        d, brief = TD.decide()
        self.assertEqual(d["action"], "MERGE")
        brief = copy.deepcopy(brief)
        brief["c1b"]["gaps"] = [B.c1b_gap(None, TC.sha("g"), "C1b:range", 100, TB.ts(65))]
        brief["c1b"]["fence"], brief["c1b"]["gap"] = [], None                 # even a brief whose fence and summary were dropped
        d = D.decide(brief)
        self.assertEqual(d["action"], "NOOP")
        self.assertIn("lane:C1b:history_gap", d["skipped"])

    def test_a_stale_native_main_health_is_unverified_never_ok(self):
        import test_s1_executor_v1 as TE
        stale = lambda w, g, n: [r.update(updated_at=TB.ts(30 * 60)) for r in w["health_runs"]]
        out, gh, _n, d = TE.execute(mode="SHADOW", mutate=TE.BEAT, live=stale)
        self.assertEqual((d["action"], gh.writes), ("MERGE", []))
        self.assertIn("lane:C7:main_health:main_health_stale", out["result"])
        self.assertEqual(out["health"], "UNVERIFIED")

    def test_the_main_health_window_is_proven_as_its_scope(self):
        run = {"id": 1}
        self.assertTrue(B.health_window_ok([run] * 100, False))                # a full newest page (max_pages=1 says "incomplete")
        self.assertTrue(B.health_window_ok([run] * 5, True))                   # a short page pages() found consistent
        self.assertFalse(B.health_window_ok([run] * 5, False))                 # a short page that is not: unread
        self.assertFalse(B.health_window_ok([], True))
        self.assertFalse(B.health_window_ok(None, True))


LONG_RUN_TICKS, LONG_RUN_SEED = 300, 20261126


class LongRun(unittest.TestCase, Invariants):
    """ChatGPT's acceptance criteria over LONG_RUN_TICKS seeded ticks. The metrics of the run are printed as one line
    (S1_C1B_LONG_RUN) and recorded in the dossier."""

    def test_a_seeded_long_run(self):
        rng = random.Random(LONG_RUN_SEED)
        sim = Sim(TB.NOW - timedelta(hours=LONG_RUN_TICKS + 30))
        calls, sizes, gap_counts, opens, faults, merges, max_streak, streak = [], [], [], [], {}, 0, 0, 0
        clean_incomplete = 0
        for tick in range(LONG_RUN_TICKS + 12):
            final = tick >= LONG_RUN_TICKS                             # the last ticks: no fault, the owner accepts every gap
            sim.t += timedelta(hours=1)
            sim.commits(rng, 0 if final else (rng.randint(40, 130) if rng.random() < 0.04 else rng.randint(2, 14)))
            sim.name_halt(sim.t - timedelta(minutes=20))               # S1 names the halt of the published brief (v9 HALT)
            pub = sim.published()
            for g in (pub or {}).get("c1b", {}).get("gaps", []) if pub else []:
                x = rng.random()
                if final or x < 0.12:
                    sim.accept(g, sim.t - timedelta(minutes=10))
                elif x < 0.20:
                    sim.accept(g, sim.t - timedelta(minutes=10), rng.choice(["forged", "edited", "predated", "wrong_from"]))
            if not final and rng.random() < 0.01 and sim.issue:        # the owner edits the brief issue (timestamp only)
                sim.issue["updated_at"] = B.iso(sim.t - timedelta(minutes=5))
            kind = None if final else rng.choices(
                ["none", "issues", "malformed", "duplicate", "run", "commits", "tree", "budget", "stop", "ledger", "cancel", "pubfail", "order", "concurrent"],
                [62, 4, 2, 2, 3, 2, 4, 6, 3, 3, 3, 2, 2, 2])[0]
            kind = None if kind == "none" else kind
            faults[kind or "none"] = faults.get(kind or "none", 0) + 1
            fault = {"issues": {"issues": "transport"}, "malformed": {"issues": "malformed"}, "duplicate": {"issues": "duplicate"},
                     "run": {"run": "transport"}, "commits": {"commits": True}, "tree": {"tree_fail_at": rng.randint(1, 30)},
                     "budget": {"max_calls": rng.randint(0, 40)}, "stop": {"stop_at": rng.randint(1, 40)}}.get(kind)
            before = sim.published()
            built = [sim.build(sim.t, fault, ledger=kind != "ledger")]
            if kind in ("order", "concurrent"):
                stale = copy.deepcopy(sim.issue)
                sim.h.commit(f"data: between {tick}")
                built.append(sim.build(sim.t + timedelta(minutes=10)))
                if kind == "order":                                    # the second build publishes first, the first one late
                    sim.publish(built[1], sim.t + timedelta(minutes=11))
                    sim.publish(built[0], sim.t + timedelta(minutes=12))
                else:                                                  # both publishers read the brief before either wrote
                    sim.publish(built[0], sim.t + timedelta(minutes=11), view=stale)
                    sim.publish(built[1], sim.t + timedelta(minutes=12), view=stale)
            elif kind == "pubfail":
                sim.end_run(built[0]["rid"], sim.t + timedelta(minutes=2), "failure")   # the publish job failed before its write
            else:
                sim.publish(built[0], sim.t + timedelta(minutes=1), conclusion="cancelled" if kind == "cancel" else "success")
            for b in built:
                self.check_build(self, sim, b)
                calls.append(b["calls"])
                sizes.append(len(b["body"]))
                merges += b["decision"]["action"] == "MERGE"
            self.check_publish(self, sim, before, sim.published(), built)
            self.check_coverage(self, sim)
            gap_counts.append(len(sim.published()["c1b"]["gaps"]))
            opens.append((sim.published()["c1b"]["open"] or {}).get("unread", 0))
            # 8: while history is readable (no fault this tick) the brief is never incomplete for long
            clean = kind is None
            streak = streak + 1 if clean and not built[0]["brief"]["complete"] else 0
            clean_incomplete += clean and not built[0]["brief"]["complete"]
            max_streak = max(max_streak, streak)
        self.assertLessEqual(max_streak, 1)
        # 8: liveness after the last fault: no gap, no open rest, no unnamed halt: the lane decides a merge again
        last = sim.published()
        self.assertEqual((last["c1b"]["gaps"], last["c1b"]["open"], last["complete"]), ([], None, True))
        self.assertEqual(D.decide(last)["action"], "MERGE")
        self.assertGreater(merges, 0)
        # 1, 2: every injected non-squash code change was found as a halt, or lies in a range the owner disposed of
        chain, at_of = sim.index()
        for c in sim.halts_made:
            self.assertTrue(c in sim.halts_found or any(lo < at_of[c] <= hi for lo, hi in sim.disposed), c[:8])
        q = lambda xs, p: sorted(xs)[min(len(xs) - 1, int(p * len(xs)))]
        print(f"S1_C1B_LONG_RUN seed={LONG_RUN_SEED} ticks={LONG_RUN_TICKS}+12 builds={len(calls)} commits={len(chain)} "
              f"calls_max={max(calls)} calls_p50={q(calls, .5)} calls_p95={q(calls, .95)} bytes_max={max(sizes)} bytes_p50={int(statistics.median(sizes))} "
              f"gaps_max={max(gap_counts)} open_unread_max={max(opens)} halts_made={len(sim.halts_made)} halts_found={len(sim.halts_found)} "
              f"merges_decided={merges} incomplete_clean_streak_max={max_streak} clean_incomplete={clean_incomplete} "
              f"faults={json.dumps(faults, sort_keys=True, separators=(',', ':'))}")


if __name__ == "__main__":
    unittest.main()
