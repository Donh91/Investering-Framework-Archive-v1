from __future__ import annotations

import json
import os
import subprocess

from tests.learning.test_action_compass_accountability import AccountabilityHarness, canonical, sha


class AcceptedDataPingActionCompassBindingTests(AccountabilityHarness):
    def test_native_accepted_packet_binds_exactly_once_to_action_compass(self):
        packet_path = self.repo / "research/data_ping_bridge/accepted/2026/W35/DPI-test.json"
        packet_path.parent.mkdir(parents=True, exist_ok=True)
        packet = {
            "contract": "ACCEPTED_DATA_PING_PACKET_v1",
            "snapshot_id": "DPI-test",
            "freeze_utc": "2026-08-26T14:00:00Z",
            "source_health": {"github": "PASS"},
            "market_metrics": {"btc_usd": 100.0},
            "framework_interpretation": "DEFERRED_TO_MAIN_FRAMEWORK",
            "acceptance_status": "ACCEPTED",
        }
        packet_path.write_bytes(canonical(packet))
        subprocess.run(["git", "add", str(packet_path.relative_to(self.repo))], cwd=self.repo, check=True)
        env = dict(os.environ, GIT_AUTHOR_DATE="2026-08-26T14:06:00Z", GIT_COMMITTER_DATE="2026-08-26T14:06:00Z")
        subprocess.run(["git", "commit", "-q", "-m", "accepted data ping"], cwd=self.repo, check=True, env=env)
        self.canonical_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        candidate = self.candidate(
            input_packet_sha256=sha(packet),
            input_binding_status="VERIFIED_REPO_FILE",
            input_contract="ACCEPTED_DATA_PING_PACKET_v1",
            source_reference=str(packet_path.relative_to(self.repo)),
            source_timestamp_utc=packet["freeze_utc"],
            canonical_commit_sha=self.canonical_sha,
        )
        first = self.persist(candidate)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(json.loads(first.stdout)["status"], "PERSISTED")
        receipt_path = self.receipt_path()
        receipt = json.loads(receipt_path.read_text())
        self.assertEqual(receipt["input_packet_sha256"], sha(packet))
        self.assertEqual(receipt["source_reference"], str(packet_path.relative_to(self.repo)))
        self.assertEqual(receipt["input_contract"], "ACCEPTED_DATA_PING_PACKET_v1")
        self.assertEqual(receipt["canonical_commit_sha"], self.canonical_sha)
        self.assertFalse(receipt["portfolio_execution"])

        original = receipt_path.read_bytes()
        replay = self.persist(candidate)
        self.assertEqual(replay.returncode, 0, replay.stderr)
        self.assertEqual(json.loads(replay.stdout)["status"], "DUPLICATE_NOOP")
        self.assertEqual(receipt_path.read_bytes(), original)
        self.assertEqual(len(list(self.receipts.rglob("*.json"))), 1)
