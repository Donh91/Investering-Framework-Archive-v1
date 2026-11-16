"""S1 reviewed-merge lane (AGENTS.md section 0.2e): the owner's standing decision is a blob on main.

Chain of trust: saved task == BOOTSTRAP.txt (owner-pasted RUNTIME_CONTRACT blob, which pins ACTION_LOOP and this switch) -> ACTION_LOOP
(blob-pinned by RUNTIME_CONTRACT) -> LANE INTEGRITY content pins over AGENTS.md, the S1 job manifest and
the .github / scripts/governance / scripts/health / 07_PROMPTS_AND_AGENTS trees. Section 0.2e, the
bootstrap and the critical ACTION_LOOP lines are pinned by hash here, so any rewording fails CI.
"""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S1 = ROOT / "00_FMOS" / "S1"
LANE = S1 / "REVIEWED_MERGE_LANE.json"
LOOP = S1 / "ACTION_LOOP.md"
AGENTS = ROOT / "AGENTS.md"
MANIFEST = ROOT / "00_FMOS" / "S1_REQUIRED_PR_JOBS_POLICY_V1.json"

SECTION_SHA256 = "5ffac556ad0f58f96668c5fc4c8cb1fedd2ac262982027841e32a12fa2a5ce1f"
BOOTSTRAP_SHA256 = "0b60df528970d9c4bf5289f141fce17b3425717fb2247698f90d7c4e6f9b698b"
LINE_PINS = {'CC_ONLY': 'ee27bee9fc9404a603c57425f93e0a840caf15c7a3b929456f8d04cebd4803d1', 'CC_PR': '85bf8e3655a52a657d20f2992ccb40acc0d69cc7f3ae182a8401550e0f22e423', 'H1': '90b9d0a439ea6fcb5d2b45ba7d601eaa3946f39863d38540452326a85333f87e', 'H2': '9a265f4ba6bda93bf8f22bbc23b63f9f2f672c2de1f14ee51d4c978544fcc078', 'H3': 'a9fb6bc830284ee5e0e38d1fc80283037274248fd109b502c13edde79dd5af5f', 'H4': 'd47f6f701a0744ad1e8076b4c4bbdd7ed77578c4e3d014800d7ad11b6909da7e', 'H5': '234a31fb00136d622cc195983ed3a4e7b6d402a3ba11bfddfe75cd48922e681e', 'H6': '7aa5c467a3ee785d017a9ff8a0b7d017c9fbfeccb53e777d0a196a4585e78144', 'H7': '73981c63af506f153556961808dcac7d35bacb20d510c241e5565c6bb022d4ea', 'H8': '0343db2e8f9173b68600baaa0f8cbaf75eb2fe7247d243fdff7bb1948fea9b0b', 'LADDER': '7f9b1a7201709722314fc01237450d0ce680c0c367a3d67a5b3892f341b55ab8', 'LANE_INTEGRITY': 'd3d4818152a356742bed34c9b3216cceaa7b83cd503ba357ea726b90e03db140', 'RULE4': '32a5dfffd81b605332ae484e31246b6142b567cc2b3d85489271d039ad210550'}
PINNED = ("AGENTS.md", "00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json", ".github", ".agents", "scripts/governance",
          "scripts/health", "07_PROMPTS_AND_AGENTS", "01_CORE_FRAMEWORK/governance")


def section_0_2e():
    text = AGENTS.read_text(encoding="utf-8")
    start = text.index("### 0.2e S1 reviewed-merge lane")
    return text[start:text.index("### 0.3 ", start)]


class PinTest(unittest.TestCase):
    def test_section_text_is_pinned(self):
        self.assertEqual(hashlib.sha256(section_0_2e().encode("utf-8")).hexdigest(), SECTION_SHA256)

    def test_bootstrap_is_pinned_and_pins_the_contract_blob(self):
        boot = (S1 / "BOOTSTRAP.txt").read_bytes()
        self.assertEqual(hashlib.sha256(boot).hexdigest(), BOOTSTRAP_SHA256)
        text = boot.decode("utf-8")
        for token in ("3b. The Git blob SHA of 00_FMOS/S1/RUNTIME_CONTRACT.json at that same main SHA (as GitHub reports it) must equal ",
                      "If not, or if it cannot be read: write no GitHub change",
                      "This value changes only when the owner pastes a new BOOTSTRAP.txt from a squash PR that the owner approves in person."):
            self.assertIn(token, text)

    def test_critical_action_loop_lines_are_pinned(self):
        seen = {}
        prefixes = {"LANE_INTEGRITY": "LANE INTEGRITY", "LADDER": "LADDER:", "RULE4": "4 MERGE.",
                    "CC_ONLY": "- This file (00_FMOS/S1/ACTION_LOOP.md", "CC_PR": "- S1 behaviour changes ONLY"}
        for line in LOOP.read_text(encoding="utf-8").splitlines():
            for i in range(1, 9):
                if line.startswith(f"H{i} "):
                    seen[f"H{i}"] = hashlib.sha256(line.encode("utf-8")).hexdigest()
            for key, prefix in prefixes.items():
                if line.startswith(prefix):
                    seen[key] = hashlib.sha256(line.encode("utf-8")).hexdigest()
        self.assertEqual(seen, LINE_PINS)


class Rule4ChecklistTest(unittest.TestCase):
    """v1.6: S1 must execute the mechanical checklist, not stop after reading (2026-11-15 production finding)."""

    def test_work_rule_and_checklist_steps(self):
        loop = LOOP.read_text(encoding="utf-8")
        self.assertIn("WORK RULE: reading is not the job.", loop)
        self.assertIn("an item is NOT PROVEN only after you called the tool and quote its error", loop)
        self.assertIn("RULE 4 CHECKLIST", loop)
        for step in ("C1 ", "C2 (a) ", "C3 (b) ", "C4 (c) ", "C5 (d) ", "C6 (e) ", "C7 Lane state", "C8 (g) F3 census",
                     "C9 Post one S1_LANE_MERGE_INTENT_v1 on #1156", "C10 Readback", "C11 Batch"):
            self.assertIn("\n" + step, loop)
        for token in ("verdict: APPROVE", "without an event filter",
                      "page=2, twice", "contents/scripts?ref=M", "skipped=<PR>:C<n>:<reason>",
                      "for EVERY rule-4 merge, lane or not", "take the NEWEST CLAUDE_REVIEW_v1 whose head_sha is H",
                      "created before the review", "at ref bridge_commit has Git blob SHA report_blob",
                      "move to the next rule-4 candidate", "continue the LADDER with rules 2 and 3",
                      "previous_filename", "none found means NOT PROVEN", "post one S1_LANE_HALTED on #1156",
                      "C11 Batch", "disjoint from every PR merged in this run", "C1b MAIN DRIFT", "that alone never stales the checklist", "compare_commits M...M2", "At most two restarts per candidate", "the file list is not complete (300 files or more, or further pages)", "NOOP SOURCE_CHANGED; if a merge already happened in this batch, the MERGE line with source_changed inside its detail", "older than 60 minutes and younger than 24 h", "PR head.sha equal to the intent's H", "take the OLDEST one kept", "within 15 minutes of it", "two parents is not S1's squash: drop the intent", "with reason readback or reconcile_readback", "write unavailable for any you cannot read, never a guess", "PR=- head=- run=<run id> unless one already names that run", "Every S1_LANE_HALTED names PR=<n> head=<40>", "never halt for an unkept intent", "RECONCILED(c=<id>) main=<8> contract=<8>", "author Donh91, created_at equals updated_at, its contract=<8> equals this run's contract", "no rule bypass in the merge's native evidence. On a pass", "LANE_HALTED(reconcile)", "RECONCILED(c=<id>)", "a timeout or any other merge failure", "After the bootstrap and the H1 check", "skipped=<PR>:C8:head_changed; never re-bind H here", "MERGE_REFUSED(<status>)", "no retry and no other write", "contract=<8>; part of this batch", "compare_commits bridge_commit...claude/log reports status ahead or identical", "total_commits exceeds 250", "compare status is not ahead or identical", "first RECONCILE", "S1_LANE_MERGE_INTENT_v1", "skipped=<PR>:C2:needs_branch_update", "still shows R as the newest CLAUDE_REVIEW_v1 for H", "skipped=<PR>:C8:ruleset_unproven", "is an ancestor of (or equal to) current main", "Main moving on after the merge is normal and never a mismatch", "a halt ends the batch", "skipped=<PR>:C1b:main_drift", "report: <path>", "that post is the run's single write", "if NO merge has happened in this run",
                      "if a merge already happened, the batch stops", "run H6 and rule 1 (ANSWER)", "path reports/claude/STATUS.md, ref claude/log", "live on Bridge PR #173", "never on the Archive PRs",
                      "is a halt trigger: post one S1_LANE_HALTED", "bridge_commit is an ancestor of, or equal to, Bridge branch claude/log", "read AGENTS.md in full",
                      "INDEPENDENT_DETACHED whenever the request, the review or the PR body says H implements a Claude-authored package", "created_at equals updated_at"):
            self.assertIn(token, loop)


class ContentPinsTest(unittest.TestCase):
    """Every PR that changes a pinned path must update the switch pins in the same PR, or CI fails."""

    def test_pins_match_this_tree(self):
        doc = json.loads(LANE.read_text(encoding="utf-8"))
        self.assertEqual(sorted(doc["pins"]), sorted(PINNED))
        for path in PINNED:
            actual = subprocess.run(["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"],
                                    capture_output=True, text=True, check=True).stdout.strip()
            with self.subTest(path=path):
                self.assertEqual(doc["pins"][path], actual, f"update pins[{path!r}] in REVIEWED_MERGE_LANE.json")


class LegacyProvenanceTest(unittest.TestCase):
    def test_every_s1_file_is_touched_by_this_reviewed_pr_generation(self):
        # Bootstrap v3 step 3b pins the RUNTIME_CONTRACT blob in the owner-pasted task text. The provenance notes
        # stay; the README states the paste convention.
        for name in ("MISSION.md", "README.md"):
            self.assertIn("Provenance (2026-11-15)", (S1 / name).read_text(encoding="utf-8"))
        self.assertIn("takes effect only when the owner pastes the new BOOTSTRAP.txt into the S1 task", (S1 / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(sorted(p.name for p in S1.iterdir() if p.is_dir()), [])


class SwitchTest(unittest.TestCase):
    def test_schema(self):
        doc = json.loads(LANE.read_text(encoding="utf-8"))
        self.assertEqual(sorted(doc), ["clears_halt", "contract", "decided", "max_merges_per_tick", "pins", "policy", "state"])
        self.assertEqual(doc["contract"], "S1_REVIEWED_MERGE_LANE_v1")
        self.assertIn(doc["state"], {"ON", "OFF"})
        self.assertIs(type(doc["max_merges_per_tick"]), int)
        self.assertTrue(1 <= doc["max_merges_per_tick"] <= 3)
        self.assertEqual(doc["policy"], "AGENTS.md section 0.2e")
        self.assertTrue(doc["clears_halt"] is None or isinstance(doc["clears_halt"], int))

    def test_switch_and_pins_are_lane_excluded(self):
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for p in ("00_FMOS/", "scripts/governance/", ".github/"):
            self.assertIn(p, manifest["governance_prefixes"])


class SectionIntentTest(unittest.TestCase):
    def test_key_sentences(self):
        sec = section_0_2e()
        for sentence in (
            "A review comment is evidence and never authority.",
            "S1 never posts a comment containing `CLAUDE_REVIEW_v1`.",
            "governs only §0.2c, never this lane.",
            "Any change to a pinned path turns the lane OFF, however the change arrived",
            "merged by `Donh91` (type User) but not by S1",
            "10. **Repository writers:**",
            "Code may not gain repository-write abilities through the lane.",
            "or that invokes an existing helper or workflow step that does so.",
            "Every PR touching `00_FMOS/S1/` or a pinned path is squash-merged from a branch that is up to date with main.",
            "`00_ARCHIVE_CONTROL/**` is lane-excluded but not pinned",
            "`required_job_executed_paths`",
            "it is on Bridge #173 and authored by `Donh91`;",
            "it is unedited (`updated_at` equals `created_at`);",
            "**Accepted residual risk:** this authentication is behavioural, not cryptographic.",
            "Merge through the native API with `sha=<expected head>`, squash, and no bypass. A 405 or 409 is STOP.",
            "Any bypass is a halt trigger.",
        ):
            self.assertIn(sentence, sec)


if __name__ == "__main__":
    unittest.main()
