"""D4 offline cross-module falsifiers. No remote, credentials, or S1 authority."""
from dataclasses import replace
from hashlib import sha256
from itertools import product
import os
import random
import subprocess
import tempfile
import unittest

from scripts.research.s1_branch_update_candidate_v1 import Entry, Hold, Snapshot, propose, verify_readback
from scripts.research.s1_ci_recovery_candidate_v1 import diagnose
from scripts.research.s1_execution_learning_candidate_v1 import Scope, Observation, assess


REPO = 1289482022
HEAD = "7e03fd4b9650c40e658ba566361d9c63c1af15e0"
WORKFLOW = ".github/workflows/data-architecture-gate.yml"
NOW = "2026-11-24T09:00:00Z"
SCOPE = Scope(REPO, 2314, HEAD, WORKFLOW, "gate", "b"*40, "branch_update")


def h(n):
    return f"{n:040x}"


def snapshot(n, entries):
    return Snapshot(h(n), h(n+100), True, entries)


def ci_world(conclusion="success", *, head=HEAD, complete=True, stale=False):
    run = dict(id=45241495015, run_number=5927, run_attempt=1, path=WORKFLOW,
               head_sha=head, event="pull_request", repository={"id": REPO},
               head_repository={"id": REPO}, status="completed", conclusion=conclusion)
    job = dict(id=100, run_id=run["id"], run_attempt=1, head_sha=head, name="gate",
               status="completed", conclusion="success",
               steps=[dict(name="validate", status="completed", conclusion="success")])
    key = (run["id"], 1)
    return dict(head=head, repo_id=REPO, workflow_path=WORKFLOW, job_name="gate",
                must_run_steps=["validate"], runs=[run], runs_complete=complete,
                jobs_by_run={key: [] if conclusion == "action_required" else [job]},
                jobs_complete={key: True}, gate_stale=stale)


def observation(n, scope=SCOPE, outcome="FAILED", cause="synthetic repair failure"):
    return Observation(scope, n, 100+n, 1, sha256(cause.encode()).hexdigest(),
                       f"2026-11-24T08:{n:02d}:00Z", outcome)


def assessment(rows, scope=SCOPE, complete=True):
    return assess(scope, rows, as_of_utc=NOW, history_complete=complete)


def pr_diff(base, head):
    return {p: "added" if p not in base else "removed" if p not in head else "modified"
            for p in base.keys() | head.keys() if base.get(p) != head.get(p)}


def plan_for(b, h_, m, **over):
    kwargs = dict(pr_paths=pr_diff(b.entries, h_.entries), pr_complete=True,
                  native_merge_base=b.commit, current_head=h_.commit, owner_gated=False,
                  writer_clear=True, historical_overlap_clear=True)
    return propose(b, h_, m, **(kwargs | over))


class CrossModuleReplay(unittest.TestCase):
    def setUp(self):
        self.b = snapshot(1, {"a": Entry("100644", h(10)), "ledger": Entry("100644", h(11))})
        self.h = replace(snapshot(2, self.b.entries | {"a": Entry("100755", h(12))}), commit=HEAD)
        self.m = snapshot(3, self.b.entries | {"ledger": Entry("100644", h(13))})

    def test_ci_diagnosis_is_not_attempt_evidence(self):
        # The native #2314 shape has no executed job; it must never count as a failed repair.
        d = diagnose(**ci_world("action_required"))
        self.assertEqual(d.state, "ACTION_REQUIRED_NO_JOBS")
        self.assertIsNone(d.job_id)
        self.assertFalse(d.release_authorized)
        self.assertEqual(assessment([]).state, "NO_ATTEMPT_EVIDENCE")
        self.assertEqual(assessment([], complete=False).state, "EVIDENCE_UNPROVEN")

    def test_stale_gate_does_not_override_writer_or_history(self):
        d = diagnose(**ci_world(stale=True))
        self.assertEqual(d.state, "GATE_STALE")
        for owner, writer, history, complete in product((False, True), repeat=4):
            kw = dict(owner_gated=owner, writer_clear=writer,
                      historical_overlap_clear=history, pr_complete=complete)
            with self.subTest(**kw):
                if not owner and writer and history and complete:
                    self.assertEqual(plan_for(self.b, self.h, self.m, **kw).head, HEAD)
                else:
                    with self.assertRaises(Hold):
                        plan_for(self.b, self.h, self.m, **kw)
                self.assertFalse(d.release_authorized)

    def test_readback_requires_all_gates_and_never_closes(self):
        p = plan_for(self.b, self.h, self.m)
        new = snapshot(4, dict(p.expected))
        args = dict(actual=new, parents=[p.head, p.main], live_head=new.commit, native_main=p.main)
        for kw in (dict(live_head=h(99)), dict(parents=[p.main, p.head]),
                   dict(actual=replace(new, complete=False)),
                   dict(actual=replace(new, entries=new.entries | {"ledger": self.b.entries["ledger"]}))):
            with self.subTest(kw=kw), self.assertRaises(Hold):
                verify_readback(p, **(args | kw))
        self.assertTrue(verify_readback(p, **args))
        d = diagnose(**ci_world(head=new.commit))
        self.assertEqual(d.state, "REQUIRED_JOB_EVIDENCE_PASS")
        self.assertFalse(d.release_authorized)
        a = assessment([observation(1), observation(2, outcome="ACTION_READBACK")])
        self.assertEqual(a.state, "ROUTE_EXISTING_CLOSURE_OWNER")
        self.assertFalse(a.verified_closure)
        self.assertFalse(a.release_authorized)

    def test_cause_and_scope_separation(self):
        # Native run/attempt IDs distinguish observations, but must not form the normalized cause.
        self.assertEqual(assessment([observation(1), observation(2)]).state, "PROCESS_STALLED_CANDIDATE")
        self.assertEqual(assessment([observation(1)]*2).state, "SINGLE_FAILURE_OBSERVED")
        self.assertEqual(assessment([observation(1), observation(2, cause="new cause")]).state,
                         "SINGLE_FAILURE_OBSERVED")
        new = replace(SCOPE, head=h(4))
        self.assertEqual(assessment([observation(1), observation(2)], new).state, "NO_ATTEMPT_EVIDENCE")
        self.assertNotEqual(diagnose(**ci_world()).fingerprint, diagnose(**ci_world(head=new.head)).fingerprint)

    def test_newer_blocked_run_defeats_old_green(self):
        w = ci_world()
        old = w["runs"][0]
        new = dict(old, run_attempt=2, conclusion="action_required")
        w["runs"].append(new)
        w["jobs_by_run"][(old["id"], 2)] = []
        w["jobs_complete"][(old["id"], 2)] = True
        self.assertEqual(diagnose(**w).state, "ACTION_REQUIRED_NO_JOBS")
        w["jobs_complete"][(old["id"], 2)] = False
        self.assertEqual(diagnose(**w).state, "JOBS_UNPROVEN")


class GitDifferentialReplay(unittest.TestCase):
    """Use real local git merge-tree as an independent oracle, never a remote."""
    def test_seeded_tree_comparisons(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                   "GIT_TERMINAL_PROMPT": "0",
                   "GIT_AUTHOR_NAME": "D4", "GIT_AUTHOR_EMAIL": "d4@example.invalid",
                   "GIT_COMMITTER_NAME": "D4", "GIT_COMMITTER_EMAIL": "d4@example.invalid",
                   "GIT_AUTHOR_DATE": "2026-11-24T08:00:00Z", "GIT_COMMITTER_DATE": "2026-11-24T08:00:00Z"})
            def run(*args, data=None, check=True):
                return subprocess.run(["git", *args], cwd=tmp, env=env, input=data,
                                      capture_output=True, check=check, timeout=10)
            run("init", "-q", "--object-format=sha1")
            blobs = [run("hash-object", "-w", "--stdin", data=f"content {i}\n".encode()).stdout.decode().strip()
                     for i in range(8)]
            def tree(entries):
                children = {}
                for p, entry in entries.items():
                    first, sep, rest = p.partition("/")
                    if sep:
                        children.setdefault(first, {})[rest] = entry
                    else:
                        children[first] = entry
                lines = []
                for name, value in sorted(children.items()):
                    mode, kind, oid = ("040000", "tree", tree(value)) if isinstance(value, dict) else (value.mode, "blob", value.sha)
                    lines.append(f"{mode} {kind} {oid}\t{name}\n")
                return run("mktree", data="".join(lines).encode()).stdout.decode().strip()
            def commit(entries, message, parent=None):
                t = tree(entries)
                args = ["commit-tree", t, "-m", message]
                if parent:
                    args.extend(["-p", parent])
                c = run(*args).stdout.decode().strip()
                return Snapshot(c, t, True, entries)
            def entry(i, mode="100644"):
                return Entry(mode, blobs[i])
            rng = random.Random(2411)
            cases = []
            for _ in range(48):
                b = {f"d/f{i}": entry(i) for i in range(4)}
                head, main = b.copy(), b.copy()
                for side in (head, main):
                    for i in rng.sample(range(6), rng.randint(1, 3)):
                        p = f"d/f{i}"
                        if rng.randrange(3) == 0:
                            side.pop(p, None)
                        else:
                            side[p] = entry(rng.randrange(4, 8), rng.choice(("100644", "100755")))
                cases.append((b, head, main))
            b = {"d/a": entry(0), "d/b": entry(1)}
            moved = {"e/a": entry(0), "e/b": entry(1)}
            added = b | {"d/new": entry(2)}
            cases.extend([(b, moved, added), (b, added, moved)])
            accepted = held = unsafe = 0
            for i, (b, h_, m) in enumerate(cases):
                bs = commit(b, f"base {i}")
                hs = commit(h_, f"head {i}", bs.commit)
                ms = commit(m, f"main {i}", bs.commit)
                native = run("merge-tree", "--write-tree", hs.commit, ms.commit, check=False)
                with self.subTest(i=i):
                    self.assertIn(native.returncode, (0, 1), native.stderr)
                    try:
                        p = plan_for(bs, hs, ms)
                    except Hold:
                        held += 1
                        continue
                    accepted += 1
                    if native.returncode != 0 or tree(dict(p.expected)) != native.stdout.decode().splitlines()[0]:
                        unsafe += 1
                    self.assertEqual(native.returncode, 0, native.stdout)
                    self.assertEqual(tree(dict(p.expected)), native.stdout.decode().splitlines()[0])
            self.assertEqual(accepted + held, 50)
            self.assertGreater(accepted, 0)
            self.assertGreater(held, 0)
            self.assertEqual(unsafe, 0)
            print(f"D4 git oracle: accepted={accepted} held={held} unsafe={unsafe}")


if __name__ == "__main__":
    unittest.main()
