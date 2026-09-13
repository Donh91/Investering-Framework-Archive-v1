import json
from pathlib import Path
import tempfile
import unittest

from scripts.data_terminal import situation_room_daily_owner as owner


class AtExp004SituationRoomDonorAssertions(unittest.TestCase):
    @staticmethod
    def result(status: str, detection: str, run_id: str, event_id: str | None = None) -> dict:
        events = [] if event_id is None else [{"event_id": event_id}]
        return {
            "observation_date_utc": "2026-01-01",
            "detection_time_utc": detection,
            "run_status": status,
            "daily_result": "NO_NEW_MATERIAL_CATALYST" if status == "PASS" else "UNKNOWN_DUE_TO_SOURCE_FAILURE",
            "run_id": run_id,
            "events": events,
        }

    @staticmethod
    def dated(root: Path) -> dict:
        return json.loads((root / "2026" / "01" / "2026-01-01.json").read_text())

    def test_first_degraded_observation_is_persisted_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            degraded = self.result("DEGRADED", "2026-01-01T01:00:00Z", "D1")
            owner.write_outputs(root, degraded)
            saved = self.dated(root)
            self.assertEqual(saved["run_id"], "D1")
            self.assertEqual(saved["run_status"], "DEGRADED")

    def test_rejected_downgrade_audit_is_deduplicated_and_event_is_not_admitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = self.result("PASS", "2026-01-01T01:00:00Z", "G1", "EVT_GOOD")
            degraded = self.result("DEGRADED", "2026-01-01T02:00:00Z", "D2", "EVT_REJECTED")
            owner.write_outputs(root, good)
            owner.write_outputs(root, degraded)
            owner.write_outputs(root, degraded)

            self.assertEqual(self.dated(root)["run_id"], "G1")
            ledger = (root / "EVENT_LEDGER.jsonl").read_text()
            self.assertIn("EVT_GOOD", ledger)
            self.assertNotIn("EVT_REJECTED", ledger)
            receipts = list((root / "superseded").glob("*.json"))
            self.assertEqual(len(receipts), 1)


if __name__ == "__main__":
    unittest.main()
