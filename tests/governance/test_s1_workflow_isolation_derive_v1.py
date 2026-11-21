"""The live S1 workflow isolation derivation (scripts/governance/s1_workflow_isolation_derive_v1.py).

The six path lists are no longer enumerated in the pinned 00_FMOS/S1_WORKFLOW_ISOLATION_V1.json. They are derived at
the PR head and at main, and lane eligibility uses the union. These tests prove:
- the Archive #2188 case: a PR that adds a test file which a secret job runs needs no edit of the pinned file, and the
  new file is still OWNER_GATED (on a synthetic tree and on the real tree);
- union strictness: a head that deletes the edge that makes a file secret-run does not un-list that file;
- a writer-run path is HIGH at least, an unresolved dynamic edge is OWNER_GATED;
- fail closed: an unparsable workflow, a missing workflow directory or a derivation without the path lists raises;
- the caches are per tree, and the derivation never imports or executes a file of the tree it analyses;
- the CLI.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.governance import s1_workflow_isolation_derive_v1 as derivation
from tests.governance import test_s1_workflow_isolation_v1 as iso

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "governance" / "s1_workflow_isolation_derive_v1.py"
SECRET_ENV = {"TOKEN": "${{ " + "secrets" + ".PUBLISH }}"}
READ_ONLY = {"contents": "read"}


def workflow(jobs, on=("schedule",)):
    return yaml.safe_dump({"name": "w", "on": {k: None for k in on}, "jobs": jobs}, sort_keys=False)


def base_files():
    """main: a secret job runs every test under tests/pub (one imports scripts/pub/helper.py), a writer job runs a
    build script, and a read-only job without a secret runs a plain script."""
    return {
        ".github/workflows/w.yml": workflow({
            "pub": {"runs-on": "ubuntu-latest", "permissions": READ_ONLY,
                    "steps": [{"run": "python -m pytest tests/pub -q", "env": SECRET_ENV}]},
            "build": {"runs-on": "ubuntu-latest", "permissions": {"contents": "write"},
                      "steps": [{"run": "python scripts/build/build.py --config config/build/targets.json"}]},
            "plain": {"runs-on": "ubuntu-latest", "permissions": READ_ONLY,
                      "steps": [{"run": "python scripts/plain/report.py"}]}}),
        "tests/pub/test_a.py": "from scripts.pub import helper\n\n\ndef test_a():\n    assert helper.VALUE == 1\n",
        "scripts/pub/helper.py": "VALUE = 1\n",
        "scripts/build/build.py": "import json\n",
        "scripts/plain/report.py": "print('report')\n",
    }


class TreeCase(unittest.TestCase):
    def tree(self, files):
        root = Path(tempfile.mkdtemp(prefix="s1iso_"))
        self.addCleanup(shutil.rmtree, root, True)
        for rel, text in files.items():
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root

    @staticmethod
    def pinned_file(derived):
        """The pinned job-level file that matches a derivation (what main carries)."""
        return {"contract": "S1_WORKFLOW_ISOLATION_V1", "rule": "fixture",
                **{k: v for k, v in derived.items() if k not in derivation.PATH_LIST_KEYS}}


class Regression2188Test(TreeCase):
    NEW = "tests/pub/test_new_case.py"

    def test_new_secret_run_test_file_needs_no_edit_of_the_pinned_file(self):
        main = self.tree(base_files())
        head = self.tree(base_files() | {self.NEW: "def test_new():\n    assert True\n"})
        d_main, d_head = derivation.derive(main), derivation.derive(head)
        pinned = self.pinned_file(d_main)                        # main's file; the PR does not touch it
        self.assertNotIn(self.NEW, d_main["secret_job_executed_paths"])
        self.assertIn(self.NEW, d_head["secret_job_executed_paths"])
        # the equality rule of test_isolation_file_equals_the_derivation passes at the head with the file unchanged
        self.assertEqual(iso.file_mismatches(pinned, d_head), [])
        self.assertFalse(set(pinned) & set(derivation.PATH_LIST_KEYS))
        # and the new file is still lane-excluded
        self.assertEqual(derivation.lane_classification([self.NEW, "docs/note.md"], [d_main, d_head]),
                         {"owner_gated": [self.NEW], "high_floor": []})

    def test_a_job_level_change_still_fails_the_equality_rule(self):
        # Not weaker for what the file still carries: a new secret job, or a path list put back, is a mismatch.
        main = self.tree(base_files())
        files = base_files()
        doc = yaml.safe_load(files[".github/workflows/w.yml"])
        doc["jobs"]["plain"]["steps"][0]["env"] = SECRET_ENV
        head = self.tree(files | {".github/workflows/w.yml": yaml.safe_dump(doc, sort_keys=False)})
        d_main, d_head = derivation.derive(main), derivation.derive(head)
        pinned = self.pinned_file(d_main)
        self.assertEqual(iso.file_mismatches(pinned, d_main), [])
        self.assertEqual(iso.file_mismatches(pinned, d_head), ["secret_jobs"])
        self.assertEqual(iso.file_mismatches(pinned | {"secret_job_executed_paths": []}, d_main), ["secret_job_executed_paths"])
        self.assertEqual(iso.file_mismatches({k: v for k, v in pinned.items() if k != "action_refs"}, d_main), ["action_refs"])

    def test_on_the_real_tree(self):
        """A copy of the real tree (the workflows and every code file: all the derivation reads) plus one new test
        file in a directory that a secret job runs; the real pinned file is not edited."""
        real = iso.real_tree_derivation()
        tree = derivation.Tree(ROOT)
        target = None
        for name, _, doc in tree.workflows():
            for job in (doc.get("jobs") or {}).values():
                if not derivation.receives_secret(doc, job):
                    continue
                for token in derivation.sp._TOKEN.findall(json.dumps(job.get("steps") or [], default=str).replace("\\n", "\n")):
                    token = token.rstrip("./")
                    if target is None and token.startswith("tests/") and (ROOT / token).is_dir():
                        target = token
        if target is None:
            self.skipTest("no secret job names a test directory any more")
        new = f"{target}/test_zz_s1_isolation_2188_regression.py"
        self.assertFalse((ROOT / new).exists())
        head = Path(tempfile.mkdtemp(prefix="s1iso_real_"))
        self.addCleanup(shutil.rmtree, head, True)
        for folder, dirs, names in os.walk(ROOT):
            dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
            rel = Path(folder).relative_to(ROOT)
            for name in names:
                if rel.parts[:1] == (".github",) or name.endswith(derivation.sp._CODE_SUFFIXES):
                    (head / rel).mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(Path(folder) / name, head / rel / name)
        (head / new).write_text("def test_new():\n    assert True\n", encoding="utf-8")
        d_head = derivation.derive(head)
        self.assertEqual(d_head["secret_job_executed_paths"], sorted(set(real["secret_job_executed_paths"]) | {new}))
        self.assertEqual({k: v for k, v in d_head.items() if k != "secret_job_executed_paths"},
                         {k: v for k, v in real.items() if k != "secret_job_executed_paths"})
        pinned = json.loads(iso.ISOLATION.read_text(encoding="utf-8"))
        self.assertEqual(iso.file_mismatches(pinned, d_head), [])       # CI at the head passes, the file is unchanged
        self.assertEqual(derivation.lane_classification([new], [real, d_head]), {"owner_gated": [new], "high_floor": []})
        # the frozen debt checks see the same live lists at the head
        self.assertLessEqual(set(d_head["unresolved_edge_paths"]), iso.FROZEN_UNRESOLVED_EDGE_DEBT)
        self.assertLessEqual(set(d_head["writer_unresolved_edge_paths"]), iso.FROZEN_WRITER_UNRESOLVED_EDGE_DEBT)


class LaneClassificationTest(TreeCase):
    def test_union_a_head_that_deletes_the_import_edge_does_not_unlist_the_file(self):
        helper = "scripts/pub/helper.py"
        main = self.tree(base_files())
        head = self.tree(base_files() | {"tests/pub/test_a.py": "def test_a():\n    assert True\n",
                                         helper: "VALUE = 2  # changed by the PR\n"})
        d_main, d_head = derivation.derive(main), derivation.derive(head)
        self.assertIn(helper, d_main["secret_job_executed_paths"])
        self.assertNotIn(helper, d_head["secret_job_executed_paths"])
        self.assertEqual(derivation.lane_classification([helper], [d_head]), {"owner_gated": [], "high_floor": []})
        for both in ([d_main, d_head], [d_head, d_main]):
            self.assertEqual(derivation.lane_classification([helper, "tests/pub/test_a.py"], both),
                             {"owner_gated": [helper, "tests/pub/test_a.py"], "high_floor": []})

    def test_union_a_head_that_moves_a_secret_run_file_to_a_writer_job_stays_owner_gated(self):
        d_main = derivation.derive(self.tree(base_files()))
        files = base_files()
        files[".github/workflows/w.yml"] = files[".github/workflows/w.yml"].replace(
            "python scripts/build/build.py", "python scripts/build/build.py && python scripts/pub/helper.py")
        files["tests/pub/test_a.py"] = "def test_a():\n    assert True\n"
        d_head = derivation.derive(self.tree(files))
        self.assertIn("scripts/pub/helper.py", d_head["writer_job_executed_paths"])
        self.assertEqual(derivation.lane_classification(["scripts/pub/helper.py"], [d_main, d_head]),
                         {"owner_gated": ["scripts/pub/helper.py"], "high_floor": []})

    def test_writer_run_path_and_writer_named_file_are_high_floor(self):
        d = derivation.derive(self.tree(base_files()))
        self.assertEqual(d["writer_job_executed_paths"], ["scripts/build/build.py"])
        self.assertEqual(d["writer_job_named_files"], ["config/build/targets.json"])
        self.assertEqual(derivation.lane_classification(
            ["./scripts/build/build.py", "config/build/targets.json\n", "scripts/plain/report.py", ""], [d, d]),
            {"owner_gated": [], "high_floor": ["config/build/targets.json", "scripts/build/build.py"]})

    def test_unresolved_dynamic_edge_is_owner_gated(self):
        files = base_files() | {
            "tests/pub/test_a.py": "import importlib\nimport sys\n\nMOD = importlib.import_module(sys.argv[1])\n",
            "scripts/build/build.py": "import subprocess\nimport sys\n\nsubprocess.run(sys.argv[1:])\n"}
        d = derivation.derive(self.tree(files))
        self.assertEqual(d["unresolved_edge_paths"], ["tests/pub/test_a.py"])
        self.assertEqual(d["writer_unresolved_edge_paths"], ["scripts/build/build.py"])
        self.assertEqual(derivation.lane_classification(["tests/pub/test_a.py", "scripts/build/build.py"], [d]),
                         {"owner_gated": ["tests/pub/test_a.py"], "high_floor": ["scripts/build/build.py"]})
        # each key decides alone: a path that only the unresolved lists name
        empty = {k: [] for k in derivation.PATH_LIST_KEYS}
        self.assertEqual(derivation.lane_classification(["x.py"], [empty, empty | {"unresolved_edge_paths": ["x.py"]}]),
                         {"owner_gated": ["x.py"], "high_floor": []})
        self.assertEqual(derivation.lane_classification(["x.json"], [empty | {"secret_job_named_files": ["x.json"]}, empty]),
                         {"owner_gated": ["x.json"], "high_floor": []})
        self.assertEqual(derivation.lane_classification(["x.py"], [empty | {"writer_unresolved_edge_paths": ["x.py"]}]),
                         {"owner_gated": [], "high_floor": ["x.py"]})
        self.assertEqual(derivation.lane_classification(
            ["x.py"], [empty | {"writer_job_executed_paths": ["x.py"]}, empty | {"unresolved_edge_paths": ["x.py"]}]),
            {"owner_gated": ["x.py"], "high_floor": []})

    def test_a_python_file_that_does_not_parse_is_an_unresolved_edge(self):
        d = derivation.derive(self.tree(base_files() | {"tests/pub/test_a.py": "def broken(:\n"}))
        self.assertEqual(d["unresolved_edge_paths"], ["tests/pub/test_a.py"])
        self.assertFalse(set(d["unresolved_edge_paths"]) <= iso.FROZEN_UNRESOLVED_EDGE_DEBT)   # so CI fails at the head

    def test_keys(self):
        self.assertEqual(set(derivation.PATH_LIST_KEYS), set(derivation.OWNER_GATED_KEYS) | set(derivation.HIGH_FLOOR_KEYS))
        self.assertEqual(len(derivation.PATH_LIST_KEYS), 6)
        self.assertFalse(set(derivation.OWNER_GATED_KEYS) & set(derivation.HIGH_FLOOR_KEYS))
        self.assertLessEqual(set(derivation.PATH_LIST_KEYS), set(derivation.derive(self.tree(base_files()))))
        self.assertEqual(iso.LOWER_BOUND_KEYS, ())
        self.assertIs(iso.PATH_LIST_KEYS, derivation.PATH_LIST_KEYS)


class FailClosedTest(TreeCase):
    def test_unparsable_workflow_yaml_raises(self):
        root = self.tree(base_files() | {".github/workflows/broken.yml": "jobs:\n  a: [unclosed\n   b: {\n"})
        with self.assertRaisesRegex(derivation.DerivationError, r"unparsable workflow \.github/workflows/broken\.yml"):
            derivation.derive(root)

    def test_workflow_that_is_not_a_mapping_of_jobs_raises(self):
        for text in ("- a\n- b\n", "jobs: [a, b]\n", "jobs:\n  a: just-a-string\n", "\xff\xfe"):
            root = self.tree(base_files())
            (root / ".github/workflows/odd.yml").write_bytes(text.encode("latin-1"))
            with self.subTest(text=text), self.assertRaises(derivation.DerivationError):
                derivation.derive(root)

    def test_missing_workflow_directory_raises(self):
        root = self.tree({"scripts/pub/helper.py": "VALUE = 1\n"})
        with self.assertRaisesRegex(derivation.DerivationError, "no workflow directory"):
            derivation.derive(root)
        with self.assertRaises(derivation.DerivationError):
            derivation.derive(root / "does-not-exist")

    def test_classification_needs_real_derivations(self):
        d = derivation.derive(self.tree(base_files()))
        with self.assertRaises(derivation.DerivationError):
            derivation.lane_classification(["a.py"], [])
        with self.assertRaisesRegex(derivation.DerivationError, "pinned isolation file"):
            derivation.lane_classification(["a.py"], [d, self.pinned_file(d)])     # the file has no path lists
        with self.assertRaises(derivation.DerivationError):
            derivation.lane_classification(["a.py"], [d, None])


class PerTreeCacheTest(TreeCase):
    def test_two_roots_with_the_same_paths_do_not_share_a_cache(self):
        a = self.tree(base_files())
        b = self.tree(base_files() | {"tests/pub/test_a.py": "from scripts.pub import other\n",
                                      "scripts/pub/other.py": "VALUE = 3\n"})
        d_a1, d_b, d_a2 = derivation.derive(a), derivation.derive(b), derivation.derive(a)
        self.assertEqual(d_a1["secret_job_executed_paths"], ["scripts/pub/helper.py", "tests/pub/test_a.py"])
        self.assertEqual(d_b["secret_job_executed_paths"], ["scripts/pub/other.py", "tests/pub/test_a.py"])
        self.assertEqual(d_a1, d_a2)
        # interleaved Tree objects, same relative path, different content
        t_a, t_b = derivation.Tree(a), derivation.Tree(b)
        self.assertEqual(t_a.import_edges("tests/pub/test_a.py"), {"scripts/pub/helper.py"})
        self.assertEqual(t_b.import_edges("tests/pub/test_a.py"), {"scripts/pub/other.py"})
        self.assertEqual(t_a.import_edges("tests/pub/test_a.py"), {"scripts/pub/helper.py"})

    def test_a_changed_tree_is_read_again(self):
        root = self.tree(base_files())
        before = derivation.derive(root)
        (root / "tests/pub/test_more.py").write_text("def test_more():\n    assert True\n", encoding="utf-8")
        after = derivation.derive(root)
        self.assertNotIn("tests/pub/test_more.py", before["secret_job_executed_paths"])
        self.assertIn("tests/pub/test_more.py", after["secret_job_executed_paths"])

    def test_the_test_module_derive_follows_its_root(self):
        root = self.tree(base_files())
        self.assertEqual(iso.derive(root), derivation.derive(root))
        saved = (iso.ROOT, iso.WF)
        iso.ROOT, iso.WF = root, root / ".github" / "workflows"          # what IsolationFixture and repin.py do
        try:
            self.assertEqual(iso.derive(), derivation.derive(root))
            self.assertEqual([name for name, _, _ in iso.workflows()], ["w.yml"])
        finally:
            iso.ROOT, iso.WF = saved


class NeverExecutesTheTreeTest(TreeCase):
    def test_tree_code_is_parsed_never_imported_or_run(self):
        marker = Path(tempfile.mkdtemp(prefix="s1iso_marker_"))
        self.addCleanup(shutil.rmtree, marker, True)
        bomb = f"from pathlib import Path\nPath({str(marker / 'ran')!r}).write_text('x')\n"
        root = self.tree(base_files() | {"tests/pub/test_a.py": bomb + "import yaml\nimport json\nimport scripts.pub.helper\n",
                                         "scripts/pub/helper.py": bomb, "yaml.py": bomb, "json.py": bomb, "ast.py": bomb,
                                         "scripts/governance/s1_standing_policy_v1.py": bomb,
                                         "tests/pub/conftest.py": bomb, "sitecustomize.py": bomb})
        d = derivation.derive(root)
        self.assertIn("scripts/pub/helper.py", d["secret_job_executed_paths"])
        result = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), "--json"], capture_output=True, text=True,
                                cwd=marker, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), d)
        self.assertEqual(list(marker.iterdir()), [])


class CliTest(TreeCase):
    def run_cli(self, *args):
        scratch = Path(tempfile.mkdtemp(prefix="s1iso_cwd_"))
        self.addCleanup(shutil.rmtree, scratch, True)
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, cwd=scratch, timeout=120)

    def test_derivation_output(self):
        root = self.tree(base_files())
        result = self.run_cli("--root", root, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), derivation.derive(root))
        summary = self.run_cli("--root", root)
        self.assertEqual(summary.returncode, 0, summary.stderr)
        self.assertIn("secret_job_executed_paths: 2", summary.stdout)
        self.assertIn("gate_isolation: NOT_LIVE", summary.stdout)

    def test_classification_output_is_the_union_of_base_and_head(self):
        main = self.tree(base_files())
        head = self.tree(base_files() | {"tests/pub/test_a.py": "def test_a():\n    assert True\n",
                                         "tests/pub/test_new_case.py": "def test_new():\n    assert True\n"})
        changed = head / "changed.txt"
        changed.write_text("tests/pub/test_new_case.py\nscripts/pub/helper.py\nscripts/build/build.py\ndocs/x.md\n", encoding="utf-8")
        result = self.run_cli("--root", head, "--base-root", main, "--changed", changed)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"owner_gated": ["scripts/pub/helper.py", "tests/pub/test_new_case.py"],
                                                     "high_floor": ["scripts/build/build.py"]})

    def test_fails_closed_with_a_reason(self):
        main = self.tree(base_files())
        broken = self.tree(base_files() | {".github/workflows/broken.yml": "jobs:\n  a: [unclosed\n   b: {\n"})
        changed = main / "changed.txt"
        changed.write_text("scripts/pub/helper.py\n", encoding="utf-8")
        cases = {"unparsable head": ("--root", broken, "--json"),
                 "unparsable base": ("--root", main, "--base-root", broken, "--changed", changed),
                 "unparsable head in a classification": ("--root", broken, "--base-root", main, "--changed", changed),
                 "no base root": ("--root", main, "--changed", changed),
                 "no changed file": ("--root", main, "--base-root", main, "--changed", main / "absent.txt"),
                 "no tree": ("--root", main / "absent", "--json")}
        for label, args in cases.items():
            result = self.run_cli(*args)
            with self.subTest(label):
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertIn("DERIVATION_FAILED", result.stderr)
        self.assertIn("unparsable workflow .github/workflows/broken.yml", self.run_cli("--root", broken).stderr)


if __name__ == "__main__":
    unittest.main()
