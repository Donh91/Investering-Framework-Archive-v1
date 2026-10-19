"""Adversarial budget-advisory tests. No GitHub/API, Work or Codex runs."""
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.framework_intelligence.resource_budget_guard_v1 import (
    POLICY, assess, strict_read, utc,
)

T = datetime(2026, 10, 19, 8, 45, tzinfo=timezone.utc)
POL = {
    "contract": "RESOURCE_CONSERVATION_OWNER_POLICY_v1",
    "codex_cloud_default": "DISABLED_PASSIVE",
    "automatic_spend_authority": False,
    "new_workflows_or_agent_schedules": False,
    "actions_critical_until_utc": "2026-11-01T00:00:00Z",
    "codex_cloud_critical_until_utc": "2026-10-25T00:00:00Z",
}


class ResourceBudgetGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        p = self.root / POLICY
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(POL))
        self.source = self.root / "private_billing_source.json"

    def snapshot(self, *, used=2700, total=3000, codex=29, as_of="2026-10-19T08:30:00Z",
                 source_type="OWNER_SCREENSHOT"):
        self.source.write_text(json.dumps({
            "contract": "RESOURCE_USAGE_SNAPSHOT_v1",
            "as_of_utc": as_of,
            "source_type": source_type,
            "github_actions": {"used_minutes": used, "included_minutes": total},
            "codex": {"remaining_pct": codex},
        }))
        return self.source

    def test_owner_emergency_without_billing_stays_unverified(self):
        d = assess(self.root, now=T)
        self.assertEqual(d["status"], "CRITICAL")
        self.assertEqual(d["snapshot_status"], "MISSING")
        self.assertIsNone(d["github_actions"]["usage"])
        self.assertFalse(d["billing_hard_stop_verified"])
        self.assertEqual(d["codex_cloud"]["passive_execution"], "NOT_AUTHORIZED")

    def test_exact_owner_snapshot_critical_but_not_provider_verified(self):
        d = assess(self.root, now=T, snapshot=self.snapshot())
        self.assertEqual(d["status"], "CRITICAL")
        self.assertEqual(d["snapshot_status"], "CURRENT_OWNER_REPORTED")
        self.assertEqual(d["github_actions"]["usage"]["fraction_used"], .9)
        self.assertEqual(d["codex_cloud"]["remaining_pct"], 29)
        self.assertFalse(d["authority"]["automatic_dispatch"])

    def test_untrusted_local_direct_billing_claim_never_authenticates_itself(self):
        d = assess(self.root, now=T, snapshot=self.snapshot(source_type="GITHUB_BILLING_DIRECT"))
        self.assertEqual(d["snapshot_status"], "UNAUTHENTICATED_BILLING_CLAIM")
        self.assertIsNone(d["github_actions"]["usage"])
        self.assertIsNone(d["codex_cloud"]["remaining_pct"])
        self.assertFalse(d["billing_hard_stop_verified"])

    def test_durable_readback_covers_resource_advisory(self):
        repo = Path(__file__).resolve().parents[2]
        workflow = (repo / ".github/workflows/framework-learning-supervisor.yml").read_text()
        readback = workflow.split("Commit learning products with bounded retry and main readback", 1)[1]
        readback = readback.split("git show origin/main:", 1)[0]
        self.assertIn("research/framework_learning/resource_budget/LATEST.json", readback)
        self.assertIn("research/framework_learning/strategist/LATEST.json", readback)

    def test_stale_claim_does_not_become_current_usage(self):
        d = assess(self.root, now=T, snapshot=self.snapshot(as_of="2026-10-16T00:00:00Z"))
        self.assertEqual(d["snapshot_status"], "STALE_OR_FUTURE")
        self.assertIsNone(d["github_actions"]["usage"])

    def test_unknown_after_reset_not_green(self):
        t = datetime(2026, 11, 2, tzinfo=timezone.utc)
        d = assess(self.root, now=t)
        self.assertEqual(d["status"], "UNKNOWN")
        self.assertEqual(d["codex_cloud"]["status"], "UNKNOWN")
        self.assertEqual(d["github_actions"]["status"], "UNKNOWN")

    def test_boolean_or_invalid_values_do_not_admit(self):
        d = assess(self.root, now=T, snapshot=self.snapshot(used=True))
        self.assertEqual(d["snapshot_status"], "INVALID_VALUES")
        self.assertIsNone(d["github_actions"]["usage"])

    def test_nonfinite_input_fails_closed(self):
        p = self.snapshot()
        p.write_text(p.read_text().replace("2700", "NaN"))
        d = assess(self.root, now=T, snapshot=p)
        self.assertEqual(d["snapshot_status"], "INVALID_OR_UNREADABLE")

    def test_out_of_root_snapshot_refused(self):
        with tempfile.TemporaryDirectory() as out:
            p = Path(out) / "snapshot.json"
            p.write_text("{}")
            d = assess(self.root, now=T, snapshot=p)
            self.assertEqual(d["snapshot_status"], "INVALID_OR_UNREADABLE")

    def test_model_or_money_authority_change_is_rejected(self):
        p = self.root / POLICY
        x = json.loads(p.read_text())
        x["automatic_spend_authority"] = True
        p.write_text(json.dumps(x))
        with self.assertRaisesRegex(ValueError, "AUTHORITY_BOUNDARY_BROKEN"):
            assess(self.root, now=T)

    def test_valid_snapshot_normal_after_emergency_expires(self):
        t = datetime(2026, 11, 2, tzinfo=timezone.utc)
        p = self.snapshot(used=100, total=3000, codex=95, as_of="2026-11-02T00:00:00Z")
        d = assess(self.root, now=t, snapshot=p)
        self.assertEqual(d["status"], "NORMAL")

    def test_utc_enforced(self):
        with self.assertRaises(ValueError):
            utc("2026-10-19T08:00:00+02:00")


if __name__ == "__main__":
    unittest.main()
