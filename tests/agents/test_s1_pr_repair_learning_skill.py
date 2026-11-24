"""Static, adversarial routing checks for the repository-local S1 skill."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import json
import unittest
import hashlib
import tempfile
from tests.exact_pr_head_support import ensure_exact_pr_head

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / ".agents/skills/s1-pr-repair-learning/SKILL.md"
CASES = ROOT / ".agents/skills/s1-pr-repair-learning/references/verified-casebook.json"

class S1RepairLearningSkillTest(unittest.TestCase):
    def test_installed_skill_and_triggers(self):
        body = SKILL.read_text(encoding="utf-8")
        self.assertTrue(body.startswith("---\nname: s1-pr-repair-learning\n"))
        for marker in ("PROCESS_STALLED", "merge base", "adversarial negatives",
                       "native merge", "postmerge", "CANDIDATE_ONLY", "skill-quality-gate",
                       "Sol MAX", "original PR", "AGENTS.md"):
            self.assertIn(marker.lower(), body.lower())
        self.assertNotIn("AUTO_APPROVE", body)
        self.assertNotIn("AUTO_PAID_DISPATCH", body)

    def test_routing_is_discoverable_but_not_new_authority(self):
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        registry = (ROOT / "00_ARCHIVE_CONTROL/SKILL_REGISTRY.md").read_text(encoding="utf-8")
        self.assertIn(".agents/skills/s1-pr-repair-learning/SKILL.md", agents)
        self.assertIn(".agents/skills/s1-pr-repair-learning/SKILL.md", registry)
        self.assertIn("existing", agents.split("### 0.2b S1", 1)[1].split("### 0.3", 1)[0].lower())
        self.assertIn("no new", registry.lower())

    def test_cases_separate_merge_from_production(self):
        packet = json.loads(CASES.read_text(encoding="utf-8"))
        self.assertEqual(packet["contract"], "S1_PR_REPAIR_LEARNING_CASEBOOK_v1")
        self.assertEqual({x["original_pr"] for x in packet["examples"]}, {176, 1879, 1889, 1900})
        self.assertTrue(all(x["merge_confirmed"] for x in packet["examples"]))
        self.assertTrue(all("not" in x["verified_limit"].lower() or
                            "remain" in x["verified_limit"].lower() or
                            "requires" in x["verified_limit"].lower()
                            for x in packet["examples"]))
        self.assertGreaterEqual(len(packet["negative_controls"]), 6)
        alpha = next(case for case in packet["examples"] if case["id"] == "S1-RECOVERY-ALPHA-176")
        self.assertEqual(alpha["repository"], "Donh91/Meme-Alpha-Lab")
        self.assertEqual(len(alpha["merged_main_sha"]), 40)
        self.assertEqual(len(alpha["conflict_resolution_sha"]), 40)
        self.assertEqual(alpha["original_files_preserved_without_blob_change"], 16)
        self.assertEqual(alpha["workflow_merge_additive_lines"], 19)
        self.assertEqual(alpha["overlapping_changed_paths"], [".github/workflows/v4-gate.yml"])
        self.assertEqual(alpha["exact_head_ci"]["event"], "pull_request")
        self.assertEqual(alpha["exact_head_ci"]["conclusion"], "success")
        self.assertIn("NOT VERIFIED", alpha["verified_limit"])
        self.assertIn("owner-invoked", alpha["verified_limit"])



def _git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True,
                          capture_output=True, timeout=60).stdout


def materialize_exact_host_tree(root, head, destination):
    """Test exact PR host bytes without changing shared checkout or shallow graph."""
    ensure_exact_pr_head(root, head)
    records = _git(root, "ls-tree", "-r", "-z", head, "--", "tools/s1-release-control")
    entries = [item for item in records.split(b"\0") if item]
    if not entries:
        raise ValueError("S1_HOST_TREE_EMPTY")
    seen = set()
    for entry in entries:
        metadata, raw_path = entry.split(b"\t", 1)
        mode, kind, blob = metadata.decode("ascii").split()
        rel = Path(raw_path.decode("utf-8"))
        if (mode not in {"100644", "100755"} or kind != "blob" or
                rel.is_absolute() or ".." in rel.parts or
                rel.parts[:2] != ("tools", "s1-release-control") or rel in seen):
            raise ValueError("S1_HOST_TREE_UNSAFE_ENTRY")
        seen.add(rel)
        raw = _git(root, "cat-file", "blob", blob)
        actual = hashlib.sha1(("blob %d\0" % len(raw)).encode("ascii") + raw).hexdigest()
        if actual != blob:
            raise ValueError("S1_HOST_BLOB_MISMATCH")
        output = destination / rel
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("xb") as handle:
            handle.write(raw)
        if mode == "100755":
            output.chmod(0o755)
    return len(entries)


class S1ExactHostIsolation(unittest.TestCase):
    def test_exact_head_tree_does_not_mutate_shared_graph_or_worktree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            root.mkdir()
            _git(root, "init", "-q")
            _git(root, "config", "user.name", "Fixture")
            _git(root, "config", "user.email", "fixture@example.invalid")
            file = root / "tools/s1-release-control/test.mjs"
            file.parent.mkdir(parents=True)
            file.write_bytes(b"old")
            _git(root, "add", ".")
            _git(root, "commit", "-qm", "old")
            head = _git(root, "rev-parse", "HEAD").decode().strip()
            file.write_bytes(b"new")
            _git(root, "add", ".")
            _git(root, "commit", "-qm", "new")
            before = _git(root, "rev-parse", "HEAD")
            shallow = _git(root, "rev-parse", "--is-shallow-repository")
            destination = Path(directory) / "isolated"
            self.assertEqual(materialize_exact_host_tree(root, head, destination), 1)
            self.assertEqual((destination / "tools/s1-release-control/test.mjs").read_bytes(), b"old")
            self.assertEqual(file.read_bytes(), b"new")
            self.assertEqual(_git(root, "rev-parse", "HEAD"), before)
            self.assertEqual(_git(root, "rev-parse", "--is-shallow-repository"), shallow)
            _git(root, "merge-base", "--is-ancestor", head, "HEAD")
            self.assertEqual(_git(root, "status", "--porcelain"), b"")
            with self.assertRaises(ValueError):
                materialize_exact_host_tree(root, "HEAD", Path(directory) / "invalid")
            with self.assertRaises(subprocess.CalledProcessError):
                materialize_exact_host_tree(root, "0" * 40, Path(directory) / "missing")


    def test_already_shallow_merge_checkout_fetches_only_bound_second_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            origin = Path(directory) / "origin"
            origin.mkdir()
            _git(origin, "init", "-q")
            _git(origin, "config", "user.name", "Fixture")
            _git(origin, "config", "user.email", "fixture@example.invalid")
            file = origin / "tools/s1-release-control/test.mjs"
            file.parent.mkdir(parents=True)
            file.write_bytes(b"base")
            _git(origin, "add", ".")
            _git(origin, "commit", "-qm", "base")
            base = _git(origin, "rev-parse", "HEAD").decode().strip()
            _git(origin, "checkout", "-qb", "candidate")
            file.write_bytes(b"candidate")
            _git(origin, "commit", "-qam", "candidate")
            candidate = _git(origin, "rev-parse", "HEAD").decode().strip()
            _git(origin, "checkout", "-qb", "merge-target", base)
            (origin / "other.txt").write_text("main")
            _git(origin, "add", ".")
            _git(origin, "commit", "-qm", "main")
            main = _git(origin, "rev-parse", "HEAD").decode().strip()
            _git(origin, "merge", "--no-ff", "--no-edit", "candidate")
            merge = _git(origin, "rev-parse", "HEAD")
            checkout = Path(directory) / "shallow"
            subprocess.run(["git", "clone", "-q", "--depth=1", "--branch", "merge-target",
                            origin.as_uri(), str(checkout)], check=True, capture_output=True)
            self.assertEqual(_git(checkout, "rev-parse", "--is-shallow-repository"), b"true\n")
            for invalid in (main, base, "0" * 40):
                with self.assertRaisesRegex(ValueError, "NOT_RAW_MERGE_PARENT"):
                    ensure_exact_pr_head(checkout, invalid)
            destination = Path(directory) / "host"
            self.assertEqual(materialize_exact_host_tree(checkout, candidate, destination), 1)
            self.assertEqual((destination / "tools/s1-release-control/test.mjs").read_bytes(), b"candidate")
            self.assertEqual(_git(checkout, "rev-parse", "HEAD"), merge)
            self.assertEqual(_git(checkout, "status", "--porcelain"), b"")
            self.assertEqual(_git(checkout, "rev-parse", "--is-shallow-repository"), b"true\n")


class S1ReleaseControlHostAcceptance(unittest.TestCase):
    """Actual Node and Chrome acceptance of existing S1 read-only code, no workflow edit."""

    @classmethod
    def setUpClass(cls):
        cls.node = shutil.which("node")
        if cls.node is None:
            raise AssertionError("S1_NODE_NOT_INSTALLED")
        found = subprocess.run([cls.node, "--version"], check=True, text=True,
                               stdout=subprocess.PIPE, timeout=10).stdout.strip()
        major = int(found.removeprefix("v").split(".")[0])
        if major < 22:
            alternatives = sorted(Path("/opt/hostedtoolcache/node").glob("22.*/x64/bin/node"))
            if alternatives:
                cls.node = str(alternatives[-1])
                found = subprocess.run([cls.node, "--version"], check=True,
                                       text=True, stdout=subprocess.PIPE, timeout=10).stdout.strip()
                major = int(found.removeprefix("v").split(".")[0])
        if major < 22:
            raise AssertionError("S1_NODE_22_REQUIRED_FOUND_" + found)
        print("S1_CI_NODE_VERSION=" + found, flush=True)
        cls.host_root = ROOT
        if os.getenv("GITHUB_EVENT_NAME") == "pull_request":
            event_path = os.getenv("GITHUB_EVENT_PATH")
            if not event_path:
                raise AssertionError("S1_PR_EVENT_PATH_MISSING")
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
            head = event.get("pull_request", {}).get("head", {}).get("sha", "")
            if not re.fullmatch(r"[0-9a-f]{40}", head):
                raise AssertionError("S1_PR_EVENT_HEAD_INVALID")
            temporary = tempfile.TemporaryDirectory(prefix="s1-exact-host-")
            cls.addClassCleanup(temporary.cleanup)
            cls.host_root = Path(temporary.name)
            cls.host_blob_count = materialize_exact_host_tree(ROOT, head, cls.host_root)
            print("S1_CI_EXACT_PR_HEAD=" + head, flush=True)
        elif os.getenv("CI") and os.getenv("GITHUB_EVENT_NAME") not in ("push", "workflow_dispatch"):
            raise AssertionError("S1_HOST_EVENT_UNKNOWN")

    def _run(self, argv, *, env=None, timeout=80):
        result = subprocess.run([self.node, *argv], cwd=self.host_root, env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=timeout, check=False)
        self.assertEqual(result.returncode, 0, result.stdout[-12000:])
        return result.stdout

    def test_node_public_privacy_regressions(self):
        output = self._run([
            "--test-reporter=tap",  # Node 22/24 format-stable, preserves exact TAP assertions
            "--test",
            "tools/s1-release-control/test-discovery-inventory-v1.mjs",
            "tools/s1-release-control/test-agent-work-hub-v1.mjs",
            "tools/s1-release-control/test-history-core-v1.mjs",
            "tools/s1-release-control/test-static.mjs",
        ])
        matches = dict((key, int(count)) for key, count in
                       re.findall(r"(?m)^# (tests|pass|fail) (\d+)$", output))
        self.assertGreaterEqual(matches.get("tests", 0), 37, output[-6000:])
        self.assertEqual(matches.get("pass"), matches["tests"], output[-6000:])
        self.assertEqual(matches.get("fail"), 0, output[-6000:])
        print("S1_CI_HOSTED_NODE_TESTS=" + str(matches["tests"]) + "_PASS_0_FAIL", flush=True)

    def test_chrome_public_and_api_denied(self):
        for mode, expected in (("mock", "MOCK_PUBLIC_SUCCESS"), ("denied", "API_DENIED")):
            with self.subTest(mode=mode):
                env = os.environ.copy()
                env["S1_BROWSER_MODE"] = mode
                output = self._run(["tools/s1-release-control/test-browser.mjs"],
                                   env=env, timeout=100)
                match = re.search(r"S1_CHROME_ACCEPTANCE (\{[^\n]+\})", output)
                self.assertIsNotNone(match, output[-6000:])
                payload = json.loads(match.group(1))
                self.assertEqual(payload.get("mode"), expected)
                self.assertEqual([x["width"] for x in payload.get("reports", [])],
                                 [390, 430, 1440])
                self.assertEqual(payload.get("exceptions"), [])
                print("S1_CI_HOSTED_CHROME_" + expected + "_PASS_390_430_1440", flush=True)

if __name__ == "__main__":
    unittest.main()
