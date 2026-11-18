"""Tests for S1_SITE_PUBLIC_READBACK_V1: readback of the generated public site bundle (fix 4).

Three layers: the trusted readback over a staged fixture bundle, the untrusted build half over a throwaway git
repository with a small Pages-shaped workflow, and the native privacy step consuming a readback for a site-only PR.
Restricted markers and key shapes are assembled at runtime so that this file itself stays scanner-clean.
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from scripts.governance import s1_diff_scan_v1 as scanner
from scripts.governance import s1_native_privacy_scan_step_v1 as step
from scripts.governance import s1_site_public_readback_v1 as rb
from tests.governance.test_s1_native_privacy_scan_step_v1 import Fixture, git

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "governance" / "s1_site_public_readback_v1.py"
PAGES = (ROOT / rb.PAGES_WORKFLOW).read_bytes()
HEAD = "a" * 40
OTHER = "b" * 40
MARKER = "OWNER" + "_" + "ONLY"
API_KEY = "gh" + "p_" + "A1b2C3d4E5f6G7h8I9j0K1l2"
KEY_BLOCK = "-----BEGIN " + "PRIVATE KEY-----"
SITE = scanner.SITE_PUBLIC_PREFIX
NEEDS = "GENERATED_PUBLIC_OUTPUT_NEEDS_SEPARATE_READBACK"
CLEAN_SITE = {"index.html": "<!doctype html><title>Cycle Navigator</title>\n",
              "app.js": "console.log('public');\n",
              "data/latest.json": json.dumps({"issue_number": 35, "status": "PUBLIC"}) + "\n",
              "favicon.svg": "<svg xmlns='http://www.w3.org/2000/svg'/>\n",
              "manifest.webmanifest": "{\"name\": \"Cycle Navigator\"}\n"}
PNG = b"\x89PNG\r\n\x1a\n" + bytes(range(256))


def repo_with_recipe(tmp, workflow=PAGES):
    repo = Path(tmp) / "checkout"
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / rb.PAGES_WORKFLOW).write_bytes(workflow)
    return str(repo)


def stage(tmp, files, head=HEAD, name="staged", workflow=PAGES, **receipt):
    """A staged bundle as the build job uploads it: dist/ plus the build receipt."""
    out = Path(tmp) / name
    for rel, data in files.items():
        p = out / rb.STAGED_DIST / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data if isinstance(data, bytes) else data.encode("utf-8"))
    (out / rb.STAGED_DIST).mkdir(parents=True, exist_ok=True)
    doc = {"contract": rb.RECEIPT_CONTRACT, "status": "BUILT", "head_sha": head, "merge_sha": None,
           "run_id": "1", "run_attempt": "1", "file_count": len(files),
           "publish_root": rb.parse_pages_recipe(workflow.decode("utf-8"))["publish_root"],
           "pages_workflow_blob_sha": rb.git_blob_sha(workflow)}
    doc.update(receipt)
    (out / rb.RECEIPT_NAME).write_text(json.dumps(doc), encoding="utf-8")
    return str(out)


def reasons(out):
    return sorted(out["findings_by_rule"])


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="s1sitereadback-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = repo_with_recipe(self.tmp)

    def read(self, staged, head=HEAD, **kw):
        kw.setdefault("run_id", "1")
        kw.setdefault("run_attempt", "1")
        return rb.readback(staged, head, repo=self.repo, **kw)


class ReadbackOfStagedBundle(Base):
    def test_clean_site_is_public_output_clean(self):
        out = self.read(stage(self.tmp, CLEAN_SITE))
        self.assertEqual((out["result"], out["findings"], out["findings_by_rule"]), ("PUBLIC_OUTPUT_CLEAN", [], {}), out)
        self.assertEqual((out["contract"], out["head"], out["publish_root"]),
                         ("S1_SITE_PUBLIC_READBACK_V1", HEAD, "05_CYCLE_NAVIGATOR/site/dist"))
        self.assertEqual(out["file_count"], len(CLEAN_SITE))
        self.assertEqual(out["text_files_scanned"], len(CLEAN_SITE))
        self.assertEqual(out["total_bytes"], sum(len(v.encode()) for v in CLEAN_SITE.values()))
        self.assertEqual(out["rules_version"], scanner.RULES_VERSION)
        self.assertIs(out["executes_pr_code"], False)
        self.assertRegex(out["manifest_sha256"], r"^[0-9a-f]{64}$")

    def test_manifest_digest_is_deterministic_and_byte_sensitive(self):
        a = self.read(stage(self.tmp, CLEAN_SITE, name="a"))
        b = self.read(stage(self.tmp, dict(reversed(list(CLEAN_SITE.items()))), name="b"))
        self.assertEqual(a["manifest_sha256"], b["manifest_sha256"])
        rows = [(p, __import__("hashlib").sha256(v.encode()).hexdigest()) for p, v in CLEAN_SITE.items()]
        self.assertEqual(a["manifest_sha256"], rb.manifest_sha256(rows))
        self.assertEqual(a["manifest_sha256"], rb.manifest_sha256(list(reversed(rows))))
        changed = dict(CLEAN_SITE, **{"app.js": "console.log('public!');\n"})
        self.assertNotEqual(a["manifest_sha256"], self.read(stage(self.tmp, changed, name="c"))["manifest_sha256"])
        renamed = {("app2.js" if k == "app.js" else k): v for k, v in CLEAN_SITE.items()}
        self.assertNotEqual(a["manifest_sha256"], self.read(stage(self.tmp, renamed, name="d"))["manifest_sha256"])

    def test_restricted_content_in_any_generated_file_is_found_and_not_echoed(self):
        cases = {"EXPLICIT_PRIVATE_DESIGN": f"{{\"note\": \"{MARKER} design\"}}\n",
                 "API_KEY_LITERAL": f"const k = '{API_KEY}';\n",
                 "PRIVATE_KEY_BLOCK": KEY_BLOCK + "\nabc\n",
                 "CREDENTIAL_ASSIGNMENT": "api" + "_key = 'abcdefghijklmnopqrstuvwxyz0123'\n"}
        for index, (rule, text) in enumerate(cases.items()):
            with self.subTest(rule=rule):
                files = dict(CLEAN_SITE, **{"data/deep/generated-secret-carrier.json": text})
                out = self.read(stage(self.tmp, files, name=f"r{index}"))
                self.assertEqual(out["result"], "RESTRICTED_CONTENT", out)
                self.assertIn(rule, out["findings_by_rule"])
                dumped = json.dumps(out)
                for secret in (MARKER, API_KEY, KEY_BLOCK, "generated-secret-carrier"):
                    self.assertNotIn(secret, dumped)
                self.assertEqual({f["path_sha256_16"] for f in out["findings"]},
                                 {rb._path_ref("data/deep/generated-secret-carrier.json")})

    def test_restricted_file_name_is_a_finding(self):
        out = self.read(stage(self.tmp, dict(CLEAN_SITE, **{f"data/{MARKER}.json": "{}\n"})))
        self.assertEqual((out["result"], reasons(out)), ("RESTRICTED_CONTENT", ["EXPLICIT_PRIVATE_DESIGN_IN_FILENAME"]))

    def test_every_rule_of_the_scanner_table_is_applied_not_a_copy(self):
        self.assertEqual([(n, p.pattern, p.flags) for n, p in rb.scanner.KNOWN_SECRET_OR_RESTRICTED_DESIGN],
                         [(n, p.pattern, p.flags) for n, p in scanner.KNOWN_SECRET_OR_RESTRICTED_DESIGN])
        self.assertEqual(Path(rb.scanner.__file__).resolve(), Path(scanner.__file__).resolve())
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("re.compile(r\"-----BEGIN", source)
        fake = (("FIXTURE_RULE", __import__("re").compile("zzfixturezz")),)
        self.assertNotIn("re.compile(r\"(?", source)
        with mock.patch.object(rb.scanner, "KNOWN_SECRET_OR_RESTRICTED_DESIGN", fake):
            out = self.read(stage(self.tmp, dict(CLEAN_SITE, **{"x.css": "a{}/*zzfixturezz*/\n"})))
        self.assertEqual((out["result"], reasons(out)), ("RESTRICTED_CONTENT", ["FIXTURE_RULE"]))

    def test_readback_for_another_head_or_run_or_recipe_is_unknown(self):
        cases = [
            (dict(head=OTHER), {}, "BUILD_RECEIPT_FOR_ANOTHER_HEAD"),
            (dict(run_id="2"), {}, "BUILD_RECEIPT_NOT_FROM_THIS_RUN"),
            (dict(run_attempt="2"), {}, "BUILD_RECEIPT_NOT_FROM_THIS_RUN"),
            ({}, dict(run_id=None), "BUILD_RECEIPT_NOT_FROM_THIS_RUN"),
            ({}, dict(run_attempt=""), "BUILD_RECEIPT_NOT_FROM_THIS_RUN"),
            (dict(merge_sha=OTHER), dict(merge_sha=HEAD), "BUILD_RECEIPT_FOR_ANOTHER_CHECKOUT"),
            (dict(publish_root="05_CYCLE_NAVIGATOR/site"), {}, "BUILD_RECEIPT_FOR_ANOTHER_RECIPE"),
            (dict(pages_workflow_blob_sha="0" * 40), {}, "BUILD_RECEIPT_FOR_ANOTHER_RECIPE"),
            (dict(status="FAILED"), {}, "BUILD_RECEIPT_MISSING_OR_UNPARSABLE"),
            (dict(contract="OTHER"), {}, "BUILD_RECEIPT_MISSING_OR_UNPARSABLE"),
            (dict(file_count=len(CLEAN_SITE) + 1), {}, "FILE_COUNT_MISMATCH_WITH_RECEIPT"),
        ]
        for index, (receipt, kw, reason) in enumerate(cases):
            with self.subTest(reason=reason, receipt=receipt, kw=kw):
                out = self.read(stage(self.tmp, CLEAN_SITE, name=f"s{index}", **receipt), **kw)
                self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", [reason]), out)

    def test_missing_or_unparsable_input_is_unknown(self):
        self.assertEqual(reasons(self.read(None)), ["READBACK_INPUT_ABSENT"])
        self.assertEqual(reasons(self.read("")), ["READBACK_INPUT_ABSENT"])
        self.assertEqual(reasons(self.read(os.path.join(self.tmp, "nope"))), ["READBACK_INPUT_ABSENT"])
        self.assertEqual(reasons(self.read(stage(self.tmp, CLEAN_SITE, name="h"), head="not-a-sha")), ["HEAD_SHA_INVALID"])
        staged = stage(self.tmp, CLEAN_SITE, name="i")
        os.symlink(staged, os.path.join(self.tmp, "link"))
        self.assertEqual(reasons(self.read(os.path.join(self.tmp, "link"))), ["READBACK_INPUT_ABSENT"])
        for index, text in enumerate(["", "{", "[]", "x" * (rb.MAX_RECEIPT_BYTES + 1)]):
            staged = stage(self.tmp, CLEAN_SITE, name=f"j{index}")
            Path(staged, rb.RECEIPT_NAME).write_text(text, encoding="utf-8")
            out = self.read(staged)
            self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["BUILD_RECEIPT_MISSING_OR_UNPARSABLE"]))
        staged = stage(self.tmp, CLEAN_SITE, name="k")
        os.remove(os.path.join(staged, rb.RECEIPT_NAME))
        self.assertEqual(reasons(self.read(staged)), ["BUILD_RECEIPT_MISSING_OR_UNPARSABLE"])
        staged = stage(self.tmp, CLEAN_SITE, name="l")
        Path(staged, "extra.txt").write_text("x", encoding="utf-8")
        self.assertEqual(reasons(self.read(staged)), ["UNEXPECTED_STAGED_ENTRY"])
        self.assertEqual(reasons(self.read(stage(self.tmp, {}, name="m"))), ["EMPTY_PUBLIC_OUTPUT"])
        for r in rb.RESULTS:
            self.assertIn(r, ("PUBLIC_OUTPUT_CLEAN", "RESTRICTED_CONTENT", "UNKNOWN"))

    def test_recipe_that_cannot_be_reproduced_is_unknown(self):
        broken = PAGES.replace(b"          path: 05_CYCLE_NAVIGATOR/site/dist\n",
                               b"          path: 05_CYCLE_NAVIGATOR/site/dist\n          include-hidden-files: true\n")
        self.assertNotEqual(broken, PAGES)
        staged = stage(self.tmp, CLEAN_SITE)
        out = rb.readback(staged, HEAD, repo=repo_with_recipe(os.path.join(self.tmp, "x"), broken), run_id="1", run_attempt="1")
        self.assertEqual(out["result"], "UNKNOWN")
        self.assertEqual(reasons(out), ["PUBLISH_RECIPE_NOT_REPRODUCIBLE_UPLOAD_STEP_HAS_OPTIONS_THAT_CHANGE_THE_PUBLISHED_SET"])
        out = rb.readback(staged, HEAD, repo=os.path.join(self.tmp, "no-such-checkout"), run_id="1", run_attempt="1")
        self.assertEqual(reasons(out), ["PUBLISH_RECIPE_NOT_REPRODUCIBLE_WORKFLOW_FILE_UNAVAILABLE"])

    def test_binary_file_is_accepted_only_when_pinned_for_that_path(self):
        files = dict(CLEAN_SITE, **{"icon.png": PNG})
        sha = __import__("hashlib").sha256(PNG).hexdigest()
        out = self.read(stage(self.tmp, files, name="b0"), pinned={"icon.png": frozenset({sha})})
        self.assertEqual((out["result"], out["binary_files_pinned"]), ("PUBLIC_OUTPUT_CLEAN", 1), out)
        # strict rule: a changed, new, moved or unpinned binary cannot be scanned, so it is UNKNOWN
        for index, (name, data, pins) in enumerate([
                ("icon.png", PNG + b"\x00changed", {"icon.png": frozenset({sha})}),
                ("icon.png", PNG, {}),
                ("other/icon.png", PNG, {"icon.png": frozenset({sha})}),
                ("blob.bin", b"plain ascii in an unknown file type\n", {}),
                ("font.woff2", b"\x00\x01\x02", {})]):
            with self.subTest(name=name, index=index):
                out = self.read(stage(self.tmp, dict(CLEAN_SITE, **{name: data}), name=f"b{index + 1}"), pinned=pins)
                self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["BINARY_PUBLISHED_FILE_NOT_PINNED"]), out)
        # the shipped table pins exactly the two images the real site publishes
        self.assertEqual(sorted(rb.PINNED_BINARY_SHA256), ["apple-touch-icon.png", "social-card.png"])
        icon = (ROOT / SITE / "apple-touch-icon.png").read_bytes()
        self.assertIn(__import__("hashlib").sha256(icon).hexdigest(), rb.PINNED_BINARY_SHA256["apple-touch-icon.png"])

    def test_undecodable_or_nul_text_is_unknown(self):
        for index, data in enumerate([b"\xff\xfe not utf-8\n", b"var a = 1;\x00\n"]):
            out = self.read(stage(self.tmp, dict(CLEAN_SITE, **{"bad.js": data}), name=f"u{index}"))
            self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["PUBLISHED_TEXT_NOT_UTF8"]), out)

    def test_symlink_hidden_entry_special_file_and_path_escape_are_unknown(self):
        secret = Path(self.tmp, "outside-secret.json")
        secret.write_text("{\"public\": false}\n", encoding="utf-8")

        def case(name, mutate):
            staged = stage(self.tmp, CLEAN_SITE, name=name)
            mutate(Path(staged, rb.STAGED_DIST))
            return self.read(staged)

        out = case("y0", lambda d: os.symlink(secret, d / "data" / "leak.json"))        # leaves the publish root
        self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["SYMLINK_IN_PUBLIC_OUTPUT"]), out)
        out = case("y1", lambda d: os.symlink("app.js", d / "alias.js"))                 # inside the root: still no
        self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["SYMLINK_IN_PUBLIC_OUTPUT"]), out)
        out = case("y2", lambda d: os.symlink(self.tmp, d / "tree"))                     # directory symlink
        self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["SYMLINK_IN_PUBLIC_OUTPUT"]), out)
        out = case("y3", lambda d: (d / ".env.json").write_text("{}\n", encoding="utf-8"))
        self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["HIDDEN_ENTRY_NOT_IN_PAGES_SET"]), out)
        out = case("y4", lambda d: (d / ".cache").mkdir())
        self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["HIDDEN_ENTRY_NOT_IN_PAGES_SET"]), out)
        out = case("y5", lambda d: os.mkfifo(d / "pipe.json"))
        self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["UNEXPECTED_FILE_TYPE"]), out)
        out = case("y6", lambda d: (d / "bad\\name.js").write_text("x\n", encoding="utf-8"))
        self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["INVALID_PATH"]), out)
        staged = stage(self.tmp, CLEAN_SITE, name="y7")                                  # the bundle itself is a symlink
        shutil.move(os.path.join(staged, rb.STAGED_DIST), os.path.join(self.tmp, "elsewhere"))
        os.symlink(os.path.join(self.tmp, "elsewhere"), os.path.join(staged, rb.STAGED_DIST))
        out = self.read(staged)
        self.assertEqual(out["result"], "UNKNOWN")
        self.assertIn("PUBLISH_ROOT_NOT_A_DIRECTORY", reasons(out))
        # a resolved path outside the root is reported even if the symlink test were ever bypassed
        staged = stage(self.tmp, CLEAN_SITE, name="y8")
        real = os.path.realpath
        with mock.patch.object(rb.os.path, "realpath", lambda p: "/elsewhere/app.js" if str(p).endswith("app.js") else real(p)):
            out = self.read(staged)
        self.assertEqual(out["result"], "UNKNOWN")
        self.assertIn("PATH_ESCAPES_PUBLISH_ROOT", reasons(out))

    def test_oversize_file_bundle_or_file_count_is_unknown(self):
        staged = stage(self.tmp, dict(CLEAN_SITE, **{"big.json": "[" + "1," * 400 + "1]\n"}))
        with mock.patch.object(rb, "MAX_FILE_BYTES", 256):
            out = self.read(staged)
        self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["PUBLISHED_FILE_EXCEEDS_SAFE_SIZE"]), out)
        self.assertIsNone(out["manifest_sha256"], "no manifest digest for a bundle that was not read completely")
        with mock.patch.object(rb, "MAX_TOTAL_BYTES", 256):
            out = self.read(staged)
        self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["PUBLIC_OUTPUT_EXCEEDS_SAFE_SIZE"]), out)
        with mock.patch.object(rb, "MAX_FILES", 3):
            out = self.read(staged)
        self.assertEqual(out["result"], "UNKNOWN")
        self.assertIn("TOO_MANY_FILES", reasons(out))
        self.assertEqual(self.read(staged)["result"], "PUBLIC_OUTPUT_CLEAN")

    def test_enumeration_error_is_unknown_and_the_cli_exits_non_zero(self):
        staged = stage(self.tmp, CLEAN_SITE)
        with mock.patch.object(rb, "enumerate_tree", side_effect=OSError("boom")):
            out = self.read(staged)
            self.assertEqual((out["result"], reasons(out)), ("UNKNOWN", ["ENUMERATION_ERROR"]), out)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = rb.main(["scan", "--staged", staged, "--head", HEAD, "--repo", self.repo],
                               env={"GITHUB_RUN_ID": "1", "GITHUB_RUN_ATTEMPT": "1"})
            self.assertEqual((code, json.loads(buf.getvalue())["result"]), (1, "UNKNOWN"))

    def test_cli_scan_exits_zero_only_for_clean_and_runs_isolated(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GITHUB_", "S1_"))}
        env.update({"GITHUB_RUN_ID": "1", "GITHUB_RUN_ATTEMPT": "1"})
        for name, files, want in (("c0", CLEAN_SITE, (0, "PUBLIC_OUTPUT_CLEAN")),
                                  ("c1", dict(CLEAN_SITE, **{"n.txt": MARKER + "\n"}), (1, "RESTRICTED_CONTENT")),
                                  ("c2", dict(CLEAN_SITE, **{"n.bin": b"\x00"}), (1, "UNKNOWN"))):
            p = subprocess.run([sys.executable, "-I", str(SCRIPT), "scan", "--staged", stage(self.tmp, files, name=name),
                                "--head", HEAD, "--repo", self.repo], capture_output=True, text=True, env=env)
            self.assertEqual((p.returncode, json.loads(p.stdout)["result"]), want, p.stdout + p.stderr)
            self.assertNotIn(MARKER, p.stdout + p.stderr)
            self.assertNotIn("S1_NATIVE_PRIVACY_SCAN_STEP_V1", p.stdout + p.stderr)
        p = subprocess.run([sys.executable, "-I", str(SCRIPT)], capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 2)


class PagesRecipe(unittest.TestCase):
    """The publication recipe is read from the Pages workflow; it is not a second hand-kept list."""

    def setUp(self):
        self.text = PAGES.decode("utf-8")
        self.recipe = rb.parse_pages_recipe(self.text)

    def test_recipe_equals_the_yaml_reading_of_the_real_pages_workflow(self):
        doc = yaml.safe_load(self.text)
        self.assertEqual(list(doc["jobs"]), ["deploy"])
        steps = doc["jobs"]["deploy"]["steps"]
        upload = [i for i, s in enumerate(steps) if str(s.get("uses", "")).startswith("actions/upload-pages-artifact")]
        self.assertEqual(len(upload), 1)
        self.assertEqual(steps[upload[0]]["uses"], rb.UPLOAD_ACTION)
        self.assertEqual(steps[upload[0]]["with"], {"path": self.recipe["publish_root"]})
        self.assertEqual(self.recipe["publish_root"], "05_CYCLE_NAVIGATOR/site/dist")
        before = steps[:upload[0]]
        want = [{"name": s.get("name", ""), "run": s["run"] if s["run"].endswith("\n") else s["run"] + "\n",
                 "id": s.get("id"), "continue_on_error": s.get("continue-on-error") is True,
                 "only_if_failed": "graph_history" if "if" in s else None} for s in before if "run" in s]
        self.assertEqual(self.recipe["steps"], want)
        self.assertEqual([s["if"] for s in before if "if" in s], ["steps.graph_history.outcome == 'failure'"])
        self.assertEqual(sorted({s["uses"] for s in before if "uses" in s}), sorted(rb.SETUP_ACTIONS))
        self.assertGreaterEqual(len(want), 20)
        # the published directory is generated: no tracked file lives in it, so "the site" is never a static upload
        tracked = git(ROOT, "ls-files", "--", self.recipe["publish_root"])
        self.assertEqual(tracked, "")

    def test_any_construct_the_reader_does_not_reproduce_fails_closed(self):
        t = self.text
        mutations = {
            "env on a build step": t.replace("      - name: Validate public product contract\n",
                                             "      - name: Validate public product contract\n        env:\n          A: b\n"),
            "shell on a build step": t.replace("      - name: Validate public product contract\n",
                                               "      - name: Validate public product contract\n        shell: sh\n"),
            "working-directory": t.replace("      - name: Validate public product contract\n",
                                           "      - name: Validate public product contract\n        working-directory: x\n"),
            "expression in a command": t.replace("run: node 05_CYCLE_NAVIGATOR/site/validate-v2.mjs",
                                                 "run: node ${{ github.workspace }}/x.mjs"),
            "another if form": t.replace("if: steps.graph_history.outcome == 'failure'", "if: always()"),
            "if on an unknown step": t.replace("if: steps.graph_history.outcome == 'failure'",
                                               "if: steps.nope.outcome == 'failure'"),
            "unknown action before upload": t.replace("        uses: actions/configure-pages@v5", "        uses: evil/action@v1"),
            "other upload action version": t.replace(rb.UPLOAD_ACTION, "actions/upload-pages-artifact@v3"),
            "upload option that changes the set": t.replace("          path: 05_CYCLE_NAVIGATOR/site/dist\n",
                                                            "          path: 05_CYCLE_NAVIGATOR/site/dist\n          include-hidden-files: true\n"),
            "unsafe publish root": t.replace("          path: 05_CYCLE_NAVIGATOR/site/dist\n", "          path: ../outside\n"),
            "private publish root": t.replace("          path: 05_CYCLE_NAVIGATOR/site/dist\n", "          path: private/site\n"),
            "second job": t.replace("jobs:\n  deploy:", "jobs:\n  other:\n    runs-on: x\n  deploy:"),
            "tab": t.replace("      - name: Checkout", "      - name:\tCheckout"),
            "no upload step": t[:t.index("      - name: Upload Cycle Navigator public bundle only")],
            "not text": None,
        }
        for name, mutated in mutations.items():
            with self.subTest(name=name):
                self.assertNotEqual(mutated, t)
                with self.assertRaises(rb.RecipeError):
                    rb.parse_pages_recipe(mutated)


WORKFLOW_FIXTURE = """name: Fixture Pages
on:
  push:
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v6
        with:
          ref: main
      - uses: actions/setup-node@v4
        with: {node-version: '22'}
      - name: Build
        run: |
          mkdir -p site/dist/data
          cp site/index.html site/dist/index.html
          cp site/app.js site/dist/app.js
__EXTRA__      - name: Optional step that may fail
        id: optional
        continue-on-error: true
        run: test -f site/optional-input.json
      - name: Fallback only after the optional step failed
        if: steps.optional.outcome == 'failure'
        run: printf '{"optional":"UNAVAILABLE"}\\n' > site/dist/data/optional.json
      - name: Upload
        uses: actions/upload-pages-artifact@v4
        with:
          path: site/dist
      - name: Deploy
        env:
          X: ${{ github.sha }}
        run: echo never-run-by-the-readback > site/dist/after-upload.txt
"""


class UntrustedBuildHalf(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="s1sitebuild-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.out = os.path.join(self.tmp, "staged")
        self.env = {"GITHUB_RUN_ID": "1", "GITHUB_RUN_ATTEMPT": "1"}

    def repo(self, extra="", files=None):
        repo = Path(self.tmp) / "repo"
        repo.mkdir()
        git(repo, "init", "-q", "-b", "main")
        tree = {rb.PAGES_WORKFLOW: WORKFLOW_FIXTURE.replace("__EXTRA__", extra),
                "site/index.html": "<!doctype html>\n", "site/app.js": "console.log(1);\n",
                "internal/notes.json": json.dumps({"note": MARKER + " design"}) + "\n"}
        tree.update(files or {})
        for rel, text in tree.items():
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            (repo / rel).write_text(text, encoding="utf-8")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "tree")
        return str(repo), git(repo, "rev-parse", "HEAD")

    def step(self, name, command):
        return f"      - name: {name}\n        run: {command}\n"

    def test_build_stages_the_published_set_and_the_readback_accepts_it(self):
        repo, head = self.repo()
        receipt = rb.run_build(repo, self.out, head, self.env)
        self.assertEqual((receipt["status"], receipt["file_count"], receipt["publish_root"]), ("BUILT", 3, "site/dist"))
        self.assertEqual(receipt["step_outcomes"], {"optional": "failure"})
        self.assertEqual(sorted(os.listdir(self.out)), sorted([rb.STAGED_DIST, rb.RECEIPT_NAME]))
        self.assertFalse(os.path.exists(os.path.join(self.out, rb.STAGED_DIST, "after-upload.txt")),
                         "steps after the upload step are not part of the published bytes")
        out = rb.readback(self.out, head, repo=repo, run_id="1", run_attempt="1", merge_sha=head)
        self.assertEqual((out["result"], out["file_count"], out["manifest_sha256"]),
                         ("PUBLIC_OUTPUT_CLEAN", 3, receipt["manifest_sha256"]), out)
        self.assertEqual(rb.readback(self.out, OTHER, repo=repo, run_id="1", run_attempt="1")["result"], "UNKNOWN")

    def test_optional_step_success_skips_the_fallback(self):
        repo, head = self.repo(files={"site/optional-input.json": "{}\n"})
        receipt = rb.run_build(repo, self.out, head, self.env)
        self.assertEqual((receipt["file_count"], receipt["step_outcomes"]), (2, {"optional": "success"}))

    def test_private_data_copied_by_the_build_is_found_although_no_changed_line_holds_it(self):
        repo, head = self.repo(self.step("Copy internal data", "cp internal/notes.json site/dist/data/notes.json"))
        rb.run_build(repo, self.out, head, self.env)
        out = rb.readback(self.out, head, repo=repo, run_id="1", run_attempt="1")
        self.assertEqual((out["result"], reasons(out)), ("RESTRICTED_CONTENT", ["EXPLICIT_PRIVATE_DESIGN"]), out)

    def test_every_build_failure_is_fail_closed(self):
        cases = {
            "BUILD_STEP_2_FAILED": self.step("Fails", "exit 3"),
            "BUILD_CHANGED_A_TRACKED_FILE": self.step("Edits a source", "echo x >> site/app.js"),
            "BUILD_OUTPUT_OUTSIDE_PUBLISH_ROOT": self.step("Writes elsewhere", "echo x > site/stray.json"),
            "PUBLISH_ROOT_SYMLINK_IN_PUBLIC_OUTPUT": self.step("Links", "ln -s ../../internal/notes.json site/dist/leak.json"),
            "PUBLISH_ROOT_UNEXPECTED_FILE_TYPE": self.step("Pipe", "mkfifo site/dist/pipe.json"),
            "EMPTY_PUBLIC_OUTPUT": self.step("Empties", "rm -rf site/dist && mkdir site/dist"),
            "PUBLISH_ROOT_PUBLISH_ROOT_NOT_A_DIRECTORY": self.step("Removes", "rm -rf site/dist"),
        }
        for index, (reason, extra) in enumerate(cases.items()):
            with self.subTest(reason=reason):
                shutil.rmtree(os.path.join(self.tmp, "repo"), ignore_errors=True)
                repo, head = self.repo(extra, files={"site/optional-input.json": "{}\n"})
                out = os.path.join(self.tmp, f"out{index}")
                with self.assertRaises(rb.BuildError) as caught:
                    rb.run_build(repo, out, head, self.env)
                self.assertEqual(str(caught.exception), reason)
                self.assertFalse(os.path.exists(os.path.join(out, rb.RECEIPT_NAME)), "no receipt for a failed build")

    def test_leftover_caches_are_allowed_and_hidden_entries_are_left_out_like_pages(self):
        extra = self.step("Caches and a dotfile", "mkdir -p site/node_modules/x scripts/__pycache__ && echo 1 > site/node_modules/x/i.js"
                          " && echo 1 > scripts/__pycache__/m.pyc && echo secret > site/dist/.hidden.json")
        repo, head = self.repo(extra)
        receipt = rb.run_build(repo, self.out, head, self.env)
        self.assertEqual((receipt["file_count"], receipt["hidden_entries_left_out_like_pages"]), (3, 1))
        self.assertFalse(os.path.exists(os.path.join(self.out, rb.STAGED_DIST, ".hidden.json")))
        self.assertEqual(rb.readback(self.out, head, repo=repo, run_id="1", run_attempt="1")["result"], "PUBLIC_OUTPUT_CLEAN")

    def test_preconditions_and_timeout_are_fail_closed(self):
        repo, head = self.repo()
        with self.assertRaisesRegex(rb.BuildError, "HEAD_SHA_INVALID"):
            rb.run_build(repo, self.out, "main", self.env)
        with self.assertRaisesRegex(rb.BuildError, "OUTPUT_DIRECTORY_INSIDE_REPOSITORY"):
            rb.run_build(repo, os.path.join(repo, "site", "staged"), head, self.env)
        with self.assertRaisesRegex(rb.BuildError, "BUILD_STEP_1_FAILED"):
            rb.run_build(repo, self.out, head, self.env, run_step=lambda script, cwd, timeout: 124)
        self.assertEqual(rb._bash("sleep 5", repo, 1), 124)
        os.makedirs(os.path.join(repo, "site", "dist"))
        with self.assertRaisesRegex(rb.BuildError, "PUBLISH_ROOT_EXISTS_BEFORE_BUILD"):
            rb.run_build(repo, self.out, head, self.env)
        os.rmdir(os.path.join(repo, "site", "dist"))
        Path(repo, "site", "untracked.json").write_text("{}\n", encoding="utf-8")
        with self.assertRaisesRegex(rb.BuildError, "CHECKOUT_NOT_CLEAN_BEFORE_BUILD"):
            rb.run_build(repo, self.out, head, self.env)
        os.remove(os.path.join(repo, "site", "untracked.json"))
        os.makedirs(self.out)
        Path(self.out, "old.txt").write_text("stale", encoding="utf-8")
        with self.assertRaisesRegex(rb.BuildError, "OUTPUT_DIRECTORY_NOT_EMPTY"):
            rb.run_build(repo, self.out, head, self.env)
        Path(repo, rb.PAGES_WORKFLOW).write_text(WORKFLOW_FIXTURE.replace("__EXTRA__", "      - uses: evil/action@v1\n"),
                                                 encoding="utf-8")
        with self.assertRaisesRegex(rb.BuildError, "PUBLISH_RECIPE_NOT_REPRODUCIBLE_ACTION_BEFORE_UPLOAD_NOT_KNOWN"):
            rb.run_build(repo, os.path.join(self.tmp, "fresh"), head, self.env)

    def test_cli_build_exit_codes_and_no_half_staged_bundle(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GITHUB_", "S1_"))}
        env.update(self.env)
        repo, head = self.repo(self.step("Fails late", "exit 1"))
        p = subprocess.run([sys.executable, "-I", str(SCRIPT), "build", "--repo", repo, "--head", head, "--out", self.out],
                           capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn(f"S1_SITE_PUBLIC_BUILD_V1 status=FAILED head={head} BUILD_STEP_2_FAILED", p.stdout)
        self.assertFalse(os.path.exists(self.out), "a failed build leaves nothing for the upload step")
        self.assertNotIn("S1_NATIVE_PRIVACY_SCAN_STEP_V1", p.stdout + p.stderr)
        p = subprocess.run([sys.executable, "-I", str(SCRIPT), "build", "--repo", repo, "--head", head],
                           capture_output=True, text=True, env=env)
        self.assertEqual(p.returncode, 1)

    def test_skip_only_when_the_merge_commit_changes_no_site_path(self):
        def site_change(fx):
            fx.write(SITE + "app.js", "console.log('new');\n")

        def other_change(fx):
            fx.write("docs/new.md", "A new public page.\n")

        base = {SITE + "app.js": "console.log('old');\n"}
        os.makedirs(os.path.join(self.tmp, "a"))
        fx = Fixture(os.path.join(self.tmp, "a"), site_change, base_files=base)
        self.assertIs(rb.site_changed_in_merge(str(fx.repo)), True)
        os.makedirs(os.path.join(self.tmp, "b"))
        fx = Fixture(os.path.join(self.tmp, "b"), other_change, base_files=base)
        self.assertIs(rb.site_changed_in_merge(str(fx.repo)), False)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = rb.main(["build", "--skip-unless-site-changed", "--repo", str(fx.repo), "--head", fx.head, "--out", self.out], env=self.env)
        self.assertEqual(code, 0)
        self.assertIn("status=SKIPPED", buf.getvalue())
        self.assertFalse(os.path.exists(self.out), "a skipped build stages nothing, so the readback stays absent")
        repo, _ = self.repo()                                    # a single commit: no base parent, never skipped
        self.assertIsNone(rb.site_changed_in_merge(repo))


def site_change(fx):
    fx.write(SITE + "app.js", "console.log('second edition');\n")


class PrivacyStepWithReadback(unittest.TestCase):
    """The native privacy step for a PR that changes a site path."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="s1sitestep-")
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def fixture(self, change=site_change, **kw):
        kw.setdefault("base_files", {SITE + "app.js": "console.log('first edition');\n"})
        return Fixture(self.tmp, change, **kw)

    def staged(self, fx, files=CLEAN_SITE, name="staged", **receipt):
        receipt.setdefault("head", fx.head)
        receipt.setdefault("merge_sha", fx.merge)
        return stage(self.tmp, files, name=name, **receipt)

    def test_without_a_readback_a_site_path_is_unknown_exactly_as_before(self):
        fx = self.fixture()
        code, out, text = fx.cli()
        self.assertEqual((code, out["result"], out["wrapper_reasons"]), (1, "UNKNOWN", []), out)
        self.assertEqual([f["reason"] for f in out["scanner_result"]["findings"]], [NEEDS])
        self.assertNotIn("site_public_readback", out, "no readback input: the step output has no new field")
        self.assertEqual(text.count("S1_NATIVE_PRIVACY_SCAN_STEP_V1 result="), 1)
        self.assertIn(f"S1_NATIVE_PRIVACY_SCAN_STEP_V1 result=UNKNOWN head={fx.head} mode=enforce exit=1", text)
        # absent, empty, failed, stale or unparsable readback input: the scanner sees the very same record
        absent = os.path.join(self.tmp, "never-downloaded")
        variants = {"empty value": "", "absent directory": absent,
                    "other head": self.staged(fx, name="o1", head=OTHER),
                    "other checkout": self.staged(fx, name="o2", merge_sha=OTHER),
                    "other run": self.staged(fx, name="o3", run_id="99"),
                    "failed build": self.staged(fx, name="o4", status="FAILED"),
                    "unpinned binary": self.staged(fx, name="o5", files=dict(CLEAN_SITE, **{"x.png": PNG}))}
        unparsable = self.staged(fx, name="o6")
        Path(unparsable, rb.RECEIPT_NAME).write_text("{not json", encoding="utf-8")
        variants["unparsable receipt"] = unparsable
        for name, value in variants.items():
            with self.subTest(name=name):
                code2, out2, text2 = fx.cli(S1_SITE_PUBLIC_READBACK_DIR=value)
                self.assertEqual((code2, out2["result"]), (1, "UNKNOWN"), out2)
                self.assertEqual(out2["scanner_result"], out["scanner_result"])
                self.assertEqual(text2.count("S1_NATIVE_PRIVACY_SCAN_STEP_V1 result="), 1)
                if value:
                    self.assertEqual(out2["site_public_readback"]["result"], "UNKNOWN")
                    self.assertEqual({k: v for k, v in out2.items() if k != "site_public_readback"}, out)
                else:
                    self.assertEqual(out2, out)

    def test_clean_readback_for_this_head_lifts_the_unknown_of_a_site_only_diff(self):
        fx = self.fixture()
        code, out, text = fx.cli(S1_SITE_PUBLIC_READBACK_DIR=self.staged(fx))
        self.assertEqual((code, out["result"], out["wrapper_reasons"]), (0, "NO_RESTRICTED_CONTENT", []), out)
        self.assertEqual(out["scanner_result"]["findings"], [])
        self.assertEqual((out["site_public_readback"]["result"], out["site_public_readback"]["head"]),
                         ("PUBLIC_OUTPUT_CLEAN", fx.head))
        self.assertEqual(out["site_public_readback"]["file_count"], len(CLEAN_SITE))
        self.assertTrue(out["scan_code"]["identical_to_base_parent"])
        self.assertEqual(text.count("S1_NATIVE_PRIVACY_SCAN_STEP_V1 result="), 1)
        self.assertIn(f"S1_NATIVE_PRIVACY_SCAN_STEP_V1 result=NO_RESTRICTED_CONTENT head={fx.head} mode=enforce exit=0", text)

    def test_restricted_generated_file_that_is_not_in_the_diff_fails_the_step(self):
        fx = self.fixture()
        files = dict(CLEAN_SITE, **{"data/copied-by-the-build.json": json.dumps({"k": API_KEY}) + "\n"})
        code, out, text = fx.cli(S1_SITE_PUBLIC_READBACK_DIR=self.staged(fx, files=files))
        self.assertEqual((code, out["result"]), (1, "RESTRICTED_CONTENT"), out)
        self.assertEqual(out["site_public_readback"]["findings_by_rule"], {"API_KEY_LITERAL": 1})
        self.assertIn("GENERATED_PUBLIC_OUTPUT_RESTRICTED_CONTENT", [f["reason"] for f in out["scanner_result"]["findings"]])
        self.assertNotIn(API_KEY, text)
        self.assertNotIn("copied-by-the-build", text)
        self.assertEqual(text.count("S1_NATIVE_PRIVACY_SCAN_STEP_V1 result="), 1)

    def test_the_diff_itself_is_still_scanned_under_a_clean_readback(self):
        fx = self.fixture(lambda f: f.write(SITE + "app.js", f"// {MARKER} design\n"))
        code, out, text = fx.cli(S1_SITE_PUBLIC_READBACK_DIR=self.staged(fx))
        self.assertEqual((code, out["result"]), (1, "RESTRICTED_CONTENT"), out)
        self.assertEqual(out["site_public_readback"]["result"], "PUBLIC_OUTPUT_CLEAN")
        self.assertEqual({f["reason"] for f in out["scanner_result"]["findings"]}, {"EXPLICIT_PRIVATE_DESIGN"})
        self.assertNotIn(MARKER, text)
        # a binary site file in the diff stays UNKNOWN: the readback lifts one reason, not the others
        shutil.rmtree(self.tmp)
        os.makedirs(self.tmp)
        fx = self.fixture(lambda f: f.write(SITE + "logo.png", PNG))
        code, out, _ = fx.cli(S1_SITE_PUBLIC_READBACK_DIR=self.staged(fx))
        self.assertEqual((code, out["result"]), (1, "UNKNOWN"), out)
        self.assertNotIn(NEEDS, [f["reason"] for f in out["scanner_result"]["findings"]])

    def test_site_path_with_an_owner_gated_path_is_high_impact_path_only(self):
        def change(fx):
            site_change(fx)
            fx.write("00_FMOS/NOTE.md", "Governance note.\n")

        fx = self.fixture(change)
        code, out, _ = fx.cli()
        self.assertEqual((code, out["result"]), (1, "UNKNOWN"), out)
        code, out, _ = fx.cli(S1_SITE_PUBLIC_READBACK_DIR=self.staged(fx))
        self.assertEqual((code, out["result"]), (0, "HIGH_IMPACT_PATH_ONLY"), out)

    def test_pr_that_changes_the_readback_code_or_the_pages_recipe_is_never_lane_evidence(self):
        for index, rel in enumerate(("scripts/governance/s1_site_public_readback_v1.py", rb.PAGES_WORKFLOW)):
            with self.subTest(rel=rel):
                shutil.rmtree(self.tmp)
                os.makedirs(self.tmp)

                def change(fx, rel=rel):
                    site_change(fx)
                    text = (ROOT / rel).read_text(encoding="utf-8")
                    changed = text.replace("- name: Checkout\n", "- name: Checkout the tree\n") if rel == rb.PAGES_WORKFLOW \
                        else text + "\n# changed by the PR\n"
                    self.assertNotEqual(changed, text)
                    fx.write(rel, changed)

                fx = self.fixture(change)
                code, out, _ = fx.cli(S1_SITE_PUBLIC_READBACK_DIR=self.staged(
                    fx, workflow=(fx.repo / rb.PAGES_WORKFLOW).read_bytes()))
                self.assertIn("SCAN_CODE_CHANGED_BY_PR_OR_ABSENT_ON_BASE", out["wrapper_reasons"])
                self.assertNotEqual(out["result"], "NO_RESTRICTED_CONTENT")
        self.assertIn("scripts/governance/s1_site_public_readback_v1.py", step.SCAN_CODE_PATHS)
        self.assertIn(rb.PAGES_WORKFLOW, step.SCAN_CODE_PATHS)

    def test_a_pr_without_a_site_path_never_consults_the_readback(self):
        fx = self.fixture(lambda f: f.write("docs/new.md", "A new public page.\n"))
        bad = self.staged(fx, files=dict(CLEAN_SITE, **{"n.txt": MARKER + "\n"}))
        code, out, _ = fx.cli(S1_SITE_PUBLIC_READBACK_DIR=bad)
        self.assertEqual((code, out["result"]), (0, "NO_RESTRICTED_CONTENT"), out)
        self.assertNotIn("site_public_readback", out)

    def test_deleted_and_renamed_site_paths_need_the_readback_too(self):
        base = {SITE + "app.js": "console.log('first edition');\n", SITE + "old.js": "console.log('old page');\n" * 30}
        fx = self.fixture(lambda f: (f.repo / SITE / "old.js").unlink(), base_files=base)
        self.assertEqual(fx.cli()[1]["result"], "UNKNOWN")
        code, out, _ = fx.cli(S1_SITE_PUBLIC_READBACK_DIR=self.staged(fx))
        self.assertEqual((code, out["result"]), (0, "NO_RESTRICTED_CONTENT"), out)


class ScannerInputContract(unittest.TestCase):
    """scan_pr itself: the site reason is lifted only by a decided readback of this contract for the same head."""

    def record(self, **extra):
        path = SITE + "app.js"
        rec = {"repo": scanner.REPO, "head": HEAD, "pr_head_sha": HEAD, "changed_files_count_head_sha": HEAD,
               "changed_files_count": 1, "pages_complete": True, "title": "Update the site", "body": "",
               "files": [{"path": path, "status": "modified", "head_sha": HEAD, "binary": False, "is_symlink": False,
                          "patch": "+console.log(2);\n", "patch_complete": True, "content": "console.log(2);\n",
                          "content_head_sha": HEAD}]}
        rec.update(extra)
        return rec

    def rb(self, **kw):
        doc = {"contract": "S1_SITE_PUBLIC_READBACK_V1", "head": HEAD, "result": "PUBLIC_OUTPUT_CLEAN"}
        doc.update(kw)
        return doc

    def test_only_a_clean_same_head_readback_lifts_the_reason(self):
        base = scanner.scan_pr(self.record())
        self.assertEqual((base["result"], [f["reason"] for f in base["findings"]]), ("UNKNOWN", [NEEDS]))
        self.assertEqual(scanner.scan_pr(self.record(site_public_readback=self.rb()))["result"], "NO_RESTRICTED_CONTENT")
        for bad in (None, "PUBLIC_OUTPUT_CLEAN", [], {}, self.rb(head=OTHER), self.rb(head=None), self.rb(contract="X"),
                    self.rb(result="UNKNOWN"), self.rb(result="NO_RESTRICTED_CONTENT"), self.rb(result=True)):
            with self.subTest(bad=bad):
                out = scanner.scan_pr(self.record(site_public_readback=bad))
                self.assertEqual((out["result"], [f["reason"] for f in out["findings"]]), ("UNKNOWN", [NEEDS]))
        out = scanner.scan_pr(self.record(site_public_readback=self.rb(result="RESTRICTED_CONTENT")))
        self.assertEqual((out["result"], [f["reason"] for f in out["findings"]]),
                         ("RESTRICTED_CONTENT", ["GENERATED_PUBLIC_OUTPUT_RESTRICTED_CONTENT"]))
        self.assertTrue(step.is_content_reason("GENERATED_PUBLIC_OUTPUT_RESTRICTED_CONTENT"))

    def test_a_readback_never_lifts_any_other_reason_and_is_ignored_without_a_site_path(self):
        rec = self.record(site_public_readback=self.rb())
        rec["files"][0]["patch_complete"] = False
        self.assertEqual(scanner.scan_pr(rec)["result"], "UNKNOWN")
        rec = self.record(site_public_readback=self.rb(result="RESTRICTED_CONTENT"))
        rec["files"][0]["path"] = "docs/app.js"
        self.assertEqual(scanner.scan_pr(rec)["result"], "NO_RESTRICTED_CONTENT")
        rec = self.record(site_public_readback=self.rb())
        rec["files"][0]["content"] = f"// {MARKER} design\n"
        self.assertEqual(scanner.scan_pr(rec)["result"], "RESTRICTED_CONTENT")


class RealSiteTree(unittest.TestCase):
    """Honest readings of this tree. No rule is loosened to make either of them pass."""

    def test_tracked_site_sources_hold_no_content_rule_match(self):
        # The tracked source directory is NOT the published bundle (that is generated); this reads it as bytes with
        # the same engine so that a rule match in a file the build copies verbatim is seen without running a build.
        tmp = tempfile.mkdtemp(prefix="s1sitereal-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        names = [n for n in git(ROOT, "ls-files", "--", SITE.rstrip("/")).splitlines() if n]
        files = {n[len(SITE):]: (ROOT / n).read_bytes() for n in names}
        self.assertGreater(len(files), 150)
        out = rb.readback(stage(tmp, files), HEAD, repo=repo_with_recipe(tmp), run_id="1", run_attempt="1")
        self.assertEqual(out["file_count"], len(files))
        # Recorded honest reading on 2026-11-17 (no rule was loosened): RESTRICTED_CONTENT for the SOURCE tree, from
        # exactly one CREDENTIAL_ASSIGNMENT match. It is the negative-control sentinel of a site test input (a fake
        # value the test asserts never reaches the public projection); the file is not in the published set, and the
        # generated bundle of the same tree reads back clean (next test). Every other reason is a file type that is
        # not published as it is: the base64 parts of the social card and one source image.
        sentinel = rb._path_ref("tests/test_public_hourly_curve.py")
        content = [f for f in out["findings"] if step.is_content_reason(f["reason"])]
        self.assertLessEqual({(f["reason"], f["path_sha256_16"]) for f in content}, {("CREDENTIAL_ASSIGNMENT", sentinel)},
                             "a tracked site source newly matches a content rule: fix the source, never the rule")
        self.assertEqual(out["result"], "RESTRICTED_CONTENT" if content else "UNKNOWN")
        self.assertLessEqual(set(out["findings_by_rule"]), {"CREDENTIAL_ASSIGNMENT", "BINARY_PUBLISHED_FILE_NOT_PINNED"})
        self.assertEqual(out["findings_by_rule"].get("BINARY_PUBLISHED_FILE_NOT_PINNED"), 7)

    @unittest.skipUnless(os.environ.get("S1_SITE_READBACK_REAL_BUILD") == "1" and shutil.which("node") and shutil.which("npm"),
                         "opt-in: S1_SITE_READBACK_REAL_BUILD=1 runs the real Pages build steps (node, npm ci, a browser)")
    def test_real_pages_build_of_this_tree_reads_back_clean(self):
        tmp = tempfile.mkdtemp(prefix="s1sitebuildreal-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        recipe = rb.parse_pages_recipe(PAGES.decode("utf-8"))
        self.addCleanup(shutil.rmtree, ROOT / recipe["publish_root"], ignore_errors=True)
        self.addCleanup(shutil.rmtree, ROOT / SITE / "premium-v2" / "node_modules", ignore_errors=True)
        head = git(ROOT, "rev-parse", "HEAD")
        staged = os.path.join(tmp, "staged")
        receipt = rb.run_build(str(ROOT), staged, head, {"GITHUB_RUN_ID": "1", "GITHUB_RUN_ATTEMPT": "1"})
        out = rb.readback(staged, head, repo=str(ROOT), run_id="1", run_attempt="1", merge_sha=head)
        print(json.dumps({k: out[k] for k in ("result", "file_count", "total_bytes", "text_files_scanned",
                                              "binary_files_pinned", "findings_by_rule", "manifest_sha256")}))
        self.assertEqual((out["result"], out["findings_by_rule"]), ("PUBLIC_OUTPUT_CLEAN", {}), out)
        self.assertEqual(out["file_count"], receipt["file_count"])
        self.assertEqual(out["binary_files_pinned"], 2)


if __name__ == "__main__":
    unittest.main()
