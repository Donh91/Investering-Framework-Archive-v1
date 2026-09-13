import json
from pathlib import Path
import tempfile
import unittest

from scripts.data_terminal import situation_room_daily_owner as owner


class AtExp004SituationRoomPersistenceTests(unittest.TestCase):
    @staticmethod
    def result(status, detection, run_id, event_id=None):
        events = []
        if event_id:
            events.append({
                "event_id": event_id,
                "event_family_id": "EVF_TEST",
                "title": event_id,
                "event_time_utc": "2026-01-01T00:00:00Z",
                "event_time_precision": "TIMESTAMP",
                "detection_time_utc": detection,
                "classification": "MARKET_RELEVANT",
                "catalyst_subtype": "TEST",
                "confidence": "HIGH_PRIMARY_SOURCE",
                "expected_duration": "HOURS_TO_DAYS",
                "affected_framework_lanes": ["TEST"],
                "verification_status": "PRIMARY_SOURCE_VERIFIED",
                "source_receipts": [],
                "causal_authority": "NONE",
            })
        return {
            "contract": owner.CONTRACT,
            "authority": owner.AUTHORITY,
            "run_id": run_id,
            "observation_date_utc": "2026-01-01",
            "detection_time_utc": detection,
            "run_status": status,
            "daily_result": "NO_NEW_MATERIAL_CATALYST" if status == "PASS" else "UNKNOWN_DUE_TO_SOURCE_FAILURE",
            "source_coverage": {"primary_pass": 5 if status == "PASS" else 1, "primary_total": 5, "receipts": []},
            "events": events,
            "unverified_discoveries": [],
            "current_unverified_discoveries": [],
            "unresolved_candidates": [],
            "market_reaction_observations": [],
            "market_reaction_separate_from_event": True,
            "shared_row_tournament_eligible": False,
            "retroactive_candidate_eligibility": False,
            "canonical_effect": False,
            "market_state_effect": False,
            "portfolio_effect": False,
            "situation_room_role": "DISCOVERY_ONLY",
        }

    @staticmethod
    def dated(root):
        return json.loads((root / "2026" / "01" / "2026-01-01.json").read_text())

    def test_first_degraded_observation_is_persisted_explicitly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            degraded = self.result("DEGRADED", "2026-01-01T01:00:00Z", "D1")
            self.assertTrue(owner.write_outputs(root, degraded))
            self.assertEqual(self.dated(root)["run_id"], "D1")
            self.assertEqual(self.dated(root)["run_status"], "DEGRADED")

    def test_same_attempt_finalization_may_fail_closed_without_being_treated_as_rerun(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            initial = self.result("PASS", "2026-01-01T01:00:00Z", "RUN1")
            final = self.result("DEGRADED", "2026-01-01T01:00:00Z", "RUN1")
            final["retrieval"] = {"strategy": "DETERMINISTIC_STATIC_DAILY_BRIEFING"}
            self.assertTrue(owner.write_outputs(root, initial))
            self.assertTrue(owner.write_outputs(root, final))
            stored = self.dated(root)
            self.assertEqual(stored["run_id"], "RUN1")
            self.assertEqual(stored["run_status"], "DEGRADED")
            self.assertEqual(stored["retrieval"]["strategy"], "DETERMINISTIC_STATIC_DAILY_BRIEFING")
            self.assertFalse((root / "SUPERSEDED_ATTEMPTS.jsonl").exists())

    def test_good_then_degraded_preserves_good_and_does_not_append_rejected_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = self.result("PASS", "2026-01-01T01:00:00Z", "G1", "EVT_GOOD")
            degraded = self.result("DEGRADED", "2026-01-01T02:00:00Z", "D2", "EVT_REJECTED")
            self.assertTrue(owner.write_outputs(root, good))
            before = (root / "2026" / "01" / "2026-01-01.json").read_bytes()
            self.assertFalse(owner.write_outputs(root, degraded))
            self.assertEqual((root / "2026" / "01" / "2026-01-01.json").read_bytes(), before)
            self.assertEqual(self.dated(root)["run_id"], "G1")
            ledger = (root / "EVENT_LEDGER.jsonl").read_text()
            self.assertIn("EVT_GOOD", ledger)
            self.assertNotIn("EVT_REJECTED", ledger)
            audit = (root / "SUPERSEDED_ATTEMPTS.jsonl").read_text()
            self.assertIn("LOWER_QUALITY_RERUN_REJECTED", audit)

    def test_degraded_then_good_upgrades(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertTrue(owner.write_outputs(root, self.result("DEGRADED", "2026-01-01T01:00:00Z", "D1")))
            self.assertTrue(owner.write_outputs(root, self.result("PASS", "2026-01-01T02:00:00Z", "G2")))
            self.assertEqual(self.dated(root)["run_id"], "G2")
            self.assertEqual(self.dated(root)["run_status"], "PASS")

    def test_equal_quality_later_valid_detection_time_wins(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertTrue(owner.write_outputs(root, self.result("PASS", "2026-01-01T01:00:00Z", "G1")))
            self.assertTrue(owner.write_outputs(root, self.result("PASS", "2026-01-01T02:00:00Z", "G2")))
            self.assertEqual(self.dated(root)["run_id"], "G2")

    def test_equal_quality_older_or_invalid_detection_time_loses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertTrue(owner.write_outputs(root, self.result("PASS", "2026-01-01T02:00:00Z", "G2")))
            self.assertFalse(owner.write_outputs(root, self.result("PASS", "2026-01-01T01:00:00Z", "G1")))
            self.assertFalse(owner.write_outputs(root, self.result("PASS", "not-a-time", "GBAD")))
            self.assertEqual(self.dated(root)["run_id"], "G2")

    def test_rejected_attempt_audit_is_deduplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = self.result("PASS", "2026-01-01T01:00:00Z", "G1")
            bad = self.result("DEGRADED", "2026-01-01T02:00:00Z", "D2")
            owner.write_outputs(root, good)
            owner.write_outputs(root, bad)
            owner.write_outputs(root, bad)
            lines = (root / "SUPERSEDED_ATTEMPTS.jsonl").read_text().splitlines()
            self.assertEqual(len(lines), 1)


if __name__ == "__main__":
    unittest.main()
