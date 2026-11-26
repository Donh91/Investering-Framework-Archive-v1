"""S1 executor (AGENTS.md section 0.2i): the `execute` job re-verifies natively and performs the ONE decided action.

Fixtures only, no network: a fake GitHub that serves the same world the brief was built from, and a fake of the git
reads. Every negative case changes ONE live fact AFTER the brief was built (so the decision still says MERGE) and
asserts that the executor writes nothing. The call counter of the fake is the dry-run harness that measures reads and
writes per run type.
"""
import copy
import json
import os
import re
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "governance"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import s1_decision_v1 as D  # noqa: E402
import s1_executor_v1 as E  # noqa: E402
import s1_tick_brief_v1 as B  # noqa: E402
import test_s1_decision_v1 as TD  # noqa: E402
import test_s1_tick_brief_v1 as TB  # noqa: E402
import yaml  # noqa: E402

NOW, MAIN, HEAD = TB.NOW, TB.MAIN, TB.HEAD
MERGE_SHA = "9" * 40
MAIN2 = "e" * 40
SOURCE = (ROOT / "scripts" / "governance" / "s1_executor_v1.py").read_text(encoding="utf-8")
WORKFLOW = yaml.safe_load((ROOT / B.WORKFLOW_PATH).read_text(encoding="utf-8"))
SWITCH = json.loads((ROOT / B.SWITCH).read_text(encoding="utf-8"))
ENV = {"GITHUB_REPOSITORY": B.REPO, "GITHUB_REF": "refs/heads/main", "GITHUB_EVENT_NAME": "schedule", "GITHUB_RUN_ID": "555",
       "GITHUB_RUN_ATTEMPT": "1", "GITHUB_SHA": MAIN}


def executor_run(run_id, created, updated=None, status="completed", **kw):
    """GET actions/runs/<id> of a run of the brief workflow on main (what proves an executor post)."""
    return dict({"id": run_id, "path": B.WORKFLOW_PATH, "head_branch": "main", "event": "schedule", "status": status,
                 "conclusion": "success" if status == "completed" else None, "created_at": B.iso(created), "run_started_at": B.iso(created),
                 "updated_at": B.iso(updated or created + timedelta(minutes=4)), "repository": {"full_name": B.REPO},
                 "head_repository": {"full_name": B.REPO}}, **kw)


class FakeGitHub:
    """GitHub as the executor reads it, built from the snapshot `w` the brief was built from. Every call is recorded."""

    repo = B.REPO

    def __init__(self, w, now):
        self.w, self.now, self.calls, self.writes, self.next_id = w, now, [], [], 7000
        self.main = w["main_sha"]
        self.fail_merge = None
        pr = w["pr"].get(7, {})
        pull = w["pulls"][0] if w["pulls"] else {}
        self.pull = dict(copy.deepcopy(pr.get("detail") or {}), title=pull.get("title"), labels=copy.deepcopy(pull.get("labels") or []),
                         user=copy.deepcopy(pull.get("user")), body=pull.get("body"), merged=False,
                         head=copy.deepcopy(pull.get("head")), base=copy.deepcopy(pull.get("base")))
        self.late = []                                             # comments that reach #1156 after the ledger read
        # this run, as GET actions/runs/555 shows it while the execute job is running (section 0.2i: the proof that a
        # ledger post of the Actions bot is the executor's own)
        self.runs = {555: executor_run(555, created=now - timedelta(minutes=3), status="in_progress", updated=now)}
        self.pull_reads, self.head_from_read = 0, None             # (k, sha): from the k-th read of the PR on, it shows that head
        self.fail_label = None                                      # an exception the label write raises

    def run_of(self, run_id):
        return copy.deepcopy(self.runs.get(int(run_id)))

    def url(self, path, params=None):
        return path

    def _record(self, kind, path):
        self.calls.append((kind, path))

    def get(self, path, params=None):
        self._record("GET", path)
        w = self.w
        if path == "":
            return dict(w["repo"])
        if path == "branches/main":
            return {"commit": {"sha": self.main}, "protected": w.get("main_protected")}
        if path == "pulls/7":
            self.pull_reads += 1
            doc = copy.deepcopy(self.pull)
            if self.head_from_read and self.pull_reads >= self.head_from_read[0]:
                doc["head"]["sha"] = self.head_from_read[1]
            return doc
        if path == f"issues/{B.OWNER_ISSUE}/comments":
            return list(self.late)
        if path.startswith("commits/"):
            return copy.deepcopy(w.get("commit_objects", {}).get(path.split("/", 1)[1]) or {})
        if path.startswith("git/trees/"):
            return copy.deepcopy(w.get("tree_objects", {}).get(path.split("/", 2)[2]) or {})
        if path.startswith("actions/runs/"):
            rid = int(path.rsplit("/", 1)[1])
            if rid in self.runs:
                return copy.deepcopy(self.runs[rid])
            run = copy.deepcopy(next((r for r in w["health_runs"] if r["id"] == rid), {}))
            return dict({"repository": {"full_name": B.REPO}}, **run) if run else run   # a real run object names both repositories
        if path == "actions/workflows/s1-tick-brief.yml/runs":
            return {"workflow_runs": [{"event": "workflow_dispatch", "created_at": B.iso(self.now - timedelta(hours=h))} for h in range(30)]}
        raise AssertionError(f"unexpected GET {path}")

    def pages(self, path, params=None, key=None, max_pages=30):
        self._record("PAGES", path)
        w, d = self.w, self.w["pr"].get(7, {})
        table = {
            f"issues/{B.OWNER_ISSUE}/comments": (w["issue_comments"], w.get("issue_comments_complete", True)),
            "pulls/7/files": (d.get("files"), d.get("files_complete")),
            "pulls/7/commits": (d.get("commits"), d.get("commits_complete")),
            "issues/7/comments": (d.get("comments"), d.get("review_reads_complete")),
            "pulls/7/reviews": (d.get("reviews"), d.get("review_reads_complete")),
            "pulls/7/comments": (d.get("inline"), d.get("review_reads_complete")),
            "actions/runs": (d.get("runs"), d.get("runs_complete")),
            f"commits/{HEAD}/check-runs": (d.get("check_runs"), d.get("checks_complete")),
            f"commits/{HEAD}/statuses": (d.get("statuses"), d.get("checks_complete")),
            "actions/workflows/automation-production-health.yml/runs": (w["health_runs"], True),
            "rulesets": (w["rulesets_1"], w.get("rulesets_complete", True)),
        }
        if path in table:
            rows, complete = table[path]
            return copy.deepcopy(rows or []), bool(complete)
        m = re.fullmatch(r"actions/runs/(\d+)/jobs", path)
        if m:
            return copy.deepcopy(d["jobs"].get(int(m.group(1))) or []), True
        if path in ("issues/comments", "pulls/comments"):              # Codex's activity in the whole repository (B.read_codex_feed)
            feed = TD.codex_feed_of(w)
            return feed["comments" if path == "issues/comments" else "inline"], bool(feed["complete"])
        m = re.fullmatch(r"(?:issues|pulls)/(\d+)/(comments|reviews|commits)", path)   # a merged PR with a pending Codex recall
        read = (w.get("recall_reads") or {}).get(m.group(1)) if m else None
        if read is not None:
            key = {"issues/comments": "comments", "pulls/reviews": "reviews", "pulls/comments": "inline", "pulls/commits": "commits"}[path.split("/")[0] + "/" + m.group(2)]
            return copy.deepcopy(read[key]), bool(read["commits_complete"] if key == "commits" else read["complete"])
        raise AssertionError(f"unexpected PAGES {path}")

    def text(self, path):
        self._record("TEXT", path)
        return self.w["pr"][7]["privacy_log"]

    def graphql(self, query, variables):
        self._record("GRAPHQL", "threads")
        threads = self.w["pr"][7].get("threads")
        if threads is None:
            raise RuntimeError("GRAPHQL_ERROR")
        return {"repository": {"pullRequest": {"reviewThreads": {"pageInfo": {"hasNextPage": False, "endCursor": None},
                "nodes": [{"isResolved": t["resolved"], "comments": {"nodes": [{"body": t["first_body"]}]}} for t in threads]}}}}

    def _request(self, method, url, data=None, accept=""):
        self._record(method, url)
        self.writes.append((method, url, copy.deepcopy(data)))
        if method == "POST" and url == f"issues/{B.OWNER_ISSUE}/comments":
            self.next_id += 1
            row = {"id": self.next_id, "body": data["body"], "user": dict(B.ACTIONS_BOT), "created_at": B.iso(self.now), "updated_at": B.iso(self.now)}
            self.w["issue_comments"].append(row)
            return json.dumps(row).encode(), {}
        if (method, url) in (("POST", "issues/7/labels"), ("DELETE", f"issues/9/labels/{D.RECALL_LABEL}")):
            if self.fail_label:
                raise self.fail_label
            return b"[]", {}
        if method == "PUT" and url == "pulls/7/merge":
            if self.fail_merge:
                raise self.fail_merge
            self.pull.update(merged=True, state="closed", merged_at=B.iso(self.now), merge_commit_sha=MERGE_SHA, merged_by={"login": B.ACTIONS_BOT["login"]})
            self.w.setdefault("commit_objects", {})[MERGE_SHA] = {"sha": MERGE_SHA, "parents": [{"sha": self.main}], "commit": {"message": "docs: a note (#7)\n\nbody"}}
            self.main = MERGE_SHA
            return json.dumps({"merged": True, "sha": MERGE_SHA}).encode(), {}
        raise AssertionError(f"unexpected write {method} {url}")


class FakeNative:
    def __init__(self, w):
        self.w, self.relation, self.drift_paths, self.ancestor, self.merged_blobs = w, "ahead", ["04_MARKET_LEARNING/x.json"], True, {}
        self.calls = []

    def drift(self, base, head):
        self.calls.append(("drift", base, head))
        return self.relation, self.drift_paths

    def tree_shas(self, commit, paths):
        self.calls.append(("tree_shas", commit))
        if commit == MERGE_SHA:
            return {p: self.merged_blobs.get(p, "blob-" + p) for p in paths}
        if commit == HEAD:
            return {p: "blob-" + p for p in paths}
        return {p: self.w["pins_actual"].get(p) for p in paths}

    def is_ancestor(self, sha, main):
        self.calls.append(("is_ancestor", sha, main))
        return self.ancestor


def setup(mutate=None, mode="LIVE", policy="NATIVE_GATES", live=None, env=None, minutes=2):
    """Build the brief from world `w` (after `mutate`), then apply `live` to the SAME world (a fact that changes after
    the decision), and return the executor run plus its fakes."""
    w = TD.thin_world(mode, policy)
    if mutate:
        mutate(w)
    body, decision = B.render_issue(B.build_brief(dict(copy.deepcopy(w), codex_feed=TD.codex_feed_of(w))))
    now = NOW + timedelta(minutes=minutes)
    gh, native = FakeGitHub(w, now), FakeNative(w)
    if live:
        live(w, gh, native)
    files = {"switch": w["switch"], "contract": w["contract"], "policy": TB.POLICY, "gate_isolation": "LIVE", "bindings": TB.BINDINGS, "budgets": TB.BUDGETS}
    run = E.Run(gh, native, dict(ENV, **(env or {})), files, now_fn=lambda: now, out=lambda line: None)
    return run, gh, native, body, decision


def execute(**kw):
    run, gh, native, body, decision = setup(**kw)
    return run.execute(body), gh, native, decision


def tokens(gh):
    return [("LABEL+" if method == "POST" else "LABEL-") if "/labels" in url else B.first_line_token(data["body"]) if method == "POST" else "MERGE"
            for method, url, data in gh.writes]


class LiveMerge(unittest.TestCase):
    def test_intent_then_exact_head_merge_then_readback_then_receipt(self):
        out, gh, native, d = execute()
        self.assertEqual((out["action"], out["pr"], out["head"]), ("MERGE", 7, HEAD))
        self.assertEqual(out["result"], f"MERGED(n=1,main={MERGE_SHA[:8]})")
        self.assertEqual(tokens(gh), ["S1_HEARTBEAT_v1", "S1_LANE_MERGE_INTENT_v1", "MERGE", "S1_LANE_MERGE_v1"])
        merge = next(w for w in gh.writes if w[0] == "PUT")
        self.assertEqual(merge, ("PUT", "pulls/7/merge", {"merge_method": "squash", "sha": HEAD}))        # the exact head, enforced by GitHub
        intent, receipt = gh.writes[1][2]["body"], gh.writes[3][2]["body"]
        for line in ("pr: 7", f"head: {HEAD}", f"main: {MAIN}", f"repo_id={TB.REPO_ID}", f"loop={'4' * 40}", "brief=555", "decision=555.1",
                     "executor: GITHUB run=555", "risk: LOW", "review: CODEX", "contract=44444444"):
            self.assertIn(line, intent.splitlines())
        for line in ("pr: 7", f"head: {HEAD}", f"merge: {MERGE_SHA}", "review: CODEX", "privacy=NO_RESTRICTED_CONTENT run=101", f"main_before: {MAIN}",
                     f"main_after: {MERGE_SHA}", "blob_match: 2 paths", f"repo_id={TB.REPO_ID}", "intent: 7002", "brief=555",
                     "merge_execution_origin: S1_GITHUB_EXECUTOR run=555", "executor: GITHUB run=555", "contract=44444444"):
            self.assertIn(line, receipt.splitlines())
        self.assertIn("ci=privacy-scan@101.1", receipt)
        self.assertEqual(out["lines"][-1], f"S1_TICK MERGE 7 {HEAD[:8]} MERGED(n=1,main={MERGE_SHA[:8]}) main={MAIN[:8]} contract=44444444")
        # the receipts are ledger posts the next brief counts: the intent is settled and the merge is counted
        comments = gh.w["issue_comments"]
        self.assertEqual(B.open_intents(comments, NOW + timedelta(minutes=5), 0, gh.run_of), [])
        self.assertEqual(len(B.open_intents(comments, NOW + timedelta(minutes=5), 0)), 1)     # ... only because run 555 is proven (P2-4)
        self.assertEqual((out["alarms"], [line for line in out["lines"] if "ALARM" in line]), ([], []))
        self.assertEqual(len(B.lane_merges(comments)), 1)
        self.assertEqual(B.heartbeat_due(comments, NOW + timedelta(minutes=5)), False)

    def test_invariant_exact_head_only_the_decisions_pr_and_sha_can_be_merged(self):
        run, gh, native, body, d = setup()
        run.brief, run.decision, run.mode = B.parse_body(body), d, "LIVE"
        for bad in ({"pr": 8, "sha": HEAD}, {"pr": 7, "sha": "c" * 40}, {"pr": 7, "sha": HEAD[:39]}, {"pr": "7", "sha": HEAD}):
            with self.assertRaises(E.Stop):
                run.write("merge", **bad)
        self.assertEqual(gh.writes, [])
        run.write("merge", pr=7, sha=HEAD)
        with self.assertRaises(E.Stop):                                                # ONE merge per run, whatever the caller asks
            run.write("merge", pr=7, sha=HEAD)
        self.assertEqual(len(gh.writes), 1)

    def test_invariant_one_action_per_run_and_a_write_cap(self):
        out, gh, _n, _d = execute()
        self.assertEqual(sum(1 for w in gh.writes if w[0] == "PUT"), 1)
        self.assertLessEqual(len(gh.writes), E.MAX_WRITES)
        run, gh, _n, body, d = setup()
        run.brief, run.decision, run.mode = B.parse_body(body), d, "LIVE"
        for _ in range(E.MAX_WRITES):
            run.write("comment", body="S1_OP_DONE_v1\nintent: 1")
        with self.assertRaises(E.Stop):
            run.write("comment", body="S1_OP_DONE_v1\nintent: 1")

    def test_invariant_the_executor_writes_only_the_two_allowed_shapes(self):
        run, gh, _n, body, d = setup()
        run.brief, run.decision, run.mode = B.parse_body(body), d, "LIVE"
        for bad in ("hello", "@codex review", "CLAUDE_REVIEW_v1\nverdict: APPROVE", "", "S1_ITEM_v1\nitem: pr:7", "x" * 10, "S1_LANE_HALTED " + "x" * 5000, None):
            with self.assertRaises(E.Stop):
                run.write("comment", body=bad)
        with self.assertRaises((E.Stop, KeyError)):
            run.write("delete", pr=7)
        self.assertEqual(gh.writes, [])
        # the source has exactly four write calls, all inside write(), and no other mutating verb (fix round 2 added
        # the ONE label codex-recall-pending: its name is a constant, never a parameter)
        self.assertEqual(re.findall(r'_request\("(\w+)", self\.gh\.url\(f?"([^"]+)"\)', SOURCE),
                         [("POST", "issues/{B.OWNER_ISSUE}/comments"), ("POST", "issues/{pr}/labels"), ("DELETE", "issues/{pr}/labels/{D.RECALL_LABEL}"),
                          ("PUT", "pulls/{pr}/merge")])
        self.assertEqual(SOURCE.count("_request("), 4)
        body_of_write = SOURCE[SOURCE.index("    def write(self, kind, **kw):"):SOURCE.index("    def say(self, line):")]
        self.assertEqual(body_of_write.count("_request("), 4)
        self.assertIn('{"labels": [D.RECALL_LABEL]}', body_of_write)
        for verb in ('"PATCH"', "update-branch", "/dispatches", "git/refs", "/reviews\", {", "contents/"):
            self.assertNotIn(verb, SOURCE, verb)
        self.assertNotIn("subprocess", SOURCE)                                         # every git read goes through the brief module's helpers

    def test_invariant_write_itself_refuses_unless_the_mode_is_live(self):
        # the second layer: even a caller that forgot its own mode check cannot write in SHADOW or OFF
        for mode in ("SHADOW", "OFF", "banana", None):
            run, gh, _n, body, d = setup()
            run.brief, run.decision, run.mode = B.parse_body(body), d, mode
            for call in (lambda: run.write("comment", body="S1_LANE_HALTED PR=- head=-"), lambda: run.write("merge", pr=7, sha=HEAD)):
                with self.assertRaises(E.Stop) as stop:
                    call()
                self.assertEqual(stop.exception.reason, "executor_not_live")
            self.assertEqual(gh.writes, [])

    def test_every_write_is_preceded_by_the_clock_check(self):
        run, gh, _n, body, d = setup()
        run.brief, run.decision, run.mode = B.parse_body(body), d, "LIVE"
        run.now_fn = lambda: datetime(2026, 11, 23, 9, 0, tzinfo=timezone.utc)         # inside the Monday window
        with self.assertRaises(E.Stop) as stop:
            run.write("comment", body="S1_LANE_HALTED PR=- head=-")
        self.assertEqual(stop.exception.reason, "clock:MONDAY_READ_ONLY")
        run.now_fn = lambda: NOW + timedelta(minutes=D.EXECUTE_MAX_AGE_MINUTES + 1)
        with self.assertRaises(E.Stop):
            run.write("merge", pr=7, sha=HEAD)
        self.assertEqual(gh.writes, [])


class ModesAndBinding(unittest.TestCase):
    def test_shadow_reads_everything_and_writes_nothing(self):
        out, gh, native, d = execute(mode="SHADOW")
        self.assertEqual(gh.writes, [])
        self.assertEqual((out["mode"], out["action"], out["result"]), ("SHADOW", "NOOP", "WOULD_MERGE(pr=7,head=bbbbbbbb,risk=LOW,review=CODEX)"))
        self.assertIn(("TEXT", "actions/jobs/1010/logs"), gh.calls)                    # the privacy line was really re-read
        self.assertIn(("GRAPHQL", "threads"), gh.calls)
        self.assertTrue(out["lines"][-1].startswith("S1_TICK NOOP 7 bbbbbbbb WOULD_MERGE("))   # never a MERGE line without a merge

    def test_off_and_the_owner_hold_do_nothing_at_all(self):
        out, gh, _n, _d = execute(mode="OFF", policy="CODEX_FINAL_REQUIRED")
        self.assertEqual((out["result"], gh.calls), ("EXECUTOR_OFF(switch)", []))
        for hold in ("1", "true", "HOLD", "x", "0", "false", "off", "OFF", "no"):          # ANY non-empty value holds (P2-5)
            out, gh, _n, _d = execute(env={"S1_EXECUTOR_HOLD": hold})
            self.assertEqual((out["result"], gh.calls, gh.writes), ("EXECUTOR_OFF(hold)", [], []), hold)
        for free in ("", " ", "\n"):
            self.assertEqual(D.effective_mode("LIVE", free), "LIVE", free)
            self.assertTrue(execute(env={"S1_EXECUTOR_HOLD": free})[0]["result"].startswith("MERGED("), repr(free))
        self.assertEqual(D.effective_mode("SHADOW", "1"), "OFF")
        self.assertEqual(D.effective_mode("banana", ""), "OFF")
        self.assertEqual(D.effective_mode("OFF", ""), "OFF")                           # the variable can never switch the executor ON

    def test_invariant_a_decision_of_another_run_is_never_executed(self):
        for name, env in {"another run id": {"GITHUB_RUN_ID": "556"}, "a re-run attempt": {"GITHUB_RUN_ATTEMPT": "2"}, "another sha": {"GITHUB_SHA": "c" * 40},
                          "a push event": {"GITHUB_EVENT_NAME": "push"}, "a workflow_run event": {"GITHUB_EVENT_NAME": "workflow_run"},
                          "a pull_request event": {"GITHUB_EVENT_NAME": "pull_request"}, "another branch": {"GITHUB_REF": "refs/heads/x"},
                          "another repository": {"GITHUB_REPOSITORY": "someone/fork"}}.items():
            with self.subTest(name):
                out, gh, _n, _d = execute(env=env)
                self.assertEqual((out["result"], gh.calls, gh.writes), ("BRIEF_UNVERIFIED(run_binding)", [], []))

    def test_invariant_stale_malformed_or_tampered_decisions_are_noops(self):
        run, gh, _n, body, d = setup()
        for name, bad in {"garbage": "garbage", "empty": "", "no decision block": body[body.index(B.SCHEMA + " run_id"):],
                          "tampered block": body.replace('"sha":"' + HEAD, '"sha":"' + "c" * 40, 1),
                          "tampered brief": body.replace('"state":"ON"', '"state":"OFF"'),
                          "duplicate key": body.replace('"action":"MERGE"', '"action":"MERGE","action":"MERGE"', 1)}.items():
            with self.subTest(name):
                run, gh, _n, _b, _d = setup()
                out = run.execute(bad)
                self.assertEqual((out["result"], gh.calls, gh.writes), ("BRIEF_UNVERIFIED(body)", [], []))
        out, gh, _n, _d = execute(minutes=D.EXECUTE_MAX_AGE_MINUTES + 1)               # a re-run of an old run's execute job
        self.assertEqual((out["result"], gh.writes), ("BRIEF_STALE(age_min=21)", []))
        # the switch of the checkout differs from the one the brief was built with
        run, gh, _n, body, _d = setup()
        run.files["switch"] = dict(run.files["switch"], executor="SHADOW")
        self.assertEqual((run.execute(body)["result"], gh.writes), ("BRIEF_UNVERIFIED(switch)", []))
        run, gh, _n, body, _d = setup()
        run.files["switch"] = dict(run.files["switch"], review_policy="CODEX_FINAL_REQUIRED")
        self.assertEqual((run.execute(body)["result"], gh.writes), ("BRIEF_UNVERIFIED(switch)", []))

    def test_invariant_monday_window_no_write_even_for_a_decision_made_before_it(self):
        before = datetime(2026, 11, 23, 8, 27, tzinfo=timezone.utc)
        w = TD.thin_world("LIVE", "NATIVE_GATES")
        brief = B.build_brief(dict(copy.deepcopy(w), codex_feed=TD.codex_feed_of(w)))
        body, d = B.render_issue(dict(brief, generated_at=B.iso(before), decision_log=[]))
        self.assertEqual((d["action"], d["expires_at"]), ("MERGE", "2026-11-23T08:30:00Z"))
        for now, want in ((before + timedelta(minutes=5), "MONDAY_READ_ONLY"), (before + timedelta(minutes=30), "MONDAY_READ_ONLY")):
            gh = FakeGitHub(copy.deepcopy(w), now)
            run = E.Run(gh, FakeNative(w), dict(ENV), {"switch": w["switch"], "contract": w["contract"], "policy": TB.POLICY, "gate_isolation": "LIVE",
                                                       "bindings": TB.BINDINGS, "budgets": TB.BUDGETS}, now_fn=lambda: now, out=lambda line: None)
            out = run.execute(body)
            self.assertEqual((out["result"], gh.writes), (want, []))


def live_cases():
    """name -> (live mutation after the decision, the skipped reason). Each is ONE fact the executor re-reads natively."""
    def pr_field(**kw):
        return lambda w, gh, n: gh.pull.update(**kw)

    def data(key, value):
        return lambda w, gh, n: w["pr"][7].update({key: value})

    return {
        "head moved": (lambda w, gh, n: gh.pull["head"].update(sha="c" * 40), "7:C8:head_changed"),
        "PR closed": (pr_field(state="closed"), "7:C8:state"),
        "PR already merged": (pr_field(merged=True), "7:C8:state"),
        "converted to draft (an owner veto)": (pr_field(draft=True), "7:C8:state"),
        "base is not main": (lambda w, gh, n: gh.pull["base"].update(ref="dev"), "7:B1:fork_head"),
        "head repository is a fork": (lambda w, gh, n: gh.pull["head"].update(repo={"id": 999}), "7:B1:fork_head"),
        "repository identity": (lambda w, gh, n: w["repo"].update(id=5), "B1:repository_identity"),
        "merge conflict": (pr_field(mergeable=False), "7:C2:mergeable"),
        "a file was added to the PR": (lambda w, gh, n: (w["pr"][7]["files"].append(TD.file_("docs/notes/c.md")), gh.pull.update(changed_files=3)), "7:C8:files_changed"),
        "a file was swapped at the same count": (lambda w, gh, n: w["pr"][7]["files"][0].update(filename="docs/notes/z.md"), "7:C8:files_changed"),
        "the file list is incomplete": (data("files_complete", False), "7:C8:files_changed"),
        "the diff gained a repository writer": (lambda w, gh, n: w["pr"][7]["files"][0].update(patch="@@\n+os.system('git push')"), "7:C2:owner_gated"),
        "retitled to a money word": (pr_field(title="docs: wallet"), "7:C2:judgment"),
        "an S1_ITEM_v1 raised the risk to HIGH": (lambda w, gh, n: w["pr"][7]["comments"].append(
            TB.comment(81, "S1_ITEM_v1\nitem: pr:7\nstate: REVIEW\nkind: FIX\nrisk: HIGH\ncontract=44444444", minutes_ago=200)), "7:C2:risk"),
        "an S1_ITEM_v1 says DIRECTION": (lambda w, gh, n: w["pr"][7]["comments"].append(
            TB.comment(81, "S1_ITEM_v1\nitem: pr:7\nstate: REVIEW\nkind: DIRECTION\nrisk: LOW\ncontract=44444444", minutes_ago=200)), "7:C5:strategist"),
        "a file of the diff now shrinks": (lambda w, gh, n: w["pr"][7]["files"][0].update(additions=1, deletions=9), "7:C2:shrinks"),
        "retitled harmlessly": (pr_field(title="docs: another note"), "7:C8:title_changed"),
        "a hold label arrived (an owner veto)": (pr_field(labels=[{"name": "s1-hold"}]), "7:C2:judgment"),
        "a required job failed in a newer attempt": (lambda w, gh, n: w["pr"][7]["jobs"][101][1].update(conclusion="failure"), "7:C4:ci_identity:gate"),
        "a newer run attempt exists": (lambda w, gh, n: (w["pr"][7]["runs"][0].update(run_attempt=2), [j.update(run_attempt=2) for j in w["pr"][7]["jobs"][101]]),
                                         "7:C4:ci_identity:privacy-scan"),
        "another job id proves the tuple": (lambda w, gh, n: w["pr"][7]["jobs"][103][0].update(id=4242), "7:C4:ci_identity:test"),
        "a check run is pending": (lambda w, gh, n: w["pr"][7]["check_runs"].append({"id": 99, "name": "x", "status": "queued", "conclusion": None, "app": {"slug": "y"}}), "7:C4:checks"),
        "a failed commit status": (lambda w, gh, n: w["pr"][7]["statuses"].append({"id": 1, "context": "ci", "state": "failure"}), "7:C4:checks"),
        "the privacy line is gone": (data("privacy_log", "no marker"), "7:C3:privacy_line"),
        "the privacy line names another head": (lambda w, gh, n: w["pr"][7].update(privacy_log=w["pr"][7]["privacy_log"].replace(HEAD, "c" * 40)), "7:C3:privacy_line"),
        "two privacy lines": (lambda w, gh, n: w["pr"][7].update(privacy_log=w["pr"][7]["privacy_log"] * 2), "7:C3:privacy_line"),
        "CHANGES_REQUESTED arrived (an owner veto)": (lambda w, gh, n: w["pr"][7]["reviews"].append({"id": 5, "state": "CHANGES_REQUESTED", "commit_id": HEAD, "user": {"login": "x"}}),
                                                       "7:C5:changes_requested"),
        "CHANGES_REQUESTED on an OLDER commit (a push never lifts the veto)": (
            lambda w, gh, n: w["pr"][7]["reviews"].append({"id": 5, "state": "CHANGES_REQUESTED", "commit_id": "f" * 40, "user": {"login": "Donh91"}}), "7:C5:changes_requested"),
        "a HIGH_IMPACT label arrived (an owner veto)": (pr_field(labels=[{"name": "HIGH_IMPACT"}]), "7:C2:judgment"),
        "a P0 label arrived (an owner veto)": (pr_field(labels=[{"name": "P0"}]), "7:C2:judgment"),
        "a priority: high label arrived (an owner veto)": (pr_field(labels=[{"name": "priority: high"}]), "7:C2:judgment"),
        "a risk:high label arrived (an owner veto)": (pr_field(labels=[{"name": "risk:high"}]), "7:C2:judgment"),
        "an auto-trading label arrived (an owner veto)": (pr_field(labels=[{"name": "auto-trading"}]), "7:C2:judgment"),
        "the body gained a money word": (pr_field(body="Enables LIVE trading with real funds on Jupiter"), "7:C2:judgment"),
        "the body gained a credential word": (pr_field(body="also rotates the deploy key in .env"), "7:C2:judgment"),
        "retitled to a money word inside an identifier": (pr_field(title="docs: placeOrder"), "7:C2:judgment"),
        "retitled to a draft": (pr_field(title="DRAFT: docs: a note"), "7:C2:judgment"),
        "the branch turns out to be an AI branch and the review is gone": (
            lambda w, gh, n: (w["pr"][7].update(comments=[]), gh.pull["head"].update(ref="claude/x")), "7:C5:ai_authored"),
        "the head turns out to be Codex-authored and the review is gone": (
            lambda w, gh, n: (w["pr"][7].update(comments=[]), w["pr"][7]["commits"][0].update(author={"login": B.CODEX_BOT_LOGIN})), "7:C5:codex_authored"),
        "the head turns out to be Codex-authored and the review is still there": (
            lambda w, gh, n: w["pr"][7]["commits"][0].update(author={"login": B.CODEX_BOT_LOGIN}), "7:C5:codex_authored"),
        "a P0 thread arrived (an owner veto)": (data("threads", [{"resolved": False, "first_body": "p0 data loss"}]), "7:C6:unresolved_p0p1"),
        "threads unreadable": (data("threads", None), "BRIEF_INCOMPLETE(executor:RuntimeError)"),
        "review reads incomplete": (data("review_reads_complete", False), "7:C5:reviews_unreadable"),
        "a new @codex address request": (lambda w, gh, n: w["pr"][7]["comments"].append(TB.comment(80, "@codex address x", minutes_ago=1)), "7:C1:concurrent_writer"),
        "codex posted findings": (lambda w, gh, n: w["pr"][7]["comments"][1].update(
            body="<!-- codex-review-state:v1 " + json.dumps({"code_review": {"commit_sha": HEAD, "status": "completed", "has_unresolved_findings": True}}) + " -->"),
            "7:C5:codex_findings"),
        "the codex review vanished (the PR holds code: no merge without a review)": (lambda w, gh, n: w["pr"][7].update(comments=[]), "7:C5:review_required"),
        "the PR turns out to be opened by a bot and the review is gone": (lambda w, gh, n: (w["pr"][7].update(comments=[]), gh.pull.update(user=dict(TB.BOT))), "7:C5:bot_authored"),
        "main moved with a code change": (lambda w, gh, n: (setattr(gh, "main", MAIN2), setattr(n, "drift_paths", ["scripts/x.py"])), "BRIEF_STALE(source_changed)"),
        "main moved and touched a file of the PR": (lambda w, gh, n: (setattr(gh, "main", MAIN2), setattr(n, "drift_paths", ["docs/notes/a.md"])), "C2:needs_branch_update"),
        "main was rewound (not ahead)": (lambda w, gh, n: (setattr(gh, "main", MAIN2), setattr(n, "relation", "behind")), "BRIEF_STALE(drift:behind)"),
        "main drift unreadable": (lambda w, gh, n: (setattr(gh, "main", MAIN2), setattr(n, "relation", "unknown")), "BRIEF_STALE(drift:unknown)"),
        "main drift too large": (lambda w, gh, n: (setattr(gh, "main", MAIN2), setattr(n, "drift_paths", ["d/%d.json" % i for i in range(B.DRIFT_MAX_FILES)])),
                                 "BRIEF_STALE(drift_unreadable)"),
        "a pin changed at current main": (lambda w, gh, n: w["pins_actual"].update({".github": "f" * 40}), "lane:C7:pins:.github"),
        "the contract blob changed at current main": (lambda w, gh, n: w["pins_actual"].update({B.CONTRACT_FILE: "f" * 40}), "lane:C7:pins:contract_blob"),
        "the tick blob changed at current main": (lambda w, gh, n: w["pins_actual"].update({"00_FMOS/S1/TICK.md": "f" * 40}), "lane:C7:pins:00_FMOS/S1/TICK.md"),
        "an owner halt was posted (an owner veto)": (lambda w, gh, n: w["issue_comments"].append(TB.comment(60, "S1_LANE_HALTED PR=- head=-\nreason: owner", minutes_ago=1)), "lane:C7:halt c=60"),
        "a halt reached the ledger after the ledger read": (lambda w, gh, n: gh.late.append(TB.comment(61, "S1_LANE_HALTED PR=- head=-", minutes_ago=0)), "lane:C7:halt_after_read"),
        "another intent reached the ledger after the read": (lambda w, gh, n: gh.late.append(TB.comment(62, "S1_LANE_MERGE_INTENT_v1\npr: 9", TB.BOT, 0)), "lane:C9:intent_after_read"),
        "the ledger cannot be read completely": (lambda w, gh, n: w.update(issue_comments_complete=False), "lane:C7:ledger_unreadable"),
        "main health failed meanwhile": (lambda w, gh, n: w["health_runs"].append(dict(w["health_runs"][0], id=950, conclusion="failure", updated_at=TB.ts(1))), "lane:C7:main_health:main_health_failed"),
        "a ruleset became active": (lambda w, gh, n: w.update(rulesets_1=[{"id": 1, "target": "branch", "enforcement": "active", "updated_at": "x"}]), "lane:C8:ruleset_census"),
        "main became protected": (lambda w, gh, n: w.update(main_protected=True), "lane:C8:ruleset_unproven"),
        "a receipt for this PR and head exists": (lambda w, gh, n: w["issue_comments"].append(TB.comment(63, f"S1_LANE_MERGE_v1\npr: 7\nhead: {HEAD}\ncontract=44444444", TB.BOT, 3)), "7:C9:already_done"),
        "ONE earlier attempt at this head, settled by the owner (no retry, ever)": (lambda w, gh, n: w["issue_comments"].extend(
            [TB.comment(64, f"S1_LANE_MERGE_INTENT_v1\npr: 7\nhead: {HEAD}\nloop={'4' * 40}\ncontract=44444444", TB.BOT, 200),
             TB.comment(65, "S1_OP_DONE_v1\nintent: 64\nresult: ABSENT\ncontract=44444444", TB.OWNER, 199)]), "7:C9:attempted_head"),
        "ONE earlier attempt at this head, settled by a proven executor run": (lambda w, gh, n: (
            gh.runs.update({540: executor_run(540, created=NOW - timedelta(minutes=202))}), w["issue_comments"].extend(
                [TB.comment(64, f"S1_LANE_MERGE_INTENT_v1\npr: 7\nhead: {HEAD}\nloop={'4' * 40}\nexecutor: GITHUB run=540\ncontract=44444444", TB.BOT, 200),
                 TB.comment(65, "S1_OP_DONE_v1\nintent: 64\nresult: ABSENT\nexecutor: GITHUB run=540\ncontract=44444444", TB.BOT, 199)])), "7:C9:attempted_head"),
        "an earlier attempt of the ChatGPT task at this head": (lambda w, gh, n: w["issue_comments"].extend(
            [TB.comment(64, f"S1_LANE_MERGE_INTENT_v1\npr: 7\nhead: {HEAD}\nloop={'4' * 40}\ncontract=44444444", TB.OWNER, 200),
             TB.comment(65, "S1_LANE_HALTED PR=7 head=-\nreason: x\ncontract=44444444", TB.OWNER, 199)]), "lane:C7:halt c=65"),
    }


class NativeReverification(unittest.TestCase):
    """Every fact is read again right before the write; any one of them stops the merge with no write at all."""

    def test_invariant_each_live_fact_stops_the_merge_with_no_write(self):
        for name, (live, reason) in live_cases().items():
            for mode in ("LIVE", "SHADOW"):
                with self.subTest(name=name, mode=mode):
                    out, gh, _n, d = execute(mode=mode, live=live, mutate=lambda w: w["issue_comments"].append(
                        TB.comment(40, "S1_HEARTBEAT_v1 main=aaaaaaaa contract=44444444", TB.BOT, 60)))     # today's heartbeat exists: any write would be the merge path
                    self.assertEqual(d["action"], "MERGE")                              # the decision itself still says MERGE
                    self.assertEqual(gh.writes, [], out["result"])
                    self.assertEqual(out["action"], "NOOP")
                    self.assertIn(reason, out["result"])

    def test_the_cases_cover_every_fact_the_owner_decision_names(self):
        names = " ".join(live_cases())
        for fact in ("head", "job", "privacy", "CHANGES_REQUESTED", "P0", "title", "label", "pin", "halt", "ruleset", "main moved", "file", "ledger", "health"):
            self.assertIn(fact.lower(), names.lower(), fact)

    def test_data_only_drift_of_main_is_accepted(self):
        out, gh, native, _d = execute(live=lambda w, gh, n: setattr(gh, "main", MAIN2))
        self.assertTrue(out["result"].startswith("MERGED("), out["result"])
        self.assertIn(("drift", MAIN, MAIN2), native.calls)
        self.assertIn(("tree_shas", MAIN2), native.calls)                              # the pins were read at CURRENT main

    def test_a_refused_merge_is_never_retried_and_leaves_the_intent_for_reconcile(self):
        for err, want in ((urllib.error.HTTPError("u", 405, "Not Allowed", {}, None), "MERGE_REFUSED(405)"),
                          (urllib.error.HTTPError("u", 409, "Conflict", {}, None), "MERGE_REFUSED(409)"), (TimeoutError("t"), "MERGE_REFUSED(TimeoutError)")):
            out, gh, _n, _d = execute(live=lambda w, gh, n: setattr(gh, "fail_merge", err))
            self.assertEqual((out["action"], out["result"]), ("NOOP", want))
            self.assertEqual(tokens(gh), ["S1_HEARTBEAT_v1", "S1_LANE_MERGE_INTENT_v1", "MERGE"])             # one merge call, nothing after it
            self.assertEqual(len(B.open_intents(gh.w["issue_comments"], NOW + timedelta(minutes=3), 0, gh.run_of)), 1)
            self.assertEqual(out["alarms"], ["intent_without_outcome(c=7002)"])                               # ... and it is not silent (P2-7)

    def test_invariant_a_readback_mismatch_posts_a_halt(self):
        cases = {"a blob differs from the head": (lambda w, gh, n: n.merged_blobs.update({"docs/notes/a.md": "other"}), "blob:docs/notes/a.md"),
                 "the merge commit is not on main": (lambda w, gh, n: setattr(n, "ancestor", False), "not_on_main")}
        for name, (live, why) in cases.items():
            with self.subTest(name):
                out, gh, _n, _d = execute(live=live)
                self.assertEqual(out["result"], f"LANE_HALTED(readback:{why})")
                self.assertEqual(tokens(gh), ["S1_HEARTBEAT_v1", "S1_LANE_MERGE_INTENT_v1", "MERGE", "S1_LANE_HALTED"])
                halt = gh.writes[-1][2]["body"]
                self.assertTrue(halt.startswith(f"S1_LANE_HALTED PR=7 head={HEAD}\nreason: readback\n"))
                self.assertIsNotNone(B.standing_halt(B.lane_halts(gh.w["issue_comments"]), None))             # the next brief reads the lane OFF
                self.assertEqual(B.open_intents(gh.w["issue_comments"], NOW + timedelta(minutes=5), 0, gh.run_of), [])  # and the intent is settled
                self.assertEqual(out["alarms"], [f"readback_mismatch({why})"])


class ReadbackVerdict(unittest.TestCase):
    def setUp(self):
        self.pr = {"number": 7, "merged": True, "merged_at": TB.ts(-1), "head": {"sha": HEAD}, "merged_by": {"login": "github-actions[bot]"}, "merge_commit_sha": MERGE_SHA}
        self.commit = {"sha": MERGE_SHA, "parents": [{"sha": MAIN}], "commit": {"message": "docs: x (#7)\n\nbody"}}
        self.blobs = [("a", "1", "1"), ("gone", None, None)]

    def verdict(self, pr=None, commit="same", blobs="same", ancestor=True, intent_at=None, **kw):
        return D.readback_verdict(self.pr if pr is None else pr, HEAD, intent_at or TB.ts(0), self.commit if commit == "same" else commit,
                                  self.blobs if blobs == "same" else blobs, ancestor, NOW, **kw)

    def test_match(self):
        self.assertEqual(self.verdict(), ("MATCH", "paths=2"))

    def test_every_c10_fact(self):
        p = self.pr
        self.assertEqual(self.verdict(pr=dict(p, merged=False)), ("ABSENT", "not_merged"))
        self.assertEqual(self.verdict(pr=dict(p, head={"sha": "c" * 40})), ("FOREIGN", "other_head"))
        self.assertEqual(self.verdict(pr=dict(p, merged_at=TB.ts(10))), ("FOREIGN", "outside_intent_window"))      # merged before the intent
        self.assertEqual(self.verdict(pr=dict(p, merged_at=TB.ts(-16))), ("FOREIGN", "outside_intent_window"))     # later than the origin window
        self.assertEqual(self.verdict(pr=dict(p, merged_by={"login": "Donh91"})), ("FOREIGN", "other_actor"))       # the owner's own merge is never ours
        self.assertEqual(self.verdict(pr=dict(p, merged_by={"login": "Donh91"}), executor_login="Donh91"), ("MATCH", "paths=2"))
        self.assertEqual(self.verdict(commit=None), ("MISMATCH", "merge_commit_unreadable"))
        self.assertEqual(self.verdict(commit=dict(self.commit, sha="c" * 40)), ("MISMATCH", "merge_commit_unreadable"))
        self.assertEqual(self.verdict(commit=dict(self.commit, parents=[{"sha": MAIN}, {"sha": HEAD}])), ("MISMATCH", "parents"))
        self.assertEqual(self.verdict(commit=dict(self.commit, commit={"message": "docs: x (#8)"})), ("MISMATCH", "subject"))
        self.assertEqual(self.verdict(commit=dict(self.commit, commit={"message": "docs: x\n\n(#7)"})), ("MISMATCH", "subject"))
        self.assertEqual(self.verdict(ancestor=False), ("MISMATCH", "not_on_main"))
        self.assertEqual(self.verdict(ancestor=None), ("MISMATCH", "not_on_main"))
        self.assertEqual(self.verdict(blobs=[("a", "1", "2")]), ("MISMATCH", "blob:a"))
        self.assertEqual(self.verdict(blobs=[("a", None, "2")]), ("MISMATCH", "blob:a"))
        self.assertEqual(self.verdict(blobs=[]), ("MISMATCH", "blobs_unreadable"))
        self.assertEqual(self.verdict(blobs=None), ("MISMATCH", "blobs_unreadable"))
        self.assertEqual(self.verdict(pr={}), ("UNREADABLE", "pr"))
        self.assertEqual(self.verdict(pr=dict(p, merged_at=None)), ("UNREADABLE", "timestamps"))


class Reconcile(unittest.TestCase):
    """An intent with no outcome (a run that died between the intent and the receipt) is settled from native state."""

    def intent(self, w, minutes_ago=30, user=None, head=HEAD):
        w["issue_comments"].append(TB.comment(300, f"S1_LANE_MERGE_INTENT_v1\npr: 7\nhead: {head}\nmain: {MAIN}\nloop={'4' * 40}\nbrief=500\ndecision=500.1\ncontract=44444444",
                                              user or TB.BOT, minutes_ago))
        w["issue_comments"].append(TB.comment(301, "S1_HEARTBEAT_v1 main=aaaaaaaa contract=44444444", TB.BOT, 60))

    def merged(self, by="github-actions[bot]", minutes_ago=29, **kw):
        def live(w, gh, n):
            gh.pull.update(merged=True, state="closed", merged_at=TB.ts(minutes_ago), merge_commit_sha=MERGE_SHA, merged_by={"login": by}, **kw)
            w.setdefault("commit_objects", {})[MERGE_SHA] = {"sha": MERGE_SHA, "parents": [{"sha": MAIN}], "commit": {"message": "docs (#7)"}}
        return live

    def test_the_brief_holds_every_merge_while_an_intent_is_open(self):
        d, _b = TD.decide(lambda w: self.intent(w), "LIVE")
        self.assertEqual((d["action"], d["skipped"][:1]), ("NOOP", ["lane:C9:open_merge_intent"]))

    def test_a_merge_that_landed_gets_its_missing_receipt(self):
        out, gh, _n, _d = execute(mutate=lambda w: self.intent(w), live=self.merged())
        self.assertEqual((out["action"], out["result"]), ("MERGE", "RECONCILED(c=300)"))
        self.assertEqual(tokens(gh), ["S1_LANE_MERGE_v1"])
        body = gh.writes[0][2]["body"]
        self.assertTrue(body.startswith("S1_LANE_MERGE_v1 reconciled\npr: 7\n"))
        for line in ("merge_execution_origin: UNKNOWN", "executor: GITHUB run=555", "intent: 300", "evidence_gap: review, privacy, ci, main_health",
                     "review: unavailable", "brief=500"):
            self.assertIn(line, body.splitlines())
        self.assertEqual(B.open_intents(gh.w["issue_comments"], NOW + timedelta(minutes=5), 0, gh.run_of), [])

    def test_a_reconcile_mismatch_is_a_halt(self):
        out, gh, _n, _d = execute(mutate=lambda w: self.intent(w), live=lambda w, gh, n: (self.merged()(w, gh, n), n.merged_blobs.update({"docs/notes/a.md": "x"})))
        self.assertEqual(out["result"], "LANE_HALTED(reconcile:blob:docs/notes/a.md)")
        self.assertEqual(tokens(gh), ["S1_LANE_HALTED"])
        self.assertIn("reason: reconcile_readback", gh.writes[0][2]["body"])

    def test_absent_and_foreign_are_one_record_and_never_a_merge(self):
        out, gh, _n, _d = execute(mutate=lambda w: self.intent(w))                      # the PR is still open: ABSENT
        self.assertEqual(tokens(gh), ["S1_OP_DONE_v1"])
        self.assertIn("result: ABSENT", gh.writes[0][2]["body"])
        self.assertEqual(out["action"], "NOOP")
        for live in (self.merged(by="Donh91"), self.merged(minutes_ago=5), self.merged(head={"sha": "c" * 40})):
            out, gh, _n, _d = execute(mutate=lambda w: self.intent(w), live=live)
            self.assertEqual(tokens(gh), ["S1_OP_DONE_v1"])
            self.assertIn("result: FOREIGN", gh.writes[0][2]["body"])
        self.assertFalse(any(w[0] == "PUT" for w in gh.writes))                         # RECONCILE never merges

    def test_an_intent_of_the_chatgpt_task_is_reconciled_under_its_own_actor(self):
        out, gh, _n, _d = execute(mutate=lambda w: self.intent(w, user=TB.OWNER), live=self.merged(by="Donh91"))
        self.assertEqual(out["result"], "RECONCILED(c=300)")
        out, gh, _n, _d = execute(mutate=lambda w: self.intent(w, user=TB.OWNER), live=self.merged(by="github-actions[bot]"))
        self.assertIn("result: FOREIGN", gh.writes[0][2]["body"])

    def test_shadow_reconciles_nothing(self):
        out, gh, _n, _d = execute(mode="SHADOW", mutate=lambda w: self.intent(w), live=self.merged())
        self.assertEqual(gh.writes, [])
        self.assertIn("S1_EXECUTOR_RECONCILE WOULD_RECONCILE(300:MATCH)", out["lines"])   # it says what it would do, by its own mode check
        self.assertNotIn("executor_not_live", out["result"])


class Halts(unittest.TestCase):
    def c1b(self, w):
        TD.halt_c1b(w)
        w["commit_objects"] = {"c" * 40: {"sha": "c" * 40, "parents": [{"sha": "d" * 40}], "commit": {"message": "ops: direct push"}}}
        tree = lambda sha: {"truncated": False, "tree": [{"path": d, "type": "tree", "sha": sha if d == "scripts" else "0" * 40} for d in B.T3_TREE_DIRS]}
        w["tree_objects"] = {"d" * 40: tree("1" * 40), "c" * 40: tree("2" * 40)}

    def test_c1b_is_re_proven_and_posted_once(self):
        out, gh, _n, d = execute(mutate=self.c1b)
        self.assertEqual((d["action"], out["action"], out["result"]), ("HALT", "NOOP", "LANE_HALTED(c1b)"))
        self.assertEqual(tokens(gh), ["S1_HEARTBEAT_v1", "S1_LANE_HALTED"])
        body = gh.writes[-1][2]["body"]
        self.assertEqual(body.splitlines()[:3], ["S1_LANE_HALTED PR=- head=-", "reason: unreviewed_code_on_main", f"commit: {'c' * 40}"])
        self.assertFalse(any(w[0] == "PUT" for w in gh.writes))                         # a halt decision never merges
        # the next run sees it named and posts nothing more
        out2, gh2, _n, _d = execute(mutate=lambda w: (self.c1b(w), w["issue_comments"].append(TB.comment(70, body, TB.BOT, 5)),
                                                      w["issue_comments"].append(TB.comment(71, "S1_HEARTBEAT_v1 main=a contract=44444444", TB.BOT, 5))))
        self.assertEqual(gh2.writes, [])

    def test_c1b_checks_that_fail_post_nothing(self):
        cases = {"it is a squash merge": lambda w, gh, n: w["commit_objects"]["c" * 40]["commit"].update(message="fix: x (#12)"),
                 "the trees are equal": lambda w, gh, n: w["tree_objects"].update({"c" * 40: w["tree_objects"]["d" * 40]}),
                 "the commit is not on main": lambda w, gh, n: setattr(n, "ancestor", False),
                 "the commit cannot be read": lambda w, gh, n: w["commit_objects"].clear()}
        for name, live in cases.items():
            with self.subTest(name):
                out, gh, _n, _d = execute(mutate=lambda w: (self.c1b(w), w["issue_comments"].append(TB.comment(71, "S1_HEARTBEAT_v1 main=a contract=44444444", TB.BOT, 5))), live=live)
                self.assertEqual((out["action"], gh.writes), ("NOOP", []))

    def test_c7_failed_main_health_run(self):
        out, gh, _n, d = execute(mutate=TD.halt_c7)
        self.assertEqual((d["halt"], out["result"]), ({"source": "C7", "run": 901}, "LANE_HALTED(main_health)"))
        self.assertIn("run=901", gh.writes[-1][2]["body"].splitlines())
        out, gh, _n, _d = execute(mutate=lambda w: (TD.halt_c7(w), w["issue_comments"].append(TB.comment(71, "S1_HEARTBEAT_v1 main=a contract=44444444", TB.BOT, 5))),
                                  live=lambda w, gh, n: w["health_runs"][1].update(conclusion="success"))
        self.assertEqual(gh.writes, [])

    def test_shadow_halts_nothing(self):
        out, gh, _n, _d = execute(mode="SHADOW", mutate=self.c1b)
        self.assertEqual((out["result"], gh.writes), ("WOULD_HALT(c1b:cccccccc)", []))


class Heartbeat(unittest.TestCase):
    def test_once_per_copenhagen_day_and_never_instead_of_the_action(self):
        out, gh, _n, _d = execute(mutate=lambda w: w.update(pulls=[], pr={}))
        self.assertEqual(tokens(gh), ["S1_HEARTBEAT_v1"])
        body = gh.writes[0][2]["body"]
        self.assertTrue(body.startswith("S1_HEARTBEAT_v1 main=aaaaaaaa contract=44444444 ticks_24h=25 last_noop=UNKNOWN last_action=NONE open_ops=0 closures=UNKNOWN\n"))
        self.assertIn("brief=555 brief_state=OK executor=GITHUB mode=LIVE run=555", body.splitlines())
        self.assertEqual(len(B.heartbeats([dict(TB.comment(1, body, TB.BOT, 0))])), 1)   # the brief counts it as today's heartbeat
        out, gh, _n, _d = execute(mutate=lambda w: (w.update(pulls=[], pr={}), w["issue_comments"].append(TB.comment(71, "S1_HEARTBEAT_v1 main=a contract=44444444", TB.OWNER, 5))))
        self.assertEqual(gh.writes, [])
        out, gh, _n, _d = execute(mode="SHADOW", mutate=lambda w: w.update(pulls=[], pr={}))
        self.assertEqual(gh.writes, [])


class Harness(unittest.TestCase):
    """Dry-run measurement: reads and writes of ONE executor run, per run type (the fake counts every call)."""

    def measure(self, **kw):
        out, gh, native, _d = execute(**kw)
        reads = sum(1 for kind, _p in gh.calls if kind in ("GET", "PAGES", "TEXT", "GRAPHQL"))
        return reads, len(gh.writes), len(native.calls), out["result"]

    def test_calls_per_run_type(self):
        beat = lambda w: w["issue_comments"].append(TB.comment(71, "S1_HEARTBEAT_v1 main=a contract=44444444", TB.BOT, 5))
        table = {
            "NOOP (nothing actionable)": self.measure(mutate=lambda w: (beat(w), w.update(pulls=[], pr={}))),
            "NOOP + heartbeat": self.measure(mutate=lambda w: w.update(pulls=[], pr={})),
            "MERGE live": self.measure(mutate=beat),
            "MERGE shadow": self.measure(mode="SHADOW", mutate=beat),
            "OFF": self.measure(mode="OFF", policy="CODEX_FINAL_REQUIRED"),
        }
        self.assertEqual(table["OFF"][:2], (0, 0))
        self.assertEqual(table["NOOP (nothing actionable)"][:2], (1, 0))               # the ledger read only
        self.assertEqual(table["NOOP + heartbeat"][:2], (2, 1))
        self.assertEqual(table["MERGE live"][1], 3)                                    # intent, merge, receipt
        self.assertEqual(table["MERGE shadow"][1], 0)
        self.assertLessEqual(table["MERGE live"][0], 40)
        self.assertLess(table["MERGE live"][0], E.EXECUTE_API_CALLS)
        self.assertEqual(table["MERGE live"][0] - table["MERGE shadow"][0], 3)         # the readback: the PR, the merge commit, main
        self.__class__.table = table


class WorkflowAndSwitch(unittest.TestCase):
    """The executor job as shipped: read-only, never on a PR event, main's own scripts only; and LIVE needs both halves."""

    def setUp(self):
        self.job = WORKFLOW["jobs"]["execute"]
        self.text = (ROOT / B.WORKFLOW_PATH).read_text(encoding="utf-8")

    def test_triggers_and_gating(self):
        self.assertEqual(sorted(WORKFLOW[True]), ["push", "schedule", "workflow_dispatch", "workflow_run"])
        self.assertNotIn("pull_request", self.text.replace("pull-requests", ""))       # no pull_request or pull_request_target trigger at all
        cond = " ".join(self.job["if"].split())
        self.assertEqual(cond, "github.ref == 'refs/heads/main' && github.repository == 'Donh91/Investering-Framework-Archive-v1' && "
                               "(github.event_name == 'schedule' || github.event_name == 'workflow_dispatch') && needs.build.outputs.brief != ''")
        self.assertEqual(self.job["needs"], ["build", "publish"])
        self.assertEqual(self.job["concurrency"], {"group": "s1-executor", "cancel-in-progress": False})
        self.assertEqual(E.EVENTS, ("schedule", "workflow_dispatch"))

    def test_a_failed_executor_job_never_fails_the_run_that_carries_the_brief(self):
        # TICK.md T2 (run_not_success) and the next build's C1b anchor (previous_anchor) accept a brief only from a run
        # whose conclusion is success. The executor runs AFTER the publish, in the same run, so its failure must not
        # change that conclusion: continue-on-error at JOB level (the job itself still shows as failed).
        self.assertIs(self.job["continue-on-error"], True)
        self.assertNotIn("continue-on-error", {k for name, job in WORKFLOW["jobs"].items() if name != "execute" for k in job})
        self.assertEqual([name for name, job in WORKFLOW["jobs"].items() if "execute" in (job.get("needs") or [])], [])   # nothing waits for it
        run = {"id": 555, "path": B.WORKFLOW_PATH, "repository": {"full_name": B.REPO}, "head_branch": "main", "head_sha": MAIN, "status": "completed",
               "run_started_at": TB.ts(5), "updated_at": TB.ts(-5)}
        brief = {"run_id": 555, "main": MAIN, "generated_at": TB.ts(2), "c1b": {"checked_through": MAIN}}
        issue = {"updated_at": TB.ts(1)}
        self.assertEqual(B.previous_anchor(issue, brief, dict(run, conclusion="success"), NOW), ([MAIN], None, None))
        self.assertEqual(B.previous_anchor(issue, brief, dict(run, conclusion="failure"), NOW), ([], None, "run_not_success"))   # what a failing run would cost

    def test_it_runs_only_mains_own_scripts(self):
        steps = self.job["steps"]
        self.assertEqual([(s.get("uses") or "").split("@")[0] for s in steps], ["actions/checkout", "actions/setup-python", ""])
        if SWITCH["executor"] != "LIVE":
            self.assertEqual([s.get("uses") for s in steps], ["actions/checkout@v4", "actions/setup-python@v5", None])   # as every other job of this file
        self.assertEqual(steps[0]["with"], {"ref": "${{ github.sha }}", "persist-credentials": False, "sparse-checkout": "scripts/governance\n00_FMOS\n"})
        run = steps[2]["run"]
        self.assertEqual([line.strip() for line in run.strip().splitlines()],
                         ['printf \'%s\' "$BRIEF_B64" | base64 -d > "$RUNNER_TEMP/brief.md"', 'python scripts/governance/s1_executor_v1.py execute "$RUNNER_TEMP/brief.md"'])
        self.assertEqual(sorted(steps[2]["env"]), ["BRIEF_B64", "GITHUB_TOKEN", "PYTHONDONTWRITEBYTECODE", "S1_EXECUTOR_HOLD"])
        self.assertEqual(steps[2]["env"]["S1_EXECUTOR_HOLD"], "${{ vars.S1_EXECUTOR_HOLD }}")
        self.assertNotIn("secrets.", self.text)
        for step in steps:
            self.assertNotIn("continue-on-error", step)
        # the PR head is data: the executor never fetches, checks out, imports or runs it
        for token in ("worktree", "checkout\", ", "import_module", "exec(", "eval(", "derive("):
            self.assertNotIn(token, SOURCE, token)

    def test_live_needs_the_switch_and_the_permissions_together(self):
        perms = self.job["permissions"]
        read_only = {"contents": "read", "actions": "read", "pull-requests": "read", "issues": "read"}
        live = {"contents": "write", "actions": "read", "pull-requests": "write", "issues": "write"}
        self.assertIn(perms, (read_only, live))
        self.assertNotIn("actions", [k for k, v in perms.items() if v == "write"])     # actions: write is never granted (no dispatch)
        self.assertEqual(SWITCH["executor"] == "LIVE", perms == live,
                         "the switch reads LIVE if and only if the execute job holds the write permissions (the enable PR changes both)")
        for name, job in WORKFLOW["jobs"].items():
            if name != "execute":
                self.assertNotIn("write", [v for k, v in job["permissions"].items() if k in ("contents", "pull-requests", "actions")], name)
        self.assertEqual(WORKFLOW["permissions"], {})
        # review finding P3-10: a job that holds write permissions runs actions pinned by commit SHA, never by a tag
        uses = [s["uses"] for s in self.job["steps"] if s.get("uses")]
        self.assertEqual([u.split("@")[0] for u in uses], ["actions/checkout", "actions/setup-python"])
        if perms == live:
            for ref in uses:
                self.assertRegex(ref, r"^actions/[a-z-]+@[0-9a-f]{40}$", "the LIVE execute job pins its actions by commit SHA")
        # review finding P1-1 and the owner decision of 2026-11-25: NATIVE_GATES is not the owner's review route and is never shipped
        self.assertIn(SWITCH["review_policy"], ("CODEX_FINAL_REQUIRED", D.RECALL_POLICY))

    def test_as_shipped_the_executor_is_shadow_and_read_only(self):
        self.assertEqual(self.job["permissions"], {"contents": "read", "actions": "read", "pull-requests": "read", "issues": "read"})
        # the owner's review route of 2026-11-25 ships (Codex, a Claude receipt, or the Codex-offline fallback with recall)
        self.assertEqual((SWITCH["executor"], SWITCH["review_policy"]), ("SHADOW", "CODEX_CLAUDE_OR_OFFLINE_RECALL"))

    def test_the_brief_script_still_never_merges(self):
        brief_source = (ROOT / "scripts/governance/s1_tick_brief_v1.py").read_text(encoding="utf-8")
        self.assertNotIn("/merge", brief_source.replace("/merges", ""))
        self.assertNotIn("s1_executor_v1", brief_source)
        build = "\n".join(str(s.get("run", "")) for name in ("due", "build", "publish") for s in WORKFLOW["jobs"][name]["steps"])
        self.assertNotIn("s1_executor_v1", build)

    def test_read_files_reads_the_real_policy_files(self):
        files = E.read_files(ROOT)
        self.assertEqual(files["switch"], SWITCH)
        self.assertEqual(sorted(files), ["bindings", "budgets", "contract", "gate_isolation", "policy", "switch"])
        self.assertEqual(files["gate_isolation"], "LIVE")
        self.assertEqual(len(files["bindings"]["required_job_tuples"]), 5)


# ----------------------------------------------------------------------------------------------- fix round 1
BEAT = lambda w: w["issue_comments"].append(TB.comment(40, "S1_HEARTBEAT_v1 main=aaaaaaaa contract=44444444", TB.BOT, 60))   # today's heartbeat exists
INTENT = f"S1_LANE_MERGE_INTENT_v1\npr: 7\nhead: {HEAD}\nmain: {MAIN}\nloop={'4' * 40}\ncontract=44444444"
RUN_LINE = "executor: GITHUB run={}"


class HeadIsReadTwice(unittest.TestCase):
    """P3-8: section 0.2i says the head is read twice. The second read is the last read before the intent."""

    def test_invariant_a_head_that_moves_during_the_verification_is_never_merged(self):
        for mode in ("LIVE", "SHADOW"):
            out, gh, _n, d = execute(mode=mode, mutate=BEAT, live=lambda w, gh, n: setattr(gh, "head_from_read", (2, "c" * 40)))
            self.assertEqual(d["action"], "MERGE")
            self.assertEqual((out["action"], gh.writes), ("NOOP", []), mode)
            self.assertIn("7:C8:head_changed", out["result"])
            self.assertEqual(gh.pull_reads, 2)                                         # the first read passed; the SECOND one saw the new head
        # the control: a head that only moves at a third read (the readback, after the merge call) does not stop the intent
        out, gh, _n, _d = execute(mutate=BEAT, live=lambda w, gh, n: setattr(gh, "head_from_read", (3, "c" * 40)))
        self.assertEqual(tokens(gh)[:2], ["S1_LANE_MERGE_INTENT_v1", "MERGE"])

    def test_the_second_read_is_after_every_other_read_of_the_verification(self):
        out, gh, _n, _d = execute(mode="SHADOW", mutate=BEAT)
        reads = [i for i, (kind, path) in enumerate(gh.calls) if (kind, path) == ("GET", "pulls/7")]
        self.assertEqual(len(reads), 2)
        late = gh.calls[reads[1] + 1:]
        self.assertEqual(late, [("GET", f"issues/{B.OWNER_ISSUE}/comments")])          # only the last look at the ledger follows it


class SettlementIdentity(unittest.TestCase):
    """P2-4. About 30 workflows of the repository can post as github-actions[bot]. Settling an intent unblocks the lane,
    so a bot post settles one only when it is PROVEN to be the executor job's; the owner account always can."""

    def setUp(self):
        self.now = NOW
        self.runs = {540: executor_run(540, created=NOW - timedelta(minutes=32))}      # ran from -32 to -28 minutes
        self.run_of = lambda rid: copy.deepcopy(self.runs.get(int(rid)))

    def ledger(self, outcome, user=TB.BOT, run=540, minutes_ago=29, intent_user=TB.BOT, edited=False):
        rows = [TB.comment(300, INTENT + ("\n" + RUN_LINE.format(540) if intent_user is TB.BOT else ""), intent_user, 30)]
        if outcome:
            rows.append(TB.comment(301, outcome + ("\n" + RUN_LINE.format(run) if run is not None else ""), user, minutes_ago, edited=edited))
        return rows

    def open(self, rows, run_of="default"):
        return [i["id"] for i in B.open_intents(rows, self.now, 0, self.run_of if run_of == "default" else run_of)]

    def test_invariant_only_the_owner_or_a_proven_executor_post_settles_an_intent(self):
        done, receipt, halt = "S1_OP_DONE_v1\nintent: 300\nresult: ABSENT", f"S1_LANE_MERGE_v1\npr: 7\nhead: {HEAD}", "S1_LANE_HALTED PR=7 head=-\nreason: readback"
        for outcome in (done, receipt, halt):
            with self.subTest(outcome=outcome.split()[0]):
                self.assertEqual(self.open(self.ledger(None)), [300])
                self.assertEqual(self.open(self.ledger(outcome)), [])                                    # the executor's own post, run 540 proven
                self.assertEqual(self.open(self.ledger(outcome, user=TB.OWNER, run=None)), [])           # the owner account
                self.assertEqual(self.open(self.ledger(outcome, run=None)), [300])                       # a bot post that names no run
                self.assertEqual(self.open(self.ledger(outcome), run_of=None), [300])                    # no run reader: no bot post settles
                self.assertEqual(self.open(self.ledger(outcome), run_of=lambda rid: None), [300])        # the run does not exist
                self.assertEqual(self.open(self.ledger(outcome, edited=True)), [300])                    # an edited post
                self.assertEqual(self.open(self.ledger(outcome, user=TB.OWNER, run=None, edited=True)), [300])
                self.assertEqual(self.open(self.ledger(outcome, user={"login": "someone", "id": 9, "type": "User"})), [300])
                self.assertEqual(self.open(self.ledger(outcome, user={"login": "github-actions[bot]", "id": 7, "type": "Bot"})), [300])   # a look-alike

    def test_invariant_a_post_of_another_workflow_never_settles(self):
        done = "S1_OP_DONE_v1\nintent: 300\nresult: ABSENT"
        other = {
            "another workflow file": {"path": ".github/workflows/hourly-sequence-capture.yml"},
            "a run on another branch": {"head_branch": "claude/x"},
            "a pull_request run": {"event": "pull_request"},
            "a push run": {"event": "push"},
            "a workflow_run run": {"event": "workflow_run"},
            "another repository": {"repository": {"full_name": "someone/fork"}},
            "a fork head repository": {"head_repository": {"full_name": "someone/fork"}},
            "another run id in the answer": {"id": 541},
            "no timestamps": {"created_at": None},
            "an unreadable end": {"updated_at": "garbage"},
        }
        for name, change in other.items():
            with self.subTest(name):
                self.runs = {540: dict(executor_run(540, created=NOW - timedelta(minutes=32)), **change)}
                self.assertEqual(self.open(self.ledger(done)), [300])
        self.runs = {540: executor_run(540, created=NOW - timedelta(minutes=32))}
        self.assertEqual(self.open(self.ledger(done)), [])
        # the post must have been created while the run existed (2 minutes of slack on either side)
        for minutes_ago, settled in ((29, True), (33, True), (35, False), (27, True), (25, False), (5, False)):
            rows = self.ledger(done, minutes_ago=minutes_ago)
            rows[0] = TB.comment(300, INTENT, TB.OWNER, 60)                            # the intent itself is old enough either way
            self.assertEqual(self.open(rows) == [], settled, minutes_ago)
        # a run that is still in progress has no end yet: `now` is its end
        self.runs = {540: executor_run(540, created=NOW - timedelta(minutes=3), status="in_progress")}
        rows = [TB.comment(300, INTENT, TB.OWNER, 30), TB.comment(301, done + "\n" + RUN_LINE.format(540), TB.BOT, 1)]
        self.assertEqual(self.open(rows), [])
        # the FIRST run line of a post decides: a second one never overrides it
        rows = [TB.comment(300, INTENT, TB.OWNER, 30), TB.comment(301, done + "\nexecutor: GITHUB run=999\nexecutor: GITHUB run=540", TB.BOT, 1)]
        self.assertEqual(self.open(rows), [300])
        for line in ("executor: GITHUB run=540 x", " executor: GITHUB run=540", "executor: GITHUB run=", "executor: github run=540", "x executor: GITHUB run=540"):
            self.assertIsNone(B.executor_run("S1_OP_DONE_v1\n" + line), line)
        self.assertEqual(B.executor_run("S1_OP_DONE_v1\nexecutor: GITHUB run=540  \nx"), 540)

    def test_the_decision_holds_every_merge_until_a_proven_post_settles_the_intent(self):
        forged = lambda w: w["issue_comments"].extend([TB.comment(300, INTENT, TB.BOT, 30), TB.comment(301, "S1_OP_DONE_v1\nintent: 300\nresult: ABSENT", TB.BOT, 29)])
        d, brief = TD.decide(forged, "LIVE")
        self.assertEqual((d["action"], d["skipped"][0]), ("NOOP", "lane:C9:open_merge_intent"))            # before fix round 1 this was a MERGE
        self.assertEqual([i["id"] for i in brief["open_intents"]], [300])
        proven = lambda w: (forged(w), w["issue_comments"][-1].update(body="S1_OP_DONE_v1\nintent: 300\nresult: ABSENT\nexecutor: GITHUB run=540"),
                            w.update(executor_runs={"540": executor_run(540, created=NOW - timedelta(minutes=32))}))
        d, brief = TD.decide(proven, "LIVE")
        self.assertEqual(brief["open_intents"], [])
        self.assertEqual(d["skipped"], ["7:C9:attempted_head"])                        # settled; that head stays the owner's (one attempt per head)
        other_pr = lambda w: (proven(w), w["issue_comments"][-2].update(body=INTENT.replace("pr: 7", "pr: 9")))
        self.assertEqual(TD.decide(other_pr, "LIVE")[0]["action"], "MERGE")
        unread = lambda w: (proven(w), w.pop("executor_runs"))                         # a snapshot without the run record: not proven
        self.assertEqual(TD.decide(unread, "LIVE")[0]["skipped"][0], "lane:C9:open_merge_intent")

    def test_the_executor_settles_a_forged_settlement_itself_from_native_state(self):
        # another workflow "settled" the executor's intent; the executor does not believe it and reads the PR back
        forged = lambda w: (BEAT(w), w["issue_comments"].extend([TB.comment(300, INTENT, TB.BOT, 30),
                                                                   TB.comment(301, "S1_OP_DONE_v1\nintent: 300\nresult: ABSENT", TB.BOT, 29)]))
        out, gh, _n, d = execute(mutate=forged)
        self.assertEqual(d["action"], "NOOP")
        self.assertEqual(tokens(gh), ["S1_OP_DONE_v1"])
        self.assertIn(RUN_LINE.format(555), gh.writes[0][2]["body"].splitlines())
        self.assertEqual(B.open_intents(gh.w["issue_comments"], NOW + timedelta(minutes=5), 0, gh.run_of), [])
        self.assertIn(("GET", "pulls/7"), gh.calls)                                    # the native read the forged post tried to skip
        out, gh, _n, _d = execute(mode="SHADOW", mutate=forged)
        self.assertIn("S1_EXECUTOR_RECONCILE WOULD_RECONCILE(300:ABSENT)", out["lines"])

    def test_every_post_the_executor_writes_names_its_run(self):
        out, gh, _n, _d = execute()
        bodies = [data["body"] for method, _u, data in gh.writes if method == "POST"]
        self.assertEqual([B.first_line_token(b) for b in bodies], ["S1_HEARTBEAT_v1", "S1_LANE_MERGE_INTENT_v1", "S1_LANE_MERGE_v1"])
        for body in bodies[1:]:
            self.assertEqual(B.executor_run(body), 555, body.split()[0])
        for body in (D.halt_body("readback", pr=7, head=HEAD, run_id=555), D.op_done_body(300, "ABSENT", "pr=7", run_id=555),
                     D.merge_receipt_body({"merge": None}, 1, 300, {"pr": 7, "head": HEAD, "merge_commit": MERGE_SHA, "main_after": MAIN, "paths": 1}, 555, None, reconciled=True)):
            self.assertEqual(B.executor_run(body), 555, body.split()[0])

    def test_bounded_reads_older_executor_intents_are_closed_by_induction(self):
        # five executor merges over time, each settled by its own receipt; only the NEWEST intent's run is read
        rows, runs = [], {}
        for k in range(5):
            run, at = 500 + k, 600 - 100 * k
            runs[run] = executor_run(run, created=NOW - timedelta(minutes=at + 2))
            rows.append(TB.comment(1000 + 2 * k, INTENT.replace("pr: 7", f"pr: {20 + k}") + "\n" + RUN_LINE.format(run), TB.BOT, at))
            rows.append(TB.comment(1001 + 2 * k, f"S1_LANE_MERGE_v1\npr: {20 + k}\nhead: {HEAD}\n" + RUN_LINE.format(run), TB.BOT, at - 1))
        asked = []
        reader = lambda rid: (asked.append(int(rid)), copy.deepcopy(runs.get(int(rid))))[1]
        self.assertEqual(B.open_intents(rows, NOW, 0, reader), [])
        self.assertEqual(set(asked), {504})                                            # one run, however long the history is
        # a forged settlement of an OLD executor intent changes nothing: that intent is not examined again
        rows[1]["body"] = "S1_OP_DONE_v1\nintent: 1000\nresult: ABSENT"
        self.assertEqual(B.open_intents(rows, NOW, 0, reader), [])
        # when the NEWEST executor intent is not proven it stays open, and the induction starts at the newest PROVEN one
        runs.pop(504)
        asked.clear()
        self.assertEqual([i["id"] for i in B.open_intents(rows, NOW, 0, reader)], [1008])
        self.assertEqual(set(asked), {504, 503})
        # with no proven executor intent at all nothing is closed by induction: every intent needs its own proven outcome
        self.assertEqual([i["id"] for i in B.open_intents(rows, NOW, 0, lambda rid: None)], [1000, 1002, 1004, 1006, 1008])
        self.assertEqual([i["id"] for i in B.open_intents(rows, NOW, 0)], [1000, 1002, 1004, 1006, 1008])
        # an owner post that settles the newest executor intent closes it and every older one
        rows.append(TB.comment(2000, "S1_OP_DONE_v1\nintent: 1008\nresult: OWNER_SETTLED", TB.OWNER, 1))
        self.assertEqual(B.open_intents(rows, NOW, 0, lambda rid: None), [])
        # intents the owner account posted are ALWAYS examined (no induction for them)
        rows.insert(0, TB.comment(900, INTENT.replace("pr: 7", "pr: 19"), TB.OWNER, 700))
        self.assertEqual([i["id"] for i in B.open_intents(rows, NOW, 0, lambda rid: None)], [900])

    def test_the_run_reader_is_memoised_capped_and_reads_a_missing_run_as_none(self):
        class Gh:
            def __init__(self):
                self.calls = []

            def get(self, path, params=None):
                self.calls.append(path)
                if path.endswith("/404"):
                    raise urllib.error.HTTPError(path, 404, "Not Found", {}, None)
                if path.endswith("/500"):
                    raise urllib.error.HTTPError(path, 500, "boom", {}, None)
                return {"id": int(path.rsplit("/", 1)[1])}
        gh = Gh()
        reader = B.RunReader(gh, max_reads=3)
        self.assertEqual((reader(11), reader("11"), reader(11)), ({"id": 11}, {"id": 11}, {"id": 11}))
        self.assertIsNone(reader(404))
        self.assertIsNone(reader(404))
        self.assertEqual(gh.calls, ["actions/runs/11", "actions/runs/404"])            # each run once
        self.assertIsNone(reader(500))                                                 # any HTTP error: not proven, and never an exception
        self.assertIsNone(reader(500))
        self.assertEqual(len(gh.calls), 3)
        self.assertIsNone(reader(13))                                                  # past the cap: not read, so not proven
        self.assertEqual(len(gh.calls), 3)
        self.assertEqual(reader.docs, {"11": {"id": 11}, "404": None, "500": None})
        # a rate limit or the API cap is NOT swallowed: it stops the reads, and the brief that results is incomplete
        class Stopped:
            def get(self, path, params=None):
                raise B.ApiBudget("API_BUDGET_EXHAUSTED")
        with self.assertRaises(B.StopReading):
            B.RunReader(Stopped())(11)
        self.assertEqual(B.SETTLE_RUN_READS, 4)
        # a flood of forged bot posts cannot get one of them believed: past the cap every further post is unproven
        rows = [TB.comment(300, INTENT, TB.OWNER, 30)] + [TB.comment(400 + k, f"S1_OP_DONE_v1\nintent: 300\n" + RUN_LINE.format(900 + k), TB.BOT, 20) for k in range(9)]
        gh2 = Gh()
        self.assertEqual([i["id"] for i in B.open_intents(rows, NOW, 0, B.RunReader(gh2))], [300])
        self.assertEqual(len(gh2.calls), B.SETTLE_RUN_READS)

    def test_the_other_uses_of_a_bot_post_can_only_stop_or_suppress(self):
        # unchanged by fix round 1, pinned here: an UNPROVEN bot post still halts the lane, opens an intent, marks a head
        # as attempted and counts as a merge for the halt trigger. None of these can start a merge.
        halt = TB.comment(61, "S1_LANE_HALTED PR=- head=-\nreason: x", TB.BOT, 5)
        self.assertEqual(B.standing_halt(B.lane_halts([halt]), None), 61)
        self.assertEqual([i["id"] for i in B.open_intents([TB.comment(62, INTENT, TB.BOT, 5)], NOW, 0, lambda rid: None)], [62])
        self.assertEqual(B.attempted_heads([TB.comment(62, INTENT, TB.BOT, 5)]), {(7, HEAD)})
        self.assertEqual(len(B.lane_merges([TB.comment(63, "S1_LANE_MERGE_v1\npr: 7", TB.BOT, 5)])), 1)


class NoSilentFailure(unittest.TestCase):
    """P2-7: the job is continue-on-error (the run must stay green for the brief). So the executor itself must be
    loud: its lines go to the job summary and the process exits non-zero when something went wrong after a write."""

    def test_what_is_an_alarm_and_what_is_not(self):
        refused = urllib.error.HTTPError("u", 405, "Not Allowed", {}, None)
        cases = {
            "a clean merge": (dict(mutate=BEAT), []),
            "a clean shadow run": (dict(mode="SHADOW", mutate=BEAT), []),
            "nothing to do": (dict(mutate=lambda w: (BEAT(w), w.update(pulls=[], pr={}))), []),
            "a heartbeat, then a check that stops the merge": (dict(live=lambda w, gh, n: gh.pull.update(draft=True)), []),
            "a read that stops before any write": (dict(mutate=BEAT, live=lambda w, gh, n: w.update(issue_comments_complete=False)), []),
            "a refused merge": (dict(mutate=BEAT, live=lambda w, gh, n: setattr(gh, "fail_merge", refused)), ["intent_without_outcome(c=7001)"]),
            "a merge call that times out": (dict(mutate=BEAT, live=lambda w, gh, n: setattr(gh, "fail_merge", TimeoutError("t"))), ["intent_without_outcome(c=7001)"]),
            "a readback mismatch": (dict(mutate=BEAT, live=lambda w, gh, n: setattr(n, "ancestor", False)), ["readback_mismatch(not_on_main)"]),
            "anything unexpected, even with no write": (dict(mutate=BEAT, live=lambda w, gh, n: w["pr"][7].update(threads=None)), ["unexpected(RuntimeError)"]),
            "anything unexpected in SHADOW": (dict(mode="SHADOW", mutate=BEAT, live=lambda w, gh, n: w["pr"][7].update(threads=None)), ["unexpected(RuntimeError)"]),
        }
        for name, (kw, want) in cases.items():
            with self.subTest(name):
                out, gh, _n, _d = execute(**kw)
                self.assertEqual(out["alarms"], want)
                alarm_lines = [line for line in out["lines"] if line.startswith("S1_EXECUTOR_ALARM ")]
                self.assertEqual(alarm_lines, ["S1_EXECUTOR_ALARM " + " ".join(want)] if want else [])
                self.assertTrue(out["lines"][-1].startswith("S1_TICK "))               # the tick line stays the last line
                self.assertTrue(out["lines"][-2].startswith("S1_EXECUTOR_V1 "))

    def test_an_intent_followed_by_a_stop_is_an_alarm(self):
        # the clock closes between the intent and the merge call (the Monday window starts): the intent stays open
        run, gh, _n, body, d = setup(mutate=BEAT)
        calls = {"n": 0}

        def clock():
            calls["n"] += 1
            return NOW + timedelta(minutes=2) if not any(w[0] == "comment" for w in run.writes) else datetime(2026, 11, 23, 9, 0, tzinfo=timezone.utc)
        run.now_fn = clock
        out = run.execute(body)
        self.assertEqual(tokens(gh), ["S1_LANE_MERGE_INTENT_v1"])
        self.assertIn("clock:MONDAY_READ_ONLY", out["result"])
        self.assertEqual(out["alarms"], ["intent_without_outcome(c=7001)"])

    def test_a_read_that_stops_after_a_write_is_an_alarm(self):
        def budget(w, gh, n):
            real = gh.pages

            def pages(path, params=None, key=None, max_pages=30):
                if path == "pulls/7/files":
                    raise B.ApiBudget("API_BUDGET_EXHAUSTED")
                return real(path, params, key, max_pages)
            gh.pages = pages
        out, gh, _n, _d = execute(live=budget)                                         # the heartbeat is written first, then the read stops
        self.assertEqual(tokens(gh), ["S1_HEARTBEAT_v1"])
        self.assertTrue(out["result"].startswith("BRIEF_INCOMPLETE(executor:"), out["result"])
        self.assertEqual(len(out["alarms"]), 1)
        self.assertTrue(out["alarms"][0].startswith("read_stopped_after_write("))
        out, gh, _n, _d = execute(mutate=BEAT, live=budget)                            # the same stop with no write before it: no alarm
        self.assertEqual((gh.writes, out["alarms"]), ([], []))

    def test_the_summary_holds_the_lines_as_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "summary.md")
            env = {"GITHUB" + "_STEP_SUMMARY": path}
            self.assertTrue(E.write_summary(env, ["S1_EXECUTOR_V1 mode=SHADOW result=WOULD_MERGE(pr=7)", "S1_TICK NOOP 7 `x` <b>é</b>\x07"]))
            self.assertTrue(E.write_summary(env, ["second run"]))                      # appended, never truncated
            text = Path(path).read_text(encoding="utf-8")
            self.assertEqual(text, "### S1 executor\n\n```text\nS1_EXECUTOR_V1 mode=SHADOW result=WOULD_MERGE(pr=7)\nS1_TICK NOOP 7 'x' <b>?</b>?\n```\n"
                                   "### S1 executor\n\n```text\nsecond run\n```\n")
            self.assertFalse(E.write_summary({}, ["x"]))
            self.assertFalse(E.write_summary({"GITHUB" + "_STEP_SUMMARY": os.path.join(tmp, "no", "such", "dir", "f")}, ["x"]))
        self.assertNotIn("GITHUB" + "_STEP_SUMMARY", SOURCE)                           # the name is assembled (the §0.2e exclusion 11 token list)

    def test_one_line_stays_one_line(self):
        run, gh, _n, body, d = setup()
        seen = []
        run.out = seen.append
        run.say("S1_TICK NOOP - - x\nS1_EXECUTOR_V1 forged\rline\x00")
        self.assertEqual(seen, ["S1_TICK NOOP - - x S1_EXECUTOR_V1 forged line "])

    def test_the_process_exit_code(self):
        class FakeRun:
            def __init__(self, *a, **k):
                pass

            def execute(self, body):
                return FakeRun.out
        with tempfile.TemporaryDirectory() as tmp:
            brief, summary = os.path.join(tmp, "brief.md"), os.path.join(tmp, "summary.md")
            Path(brief).write_text("x", encoding="utf-8")
            env = {"GITHUB_REPOSITORY": B.REPO, "GITHUB" + "_STEP_SUMMARY": summary}
            with mock.patch.object(E, "Run", FakeRun), mock.patch.object(E, "read_files", lambda root: {}), mock.patch.dict(os.environ, env, clear=False):
                FakeRun.out = {"lines": ["S1_EXECUTOR_V1 a", "S1_TICK NOOP a"], "alarms": []}
                self.assertEqual(E.main(["x", "execute", brief]), 0)
                FakeRun.out = {"lines": ["S1_EXECUTOR_ALARM intent_without_outcome(c=1)", "S1_EXECUTOR_V1 b", "S1_TICK NOOP b"], "alarms": ["intent_without_outcome(c=1)"]}
                self.assertEqual(E.main(["x", "execute", brief]), 1)
            text = Path(summary).read_text(encoding="utf-8")
            self.assertIn("S1_TICK NOOP a", text)
            self.assertIn("S1_EXECUTOR_ALARM intent_without_outcome(c=1)", text)
        with self.assertRaises(SystemExit):
            E.main(["x", "nope"])
        self.assertIs(WORKFLOW["jobs"]["execute"]["continue-on-error"], True)          # so that exit 1 is a red JOB, never a failed run


class OneAttemptPerHeadEndToEnd(unittest.TestCase):
    """P3-9: "A 405, a 409 or any other failure is STOP: no retry" is now literally true, over runs as well."""

    def test_a_refused_merge_is_never_tried_again_at_that_head(self):
        self.assertEqual(E.MAX_ATTEMPTS_PER_HEAD, 1)
        w = TD.thin_world("LIVE", "NATIVE_GATES")
        BEAT(w)
        puts = 0
        results = []
        for hour in range(4):
            now = NOW + timedelta(minutes=2)
            brief = B.build_brief(dict(copy.deepcopy(w), executor_runs={"555": executor_run(555, created=NOW - timedelta(minutes=1), status="in_progress")}))
            body, decision = B.render_issue(brief)
            gh, native = FakeGitHub(w, now), FakeNative(w)
            gh.fail_merge = urllib.error.HTTPError("u", 405, "Not Allowed", {}, None)
            gh.next_id = 7000 + 10 * hour
            files = {"switch": w["switch"], "contract": w["contract"], "policy": TB.POLICY, "gate_isolation": "LIVE", "bindings": TB.BINDINGS, "budgets": TB.BUDGETS}
            out = E.Run(gh, native, dict(ENV), files, now_fn=lambda: now, out=lambda line: None).execute(body)
            puts += sum(1 for x in gh.writes if x[0] == "PUT")
            results.append((decision["action"], decision["result"] if decision["action"] == "NOOP" else "-", out["result"], tokens(gh)))
        self.assertEqual(puts, 1)                                                      # ONE merge call, ever, for this head
        self.assertEqual(results[0], ("MERGE", "-", "MERGE_REFUSED(405)", ["S1_LANE_MERGE_INTENT_v1", "MERGE"]))
        # the next run settles the open intent from native state (the PR is still open: ABSENT) and merges nothing
        self.assertEqual(results[1][0], "NOOP")
        self.assertIn("lane:C9:open_merge_intent", results[1][1])
        self.assertEqual(results[1][3], ["S1_OP_DONE_v1"])
        # from then on the decision itself names the head as attempted: the owner's to merge, no further write
        for later in results[2:]:
            self.assertEqual(later, ("NOOP", "NOTHING_ACTIONABLE(skipped=7:C9:attempted_head)", "NOTHING_ACTIONABLE(skipped=7:C9:attempted_head)", []))


class NativeGatesMergesOnlyReviewedCodeOrPlainDocuments(unittest.TestCase):
    """P1-1 end to end: under NATIVE_GATES the executor merges an unreviewed PR only when it changes documents only."""

    def test_a_plain_document_with_no_review_is_merged_under_native_gates_only(self):
        out, gh, _n, d = execute(mutate=lambda w: (BEAT(w), TD.docs_no_review(w)))
        self.assertEqual((d["merge"]["review"], d["merge"]["risk"]), ("NONE(policy=NATIVE_GATES)", "LOW"))
        self.assertTrue(out["result"].startswith("MERGED("), out["result"])
        self.assertIn("review: NONE(policy=NATIVE_GATES)", gh.writes[0][2]["body"].splitlines())
        out, gh, _n, d = execute(policy="CODEX_FINAL_REQUIRED", mutate=lambda w: (BEAT(w), TD.docs_no_review(w)))
        self.assertEqual((d["action"], gh.writes), ("NOOP", []))

    def test_the_live_re_read_applies_the_same_rule(self):
        # the brief saw a plain document; live, the same PR holds code (same count, same hash is impossible, so the file
        # check stops it first) or its review is gone: neither is merged
        docs = lambda w: (BEAT(w), TD.docs_only(w))
        out, gh, _n, d = execute(mutate=docs, live=lambda w, gh, n: w["pr"][7].update(comments=[]))
        self.assertEqual((d["merge"]["review"], gh.writes), ("CODEX", []))
        self.assertIn("7:C8:review_changed", out["result"])                            # a document, still mergeable, but not the decision's review
        out, gh, _n, d = execute(mutate=docs, live=lambda w, gh, n: (w["pr"][7].update(comments=[]), gh.pull["head"].update(ref="codex/x")))
        self.assertIn("7:C5:codex_authored", out["result"])
        out, gh, _n, d = execute(mutate=lambda w: (BEAT(w), TD.docs_no_review(w)), live=lambda w, gh, n: gh.pull.update(user=dict(TB.BOT)))
        self.assertIn("7:C5:bot_authored", out["result"])
        self.assertEqual(gh.writes, [])


# ----------------------------------------------------------------------------------------------- fix round 2
RECALL = D.RECALL_POLICY
FILES = lambda w: {"switch": w["switch"], "contract": w["contract"], "policy": TB.POLICY, "gate_isolation": "LIVE", "bindings": TB.BINDINGS, "budgets": TB.BUDGETS}


def offline_world():
    """PR 7 qualifies, nobody reviewed it, and Codex answered the request for this head with a usage limit."""
    w = TD.thin_world("LIVE", RECALL)
    BEAT(w)
    TD.codex_limit(w)
    return w


def hourly_run(w, run_id, minutes, mode="LIVE", live=None, runs=None):
    """One run of the workflow on the SAME world: a fresh brief at NOW+minutes, then the executor two minutes later."""
    at = NOW + timedelta(minutes=minutes)
    w["now"], w["run"] = B.iso(at), {"id": run_id, "attempt": 1, "event": "schedule"}
    w["switch"]["executor"] = mode
    body, decision = B.render_issue(B.build_brief(dict(copy.deepcopy(w), codex_feed=TD.codex_feed_of(w))))
    now = at + timedelta(minutes=2)
    gh, native = FakeGitHub(w, now), FakeNative(w)
    gh.runs = dict(runs or {})
    gh.runs[run_id] = executor_run(run_id, created=at - timedelta(minutes=1), status="in_progress", updated=now)
    gh.next_id = 7000 + 10 * (run_id - 555)
    if live:
        live(w, gh, native)
    out = E.Run(gh, native, dict(ENV, GITHUB_RUN_ID=str(run_id)), FILES(w), now_fn=lambda: now, out=lambda line: None).execute(body)
    return out, gh, decision


RUN_555 = {555: executor_run(555, created=NOW - timedelta(minutes=1))}             # the first run, as later runs read it: completed at NOW+3


class CodexOfflineFallback(unittest.TestCase):
    """Route (c): never a merge in the run that first saw the PR qualify. A second, independent run must agree."""

    def test_invariant_two_independent_runs_that_agree_then_a_merge_flagged_for_codex(self):
        w = offline_world()
        out, gh, d = hourly_run(w, 555, 0)
        self.assertEqual((d["action"], d["merge"]["review"]), ("MERGE", "FALLBACK(UNAVAILABLE)"))
        self.assertEqual((out["action"], out["result"], tokens(gh)), ("NOOP", f"FALLBACK_CANDIDATE(pr=7,head={HEAD[:8]},n=1,first_run)", ["S1_FALLBACK_CANDIDATE_v1"]))
        candidate = gh.writes[0][2]["body"]
        for line in ("pr: 7", f"head: {HEAD}", "offline: UNAVAILABLE", "candidate_n: 1", "executor: GITHUB run=555"):
            self.assertIn(line, candidate.splitlines())
        evidence = B.fields(candidate)["evidence"]
        self.assertRegex(evidence, r"^[0-9a-f]{32}$")
        # ten minutes later another run agrees, but the first is too young: it waits and writes nothing
        out, gh, _d = hourly_run(w, 556, 10, runs=RUN_555)
        self.assertEqual((out["result"], gh.writes), ("FALLBACK_WAITING(pr=7,age_min=10)", []))
        # an hour after the first run: every gate again, the same hash, the merge, and the recall flag
        out, gh, d = hourly_run(w, 557, 60, runs=RUN_555)
        self.assertEqual((out["action"], out["result"]), ("MERGE", f"MERGED(n=1,main={MERGE_SHA[:8]})"))
        self.assertEqual(tokens(gh), ["S1_LANE_MERGE_INTENT_v1", "MERGE", "S1_LANE_MERGE_v1", "S1_CODEX_RECALL_PENDING_v1", "LABEL+"])
        self.assertEqual(gh.writes[1], ("PUT", "pulls/7/merge", {"merge_method": "squash", "sha": HEAD}))
        self.assertEqual(gh.writes[4], ("POST", "issues/7/labels", {"labels": ["codex-recall-pending"]}))
        self.assertIn("review: FALLBACK(UNAVAILABLE)", gh.writes[2][2]["body"].splitlines())
        recall = gh.writes[3][2]["body"]
        for line in ("pr: 7", f"head: {HEAD}", f"merge: {MERGE_SHA}", "runs: 555,557", "label: codex-recall-pending", "executor: GITHUB run=557"):
            self.assertIn(line, recall.splitlines())
        self.assertEqual(out["alarms"], [])
        self.assertEqual(B.recalls(w["issue_comments"]), [{"c": B.recalls(w["issue_comments"])[0]["c"], "pr": 7, "head": HEAD, "merge": MERGE_SHA, "cleared": False}])
        self.assertEqual(B.fields(candidate)["evidence"], evidence)                    # the second run derived the same hash itself:
        self.assertEqual(sum(1 for kind, path in gh.calls if (kind, path) == ("TEXT", "actions/jobs/1010/logs")), 1)   # it re-read the privacy log, the CI, ...
        self.assertIn(("GRAPHQL", "threads"), gh.calls)

    def test_invariant_a_second_run_that_derives_something_else_parks_the_head(self):
        changes = {
            "the body changed": lambda w: w["pulls"][0].update(body="one more sentence"),
            "a required job ran again (other ids)": lambda w: (w["pr"][7]["runs"][0].update(run_attempt=2), [j.update(run_attempt=2) for j in w["pr"][7]["jobs"][101]]),
        }
        for name, change in changes.items():
            with self.subTest(name):
                w = offline_world()
                hourly_run(w, 555, 0)
                change(w)
                out, gh, d = hourly_run(w, 557, 60, runs=RUN_555)
                self.assertEqual(d["action"], "MERGE")                                 # the brief cannot know yet: the PR still qualifies on its own
                # the run that disagrees merges nothing and puts ITS evidence on the ledger: two different hashes for one head
                self.assertEqual((out["action"], out["result"], tokens(gh)), ("NOOP", f"FALLBACK_MISMATCH(pr=7,head={HEAD[:8]},n=2,mismatch)", ["S1_FALLBACK_CANDIDATE_v1"]))
                hashes = [B.fields(c["body"])["evidence"] for c in B.fallback_candidates(w["issue_comments"])[(7, HEAD)]]
                self.assertEqual((len(hashes), len(set(hashes))), (2, 2))
                # from the next brief on the head is PARKED, with the reason on the owner's first line; no run merges it, however long they agree
                runs = {**RUN_555, 557: executor_run(557, created=NOW + timedelta(minutes=59))}
                for k, minutes in ((559, 120), (560, 180)):
                    out, gh, d = hourly_run(w, k, minutes, runs=runs)
                    self.assertEqual((d["action"], d["skipped"], out["action"], gh.writes), ("NOOP", ["7:C5:fallback_parked:mismatch"], "NOOP", []))
                    self.assertIn(f"#7 {HEAD[:8]} (owner_merge:C5:fallback_parked:mismatch)", d["status_lines"][0])
                # a review (route a) still merges the parked head: the park is for the fallback only
                w["pr"][7]["comments"] = TB.codex_comments()
                out, gh, d = hourly_run(w, 561, 240, runs=runs)
                self.assertEqual((d["merge"]["review"], out["action"]), ("CODEX", "MERGE"))

    def test_each_run_proves_the_offline_signal_for_itself(self):
        # the first run saw Codex's usage-limit answer, the second sees an unanswered request 24 hours old: another signal,
        # the same PR facts. The evidence is about the PR; both runs proved Codex offline on their own.
        w = offline_world()
        out, gh, d = hourly_run(w, 555, 0)
        self.assertEqual(d["merge"]["review"], "FALLBACK(UNAVAILABLE)")
        TD.codex_silent(w)
        out, gh, d = hourly_run(w, 557, 60, runs=RUN_555)
        self.assertEqual((d["merge"]["review"], out["action"]), ("FALLBACK(SILENT)", "MERGE"))
        self.assertIn("review: FALLBACK(SILENT)", gh.writes[2][2]["body"].splitlines())
        self.assertEqual(D.fallback_evidence(7, HEAD, "LOW", 1, "p", "t", "body", [1]), D.fallback_evidence(7, HEAD, "LOW", 1, "p", "t", "body", [1]))
        base = D.fallback_evidence(7, HEAD, "LOW", 1, "p", "t", "body", [1])
        for other in (D.fallback_evidence(8, HEAD, "LOW", 1, "p", "t", "body", [1]), D.fallback_evidence(7, "c" * 40, "LOW", 1, "p", "t", "body", [1]),
                      D.fallback_evidence(7, HEAD, "MEDIUM", 1, "p", "t", "body", [1]), D.fallback_evidence(7, HEAD, "LOW", 2, "p", "t", "body", [1]),
                      D.fallback_evidence(7, HEAD, "LOW", 1, "q", "t", "body", [1]), D.fallback_evidence(7, HEAD, "LOW", 1, "p", "u", "body", [1]),
                      D.fallback_evidence(7, HEAD, "LOW", 1, "p", "t", "body.", [1]), D.fallback_evidence(7, HEAD, "LOW", 1, "p", "t", "body", [2])):
            self.assertNotEqual(base, other)                                           # every PR fact is part of the hash
        # a new commit is a new head: the old candidate is for another head and counts for nothing
        w = offline_world()
        hourly_run(w, 555, 0)
        self.assertEqual(B.fallback_candidates(w["issue_comments"]).get((7, "c" * 40)), None)

    def candidate(self, evidence="E1", minutes_ago=60, run=540, user=None, edited=False, cid=600):
        body = f"S1_FALLBACK_CANDIDATE_v1\npr: 7\nhead: {HEAD}\nevidence: {evidence}\nexecutor: GITHUB run={run}"
        return TB.comment(cid, body, user or TB.BOT, minutes_ago, edited)

    def run_with(self, rows, mode="LIVE", runs=None):
        run, gh, _n, body, d = setup(mutate=lambda w: (BEAT(w), TD.codex_limit(w)), policy=RECALL, mode=mode)
        run.brief, run.decision, run.mode = B.parse_body(body), d, mode
        gh.runs.update(runs if runs is not None else {540: executor_run(540, created=NOW - timedelta(minutes=61))})
        return run, gh, {"candidates": rows, "evidence": "E1", "offline": "UNAVAILABLE"}

    def test_invariant_which_earlier_candidate_counts_as_the_first_run(self):
        ok = self.candidate()
        run, gh, proof = self.run_with([ok])
        self.assertEqual(run.fallback(proof), (ok, None))                              # proven, another run, 62 minutes old, the same hash
        self.assertEqual(gh.writes, [])
        young = self.candidate(minutes_ago=30)
        run, gh, proof = self.run_with([young], runs={540: executor_run(540, created=NOW - timedelta(minutes=31))})
        self.assertEqual((run.fallback(proof), gh.writes), ((None, "FALLBACK_WAITING(pr=7,age_min=32)"), []))
        boundary = self.candidate(minutes_ago=48)                                      # 50 minutes exactly: enough
        run, gh, proof = self.run_with([boundary], runs={540: executor_run(540, created=NOW - timedelta(minutes=49))})
        self.assertEqual(run.fallback(proof)[0], boundary)
        not_first = {
            "a post of another workflow (run not proven)": ([ok], {540: dict(executor_run(540, created=NOW - timedelta(minutes=61)), path=".github/workflows/x.yml")}),
            "a run that does not exist": ([ok], {}),
            "this very run, proven and old enough (not independent)": ([self.candidate(run=555)], {555: executor_run(555, created=NOW - timedelta(minutes=61))}),
            "an edited candidate": ([self.candidate(edited=True)], None),
            "a candidate the owner account posted (not an executor run)": ([self.candidate(user=TB.OWNER)], None),
            "an expired candidate (25 hours)": ([self.candidate(minutes_ago=25 * 60)], {540: executor_run(540, created=NOW - timedelta(minutes=25 * 60 + 1))}),
            "no run line": ([TB.comment(600, f"S1_FALLBACK_CANDIDATE_v1\npr: 7\nhead: {HEAD}\nevidence: E1", TB.BOT, 60)], None),
        }
        for name, (rows, runs) in not_first.items():
            with self.subTest(name):
                run, gh, proof = self.run_with(rows, runs=runs)
                self.assertEqual(run.fallback(proof), (None, f"FALLBACK_CANDIDATE(pr=7,head={HEAD[:8]},n=2,restart)"))
                self.assertEqual(tokens(gh), ["S1_FALLBACK_CANDIDATE_v1"])             # this run becomes a first run; it never merges
        # another hash: the runs DISAGREE. No merge; this run's evidence goes on the ledger as the record of the mismatch
        for rows in ([self.candidate(evidence="E2")], [self.candidate(evidence="")],
                     [self.candidate(cid=600), self.candidate(evidence="E2", minutes_ago=55, cid=601)]):   # the NEWEST candidate decides
            run, gh, proof = self.run_with(rows)
            self.assertEqual(run.fallback(proof), (None, f"FALLBACK_MISMATCH(pr=7,head={HEAD[:8]},n={len(rows) + 1},mismatch)"))
            self.assertEqual(tokens(gh), ["S1_FALLBACK_CANDIDATE_v1"])
            self.assertIn("evidence: E1", gh.writes[0][2]["body"].splitlines())
        run, gh, proof = self.run_with([self.candidate(evidence="E2")], mode="SHADOW")
        self.assertEqual((run.fallback(proof), gh.writes), ((None, f"WOULD_POST_FALLBACK_CANDIDATE(pr=7,head={HEAD[:8]},mismatch)"), []))
        # three candidates and still no merge: PARK, no fourth
        run, gh, proof = self.run_with([self.candidate(cid=600 + k, run=555) for k in range(3)])
        with self.assertRaises(E.Stop) as stop:
            run.fallback(proof)
        self.assertEqual((stop.exception.reason, gh.writes), ("7:C5:fallback_parked:candidates", []))
        # SHADOW says what it would do and writes nothing
        run, gh, proof = self.run_with([], mode="SHADOW")
        self.assertEqual((run.fallback(proof), gh.writes), ((None, f"WOULD_POST_FALLBACK_CANDIDATE(pr=7,head={HEAD[:8]},first_run)"), []))

    def test_invariant_the_offline_signal_is_derived_again_by_the_executor_from_the_whole_repository(self):
        # fix round 3 (P1-A, P3-F): the executor reads Codex's activity in the WHOLE repository itself, not one PR
        def world(offline=TD.codex_out_of_usage):
            w = TD.thin_world("LIVE", RECALL)
            BEAT(w)
            offline(w)
            return w
        out, gh, d = hourly_run(world(), 555, 0)
        self.assertEqual((d["merge"]["review"], tokens(gh)), ("FALLBACK(LIMIT)", ["S1_FALLBACK_CANDIDATE_v1"]))
        self.assertIn("offline: LIMIT", gh.writes[0][2]["body"].splitlines())
        for path in ("issues/comments", "pulls/comments"):
            self.assertEqual(sum(1 for kind, got in gh.calls if (kind, got) == ("PAGES", path)), 1, path)
        elsewhere = lambda body, cid=900: (lambda w, gh, n: w.setdefault("codex_elsewhere", []).append(TB.comment(cid, body, TB.CODEX, 1)))
        live = {
            "Codex spoke again on this PR (the limit answer is no longer its newest activity)": lambda w, gh, n: w["pr"][7]["comments"].append(TB.comment(13, "Codex: on it", TB.CODEX, 1)),
            "Codex completed a review on ANOTHER PR since the build": elsewhere("Codex Review: Didn't find any major issues"),
            "Codex posted an inline comment somewhere since the build": lambda w, gh, n: w["pr"][7].update(inline=[dict(TB.comment(6, "nit", TB.CODEX, 1), commit_id=HEAD, path="a.md")]),
            "the limit answer is gone": lambda w, gh, n: w["pr"][7].update(comments=w["pr"][7]["comments"][:1]),
            "someone asked Codex about this head meanwhile (a pending request is never offline)": lambda w, gh, n: w["pr"][7]["comments"].append(TB.comment(14, "@codex review", minutes_ago=1)),
            "the executor's repository-wide read is incomplete": lambda w, gh, n: w.update(codex_feed_complete=False),
        }
        for name, change in live.items():
            for mode in ("LIVE", "SHADOW"):
                out, gh, d = hourly_run(world(), 555, 0, mode=mode, live=change)
                self.assertEqual((d["merge"]["review"], gh.writes), ("FALLBACK(LIMIT)", []), name)
                self.assertRegex(out["result"], r"7:C5:codex_review_(required|pending)", name)
        # the same for the two signals that rest on the owner's request
        for offline, route in ((TD.codex_limit, "FALLBACK(UNAVAILABLE)"), (TD.codex_silent, "FALLBACK(SILENT)")):
            out, gh, d = hourly_run(world(offline), 555, 0)
            self.assertEqual((d["merge"]["review"], tokens(gh)), (route, ["S1_FALLBACK_CANDIDATE_v1"]))
            out, gh, d = hourly_run(world(offline), 555, 0, live=elsewhere("Codex Review: Didn't find any major issues"))
            self.assertEqual((d["merge"]["review"], gh.writes), (route, []))
            self.assertIn("7:C5:codex_review_required", out["result"])
        # a newer usage-limit answer elsewhere keeps LIMIT and UNAVAILABLE (Codex is still out of usage); for SILENT it is activity
        for offline, route, stops in ((TD.codex_out_of_usage, "FALLBACK(LIMIT)", False), (TD.codex_limit, "FALLBACK(UNAVAILABLE)", False), (TD.codex_silent, "FALLBACK(SILENT)", True)):
            out, gh, d = hourly_run(world(offline), 555, 0, live=elsewhere(TD.LIMIT_TEXT))
            self.assertEqual((d["merge"]["review"], tokens(gh) == []), (route, stops), route)
        # the owner's request was edited after the build: no longer a request that counts
        edited = lambda w, gh, n: w["pr"][7]["comments"][0].update(updated_at=TB.ts(0))
        for offline in (TD.codex_limit, TD.codex_silent):
            out, gh, d = hourly_run(world(offline), 555, 0, live=edited)
            self.assertEqual(gh.writes, [])
            self.assertRegex(out["result"], r"7:C5:codex_review_(required|pending)")   # an edited request is at best a new, pending one
        # a route with a review does not cost the two repository-wide reads
        out, gh, _n, d = execute(policy=RECALL)
        self.assertEqual((d["merge"]["review"], ("PAGES", "issues/comments") in gh.calls), ("CODEX", False))

    def test_invariant_route_c_merges_class_low_only_also_live(self):
        # fix round 3 (P1-B): the brief may be older than the PR's label or class; the executor's own risk decides too
        w = offline_world()
        out, gh, d = hourly_run(w, 555, 0, live=lambda w, gh, n: None)
        self.assertEqual((d["merge"]["risk"], d["merge"]["review"]), ("LOW", "FALLBACK(UNAVAILABLE)"))
        run, gh, _n, body, d = setup(mutate=lambda w: (BEAT(w), TD.codex_limit(w)), policy=RECALL)
        live = {"review": {"codex": {"status": "UNAVAILABLE"}}, "author": {"s1": False, "codex": False},
                "thin": {"bot": False, "claude": "NONE", "claude_written": False, "diff_x": [], "fallback_candidates": 0, "fallback_mismatch": False,
                         "p01_named": False, "codex_offline": "UNAVAILABLE", "risk": "LOW"}}
        self.assertEqual(D.review_route(live, RECALL), ("FALLBACK(UNAVAILABLE)", None))
        self.assertEqual(D.review_route(dict(live, thin=dict(live["thin"], risk="MEDIUM")), RECALL), (None, "C5:fallback_parked:risk"))
        source = (ROOT / "scripts/governance/s1_executor_v1.py").read_text(encoding="utf-8")
        self.assertIn('"risk": risk, "codex_offline": self.codex_offline(n, cx, prc, reviews, inline, now)', source)   # the live facts carry this run's own class

    def test_shadow_never_writes_on_the_fallback_route(self):
        out, gh, d = hourly_run(offline_world(), 555, 0, mode="SHADOW")
        self.assertEqual((d["merge"]["review"], out["result"], gh.writes), ("FALLBACK(UNAVAILABLE)", f"WOULD_POST_FALLBACK_CANDIDATE(pr=7,head={HEAD[:8]},first_run)", []))

    def test_invariant_the_route_is_derived_again_live(self):
        cases = {
            "Codex answered meanwhile (a completed review)": (lambda w, gh, n: w["pr"][7].update(comments=TB.codex_comments()), "7:C8:review_changed"),
            "Codex posted findings meanwhile": (lambda w, gh, n: w["pr"][7].update(comments=[c if i != 1 else dict(c, body="<!-- codex-review-state:v1 " + json.dumps(
                {"code_review": {"commit_sha": HEAD, "status": "completed", "has_unresolved_findings": True}}) + " -->") for i, c in enumerate(TB.codex_comments())]), "7:C5:codex_findings"),
            "a Claude refusal arrived on the PR": (lambda w, gh, n: w["pr"][7]["comments"].append(
                TB.comment(21, TD.CLAUDE_OK.replace("APPROVE", "BLOCK"), TB.OWNER, 1)), "7:C5:claude_veto"),
            "the request was withdrawn (Codex was never asked)": (lambda w, gh, n: w["pr"][7].update(comments=[]), "7:C5:codex_review_required"),
            "the PR turns out to be opened by a bot": (lambda w, gh, n: gh.pull.update(user=dict(TB.BOT)), "7:C5:bot_authored"),
            "the head turns out to be S1's": (lambda w, gh, n: gh.pull["head"].update(ref="s1/x"), "7:C5:s1_authored"),
            "the candidates were used up meanwhile": (lambda w, gh, n: w["issue_comments"].extend(
                TB.comment(600 + k, f"S1_FALLBACK_CANDIDATE_v1\npr: 7\nhead: {HEAD}\nevidence: X\nexecutor: GITHUB run=54{k}", TB.BOT, 5) for k in range(3)), "7:C5:fallback_parked:candidates"),
            "someone wrote P1 in the PR conversation meanwhile": (lambda w, gh, n: w["pr"][7]["comments"].append(
                TB.comment(15, "P1: this places live orders, do not merge", minutes_ago=1)), "7:C5:fallback_parked:p0p1_comment"),
            "a review summary named P0 meanwhile": (lambda w, gh, n: w["pr"][7].update(
                reviews=[{"id": 1, "user": {"login": "someone"}, "state": "COMMENTED", "body": "P0: no", "commit_id": HEAD}]), "7:C5:fallback_parked:p0p1_comment"),
            "two runs disagreed about this head meanwhile": (lambda w, gh, n: w["issue_comments"].extend(
                TB.comment(600 + k, f"S1_FALLBACK_CANDIDATE_v1\npr: 7\nhead: {HEAD}\nevidence: X{k}\nexecutor: GITHUB run=54{k}", TB.BOT, 5) for k in range(2)), "7:C5:fallback_parked:mismatch"),
        }
        for name, (live, reason) in cases.items():
            for mode in ("LIVE", "SHADOW"):
                with self.subTest(name=name, mode=mode):
                    out, gh, d = hourly_run(offline_world(), 555, 0, mode=mode, live=live)
                    self.assertEqual(d["merge"]["review"], "FALLBACK(UNAVAILABLE)")
                    self.assertEqual((out["action"], gh.writes), ("NOOP", []), out["result"])
                    self.assertIn(reason, out["result"])

    def test_a_fallback_merge_that_cannot_be_flagged_is_an_alarm_and_stays_on_the_ledger(self):
        w = offline_world()
        hourly_run(w, 555, 0)
        refuse = lambda w, gh, n: setattr(gh, "fail_label", urllib.error.HTTPError("u", 422, "Unprocessable", {}, None))
        out, gh, _d = hourly_run(w, 557, 60, runs=RUN_555, live=refuse)
        self.assertTrue(out["result"].startswith("MERGED("))
        self.assertEqual(out["alarms"], ["recall_flag_incomplete(HTTPError)"])
        self.assertEqual([r["pr"] for r in B.recalls(w["issue_comments"])], [7])       # the receipts carry the recall without the label

    def test_a_reconciled_fallback_merge_keeps_its_recall(self):
        def intent(w):
            BEAT(w)
            w["issue_comments"].append(TB.comment(300, f"S1_LANE_MERGE_INTENT_v1\npr: 7\nhead: {HEAD}\nmain: {MAIN}\nloop={'4' * 40}\nbrief=500\ndecision=500.1\n"
                                                       "review: FALLBACK(SILENT)\ncontract=44444444", TB.BOT, 30))

        def merged(w, gh, n):
            gh.pull.update(merged=True, state="closed", merged_at=TB.ts(29), merge_commit_sha=MERGE_SHA, merged_by={"login": "github-actions[bot]"})
            w.setdefault("commit_objects", {})[MERGE_SHA] = {"sha": MERGE_SHA, "parents": [{"sha": MAIN}], "commit": {"message": "docs (#7)"}}
        out, gh, _n, _d = execute(mutate=intent, live=merged, policy=RECALL)
        self.assertEqual(out["result"], "RECONCILED(c=300)")
        self.assertIn("review: FALLBACK(SILENT)", gh.writes[0][2]["body"].splitlines())
        self.assertEqual([(r["pr"], r["head"], r["merge"]) for r in B.recalls(gh.w["issue_comments"])], [(7, HEAD, MERGE_SHA)])

    def test_invariant_the_label_writes_are_the_one_label_and_only_after_this_runs_own_merge_or_proof(self):
        run, gh, _n, body, d = setup()
        run.brief, run.decision, run.mode = B.parse_body(body), d, "LIVE"
        for bad, reason in (({"pr": 7, "add": True}, "label_without_merge"), ({"pr": 9, "add": False}, "label_without_clear"),
                            ({"pr": "7", "add": True}, "label_shape"), ({"pr": 7, "add": "yes"}, "label_shape")):
            with self.assertRaises(E.Stop) as stop:
                run.write("label", **bad)
            self.assertEqual(stop.exception.reason, reason)
        self.assertEqual(gh.writes, [])
        run.write("merge", pr=7, sha=HEAD)
        run.write("label", pr=7, add=True)
        with self.assertRaises(E.Stop):                                                # another PR's label: never
            run.write("label", pr=8, add=True)
        run.recall_cleared.add(9)
        run.write("label", pr=9, add=False)
        self.assertEqual([(m, u, b) for m, u, b in gh.writes[1:]], [("POST", "issues/7/labels", {"labels": ["codex-recall-pending"]}),
                                                                      ("DELETE", "issues/9/labels/codex-recall-pending", None)])
        run.mode = "SHADOW"
        with self.assertRaises(E.Stop):
            run.write("label", pr=7, add=True)
        self.assertEqual(E.MAX_WRITES, 8)


class ClaudeReceiptRoute(unittest.TestCase):
    """Route (b): a Claude exact-head APPROVE receipt among the PR's own comments."""

    def test_a_claude_approve_is_a_merge_with_no_recall(self):
        approved = lambda w: (BEAT(w), TD.no_codex(w), TD.claude_receipt()(w))
        out, gh, _n, d = execute(mutate=approved, policy=RECALL)
        self.assertEqual((d["merge"]["review"], out["action"]), ("CLAUDE", "MERGE"))
        self.assertEqual(tokens(gh), ["S1_LANE_MERGE_INTENT_v1", "MERGE", "S1_LANE_MERGE_v1"])           # a review was given: no candidate, no recall, no label
        receipt = gh.writes[2][2]["body"]
        # fix round 3 (P1-C): the receipt records what was accepted, and that nobody checked it against the Bridge
        for line in ("review: CLAUDE", "claude_request: 7165386485", f"report_blob: {'a' * 40}", f"bridge_commit: {'b' * 40}", "claude_receipt: UNVERIFIED", "executor: GITHUB run=555"):
            self.assertIn(line, receipt.splitlines())
        self.assertEqual(B.recalls(gh.w["issue_comments"]), [])
        self.assertEqual(B.unverified_receipts(gh.w["issue_comments"]), [{"c": gh.writes[2][2]["id"] if "id" in gh.writes[2][2] else B.unverified_receipts(gh.w["issue_comments"])[0]["c"],
                                                                         "pr": 7, "head": HEAD, "report_blob": "a" * 40}])
        self.assertTrue(B.build_brief(dict(copy.deepcopy(gh.w), codex_feed=TD.codex_feed_of(gh.w)))["claude_receipts"]["unverified"] == 1)
        live = {
            "the receipt was edited meanwhile": (lambda w, gh, n: w["pr"][7]["comments"][-1].update(updated_at=TB.ts(0)), "7:C5:codex_review_required"),
            "a newer refusal arrived": (lambda w, gh, n: w["pr"][7]["comments"].append(TB.comment(21, TD.CLAUDE_OK.replace("APPROVE", "REQUEST_CHANGES"), TB.OWNER, 1)), "7:C5:claude_veto"),
            "the head turns out to be Claude's own": (lambda w, gh, n: gh.pull["head"].update(ref="claude/x"), "7:C5:claude_authored"),
            "the head turns out to be S1's own": (lambda w, gh, n: gh.pull["head"].update(ref="s1/x"), "7:C5:s1_authored"),
            "the request row is gone": (lambda w, gh, n: w["pr"][7].update(comments=[c for c in w["pr"][7]["comments"] if c["id"] != 7165386485]), "7:C5:codex_review_required"),
            "the request row was edited meanwhile": (lambda w, gh, n: [c.update(updated_at=TB.ts(0)) for c in w["pr"][7]["comments"] if c["id"] == 7165386485], "7:C5:codex_review_required"),
        }
        for name, (change, reason) in live.items():
            out, gh, _n, d = execute(mutate=approved, policy=RECALL, live=change)
            self.assertEqual((d["merge"]["review"], gh.writes), ("CLAUDE", []), name)
            self.assertIn(reason, out["result"], name)


class RecallIsClearedOnlyByCodex(unittest.TestCase):
    PENDING = TD.CodexRecall.PENDING

    def world(self, comments):
        def mutate(w):
            BEAT(w)
            w["issue_comments"].append(TB.comment(700, self.PENDING, TB.BOT, 500))
            w["recall_reads"] = {"9": TD.CodexRecall().read(comments)}
        return mutate

    def final(self):
        state = json.dumps({"code_review": {"commit_sha": "e" * 40, "status": "completed", "has_unresolved_findings": False}})
        return [TB.comment(31, "@codex review", minutes_ago=200), TB.comment(32, f"<!-- codex-review-state:v1 {state} -->", TB.CODEX, 180),
                TB.comment(33, f"Codex Review: Didn't find any major issues\n**Reviewed commit:** `{'e' * 10}`", TB.CODEX, 170)]

    def test_invariant_the_flag_clears_on_codexs_completed_review_read_again_by_the_executor(self):
        out, gh, _n, d = execute(mutate=self.world(self.final()), policy=RECALL)
        self.assertEqual(tokens(gh)[:2], ["S1_CODEX_RECALL_CLEARED_v1", "LABEL-"])     # bookkeeping first, then the run's one action
        self.assertEqual(gh.writes[1][:2], ("DELETE", "issues/9/labels/codex-recall-pending"))
        for line in ("pr: 9", f"head: {'e' * 40}", "codex: FINAL", "executor: GITHUB run=555"):
            self.assertIn(line, gh.writes[0][2]["body"].splitlines())
        self.assertIn("S1_EXECUTOR_RECALL RECALL_CLEARED(pr=9)", out["lines"])
        self.assertEqual([(r["pr"], r["cleared"]) for r in B.recalls(gh.w["issue_comments"])], [(9, True)])   # recorded; it decides nothing
        self.assertEqual(d["recall"], {"pending": 0})                                  # not pending: THIS build read Codex's completed review
        # the next run: the clear receipt is on the ledger, so no second one and no second label call
        again = lambda w: (self.world(self.final())(w), w["issue_comments"].append(TB.comment(702, f"S1_CODEX_RECALL_CLEARED_v1\npr: 9\nhead: {'e' * 40}\ncodex: FINAL", TB.BOT, 30)))
        # ... and when the clear receipt reached the ledger after the brief was built: the executor reads the ledger itself
        late = lambda w, gh, n: w["issue_comments"].append(TB.comment(702, f"S1_CODEX_RECALL_CLEARED_v1\npr: 9\nhead: {'e' * 40}\ncodex: FINAL", TB.BOT, 1))
        out3, gh3, _n, d3 = execute(mutate=self.world(self.final()), policy=RECALL, live=late)
        self.assertEqual([t for t in tokens(gh3) if t in ("S1_CODEX_RECALL_CLEARED_v1", "LABEL-")], [])
        out2, gh2, _n, d2 = execute(mutate=again, policy=RECALL)
        self.assertEqual(([t for t in tokens(gh2) if t in ("S1_CODEX_RECALL_CLEARED_v1", "LABEL-")], d2["recall"], any("S1_EXECUTOR_RECALL" in l for l in out2["lines"])), ([], {"pending": 0}, False))
        self.assertTrue(out["result"].startswith("MERGED("))                           # PR 7 (Codex reviewed) still merges in the same run
        for path in ("issues/9/comments", "pulls/9/reviews", "pulls/9/comments", "pulls/9/commits"):
            self.assertIn(("PAGES", path), gh.calls)                                   # read again, natively, by the executor itself
        out, gh, _n, _d = execute(mode="SHADOW", mutate=self.world(self.final()), policy=RECALL)
        self.assertEqual(gh.writes, [])
        self.assertIn("S1_EXECUTOR_RECALL WOULD_CLEAR_RECALL(pr=9)", out["lines"])

    def test_invariant_nothing_else_clears_it(self):
        asked = self.final()[:1]
        for name, comments in {"not asked": [], "asked, no answer yet": asked}.items():
            out, gh, _n, d = execute(mutate=self.world(comments), policy=RECALL)
            self.assertNotIn("S1_CODEX_RECALL_CLEARED_v1", tokens(gh), name)
            self.assertNotIn("LABEL-", tokens(gh), name)
            self.assertEqual(d["recall"], {"pending": 1})
        # fix round 3 (P2-D): a forged clear receipt (the owner account, or any workflow that may comment) changes nothing.
        # The recall stays pending, it stays in the brief, Codex is still asked, and the label stays on the PR
        for who in (TB.OWNER, TB.BOT):
            forged = lambda w: (self.world([])(w), w["issue_comments"].append(TB.comment(702, f"S1_CODEX_RECALL_CLEARED_v1\npr: 9\nhead: {'e' * 40}\ncodex: FINAL", who, 30)))
            out, gh, _n, d = execute(mutate=forged, policy=RECALL)
            self.assertEqual((d["recall"], "LABEL-" in tokens(gh)), ({"pending": 1}, False))
            self.assertIn({"action": "REQUEST_REVIEW", "pr": 9, "head": "e" * 40, "how": "CODEX_RECALL"}, d["advice"])
            self.assertTrue(d["status_lines"][0].endswith(" ; CODEX_RECALL_PENDING(1): #9"), d["status_lines"][0])
        # the brief saw Codex's review, but the executor's own read does not: no clear
        gone = lambda w, gh, n: w["recall_reads"]["9"].update(comments=[])
        out, gh, _n, _d = execute(mutate=self.world(self.final()), policy=RECALL, live=gone)
        self.assertIn("S1_EXECUTOR_RECALL RECALL_NOT_PROVEN(pr=9,NONE)", out["lines"])
        self.assertNotIn("S1_CODEX_RECALL_CLEARED_v1", tokens(gh))
        self.assertEqual([r["cleared"] for r in B.recalls(gh.w["issue_comments"])], [False])
        # a label that is not on the PR (404) is no alarm; any other refusal is
        for code, alarms in ((404, []), (500, ["recall_label_remove_failed(500)"])):
            fail = lambda w, gh, n: setattr(gh, "fail_label", urllib.error.HTTPError("u", code, "x", {}, None))
            out, gh, _n, _d = execute(mutate=lambda w: (self.world(self.final())(w), w.update(pulls=[], pr={})), policy=RECALL, live=fail)
            self.assertEqual((out["alarms"], [r["cleared"] for r in B.recalls(gh.w["issue_comments"])]), (alarms, [True]))


if __name__ == "__main__":
    unittest.main()
