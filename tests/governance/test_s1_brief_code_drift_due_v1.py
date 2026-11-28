"""code_drift_due: a push that brought code since the published brief makes a new brief due at once."""
import json, sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "governance"))
import s1_tick_brief_v1 as B

A, H = "a" * 40, "b" * 40
BOT = dict(B.ACTIONS_BOT)


def issue(main=A, user=None):
    doc = {"main": main}
    body = f"{B.BEGIN}\n```json\n{json.dumps(doc)}\n```\n{B.END}\n"
    return {"user": user or BOT, "body": body}


class CodeDriftDue(unittest.TestCase):
    def setUp(self):
        self.real_parse = B.parse_body
        B.parse_body = lambda body: json.loads(body.split("```json\n", 1)[1].split("\n```", 1)[0])

    def tearDown(self):
        B.parse_body = self.real_parse

    def due(self, files, status="ahead", issues=None, head=H, commits=2, raises=False):
        def drift(base, h):
            self.assertEqual((base, h), (A, head))
            if raises:
                raise OSError("boom")
            return status, [f["filename"] for f in files] if files is not None else None
        return B.code_drift_due([issue()] if issues is None else issues, drift, head)

    def test_data_only_drift_is_not_due(self):
        self.assertFalse(self.due([{"filename": "research/framework_memory/x.json"}, {"filename": "data/a.csv"}]))

    def test_code_paths_are_due(self):
        for p in ("scripts/data_terminal/fred_csv_collector.py", "tests/data_terminal/test_x.py", "AGENTS.md",
                  ".github/workflows/x.yml", "00_FMOS/S1/TICK.md", "research/s1_root_v2/ledger_screen.py",
                  "05_CYCLE_NAVIGATOR/site/build-public.mjs", "a/b/requirements-dev.txt", "07_PROMPTS_AND_AGENTS/p.md",
                  "01_CORE_FRAMEWORK/governance/rule.md", "x/setup.cfg", "tests/fixtures/case.json"):
            with self.subTest(p):
                self.assertTrue(self.due([{"filename": "data/a.json"}, {"filename": p}]))

    def test_rename_from_code_path_is_due(self):
        # git diff --no-renames lists a rename as delete + add: both paths are classified
        self.assertTrue(self.due([{"filename": "data/a.txt"}, {"filename": "scripts/a.py"}]))

    def test_unreadable_or_large_compare_is_due(self):
        self.assertTrue(self.due([], raises=True))
        self.assertTrue(self.due(None))
        self.assertTrue(self.due([{"filename": "d/x.json"}], status="unknown"))
        self.assertTrue(self.due([{"filename": None}]))
        self.assertTrue(self.due([{"filename": "d/x.json"}] * B.DRIFT_MAX_FILES))   # T3's cap: unreadable drift
        self.assertFalse(self.due([{"filename": "d/x.json"}] * (B.DRIFT_MAX_FILES - 1)))
        self.assertTrue(self.due([{"filename": "d/x.json"}], status="too_large"))

    def test_newer_brief_already_covers_push(self):
        self.assertFalse(self.due([{"filename": "scripts/a.py"}], status="behind"))

    def test_no_or_foreign_brief_leaves_it_to_the_old_rule(self):
        def boom(base, head):
            raise AssertionError("must not compare")
        self.assertFalse(B.code_drift_due([], boom, H))
        self.assertFalse(B.code_drift_due([issue(), issue()], boom, H))
        self.assertFalse(B.code_drift_due([issue(user={"login": "Donh91", "type": "User", "id": 1})], boom, H))
        self.assertFalse(B.code_drift_due([issue(main=H)], boom, H))
        self.assertFalse(B.code_drift_due([issue()], boom, "not-a-sha"))
        self.assertFalse(B.code_drift_due(None, boom, H))

    def test_every_lane_pin_is_a_code_path(self):
        lane = json.loads((ROOT / "00_FMOS" / "S1" / "REVIEWED_MERGE_LANE.json").read_text())
        for pin in lane["pins"]:
            with self.subTest(pin):
                self.assertTrue(B.code_drift_path(pin) or B.code_drift_path(pin + "/x.md"))

    def test_no_rest_compare_and_unchanged_api_budget(self):
        src = (ROOT / "scripts" / "governance" / "s1_tick_brief_v1.py").read_text()
        self.assertNotIn('gh.get(f"compare/', src)
        self.assertEqual(B.DUE_API_CALLS, 5)


class GitDrift(unittest.TestCase):
    """git_drift against a real local repository (a bare 'origin' and a clone)."""
    def test_relations_and_paths(self):
        import subprocess, tempfile
        def run(*a, cwd):
            return subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()
        with tempfile.TemporaryDirectory() as t:
            t = Path(t); work = t / "w"; work.mkdir()
            run("init", "-q", "-b", "main", cwd=work)
            run("config", "user.email", "t@t", cwd=work); run("config", "user.name", "t", cwd=work)
            run("config", "uploadpack.allowFilter", "true", cwd=work); run("config", "uploadpack.allowAnySHA1InWant", "true", cwd=work)
            (work / "data").mkdir(); (work / "data/a.json").write_text("1")
            run("add", "-A", cwd=work); run("commit", "-qm", "a", cwd=work); a = run("rev-parse", "HEAD", cwd=work)
            (work / "data/a.json").write_text("2"); run("commit", "-qam", "b", cwd=work); b = run("rev-parse", "HEAD", cwd=work)
            (work / "scripts").mkdir(); (work / "scripts/x.py").write_text("x")
            run("add", "-A", cwd=work); run("commit", "-qm", "c", cwd=work); c = run("rev-parse", "HEAD", cwd=work)
            run("checkout", "-q", "-b", "side", a, cwd=work); (work / "data/a.json").write_text("side")
            run("commit", "-qam", "d", cwd=work); d = run("rev-parse", "HEAD", cwd=work); run("checkout", "-q", "main", cwd=work)
            clone = t / "c"; run("clone", "-q", "--no-checkout", "file://" + str(work), str(clone), cwd=t)
            B.GIT_ENV = None
            self.assertEqual(B.git_drift(clone, a, b), ("ahead", ["data/a.json"]))
            rel, paths = B.git_drift(clone, a, c)
            self.assertEqual((rel, sorted(paths)), ("ahead", ["data/a.json", "scripts/x.py"]))
            self.assertEqual(B.git_drift(clone, c, a)[0], "behind")
            self.assertEqual(B.git_drift(clone, a, "f" * 40), ("unknown", None))
            self.assertEqual(B.git_drift(clone, d, c), ("unknown", None))   # diverged: neither is an ancestor
            saved = B.DRIFT_MAX_COMMITS; B.DRIFT_MAX_COMMITS = 1
            try:
                self.assertEqual(B.git_drift(clone, a, c), ("too_large", None))   # 2 commits > cap 1
            finally:
                B.DRIFT_MAX_COMMITS = saved


class DueReachability(unittest.TestCase):
    """main('due') on a push reaches D1 even when a cron run of the last hour exists (detached review F1)."""
    def run_due(self, runs, drift_result, event="push"):
        import io, contextlib, os
        brief = issue()
        class FakeGH:
            def __init__(self, *a, **k): self.calls = 0
            def get(self, path, params=None):
                self.calls += 1
                if path.startswith("actions/workflows/"): return {"workflow_runs": runs}
                if path == "issues": return [brief]
                raise AssertionError(path)
        saved = (B.GitHub, B.git_drift, B.parse_body, dict(os.environ))
        B.GitHub = FakeGH
        B.git_drift = lambda root, base, head: drift_result
        B.parse_body = lambda body: json.loads(body.split("```json\n", 1)[1].split("\n```", 1)[0])
        os.environ.update({"GITHUB_EVENT_NAME": event, "GITHUB_SHA": H, "GITHUB_RUN_ID": "999", "GITHUB_REPOSITORY": B.REPO})
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                B.main(["x", "due"])
        finally:
            B.GitHub, B.git_drift, B.parse_body = saved[:3]
            os.environ.clear(); os.environ.update(saved[3])
        return out.getvalue().strip()

    def fresh_cron(self):
        from datetime import datetime, timedelta, timezone
        t = (datetime.now(timezone.utc) - timedelta(minutes=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
        return [{"id": 1, "event": "schedule", "created_at": t, "updated_at": t, "status": "completed"}]

    def test_code_push_after_a_fresh_cron_is_due(self):
        self.assertEqual(self.run_due(self.fresh_cron(), ("ahead", ["scripts/governance/x.py"])), "true")

    def test_data_push_after_a_fresh_cron_is_not_due(self):
        self.assertEqual(self.run_due(self.fresh_cron(), ("ahead", ["data/a.json"])), "false")

    def test_workflow_run_event_never_uses_d1(self):
        self.assertEqual(self.run_due(self.fresh_cron(), ("ahead", ["scripts/x.py"]), event="workflow_run"), "false")

    def test_checkout_root_is_the_script_checkout(self):
        self.assertEqual(B.CHECKOUT_ROOT, ROOT)


class DueWiring(unittest.TestCase):
    def test_push_only_and_after_fallback(self):
        src = (ROOT / "scripts" / "governance" / "s1_tick_brief_v1.py").read_text()
        block = src.split('if mode == "due":', 1)[1].split('if mode == "build":', 1)[0]
        self.assertIn('if not due and os.environ.get("GITHUB_EVENT_NAME") == "push":', block)
        self.assertLess(block.index("fallback_due("), block.index("code_drift_due("))
        self.assertIn("git_drift(CHECKOUT_ROOT, base, head)", block)
        self.assertIn('GITHUB_SHA', block)


if __name__ == "__main__":
    unittest.main()
