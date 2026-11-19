"""BC 90d three-state health, CMC cross-check and PASS-only consumer gating."""
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.data_ping import auto_market_state as A
from scripts.data_ping import native_handlekompas as K
from scripts.health.native_market_recovery import POLICY, decide, default_state

NOW = datetime(2026, 11, 19, 12, 0, tzinfo=timezone.utc)


def stamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def bc(score, *, status="PASS", retrieved=None):
    retrieved = retrieved or NOW
    return {
        "status": status,
        "retrieved_at_utc": stamp(retrieved),
        "observation_date_utc": stamp(retrieved)[:10],
        "source_raw_sha256": "a" * 64,
        "horizons": {} if score is None else {"90": {"published_score": score}},
    }


def cmc(score, status="PASS"):
    return {"status": status, "published_score": score, "horizon_days": 90}


def context(bc_row=None, cmc_row=None):
    out = {}
    if bc_row is not None:
        out["blockchaincenter_altcoin_season"] = bc_row
    if cmc_row is not None:
        out["coinmarketcap_altcoin_season"] = cmc_row
    return out


def prior_with_fresh(score, age):
    return {
        "packet_generated_at_utc": stamp(NOW - age),
        "normalized_state": {"altseason_context": context(bc(score, retrieved=NOW - age)), "altseason_carry": None},
    }


def health_of(current, prior, now):
    return A.altseason_source_health(A.live_altseason_has_observation(current), prior, now)


CURRENT_MISSING = context(bc(None, status="DEGRADED"), cmc(60))


class ThreeStateHealthTests(unittest.TestCase):
    def test_constant_is_72_hours(self):
        self.assertEqual(A.ALTSEASON_CARRY_MAX_HOURS, 72)

    def test_fresh_bc_90d_is_pass_without_carry(self):
        health, carry = health_of(context(bc(41)), prior_with_fresh(30, timedelta(hours=1)), NOW)
        self.assertEqual(health, {"status": "PASS", "classification": "LIVE_ANCHOR_ALTSEASON_CONTEXT"})
        self.assertIsNone(carry)

    def test_carry_within_window_is_degraded_carry_with_explicit_age_time_value(self):
        health, carry = health_of(CURRENT_MISSING, prior_with_fresh(33, timedelta(hours=5)), NOW)
        self.assertEqual(health["status"], "DEGRADED_CARRY")
        self.assertEqual(health["classification"], "BLOCKCHAINCENTER_90D_CARRIED_FROM_PRIOR_CAPTURE")
        self.assertEqual(health["carry_age_hours"], 5.0)
        self.assertEqual(health["carry_source_retrieved_at_utc"], stamp(NOW - timedelta(hours=5)))
        self.assertEqual(carry["value"], 33)
        self.assertEqual(carry["age_hours"], 5.0)
        self.assertEqual(carry["source_retrieved_at_utc"], stamp(NOW - timedelta(hours=5)))
        self.assertEqual(carry["carry_origin"], "PREDECESSOR_PACKET_FRESH_OBSERVATION")
        self.assertNotIn("detail", health)  # recovery token scan reads classification+detail only

    def test_boundary_exactly_72h_carries(self):
        health, carry = health_of(CURRENT_MISSING, prior_with_fresh(33, timedelta(hours=72)), NOW)
        self.assertEqual(health["status"], "DEGRADED_CARRY")
        self.assertEqual(carry["age_hours"], 72.0)

    def test_boundary_72h_plus_one_second_is_unavailable(self):
        health, carry = health_of(CURRENT_MISSING, prior_with_fresh(33, timedelta(hours=72, seconds=1)), NOW)
        self.assertEqual(health, {"status": "UNAVAILABLE", "classification": "BLOCKCHAINCENTER_90D_REQUIRED_VALUE_UNAVAILABLE"})
        self.assertIsNone(carry)

    def test_no_prior_or_invalid_prior_is_unavailable(self):
        for prior in (
            None,
            {"normalized_state": {}},
            prior_with_fresh(101, timedelta(hours=1)),
            prior_with_fresh(True, timedelta(hours=1)),
            {"normalized_state": {"altseason_context": context(bc(40, status="DEGRADED"))}},
            prior_with_fresh(40, timedelta(hours=-1)),  # future source time
        ):
            health, carry = health_of(CURRENT_MISSING, prior, NOW)
            self.assertEqual(health["status"], "UNAVAILABLE", prior)
            self.assertIsNone(carry)

    def test_chained_carry_keeps_original_source_age_and_cannot_extend_window(self):
        first_health, first_carry = health_of(CURRENT_MISSING, prior_with_fresh(33, timedelta(hours=60)), NOW)
        self.assertEqual(first_health["status"], "DEGRADED_CARRY")
        prior = {"packet_generated_at_utc": stamp(NOW), "normalized_state": {"altseason_context": CURRENT_MISSING, "altseason_carry": first_carry}}
        later = NOW + timedelta(hours=12)
        health, carry = health_of(CURRENT_MISSING, prior, later)
        self.assertEqual(health["status"], "DEGRADED_CARRY")
        self.assertEqual(carry["age_hours"], 72.0)
        self.assertEqual(carry["value"], 33)
        self.assertEqual(carry["carry_origin"], "PREDECESSOR_PACKET_CARRY")
        health, carry = health_of(CURRENT_MISSING, prior, later + timedelta(seconds=1))
        self.assertEqual(health["status"], "UNAVAILABLE")
        self.assertIsNone(carry)

    def test_cmc_is_never_the_value(self):
        current = context(bc(None, status="DEGRADED"), cmc(64))
        prior = {"normalized_state": {"altseason_context": context(None, cmc(70))}}
        health, carry = health_of(current, prior, NOW)
        self.assertEqual(health["status"], "UNAVAILABLE")
        self.assertIsNone(carry)
        self.assertFalse(A.live_altseason_has_observation(context(None, cmc(64))))
        health, carry = health_of(current, prior_with_fresh(22, timedelta(hours=2)), NOW)
        self.assertEqual(carry["value"], 22)


class CrossCheckTests(unittest.TestCase):
    def test_threshold_is_documented_and_conservative(self):
        self.assertEqual(A.ALTSEASON_CROSSCHECK_DIVERGENCE_POINTS, 35)

    def test_consistent_divergent_unavailable(self):
        row = A.altseason_crosscheck(context(bc(30), cmc(65)))
        self.assertEqual((row["status"], row["bc"], row["cmc"], row["abs_diff"]), ("CONSISTENT", 30, 65, 35))
        row = A.altseason_crosscheck(context(bc(30), cmc(66)))
        self.assertEqual((row["status"], row["abs_diff"]), ("DIVERGENT", 36))
        self.assertEqual(row["authority"], "INFORMATIONAL_WARNING_ONLY_NO_SIGNAL_CHANGE")
        for value in (context(bc(30)), context(None, cmc(40)), context(bc(30), cmc(40, status="DEGRADED")), context(bc(30, status="DEGRADED"), cmc(40))):
            row = A.altseason_crosscheck(value)
            self.assertEqual(row["status"], "UNAVAILABLE")
            self.assertIsNone(row["abs_diff"])

    def test_divergence_changes_no_health(self):
        health, _ = health_of(context(bc(10), cmc(90)), None, NOW)
        self.assertEqual(health["status"], "PASS")


class PassOnlyConsumerGatingTests(unittest.TestCase):
    def test_decision_context_and_score_still_require_pass(self):
        health = {lane: {"status": "PASS"} for lane in A.LANES}
        health["altseason_context"] = {"status": "DEGRADED_CARRY"}
        required = A.decision_lanes(None)
        self.assertIn("altseason_context", [lane for lane in required if health[lane]["status"] != "PASS"])
        carry_score = A.replacement_score(None, health, None)
        health["altseason_context"] = {"status": "UNAVAILABLE"}
        self.assertEqual(carry_score, A.replacement_score(None, health, None))

    def test_altseason_blocker_degrades_only_the_alt_outputs(self):
        # Superseded #2244 deferred decision 4 (2026-11-19, K06): altseason_context is CONTEXT_ONLY for the core.
        # A failed or carried altseason lane no longer blanks BTC/ETH; it fails closed only for the alt outputs.
        for status, alt_usable in (("UNAVAILABLE", False), ("DEGRADED_CARRY", True), ("PASS", True)):
            auto = {"validation_status": "DEGRADED", "decision_context_status": "DEGRADED", "blockers": ["altseason_context"],
                    "source_health": {"altseason_context": {"status": status}}}
            self.assertTrue(K._health_ok(auto), status)
            self.assertEqual(K._alt_context_usable(auto), alt_usable, status)
        # any other required lane still blanks the core
        auto = {"validation_status": "DEGRADED", "decision_context_status": "DEGRADED", "blockers": ["altseason_context", "breadth"],
                "source_health": {"altseason_context": {"status": "UNAVAILABLE"}}}
        self.assertFalse(K._health_ok(auto))
        self.assertFalse(K._health_ok({"validation_status": "FAIL", "decision_context_status": "DEGRADED", "blockers": ["altseason_context"]}))
        self.assertFalse(K._health_ok({"validation_status": "DEGRADED", "decision_context_status": "UNKNOWN", "blockers": []}))

    def test_recovery_keeps_retrying_on_carry(self):
        health = {lane: {"status": "PASS", "classification": "PASS"} for lane in POLICY}
        health["altseason_context"], _ = health_of(CURRENT_MISSING, prior_with_fresh(33, timedelta(hours=4, minutes=29)), NOW)
        auto = {"packet_sha256": "abc", "source_snapshot": {"exact_commit_sha": "x"}, "source_health": health}
        _, state = decide(auto, default_state(), NOW)
        decision, _ = decide(auto, state, NOW + timedelta(hours=1))
        self.assertEqual([row["lanes"] for row in decision["dispatches"]], [["altseason_context"]])
        self.assertEqual(decision["suppressed_retries"], [])

    def _feature(self, auto):
        rows = K.evidence_snapshot(auto, Path("p.json"))["selected_features"]
        return next(row for row in rows if row["feature_id"] == "altseason_score_90d")

    def test_compass_evidence_shows_carry_only_as_degraded_with_age(self):
        health, carry = health_of(CURRENT_MISSING, prior_with_fresh(33, timedelta(hours=5)), NOW)
        auto = {"source_health": {"altseason_context": health}, "normalized_state": {"altseason_context": CURRENT_MISSING, "altseason_carry": carry}}
        row = self._feature(auto)
        self.assertEqual(row["value"], 33)
        self.assertEqual(row["freshness_state"], "DEGRADED_CARRY")
        self.assertEqual(row["eligibility"], "CONTEXT_ONLY_OR_DEGRADED")
        self.assertEqual(row["carry_age_hours"], 5.0)
        self.assertEqual(row["retrieved_at"], stamp(NOW - timedelta(hours=5)))

    def test_compass_evidence_unchanged_for_pass_and_unavailable(self):
        auto = {"source_health": {"altseason_context": {"status": "PASS"}}, "normalized_state": {"altseason_context": context(bc(41)), "altseason_carry": None}}
        row = self._feature(auto)
        self.assertEqual((row["value"], row["eligibility"]), (41, "ELIGIBLE_PRESENT"))
        self.assertNotIn("carry_age_hours", row)
        stray = {"value": 50, "source_retrieved_at_utc": stamp(NOW)}
        auto = {"source_health": {"altseason_context": {"status": "UNAVAILABLE"}}, "normalized_state": {"altseason_context": CURRENT_MISSING, "altseason_carry": stray}}
        row = self._feature(auto)
        self.assertEqual((row["value"], row["eligibility"]), (None, "MISSING"))


class AssembleWiringTests(unittest.TestCase):
    """End-to-end packet wiring with every source owner stubbed (no git, no network)."""

    def assemble(self, current, prior):
        from unittest import mock
        snapshot = mock.Mock(commit_sha="c" * 40, resolution_count=1)
        snapshot.consistency.return_value = "PINNED"
        live = {"target": {"market_metrics": {"rotation_context": current}}}

        def resolve(_snap, path, *_args):
            return (live, {"status": "PASS"}) if "captures" in path else (None, {"status": "FAIL"})

        with mock.patch.object(A.ti.GitCliSnapshot, "open_repo", return_value=snapshot), \
                mock.patch.object(A, "resolve", side_effect=resolve), \
                mock.patch.object(A, "hourly_row", return_value=(None, {"status": "UNAVAILABLE"})), \
                mock.patch.object(A, "read_json", return_value=(None, {"status": "UNAVAILABLE"})), \
                mock.patch.object(A, "latest_macro", return_value=(None, {"status": "UNAVAILABLE"})), \
                mock.patch.object(A, "btc_d", return_value=(None, {"status": "UNAVAILABLE"})), \
                mock.patch.object(A, "prior_packet", return_value=(prior, {"status": "AVAILABLE"})):
            return A.assemble(Path("."), NOW)

    def test_packet_exposes_carry_crosscheck_and_keeps_blocker(self):
        packet = self.assemble(CURRENT_MISSING, prior_with_fresh(33, timedelta(hours=6)))
        self.assertEqual(packet["source_health"]["altseason_context"]["status"], "DEGRADED_CARRY")
        self.assertEqual(packet["normalized_state"]["altseason_carry"]["value"], 33)
        self.assertEqual(packet["normalized_state"]["altseason_context"], CURRENT_MISSING)  # current raw untouched
        self.assertIn("altseason_context", packet["blockers"])
        self.assertEqual(packet["crosschecks"]["altseason_crosscheck"]["status"], "UNAVAILABLE")

    def test_packet_pass_and_divergent_warning(self):
        packet = self.assemble(context(bc(20), cmc(80)), None)
        self.assertEqual(packet["source_health"]["altseason_context"]["status"], "PASS")
        self.assertIsNone(packet["normalized_state"]["altseason_carry"])
        self.assertNotIn("altseason_context", packet["blockers"])
        self.assertEqual(packet["crosschecks"]["altseason_crosscheck"]["status"], "DIVERGENT")


if __name__ == "__main__":
    unittest.main()
