"""Independent regression candidates for Archive #2337 (base 271d17c7).

Copy to Archive tests/governance/test_s1_fix6_adversarial.py, run:
    python -m pytest -q tests/governance/test_s1_fix6_adversarial.py
No real GitHub writes, no network, no new dependency. Uses existing fixtures.
These are proposed tests, not a claimed successful exact-head replay.
"""
import copy
import json
import unittest

import test_s1_brief_c1b_v1 as TC
import test_s1_tick_brief_v1 as TB
import test_s1_decision_v1 as TD
import test_s1_executor_v1 as TE

B, D, E = TE.B, TE.D, TE.E
NOW = TB.NOW


def history_gaps(doc):
    """Extract individual unresolved anchors, supporting old singular and proposed plural forms.
    If a conservative union is chosen, adapt this adapter to prove both original
    anchors remain covered; do not weaken the assertions to mere gap presence.
    """
    c = doc.get("c1b", doc)
    raw = c.get("gaps", [])
    if isinstance(raw, dict):
        raw = list(raw.values())
    raw = list(raw) if isinstance(raw, list) else []
    if isinstance(c.get("gap"), dict):
        raw.append(c["gap"])
    return {g.get("to") for g in raw if isinstance(g, dict)
            and g.get("from_unknown") is True
            and not str(g.get("reason", "")).startswith("C1b:capped_equal_ends")}


def snapshot(main, record, run_id=555, age=0):
    w = TD.thin_world("SHADOW")
    w.update(main_sha=main, c1b=record,
             run={"id": run_id, "attempt": 1, "event": "schedule"})
    w["codex_feed"] = TD.codex_feed_of(w)
    brief = B.build_brief(w)
    brief["generated_at"] = TB.ts(age)
    return brief


def previous(main, record, run_id=554):
    brief = snapshot(main, record, run_id, 65)
    body, _ = B.render_issue(brief)
    issue = {"number": 3, "user": dict(TB.BOT), "body": body,
             "updated_at": TB.ts(64)}
    run = {"id": run_id, "path": B.WORKFLOW_PATH,
           "repository": {"full_name": B.REPO},
           "head_repository": {"full_name": B.REPO},
           "head_branch": "main", "head_sha": main, "event": "schedule",
           "run_attempt": 1, "status": "completed", "conclusion": "success",
           "run_started_at": TB.ts(70), "updated_at": TB.ts(60)}
    return issue, run


def gap_record(main, anchor):
    # Claude, fix round 6 (adapter only, documented in the dossier): the record of a brief made 65 minutes ago that holds
    # ONE unaccepted range gap to `anchor`, in the gap ledger's schema (B.c1b_gap; its detection time is that brief's).
    # The kit's singular form ({"gap": {...}}) is still read (c1b_block migrates it), but with no detection time it is
    # dated at the build, and an acceptance from before the build then rightly does not clear it.
    return {"checked_through": main, "from": main, "halt": None,
            "complete": True,
            "gaps": [B.c1b_gap(None, anchor, "C1b:range", B.C1B_WINDOW, TB.ts(65))]}


class PublishStore:
    """Simulated persistent issue: publisher can read it after producer failed.
    Every mutation is local, and recorded. No catch-all network methods.
    """
    def __init__(self, issue, run, ledger=()):
        self.issue, self.run = copy.deepcopy(issue), copy.deepcopy(run)
        self.ledger, self.writes = list(ledger), []

    def get(self, path, params=None):
        if path == "issues":
            return [copy.deepcopy(self.issue)]
        if path == f"issues/{self.issue['number']}":
            return copy.deepcopy(self.issue)
        if path == f"issues/{B.OWNER_ISSUE}/comments":
            return copy.deepcopy(self.ledger)
        if path.startswith("actions/runs/"):
            return copy.deepcopy(self.run)
        raise AssertionError(path)

    def pages(self, path, *args, **kwargs):
        return self.get(path), True

    def url(self, path, params=None):
        return path

    def _request(self, method, path, data=None, **kw):
        assert method == "PATCH" and path == f"issues/{self.issue['number']}", (method, path)
        self.writes.append((method, path, copy.deepcopy(data)))
        self.issue.update(data)
        return json.dumps(self.issue).encode(), {}


class AdversarialGapSequences(unittest.TestCase):
    def test_old_gap_survives_producer_failure_then_successful_publisher_read(self):
        for failure in ("transport", "budget", "budget_before_read", "malformed", "duplicate"):
            with self.subTest(failure=failure):
                h = TC.History()
                main = h.commit("data: first")
                g1 = TC.sha("unaccepted-history-A")
                issue, run = previous(main, gap_record(main, g1))
                h.commit("data: next")
                gh = TC.Gh(h, issue, run)
                kwargs = {}
                if failure == "transport":
                    gh.fail.add("issues")
                elif failure == "budget":
                    gh.stop_on = "issues"
                elif failure == "budget_before_read":
                    kwargs["max_calls"] = 0
                else:
                    normal_get = gh.get
                    def bad_get(path, params=None):
                        if path == "issues":
                            gh.calls += 1
                            if failure == "malformed":
                                return {"message": "unreadable"}
                            return [copy.deepcopy(issue), dict(issue, number=4)]
                        return normal_get(path, params)
                    gh.get = bad_get
                record = B.read_c1b(gh, h.main, [], NOW, **kwargs)
                body, decision = B.render_issue(snapshot(h.main, record))
                store = PublishStore(issue, run)
                try:
                    B.publish(store, body, now=NOW)
                except SystemExit:
                    pass  # explicit refusal is safe only if prior evidence survives
                persisted = B.parse_body(store.issue["body"])
                self.assertIsNotNone(persisted)
                self.assertIn(g1, history_gaps(persisted), failure)
                self.assertNotEqual(decision["action"], "MERGE")

    def test_second_disjoint_range_cannot_disappear_behind_first(self):
        h = TC.History()
        anchor = h.commit("data: old anchor")
        g1 = TC.sha("unaccepted-history-A")
        issue, run = previous(anchor, gap_record(anchor, g1))
        # Squash-shaped data commits isolate range loss from equal-end scan caps.
        # Claude, fix round 6 (setup only, documented in the dossier): a known anchor is followed back over up to
        # B.C1B_PAGES commit pages, so the range the walk cannot reach starts C1B_PAGES * C1B_WINDOW commits back.
        for i in range(B.C1B_WINDOW * B.C1B_PAGES + 5):
            h.commit(f"data snapshot (#{1000+i})")
        _, g2, reached = B.c1b_walk(h.main, h.page(), [anchor], B.C1B_WINDOW * B.C1B_PAGES)
        self.assertFalse(reached)
        self.assertNotEqual(g1, g2)
        record = B.read_c1b(TC.Gh(h, issue, run), h.main, [], NOW)
        self.assertTrue({g1, g2}.issubset(history_gaps(record)), record)
        # Simulate the actual serialization boundary and next successful tick.
        issue2, run2 = previous(h.main, record)
        h.commit("data: current")
        accept1 = TC.accept_comment(90, next(g for g in record["gaps"] if g["to"] == g1))   # fix round 7: exact detection
        record2 = B.read_c1b(TC.Gh(h, issue2, run2), h.main, [accept1], NOW)
        self.assertIn(g2, history_gaps(record2), record2)
        self.assertNotIn(g1, history_gaps(record2), record2)
        self.assertNotEqual(D.decide(snapshot(h.main, record2))["action"], "MERGE")

    def test_owner_acceptance_is_exact_immutable_and_role_bound(self):
        h = TC.History()
        main = h.commit("data: base")
        g1 = TC.sha("unaccepted-history-A")
        issue, run = previous(main, gap_record(main, g1))
        h.commit("data: current")
        gap = next(g for g in B.read_c1b(TC.Gh(h, issue, run), h.main, [], NOW)["gaps"] if g["to"] == g1)
        accept = TC.accept_comment(90, gap)                          # fix round 7: exact detection, natively unedited
        for ledger in (None, [], [dict(accept, user=TB.BOT)],
                       [dict(accept, updated_at=TB.ts(1))],
                       [TC.accept_comment(91, dict(gap, to="1" * 40, id="-.." + "1" * 40))]):
            self.assertIn(g1, history_gaps(B.read_c1b(TC.Gh(h, issue, run), h.main, ledger, NOW)))
        self.assertNotIn(g1, history_gaps(B.read_c1b(TC.Gh(h, issue, run), h.main, [accept], NOW)))


class AdversarialHealth(unittest.TestCase):
    def assert_unknown(self, out, gh):
        self.assertEqual(gh.writes, [])
        self.assertEqual(out["action"], "NOOP")
        self.assertIn(out["health"], ("UNVERIFIED", "DEGRADED"), out["result"])

    def test_producer_main_health_unread_is_not_ok(self):
        out, gh, _, d = TE.execute(mode="SHADOW",
            mutate=lambda w: (TE.BEAT(w), w.update(health_runs=[], health_runs_complete=False)))
        self.assertNotEqual(d["action"], "MERGE")
        self.assert_unknown(out, gh)

    def test_producer_protection_unknown_is_not_ok(self):
        for value in (None, "false", 0):
            with self.subTest(value=value):
                out, gh, _, d = TE.execute(mode="SHADOW",
                    mutate=lambda w: (TE.BEAT(w), w.update(main_protected=value)))
                self.assertNotEqual(d["action"], "MERGE")
                self.assert_unknown(out, gh)

    def test_native_protection_unknown_is_not_ok(self):
        for value in (None, "false", 0):
            with self.subTest(value=value):
                out, gh, _, d = TE.execute(mode="SHADOW", mutate=TE.BEAT,
                    live=lambda w, g, n: w.update(main_protected=value))
                self.assertEqual(d["action"], "MERGE")
                self.assert_unknown(out, gh)

    def test_known_protection_is_a_proven_block_not_a_merge(self):
        out, gh, _, _ = TE.execute(mode="SHADOW", mutate=TE.BEAT,
            live=lambda w, g, n: w.update(main_protected=True))
        self.assertEqual((out["action"], gh.writes), ("NOOP", []))

    def test_env_hold_does_not_substitute_for_native_hold_evidence(self):
        out, gh, _, _ = TE.execute(mode="SHADOW", mutate=TE.BEAT,
            env={"S1_EXECUTOR_HOLD": " "},
            live=lambda w, g, n: setattr(g, "hold", " "))
        self.assertEqual(gh.writes, [])
        self.assertGreaterEqual(gh.hold_reads, 1)
        self.assertIn("hold:start", out["result"])
        self.assertEqual(out["health"], "HELD")


if __name__ == "__main__":
    unittest.main()
