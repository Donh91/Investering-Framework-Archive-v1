"""Fix round 8 (#2337; Bridge #173/7201853836 R7-SH1, addendum 7201991151 R7-SH2 and the publication line): the exact
identity of ONE gap detection (range id AND detected_at, i.e. gap_action_id) conserved across the carried union of
duplicate brief issues, the owner acceptance, the cleared record, preserved() and the closing of an extra issue; the
C1b ledger and the generation kept at every render level (the shrunk brief is published, read back and resumed); and
a publish step that says WRITTEN or SKIPPED. Real read_c1b / build_brief / render_issue / decide / publish over
multi-tick fake-GitHub worlds. Fixtures only, no network."""
import contextlib
import copy
import io
import os
import sys
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
for _p in (ROOT / "scripts" / "governance", ROOT / "tests" / "governance"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import s1_decision_v1 as D  # noqa: E402
import s1_tick_brief_v1 as B  # noqa: E402
import test_s1_brief_c1b_v1 as TC  # noqa: E402  (module imports: their TestCases are not collected twice)
import test_s1_c1b_ledger_v1 as TL  # noqa: E402
import test_s1_tick_brief_v1 as TB  # noqa: E402

NOW = TB.NOW
EXTRA = TL.ISSUE + 1


def det(g):
    """The exact detection identity of one gap item."""
    return (g["id"], g["detected_at"])


def gaps_of(brief):
    return [det(g) for g in ((brief or {}).get("c1b") or {}).get("gaps") or []]


class DupWorld:
    """main's history, the canonical brief issue (TL.ISSUE), any open extra brief issues and the owner's #1156. Every
    tick builds with the real read_c1b over the issues GitHub would list, then publishes with the real publish() over
    the issues the publish job would list. The run of every build completes (success) after its publish."""

    def __init__(self, tc, canon_gaps, extra_gaps, reverse_listing=False):
        self.tc, self.reverse = tc, reverse_listing
        sim = self.sim = TL.Sim(NOW - timedelta(hours=10))
        sim.t += timedelta(hours=1)
        sim.h.commit("data: a")
        tc.assertTrue(sim.publish(sim.build(sim.t), sim.t + timedelta(minutes=1)))
        first = B.parse_body(sim.issue["body"])
        sim.issue = dict(sim.issue, body=B.render_issue(dict(first, c1b=dict(first["c1b"], gaps=canon_gaps)))[0])
        extra = dict(first, c1b=dict(first["c1b"], gaps=extra_gaps, halt=None))
        self.extras = [{"number": EXTRA, "user": dict(TL.BOT), "body": B.render(extra), "updated_at": sim.issue["updated_at"]}]
        self.history, self.strict = [], True

    def listing(self):
        rows = [copy.deepcopy(self.sim.issue)] + [copy.deepcopy(x) for x in self.extras]
        return list(reversed(rows)) if self.reverse else rows

    def tick(self, lose=None, mutate_world=None, mutate_body=None):
        """One build + publish. lose: "body" (the canonical PATCH lands, its answer is lost) or "close" (the close of an
        extra lands, its answer is lost). Returns (record, published brief of THIS build, decision, writes, wrote)."""
        sim, world = self.sim, self
        sim.t += timedelta(hours=1)
        sim.h.commit("data: tick")
        rid, sim.next_run = sim.next_run, sim.next_run + 1
        sim.runs[rid] = dict(sim.runs[min(sim.runs)], id=rid, head_sha=sim.h.main, status="in_progress", conclusion=None,
                             run_started_at=B.iso(sim.t - timedelta(minutes=1)), updated_at=B.iso(sim.t - timedelta(minutes=1)))
        gh = TL.BuildGh(sim, None)
        plain = gh.get
        gh.get = lambda path, params=None: world.listing() if path == "issues" else plain(path, params)
        record = B.read_c1b(gh, sim.h.main, copy.deepcopy(sim.ledger), sim.t)
        w = TL.TD.thin_world("SHADOW")
        w.update(main_sha=sim.h.main, c1b=record, run={"id": rid, "attempt": 1, "event": "schedule"})
        if mutate_world:
            mutate_world(w)
        w["codex_feed"] = TL.TD.codex_feed_of(w)
        brief = B.build_brief(w)
        brief["generated_at"] = B.iso(sim.t)
        if mutate_body:
            brief = mutate_body(brief)
        body, decision = B.render_issue(brief)
        writes = []

        class Gh(TL.PublishGh):
            def get(self, path, params=None):
                if path == "issues":
                    return world.listing()
                if path.startswith("issues/"):
                    n = int(path.split("/")[1])
                    return copy.deepcopy(sim.issue if n == TL.ISSUE else next(x for x in world.extras if x["number"] == n))
                return super().get(path, params)

            def _request(self, method, path, data=None, **kw):
                writes.append((method, path, dict(data or {})))
                if path == f"issues/{TL.ISSUE}" and "body" in data:
                    sim.issue = dict(sim.issue, body=data["body"], updated_at=B.iso(sim.t))
                    if lose == "body":
                        raise OSError("connection reset after the write")
                elif data.get("state") == "closed":
                    if lose == "close_fail":
                        raise OSError("HTTP 502 before the close")
                    world.extras = [x for x in world.extras if f"issues/{x['number']}" != path]
                    if lose == "close":
                        raise OSError("connection reset after the write")
                return b"{}", {}

        gh_pub = Gh(sim, sim.t)
        try:
            with contextlib.redirect_stdout(sim.lines):
                B.publish(gh_pub, body, now=sim.t)
        except OSError:
            pass
        sim.end_run(rid, sim.t + timedelta(minutes=1), "success")
        wrote = any(p == f"issues/{TL.ISSUE}" and "body" in d for _m, p, d in writes)
        out = (record, B.parse_body(body), decision, writes, wrote)
        self.history.append(out)
        self.check_fenced(out)
        return out

    def check_fenced(self, out):
        record, brief, decision, _w, _wrote = out
        tc = self.tc
        if not brief["c1b"]["fence"] and brief["complete"] and not self.extras and not self.strict:
            return                                                      # nothing open, no duplicate left: progress may happen
        tc.assertNotEqual(decision["action"], "MERGE")
        tc.assertEqual([e for e in brief["next"] if e["action"] in B.MERGE_ACTIONS], [])
        tc.assertFalse(any(x.get("ready") for x in brief["claude_slots"]))

    def published(self):
        return B.parse_body(self.sim.issue["body"])

    def extra_open(self):
        return bool(self.extras)

    def b_conserved(self, g):
        """B is still fenced: its exact detection is in the canonical brief, or the extra issue that holds it is open."""
        return det(g) in gaps_of(self.published()) or any(det(g) in gaps_of(B.parse_body(x["body"])) for x in self.extras)


def rng(tag):
    return TC.sha(f"{tag}-from"), TC.sha(f"{tag}-to")


class GapIdentity(unittest.TestCase):
    """R7-SH1: same range, different detected_at, in two issue histories."""

    def pair(self):
        frm, to = rng("x")
        a = B.c1b_gap(frm, to, "C1b:range", 100, B.iso(NOW - timedelta(hours=9, minutes=30)))
        b = B.c1b_gap(frm, to, "C1b:range", 100, B.iso(NOW - timedelta(hours=9, minutes=10)))
        self.assertEqual(a["id"], b["id"])
        self.assertNotEqual(B.gap_action_id(a), B.gap_action_id(b))
        return a, b

    def test_only_a_accepted_b_stays_fenced(self):
        a, b = self.pair()
        world = DupWorld(self, [a], [b])
        world.sim.accept(a, world.sim.t + timedelta(minutes=5))
        record, brief, _d, _w, wrote = world.tick()
        self.assertTrue(wrote)
        self.assertIn(det(b), gaps_of(brief))                           # B survives in the canonical brief
        self.assertNotIn(det(a), gaps_of(brief))
        self.assertEqual([x["gap"] for x in brief["c1b"]["cleared"]], [B.gap_action_id(a)])
        self.assertTrue(world.b_conserved(b))
        for _ in range(3):                                              # and keeps being fenced on every later tick
            world.tick()
            self.assertTrue(world.b_conserved(b))
            self.assertIn(det(b), gaps_of(world.published()))

    def test_both_accepted_each_by_its_own_receipt(self):
        a, b = self.pair()
        world = DupWorld(self, [a], [b])
        world.sim.accept(a, world.sim.t + timedelta(minutes=5))
        world.sim.accept(b, world.sim.t + timedelta(minutes=6))
        cid_a, cid_b = world.sim.ledger[-2]["id"], world.sim.ledger[-1]["id"]
        _r, brief, _d, writes, wrote = world.tick()
        self.assertTrue(wrote)
        self.assertNotIn(det(a), gaps_of(brief))
        self.assertNotIn(det(b), gaps_of(brief))
        cleared = {x["gap"]: x for x in brief["c1b"]["cleared"]}
        self.assertEqual(set(cleared), {B.gap_action_id(a), B.gap_action_id(b)})
        self.assertEqual((cleared[B.gap_action_id(a)]["comment"], cleared[B.gap_action_id(b)]["comment"]), (cid_a, cid_b))
        self.assertEqual(cleared[B.gap_action_id(b)]["detected_at"], b["detected_at"])
        self.assertFalse(world.extra_open())                            # both disposed of exactly: the extra may close

    def test_neither_accepted_both_detections_are_kept(self):
        a, b = self.pair()
        world = DupWorld(self, [a], [b])
        _r, brief, _d, _w, _wrote = world.tick()
        self.assertIn(det(a), gaps_of(brief))
        self.assertIn(det(b), gaps_of(brief))
        self.assertEqual(len([o for o in brief["c1b"]["owner_actions"] if o["gap"] == a["id"]]), 2)   # two GO ids, one per detection
        world.tick()
        self.assertIn(det(a), gaps_of(world.published()))
        self.assertIn(det(b), gaps_of(world.published()))

    def test_reversed_ordering(self):
        a, b = self.pair()
        for reverse_listing in (False, True):
            with self.subTest(reverse_listing=reverse_listing):
                world = DupWorld(self, [b], [a], reverse_listing=reverse_listing)   # the canonical issue holds B, the extra A
                world.sim.accept(a, world.sim.t + timedelta(minutes=5))
                _r, brief, _d, _w, wrote = world.tick()
                self.assertTrue(wrote)
                self.assertIn(det(b), gaps_of(brief))
                self.assertEqual([x["gap"] for x in brief["c1b"]["cleared"]], [B.gap_action_id(a)])
                world.tick()
                self.assertIn(det(b), gaps_of(world.published()))
                # and A's receipt never disposes of B later
                self.assertIsNone(B.gap_acceptance(b, world.sim.ledger))

    def test_only_a_accepted_with_the_listing_reversed(self):
        a, b = self.pair()
        world = DupWorld(self, [a], [b], reverse_listing=True)
        world.sim.accept(a, world.sim.t + timedelta(minutes=5))
        world.tick()
        self.assertTrue(world.b_conserved(b))
        self.assertIn(det(b), gaps_of(world.published()))

    def test_lost_patch_response(self):
        a, b = self.pair()
        for lose in ("body", "close"):
            with self.subTest(lose=lose):
                world = DupWorld(self, [a], [b])
                world.sim.accept(a, world.sim.t + timedelta(minutes=5))
                world.tick(lose=lose)
                self.assertTrue(world.b_conserved(b))
                self.assertEqual(world.extra_open(), lose == "body")    # a lost answer before the close: the extra stays open
                world.tick()                                            # the next build carries both issues (or the one) exactly
                self.assertTrue(world.b_conserved(b))
                self.assertIn(det(b), gaps_of(world.published()))
                self.assertFalse(world.extra_open())
                world.tick()
                self.assertIn(det(b), gaps_of(world.published()))

    def test_an_ambiguous_legacy_clearance_never_clears_another_history(self):
        a, b = self.pair()
        legacy = {"c1b": {"gaps": [], "halt": None, "cleared": [{"id": a["id"], "by": "owner:77"}]}}
        old = {"c1b": {"gaps": [b], "halt": None}, "generated_at": B.iso(NOW), "main": TC.sha("m")}
        self.assertFalse(B.preserved(old, legacy))                      # no detection id: not B's disposition
        exact_a = {"c1b": {"gaps": [], "halt": None, "cleared": [{"id": a["id"], "by": "owner:77", "gap": B.gap_action_id(a),
                                                                   "detected_at": a["detected_at"], "comment": 77}]}}
        self.assertFalse(B.preserved(old, exact_a))                     # A's exact disposition is not B's
        exact_b = {"c1b": {"gaps": [], "halt": None, "cleared": [{"id": b["id"], "by": "owner:78", "gap": B.gap_action_id(b),
                                                                   "detected_at": b["detected_at"], "comment": 78}]}}
        self.assertTrue(B.preserved(old, exact_b))
        rec_b = exact_b["c1b"]["cleared"][0]
        for name, forged in {"another_detections_action_id": dict(rec_b, gap=B.gap_action_id(a)),
                             "by_names_another_comment": dict(rec_b, by="owner:79"),
                             "no_comment_id": {k: v for k, v in rec_b.items() if k != "comment"},
                             "no_detection_id_but_detected_at": {k: v for k, v in rec_b.items() if k != "gap"},   # closer S06
                             "detection_id_not_a_string": dict(rec_b, gap=None),
                             "comment_not_positive": dict(rec_b, comment=0, by="owner:0")}.items():
            with self.subTest(name):
                self.assertFalse(B.preserved(old, {"c1b": {"gaps": [], "halt": None, "cleared": [forged]}}))
        self.assertFalse(B.preserved(old, {"c1b": {"gaps": [a], "halt": None}}))   # the same range, another detection
        self.assertTrue(B.preserved(old, {"c1b": {"gaps": [dict(b)], "halt": None}}))
        # through publish(): a body whose ledger names A's range only by a legacy record never closes the extra holding B
        world = DupWorld(self, [a], [b])

        def legacy_body(brief):
            c = dict(brief["c1b"], gaps=[g for g in brief["c1b"]["gaps"] if g["id"] != a["id"]],
                     cleared=[{"id": a["id"], "by": "owner:77"}])
            return dict(brief, c1b=c)
        world.tick(mutate_body=legacy_body)
        self.assertTrue(world.extra_open())
        self.assertIn("S1_TICK_BRIEF_DUPLICATE_KEPT", world.sim.lines.getvalue())
        self.assertTrue(world.b_conserved(b))

    def test_one_canonical_history_keeps_the_first_observation(self):
        """Normal recurring detection is unchanged: a range found again every tick in ONE history stays ONE gap with
        its first detection time (no new gap, no new action id per tick)."""
        sim = TL.Sim(NOW - timedelta(hours=10))
        sim.t += timedelta(hours=1)
        sim.h.commit("data: a")
        b = sim.build(sim.t)
        self.assertTrue(sim.publish(b, sim.t + timedelta(minutes=1), conclusion="failure"))   # no anchor next tick
        firsts = []
        for _ in range(4):
            sim.t += timedelta(hours=1)
            sim.h.commit("data: more")
            b = sim.build(sim.t)
            self.assertTrue(sim.publish(b, sim.t + timedelta(minutes=1), conclusion="failure"))
            gaps = sim.published()["c1b"]["gaps"]
            self.assertEqual(len(gaps), 1)
            firsts.append(det(gaps[0]))
        self.assertEqual(len(set(firsts)), 1)

    def test_cleared_records_survive_the_brief_record_round_trip(self):
        a, _b = self.pair()
        rec = {"checked_through": TB.MAIN, "from": TB.MAIN, "complete": True, "gaps": [],
               "cleared": [{"id": a["id"], "by": "owner:9", "gap": B.gap_action_id(a), "detected_at": a["detected_at"], "comment": 9}]}
        block, _r = B.c1b_block(rec, NOW)
        self.assertEqual(block["cleared"], rec["cleared"])
        bad = dict(rec, cleared=[{"id": a["id"], "by": "owner:9", "gap": "x", "detected_at": a["detected_at"], "comment": 9}])
        self.assertNotIn("gap", B.c1b_block(bad, NOW)[0]["cleared"][0])  # a malformed detection id is not kept as one


class ShrinkKeepsLedger(unittest.TestCase):
    """R7-SH2: the shrink-3 brief keeps generation, the exact prev tuple and the whole C1b ledger; it is published,
    read back MATCH and resumed by the next build at generation + 1."""

    @staticmethod
    def many(w, n=400, pad=10):
        for i in range(100, 100 + n):
            w["pulls"].append(TB.pull(i, TB.HEAD))
            d = TB.pr_data()
            d["detail"]["number"] = d["detail2"]["number"] = i
            d["files"][0]["filename"] = "docs/" + "x" * pad + f"/{i}.md"
            w["pr"][i] = d

    def test_oversized_brief_is_published_read_back_and_resumed(self):
        a, b = GapIdentity.pair(self)
        world = DupWorld(self, [a], [])                                 # one extra with no gaps: it is closed on tick 1
        world.tick()
        self.assertFalse(world.extra_open())
        pred = world.published()
        self.assertIn(det(a), gaps_of(pred))
        before = B.brief_tuple(world.sim.issue)
        record, brief, decision, _w, wrote = world.tick(mutate_world=self.many)
        self.assertEqual(brief["shrunk"], 3)
        self.assertTrue(wrote, world.sim.lines.getvalue()[-600:])      # the shrunk brief REPLACES its predecessor
        self.assertEqual(brief["generation"], before["generation"] + 1)
        self.assertEqual({k: brief["c1b"]["prev"][k] for k in B.TUPLE_KEYS}, before)
        self.assertEqual(brief["c1b"]["gaps"], B.c1b_block(record, world.sim.t)[0]["gaps"])   # the whole ledger
        self.assertIn(det(a), gaps_of(brief))
        self.assertEqual(brief["c1b"]["owner_actions"], [{"id": B.gap_action_id(g), "gap": g["id"], "reply": f"GO {B.gap_action_id(g)}"}
                                                         for g in brief["c1b"]["gaps"]])
        self.assertTrue(brief["c1b"]["fence"])
        self.assertEqual((brief["complete"], brief["incomplete"], brief["next"]), (False, "brief_too_large", []))
        self.assertNotEqual(decision["action"], "MERGE")
        self.assertFalse(any(x.get("ready") for x in brief["claude_slots"]))

        class Read:
            def get(self, path, params=None):
                return copy.deepcopy(world.sim.issue)
        self.assertTrue(B.readback_line(Read(), TL.ISSUE, world.sim.issue["body"]).endswith("readback=MATCH"))
        shrunk_tuple = B.brief_tuple(world.sim.issue)
        record2, brief2, _d, _w, wrote2 = world.tick()                  # the next build reads the shrunk brief
        self.assertTrue(wrote2)
        self.assertEqual({k: record2["prev"][k] for k in B.TUPLE_KEYS}, shrunk_tuple)
        self.assertEqual(brief2["generation"], shrunk_tuple["generation"] + 1)
        self.assertIn(det(a), gaps_of(brief2))

    def test_a_ledger_that_cannot_fit_fails_closed_never_drops_a_gap(self):
        gaps = [B.c1b_gap(None, TC.sha(f"g{i}"), "C1b:range", 100, B.iso(NOW - timedelta(minutes=i))) for i in range(12)]
        w = TL.TD.thin_world("SHADOW")
        self.many(w)
        w["c1b"] = {"checked_through": TB.MAIN, "from": TB.MAIN, "complete": True, "gaps": gaps}
        brief = B.build_brief(w)
        saved, saved_hard = B.MAX_BODY, B.RENDER_HARD_LIMIT
        level3 = B.parse_body(B.render(brief))
        self.assertEqual(level3["shrunk"], 3)
        self.assertEqual(len(level3["c1b"]["gaps"]), 12)
        self.assertLess(B.RENDER_HARD_LIMIT + B.MAX_DECISION_BLOCK, 65536)   # the hard limit leaves room for the decision block
        B.MAX_BODY = 100                                                # above the shrink target, under the hard limit: published whole
        self.assertEqual(len(B.parse_body(B.render(brief))["c1b"]["gaps"]), 12)
        B.RENDER_HARD_LIMIT = len(B.render(brief)) - 1                  # the ledger alone no longer fits GitHub
        try:
            with self.assertRaises(SystemExit) as cm:
                B.render(brief)
            self.assertIn("brief_too_large", str(cm.exception))
            with self.assertRaises(SystemExit):
                B.render_issue(brief)
        finally:
            B.MAX_BODY, B.RENDER_HARD_LIMIT = saved, saved_hard

    def test_every_render_level_keeps_generation_prev_and_ledger(self):
        record = {"checked_through": TB.MAIN, "from": TB.MAIN, "complete": True,
                  "gaps": [B.c1b_gap(None, TC.sha("g"), "C1b:range", 100, B.iso(NOW))],
                  "prev": {"issue": 3, "run_id": 7, "run_attempt": 1, "sha256": "a" * 64, "generation": 6}}
        for n, pad in ((0, 0), (70, 200), (400, 10)):
            with self.subTest(n=n):
                w = TL.TD.thin_world("SHADOW")
                if n:
                    self.many(w, n, pad)
                w["c1b"] = copy.deepcopy(record)
                brief = B.build_brief(w)
                out = B.parse_body(B.render(brief))
                self.assertEqual(out["generation"], 7)
                self.assertEqual(out["c1b"], brief["c1b"])


class PublicationLine(unittest.TestCase):
    """main() publish: WRITTEN vs SKIPPED (with the reason), never S1_TICK_BRIEF_PUBLISHED for a skip; the readback
    states stay distinct (MATCH after a write, SUPERSEDED after a skip)."""

    def run_main(self, sim, b):
        out = io.StringIO()
        saved_gh, saved_env = B.GitHub, dict(os.environ)

        class FakeGitHub(TL.PublishGh):
            def __init__(self, token, budget=None):
                super().__init__(sim, sim.t)

            def get(self, path, params=None):
                if path.startswith("issues/"):
                    return copy.deepcopy(sim.issue)
                return super().get(path, params)
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "brief.md"
            f.write_text(b["body"], encoding="utf-8")
            os.environ.update(GITHUB_RUN_ID=str(b["rid"]), GITHUB_SHA=b["brief"]["main"], GITHUB_REPOSITORY=B.REPO)
            B.GitHub = FakeGitHub
            try:
                with contextlib.redirect_stdout(out):
                    B.main(["s1_tick_brief_v1.py", "publish", str(f)])
            finally:
                B.GitHub = saved_gh
                os.environ.clear()
                os.environ.update(saved_env)
        return out.getvalue()

    def test_written_and_skipped_are_distinct(self):
        sim = TL.Sim(NOW - timedelta(hours=10))
        sim.t += timedelta(hours=1)
        sim.h.commit("data: a")
        self.assertTrue(sim.publish(sim.build(sim.t), sim.t + timedelta(minutes=1)))
        sim.t += timedelta(hours=1)
        sim.h.commit("data: b")
        first, second = sim.build(sim.t), sim.build(sim.t + timedelta(minutes=1))   # both carried the same predecessor
        text = self.run_main(sim, first)
        self.assertIn("S1_TICK_BRIEF_PUBLISHED", text)
        self.assertIn("result=WRITTEN", text)
        self.assertTrue(text.strip().endswith("readback=MATCH"), text)
        text = self.run_main(sim, second)                                # the CAS refuses it
        self.assertNotIn("S1_TICK_BRIEF_PUBLISHED", text)
        self.assertIn("result=SKIPPED reason=c1b_predecessor_not_carried", text)
        self.assertTrue(text.strip().endswith("readback=SUPERSEDED"), text)


class CrossFeature(unittest.TestCase):
    """Fix round 8 final adversarial pass: rounds 6+7+8 interacting over multi-tick real-code worlds."""

    def test_an_oversized_brief_with_a_duplicate_issue_keeps_b(self):
        a, b = GapIdentity.pair(self)
        world = DupWorld(self, [a], [b])
        world.sim.accept(a, world.sim.t + timedelta(minutes=5))
        _r, brief, _d, _w, wrote = world.tick(mutate_world=ShrinkKeepsLedger.many)
        self.assertEqual(brief["shrunk"], 3)
        self.assertTrue(wrote)
        self.assertIn(det(b), gaps_of(world.published()))
        self.assertTrue(brief["c1b"]["prev"]["absorbed"])               # the duplicate's tuple survives the shrink
        self.assertFalse(world.extra_open())                            # closed only because B is in the shrunk brief

    def test_a_close_that_fails_before_landing_is_retried_next_build(self):
        a, b = GapIdentity.pair(self)
        world = DupWorld(self, [a], [b])
        world.sim.accept(a, world.sim.t + timedelta(minutes=5))
        world.tick(lose="close_fail")
        self.assertTrue(world.extra_open())
        self.assertIn(det(b), gaps_of(world.published()))
        world.tick()
        self.assertFalse(world.extra_open())
        self.assertIn(det(b), gaps_of(world.published()))

    def test_recovery_and_eventual_progress(self):
        """Neither detection accepted; then the owner disposes of every published gap exactly; the fence empties, the
        generation rises by one on every written tick and the SHADOW decision finally merges (progress)."""
        a, b = GapIdentity.pair(self)
        world = DupWorld(self, [a], [b])
        world.strict = False
        gens, decided = [], None
        for k in range(8):
            _r, brief, d, _w, wrote = world.tick()
            if wrote:
                gens.append(brief["generation"])
            pub = world.published()
            if k >= 1:                                                  # the owner answers every GO line exactly once
                done = {x["body"].split("gap: ")[1].split()[0] for x in world.sim.ledger if B.GAP_ACCEPTED in x["body"]}
                for g in pub["c1b"]["gaps"]:
                    if B.gap_action_id(g) not in done:
                        world.sim.accept(g, world.sim.t + timedelta(minutes=5))
            if not pub["c1b"]["fence"] and pub["complete"] and not world.extras:
                decided = d["action"]
                break
        self.assertEqual(gens, list(range(gens[0], gens[0] + len(gens))))   # monotonic, exactly +1 per write
        self.assertEqual(decided, "MERGE", world.sim.lines.getvalue()[-800:])
        cleared = [x for _r, br, _d, _w, _wr in world.history for x in br["c1b"]["cleared"]]
        self.assertTrue({B.gap_action_id(a), B.gap_action_id(b)} <= {x["gap"] for x in cleared})

    def test_two_unresolved_halts_in_two_issues_are_both_conserved(self):
        """Multiple unresolved halts x duplicate issues: the canonical issue's halt H1 and the extra's H2. Neither is
        ever dropped: the extra stays open until H2 is carried, whatever the issue numbers (incl. a digit boundary)."""
        h1 = {"commit": TC.sha("h1"), "parent": TC.sha("h1p"), "entries": ["scripts"], "capped": False}
        h2 = {"commit": TC.sha("h2"), "parent": TC.sha("h2p"), "entries": ["tests"], "capped": False}
        for canon_no, extra_no in ((TL.ISSUE, TL.ISSUE + 1), (9999, 10000)):
            with self.subTest(canon=canon_no, extra=extra_no):
                world = DupWorld(self, [], [])
                first = world.published()
                world.sim.issue = dict(world.sim.issue, number=canon_no, body=B.render_issue(dict(first, c1b=dict(first["c1b"], halt=h1)))[0])
                world.extras = [dict(world.extras[0], number=extra_no, body=B.render(dict(first, c1b=dict(first["c1b"], halt=h2))))]
                saved = TL.ISSUE
                TL.ISSUE = canon_no
                try:
                    seen = set()
                    for _ in range(5):
                        _r, brief, _d, _w, _wrote = world.tick()
                        pub = world.published()
                        halt = pub["c1b"]["halt"]
                        if halt:
                            seen.add(halt["commit"])
                            if halt["commit"] == h1["commit"] or not world.extras:
                                world.sim.post(f"S1_LANE_HALTED\nPR=- head=-\nreason: unreviewed_code_on_main\ncommit: {halt['commit']}", world.sim.t + timedelta(minutes=5))
                        open_halts = {B.parse_body(x["body"])["c1b"]["halt"]["commit"] for x in world.extras if B.parse_body(x["body"])["c1b"].get("halt")}
                        named = {x["body"].split("commit: ")[1].strip() for x in world.sim.ledger if "S1_LANE_HALTED" in x["body"]}
                        for h in (h1, h2):                              # every halt is published, still in an open issue, or named
                            self.assertTrue(h["commit"] in seen or h["commit"] in open_halts or h["commit"] in named, h)
                    self.assertEqual(seen, {h1["commit"], h2["commit"]})
                finally:
                    TL.ISSUE = saved

    def test_a_rerun_of_an_old_run_never_erases_a_halt_or_merges(self):
        """Serialization x stale reruns: a rerun (attempt 2) of an older run builds for the OLD main, after a newer brief
        found a halt. It carries the exact predecessor, so it may write; it never erases the halt, never merges, and the
        next normal build resumes on main's chain with the halt still carried."""
        sim = TL.Sim(NOW - timedelta(hours=10))
        sim.t += timedelta(hours=1)
        sim.h.commit("data: a")
        old = sim.build(sim.t)
        self.assertTrue(sim.publish(old, sim.t + timedelta(minutes=1)))
        old_main = sim.h.main
        sim.t += timedelta(hours=1)
        sim.h.commit("direct push", code=("scripts",))
        sim.h.commit("data: b")
        nb = sim.build(sim.t)
        self.assertTrue(sim.publish(nb, sim.t + timedelta(minutes=1)))
        halt = sim.published()["c1b"]["halt"]
        self.assertTrue(halt)
        sim.t += timedelta(minutes=30)
        rid = old["rid"]
        sim.runs[rid].update(run_attempt=2, status="in_progress", conclusion=None, run_started_at=B.iso(sim.t - timedelta(minutes=1)),
                             updated_at=B.iso(sim.t - timedelta(minutes=1)))
        record = B.read_c1b(TL.BuildGh(sim, None), old_main, copy.deepcopy(sim.ledger), sim.t)
        w = TL.TD.thin_world("SHADOW")
        w.update(main_sha=old_main, c1b=record, run={"id": rid, "attempt": 2, "event": "schedule"})
        w["codex_feed"] = TL.TD.codex_feed_of(w)
        brief = B.build_brief(w)
        brief["generated_at"] = B.iso(sim.t)
        body, decision = B.render_issue(brief)
        rerun = {"rid": rid, "at": sim.t, "record": record, "body": body, "decision": decision, "brief": B.parse_body(body)}
        sim.publish(rerun, sim.t + timedelta(minutes=1))
        pub = sim.published()
        self.assertEqual(pub["c1b"]["halt"]["commit"], halt["commit"])   # never erased
        self.assertNotEqual(decision["action"], "MERGE")
        self.assertTrue(pub["c1b"]["fence"])
        sim.t += timedelta(hours=1)
        sim.h.commit("data: c")
        nxt = sim.build(sim.t)
        self.assertTrue(sim.publish(nxt, sim.t + timedelta(minutes=1)))
        pub = sim.published()
        self.assertEqual(pub["c1b"]["halt"]["commit"], halt["commit"])
        self.assertIn(pub["c1b"]["checked_through"], sim.index()[1])
        self.assertNotEqual(nxt["decision"]["action"], "MERGE")


if __name__ == "__main__":
    unittest.main()
