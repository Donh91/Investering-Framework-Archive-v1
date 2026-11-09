"""Safety and prospectivity checks for KIL v1. Execute in existing Compass PR gate."""
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.learning.kompas_interpretation_learning_v1 import (
    CONTRACT, OUTPUT, canonical, digest, evaluate_one, evaluate_path,
    read_obj, register_latest, registration_path, report, report_path, run, utc,
)

T0 = datetime(2026, 11, 10, 12, tzinfo=timezone.utc)


class KILResearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.activated = T0 - timedelta(hours=4)
        self.day = T0.strftime("%Y-%m-%d")
        self.cid = "CMP-20261110-test1234"
        self.rel = f"04_MARKET_LEARNING/handlekompas/official/daily/2026/11/10/{self.cid}.json"
        self.issue = T0 - timedelta(minutes=30)
        original = {
            "contract": "OFFICIAL_DAILY_COMPASS_v1", "compass_id": self.cid,
            "issued_at_utc": self.issue.isoformat().replace("+00:00", "Z"),
            "decision_policy_version": "TEST_V4_1", "data_status": "OK",
            "action_now": "HOLD_WAIT",
            "market_reference": {"observation_open_utc": "2026-11-10T11:00:00Z"},
            "horizons": {"NEXT_12H": {"semantics": "OBSERVED_MOMENTUM_NOT_FORECAST", "expected_direction": "UP"},
                         "NEXT_1_3D": {"expected_direction": "DOWN", "action_posture": "WAIT",
                                       "expected_path": "Downward retest", "eta": "24-72h"}},
        }
        original["compass_sha256"] = digest(original)
        self.original = original
        self.write(self.rel, original)
        self.write("04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json", {
            "contract": "OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1",
            "compass_id": self.cid, "compass_path": self.rel,
            "compass_sha256": original["compass_sha256"], "issued_at_utc": original["issued_at_utc"],
        })

    def write(self, path, value):
        full = self.root / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_bytes(canonical(value))
        return full

    def patch_git(self):
        from unittest.mock import patch
        return patch("scripts.learning.kompas_interpretation_learning_v1.git_first_added",
                     return_value=("a" * 40, self.issue + timedelta(minutes=1)))

    def register(self):
        with self.patch_git():
            return register_latest(self.root, T0, self.activated, dry_run=False)

    def test_register_once_frozen_original_and_no_chat_claim(self):
        self.assertEqual(self.register(), "REGISTERED")
        p = self.root / registration_path(self.day)
        before = p.read_bytes()
        self.assertEqual(self.register(), "ALREADY_REGISTERED")
        self.assertEqual(before, p.read_bytes())
        reg = read_obj(p)
        self.assertEqual(reg["original_compass_id"], self.cid)
        self.assertEqual(reg["official_72h_direction"], "DOWN")
        self.assertEqual(reg["chat_analyst_interpretation"], "NOT_CAPTURED_NOT_SCORED")
        self.assertNotIn("NEXT_12H", json.dumps(reg))
        self.assertEqual(reg["authority"]["automatic_promotion"], False)

    def test_dry_run_never_writes_and_stale_or_pre_activation_rejected(self):
        with self.patch_git():
            self.assertEqual(register_latest(self.root, T0, self.activated, dry_run=True), "WOULD_REGISTER")
            self.assertEqual(register_latest(self.root, T0 + timedelta(hours=7), self.activated, dry_run=False), "NOT_PROSPECTIVE_ELIGIBLE")
            self.assertEqual(register_latest(self.root, T0, T0, dry_run=False), "NOT_PROSPECTIVE_ELIGIBLE")
        self.assertFalse((self.root / OUTPUT).exists())

    def test_mutated_source_pointer_and_hash_fail_closed(self):
        self.original["horizons"]["NEXT_1_3D"]["expected_direction"] = "UP"
        self.write(self.rel, self.original)
        with self.patch_git():
            self.assertEqual(register_latest(self.root, T0, self.activated, dry_run=False), "SOURCE_HASH_INVALID")
        self.assertFalse((self.root / OUTPUT).exists())

    def test_72h_maturity_and_tamper_guards(self):
        self.assertEqual(self.register(), "REGISTERED")
        p = self.root / registration_path(self.day)
        self.assertEqual(evaluate_one(self.root, p, T0, dry_run=False), "PENDING_72H")
        end = datetime(2026, 11, 13, 11, tzinfo=timezone.utc)
        maturity = end + timedelta(minutes=20)
        out = {
            "contract": "OFFICIAL_DAILY_COMPASS_OUTCOME_v1",
            "compass_id": self.cid,
            "compass_sha256": self.original["compass_sha256"], "horizon": "72h",
            "scoring_contract": "OFFICIAL_DAILY_COMPASS_SCORING_v3",
            "target_at_utc": "2026-11-13T11:00:00Z",
            "target_source_window_end_utc": "2026-11-13T11:00:00Z",
            "matured_at_utc": "2026-11-13T11:20:00Z",
            "time_basis": {"status": "PASS"},
            "direction_accuracy": {"btc": {"result": "CORRECT", "correct": True},
                                   "eth": {"result": "INCORRECT", "correct": False}},
            "realized": {"btc_return_pct": -2.0, "eth_return_pct": 1.0},
            "action_utility": {"status": "PROXY_ONLY"},
        }
        out["outcome_sha256"] = digest(out)
        source = f"04_MARKET_LEARNING/handlekompas/official/outcomes/2026/11/10/{self.cid}_72h.json"
        self.write(source, out)
        out["matured_at_utc"] = "2026-11-13T10:00:00Z"
        out["outcome_sha256"] = digest(out)
        self.write(source, out)
        self.assertEqual(evaluate_one(self.root, p, maturity, dry_run=False), "OUTCOME_CLOCK_INVALID")
        out["matured_at_utc"] = "2026-11-13T11:20:00Z"
        out["outcome_sha256"] = digest(out)
        self.write(source, out)
        self.assertEqual(evaluate_one(self.root, p, maturity, dry_run=True), "WOULD_EVALUATE")
        self.assertEqual(evaluate_one(self.root, p, maturity, dry_run=False), "EVALUATED")
        self.assertEqual(evaluate_one(self.root, p, maturity + timedelta(minutes=1), dry_run=False), "ALREADY_EVALUATED")
        review = read_obj(self.root / evaluate_path(self.day))
        self.assertEqual(review["analyst_interpretation_verdict"], "NOT_EVALUABLE_NO_PROSPECTIVE_CHAT_RECEIPT")
        self.assertEqual(review["economic_edge"], "NOT_PROVEN_FROM_PROXY_ACTION_UTILITY")

    def test_report_due_only_three_day_no_automatic_promotion(self):
        # No fabricated hits when zero outcomes exist.
        activation = datetime(2026, 11, 9, 12, tzinfo=timezone.utc)
        not_due = datetime(2026, 11, 11, 14, tzinfo=timezone.utc)
        self.assertEqual(report(self.root, not_due, activation, dry_run=False), "REPORT_NOT_DUE")
        due = datetime(2026, 11, 12, 14, tzinfo=timezone.utc)
        self.assertEqual(report(self.root, due, activation, dry_run=True), "WOULD_REPORT")
        self.assertEqual(report(self.root, due, activation, dry_run=False), "REPORTED")
        self.assertEqual(report(self.root, due, activation, dry_run=False), "REPORT_EXISTS")
        saved = read_obj(self.root / report_path("2026-11-12"))
        self.assertEqual(saved["registered_72h_reviews"], 0)
        self.assertEqual(saved["investor_incremental_edge"], "UNPROVEN")
        self.assertEqual(saved["authority"]["automatic_model_reweighting"], False)

    def test_no_activation_does_not_invent_past_issuances(self):
        with self.patch_git():
            r = run(self.root, T0, dry_run=True, activated_at=T0)
        self.assertEqual(r["register"], "NOT_PROSPECTIVE_ELIGIBLE")
        self.assertFalse((self.root / OUTPUT).exists())


if __name__ == "__main__":
    unittest.main()
