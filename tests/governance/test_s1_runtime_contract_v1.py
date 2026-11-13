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
        "bootstrap_version", "action_loop_path", "action_loop_blob"]


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
        self.assertEqual(self.c["bootstrap_version"], "S1_BOOTSTRAP_v1")
        self.assertEqual(self.c["bootstrap_path"], "00_FMOS/S1/BOOTSTRAP.txt")
        self.assertEqual(self.c["action_loop_path"], "00_FMOS/S1/ACTION_LOOP.md")

    def test_task_id_matches_shadow_locator(self):
        shadow = json.loads((S1 / "OPERATING_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(shadow["task_id"], self.c["task_id"])

    def test_action_loop_blob_pins_the_exact_bytes(self):
        data = (ROOT / self.c["action_loop_path"]).read_bytes()
        self.assertEqual(_git_blob(data), self.c["action_loop_blob"],
                         "ACTION_LOOP.md changed without updating RUNTIME_CONTRACT.json")

    def test_bootstrap_is_thin_and_points_only_to_github(self):
        boot = (ROOT / self.c["bootstrap_path"]).read_text(encoding="utf-8")
        self.assertLessEqual(len(boot), 1500)
        for needle in ("S1 BOOTSTRAP v1", "00_FMOS/S1/RUNTIME_CONTRACT.json",
                       "00_FMOS/S1/ACTION_LOOP.md", "SOURCE_UNVERIFIED", "only instruction set"):
            self.assertIn(needle, boot)
        for forbidden in ("LADDER", "MERGE", "HARD STOPS", "owner-present"):
            self.assertNotIn(forbidden, boot)

    def test_action_loop_keeps_hard_stops_and_observability(self):
        loop = (ROOT / self.c["action_loop_path"]).read_text(encoding="utf-8")
        for needle in ("H1 Monday 09:30-10:30", "H2 No HIGH/EXTREME merge", "H3 Never enable live trading",
                       "H4 Never publish private-plane data", "H5 ", "H6 ", "H7 ", "H8 ",
                       "CHANGE CONTROL", "S1_PROMPT_DRIFT", "HEARTBEAT", "S1_HEARTBEAT_v1",
                       "contract=<first 8 of action_loop_blob>", "Never dispatch, rerun or pass inputs to any Vault workflow"):
            self.assertIn(needle, loop)


if __name__ == "__main__":
    unittest.main()
