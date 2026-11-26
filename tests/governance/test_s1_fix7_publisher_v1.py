"""Fix round 7 (#2337; Bridge #173/7196477628 R6-SH1..R6-SH4): the ONE serialized brief writer, the exact predecessor
tuple, the C1b fence before the rank and the cut (with a sustained high-load liveness run), and the owner's gap
acceptance bound to GitHub's native edit record. Fixtures only, no network.

R6-SH1 is a property of GitHub's concurrency groups plus publish(). SerializedWriterModel enumerates EVERY interleaving
of two brief runs that the concurrency configuration of the workflow file on disk allows (job-level groups make one
job's events contiguous against the other jobs of that group; a workflow-level group makes the whole run contiguous)
and drives the real build/read_c1b/publish code through each one, checking the ledger oracle after EACH acknowledged
write. At 990af084 (publish in no group, the two writes unserialized) it finds the interleaving that erases a newly
found halt; here no allowed interleaving does."""
import copy
import hashlib
import itertools
import json
import random
import sys
import unittest
from datetime import timedelta
from pathlib import Path

import yaml

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "scripts" / "governance", ROOT / "tests" / "governance"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import s1_decision_v1 as D  # noqa: E402
import s1_tick_brief_v1 as B  # noqa: E402
import test_s1_brief_c1b_v1 as TC  # noqa: E402
import test_s1_c1b_ledger_v1 as TL  # noqa: E402
import test_s1_tick_brief_v1 as TB  # noqa: E402

NOW = TB.NOW
WORKFLOW = yaml.safe_load((ROOT / B.WORKFLOW_PATH).read_text(encoding="utf-8"))


def block_sha(body):
    return hashlib.sha256((B.brief_block(body) or "").encode("utf-8")).hexdigest()


class StaleGh:
    """One publisher: issues read at its pub_read event (a snapshot), writes land on the live issue at pub_write."""

    def __init__(self, sim, snapshot):
        self.sim, self.snapshot, self.writes = sim, snapshot, []

    def get(self, path, params=None):
        if path == "issues":
            return [copy.deepcopy(self.snapshot)] if self.snapshot else []
        if path.startswith("actions/runs/"):
            return copy.deepcopy(self.sim.runs.get(int(path.split("/")[-1]))) or {}
        raise AssertionError(path)

    def url(self, path, params=None):
        return path

    def _request(self, method, path, data=None, **kw):
        self.writes.append((method, path))
        if method == "PATCH" and "body" in (data or {}):
            self.sim.issue = dict(self.sim.issue, body=data["body"], updated_at=B.iso(self.sim.t))
        return b"{}", {}


def groups(doc):
    """(workflow-level group or None, {job: job-level group or None}) of a workflow document."""
    wl = (doc.get("concurrency") or {}).get("group") if isinstance(doc.get("concurrency"), dict) else doc.get("concurrency")
    jobs = {}
    for name, job in doc["jobs"].items():
        c = job.get("concurrency")
        jobs[name] = c.get("group") if isinstance(c, dict) else c
    return wl, jobs


class SerializedWriterModel(unittest.TestCase):
    """R6-SH1: every interleaving the workflow's concurrency configuration allows, both build orders' outcomes, with a
    halt (a direct A -> B -> A tweak and revert) that only the NEWER build's range contains."""

    EVENTS = (("build", "read"), ("publish", "read"), ("publish", "write"))

    def allowed(self, order, doc):
        """Does `order` (a sequence of (run, job, step)) respect the concurrency groups of `doc`? The older run's build
        reads first (its build job was queued first and builds are serialised in every version of the file)."""
        wl, jobs = groups(doc)
        def blocks(key):
            seen, last = set(), None
            for ev in order:
                k = key(ev)
                if k is None:
                    continue
                if k != last and k in seen:
                    return False                                 # the block of k was interrupted by another of its group
                seen.add(k)
                last = k
            return True
        if wl is not None and not blocks(lambda ev: ev[0]):
            return False
        for g in {v for v in jobs.values() if v}:
            if not blocks(lambda ev: (ev[0], ev[1]) if jobs.get(ev[1]) == g else None):
                return False
        builds = [ev[0] for ev in order if ev[1:] == ("build", "read")]
        return builds == [1, 2]

    def interleavings(self, doc):
        evs = [(r,) + e for r in (1, 2) for e in self.EVENTS]
        out = []
        for slots in itertools.combinations(range(6), 3):
            seq, a, b = [], iter(evs[:3]), iter(evs[3:])
            for k in range(6):
                seq.append(next(a) if k in slots else next(b))
            if self.allowed(seq, doc):
                out.append(seq)
        return out

    def run_order(self, order):
        sim = TL.Sim(NOW - timedelta(hours=10))
        sim.t += timedelta(hours=1)
        sim.h.commit("data: start")
        first = sim.build(sim.t)
        self.assertTrue(sim.publish(first, sim.t + timedelta(minutes=1)))   # P: clean, the predecessor of both runs
        sim.t += timedelta(hours=1)
        built, snaps, halt_published, violations = {}, {}, False, []
        for run, job, step in order:
            sim.t += timedelta(minutes=1)
            if (job, step) == ("build", "read"):
                if run == 2:                                     # between M0 and M2: a direct tweak and its revert
                    old = sim.h.entries["tests"]
                    sim.h.commit("direct tweak", code=("tests",))
                    sim.h.entries["tests"] = old
                    sim.h.commit("direct revert")
                sim.h.commit(f"data: run {run}")
                built[run] = sim.build(sim.t)
            elif (job, step) == ("publish", "read"):
                snaps[run] = copy.deepcopy(sim.issue)
            else:
                before = copy.deepcopy(sim.issue)
                gh = StaleGh(sim, snaps[run])
                with TL.contextlib.redirect_stdout(sim.lines):
                    B.publish(gh, built[run]["body"], now=sim.t)
                sim.end_run(built[run]["rid"], sim.t, "success")
                if sim.issue["body"] != before["body"]:          # an acknowledged write: the oracle, after EACH one
                    new, old = B.parse_body(sim.issue["body"]), B.parse_body(before["body"])
                    prev = (new.get("c1b") or {}).get("prev") or {}
                    if prev.get("run_id") != old["run_id"] or prev.get("sha256", block_sha(before["body"])) != block_sha(before["body"]):
                        violations.append(f"run {run} replaced run {old['run_id']} without having carried it")
                    if (old.get("c1b") or {}).get("halt") and not (new.get("c1b") or {}).get("halt"):
                        violations.append(f"run {run} erased the published halt {old['c1b']['halt']['commit'][:8]}")
                    halt_published = halt_published or bool((new.get("c1b") or {}).get("halt"))
        return sim, built, violations

    def test_the_newer_build_finds_the_halt(self):
        sim, built, _v = self.run_order([(1, "build", "read"), (2, "build", "read"), (1, "publish", "read"), (1, "publish", "write"),
                                         (2, "publish", "read"), (2, "publish", "write")])
        self.assertIsNone(built[1]["record"]["halt"])
        self.assertIsNotNone(built[2]["record"]["halt"])         # the oracle's premise: only the newer range holds it

    def test_no_interleaving_the_workflow_allows_erases_a_halt_or_a_carried_ledger(self):
        orders = self.interleavings(WORKFLOW)
        self.assertGreaterEqual(len(orders), 1)
        for order in orders:
            with self.subTest(order=[f"{r}.{j}.{s}" for r, j, s in order]):
                sim, built, violations = self.run_order(order)
                self.assertEqual(violations, [])
        # the workflow-level group leaves exactly ONE order: run 1 whole, then run 2 whole (it reads run 1's brief)
        self.assertEqual(len(orders), 1)
        sim, built, violations = self.run_order(orders[0])
        self.assertEqual(B.parse_body(sim.issue["body"])["c1b"]["halt"]["commit"], built[2]["record"]["halt"]["commit"])

    def test_the_old_configuration_allows_the_erasing_interleaving(self):
        """The same model on the configuration of 990af084 (publish in no group): the R6-SH1 trace exists."""
        old = copy.deepcopy(WORKFLOW)
        old.pop("concurrency", None)
        old["jobs"]["build"]["concurrency"] = {"group": "s1-tick-brief", "cancel-in-progress": False}
        orders = self.interleavings(old)
        self.assertGreater(len(orders), 1)
        found = []
        for order in orders:
            _sim, _built, violations = self.run_order(order)
            found += violations
        # here publish() refuses the stale write too only when the two reads differ; with both reads before either
        # write the compare-and-swap of ONE process cannot see the other: the serialization is what closes it
        self.assertTrue(any("erased" in v or "without having carried" in v for v in found), found)

    def test_a_publish_in_a_fresh_read_is_refused_in_both_orders(self):
        """Both orders, fresh reads (what the serialized writer guarantees): whichever of two builds that carried the
        same brief publishes second is refused, and a halt only the refused build found is found again by the next
        build, which resumes from the published brief's proven point."""
        for second_first in (False, True):
            with self.subTest(newer_publishes_first=second_first):
                order = [(1, "build", "read"), (2, "build", "read")]
                pubs = [(2, "publish", "read"), (2, "publish", "write"), (1, "publish", "read"), (1, "publish", "write")] if second_first else \
                    [(1, "publish", "read"), (1, "publish", "write"), (2, "publish", "read"), (2, "publish", "write")]
                sim, built, violations = self.run_order(order + pubs)
                self.assertEqual(violations, [])
                self.assertIn("c1b_predecessor_not_carried", sim.lines.getvalue())
                sim.t += timedelta(minutes=30)
                nxt = sim.build(sim.t)
                self.assertEqual((nxt["record"]["halt"] or {}).get("commit"), built[2]["record"]["halt"]["commit"])
                self.assertTrue(sim.publish(nxt, sim.t + timedelta(minutes=1)))

    def test_the_workflow_is_one_critical_section_and_the_write_token_stays_in_publish(self):
        self.assertEqual(WORKFLOW["concurrency"], {"group": "s1-tick-brief", "cancel-in-progress": False})
        self.assertTrue(all("concurrency" not in j for j in WORKFLOW["jobs"].values()))
        self.assertEqual(WORKFLOW["jobs"]["build"]["permissions"]["issues"], "read")
        self.assertEqual([n for n, j in WORKFLOW["jobs"].items() if (j.get("permissions") or {}).get("issues") == "write"], ["publish"])

    def test_a_run_replaced_while_pending_is_not_a_recent_cron(self):
        runs = [{"id": 5, "event": "schedule", "status": "completed", "conclusion": "cancelled", "created_at": TB.ts(10)}]
        self.assertFalse(B.recent_build(runs, NOW, 9))
        self.assertTrue(B.recent_build([dict(runs[0], conclusion="success")], NOW, 9))


class ExactPredecessor(unittest.TestCase):
    """R6-SH2: issue + run id + run attempt + sha256 of the exact block + generation, and native provenance."""

    def setUp(self):
        self.sim = TL.Sim(NOW - timedelta(hours=10))
        self.sim.t += timedelta(hours=1)
        self.sim.h.commit("data: a")
        self.assertTrue(self.sim.publish(self.sim.build(self.sim.t), self.sim.t + timedelta(minutes=1)))
        self.sim.t += timedelta(hours=1)
        self.sim.h.commit("data: b")
        self.nxt = self.sim.build(self.sim.t)

    def published_variant(self, **change):
        brief = dict(B.parse_body(self.sim.issue["body"]), **change)
        return dict(self.sim.issue, body=B.render_issue(brief)[0] if B.decision_v1.BEGIN in self.sim.issue["body"] else B.render(brief))

    def attempt(self, issue):
        self.sim.issue = issue
        gh = TL.PublishGh(self.sim, self.sim.t)
        with TL.contextlib.redirect_stdout(self.sim.lines):
            B.publish(gh, self.nxt["body"], now=self.sim.t)
        return [w for w in gh.writes if w[0] == "PATCH"]

    def test_the_carried_tuple_is_exact(self):
        prev = self.nxt["record"]["prev"]
        self.assertEqual(sorted(prev), sorted(B.TUPLE_KEYS))
        self.assertEqual(prev, B.brief_tuple(self.sim.issue))
        self.assertEqual(self.nxt["brief"]["generation"], prev["generation"] + 1)

    def test_same_run_id_another_attempt_is_refused(self):
        self.assertEqual(self.attempt(self.published_variant(run_attempt=2)), [])

    def test_same_run_id_and_attempt_another_body_is_refused(self):
        self.assertEqual(self.attempt(self.published_variant(errors=["changed"])), [])

    def test_another_issue_number_or_generation_is_refused(self):
        self.assertEqual(self.attempt(dict(self.sim.issue, number=TL.ISSUE + 7)), [])
        self.assertEqual(self.attempt(self.published_variant(generation=5)), [])

    def test_the_exact_predecessor_is_written(self):
        self.assertEqual(self.attempt(self.sim.issue), [("PATCH", f"issues/{TL.ISSUE}")])

    def test_a_new_brief_never_replaces_a_newer_generation(self):
        newer = self.published_variant(generation=self.nxt["brief"]["generation"] + 3)
        self.assertEqual(self.attempt(newer), [])

    def test_a_carried_tuple_with_a_generation_that_is_not_the_next_is_refused(self):
        for gen in (0, self.nxt["brief"]["generation"] + 1, self.nxt["brief"]["generation"] - 1):
            with self.subTest(gen=gen):
                body = B.render_issue(dict(self.nxt["brief"], generation=gen))[0]
                gh = TL.PublishGh(self.sim, self.sim.t)
                with TL.contextlib.redirect_stdout(self.sim.lines):
                    B.publish(gh, body, now=self.sim.t)
                self.assertEqual([w for w in gh.writes if w[0] == "PATCH"], [])

    def test_an_in_progress_predecessor_is_re_read_then_never_an_anchor(self):
        sim = self.sim
        rid = B.parse_body(sim.issue["body"])["run_id"]
        sim.runs[rid].update(status="in_progress", conclusion=None)
        waits, saved = [], B.time.sleep
        B.time.sleep = waits.append
        try:
            b = sim.build(sim.t + timedelta(minutes=2))
        finally:
            B.time.sleep = saved
        self.assertEqual(waits, list(B.ANCHOR_WAITS))
        self.assertEqual((b["record"]["prev"], b["record"]["reason"]), (None, "C1b:anchor_pending"))
        self.assertFalse(sim.publish(b, sim.t + timedelta(minutes=3), conclusion="success"))   # never replaces
        sim.runs[rid].update(status="completed", conclusion="success")

    def test_a_cancelled_or_failed_predecessor_is_carried_but_never_anchors(self):
        sim = self.sim
        rid = B.parse_body(sim.issue["body"])["run_id"]
        for conclusion in ("cancelled", "failure"):
            with self.subTest(conclusion):
                sim.runs[rid].update(status="completed", conclusion=conclusion)
                b = sim.build(sim.t + timedelta(minutes=2))
                self.assertEqual(b["record"]["prev"], B.brief_tuple(sim.issue))     # read and carried
                self.assertEqual(b["record"]["from"], sim.h.base)          # no anchor: the window scan from the start
                self.assertTrue(b["record"]["gaps"])                        # and the history before it stays a gap
        sim.runs[rid].update(conclusion="success")

    def test_provenance_binds_event_attempt_and_head_repository(self):
        issue = self.sim.issue
        prev = B.parse_body(issue["body"])
        run = dict(self.sim.runs[prev["run_id"]])
        self.assertEqual(B.previous_anchor(issue, prev, run, NOW)[2], None)
        for change in ({"run_attempt": 2}, {"event": "pull_request"}, {"event": "push"}, {"head_repository": {"full_name": "fork/x"}},
                       {"head_branch": "feature"}, {"path": ".github/workflows/other.yml"}):
            with self.subTest(change):
                self.assertEqual(B.previous_anchor(issue, prev, dict(run, **change), NOW)[2], "run_binding")

    def test_a_patch_whose_answer_was_lost_is_carried_by_the_next_build(self):
        sim = self.sim
        sim.h.commit("direct push", code=("scripts",))
        b = sim.build(sim.t + timedelta(minutes=5))
        gh = TL.PublishGh(sim, sim.t)
        real = gh._request
        def lost(method, path, data=None, **kw):
            real(method, path, data, **kw)
            raise OSError("connection reset after the write")
        gh._request = lost
        with self.assertRaises(OSError), TL.contextlib.redirect_stdout(sim.lines):
            B.publish(gh, b["body"], now=sim.t)
        sim.end_run(b["rid"], sim.t + timedelta(minutes=6), "failure")
        self.assertEqual(B.parse_body(sim.issue["body"])["run_id"], b["rid"])        # the write landed
        sim.t += timedelta(hours=1)
        nxt = sim.build(sim.t)
        self.assertEqual(nxt["record"]["prev"], B.brief_tuple(sim.issue))           # carried exactly, though its run failed
        self.assertEqual(nxt["record"]["halt"]["commit"], b["record"]["halt"]["commit"])
        self.assertTrue(sim.publish(nxt, sim.t + timedelta(minutes=1)))


class DuplicateIssues(unittest.TestCase):
    """R6-SH2: an extra brief issue is closed only once every unique gap and halt of it is in the surviving brief."""

    def world(self, extra_gaps, extra_halt=None):
        sim = TL.Sim(NOW - timedelta(hours=10))
        sim.t += timedelta(hours=1)
        sim.h.commit("data: a")
        self.assertTrue(sim.publish(sim.build(sim.t), sim.t + timedelta(minutes=1)))
        first = B.parse_body(sim.issue["body"])
        extra = dict(first, c1b=dict(first["c1b"], gaps=extra_gaps, halt=extra_halt))
        sim.extra = {"number": TL.ISSUE + 1, "user": dict(TL.BOT), "body": B.render(extra), "updated_at": sim.issue["updated_at"]}
        return sim

    def run_dup(self, sim, extra_seen_by_publish=None):
        sim.t += timedelta(hours=1)
        sim.h.commit("data: b")
        gh = TL.BuildGh(sim, None)
        plain = gh.get
        gh.get = lambda path, params=None: (plain(path, params) + [copy.deepcopy(sim.extra)]) if path == "issues" else plain(path, params)
        record = B.read_c1b(gh, sim.h.main, copy.deepcopy(sim.ledger), sim.t)
        w = TL.TD.thin_world("SHADOW")
        rid = sim.next_run
        sim.next_run += 1
        sim.runs[rid] = dict(sim.runs[max(sim.runs)], id=rid, head_sha=sim.h.main)
        w.update(main_sha=sim.h.main, c1b=record, run={"id": rid, "attempt": 1, "event": "schedule"})
        w["codex_feed"] = TL.TD.codex_feed_of(w)
        brief = B.build_brief(w)
        brief["generated_at"] = B.iso(sim.t)
        body = B.render_issue(brief)[0]
        writes = []
        class Gh(TL.PublishGh):
            def get(self, path, params=None):
                if path == "issues":
                    return [copy.deepcopy(sim.issue), copy.deepcopy(extra_seen_by_publish or sim.extra)]
                return super().get(path, params)
            def _request(self, method, path, data=None, **kw):
                writes.append((method, path, data))
                if path == f"issues/{TL.ISSUE}" and "body" in data:
                    sim.issue = dict(sim.issue, body=data["body"])
                return b"{}", {}
        with TL.contextlib.redirect_stdout(sim.lines):
            B.publish(Gh(sim, sim.t), body, now=sim.t)
        return record, writes

    def test_an_extra_whose_gaps_were_carried_is_closed(self):
        g = B.c1b_gap(None, TC.sha("extra-gap"), "C1b:range", 100, B.iso(NOW - timedelta(hours=9)))
        sim = self.world([g])
        record, writes = self.run_dup(sim)
        self.assertIn(g["id"], [x["id"] for x in record["gaps"]])
        self.assertEqual(len(record["prev"]["absorbed"]), 1)
        self.assertIn(("PATCH", f"issues/{TL.ISSUE + 1}"), [(m, p) for m, p, d in writes if d.get("state") == "closed"])

    def test_an_extra_that_changed_after_the_build_is_kept_open(self):
        g = B.c1b_gap(None, TC.sha("extra-gap"), "C1b:range", 100, B.iso(NOW - timedelta(hours=9)))
        sim = self.world([g])
        changed = B.parse_body(sim.extra["body"])
        changed["c1b"]["gaps"].append(B.c1b_gap(None, TC.sha("later-gap"), "C1b:range", 100, B.iso(NOW - timedelta(hours=8))))
        _record, writes = self.run_dup(sim, dict(sim.extra, body=B.render(changed)))
        self.assertFalse([1 for m, p, d in writes if d.get("state") == "closed"])
        self.assertIn("S1_TICK_BRIEF_DUPLICATE_KEPT", sim.lines.getvalue())

    def test_preserved_needs_every_gap_and_the_halt(self):
        g = B.c1b_gap(None, TC.sha("x"), "C1b:range", 100, B.iso(NOW))
        halt = {"commit": TC.sha("h"), "parent": TC.sha("hp"), "entries": ["tests"], "capped": False}
        old = {"c1b": {"gaps": [g], "halt": halt}, "generated_at": B.iso(NOW), "main": TC.sha("m")}
        self.assertFalse(B.preserved(old, {"c1b": {"gaps": [], "halt": halt, "cleared": []}}))
        self.assertTrue(B.preserved(old, {"c1b": {"gaps": [], "halt": halt, "cleared": [{"id": g["id"], "by": "owner:9"}]}}))
        self.assertFalse(B.preserved(old, {"c1b": {"gaps": [g], "halt": None}}))
        self.assertTrue(B.preserved(old, {"c1b": {"gaps": [g], "halt": dict(halt)}}))


def merge_entry(n):
    return {"n": n, "head": f"{n:040x}", "open": [], "ci": {"state": "GREEN", "tuples": {}, "checks": {}},
            "review": {"codex": {"status": "FINAL"}}, "lane": {"risk_floor": "LOW", "eligible": True}}


def repair_entry(n):
    return {"n": n, "head": f"{n:040x}", "open": ["C3:ci"], "ci": {"state": "FAIL", "tuples": {"test": {"s": "FAIL"}}, "checks": {}},
            "review": {"codex": {"status": "NONE"}}, "lane": {"risk_floor": "LOW", "eligible": True}, "address_at_head": False}


class FenceBeforeRank(unittest.TestCase):
    """R6-SH3: with six or more merge-ranked entries and a REPAIR, the C1b fence never hides the legal REPAIR."""

    def test_the_fence_applies_before_the_cut(self):
        entries = [merge_entry(n) for n in range(1, 8)] + [repair_entry(50)]
        lane, health = {"state": "ON"}, {}
        plain = B.next_actions(entries, lane, health, [], True)
        self.assertEqual([x["action"] for x in plain], ["MERGE"] * 6)            # the cut: the REPAIR is the 8th
        fenced = B.next_actions(entries, lane, health, [], True, fence_merges=True)
        self.assertEqual([(x["action"], x["pr"], x["rank"]) for x in fenced], [("REPAIR", 50, 1)])
        self.assertEqual(B.c1b_fenced_next(plain, {"fence": ["gaps=1"]}), [])     # the old order: filtered after the cut, nothing left

    def test_build_brief_fences_before_the_cut_for_gaps_open_and_incomplete(self):
        g = B.c1b_gap(None, TC.sha("gap"), "C1b:range", 100, TB.ts(65))
        for record in ({"checked_through": TB.MAIN, "from": TB.MAIN, "complete": True, "gaps": [g]},
                       {"checked_through": TB.MAIN, "from": TB.MAIN, "complete": True,
                        "open": {"from": TB.MAIN, "to": TC.sha("t"), "reason": "C1b:budget", "unread": 5}},
                       {"checked_through": TB.MAIN, "from": TB.MAIN, "complete": False, "reason": "C1b:tree_read"}):
            with self.subTest(record=sorted(record)):
                block, _r = B.c1b_block(record, NOW)
                self.assertTrue(block["fence"])
                seen = {}
                real = B.next_actions
                def spy(*a, **kw):
                    seen.update(kw)
                    return real(*a, **kw)
                B.next_actions = spy
                try:
                    TC.brief_with(record)
                finally:
                    B.next_actions = real
                self.assertIs(seen.get("fence_merges"), True)


class HighLoadLiveness(unittest.TestCase, TL.Invariants):
    """R6-SH3 liveness: sustained 30-60 commits per tick for many ticks (with the long run's code-commit mix: squash
    merges, direct pushes, A -> B -> A tweaks). The open segment stays bounded and drains; a load above one build's proof
    capacity is surfaced on the owner line (C1B_GAP(window=<unread>)) on every brief, never silently promoted."""

    @staticmethod
    def commits(sim, rng, n, halt_rate):
        """Data captures, squash merges (some touching code) and, at `halt_rate`, direct code pushes or A -> B -> A
        tweaks (each one a C1b halt)."""
        for _ in range(n):
            x = rng.random()
            if x < halt_rate / 2:
                sim.halts_made.add(sim.h.commit("direct push", code=("scripts",)))
            elif x < halt_rate:
                old = sim.h.entries["tests"]
                sim.halts_made.add(sim.h.commit("direct tweak", code=("tests",)))
                sim.h.entries["tests"] = old
                sim.h.commit("direct revert")
            elif x < halt_rate + 0.12:
                sim.h.commit(f"Feature (#{9000 + len(sim.h.rows)})", code=(rng.choice(B.T3_TREE_DIRS),) if rng.random() < 0.7 else ())
            else:
                sim.h.commit(f"data: capture {len(sim.h.rows)}")

    def run_load(self, ticks, lo, hi, seed, halt_rate=0.005):
        rng = random.Random(seed)
        sim = TL.Sim(NOW - timedelta(hours=ticks + 20))
        unread, surfaced, calls = [], 0, []
        for tick in range(ticks):
            sim.t += timedelta(hours=1)
            self.commits(sim, rng, rng.randint(lo, hi), halt_rate)
            sim.name_halt(sim.t - timedelta(minutes=20))
            pub = sim.published()
            for g in ((pub or {}).get("c1b") or {}).get("gaps") or []:
                sim.accept(g, sim.t - timedelta(minutes=10))           # the owner disposes of every gap at once
            before = sim.published()
            b = sim.build(sim.t)
            self.check_build(self, sim, b)
            self.assertTrue(sim.publish(b, sim.t + timedelta(minutes=1)))
            self.check_publish(self, sim, before, sim.published(), [b])
            self.check_coverage(self, sim)
            opn = sim.published()["c1b"]["open"]
            unread.append((opn or {}).get("unread", 0))
            calls.append(b["calls"])
            if opn:
                self.assertIn("C1B_GAP(window=", sim.published()["status_lines"][0])   # surfaced on the owner line (gaps + open)
                self.assertNotEqual(b["decision"]["action"], "MERGE")
                surfaced += 1
        return sim, unread, surfaced, calls

    def test_sustained_30_to_60_commits_per_tick_stay_bounded(self):
        sim, unread, surfaced, calls = self.run_load(60, 30, 60, 7)
        print(f"S1_C1B_HIGH_LOAD load=30-60 ticks=60 commits={len(sim.h.rows)} unread_max={max(unread)} "
              f"unread_last10_max={max(unread[-10:])} series={unread} open_ticks={surfaced} calls_max={max(calls)}")
        self.assertLessEqual(max(calls), B.C1B_MAX_CALLS)
        self.assertLessEqual(max(unread), 2 * 60)                      # bounded: never two ticks' arrivals behind
        for k in range(0, len(unread), 10):
            self.assertEqual(min(unread[k:k + 10]), 0, unread)         # and it drains: never a growing backlog

    def test_a_load_above_capacity_is_surfaced_every_tick(self):
        sim, unread, surfaced, _calls = self.run_load(20, 150, 150, 11)
        self.assertGreater(unread[-1], unread[0])                      # above capacity the backlog grows: and is surfaced
        print(f"S1_C1B_HIGH_LOAD load=150 ticks=20 commits={len(sim.h.rows)} unread_max={max(unread)} open_ticks={surfaced}")
        self.assertEqual(surfaced, sum(1 for u in unread if u))       # every open brief carried the owner line
        self.assertGreater(surfaced, 0)


class NativeGapAcceptance(unittest.TestCase):
    """R6-SH4: exact owner acceptance: native never-edited record, positive id, the exact gap detection, its fields once."""

    def setUp(self):
        self.gap = B.c1b_gap(None, TC.sha("t"), "C1b:range", 100, TB.ts(65))
        self.ok = TC.accept_comment(90, self.gap)

    def test_the_exact_acceptance_counts(self):
        self.assertEqual(B.gap_acceptance(self.gap, [self.ok]), 90)
        self.assertTrue(B.gap_action_id(self.gap).startswith("C1B-"))
        self.assertIn(f"gap: {B.gap_action_id(self.gap)}", B.gap_accept_body(self.gap))

    def test_what_never_counts(self):
        g, ok = self.gap, self.ok
        cases = {
            "same_second_edit": dict(ok, native_edit=dict(ok["native_edit"], lastEditedAt=ok["created_at"])),   # REST created == updated
            "includes_created_edit": dict(ok, native_edit=dict(ok["native_edit"], includesCreatedEdit=True)),
            "no_native_record": {k: v for k, v in ok.items() if k != "native_edit"},
            "native_field_missing": dict(ok, native_edit={k: v for k, v in ok["native_edit"].items() if k != "lastEditedAt"}),
            "native_other_comment": dict(ok, native_edit=dict(ok["native_edit"], databaseId=91)),
            "native_other_author": dict(ok, native_edit=dict(ok["native_edit"], author="someone")),
            "wrong_issue": dict(ok, native_edit=dict(ok["native_edit"], issue=1157)),
            "non_positive_id": dict(ok, id=0, native_edit=dict(ok["native_edit"], databaseId=0)),
            "id_not_int": dict(ok, id="90", native_edit=dict(ok["native_edit"], databaseId="90")),
            "duplicate_to": dict(ok, body=ok["body"] + f"\nto: {g['to']}"),
            "duplicate_gap_by_equals": dict(ok, body=ok["body"] + f"\ngap={B.gap_action_id(g)}"),
            "missing_gap_id": dict(ok, body="\n".join(l for l in ok["body"].splitlines() if not l.startswith("gap:"))),
            "missing_from": dict(ok, body="\n".join(l for l in ok["body"].splitlines() if not l.startswith("from:"))),
            "invalid_gap_id": dict(ok, body=ok["body"].replace(B.gap_action_id(g), "C1B-zzzz")),
            "stale_generation": TC.accept_comment(90, dict(g, detected_at=TB.ts(200))),   # an earlier detection of the same range
            "rest_edited": dict(ok, updated_at=TB.ts(1)),
        }
        for name, row in cases.items():
            with self.subTest(name):
                self.assertIsNone(B.gap_acceptance(g, [row]), name)
        redetected = dict(g, detected_at=TB.ts(30))                       # the same range found again later: a new id
        self.assertNotEqual(B.gap_action_id(redetected), B.gap_action_id(g))
        self.assertIsNone(B.gap_acceptance(redetected, [ok]))

    def test_the_native_read_is_one_graphql_call_and_fails_closed(self):
        rows = [dict(TB.comment(90, B.gap_accept_body(self.gap), TB.OWNER, 5), node_id="IC_x"),
                dict(TB.comment(91, "S1_LANE_HALTED\ncommit: x", TB.OWNER, 5), node_id="IC_y")]
        class Gh:
            calls = []
            def graphql(self, q, v):
                self.calls.append(v)
                return {"nodes": [{"databaseId": 90, "lastEditedAt": None, "includesCreatedEdit": False,
                                   "author": {"login": TB.OWNER["login"]}, "issue": {"number": B.OWNER_ISSUE}}]}
        gh = Gh()
        self.assertEqual(B.read_gap_native(gh, rows), 1)
        self.assertEqual(gh.calls, [{"ids": ["IC_x"]}])
        self.assertEqual(B.gap_acceptance(self.gap, rows), 90)
        rows2 = [dict(TB.comment(90, B.gap_accept_body(self.gap), TB.OWNER, 5), node_id="IC_x")]
        class Down:
            def graphql(self, q, v):
                raise RuntimeError("GRAPHQL_ERROR")
        with self.assertRaises(RuntimeError):
            B.read_gap_native(Down(), rows2)
        self.assertIsNone(B.gap_acceptance(self.gap, rows2))               # nothing attached: nothing accepted

    def test_the_shadow_record_names_each_gap_and_its_exact_reply(self):
        block, _r = B.c1b_block({"checked_through": TB.MAIN, "from": TB.MAIN, "complete": True, "gaps": [self.gap]}, NOW)
        gid = B.gap_action_id(self.gap)
        self.assertEqual(block["owner_actions"], [{"id": gid, "gap": self.gap["id"], "reply": f"GO {gid}"}])


if __name__ == "__main__":
    unittest.main()


class MalformedHead(unittest.TestCase):
    """Found by the N07 fuzz this round (its paths changed with the new brief fields): decide() merged a PR whose head was
    not a 40-hex SHA (None, "x", [], {}) when executor=LIVE. A malformed head is a gate, never a merge."""

    def test_a_malformed_head_is_never_merged(self):
        import test_s1_invariants_v1 as TI
        _d, brief = TI.decide()
        self.assertEqual(D.decide(brief)["action"], "MERGE")             # the control: the well-formed brief merges
        for bad in (None, "x", 1, [], {}, True, [None], {"x": None}, -1, "A" * 40):
            with self.subTest(bad=bad):
                b = copy.deepcopy(brief)
                b["prs"][0]["head"] = bad
                d = D.decide(b)
                self.assertTrue(D.decision_schema_ok(d))
                self.assertNotEqual(d["action"], "MERGE")
