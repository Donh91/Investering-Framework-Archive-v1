import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.data_ping.native_handlekompas import AUTHORITY, build, load_auto_state, write


class NativeHandlekompasTest(unittest.TestCase):
    def packet(self, *, breadth=0.55, decision="PASS", validation="PASS", blockers=None, entry_state="WAIT", sentiment_status="PASS", sentiment_class="CFGI_OK"):
        return {
            "contract": "AUTO_MARKET_STATE_PACKET_v1",
            "packet_generated_at_utc": "2026-09-08T20:00:00Z",
            "packet_sha256": "abc123",
            "source_snapshot": {"exact_commit_sha": "deadbeef"},
            "validation_status": validation,
            "decision_context_status": decision,
            "blockers": blockers or [],
            "optional_degraded_lanes": [],
            "normalized_state": {
                "live_market": {"ethbtc": 0.0317},
                "breadth": {"aggregate": {"advance_ratio": breadth}},
                "entry_signal_reference": {"state": entry_state},
            },
            "source_health": {
                "sentiment": {"status": sentiment_status, "classification": sentiment_class},
                "hourly_market": {"status": "PASS", "classification": "OK"},
            },
        }

    def test_prepare_requires_healthy_state_and_supportive_breadth(self):
        out = build(self.packet(), now=datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertEqual(out["action"]["NOW"], "PREPARE")
        self.assertFalse(out["authority"]["portfolio_execution"])
        self.assertFalse(out["manual_market_data_required"])

    def test_existing_entry_signal_can_surface_graduated_topup(self):
        out = build(self.packet(entry_state="GRADUATED_ALTCOIN_TOPUP_ACTIVE"))
        self.assertEqual(out["action"]["NOW"], "GRADUATED_TOPUP_ACTIVE")
        self.assertIn("ONLY_EXISTING_ENTRY_SIGNAL", out["action"]["TOPUP_GATE"])

    def test_weak_breadth_is_defensive_wait(self):
        out = build(self.packet(breadth=0.29))
        self.assertEqual(out["action"]["NOW"], "HOLD_DEFENSIVE_WAIT")

    def test_degraded_state_cannot_be_prepare(self):
        out = build(self.packet(decision="DEGRADED", blockers=["hourly_market"]))
        self.assertEqual(out["action"]["NOW"], "HOLD_WAIT_DATA_DEGRADED")

    def test_cfgi_quota_is_visible_and_budget_degraded(self):
        out = build(self.packet(sentiment_status="DEGRADED", sentiment_class="CFGI_HTTP_429_QUOTA_EXHAUSTED"))
        self.assertEqual(out["DATA_HEALTH"]["provider_health"]["cfgi"]["issue_class"], "QUOTA_OR_RATE_LIMIT")
        self.assertEqual(out["BUDGET_HEALTH"]["status"], "DEGRADED")

    def test_external_budget_can_bind_without_invention(self):
        budget={"status":"OK","month_to_date_spend":12.5,"remaining_monthly_budget":17.5}
        out=build(self.packet(),external_budget=budget)
        self.assertEqual(out["BUDGET_HEALTH"]["status"],"OK")
        self.assertTrue(out["BUDGET_HEALTH"]["exact_monthly_spend_available"])
        self.assertEqual(out["BUDGET_HEALTH"]["remaining_monthly_budget"],17.5)

    def test_unknown_exact_budget_is_explicit(self):
        out=build(self.packet())
        self.assertEqual(out["BUDGET_HEALTH"]["status"],"UNKNOWN_EXACT_SPEND_NO_EXHAUSTION_SIGNAL")
        self.assertFalse(out["BUDGET_HEALTH"]["exact_monthly_spend_available"])

    def test_pointer_hash_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            state=root/"04_MARKET_LEARNING/entry_signals/auto_market_state"
            state.mkdir(parents=True)
            packet_path=state/"packet.json"
            packet_path.write_text(json.dumps({"packet_sha256":"actual"}))
            (state/"LATEST.json").write_text(json.dumps({"packet_path":packet_path.relative_to(root).as_posix(),"packet_sha256":"expected"}))
            with self.assertRaisesRegex(ValueError,"POINTER_HASH_MISMATCH"):
                load_auto_state(root,Path("04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json"))

    def test_write_pointer_is_non_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd=Path.cwd()
            try:
                # Use a relative output root so durable pointer semantics match production.
                root=Path(tmp)
                packet=build(self.packet())
                result=write(packet,root)
                pointer=json.loads((root/"LATEST.json").read_text())
                self.assertEqual(pointer["contract"],"NATIVE_HANDLEKOMPAS_LATEST_POINTER_v1")
                self.assertEqual(pointer["authority"],AUTHORITY)
                self.assertEqual(pointer["handlekompas_sha256"],result["sha256"])
            finally:
                _=cwd


if __name__=="__main__":
    unittest.main()
