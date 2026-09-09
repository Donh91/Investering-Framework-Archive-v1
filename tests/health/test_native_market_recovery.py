import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.health.native_market_recovery import decide, default_state, write


class NativeMarketRecoveryTest(unittest.TestCase):
    def auto(self, health):
        return {"packet_sha256":"abc","source_snapshot":{"exact_commit_sha":"deadbeef"},"source_health":health}

    def test_first_failure_waits(self):
        decision,state=decide(self.auto({"hourly_market":{"status":"DEGRADED","classification":"STALE"}}),default_state(),datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertEqual(decision["dispatches"],[])
        self.assertEqual(state["lanes"]["hourly_market"]["consecutive_nonpass"],1)

    def test_second_failure_dispatches_existing_owner(self):
        now=datetime(2026,9,8,20,0,tzinfo=timezone.utc)
        _,state1=decide(self.auto({"hourly_market":{"status":"DEGRADED","classification":"STALE"}}),default_state(),now)
        decision,_=decide(self.auto({"hourly_market":{"status":"DEGRADED","classification":"STALE"}}),state1,datetime(2026,9,8,21,0,tzinfo=timezone.utc))
        self.assertIn("hourly-sequence-capture.yml",[row["workflow"] for row in decision["dispatches"]])
        self.assertFalse(decision["manual_market_data_required"])

    def test_quota_suppresses_wasteful_retry(self):
        prior=default_state();prior["lanes"]["sentiment"]={"consecutive_nonpass":5,"last_dispatch_utc":None}
        decision,state=decide(self.auto({"sentiment":{"status":"DEGRADED","classification":"CFGI_HTTP_429_QUOTA_EXHAUSTED"}}),prior,datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertTrue(decision["suppressed_retries"])
        self.assertFalse(decision["dispatches"])
        self.assertTrue(state["lanes"]["sentiment"]["retry_suppressed_provider_limit"])

    def test_live_anchor_related_lanes_deduplicate(self):
        prior=default_state()
        for lane in ("live_anchor","breadth","sentiment"):
            prior["lanes"][lane]={"consecutive_nonpass":1,"last_dispatch_utc":None}
        health={lane:{"status":"DEGRADED","classification":"STALE"} for lane in ("live_anchor","breadth","sentiment")}
        decision,_=decide(self.auto(health),prior,datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        rows=[row for row in decision["dispatches"] if row["workflow"]=="daily-raw-owner-capture.yml"]
        self.assertEqual(len(rows),1)
        self.assertEqual(set(rows[0]["lanes"]),{"live_anchor","breadth","sentiment"})

    def test_durable_pointer_is_repo_relative(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            decision,state=decide(self.auto({}),default_state(),datetime(2026,9,8,20,0,tzinfo=timezone.utc))
            paths=write(repo,decision,state,Path("09_SOURCE_QA/native_market_recovery/STATE.json"),Path("09_SOURCE_QA/native_market_recovery/decisions"))
            latest=json.loads((repo/"09_SOURCE_QA/native_market_recovery/LATEST.json").read_text())
            self.assertFalse(Path(latest["decision_path"]).is_absolute())
            self.assertEqual(latest["decision_path"],paths["decision_path"])

    def test_authority_non_binding(self):
        decision,_=decide(self.auto({}),default_state(),datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertFalse(decision["authority"]["portfolio_action"])
        self.assertFalse(decision["authority"]["market_threshold_change"])
        self.assertFalse(decision["authority"]["owner_switch"])


if __name__=="__main__":
    unittest.main()
