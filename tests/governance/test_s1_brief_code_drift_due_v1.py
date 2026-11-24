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
        self.assertFalse(self.due([{"filename": "d/x.json"}] * 5000))   # no file cap: git lists every path

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


class DueWiring(unittest.TestCase):
    def test_push_only_and_after_fallback(self):
        src = (ROOT / "scripts" / "governance" / "s1_tick_brief_v1.py").read_text()
        block = src.split('if mode == "due":', 1)[1].split('if mode == "build":', 1)[0]
        self.assertIn('if not due and os.environ.get("GITHUB_EVENT_NAME") == "push":', block)
        self.assertLess(block.index("fallback_due("), block.index("code_drift_due("))
        self.assertIn('GITHUB_SHA', block)


if __name__ == "__main__":
    unittest.main()
