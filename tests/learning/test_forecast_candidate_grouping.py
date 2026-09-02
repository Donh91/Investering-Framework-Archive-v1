from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))
sys.path.insert(0, str(ROOT / "scripts" / "learning"))

from forecast_candidate_grouping import classified_candidate_groups  # noqa: E402
from build_forecast_ratification_queue import build_queue  # noqa: E402
from process_forecast_ratifications import process  # noqa: E402

UTC = timezone.utc


def canon(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


class ForecastCandidateGroupingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.root, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=self.root, check=True)
        self.pending = self.root / "PENDING"
        self.terminals = self.root / "TERMINAL"
        self.packets = self.root / "PACKETS"
        self.frozen = self.root / "FROZEN"
        self.captures = self.root / "CAPTURES"
        for path in (self.pending, self.terminals, self.packets, self.frozen, self.captures):
            path.mkdir(parents=True, exist_ok=True)
        self.addCleanup(self.tmp.cleanup)

    def commit_current(self, message: str):
        subprocess.run(["git", "add", "-A"], cwd=self.root, check=True)
        subprocess.run(["git", "commit", "-qm", message], cwd=self.root, check=True)

    def candidate(self, cid: str, created: str, rationale: str = "legacy"):
        return {
            "contract": "FORECAST_CANDIDATE_v1",
            "candidate_id": cid,
            "created_at_utc": created,
            "ratification_status": "PENDING",
            "self_promotion_allowed": False,
            "candidate": {
                "metric_path": "spot.ETHUSDT.close",
                "direction": "DOWN",
                "target_mode": "PCT_MOVE",
                "threshold_pct": 1.0,
                "horizon_days": 1,
                "rationale": rationale,
            },
        }

    def write(self, relative: str, value: dict):
        path = self.pending / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canon(value))
        return path

    def test_divergent_pre_cutover_id_is_archive_only_not_owner_queue(self):
        cid = "legacy-dup"
        self.write("2026/08/03/legacy-dup.json", self.candidate(cid, "2026-08-03T22:40:23Z"))
        self.write("2026/08/04/legacy-dup.json", self.candidate(cid, "2026-08-04T22:43:39Z"))
        groups = classified_candidate_groups(self.pending)
        self.assertEqual(groups[cid]["classification"], "LEGACY_PRE_CUTOVER_DIVERGENT_DUPLICATE")
        queue = build_queue(self.pending, self.terminals, datetime(2026, 9, 2, 12, 0, tzinfo=UTC))
        self.assertEqual(queue["counts"]["legacy_divergent_duplicate_ids"], 1)
        self.assertEqual(queue["counts"]["decision_required"], 0)
        self.assertEqual(queue["candidates"], [])

    def test_processor_terminalizes_divergent_legacy_group_without_selecting_variant(self):
        cid = "legacy-dup-terminal"
        self.write("2026/08/03/legacy-dup-terminal.json", self.candidate(cid, "2026-08-03T22:40:23Z", "v1"))
        self.write("2026/08/04/legacy-dup-terminal.json", self.candidate(cid, "2026-08-04T22:43:39Z", "v2"))
        self.commit_current("record legacy candidates")
        result = process(
            self.pending,
            self.packets,
            self.terminals,
            self.frozen,
            self.captures,
            self.root,
            datetime(2026, 9, 2, 12, 0, tzinfo=UTC),
        )
        self.assertEqual(result["status"], "PASS")
        key = "LEGACY_PRE_CUTOVER_DIVERGENT_DUPLICATE_HINDSIGHT_INELIGIBLE"
        self.assertEqual(result["counts"][key], 1)
        terminal = json.loads((self.terminals / f"{cid}.json").read_text())
        self.assertEqual(terminal["disposition"], key)
        self.assertIsNone(terminal["candidate_sha256"])
        self.assertEqual(terminal["candidate_variant_count"], 2)
        self.assertFalse(terminal["ratification_allowed"])
        self.assertEqual(len({row["sha256"] for row in terminal["candidate_variants"]}), 2)
        self.assertEqual(list(self.frozen.glob("*.json")), [])

    def test_identical_pre_cutover_duplicate_is_archive_only(self):
        cid = "legacy-identical"
        value = self.candidate(cid, "2026-08-03T22:40:23Z")
        self.write("2026/08/03/legacy-identical.json", value)
        self.write("2026/08/04/legacy-identical.json", value)
        groups = classified_candidate_groups(self.pending)
        self.assertEqual(groups[cid]["classification"], "LEGACY_PRE_CUTOVER_IDENTICAL_DUPLICATE")
        queue = build_queue(self.pending, self.terminals, datetime(2026, 9, 2, 12, 0, tzinfo=UTC))
        self.assertEqual(queue["counts"]["legacy_identical_duplicate_ids"], 1)
        self.assertEqual(queue["candidates"], [])

    def test_any_post_cutover_multi_path_candidate_id_is_owner_ineligible_quarantine(self):
        cid = "post-dup"
        value = self.candidate(cid, "2026-09-02T10:10:00Z")
        self.write("2026/09/02/a/post-dup.json", value)
        self.write("2026/09/02/b/post-dup.json", value)
        with self.assertRaisesRegex(ValueError, "POST_CUTOVER_DUPLICATE_CANDIDATE_ID"):
            classified_candidate_groups(self.pending)
        queue = build_queue(self.pending, self.terminals, datetime(2026, 9, 2, 10, 20, tzinfo=UTC))
        self.assertEqual(queue["counts"]["post_cutover_duplicate_quarantine_ids"], 1)
        self.assertEqual(queue["counts"]["decision_required"], 0)
        self.assertEqual(queue["candidates"], [])
        self.assertEqual(queue["quarantines"][0]["candidate_id"], cid)
        self.assertFalse(queue["quarantines"][0]["owner_decision_allowed"])


if __name__ == "__main__":
    unittest.main()
