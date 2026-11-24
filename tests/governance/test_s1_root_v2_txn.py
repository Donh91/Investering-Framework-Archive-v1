import collections
import importlib.util
import pathlib
import sys
import unittest

P = pathlib.Path(__file__).resolve().parents[2] / "research/s1_root_v2/txn_sim.py"
S = importlib.util.spec_from_file_location("s1_root_v2_txn_sim", P)
SIM = importlib.util.module_from_spec(S)
sys.modules[S.name] = SIM
S.loader.exec_module(SIM)
T = SIM.txn

A, B, C = "a" * 40, "b" * 40, "c" * 40
N = T.CALL_BUDGET["ordinary_merge"]
SUCCESS = (T.POST_RECEIPTS, T.RECONCILE_OWN)


class KeyTest(unittest.TestCase):
    def test_stable(self):
        k = T.idempotency_key(1, 2, A, B, C)
        self.assertEqual(k, T.idempotency_key(1, 2, A, B, C))
        self.assertRegex(k, "^[0-9a-f]{64}$")

    def test_pinned_vector(self):
        import hashlib
        text = "S1_TXN_KEY_v1\nrepo_id=1\npr=2\nhead=%s\nbase_main=%s\nloop_blob=%s\n" % (A, B, C)
        self.assertEqual(T.idempotency_key(1, 2, A, B, C), hashlib.sha256(text.encode()).hexdigest())

    def test_collision_sensitive(self):
        base = (1, 2, A, B, C)
        keys = {T.idempotency_key(*base)}
        for i, alt in enumerate((2, 3, "d" * 40, "d" * 40, "d" * 40)):
            keys.add(T.idempotency_key(*(base[:i] + (alt,) + base[i + 1:])))
        for swapped in ((2, 1, A, B, C), (1, 2, B, A, C), (1, 2, A, C, B), (12, 3, A, B, C), (1, 23, A, B, C)):
            keys.add(T.idempotency_key(*swapped))
        self.assertEqual(len(keys), 11)

    def test_rejects(self):
        for bad in ((True, 2, A, B, C), ("1", 2, A, B, C), (1, 2.0, A, B, C), (0, 2, A, B, C), (1, -2, A, B, C),
                    (1, 2, A[:39], B, C), (1, 2, A + "a", B, C), (1, 2, A.upper(), B, C),
                    (1, 2, "g" * 40, B, C), (1, 2, A, None, C), (1, 2, A, B, C.encode()),
                    (1, 2, A, B, "c" * 39 + "\n")):
            with self.subTest(bad=bad):
                self.assertRaises(ValueError, T.idempotency_key, *bad)


class PlanStepTest(unittest.TestCase):
    """The pure machine on synthetic observations."""

    def setUp(self):
        self.cand = dict(repo_id=9, pr=7, head=A, base_main=B, loop_blob=C)
        self.key = T.idempotency_key(9, 7, A, B, C)
        self.pr = dict(number=7, state="open", merged=False, head=A)
        self.blobs = {"x.md": "1" * 40}

    def comment(self, cid, kind, at=1000, **f):
        return dict(id=cid, author=T.S1_LOGIN, created_at=at, updated_at=at, body=T.render(kind, **f))

    def intent_comment(self, cid=10, at=1000, head=A):
        return self.comment(cid, T.INTENT, at, pr=7, head=head, main=B, repo_id=9, loop=C,
                            key=T.idempotency_key(9, 7, head, B, C))

    def merged(self, **over):
        """A reconcile observation that classifies OWN unless `over` breaks it."""
        led = [self.intent_comment()]
        obs = dict(ledger=led, now=1000 + T.SETTLE_S, run={},
                   pr=dict(number=7, state="closed", merged=True, head=A, merged_at=1005,
                           merge_commit_sha=C, merged_by=T.S1_LOGIN),
                   commit=dict(parents=[B], subject="Change (#7)", files=dict(self.blobs)),
                   on_main="ahead", rule_suite="pass", head_blobs=dict(self.blobs), pr_comments=[])
        for k, val in over.items():
            if k in ("pr", "commit"):
                obs[k].update(val)
            else:
                obs[k] = val
        return obs, T.intents(led)[0]

    def test_no_intent_path(self):
        obs = dict(ledger=[], now=1000, run={}, cand=self.cand)
        self.assertEqual(T.plan_step(dict(obs, cand=None), None).reason, "no_candidate")
        self.assertEqual(T.plan_step(obs, None), T.act(T.READBACK, "pr", need="pr"))
        a = T.plan_step(dict(obs, pr=self.pr), None)
        self.assertEqual((a.kind, a.args["key"], a.args["head"]), (T.POST_INTENT, self.key, A))
        for pr, why in ((dict(self.pr, head=B), "head_changed"), (dict(self.pr, merged=True), "pr_not_open"),
                        (dict(self.pr, state="closed"), "pr_not_open"), (dict(self.pr, merged=None), "pr_not_open"),
                        ("x", "pr_not_open")):
            self.assertEqual(T.plan_step(dict(obs, pr=pr), None), T.act(T.NOOP, why))
        halted = [self.comment(3, T.HALTED, pr="-", head="-", reason="main_health")]
        self.assertEqual(T.plan_step(dict(obs, ledger=halted, pr=self.pr), None).reason, "lane_halted")
        spent = [self.intent_comment(), self.comment(11, T.OP_DONE, intent=10, result="ABSENT")]
        self.assertEqual(T.plan_step(dict(obs, ledger=spent, pr=self.pr), None).reason, "key_spent")
        self.assertEqual(T.plan_step(dict(obs, run={"intent_id": 5}, pr=self.pr), None).reason, "intent_not_durable")

    def test_merge_only_in_the_intent_run_and_only_once(self):
        led = [self.intent_comment()]
        i = T.intents(led)[0]
        obs = dict(ledger=led, now=1002, run={"intent_id": 10}, cand=self.cand)
        self.assertEqual(T.plan_step(obs, i), T.act(T.MERGE, "one_attempt", pr=7, sha=A, method="squash"))
        for status in ("405", "409", "timeout", "sent", "response"):
            a = T.plan_step(dict(obs, run={"intent_id": 10, "merge": status}), i)
            self.assertEqual(a, T.act(T.NOOP, "MERGE_REFUSED(%s)" % status))
        self.assertEqual(T.plan_step(dict(obs, now=1000 + T.DEADLINE_S + 1), i), T.act(T.ABANDON, "deadline"))
        halted = led + [self.comment(12, T.HALTED, pr="-", head="-", reason="main_health")]
        self.assertEqual(T.plan_step(dict(obs, ledger=halted), i), T.act(T.ABANDON, "lane_halted"))
        # another run's intent: never a merge, at any age, whatever the PR looks like
        for now in (1001, 1000 + T.SETTLE_S - 1, 1000 + T.SETTLE_S, 10 ** 7):
            for run in ({}, {"intent_id": 99}):
                a = T.plan_step(dict(obs, now=now, run=run, pr=self.pr), i)
                self.assertNotIn(a.kind, (T.MERGE, T.POST_INTENT))
        self.assertEqual(T.plan_step(dict(obs, run={}), i), T.act(T.NOOP, "intent_young"))

    def test_duplicate_intent_loses(self):
        led = [self.intent_comment(10), self.intent_comment(11, at=1001)]
        first, second = T.intents(led)
        self.assertEqual(T.plan_step(dict(ledger=led, now=1002, run={"intent_id": 11}), second).kind, T.ABANDON)
        self.assertEqual(T.plan_step(dict(ledger=led, now=1002, run={"intent_id": 10}), first).kind, T.MERGE)
        self.assertEqual(T.plan_step(dict(ledger=led, now=9999, run={}), second), T.act(T.ABANDON, "DUPLICATE"))

    def test_authentic_intents_only(self):
        good = self.intent_comment()
        self.assertEqual(len(T.intents([good])), 1)
        forged_key = dict(good, body=good["body"].replace(self.key, "0" * 64))
        rebound = dict(good, body=good["body"].replace(A, "d" * 40))
        for bad in (dict(good, updated_at=1001), dict(good, author="someone"), forged_key, rebound,
                    dict(good, body=T.INTENT + "\npr: 7"), dict(good, body="")):
            self.assertEqual(T.intents([bad]), [])

    def test_open_and_closed(self):
        led = [self.intent_comment()]
        i = T.intents(led)[0]
        self.assertTrue(T.is_open(led, i))
        for c in (self.comment(11, T.MERGE_RCPT, pr=7), self.comment(11, T.HALTED, pr=7),
                  self.comment(11, T.OP_DONE, intent=10, result="ABSENT")):
            self.assertFalse(T.is_open(led + [c], i))
        for c in (self.comment(9, T.HALTED, pr=7), self.comment(11, T.HALTED, pr="-"),
                  self.comment(11, T.MERGE_RCPT, pr=8), self.comment(11, T.OP_DONE, intent=4, result="ABSENT"),
                  dict(self.comment(11, T.HALTED, pr=7), author="someone")):
            self.assertTrue(T.is_open(led + [c], i))

    def test_classify(self):
        obs, i = self.merged()
        self.assertEqual(T.classify(obs, i), (T.OWN, "verified"))
        cases = [
            (dict(pr=dict(merged=False)), T.ABSENT, "not_merged"),
            (dict(pr=dict(merged=False, head=B)), T.ABSENT, "HEAD_CHANGED"),
            (dict(pr=dict(head=B)), T.FOREIGN, "other_head"),
            (dict(pr=dict(merged_by="someone-else")), T.FOREIGN, "other_actor"),
            (dict(pr=dict(merged_at=999)), T.FOREIGN, "before_intent"),
            (dict(pr=dict(merged_at=1001 + T.WINDOW_S)), T.FOREIGN, "after_window"),
            (dict(commit=dict(parents=[B, A])), T.FOREIGN, "not_squash"),
            (dict(pr=dict(merged_at=1000)), T.UNKNOWN, "same_second_as_intent"),
            (dict(pr=dict(merged_at=None)), T.UNKNOWN, "merged_at_unreadable"),
            (dict(pr=dict(merged=None)), T.UNKNOWN, "pr_malformed"),
            (dict(pr=dict(number=8)), T.UNKNOWN, "pr_malformed"),
            (dict(commit=dict(parents=None)), T.UNKNOWN, "commit_malformed"),
            (dict(commit=dict(parents=[])), T.FOREIGN, "not_squash"),
            (dict(commit=dict(subject="Change (#77)")), T.UNKNOWN, "subject"),
            (dict(commit=dict(subject="(#7) Change")), T.UNKNOWN, "subject"),
            (dict(commit=dict(files={"x.md": "2" * 40})), T.UNKNOWN, "blob_mismatch"),
            (dict(commit=dict(files=dict(self.blobs, extra="3" * 40))), T.UNKNOWN, "blob_mismatch"),
            (dict(head_blobs={}, commit=dict(files={})), T.UNKNOWN, "blob_mismatch"),
            (dict(on_main="diverged"), T.UNKNOWN, "not_on_main"),
            (dict(on_main="behind"), T.UNKNOWN, "not_on_main"),
            (dict(rule_suite="bypass"), T.UNKNOWN, "bypass"),
            (dict(rule_suite="unavailable"), T.UNKNOWN, "bypass"),
        ]
        for over, cls, why in cases:
            with self.subTest(over=over):
                o, i = self.merged(**over)
                self.assertEqual(T.classify(o, i), (cls, why))
        o, i = self.merged()
        o["ledger"] = o["ledger"] + [dict(id=11, author=T.S1_LOGIN, created_at=1, updated_at=1,
                                          body=T.OWNER_NOTE + "\npr: 7")]
        self.assertEqual(T.classify(o, i), (T.OWN, "verified"))
        self.assertEqual(T.plan_step(o, i), T.act(T.HALT_UNKNOWN, "owner_marker", halt="reconcile_readback"))
        mine = T.plan_step(dict(o, run={"intent_id": 10, "merge": "OK"}), i)   # our own success response
        self.assertEqual(mine.kind, T.POST_RECEIPTS)
        for need in ("pr", "commit", "on_main", "rule_suite", "head_blobs"):
            o, i = self.merged()
            del o[need]
            self.assertEqual(T.plan_step(o, i), T.act(T.READBACK, need, need=need))

    def test_login_alone_never_proves_own(self):
        """Same login, everything else wrong or unreadable: never OWN."""
        for over in (dict(pr=dict(head=B)), dict(pr=dict(merged_at=999)), dict(commit=dict(parents=[B, A])),
                     dict(commit=dict(subject="x")), dict(on_main="diverged"), dict(rule_suite="?")):
            o, i = self.merged(**over)
            self.assertEqual(o["pr"]["merged_by"], T.S1_LOGIN)
            self.assertNotEqual(T.classify(o, i)[0], T.OWN)
            self.assertNotIn(T.plan_step(o, i).kind, SUCCESS)

    def test_unknown_halts_and_is_never_success(self):
        for over in (dict(commit=dict(subject="x")), dict(on_main="diverged"), dict(rule_suite="bypass"),
                     dict(commit=dict(files={})), dict(pr=dict(merged_at=1000))):
            o, i = self.merged(**over)
            a = T.plan_step(o, i)
            self.assertEqual((a.kind, a.args["halt"]), (T.HALT_UNKNOWN, "reconcile_readback"))
            a = T.plan_step(dict(o, run={"intent_id": 10, "merge": "OK"}), i)
            self.assertEqual((a.kind, a.args["halt"]), (T.HALT_UNKNOWN, "readback"))
        # the run's own success response contradicted by native state is UNKNOWN, not ABSENT/FOREIGN
        for over in (dict(pr=dict(merged=False)), dict(pr=dict(head=B)), dict(pr=dict(merged_by="x"))):
            o, i = self.merged(**over)
            self.assertEqual(T.plan_step(dict(o, run={"intent_id": 10, "merge": "OK"}), i).kind, T.HALT_UNKNOWN)

    def test_settlements(self):
        o, i = self.merged(pr=dict(merged=False))
        self.assertEqual(T.plan_step(o, i), T.act(T.ABANDON, "not_merged"))
        o, i = self.merged(pr=dict(merged=False, head=B))
        self.assertEqual(T.plan_step(o, i), T.act(T.ABANDON, "HEAD_CHANGED"))
        o, i = self.merged(pr=dict(head=B))
        self.assertEqual(T.plan_step(o, i), T.act(T.RECONCILE_FOREIGN, "other_head"))

    def test_receipts_are_separate_ordered_steps(self):
        self.assertEqual(T.RECEIPT_ORDER, (T.ITEM, T.CLOSURE, T.MERGE_RCPT))
        o, i = self.merged()
        run = {"intent_id": 10, "merge": "OK"}
        for done, nxt in (([], T.ITEM), ([T.ITEM], T.CLOSURE), ([T.ITEM, T.CLOSURE], T.MERGE_RCPT)):
            a = T.plan_step(dict(o, run=dict(run, posted=done)), i)
            self.assertEqual(a, T.act(T.POST_RECEIPTS, nxt, receipt=nxt, origin="S1_RUN"))
            pc = [self.comment(20 + n, k, key=i["key"]) for n, k in enumerate(done)]
            a = T.plan_step(dict(o, pr_comments=pc), i)
            self.assertEqual(a, T.act(T.RECONCILE_OWN, nxt, receipt=nxt, origin="UNKNOWN"))
        del o["pr_comments"]
        self.assertEqual(T.plan_step(o, i).args, {"need": "pr_comments"})
        o, i = self.merged()
        other = [self.comment(20, T.ITEM, key="0" * 64), dict(self.comment(21, T.ITEM, key=i["key"]), author="x")]
        self.assertEqual(T.plan_step(dict(o, pr_comments=other), i).args["receipt"], T.ITEM)


class FaultTest(unittest.TestCase):
    """Properties over ALL injected faults, judged against the fake's ground truth."""

    def check(self, gh, cand, outs, tag, concurrent=False):
        v = SIM.violations(gh, cand, concurrent)
        s = SIM.summary(gh)
        if gh.tamper == "two_parent" and s == "FOREIGN":
            # A two-parent result of S1's own squash call cannot occur natively. If it did and
            # the run died, B3 case (ii) files it FOREIGN without a halt: recorded, not hidden.
            v = [x for x in v if x != "s1_merge_unaccounted"]
        self.assertEqual(v, [], tag)
        for o in outs:
            if o is not None and o.kind in SUCCESS and o.args["receipt"] == T.MERGE_RCPT:
                self.assertTrue(s.startswith("MERGED"), tag)
            if o is not None and o.kind == T.HALT_UNKNOWN:
                self.assertEqual(s, "HALTED", tag)
        return s

    def test_clean_run(self):
        gh, cand, outs = SIM.scenario()
        self.assertEqual(self.check(gh, cand, outs, "clean"), "MERGED:S1_RUN")
        self.assertEqual(outs[0], T.act(T.POST_RECEIPTS, T.MERGE_RCPT, receipt=T.MERGE_RCPT, origin="S1_RUN"))
        self.assertEqual([o.reason for o in outs[1:]], ["key_spent"] * 3)
        self.assertEqual(len(gh.comments[SIM.LEDGER]), 2)
        self.assertEqual(len(gh.comments[gh.PR]), 2)

    def test_every_crash_point(self):
        seen = {}
        for k in range(N + 1):
            gh, cand, outs = SIM.scenario(crash=k)
            seen[k] = self.check(gh, cand, outs, "crash=%d" % k)
        # 0-2 nothing durable; 3-4 intent, no merge; 5+ merged: receipts completed by RECONCILE
        self.assertEqual([seen[k] for k in range(N + 1)],
                         ["MERGED:S1_RUN"] * 3 + ["ABSENT"] * 2 + ["MERGED:UNKNOWN"] * 7 + ["MERGED:S1_RUN"])

    def test_recovery_table(self):
        """Each interruption named in the contract, and what the next tick does."""
        rows = {  # crash before call k of t1 -> (settlement, action of the recovering tick)
            4: ("ABSENT", T.ABANDON),            # intent posted, no merge
            6: ("MERGED:UNKNOWN", T.RECONCILE_OWN),   # merged, no readback
            9: ("MERGED:UNKNOWN", T.RECONCILE_OWN),   # readback done, no receipt
            10: ("MERGED:UNKNOWN", T.RECONCILE_OWN),  # receipts partially posted
            11: ("MERGED:UNKNOWN", T.RECONCILE_OWN),
        }
        for k, (want, kind) in rows.items():
            gh, cand, outs = SIM.scenario(crash=k)
            self.assertEqual((self.check(gh, cand, outs, k), outs[1].kind), (want, kind), k)
        gh, cand, outs = SIM.scenario(fault=(4, "lost"))          # merge sent, response lost
        self.assertEqual(outs[0], T.act(T.NOOP, "MERGE_REFUSED(timeout)"))
        self.assertEqual((self.check(gh, cand, outs, "lost"), outs[1].kind), ("MERGED:UNKNOWN", T.RECONCILE_OWN))
        gh, cand, outs = SIM.scenario(fault=(4, "error"))         # merge never arrived
        self.assertEqual((self.check(gh, cand, outs, "error"), len(gh.log)), ("ABSENT", 0))
        gh, cand, outs = SIM.scenario(crash=4, event=(4, "owner_push"))
        self.assertEqual(fieldsof(gh, T.OP_DONE)["reason"], "HEAD_CHANGED")
        self.assertEqual(len(gh.log), 0)

    def test_crash_and_call_fault_times_foreign_event(self):
        seen = collections.Counter()
        for ev in [None] + [(j, name) for name in SIM.EVENTS for j in range(N + 1)]:
            for k in range(N + 1):
                gh, cand, outs = SIM.scenario(crash=k, event=ev)
                seen[self.check(gh, cand, outs, ("crash", k, ev))] += 1
            for k in range(N):
                for mode in SIM.MODES:
                    gh, cand, outs = SIM.scenario(fault=(k, mode), event=ev)
                    seen[self.check(gh, cand, outs, ("fault", k, mode, ev))] += 1
        for outcome in ("MERGED:S1_RUN", "MERGED:UNKNOWN", "HALTED", "ABSENT", "FOREIGN", "NO_TRANSACTION"):
            self.assertGreater(seen[outcome], 20, outcome)      # the sweep is not vacuous
        self.assertEqual(set(seen), {"MERGED:S1_RUN", "MERGED:UNKNOWN", "HALTED", "ABSENT", "FOREIGN",
                                     "NO_TRANSACTION"})

    def test_double_crash(self):
        for k in range(N + 1):
            for k2 in range(N + 1):
                for ev in (None, (k, "owner_merge"), (k, "owner_push_merge")):
                    gh, cand, outs = SIM.scenario(crash=k, crash2=k2, event=ev, ticks=4)
                    self.check(gh, cand, outs, ("double", k, k2, ev))

    def test_unprovable_merge_halts_at_every_fault(self):
        for tamper in SIM.TAMPERS:
            kinds = collections.Counter()
            for k in range(N + 1):
                for fault in [None] + [(j, m) for j in range(N) for m in SIM.MODES]:
                    gh, cand, outs = SIM.scenario(crash=k, fault=fault, tamper=tamper)
                    s = self.check(gh, cand, outs, (tamper, k, fault))
                    self.assertFalse(s.startswith("MERGED"), (tamper, k, fault))
                    if any(e["applied"] for e in gh.log):
                        # S1's own two-parent "squash" cannot happen natively; B3 (ii) files it FOREIGN
                        self.assertIn(s, ("HALTED", "FOREIGN") if tamper == "two_parent" else ("HALTED",),
                                      (tamper, k, fault))
                    kinds[s] += 1
            self.assertGreater(kinds["HALTED"], 50, tamper)

    def test_two_parent_own_response_halts(self):
        gh, cand, outs = SIM.scenario(tamper="two_parent")
        self.assertEqual((SIM.summary(gh), outs[0].reason), ("HALTED", "response_contradicts_native:not_squash"))

    def test_foreign_merges_get_no_merge_receipt(self):
        for name in ("owner_merge_2p", "owner_push_merge", "other_login_merge", "owner_merge_late"):
            for j in range(N + 1):
                for k in range(N + 1):
                    gh, cand, outs = SIM.scenario(crash=k, event=(j, name))
                    s = self.check(gh, cand, outs, (name, j, k))
                    if gh.log and gh.log[0]["actor"] != "s1" and gh.log[0]["applied"]:
                        self.assertIn(s, ("FOREIGN", "NO_TRANSACTION", "ABSENT"), (name, j, k))

    def test_shared_identity_residual(self):
        """The owner squashes the intent's head inside the window, as the same login.
        Natively this IS the operation (B3 case i): it is reconciled, but its origin is
        UNKNOWN and never S1_RUN. Only an owner marker makes it a halt."""
        gh, cand, outs = SIM.scenario(crash=4, event=(4, "owner_merge"))
        self.assertEqual(gh.log, [dict(actor="owner", sha=None, applied=True, prior_intent=False, head=cand["head"])])
        self.assertEqual(self.check(gh, cand, outs, "residual"), "MERGED:UNKNOWN")
        self.assertEqual(fieldsof(gh, T.MERGE_RCPT)["reconciled"], "True")
        gh = SIM.FakeGitHub()
        cand = gh.candidate()
        p = SIM.Proc(gh, cand, "t1")
        for _ in range(4):
            p.step()
        gh.event("owner_merge")
        gh.event("owner_note")
        outs = []
        SIM.recover(gh, cand, 2, outs)
        self.assertEqual((self.check(gh, cand, outs, "marker"), outs[0].reason), ("HALTED", "owner_marker"))

    def test_main_moving_is_recorded_not_fatal(self):
        gh, cand, outs = SIM.scenario(event=(4, "main_moves"))
        self.assertEqual(self.check(gh, cand, outs, "main"), "MERGED:S1_RUN")
        self.assertEqual(fieldsof(gh, T.MERGE_RCPT)["base_drift"], "True")
        gh, cand, outs = SIM.scenario(event=(8, "main_moves"))
        self.assertEqual(fieldsof(gh, T.MERGE_RCPT)["base_drift"], "False")

    def test_head_push_between_checks(self):
        for j in range(N + 1):
            gh, cand, outs = SIM.scenario(event=(j, "owner_push"))
            s = self.check(gh, cand, outs, j)
            self.assertEqual(s, "NO_TRANSACTION" if j < 2 else "ABSENT" if j < 5 else "MERGED:S1_RUN", j)
            if 2 <= j < 5:      # natively refused by sha=; never merged at the new head, never re-bound
                self.assertFalse(gh.pr["merged"])
                self.assertEqual([(e["actor"], e["applied"]) for e in gh.log], [("s1", False)])

    def test_duplicate_tick_all_interleavings(self):
        n, both = 0, 0
        for gh, cand, procs, sched in SIM.duplicate_ticks():
            outs = [p.out for p in procs]
            SIM.recover(gh, cand, 3, outs)
            self.assertEqual(self.check(gh, cand, outs, sched, concurrent=True), "MERGED:S1_RUN", sched)
            self.assertEqual(len(gh.log), 1, sched)
            self.assertEqual(sum(f == T.MERGE_RCPT for f in kinds(gh)), 1, sched)
            both += sum(f == T.INTENT for f in kinds(gh)) == 2
            n += 1
        self.assertGreater(n, 50)
        self.assertGreater(both, 0)      # the race where both post an intent is reached

    def test_duplicate_reconcilers_all_interleavings(self):
        n = 0
        for crash in range(3, N + 1):
            for gh, cand, procs, sched in SIM.duplicate_reconcilers(crash):
                outs = [p.out for p in procs]
                SIM.recover(gh, cand, 2, outs)
                self.check(gh, cand, outs, (crash, sched), concurrent=True)
                self.assertLessEqual(len(gh.log), 1)
                n += 1
        self.assertGreater(n, 100)

    def test_call_counts(self):
        got = SIM.measure_call_counts()
        self.assertEqual({k: v[0] for k, v in got.items()}, T.CALL_BUDGET)
        ops = got["ordinary_merge"][1]
        self.assertEqual(ops, ["list_comments", "get_pr", "post_comment", "list_comments", "merge", "get_pr",
                               "get_commit", "compare", "rule_suite", "post_comment", "post_comment",
                               "post_comment"])
        self.assertEqual((ops.count("merge"), ops.count("post_comment")), (1, 4))
        for name in ("noop_head_changed", "noop_lane_halted", "noop_intent_young"):
            self.assertLessEqual(got[name][0], 3)
            self.assertNotIn("merge", got[name][1])
            self.assertNotIn("post_comment", got[name][1])
        for name in ("reconcile_own", "reconcile_absent", "reconcile_foreign"):
            self.assertNotIn("merge", got[name][1])       # RECONCILE never merges


def kinds(gh):
    return [SIM.fields(c)[0] for c in gh.comments[SIM.LEDGER]]


def fieldsof(gh, kind):
    return next(SIM.fields(c)[1] for c in gh.comments[SIM.LEDGER] if SIM.fields(c)[0] == kind)


if __name__ == "__main__":
    unittest.main()
