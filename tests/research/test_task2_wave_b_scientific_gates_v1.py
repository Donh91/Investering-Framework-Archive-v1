"""Synthetic-only adversarial tests: no original W46 or historical warning fabricated."""
from __future__ import annotations
import unittest
from datetime import datetime, timedelta, timezone
from scripts.research import task2_wave_b_scientific_gates_v1 as mod


def stamp(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def week_packet():
    return {
        "asset": "BTC", "target_week": "2026-W46",
        "target_start_utc": "2026-11-09T00:00:00Z",
        "target_end_utc": "2026-11-16T00:00:00Z",
        "preissue_anchor_price": 100.,
        "anchor_source": {"immutable_sha": "d"*40, "quote": "USDT",
                          "first_known_utc": "2026-11-08T22:00:00Z"},
        "original": {"issue_utc": "2026-11-08T23:00:00Z",
                     "vendor_first_known_utc": "2026-11-08T22:00:00Z",
                     "immutable_sha": "a"*40, "quote": "USDT"},
        "models": {
            "ORIGINAL": {"issue_utc": "2026-11-08T23:00:00Z",
                         "vendor_first_known_utc": "2026-11-08T22:00:00Z",
                         "immutable_sha": "b"*40, "quote": "USDT",
                         "low": 80., "high": 120.},
            "B1": {"issue_utc": "2026-11-08T23:00:00Z",
                   "vendor_first_known_utc": "2026-11-08T22:00:00Z",
                   "immutable_sha": "c"*40, "quote": "USDT",
                   "low": 90., "high": 110.}},
        "outcome": {"matured_at_utc": "2026-11-16T01:00:00Z", "quote": "USDT",
                    "low": 88., "high": 111.,
                    "source": {"immutable_sha": "e"*40, "closed_hour_count": 168,
                               "first_closed_utc": "2026-11-09T00:00:00Z",
                               "last_closed_utc": "2026-11-16T00:00:00Z"}}}


def episode(kind="PULLBACK"):
    anchor = datetime(2026, 10, 8, 12, tzinfo=timezone.utc)
    slots = [
        {"decision_utc": stamp(anchor-timedelta(hours=i)),
         "status": "RECORDED", "severity": 3,
         "source_first_known_utc": stamp(anchor-timedelta(hours=i, minutes=30))}
        for i in range(4, 0, -1)]
    return {"kind": kind, "episode_id": "synthetic-ep1",
            "family_id": "synthetic-family1", "anchor_utc": stamp(anchor),
            "slots": slots}


class Task2WaveBScientificGatesTests(unittest.TestCase):
    def test_three_of_five_is_not_early_high_warning(self):
        r = mod.audit_pullback_episode(episode())
        self.assertEqual(r["source_legal_risk3_slots"], 4)
        self.assertTrue(r["pullback_without_delivered_high_risk"])
        self.assertIsNone(r["lead_hours_from_first_proven_delivery"])
        self.assertFalse(r["risk_policy_change"])

    def test_early_proven_delivery_and_false_alarm_control(self):
        p = episode()
        p["slots"][1]["severity"] = 4
        p["slots"][1]["delivered_utc"] = "2026-10-08T10:30:00Z"
        r = mod.audit_pullback_episode(p)
        self.assertEqual(r["lead_hours_from_first_proven_delivery"], 1.5)
        p["kind"] = "CONTROL"
        self.assertTrue(mod.audit_pullback_episode(p)["control_with_delivered_high_risk"])

    def test_grid_cannot_silently_lose_an_hour(self):
        p = episode()
        p["slots"].pop(1)
        with self.assertRaisesRegex(ValueError, "INCOMPLETE_OR_NONCONTIGUOUS"):
            mod.audit_pullback_episode(p)
        p = episode()
        p["slots"][1] = {"decision_utc": p["slots"][1]["decision_utc"],
                          "status": "SOURCE_MISSING"}
        self.assertEqual(mod.audit_pullback_episode(p)["explicit_non_recorded_slots"], 1)
        p["slots"][1]["severity"] = 4
        with self.assertRaisesRegex(ValueError, "FABRICATION"):
            mod.audit_pullback_episode(p)

    def test_unknown_first_known_or_delivery_never_win(self):
        p = episode()
        p["slots"][0]["severity"] = 5
        p["slots"][0]["source_first_known_utc"] = None
        p["slots"][1]["severity"] = 5
        r = mod.audit_pullback_episode(p)
        self.assertEqual(r["uncertified_recorded_slots"], 1)
        self.assertFalse(r["pre_anchor_delivered_high_risk"])

    def test_lookahead_and_delivery_before_issue_not_accepted(self):
        p = episode()
        p["slots"][1]["severity"] = 4
        p["slots"][1]["source_first_known_utc"] = "2026-10-08T13:00:00Z"
        self.assertFalse(mod.audit_pullback_episode(p)["pre_anchor_delivered_high_risk"])
        p = episode()
        p["slots"][1]["severity"] = 4
        p["slots"][1]["delivered_utc"] = "2026-10-08T07:00:00Z"
        with self.assertRaisesRegex(ValueError, "DELIVERY_BEFORE_ISSUANCE"):
            mod.audit_pullback_episode(p)

    def test_narrow_interval_may_miss_with_higher_overlap(self):
        r = mod.score_weekly_pair(week_packet())
        self.assertEqual(r["status"], "DESCRIPTIVE_PAIRED_SCORE_ONLY")
        self.assertTrue(r["scores"]["ORIGINAL"]["joint_extrema_contained"])
        self.assertFalse(r["scores"]["B1"]["joint_extrema_contained"])
        self.assertLess(r["scores"]["B1"]["width_over_preissue_anchor"],
                        r["scores"]["ORIGINAL"]["width_over_preissue_anchor"])
        self.assertFalse(r["statistical_edge_admitted"])
        self.assertIsNone(r["scores"]["B1"]["probabilistic_interval_score"])

    def test_quote_usd_vs_usdt_blocks_scoring(self):
        p = week_packet()
        p["original"]["quote"] = "USD"
        self.assertEqual(mod.score_weekly_pair(p)["status"], "QUOTE_INCOMPARABLE")

    def test_original_and_challenger_first_known_are_required(self):
        p = week_packet()
        p["original"]["vendor_first_known_utc"] = None
        self.assertEqual(mod.score_weekly_pair(p)["status"], "PIT_UNVERIFIED")
        p = week_packet()
        p["models"]["B1"]["vendor_first_known_utc"] = "2026-11-09T06:00:00Z"
        self.assertEqual(mod.score_weekly_pair(p)["status"], "CHALLENGER_PIT_UNVERIFIED")

    def test_anchor_and_outcome_contiguity_are_required(self):
        p = week_packet()
        p["anchor_source"]["first_known_utc"] = None
        self.assertEqual(mod.score_weekly_pair(p)["status"], "ANCHOR_PIT_UNVERIFIED")
        p = week_packet()
        p["outcome"]["source"]["closed_hour_count"] = 167
        self.assertEqual(mod.score_weekly_pair(p)["status"], "OUTCOME_COVERAGE_UNVERIFIED")

    def test_no_early_maturity_or_post_issuance_challenger(self):
        p = week_packet()
        p["outcome"]["matured_at_utc"] = "2026-11-14T00:00:00Z"
        self.assertEqual(mod.score_weekly_pair(p)["status"], "NOT_MATURED")
        p = week_packet()
        p["models"]["B1"]["issue_utc"] = "2026-11-09T00:01:00Z"
        self.assertEqual(mod.score_weekly_pair(p)["status"], "CHALLENGER_ISSUED_TOO_LATE")

    def test_bad_prices_fail(self):
        p = week_packet()
        p["models"]["B1"]["high"] = float("nan")
        with self.assertRaisesRegex(ValueError, "INVALID_POSITIVE_PRICE"):
            mod.score_weekly_pair(p)
        p = week_packet()
        p["outcome"]["high"] = 80.
        with self.assertRaisesRegex(ValueError, "INVALID_OUTCOME_EXTREMA"):
            mod.score_weekly_pair(p)

    def test_no_matured_outcome_is_not_imputed(self):
        p = week_packet()
        p["outcome"] = None
        self.assertEqual(mod.score_weekly_pair(p)["status"], "NOT_MATURED")


if __name__ == "__main__":
    unittest.main()
