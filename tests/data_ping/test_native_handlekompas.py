import json
import tempfile
import unittest
from pathlib import Path

from scripts.data_ping.native_handlekompas import AUTHORITY, build, load_auto_state, write


class NativeHandlekompasTest(unittest.TestCase):
    def _packet(self, *, breadth=0.55, decision="PASS", blockers=None, sentiment_status="PASS", sentiment_class="CFGI_OK"):
        return {
            "contract": "AUTO_MARKET_STATE_PACKET_v1",
            "packet_generated_at_utc": "2026-09-08T20:00:00Z",
            "packet_sha256": "abc123",
            "source_snapshot": {"exact_commit_sha": "deadbeef"},
            "validation_status": "PASS",
            "decision_context_status": decision,
            "blockers": blockers or [],
            "optional_degraded_lanes": [],
            "normalized_state": {
                "live_market": {"ethbtc": 0.0317},
                "breadth": {"aggregate": {"advance_ratio": breadth}},
            },
            "source_health": {
                "sentiment": {"status": sentiment_status, "classification": sentiment_class},
                "hourly_market": {"status": "PASS", "classification": "OK"},
            },
        }

    def test_prepare_requires_healthy_state_and_supportive_breadth(self):
        packet = build(self._packet())
        self.assertEqual(packet["action"]["NOW"], "PREPARE")
        self.assertFalse(packet["authority"]["portfolio_execution"])
        self.assertFalse(packet["authority"]["market_threshold_change"])

    def test_weak_breadth_is_defensive_wait(self):
        packet = build(self._packet(breadth=0.29))
        self.assertEqual(packet["action"]["NOW"], "HOLD_DEFENSIVE_WAIT")

    def test_provider_quota_is_visible_not_market_evidence(self):
        packet = build(self._packet(sentiment_status="DEGRADED", sentiment_class="CFGI_HTTP_429_QUOTA_EXHAUSTED"))
        self.assertEqual(packet["BUDGET_HEALTH"]["status"], "DEGRADED")
        self.assertEqual(packet["DATA_HEALTH"]["provider_health"]["cfgi"]["issue_class"], "QUOTA_OR_RATE_LIMIT")
        self.assertFalse(packet["authority"]["portfolio_execution"])

    def test_unknown_exact_budget_is_explicit(self):
        packet = build(self._packet())
        self.assertEqual(packet["BUDGET_HEALTH"]["status"], "UNKNOWN_EXACT_SPEND_NO_EXHAUSTION_SIGNAL")
        self.assertFalse(packet["BUDGET_HEALTH"]["exact_monthly_spend_available"])

    def test_pointer_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = root / "04_MARKET_LEARNING/entry_signals/auto_market_state"
            out.mkdir(parents=True)
            packet_path = out / "packet.json"
            packet_path.write_text(json.dumps({"packet_sha256": "actual"}))
            (out / "LATEST.json").write_text(json.dumps({"packet_path": packet_path.relative_to(root).as_posix(), "packet_sha256": "expected"}))
            with self.assertRaisesRegex(ValueError, "POINTER_HASH_MISMATCH"):
                load_auto_state(root, Path("04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json"))

    def test_write_pointer_is_non_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "handlekompas"
            packet = build(self._packet())
            result = write(packet, root)
            pointer = json.loads((root / "LATEST.json").read_text())
            self.assertEqual(pointer["contract"], "NATIVE_HANDLEKOMPAS_LATEST_POINTER_v1")
            self.assertEqual(pointer["authority"], AUTHORITY)
            self.assertEqual(pointer["handlekompas_sha256"], result["sha256"])


if __name__ == "__main__":
    unittest.main()
