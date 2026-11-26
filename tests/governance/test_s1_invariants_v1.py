"""S1 executor safety invariants (fix round 4, ChatGPT #173/7186140947): one class per invariant, each with its own
adversarial cases, kept in the regression suite. The larger suites (test_s1_decision_v1.py, test_s1_executor_v1.py)
hold the full matrices; this module states each invariant once and attacks it directly.

Fixtures only, no network. A green finite suite is not a proof of a universal property: each class names what it
attacks and nothing more.
"""
import copy
import sys
import unittest
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
                             ("hold", lambda w, g: setattr(g, "hold", "x")),
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
        d, _b = decide(lambda w: w["c1b"].update(gap={"from_unknown": True, "window": 4, "reason": "C1b:capped_equal_ends"}))
        self.assertEqual(d["action"], "NOOP")
        self.assertIn("lane:C1b:history_gap", d["skipped"])
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
        for result in ("SOURCE_UNVERIFIED(3)", "BRIEF_UNVERIFIED(publication:decision_differs)", "NOTHING_ACTIONABLE(skipped=hold_unreadable:intent(404x))"):
            self.assertEqual(TE.E.health_state(result, [], None), "DEGRADED", result)

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
