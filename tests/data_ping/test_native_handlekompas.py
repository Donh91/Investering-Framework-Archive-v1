import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.data_ping.native_handlekompas import AUTHORITY, build, load_auto_state, owner_freshness, protection_tracker, write


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
            "predecessor": {"status": "AVAILABLE", "market_observation_open_utc": "2026-09-08T19:00:00Z"},
            "normalized_state": {
                "live_market": {"ethbtc": 0.0317, "observation_open_utc": "2026-09-08T20:00:00Z"},
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

    def test_optional_source_degradation_does_not_poison_decision_health(self):
        packet = self.packet(validation="DEGRADED", decision="PASS")
        packet["optional_degraded_lanes"] = ["catalyst_context"]
        packet["source_health"]["catalyst_context"] = {
            "status": "DEGRADED",
            "classification": "CATALYST_DISCOVERY_ONLY_REFERENCE",
        }
        out = build(packet, now=datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertEqual(out["DATA_HEALTH"]["status"], "PASS")
        self.assertEqual(out["action"]["NOW"], "HOLD_WAIT")
        self.assertEqual(out["DATA_HEALTH"]["source_validation_status"], "DEGRADED")

    def test_stale_owner_fails_native_action_closed(self):
        out = build(self.packet(), now=datetime(2026,9,9,4,0,tzinfo=timezone.utc))
        self.assertEqual(out["action"]["NOW"], "HOLD_WAIT_DATA_DEGRADED")
        self.assertEqual(out["DATA_HEALTH"]["status"], "DEGRADED")
        self.assertEqual(out["DATA_HEALTH"]["owner_freshness"]["status"], "STALE_OR_UNAVAILABLE")

    def test_missing_owner_age_policy_fails_closed(self):
        packet = self.packet()
        freshness = packet["source_health"]["hourly_market"]["freshness"]
        for lane in (
            "pointer_freshness", "retrieval_freshness",
            "session_coverage_freshness", "source_observation_freshness",
        ):
            freshness[lane].pop("max_age_seconds")
        now = datetime(2026, 9, 9, 4, 0, tzinfo=timezone.utc)
        verdict = owner_freshness(packet, now)
        self.assertEqual(verdict["status"], "STALE_OR_UNAVAILABLE")
        self.assertIn("OWNER_FRESHNESS_MAX_AGE_UNAVAILABLE", verdict["reasons"])
        self.assertEqual(verdict["checks"], [])
        out = build(packet, now=now)
        self.assertEqual(out["action"]["NOW"], "HOLD_WAIT_DATA_DEGRADED")

    def test_current_owner_age_policy_still_passes(self):
        packet = self.packet()
        now = datetime(2026, 9, 8, 20, 0, tzinfo=timezone.utc)
        verdict = owner_freshness(packet, now)
        self.assertEqual(verdict["status"], "PASS")
        self.assertEqual(len(verdict["checks"]), 5)

    def test_one_missing_or_invalid_owner_ttl_cannot_borrow_other_lane_policy(self):
        now = datetime(2026, 9, 8, 20, 0, tzinfo=timezone.utc)
        for lane in ("pointer_freshness", "retrieval_freshness",
                     "session_coverage_freshness", "source_observation_freshness"):
            for maximum in (None, True, False, -1, float("nan"), float("inf"), "10800"):
                with self.subTest(lane=lane, maximum=maximum):
                    packet = self.packet()
                    row = packet["source_health"]["hourly_market"]["freshness"][lane]
                    if maximum is None:
                        row.pop("max_age_seconds")
                    else:
                        row["max_age_seconds"] = maximum
                    verdict = owner_freshness(packet, now)
                    self.assertEqual(verdict["status"], "STALE_OR_UNAVAILABLE")
                    self.assertIn(f"{lane.upper()}_MAX_AGE_UNAVAILABLE", verdict["reasons"])
                    out = build(packet, now=now)
                    self.assertEqual(out["action"]["NOW"], "HOLD_WAIT_DATA_DEGRADED")
                    self.assertEqual(out["DATA_HEALTH"]["status"], "DEGRADED")

    def test_omitted_ttl_cannot_hide_stale_or_future_observation(self):
        now = datetime(2026, 9, 8, 20, 0, tzinfo=timezone.utc)
        for stamp, status in (("2026-09-01T00:00:00Z", "STALE"),
                              ("2026-09-09T00:00:00Z", "FUTURE")):
            with self.subTest(stamp=stamp):
                packet = self.packet()
                row = packet["source_health"]["hourly_market"]["freshness"]["source_observation_freshness"]
                row.update(timestamp=stamp, status=status)
                row.pop("max_age_seconds")
                self.assertEqual(owner_freshness(packet, now)["status"], "STALE_OR_UNAVAILABLE")
                self.assertEqual(build(packet, now=now)["action"]["NOW"], "HOLD_WAIT_DATA_DEGRADED")

    def test_optional_unavailable_dimension_and_zero_age_boundary_preserved(self):
        now = datetime(2026, 9, 8, 20, 0, tzinfo=timezone.utc)
        for omit in (False, True):
            with self.subTest(omit=omit):
                packet = self.packet()
                freshness = packet["source_health"]["hourly_market"]["freshness"]
                if omit:
                    del freshness["source_observation_freshness"]
                else:
                    freshness["source_observation_freshness"] = {
                        "status": "UNAVAILABLE", "timestamp": None,
                        "age_seconds": None, "max_age_seconds": None,
                    }
                freshness["retrieval_freshness"]["max_age_seconds"] = 0
                self.assertEqual(owner_freshness(packet, now)["status"], "PASS")
                self.assertEqual(build(packet, now=now)["action"]["NOW"], "HOLD_WAIT")

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

    def test_native_packet_exposes_direction_separately_from_action(self):
        packet = self.packet()
        packet["deltas_since_prior_auto_packet"] = {
            "btc_usdt": {"pct": -1.0},
            "eth_usdt": {"pct": -2.0},
            "ethbtc": {"pct": -1.0},
        }
        out = build(packet, now=datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertEqual(out["action"]["NOW"], "HOLD_WAIT")
        self.assertEqual(out["market_direction"]["directional_state"], "BEARISH")
        self.assertEqual(out["market_direction"]["action_permission"], "HOLD_WAIT")
        self.assertFalse(out["authority"]["portfolio_execution"])

    def test_repeated_market_observation_is_explicitly_not_neutral(self):
        packet = self.packet()
        packet["normalized_state"]["live_market"].update({
            "btc_usdt": 80000.0,
            "eth_usdt": 2500.0,
            "observation_open_utc": "2026-09-08T20:00:00Z",
        })
        packet["predecessor"]["market_observation_open_utc"] = "2026-09-08T20:00:00Z"
        packet["deltas_since_prior_auto_packet"] = {
            "btc_usdt": {"pct": 0.0},
            "eth_usdt": {"pct": 0.0},
            "ethbtc": {"pct": 0.0},
        }
        out = build(packet, now=datetime(2026,9,8,20,0,tzinfo=timezone.utc))
        self.assertEqual(out["market_direction"]["directional_state"], "UNCHANGED_NO_NEW_OBSERVATION")
        self.assertEqual(out["market_direction"]["regime"], "NO_NEW_OBSERVATION")
        self.assertFalse(out["market_direction"]["new_price_observation"])
        self.assertEqual(out["action"]["NOW"], "HOLD_WAIT")

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


    def _protection_transition(self, risk, prior=None, *, posture="HOLD_WAIT", direction="MIXED", packet=None):
        cn = {
            "decision_projection": {
                "contract": "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1",
                "protection": {
                    "pullback_risk_state": risk,
                    "distribution_risk": "NONE",
                    "confidence_quality": "MEDIUM",
                },
            },
        }
        result = protection_tracker(
            self.packet() if packet is None else packet,
            {"NOW": posture},
            {"directional_state": direction},
            cn, as_of=datetime(2026, 9, 8, 20, 0, tzinfo=timezone.utc),
            prior_compass={"protection_tracker": prior} if prior is not None else None,
        )
        self.assertEqual(result["authority"], {
            "portfolio_execution": False, "wallet_specific": False,
            "new_market_classifier": False,
        })
        return result

    def test_reclaim_survives_repeated_elevated_observations(self):
        high = self._protection_transition("HIGH")
        self.assertEqual(high["reentry_state"], "WAIT_FOR_FLUSH")
        prior = self._protection_transition("ELEVATED", high)
        self.assertEqual(prior["reentry_state"], "WAIT_FOR_RECLAIM")
        for posture, direction in (("HOLD_WAIT", "BEARISH"), ("PREPARE", "BULLISH")):
            with self.subTest(posture=posture, direction=direction):
                prior = self._protection_transition("ELEVATED", prior, posture=posture, direction=direction)
                self.assertEqual(prior["pullback_risk_state"], "ELEVATED")
                self.assertEqual(prior["reentry_state"], "WAIT_FOR_RECLAIM")

    def test_review_requires_current_constructive_confirmation(self):
        for risk in ("NORMAL", "BUILDING"):
            for prior_state in ("WAIT_FOR_RECLAIM", "REVIEW"):
                for posture, direction, expected in (
                    ("PREPARE", "BULLISH", "REVIEW"),
                    ("GRADUATED_TOPUP_ACTIVE", "BULLISH", "REVIEW"),
                    ("HOLD_WAIT", "BULLISH", "WAIT_FOR_RECLAIM"),
                    ("HOLD_WAIT_DATA_DEGRADED", "BULLISH", "WAIT_FOR_RECLAIM"),
                    ("PREPARE", "BEARISH", "WAIT_FOR_RECLAIM"),
                    ("PREPARE", "MIXED", "WAIT_FOR_RECLAIM"),
                    ("PREPARE", "SIDEWAYS", "WAIT_FOR_RECLAIM"),
                    ("PREPARE", "UNAVAILABLE", "WAIT_FOR_RECLAIM"),
                    ("PREPARE", "UNCHANGED_NO_NEW_OBSERVATION", "WAIT_FOR_RECLAIM"),
                ):
                    with self.subTest(risk=risk, prior=prior_state, posture=posture, direction=direction):
                        out = self._protection_transition(risk, {
                            "pullback_risk_state": "NORMAL", "reentry_state": prior_state,
                        }, posture=posture, direction=direction)
                        self.assertEqual(out["pullback_risk_state"], risk)
                        self.assertEqual(out["reentry_state"], expected)

    def test_review_cannot_survive_renewed_risk_or_unavailable_evidence(self):
        prior = {"pullback_risk_state": "NORMAL", "reentry_state": "REVIEW"}
        for risk, expected in (
            ("ELEVATED", "WAIT_FOR_RECLAIM"), ("HIGH", "WAIT_FOR_FLUSH"),
            ("CONFIRMED", "WAIT_FOR_FLUSH"), ("UNAVAILABLE", "UNAVAILABLE"),
        ):
            with self.subTest(risk=risk):
                out = self._protection_transition(risk, prior, posture="PREPARE", direction="BULLISH")
                self.assertEqual(out["reentry_state"], expected)
                self.assertEqual(out["pullback_risk_state"], risk)
        out = self._protection_transition("NORMAL", prior, posture="PREPARE",
                                          direction="BULLISH", packet=self.packet(validation="FAIL"))
        self.assertEqual(out["reentry_state"], "UNAVAILABLE")

    def test_no_review_without_prior_protection_sequence(self):
        for risk in ("NORMAL", "BUILDING", "ELEVATED"):
            with self.subTest(risk=risk):
                out = self._protection_transition(risk, posture="PREPARE", direction="BULLISH")
                self.assertEqual(out["reentry_state"], "INACTIVE")
        high = self._protection_transition("HIGH")
        first_reclaim = self._protection_transition("NORMAL", high, posture="PREPARE", direction="BULLISH")
        self.assertEqual(first_reclaim["reentry_state"], "WAIT_FOR_RECLAIM")
        self.assertEqual(self._protection_transition("NORMAL", first_reclaim, posture="PREPARE",
                                                     direction="BULLISH")["reentry_state"], "REVIEW")


    def test_outage_preserves_flush_and_reclaim_obligations(self):
        high = self._protection_transition("HIGH")
        reclaim = self._protection_transition("ELEVATED", high)
        review = self._protection_transition("NORMAL", reclaim, posture="PREPARE", direction="BULLISH")
        self.assertEqual(review["reentry_state"], "REVIEW")
        for start, expected_carry in (
            (high, "WAIT_FOR_FLUSH"), (reclaim, "WAIT_FOR_RECLAIM"),
            (review, "WAIT_FOR_RECLAIM"),
        ):
            with self.subTest(start=start["reentry_state"]):
                gap = self._protection_transition("UNAVAILABLE", start)
                self.assertEqual(gap["reentry_state"], "UNAVAILABLE")
                self.assertEqual(gap["reentry_pending_before_gap"], expected_carry)
                gap = self._protection_transition("NORMAL", gap, packet=self.packet(validation="FAIL"))
                self.assertEqual(gap["reentry_state"], "UNAVAILABLE")
                self.assertEqual(gap["reentry_pending_before_gap"], expected_carry)
                recovered = self._protection_transition("NORMAL", gap, posture="PREPARE", direction="BULLISH")
                self.assertEqual(recovered["reentry_state"], "WAIT_FOR_RECLAIM")
                self.assertNotIn("reentry_pending_before_gap", recovered)
                self.assertEqual(self._protection_transition("NORMAL", recovered, posture="PREPARE",
                                                             direction="BULLISH")["reentry_state"], "REVIEW")
                self.assertEqual(self._protection_transition("HIGH", gap)["reentry_state"], "WAIT_FOR_FLUSH")

    def test_outage_memory_does_not_invent_or_restore_permission(self):
        priors = [
            None,
            {"pullback_risk_state": "UNAVAILABLE", "reentry_state": "UNAVAILABLE"},
            {"pullback_risk_state": "UNAVAILABLE", "reentry_state": "UNAVAILABLE",
             "reentry_pending_before_gap": "REVIEW"},
            {"pullback_risk_state": "UNAVAILABLE", "reentry_state": "UNAVAILABLE",
             "reentry_pending_before_gap": ["WAIT_FOR_RECLAIM"]},
            {"pullback_risk_state": "NORMAL", "reentry_state": "INACTIVE",
             "reentry_pending_before_gap": "WAIT_FOR_FLUSH"},
        ]
        for prior in priors:
            with self.subTest(prior=prior):
                gap = self._protection_transition("UNAVAILABLE", prior)
                self.assertIsNone(gap["reentry_pending_before_gap"])
                self.assertEqual(self._protection_transition("NORMAL", gap, posture="PREPARE",
                                                             direction="BULLISH")["reentry_state"], "INACTIVE")

    def test_missing_cn_or_projection_preserves_pending_reclaim(self):
        start = self._protection_transition("ELEVATED", self._protection_transition("HIGH"))
        for cn in (None, {"decision_projection": {"contract": "CYCLE_NAVIGATOR_DECISION_PROJECTION_v1"}}):
            with self.subTest(cn=cn):
                gap = protection_tracker(self.packet(), {"NOW": "PREPARE"},
                    {"directional_state": "BULLISH"}, cn,
                    as_of=datetime(2026, 9, 8, 20, 0, tzinfo=timezone.utc),
                    prior_compass={"protection_tracker": start})
                self.assertEqual(gap["reentry_state"], "UNAVAILABLE")
                self.assertEqual(gap["reentry_pending_before_gap"], "WAIT_FOR_RECLAIM")
                self.assertEqual(self._protection_transition("ELEVATED", gap)["reentry_state"],
                                 "WAIT_FOR_RECLAIM")

    def test_review_oscillation_after_recovery_never_latches(self):
        high = self._protection_transition("HIGH")
        gap = self._protection_transition("UNAVAILABLE", high)
        prior = self._protection_transition("NORMAL", gap, posture="PREPARE", direction="BULLISH")
        for risk, expected in (("NORMAL", "REVIEW"), ("ELEVATED", "WAIT_FOR_RECLAIM"),
                               ("NORMAL", "REVIEW"), ("ELEVATED", "WAIT_FOR_RECLAIM")):
            prior = self._protection_transition(risk, prior, posture="PREPARE", direction="BULLISH")
            self.assertEqual(prior["reentry_state"], expected)


if __name__=="__main__":
    unittest.main()
