"""Static, adversarial routing checks for the repository-local S1 skill."""
from pathlib import Path
import os
import re
import shutil
import subprocess
import json
import unittest

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
        if os.getenv("GITHUB_EVENT_NAME") == "pull_request":
            event_path = os.getenv("GITHUB_EVENT_PATH")
            if not event_path:
                raise AssertionError("S1_PR_EVENT_PATH_MISSING")
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))
            head = event.get("pull_request", {}).get("head", {}).get("sha", "")
            if not re.fullmatch(r"[0-9a-f]{40}", head):
                raise AssertionError("S1_PR_EVENT_HEAD_INVALID")
            for command in (["git", "fetch", "--no-tags", "--depth=1", "origin", head],
                            ["git", "checkout", "--detach", head]):
                completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                                           timeout=60, check=False)
                if completed.returncode:
                    raise AssertionError("S1_HEAD_CHECKOUT_FAILED " + completed.stderr[-3000:])
            actual = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                    check=True, text=True, stdout=subprocess.PIPE,
                                    timeout=10).stdout.strip()
            if actual != head:
                raise AssertionError("S1_PR_HEAD_MISMATCH")
            print("S1_CI_EXACT_PR_HEAD=" + head, flush=True)
        elif os.getenv("CI") and os.getenv("GITHUB_EVENT_NAME") not in ("push", "workflow_dispatch"):
            raise AssertionError("S1_HOST_EVENT_UNKNOWN")

    def _run(self, argv, *, env=None, timeout=80):
        result = subprocess.run([self.node, *argv], cwd=ROOT, env=env, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                timeout=timeout, check=False)
        self.assertEqual(result.returncode, 0, result.stdout[-12000:])
        return result.stdout

    def test_node_public_privacy_regressions(self):
        output = self._run([
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
