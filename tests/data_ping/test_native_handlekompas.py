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
                "hourly_market": {
                    "status": "PASS",
                    "classification": "OK",
                    "freshness": {
                        "status": "PASS",
                        "pointer_freshness": {"status": "PASS", "timestamp": "2026-09-08T20:00:00Z", "max_age_seconds": 10800},
                        "retrieval_freshness": {"status": "PASS", "timestamp": "2026-09-08T20:00:00Z", "max_age_seconds": 10800},
                        "session_coverage_freshness": {"status": "PASS", "timestamp": "2026-09-08T20:00:00Z", "max_age_seconds": 10800},
                        "source_observation_freshness": {"status": "PASS", "timestamp": "2026-09-08T20:00:00Z", "max_age_seconds": 10800},
                    },
                },
            },
        }

    def test_retired_breadth_and_ethbtc_cannot_create_prepare(self):
        out = build(self.packet(), now=datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertEqual(out["action"]["NOW"], "HOLD_WAIT")
        self.assertEqual(out["action"]["proxy_authority"]["top100_breadth_action_weight"], 0)
        self.assertEqual(out["action"]["proxy_authority"]["ethbtc_0_03_gate_action_weight"], 0)
        self.assertFalse(out["authority"]["portfolio_execution"])
        self.assertFalse(out["manual_market_data_required"])

    def test_legacy_entry_observer_cannot_reactivate_graduated_topup(self):
        out = build(
            self.packet(entry_state="GRADUATED_ALTCOIN_TOPUP_ACTIVE"),
            now=datetime(2026,9,8,20,0,tzinfo=timezone.utc),
        )
        self.assertEqual(out["action"]["NOW"], "HOLD_WAIT")
        self.assertFalse(out["action"]["proxy_authority"]["legacy_entry_observer_action_authority"])
        self.assertIn("RETIRED_BREADTH_ETHBTC_PROXY", out["action"]["TOPUP_GATE"])

    def test_weak_breadth_is_descriptive_not_defensive_action(self):
        out = build(self.packet(breadth=0.29), now=datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertEqual(out["action"]["NOW"], "HOLD_WAIT")
        self.assertIn("DESCRIPTIVE_TOP100_BREADTH=0.29", out["action"]["WHY"])

    def test_stale_owner_fails_native_action_closed(self):
        out = build(self.packet(), now=datetime(2026,9,9,4,0,tzinfo=timezone.utc))
        self.assertEqual(out["action"]["NOW"], "HOLD_WAIT_DATA_DEGRADED")
        self.assertEqual(out["DATA_HEALTH"]["status"], "DEGRADED")
        self.assertEqual(out["DATA_HEALTH"]["owner_freshness"]["status"], "STALE_OR_UNAVAILABLE")

    def test_degraded_state_cannot_be_prepare(self):
        out = build(self.packet(decision="DEGRADED", blockers=["hourly_market"]), now=datetime(2026,9,8,20,0,tzinfo=timezone.utc))
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

    def test_bound_cfgi_credit_exhaustion_is_visible_without_claiming_monthly_spend(self):
        budget={
            "contract":"PROVIDER_BUDGET_STATUS_v1",
            "status":"DEGRADED",
            "scope":"PROVIDER_CREDITS_ONLY_NOT_ACCOUNT_MONTHLY_SPEND",
            "providers":{
                "CFGI":{
                    "status":"EXHAUSTED",
                    "reason":"CFGI_CREDITS_REMAINING_ZERO",
                    "credits_remaining":0,
                    "current_standard_call_expected_credits":30,
                }
            },
        }
        out=build(self.packet(),external_budget=budget)
        self.assertEqual(out["BUDGET_HEALTH"]["status"],"DEGRADED")
        self.assertEqual(out["BUDGET_HEALTH"]["providers"]["CFGI"]["credits_remaining"],0)
        self.assertEqual(out["BUDGET_HEALTH"]["provider_signals"][0]["provider"],"CFGI")
        self.assertFalse(out["BUDGET_HEALTH"]["exact_monthly_spend_available"])

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
