from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/data_terminal/verify_archived_run.py"
SPEC = importlib.util.spec_from_file_location("verify_archived_run", MODULE_PATH)
verifier = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(verifier)
ARCHIVE_DIR = ROOT / "02_DATA_PING/data_terminal/runtime/shadow/artifacts/2026-07-21"


class ArchivedReplayTests(unittest.TestCase):
    def test_archived_live_run_passes_all_replay_gates(self):
        report = verifier.verify_archive(ARCHIVE_DIR)
        self.assertEqual(report["overall_status"], "PASS")
        self.assertEqual(report["archive_part_count"], 8)
        self.assertEqual(report["archive_file_count"], 5)
        self.assertEqual(report["authority_block_count"], 9)
        self.assertEqual(report["unique_missing_row_count"], 719)
        self.assertEqual(report["missing_reference_count"], 2157)
        self.assertTrue(all(status == "PASS" for status in report["gates"].values()))

    def test_replay_report_preserves_shadow_only_authority(self):
        report = verifier.verify_archive(ARCHIVE_DIR)
        self.assertTrue(all(value is False for value in report["authority"].values()))
        self.assertEqual(report["edge_or_promotion_status"], "NOT_APPLICABLE")
        self.assertIn("SECOND_LIVE_REPEAT_REQUIRED", report["phase1_completion"])

    def test_replay_is_deterministic(self):
        first = verifier.verify_archive(ARCHIVE_DIR)
        second = verifier.verify_archive(ARCHIVE_DIR)
        self.assertEqual(verifier.canonical_json_bytes(first), verifier.canonical_json_bytes(second))

    def test_tampered_archive_part_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "archive"
            shutil.copytree(ARCHIVE_DIR, copied)
            part = copied / "data-terminal-shadow-29828218513.zip.b64.part-004"
            content = part.read_text(encoding="ascii")
            part.write_text(("A" if content[0] != "A" else "B") + content[1:], encoding="ascii")
            with self.assertRaises(verifier.ReplayVerificationError) as ctx:
                verifier.verify_archive(copied)
            self.assertIn("PART_SHA256_MISMATCH", str(ctx.exception))

    def test_receipt_hash_mutation_is_rejected(self):
        report = verifier.verify_archive(ARCHIVE_DIR)
        self.assertEqual(report["gates"]["receipt_hash"], "PASS")
        receipt = {"run_id": "X", "receipt_sha256": "0" * 64}
        with self.assertRaises(verifier.ReplayVerificationError):
            verifier.verify_receipt_hash(receipt)

    def test_authority_mutation_is_rejected(self):
        documents = {
            "bad": {
                "authority": {
                    "binding": True,
                    "canonical_acceptance": False,
                    "state_change": False,
                    "portfolio_action": False,
                }
            }
        }
        with self.assertRaises(verifier.ReplayVerificationError):
            verifier.verify_false_authority_blocks(documents)

    def test_cli_writes_machine_readable_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            result = subprocess.run(
                [sys.executable, str(MODULE_PATH), str(ARCHIVE_DIR), "--report-output", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["overall_status"], "PASS")
            self.assertEqual(report["artifact_sha256"], "ac3e2ad49f265b1cd9ae8b16d97051b875d90974ad7199cd7105143a9bd7cd89")


if __name__ == "__main__":
    unittest.main()
