"""S1 runtime contract: the saved task is a thin bootstrap; GitHub main holds the rules.

Any edit to 00_FMOS/S1/ACTION_LOOP.md without the matching action_loop_blob in
RUNTIME_CONTRACT.json fails CI, so S1 behaviour can only change deliberately
through a reviewed PR (00_FMOS/ is release-sensitive, never LOW).
"""
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S1 = ROOT / "00_FMOS" / "S1"
KEYS = ["contract", "task_id", "owner_issue", "schedule", "bootstrap_path",
        "bootstrap_version", "action_loop_path", "action_loop_blob", "tick_path", "tick_blob", "lane_switch_path", "lane_switch_blob", "rubric_blobs"]
RUBRICS = ["00_FMOS/S1/STEWARD_STATES.md", "00_FMOS/S1/REVIEW_ADMISSION.md", "00_FMOS/S1/OWNER_VISIBILITY.md",
           "00_FMOS/S1/DAILY_SUMMARY_BOOTSTRAP.txt", "00_FMOS/S1/EVIDENCE_BINDINGS.md", "00_FMOS/S1/EDGE_LEDGER.md"]
# Every file under 00_FMOS/S1/ is pinned (contract, bootstrap 3b or rubric_blobs) or is a legacy locator file.
PINNED_BY_CHAIN = {"ACTION_LOOP.md", "TICK.md", "BOOTSTRAP.txt", "RUNTIME_CONTRACT.json", "REVIEWED_MERGE_LANE.json"}
LEGACY = {"MISSION.md", "README.md", "OPERATING_MANIFEST.json"}


def _no_dupes(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate JSON key")
    return dict(pairs)


def _git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


class S1RuntimeContractTest(unittest.TestCase):
    def setUp(self):
        raw = (S1 / "RUNTIME_CONTRACT.json").read_text(encoding="utf-8")
        self.c = json.loads(raw, object_pairs_hook=_no_dupes)

    def test_exact_keys_and_identity(self):
        self.assertEqual(list(self.c), KEYS)
        self.assertEqual(self.c["contract"], "S1_RUNTIME_CONTRACT_v1")
        self.assertEqual(self.c["task_id"], "6ae5fd466b48819187abc224ec0f1c5f")
        self.assertEqual(self.c["owner_issue"], 1156)
        self.assertEqual(self.c["bootstrap_version"], "S1_BOOTSTRAP_v8")
        self.assertEqual(self.c["tick_path"], "00_FMOS/S1/TICK.md")
        self.assertEqual(self.c["bootstrap_path"], "00_FMOS/S1/BOOTSTRAP.txt")
        self.assertEqual(self.c["action_loop_path"], "00_FMOS/S1/ACTION_LOOP.md")

    def test_lane_switch_blob_pins_the_exact_bytes(self):
        # The lane switch (state, max merges, clears_halt and the content pins over AGENTS.md etc.) is S1 policy input:
        # it is pinned here, so a change needs a contract update, a BOOTSTRAP update and an owner paste.
        self.assertEqual(self.c["lane_switch_path"], "00_FMOS/S1/REVIEWED_MERGE_LANE.json")
        data = (ROOT / self.c["lane_switch_path"]).read_bytes()
        self.assertEqual(_git_blob(data), self.c["lane_switch_blob"],
                         "REVIEWED_MERGE_LANE.json changed without updating lane_switch_blob in RUNTIME_CONTRACT.json")
        boot = (ROOT / self.c["bootstrap_path"]).read_text(encoding="utf-8")
        self.assertIn("the Git blob SHA of the file at lane_switch_path must equal lane_switch_blob", boot)

    def test_bootstrap_pins_the_exact_contract_blob(self):
        # BOOTSTRAP v3 step 3b: the owner-pasted task text holds RUNTIME_CONTRACT.json's Git blob, so any contract or
        # ACTION_LOOP change without a matching BOOTSTRAP update (and an owner paste) fails CI here.
        data = (S1 / "RUNTIME_CONTRACT.json").read_bytes()
        boot = (ROOT / self.c["bootstrap_path"]).read_text(encoding="utf-8")
        self.assertIn(f"RUNTIME_CONTRACT.json at that same main SHA (as GitHub reports it) must equal {_git_blob(data)}.", boot,
                      "update the RUNTIME_CONTRACT blob in BOOTSTRAP.txt step 3b")

    def test_rubric_blobs_pin_the_exact_bytes(self):
        self.assertEqual(list(self.c["rubric_blobs"]), RUBRICS)
        for path, blob in self.c["rubric_blobs"].items():
            with self.subTest(path=path):
                self.assertEqual(_git_blob((ROOT / path).read_bytes()), blob, f"{path} changed without updating rubric_blobs")
        boot = (ROOT / self.c["bootstrap_path"]).read_text(encoding="utf-8")
        self.assertIn("every rubric_blobs path must have its listed blob", boot)
        # v6 (v3.1): the rubric files are verified by blob from ONE directory listing; their text is read only where
        # TICK.md names it. v5 read every rubric file in full before the first decision (about 120 KB).
        self.assertIn("list the directory 00_FMOS/S1", boot)
        self.assertIn("each entry's sha is that file's Git blob SHA", boot)
        self.assertIn("Read no other file yet.", boot)
        self.assertNotIn("every path in its rubric_blobs", boot)

    def test_every_s1_file_is_pinned(self):
        names = {p.name for p in S1.iterdir()}
        rubric_names = {Path(p).name for p in self.c["rubric_blobs"]}
        self.assertEqual(names - PINNED_BY_CHAIN - LEGACY - rubric_names, set(), "pin every new 00_FMOS/S1/ file in rubric_blobs")

    def test_daily_summary_bootstrap_is_thin_and_read_only(self):
        text = (S1 / "DAILY_SUMMARY_BOOTSTRAP.txt").read_text(encoding="utf-8")
        self.assertLessEqual(len(text), 1500)
        for needle in ("Daily at 20:40 Europe/Copenhagen", "Read-only except one comment on Archive issue #1156",
                       "must equal its entry in rubric_blobs of RUNTIME_CONTRACT.json", "write nothing",
                       "follow the DAILY SUMMARY section of OWNER_VISIBILITY.md exactly",
                       "Never merge, close, label, dispatch, review or post anything else"):
            self.assertIn(needle, text)

    def test_task_id_matches_shadow_locator(self):
        shadow = json.loads((S1 / "OPERATING_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(shadow["task_id"], self.c["task_id"])

    def test_action_loop_blob_pins_the_exact_bytes(self):
        data = (ROOT / self.c["action_loop_path"]).read_bytes()
        self.assertEqual(_git_blob(data), self.c["action_loop_blob"],
                         "ACTION_LOOP.md changed without updating RUNTIME_CONTRACT.json")

    def test_tick_blob_pins_the_exact_bytes(self):
        data = (ROOT / self.c["tick_path"]).read_bytes()
        self.assertEqual(_git_blob(data), self.c["tick_blob"], "TICK.md changed without updating RUNTIME_CONTRACT.json")
        boot = (ROOT / self.c["bootstrap_path"]).read_text(encoding="utf-8")
        self.assertIn("that of TICK.md must equal tick_blob", boot)
        self.assertIn("4. Otherwise execute 00_FMOS/S1/TICK.md exactly.", boot)
        self.assertIn("read ACTION_LOOP.md or a rubric file only where TICK.md names it", boot)

    def test_bootstrap_is_thin_and_points_only_to_github(self):
        boot = (ROOT / self.c["bootstrap_path"]).read_text(encoding="utf-8")
        # v5 (first live v2.2 tick, 2026-11-17: the step-1 fetch was routed into a code sandbox with no network and
        # the run ended SOURCE_UNVERIFIED): step 1 names the tools. The text grew by one sentence, so the cap is 1750.
        # v6: step 2 names the directory listing (one more URL of the same repository). Cap 2100.
        # v8 rev 2026-11-19 (S1_STEP1_PROBE_v1: web.run DisabledError, connector fetch returns current main in <1 s;
        # one run used a 3 h stale SHA): steps 1-2 name the connector, forbid web fetch, and bind M to this run's fetch.
        # No commit-age stop (S1_SELF_DIAGNOSIS_V1 7008602091: a quiet main would deadlock; an older M is caught by T3
        # main_not_ahead against a fresh brief and by F6's re-read of main before any merge).
        # Same rev, S1_T1T2_PROBE_v1: the connector's issue list returns user {"login": "github-actions"} without type and
        # id, so T1's author check can never pass on it (BRIEF_INCOMPLETE(T1:brief_not_verified)); the connector's fetch of
        # the raw REST URLs returns every field T1 and T2 check. Step 4 binds every fetch of TICK.md to it. Cap 2800.
        # Same rev, ticks 2026-11-19 19:45Z-21:45Z (BRIEF_UNVERIFIED(body) three times): S1 read "that block is one JSON
        # object B" in TICK.md T1 literally and rejected the ```json fence that render() always writes and parse_body()
        # always strips. Step 4 states the fence is the published format. Bootstrap-only: no contract, TICK or pin change.
        self.assertLessEqual(len(boot), 2800)
        self.assertIn("In T1 the block between the two markers is one ```json fenced code block: B is the JSON object between its opening ```json line and its closing ``` line; that fence is the published format, never a body failure.", boot)
        self.assertNotIn("committer.date", boot)
        self.assertNotIn("3stale", boot)
        for needle in ("Read no other file yet.", "that of TICK.md must equal tick_blob", "list the directory 00_FMOS/S1",
                       "with the GitHub connector's fetch (mcp__GitHub__fetch) of https://api.github.com/repos/Donh91/Investering-Framework-Archive-v1/branches/main",
                       "Web fetch (web.run) is disabled for this host: do not use it.",
                       "NEVER the Python or code sandbox (it has no network)",
                       "If the connector returns no SHA: SOURCE_UNVERIFIED(3).", "(never a search result)", "M is the SHA that this fetch returned in this run, never a remembered or cached SHA",
                       'Tool binding: every "fetch <URL>" and "fetch API/..." in TICK.md and ACTION_LOOP.md is the connector\'s fetch (mcp__GitHub__fetch) of that exact URL',
                       "T1 and T2 use only that fetch, never an issue list, issue search or workflow-run tool"):
            self.assertIn(needle, boot)
        self.assertEqual(boot.count("api.github.com"), 2, "main, and the 00_FMOS/S1 listing at that SHA; no other URL")
        self.assertEqual(boot.count("https://api.github.com/repos/Donh91/Investering-Framework-Archive-v1/"), 2)
        for needle in ("S1 BOOTSTRAP v8", "00_FMOS/S1/RUNTIME_CONTRACT.json", "bootstrap_version must be S1_BOOTSTRAP_v8",
                       "00_FMOS/S1/TICK.md", "ACTION_LOOP.md", "SOURCE_UNVERIFIED", "only instruction set"):
            self.assertIn(needle, boot)
        for forbidden in ("LADDER", "MERGE", "HARD STOPS", "owner-present"):
            self.assertNotIn(forbidden, boot)

    def test_action_loop_keeps_hard_stops_and_observability(self):
        loop = (ROOT / self.c["action_loop_path"]).read_text(encoding="utf-8")
        for needle in ("H1 Monday 09:30-10:30", "H2 No HIGH/EXTREME merge", "H3 Never enable live trading",
                       "H4 Never publish private-plane data", "H5 ", "H6 ", "H7 ", "H8 ",
                       "CHANGE CONTROL", "S1_PROMPT_DRIFT", "HEARTBEAT", "S1_HEARTBEAT_v1",
                       "contract=<first 8 of action_loop_blob>", "Never dispatch, rerun or pass inputs to any Vault workflow",
                       "CLAUDE_PROACTIVE_PREVIEW_v1", "ticks_24h=", "last_noop=",
                       "WAITING_ONLY_FOR_OWNER", "STEWARD_STATES.md", "REVIEW_ADMISSION.md", "OWNER_VISIBILITY.md",
                       "EVIDENCE_BINDINGS.md", "EDGE_LEDGER.md", "V3 EVIDENCE BINDINGS", "never a pass"):

            self.assertIn(needle, loop)

    def test_proactive_review_cannot_deadlock_rule_three(self):
        loop = (S1 / "ACTION_LOOP.md").read_text(encoding="utf-8")
        self.assertIn("Ignore ALL PROACTIVE receipts for rule-3 deduplication", loop)
        self.assertIn("prior exact-head S1_REVIEW_REQUEST_v1", loop)
        self.assertIn("never blocks rule 3", loop)

    def test_daily_heartbeat_not_suppressed_by_interactive_posts(self):
        loop = (S1 / "ACTION_LOOP.md").read_text(encoding="utf-8")
        self.assertIn("EVERY Copenhagen calendar day", loop)
        self.assertIn("regardless of ANY owner-interactive, RUN_NOW", loop)
        self.assertIn("Deduplicate only against today's prior S1_HEARTBEAT_v1", loop)
        self.assertIn("ticks_24h=UNKNOWN", loop)
        self.assertIn("last_noop", loop)

    def test_high_batch_requires_all_gates_and_owner_answer(self):
        loop = (S1 / "ACTION_LOOP.md").read_text(encoding="utf-8")
        # Detached review R1 P2-3: every gate of the v1.6.9 owner batch is required again.
        for token in ("HIGH EVIDENCE below all PASS", "native exact-head green required CI",
                      "zero unmitigated P0/P1 (H8)", "no CHANGES_REQUESTED on H",
                      "stating INDEPENDENT_DETACHED when H implements a Claude-authored package",
                      "WAITING_ONLY_FOR_OWNER", "S1 still never merges an OWNER_GATED PR",
                      "is HIGH_IMPACT BLOCKED with its first missing gate, never WAITING_ONLY_FOR_OWNER"):
            self.assertIn(token, loop)
        self.assertNotIn("high_evidence=PASS or HOLD", loop)
        vis = (S1 / "OWNER_VISIBILITY.md").read_text(encoding="utf-8")
        for token in ("high_evidence=PASS, and the owner action", "Never repost an identical set", "An entry is never release authority"):
            self.assertIn(token, vis)
        self.assertNotIn("PASS or HOLD", vis)


    def test_recovery_requires_bound_restore_evidence_and_bot(self):
        loop = (S1 / "ACTION_LOOP.md").read_text(encoding="utf-8")
        for token in ("newest VAULT_FINAL_REF_RECEIPT_v1", "user type Bot",
                      "performed_via_github_app.slug framework-vault-receipts", "user id 356654356",
                      "unedited (updated_at equals created_at)",
                      "restore drill PASS", "source_tree_sha must equal",
                      "release_permission=false does not itself prove",
                      "Until the App's first VAULT_FINAL_REF_RECEIPT_v1 exists", "If any evidence or binding is missing, HOLD",
                      "comments by any other author are ignored", "Watchdog silence alone proves none of these",
                      "Any App-authored comment on #1593 edited within 30 h means HOLD"):
            self.assertIn(token, loop)


if __name__ == "__main__":
    unittest.main()
