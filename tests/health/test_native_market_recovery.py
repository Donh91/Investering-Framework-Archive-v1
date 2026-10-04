import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.health.native_market_recovery import POLICY, apply_runtime_owner_freshness, decide, default_state, write


class NativeMarketRecoveryTest(unittest.TestCase):
    def auto(self, health):
        return {"packet_sha256":"abc","source_snapshot":{"exact_commit_sha":"deadbeef"},"source_health":health}

    def test_first_hourly_failure_dispatches_existing_owner(self):
        decision,state=decide(self.auto({"hourly_market":{"status":"DEGRADED","classification":"STALE"}}),default_state(),datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertIn("hourly-sequence-capture.yml",[row["workflow"] for row in decision["dispatches"]])
        self.assertEqual(state["lanes"]["hourly_market"]["consecutive_nonpass"],1)
        self.assertFalse(decision["manual_market_data_required"])

    def test_runtime_hourly_freshness_overrides_stale_auto_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=Path(tmp)
            pointer=repo/"03_DAILY_CAPTURE_LOGS/hourly/LATEST.json"
            pointer.parent.mkdir(parents=True)
            pointer.write_text(json.dumps({
                "retrieved_at_utc":"2026-09-08T18:00:00Z",
                "window_end_utc":"2026-09-08T18:00:00Z",
            }))
            auto=self.auto({"hourly_market":{"status":"PASS","classification":"GITHUB_POINTER_TARGET_CHAIN_VALID"}})
            out=apply_runtime_owner_freshness(repo,auto,datetime(2026,9,8,20,0,tzinfo=timezone.utc))
            row=out["source_health"]["hourly_market"]
            self.assertEqual(row["status"],"DEGRADED")
            self.assertEqual(row["classification"],"HOURLY_OWNER_STALE_AT_RECOVERY_CHECK")
            decision,_=decide(out,default_state(),datetime(2026,9,8,20,0,tzinfo=timezone.utc))
            self.assertIn("hourly-sequence-capture.yml",[item["workflow"] for item in decision["dispatches"]])

    def test_macro_risk_second_nonpass_dispatches_existing_live_anchor_owner(self):
        now=datetime(2026,9,8,20,0,tzinfo=timezone.utc)
        health={lane:{"status":"PASS","classification":"PASS"} for lane in POLICY}
        health["macro_risk"]={"status":"UNAVAILABLE","classification":"MACRO_OWNER_STALE"}
        _,state1=decide(
            self.auto(health),
            default_state(),
            now,
        )
        decision,_=decide(
            self.auto(health),
            state1,
            datetime(2026,9,8,21,0,tzinfo=timezone.utc),
        )
        rows=[row for row in decision["dispatches"] if row["workflow"]=="daily-raw-owner-capture.yml"]
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["lanes"],["macro_risk"])
        self.assertFalse(decision["authority"]["owner_switch"])

    def test_quota_suppresses_wasteful_retry(self):
        prior=default_state();prior["lanes"]["sentiment"]={"consecutive_nonpass":5,"last_dispatch_utc":None}
        decision,state=decide(self.auto({"sentiment":{"status":"DEGRADED","classification":"CFGI_HTTP_429_QUOTA_EXHAUSTED"}}),prior,datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertTrue(decision["suppressed_retries"])
        self.assertFalse(decision["dispatches"])
        self.assertTrue(state["lanes"]["sentiment"]["retry_suppressed_provider_limit"])

    def test_live_anchor_related_lanes_deduplicate(self):
        prior=default_state()
        shared=("live_anchor","sentiment","altseason_context","macro_risk")
        health={lane:{"status":"PASS","classification":"PASS"} for lane in POLICY}
        for lane in shared:
            prior["lanes"][lane]={"consecutive_nonpass":1,"last_dispatch_utc":None}
            health[lane]={"status":"DEGRADED","classification":"STALE"}
        decision,_=decide(self.auto(health),prior,datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        rows=[row for row in decision["dispatches"] if row["workflow"]=="daily-raw-owner-capture.yml"]
        self.assertEqual(len(rows),1)
        self.assertEqual(set(rows[0]["lanes"]),set(shared))

    def test_breadth_first_failure_uses_dedicated_checkpoint_owner(self):
        health={lane:{"status":"PASS","classification":"PASS"} for lane in POLICY}
        health["breadth"]={"status":"UNAVAILABLE","classification":"BREADTH_CONTRACT_UNAVAILABLE"}
        decision,_=decide(self.auto(health),default_state(),datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        rows=[row for row in decision["dispatches"] if row["workflow"]=="rich-breadth-checkpoint.yml"]
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["lanes"],["breadth"])

    def test_hourly_market_and_derivatives_deduplicate(self):
        prior=default_state()
        health={lane:{"status":"PASS","classification":"PASS"} for lane in POLICY}
        for lane in ("hourly_market","derivatives"):
            prior["lanes"][lane]={"consecutive_nonpass":1,"last_dispatch_utc":None}
            health[lane]={"status":"DEGRADED","classification":"STALE"}
        decision,_=decide(self.auto(health),prior,datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        rows=[row for row in decision["dispatches"] if row["workflow"]=="hourly-sequence-capture.yml"]
        self.assertEqual(len(rows),1)
        self.assertEqual(set(rows[0]["lanes"]),{"hourly_market","derivatives"})

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
