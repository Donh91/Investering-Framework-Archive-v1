"""S1 executor safety invariants (fix round 4, ChatGPT #173/7186140947): one class per invariant, each with its own
adversarial cases, kept in the regression suite. The larger suites (test_s1_decision_v1.py, test_s1_executor_v1.py)
hold the full matrices; this module states each invariant once and attacks it directly.

Fixtures only, no network. A green finite suite is not a proof of a universal property: each class names what it
attacks and nothing more.
"""
import copy
import sys
import unittest
import unittest.mock
from datetime import timedelta
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "scripts" / "governance"))
sys.path.insert(0, str(HERE))
import s1_decision_v1 as D  # noqa: E402
import s1_tick_brief_v1 as B  # noqa: E402
import test_s1_decision_v1 as TD  # noqa: E402
import test_s1_executor_v1 as TE  # noqa: E402
import test_s1_tick_brief_v1 as TB  # noqa: E402

HEAD, RECALL = TB.HEAD, D.RECALL_POLICY
PEM = "-----BEGIN " + "PRIVATE KEY-----"                            # split: no key-shaped literal in this file


def decide(*mutations, mode="LIVE", policy=RECALL):
    return TD.decide(TD._chain(*mutations), mode, policy)


def code_file(name, patch):
    return lambda w: TD.set_files(w, [TD.file_(name, "modified", 2, 1, patch)])


class Authority(unittest.TestCase):
    """Only the decision that was published, verified and re-verified at the write boundary is ever executed, and only
    in LIVE; every write needs the live hold, switch and contract."""

    def test_no_write_without_live_mode_publication_and_a_live_switch(self):
        for mode in ("SHADOW", "OFF"):
            out, gh, _n, _d = TE.execute(mode=mode, mutate=TE.BEAT)
            self.assertEqual(gh.writes, [], mode)
        out, gh, _n, _d = TE.execute(mutate=TE.BEAT, live=lambda w, g, n: setattr(g, "issue_body", None))
        self.assertEqual((gh.writes, out["health"]), ([], "DEGRADED"))
        out, gh, _n, _d = TE.execute(mutate=TE.BEAT, live=lambda w, g, n: w["pins_actual"].update({B.CONTRACT_FILE: "0" * 40}))
        self.assertEqual(gh.writes, [])

    def test_the_merge_gateway_needs_this_runs_intent_and_final_look(self):
        run, gh, _n, body, d = TE.setup()
        run.brief, run.decision, run.mode = B.parse_body(body), d, "LIVE"
        with self.assertRaises(TE.E.Stop):
            run.write("merge", pr=7, sha=HEAD)
        self.assertEqual(gh.writes, [])


class Independence(unittest.TestCase):
    """A review counts only from someone who did not write the head; a Claude veto is lifted only by a complete,
    eligible, independent APPROVE (7186140947 finding 02); two fallback runs must be two runs of the execute job."""

    def test_an_incomplete_approval_never_lifts_an_earlier_veto(self):
        veto = TD.claude_receipt(TD.CLAUDE_OK.replace("APPROVE", "BLOCK"), cid=19)
        incomplete = {
            "lane_eligible NO": TD.claude_receipt(TD.CLAUDE_OK.replace("lane_eligible: YES", "lane_eligible: NO"), cid=21),
            "no independence": TD.claude_receipt(TD.CLAUDE_OK.replace("independence: INDEPENDENT_DETACHED\n", ""), cid=21),
            "an unknown independence": TD.claude_receipt(TD.CLAUDE_OK.replace("INDEPENDENT_DETACHED", "TRUST_ME"), cid=21),
            "a short report blob": TD.claude_receipt(TD.CLAUDE_OK.replace("a" * 40, "a" * 39), cid=21),
            "another author": TD.claude_receipt(user={"login": "eve", "id": 9, "type": "User"}, cid=21),
        }
        for name, approve in incomplete.items():
            for route_extra in (lambda w: None, TD.codex_limit):                   # the veto holds on route (a) and (c) too
                with self.subTest(name=name):
                    d, b = decide(route_extra, veto, approve)
                    self.assertIn(TB.entry(b)["thin"]["claude"], ("VETO", "NOT_PROVEN"), name)
                    self.assertNotEqual(d["action"], "MERGE", name)
        d, b = decide(TD.no_codex, veto, TD.claude_receipt(cid=21))               # the control: a complete newer APPROVE lifts it
        self.assertEqual(d["merge"]["review"], "CLAUDE")

    def test_independence_is_a_known_value(self):
        self.assertEqual(B.INDEPENDENCE, ("INDEPENDENT_DETACHED", "SELF_AUTHORED_DESIGN"))
        d, _b = decide(TD.no_codex, TD.claude_receipt(TD.CLAUDE_OK.replace("INDEPENDENT_DETACHED", "SELF_AUTHORED_DESIGN")))
        self.assertEqual(d["merge"]["review"], "CLAUDE")


class Freshness(unittest.TestCase):
    """Every mutable gate is read again after the intent; the hold, switch and contract are the last reads."""

    def test_a_change_after_the_intent_stops_the_call(self):
        late = lambda change: (lambda w, g, n: setattr(g, "after_intent", lambda g2: change(w, g2)))
        for name, change in (("P1 thread", lambda w, g: w["pr"][7].update(threads=[{"resolved": False, "first_body": "P1"}])),
                             ("switch", lambda w, g: w["pins_actual"].update({B.SWITCH: "0" * 40})),   # LIVE v1: gate 2 (i), no live hold read
                             ("item risk", lambda w, g: w["pr"][7]["comments"].append(TB.comment(80, "S1_ITEM_v1\nitem: pr:7\nstate: REVIEW\nkind: FIX\nrisk: EXTREME\ncontract=44444444", TB.OWNER, 0)))):
            out, gh, _n, _d = TE.execute(mutate=TE.BEAT, live=late(change))
            self.assertEqual(TE.tokens(gh), ["S1_LANE_MERGE_INTENT_v1"], name)
            self.assertTrue(out["result"].startswith("MERGE_ABORTED_AFTER_INTENT("), name)


class FailClosed(unittest.TestCase):
    """Anything unknown parks; an unproven history segment merges nothing; an unknown allowlist admits nothing."""

    def test_unknowns_park(self):
        for name, m in (("no allowlist", lambda w: w["switch"].pop("fallback_data_allowlist", None)),
                        ("commit list incomplete", lambda w: w["pr"][7].update(commits_complete=False)),
                        ("ledger unreadable", lambda w: w.update(issue_comments_complete=False))):
            d, _b = decide(TD.data_pr, TD.codex_limit, m)
            self.assertEqual(d["action"], "NOOP", name)

    def test_a_c1b_segment_past_the_cap_is_a_gap_not_clean(self):
        trees = {"A": ("a1", "t", "g", "x", "f"), "B": ("b2", "t", "g", "x", "f")}
        clean = [(f"{k + 1:040x}", [f"{k:040x}"], "data: hourly", "A") for k in range(5)]
        late = clean + [("9" * 40, [clean[-1][0]], "fix: direct", "B"), ("8" * 40, ["9" * 40], "revert", "A")]
        unproven = []
        self.assertIsNone(B.c1b_scan(late, "0" * 40, "A", lambda key: trees[key], search_reads=3, unproven=unproven))
        self.assertEqual(len(unproven), 1)
        self.assertEqual(unproven[0]["unread"], 4)
        # fix round 6: the capped rest is the brief's OPEN segment (checked_through stops at the proven point; the next
        # build resumes it), never a clean range: no merge, and it is on the owner's line
        proven = "5" * 40
        d, _b = decide(lambda w: w["c1b"].update(checked_through=proven, open={"from": proven, "to": w["main_sha"], "reason": "C1b:capped_equal_ends", "unread": 4}))
        self.assertEqual(d["action"], "NOOP")
        self.assertIn("lane:C1b:open_segment", d["skipped"])
        self.assertIn("C1B_GAP(window=4)", d["status_lines"][0])


class HardLines(unittest.TestCase):
    """Money, credentials, custody and Round 3 are never an executor merge on ANY route (7185637589 #3)."""

    def test_reviewed_money_or_credential_code_still_goes_to_the_owner(self):
        for name, f in (("a transaction call", code_file("scripts/zz/runner.py", "@@\n+client.send_transaction(signed)\n")),
                        ("a key read", code_file("scripts/zz/runner.py", "@@\n+key = os.environ['API_" "KEY']\n")),
                        ("Round 3", code_file("scripts/zz/runner.py", "@@\n+load('round3/outcomes.csv')\n"))):
            for route_name, review in (("codex", lambda w: None), ("claude", TD._chain(TD.no_codex, TD.claude_receipt())),
                                       ("claude while codex is pending", TD._chain(lambda w: w["pr"][7].update(comments=[TB.comment(11, "@codex review", minutes_ago=30)]), TD.claude_receipt()))):
                with self.subTest(name=name, route=route_name):
                    d, _b = decide(f, review)
                    self.assertEqual(d["action"], "NOOP")
                    self.assertTrue(any(s.startswith("7:C2:judgment:diff:") for s in d["skipped"]), d["skipped"])

    def test_a_data_pr_carries_its_words_but_never_a_secret(self):
        words = lambda w: w["pr"][7]["files"][1].update(patch='@@\n+{"wallet_order_trade": "position", "api": "key"}')
        d, _b = decide(TD.data_pr, words, TD.codex_limit)
        self.assertEqual(d["merge"]["review"], "FALLBACK(UNAVAILABLE)")            # data words are no gate for automation's data
        for name, patch in (("a PEM key", f"@@\n+{PEM}\n+MII\n"), ("a GitHub token", "@@\n+" + "gh" + "p_" + "A" * 36 + "\n"), ("no patch", None)):
            leak = lambda w, patch=patch: w["pr"][7]["files"][1].update(patch=patch)
            d, b = decide(TD.data_pr, leak, TD.codex_limit)
            self.assertNotEqual(d["action"], "MERGE", name)
            self.assertIs(TB.entry(b)["thin"]["data_route"], False, name)

    def test_code_never_takes_the_unreviewed_route(self):
        for name, files in (("python", code_file("scripts/zz/tool.py", "@@\n+x = 1\n")), ("a test", code_file("tests/zz/test_x.py", "@@\n+x = 1\n")),
                            ("a workflow", code_file(".github/workflows/x.yml", "@@\n+on: push\n")), ("a document", code_file("docs/a.md", "@@\n+x\n"))):
            for signal in (TD.codex_limit, TD.codex_silent, TD.codex_out_of_usage):
                d, _b = decide(files, signal)
                self.assertEqual(d["action"], "NOOP", name)


class Recoverability(unittest.TestCase):
    """A run that dies anywhere after a write leaves a state the next run can settle; nothing claims more than it saw."""

    def test_a_reconciled_receipt_claims_no_privacy_it_did_not_see(self):
        body = D.merge_receipt_body({"merge": {"review": "FALLBACK(SILENT)"}}, 1, 300, {"pr": 7, "head": HEAD, "merge_commit": "9" * 40, "main_after": "a" * 40, "paths": 2},
                                    555, None, reconciled=True)
        self.assertIn("privacy=UNVERIFIED run=unavailable", body.splitlines())
        self.assertNotIn("privacy=NO_RESTRICTED_CONTENT", body)

    def test_an_unbound_intent_is_never_a_verified_merge(self):
        rc = TE.Reconcile()
        out, gh, _n, _d = TE.execute(mutate=lambda w: rc.intent(w, paths=""), live=rc.merged())
        self.assertEqual(gh.writes, [])


class EvidenceHonesty(unittest.TestCase):
    """Health is never OK when verification was incomplete; settlement needs exact, native evidence."""

    def test_health(self):
        for result in ("SOURCE_UNVERIFIED(3)", "BRIEF_UNVERIFIED(publication:decision_differs)"):
            self.assertEqual(TE.E.health_state(result, [], None), "DEGRADED", result)
        # fix round 5 (P1-08): an unread hold is a stop of kind UNVERIFIED (the default kind of every Stop)
        self.assertEqual(TE.E.Stop("hold_unreadable:intent(500)").kind, TE.E.UNVERIFIED)
        self.assertEqual(TE.E.health_state("NOTHING_ACTIONABLE(skipped=hold_unreadable:intent(500))", [], None, TE.E.UNVERIFIED), "UNVERIFIED")

    def test_a_stale_receipt_never_settles_an_intent(self):
        intent = TB.comment(300, TE.INTENT + "\n" + TE.RUN_LINE.format(540), TB.BOT, 30)
        stale = TB.comment(301, f"S1_LANE_MERGE_v1\npr: 7\nhead: {'c' * 40}\nmerge: {'9' * 40}\nintent: 300", TB.OWNER, 29)
        merged = lambda n: {"merged": True, "merge_commit_sha": "9" * 40, "head_sha": HEAD}
        self.assertEqual([i["id"] for i in B.open_intents([intent, stale], TB.NOW, 0, None, merged)], [300])


class RecallClosure(unittest.TestCase):
    """A fallback merge stays pending until Codex's own completed review; bookkeeping follows native state."""

    def test_a_forged_clear_neither_clears_nor_blocks_cleanup(self):
        pending = {"id": 1, "body": f"S1_CODEX_RECALL_PENDING_v1\npr: 8\nhead: {'d' * 40}\nmerge: {'1' * 40}", "user": dict(TB.BOT),
                   "created_at": TB.ts(100), "updated_at": TB.ts(100)}
        forged = dict(pending, id=2, body=f"S1_CODEX_RECALL_CLEARED_v1\npr: 8\nhead: {'d' * 40}\ncodex: FINAL", user=dict(TB.OWNER))
        self.assertEqual(len(B.recalls([pending, forged])), 1)                      # still a recall; pending is native state
        items = [dict(r, codex="FINAL") for r in B.recalls([pending, forged])]
        self.assertEqual(B.recall_publish(items), items)                            # still listed, so the executor can clean the label


# ----------------------------------------------------------------------------------------------- fix round 5
def data_world(*mutations):
    w = TD.thin_world("LIVE", RECALL)
    TD.data_pr(w)
    for m in mutations:
        m(w)
    return w


def data_route_of(w):
    return D.data_route(w["pulls"][0], w["pr"][7]["files"], True, w["pr"][7]["commits"], True, D.fallback_allowlist(w["switch"]))


WEEKLY = "04_MARKET_LEARNING/shadow_registry/weekly/{}.json"


class FixRound5DataContract(unittest.TestCase):
    """#173/7188234670 P1-01 and P1-02: route (c)'s data contract is EXACT, and an unlinked writer is unknown."""

    def test_exactly_the_two_files_of_the_head_branchs_week(self):
        self.assertEqual(data_route_of(data_world()), (True, None))                    # the control: #2314's shape, linked to the bot
        latest, weekly = TD.file_(TD.DATA_FILES[0], "modified", 3, 3, "@@\n+x"), lambda week: TD.file_(WEEKLY.format(week), "added", 3, 0, "@@\n+x")
        cases = {
            "LATEST only": [latest], "the weekly file only": [weekly("2026-W48")],
            "LATEST and two weekly files": [latest, weekly("2026-W48"), weekly("2026-W47")],
            "the weekly file of another week": [latest, weekly("2026-W47")],
            "two LATEST rows": [latest, dict(latest)],
        }
        for name, files in cases.items():
            with self.subTest(name):
                got = data_route_of(data_world(lambda w, files=files: TD.set_files(w, files)))
                self.assertEqual(got[0], False, name)
                self.assertIn(got[1], ("path_set", "week", "path"), name)
        for ref_week, ok in (("2026-W00", False), ("2026-W54", False), ("2025-W53", False), ("2026-W53", True), ("2026-W01", True)):
            with self.subTest(week=ref_week):
                w = data_world(lambda w: w["pulls"][0]["head"].update(ref=f"automation/shadow-registry-{ref_week}"),
                               lambda w: TD.set_files(w, [latest, weekly(ref_week)]))
                self.assertEqual(data_route_of(w)[0], ok, ref_week)
        self.assertTrue(D.iso_week_ok("2026-W53") and not D.iso_week_ok("2025-W53") and not D.iso_week_ok("2026-W00") and not D.iso_week_ok("x"))
        # an allowlist whose path names the week while its branch pattern does not is malformed: route (c) merges nothing
        doc = copy.deepcopy(TD.SHIPPED_SWITCH["fallback_data_allowlist"])
        doc["entries"][0]["head_ref"] = "^automation/shadow-registry-[0-9]{4}-W[0-9]{2}$"
        self.assertIsNone(D.fallback_allowlist({"fallback_data_allowlist": doc}))

    def test_an_unlinked_or_foreign_commit_identity_is_unknown(self):
        person = {"login": "someone", "id": 5, "type": "User"}
        for name, author, committer in (("null / null (#2314)", None, None), ("null / bot", None, dict(B.ACTIONS_BOT)), ("bot / null", dict(B.ACTIONS_BOT), None),
                                        ("a person / bot", person, dict(B.ACTIONS_BOT)), ("the bot's login, another id", dict(B.ACTIONS_BOT, id=1), dict(B.ACTIONS_BOT))):
            with self.subTest(name):
                w = data_world(lambda w: w["pr"][7].update(commits=[dict(c, author=author, committer=committer) for c in w["pr"][7]["commits"]]))
                self.assertEqual(data_route_of(w), (False, "commit_identity"), name)

    def test_route_c_ships_off_and_parks(self):
        self.assertEqual(TD.SHIPPED_SWITCH["fallback_route"], "OFF")
        d, _b = decide(TD.data_pr, TD.codex_limit, lambda w: w["switch"].update(fallback_route="OFF"))
        self.assertEqual((d["action"], d["skipped"][0]), ("NOOP", "7:C5:fallback_parked:route_off"))
        for value in ("on", True, "ON "):
            d, _b = decide(TD.data_pr, TD.codex_limit, lambda w, value=value: w["switch"].update(fallback_route=value))
            self.assertEqual(d["action"], "NOOP", value)
        d, _b = decide(TD.data_pr, TD.codex_limit)                                    # the fixture turns it ON: the route itself works
        self.assertEqual((d["merge"]["review"], d["merge"]["data"]), ("FALLBACK(UNAVAILABLE)", True))


class FixRound5HighOnlyOnRouteC(unittest.TestCase):
    """#173/7188234670 P1-03 and owner addendum d: the stored-data HIGH admission holds on route (c) ALONE."""

    def test_a_reviewed_data_pr_is_high_and_the_owners(self):
        words = lambda w: w["pr"][7]["files"][1].update(patch='@@\n+{"wallet_order_trade": "position"}')
        for name, review in (("codex", lambda w: None), ("claude", TD._chain(TD.no_codex, TD.claude_receipt()))):
            with self.subTest(name):
                d, _b = decide(TD.data_pr, review)
                self.assertEqual((d["action"], d["skipped"][0]), ("NOOP", "7:C2:risk:HIGH"))
                d, _b = decide(TD.data_pr, words, review)                              # and the data's words are a gate again off route (c)
                self.assertTrue(any(s.startswith("7:C2:") for s in d["skipped"]), d["skipped"])
        d, _b = decide(TD.data_pr, words, TD.codex_limit)
        self.assertEqual((d["merge"]["review"], d["merge"]["risk"], d["merge"]["data"]), ("FALLBACK(UNAVAILABLE)", "HIGH", True))
        # a decision block that claims data on a reviewed route is no decision
        self.assertFalse(D.decision_schema_ok(dict(d, merge=dict(d["merge"], review="CODEX"))))
        self.assertFalse(D.decision_schema_ok(dict(d, merge=dict(d["merge"], review="CLAUDE"))))
        self.assertTrue(D.decision_schema_ok(d))

    def test_data_fallback_needs_both_the_route_and_the_data(self):
        e = {"thin": {"data_route": True, "risk": "HIGH"}, "lane": {"risk_floor": "LOW"}, "item": {}}
        self.assertTrue(D.data_fallback(e, "FALLBACK(LIMIT)"))
        for route in ("CODEX", "CLAUDE", "NONE(policy=NATIVE_GATES)", None, "FALLBACK"):
            self.assertFalse(D.data_fallback(e, route), route)
        self.assertFalse(D.data_fallback(dict(e, item={"risk": "HIGH_IMPACT"}), "FALLBACK(LIMIT)"))


class FixRound5ChangedLines(unittest.TestCase):
    """#173/7188234670 P1-04: removed lines are read, and an omitted patch is unread, never an empty diff."""

    def test_a_removed_guard_and_an_unread_patch(self):
        guard = code_file("scripts/zz/runner.py", "@@\n-    if not live_trading_allowed:\n-        raise SystemExit('no')\n+    pass\n")
        d, _b = decide(guard, TD.no_codex, TD.claude_receipt())
        self.assertEqual(d["action"], "NOOP")
        self.assertIn("7:C2:judgment:diff:x5", d["skipped"])
        unread = lambda w: TD.set_files(w, [dict(TD.file_("scripts/zz/runner.py", "modified", 400, 10), patch=None)])
        d, brief = decide(unread, TD.no_codex, TD.claude_receipt())
        self.assertEqual(TB.entry(brief)["thin"]["diff_x"], ["patch_unread"])           # (exclusion 11 also makes it owner-gated)
        self.assertEqual(d["action"], "NOOP")
        self.assertTrue(D.unverified_gate("7:C2:judgment:diff:patch_unread"))
        facts = D.entry_facts({"title": "x"}, [{"filename": "a.png", "status": "added", "additions": 0, "deletions": 0},
                                               {"filename": "b.py", "status": "renamed", "previous_filename": "a.py", "additions": 0, "deletions": 0}], True, [])
        self.assertEqual(facts["diff_x"], [])                                          # a binary or a pure rename has no patch to read


class FixRound5Health(unittest.TestCase):
    """#173/7188234670 P1-08: an unread or unproven input is UNVERIFIED, never OK; a verified block is OK."""

    def test_each_unread_input_is_unverified_and_each_verified_block_is_ok(self):
        unread = {
            "reviews unreadable": lambda w, gh, n: w["pr"][7].update(review_reads_complete=False),
            "threads unreadable": lambda w, gh, n: w["pr"][7].update(threads=None),
            "file list incomplete": lambda w, gh, n: w["pr"][7].update(files_complete=False),
            "the CI run list unreadable": lambda w, gh, n: w["pr"][7].update(runs_complete=False),
            "a thread longer than GitHub returned": lambda w, gh, n: w["pr"][7].update(threads=[{"resolved": False, "first_body": "x", "bodies": ["x"] * 101}]),
        }
        for name, live in unread.items():
            with self.subTest(name):
                out, gh, _n, _d = TE.execute(mode="SHADOW", mutate=TE.BEAT, live=live)
                self.assertEqual((out["health"], gh.writes), ("UNVERIFIED", []), out["result"])
        # liveness round: SHADOW never reads the hold live (the job token gets 403 there); its unread hold input is the
        # job-start env value, and LIVE's live read answering 403 is unverified too
        with self.subTest("the hold unreadable"):
            out, gh, _n, _d = TE.execute(mode="SHADOW", mutate=TE.BEAT, env={"S1_EXECUTOR_HOLD": None})
            self.assertEqual((out["health"], gh.writes), ("UNVERIFIED", []), out["result"])
            out, gh, _n, _d = TE.execute(mode="LIVE", mutate=TE.BEAT, env={"S1_EXECUTOR_HOLD": None})   # LIVE v1: the env value too
            self.assertEqual((out["health"], gh.writes), ("UNVERIFIED", []), out["result"])
        blocked = {
            "a CHANGES_REQUESTED": lambda w, gh, n: w["pr"][7]["reviews"].append({"id": 9, "state": "CHANGES_REQUESTED", "commit_id": HEAD, "user": {"login": "x"}}),
            "the head moved": lambda w, gh, n: gh.pull["head"].update(sha="c" * 40),
            "an unresolved P1 thread": lambda w, gh, n: w["pr"][7].update(threads=[{"resolved": False, "first_body": "P1: no"}]),
        }
        for name, live in blocked.items():
            with self.subTest(name):
                out, gh, _n, _d = TE.execute(mode="SHADOW", mutate=TE.BEAT, live=live)
                self.assertEqual((out["health"], gh.writes), ("OK", []), out["result"])
        out, _gh, _n, _d = TE.execute(mode="SHADOW", mutate=TE.BEAT, minutes=30)      # a decision too old to act on
        self.assertEqual((out["result"][:11], out["health"]), ("BRIEF_STALE", "UNVERIFIED"))

    def test_a_noop_decision_that_rests_on_unread_facts_is_unverified(self):
        d, _b = decide(lambda w: w["pr"][7].update(threads=None))
        self.assertEqual((d["action"], d["unverified"]), ("NOOP", ["7:C6:threads_unreadable"]))
        out, gh, _n, _d = TE.execute(mode="SHADOW", mutate=lambda w: (TE.BEAT(w), w["pr"][7].update(threads=None)))
        self.assertEqual((out["result"], out["health"]), ("NOTHING_ACTIONABLE(skipped=7:C6:threads_unreadable)", "UNVERIFIED"))
        d, _b = decide(TD.ci_fail)                                                     # a verified red CI: nothing unread
        self.assertEqual((d["action"], d["unverified"]), ("NOOP", []))
        for gate, want in (("lane:C1b:history_gap", True), ("7:C5:review_unreadable", True), ("7:NOT_READ:depth_cap", False), ("7:NOT_READ:HTTPError", True),
                           ("7:C3:privacy_line:log_unreadable", True), ("7:C3:privacy_line:RESTRICTED_CONTENT", False), ("7:C2:risk:HIGH", False),
                           ("lane:C7:ledger_unreadable", True), ("7:C4:ci_fail", False)):
            self.assertEqual(D.unverified_gate(gate), want, gate)

    def test_reconcile_uncertainty_is_unverified(self):
        rc = TE.Reconcile()
        out, gh, _n, _d = TE.execute(mode="SHADOW", mutate=lambda w: (TE.BEAT(w), rc.intent(w, paths=["x/other.py"])), live=rc.merged())
        self.assertIn("UNREADABLE", " ".join(out["lines"]))
        self.assertEqual(out["health"], "UNVERIFIED")


class FixRound5BoundaryReads(unittest.TestCase):
    """P1-06, P1-09, P1-10, D02: what the last reads before the merge call re-check."""

    def run_live(self, mutate=None):
        run, gh, native, body, d = TE.setup(mutate=mutate)
        run.brief, run.decision, run.body, run.mode = B.parse_body(body), B.decision_of(body), body, "LIVE"
        return run, gh, native

    def test_live_stop_sees_code_drift_protection_and_pins_until_the_merge_call(self):
        for name, change, reason in (("main moved by code", lambda gh, n: (setattr(gh, "main", TE.MAIN2), setattr(n, "drift_paths", ["scripts/x.py"])), "BRIEF_STALE(source_changed)"),
                                     ("main protected", lambda gh, n: gh.w.update(main_protected=True), "lane:C8:main_protected:put"),
                                     ("a pin changed", lambda gh, n: gh.w["pins_actual"].update({"AGENTS.md": "0" * 40}), "lane:C7:pins:AGENTS.md:put")):
            with self.subTest(name):
                run, gh, native = self.run_live()
                change(gh, native)
                with self.assertRaises(TE.E.Stop) as ctx:
                    run.live_stop("put")
                self.assertEqual(ctx.exception.reason, reason)
                run.writes.append(("merge", 7, HEAD))                                  # after this run's merge call: outcome posts only need hold, switch, contract
                if name != "main protected":
                    run.live_stop("write:comment")

    def test_the_publication_and_the_first_candidate_are_read_again_after_the_intent(self):
        out, gh, _n, _d = TE.execute(mutate=TE.BEAT, live=lambda w, gh, n: setattr(gh, "after_intent", lambda g: setattr(g, "issue_body", g.issue_body.replace('"heartbeat_due"', '"heartbeat_due" '))))
        self.assertEqual(TE.tokens(gh), ["S1_LANE_MERGE_INTENT_v1"])
        self.assertIn("publication_after_intent", out["result"])
        # route (c): the first run's candidate is edited, or deleted, after the second run's intent
        for name, change in (("edited", lambda g, cid: g.comment_override.update({cid: dict(next(c for c in g.w["issue_comments"] if c["id"] == cid), body="S1_FALLBACK_CANDIDATE_v1\nx", updated_at=TB.ts(0))})),
                             ("deleted", lambda g, cid: g.comment_override.update({cid: {}}))):
            with self.subTest(name):
                w = TE.offline_world()
                TE.hourly_run(w, 555, 0)
                cid = B.fallback_candidates(w["issue_comments"])[(7, HEAD)][0]["id"]
                out, gh, d = TE.hourly_run(w, 557, 60, runs=TE.RUN_555, live=lambda w2, g, n: setattr(g, "after_intent", lambda g2: change(g2, cid)))
                self.assertEqual(TE.tokens(gh), ["S1_LANE_MERGE_INTENT_v1"], out["result"])
                self.assertIn("MERGE_ABORTED_AFTER_INTENT(", out["result"])

    def test_a_replaced_claude_receipt_is_noticed(self):
        replaced = lambda w, gh, n: setattr(gh, "after_intent", lambda g: (w["pr"][7]["comments"].__setitem__(
            next(i for i, c in enumerate(w["pr"][7]["comments"]) if c.get("id") == 20), TB.comment(21, TD.CLAUDE_OK, TB.OWNER, 0))))
        out, gh, _n, _d = TE.execute(mutate=TD._chain(TE.BEAT, TD.no_codex, TD.claude_receipt()), policy=RECALL, live=replaced)
        self.assertEqual(TE.tokens(gh), ["S1_LANE_MERGE_INTENT_v1"], out["result"])
        self.assertIn("claude_changed_after_intent", out["result"])


class FixRound5Bounded(unittest.TestCase):
    """D04: the merge's calls and writes are reserved before its intent; recovery writes end the run."""

    def test_no_intent_without_the_reserve(self):
        out, gh, _n, _d = TE.execute(mutate=TE.BEAT, live=lambda w, gh, n: setattr(gh, "budget_left", 60))
        self.assertEqual(gh.writes, [])
        self.assertIn("budget:merge_reserve", out["result"])
        self.assertEqual(out["health"], "UNVERIFIED")
        out, gh, _n, _d = TE.execute(mutate=TE.BEAT, live=lambda w, gh, n: setattr(gh, "budget_left", 200))
        self.assertTrue(out["result"].startswith("MERGED("), out["result"])


class FixRound5Readback(unittest.TestCase):
    """N05 and D06: the squash changed EXACTLY the intent's paths, and an unread proof is never a mismatch."""

    def test_the_whole_delta_and_tri_state_ancestry(self):
        out, gh, native, _d = TE.execute(mutate=TE.BEAT, live=lambda w, gh, n: setattr(n, "delta", ["docs/notes/a.md", "scripts/governance/x.py", "tests/test_a.py"]))
        self.assertEqual(TE.tokens(gh)[-1], "S1_LANE_HALTED", out["result"])
        self.assertIn("delta:", out["result"])
        out, gh, native, _d = TE.execute(mutate=TE.BEAT, live=lambda w, gh, n: setattr(n, "ancestor", None))
        self.assertEqual(TE.tokens(gh), ["S1_LANE_MERGE_INTENT_v1", "MERGE"], out["result"])  # unknown ancestry: no receipt, no halt
        self.assertIn("ancestry_unknown", out["result"])
        self.assertEqual(out["health"], "AMBIGUOUS")
        import subprocess, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            git = lambda *a: subprocess.run(["git", "-C", tmp, *a], capture_output=True, text=True, check=True).stdout.strip()
            git("init", "-q")
            for k in (1, 2):
                git("-c", "user.name=t", "-c", "user.email=t@invalid", "commit", "-q", "--allow-empty", "-m", str(k))
            first, second = git("rev-parse", "HEAD~1"), git("rev-parse", "HEAD")
            self.assertIs(B.ancestry(Path(tmp), first, second), True)
            self.assertIs(B.ancestry(Path(tmp), second, first), False)
            self.assertIsNone(B.ancestry(Path(tmp), "f" * 40, second))


class FixRound5Threads(unittest.TestCase):
    """D01: every reply of a review thread is read; a thread GitHub did not return in full is unread."""

    def answer(self, nodes):
        class G:
            repo = B.REPO

            def graphql(self, q, v):
                return {"repository": {"pullRequest": {"reviewThreads": {"pageInfo": {"hasNextPage": False, "endCursor": None}, "nodes": nodes}}}}
        return B.read_threads(G(), 7)

    def test_thirty_one_replies_and_malformed_nodes(self):
        replies = [{"body": "fine"}] * 30 + [{"body": "P1: this breaks"}]
        got = self.answer([{"isResolved": False, "comments": {"totalCount": 31, "nodes": replies}}])
        self.assertEqual(len(got), 1)
        self.assertRegex(got[0]["first_body"], r"\bP1\b")                              # the 31st reply is read
        for name, node in (("more replies than returned", {"isResolved": False, "comments": {"totalCount": 31, "nodes": replies[:30]}}),
                           ("isResolved missing", {"comments": {"totalCount": 1, "nodes": [{"body": "x"}]}}),
                           ("isResolved not a boolean", {"isResolved": "false", "comments": {"totalCount": 1, "nodes": [{"body": "x"}]}}),
                           ("no totalCount", {"isResolved": False, "comments": {"nodes": [{"body": "x"}]}}),
                           ("a null node", None), ("more than one page of replies", {"isResolved": False, "comments": {"totalCount": 101, "nodes": [{"body": "x"}] * 101}})):
            with self.subTest(name):
                self.assertIsNone(self.answer([node]), name)


class FixRound5Signals(unittest.TestCase):
    """P1-11 (the parts that are code): an old usage-limit answer is no UNAVAILABLE signal; an inline P0/P1 parks route (c)."""

    def test_unavailable_needs_a_fresh_limit_answer_and_inline_p01_parks(self):
        cx = {"status": "UNAVAILABLE", "offline": {"signal": "UNAVAILABLE", "at": TB.ts(60 * 30)}}
        for hours, want in ((23, "UNAVAILABLE"), (25, None)):
            act = {"complete": True, "since": TB.ts(60 * 72), "items": [{"limit": True, "at": TB.NOW - timedelta(hours=hours)}]}
            self.assertEqual(B.offline_signal(cx, act, TB.NOW), want, hours)
        self.assertIs(B.p01_named([], [], [{"body": "P0: unsafe"}]), True)
        self.assertIsNone(B.p01_named([], [], None))
        d, _b = decide(TD.data_pr, TD.codex_limit, lambda w: w["pr"][7].update(inline=[{"id": 1, "body": "P1 here", "user": {"login": "x"}}]))
        self.assertEqual(d["skipped"][0], "7:C5:fallback_parked:p0p1_comment")


class FixRound5Totality(unittest.TestCase):
    """N07: decide() is total over malformed nested shapes: never an exception, never an action from a bad shape."""

    def test_fuzzed_briefs_never_raise_and_never_act_on_a_bad_shape(self):
        import random
        _d, brief = decide()
        rng, bad = random.Random(5), (None, "x", 1, [], {}, True, [None], {"x": None}, -1)
        paths = []

        def walk(node, path):
            if isinstance(node, dict):
                for k, v in node.items():
                    paths.append(path + (k,))
                    walk(v, path + (k,))
            elif isinstance(node, list):
                for i, v in enumerate(node[:3]):
                    paths.append(path + (i,))
                    walk(v, path + (i,))
        walk(brief, ())
        merges = 0
        for _ in range(400):
            b = copy.deepcopy(brief)
            target = rng.choice(paths)
            node = b
            for key in target[:-1]:
                node = node[key]
            node[target[-1]] = rng.choice(bad)
            d = D.decide(b)
            self.assertTrue(D.decision_schema_ok(d), target)
            merges += d["action"] == "MERGE"
        d = D.decide({"prs": "not a list", "thin": [], "pins": {"ok": True}, "run_id": 1, "main": "a" * 40, "generated_at": TB.ts(1), "complete": True})
        self.assertEqual(d["action"], "NOOP")
        with unittest.mock.patch.object(D, "_decide", side_effect=[TypeError("boom"), D._decide(None)]):
            d = D.decide(brief)
        self.assertEqual((d["action"], d["result"]), ("NOOP", "BRIEF_UNVERIFIED(decide:TypeError)"))
        self.assertTrue(D.decision_schema_ok(d))


class FixRound5ExecutorOwnReads(unittest.TestCase):
    """D05 and P1-09/D08: the executor's own push-filter read, and the live hold read at start, whitespace included."""

    def test_the_executor_recomputes_the_push_trigger_rule_from_mains_workflows(self):
        out, gh, _n, d = TE.execute(mutate=TE.BEAT, live=lambda w, gh, n: None)
        self.assertTrue(out["result"].startswith("MERGED("))
        def files_say_push(w, gh, n):
            gh.files_push = True
        run, gh, native, body, d = TE.setup(mutate=TE.BEAT)
        run.files["push_filters"] = [{"workflow": "x.yml", "paths": ["**"], "paths_ignore": None}]   # main's filters, read by the executor itself
        out = run.execute(body)
        self.assertEqual((d["action"], gh.writes), ("MERGE", []))                    # the brief said no push trigger; the executor's own read says one
        self.assertIn("7:C2:push_trigger:x.yml", out["result"])
        run, gh, native, body, d = TE.setup(mutate=TE.BEAT)
        run.files["push_filters"] = None                                               # unreadable: every PR matches, UNVERIFIED
        out = run.execute(body)
        self.assertEqual((gh.writes, out["health"]), ([], "UNVERIFIED"), out["result"])

    def test_a_whitespace_hold_read_live_holds(self):
        # LIVE v1 (gate 2 (i)): the job-start env value; whitespace and "0" still hold
        for value in (" ", "\n", "0"):
            out, gh, _n, _d = TE.execute(mutate=TE.BEAT, env={"S1_EXECUTOR_HOLD": value})
            self.assertEqual((gh.writes, out["result"], out["health"]), ([], "EXECUTOR_OFF(hold:start)", "HELD"), repr(value))


if __name__ == "__main__":
    unittest.main()


class SurvivorKillers(unittest.TestCase):
    """Mutants that survived the first fix-round-4 run (N03, N09, N13, N25, N28): each gets a direct test."""

    def test_n03_an_unknown_independence_is_no_route_b_receipt(self):
        d, b = decide(TD.no_codex, TD.claude_receipt(TD.CLAUDE_OK.replace("INDEPENDENT_DETACHED", "TRUST_ME")))
        self.assertNotEqual(d["action"], "MERGE")
        self.assertIsNone(B.claude_receipt_fields(HEAD, [TB.comment(7165386485, TD.CLAUDE_REQUEST, TB.OWNER, 200),
                                                          TB.comment(20, TD.CLAUDE_OK.replace("INDEPENDENT_DETACHED", "TRUST_ME"), TB.OWNER, 100)]))

    def test_n09_high_data_needs_a_low_or_medium_lane_floor(self):
        e = {"thin": {"data_route": True, "risk": "HIGH"}, "lane": {"risk_floor": "LOW"}, "item": None}
        self.assertIs(D.data_admitted(e), True)
        for floor in ("HIGH", "OWNER_GATED", "UNCLEAR", None):
            self.assertIs(D.data_admitted(dict(e, lane={"risk_floor": floor})), False, floor)
        self.assertIs(D.data_admitted(dict(e, thin={"data_route": "yes", "risk": "HIGH"})), False)

    def test_n13_evidence_that_changes_after_the_intent_stops_the_call(self):
        """The body is no gate, but it is part of the evidence: a body edited after the intent is not the PR that was verified."""
        body = lambda w, g, n: setattr(g, "after_intent", lambda g2: g2.pull.update(body="one more sentence after the intent"))
        out, gh, _n, _d = TE.execute(mutate=TE.BEAT, live=body)
        self.assertEqual(TE.tokens(gh), ["S1_LANE_MERGE_INTENT_v1"], out["result"])
        self.assertEqual(out["result"], "MERGE_ABORTED_AFTER_INTENT(7:C8:evidence_changed_after_intent)")

    def test_n25_a_label_is_repaired_only_for_a_natively_merged_head(self):
        pending = TB.comment(700, f"S1_CODEX_RECALL_PENDING_v1\npr: 7\nhead: {HEAD}\nmerge: {'9' * 40}", TB.BOT, 500)
        run, gh, _n, body, d = TE.setup(mutate=lambda w: w["issue_comments"].append(pending), policy=RECALL)
        run.brief, run.decision, run.mode = dict(B.parse_body(body), recall={"pending": 1, "items": [{"pr": 7, "head": HEAD, "codex": "NONE"}]}), d, "LIVE"
        gh.labels[7] = []
        self.assertIsNone(run.recall(gh.w["issue_comments"]))                     # PR 7 is open in this world: no repair
        self.assertEqual(gh.writes, [])

    def test_n28_the_executor_reads_the_hard_lines_in_the_live_diff(self):
        live = lambda w, g, n: next(f for f in w["pr"][7]["files"] if not f["filename"].endswith(".md")).update(patch="@@\n+client.send_transaction(signed)\n")
        out, gh, _n, d = TE.execute(mutate=TE.BEAT, live=live)
        self.assertEqual(d["action"], "MERGE")
        self.assertEqual(gh.writes, [])
        self.assertIn("7:C2:judgment:diff", out["result"])
