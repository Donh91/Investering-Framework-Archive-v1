from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.data_ping import auto_market_state as a

NOW = datetime(2026, 9, 2, 7, 0, tzinfo=timezone.utc)


class FakeSnapshot:
    commit_sha = "a" * 40
    resolution_count = 1

    def read_json(self, path):
        raise FileNotFoundError(path)


class T(unittest.TestCase):
    def registry(self):
        return {
            "sources": [
                {
                    "manual_replacement_lane": lane,
                    "unattended_git_owner": True,
                    "normalization_contract": "AUTO_MARKET_STATE_PACKET_v1",
                    "decision_context_required": lane != "catalyst_context",
                }
                for lane in a.LANES
            ]
        }

    def health(self):
        return {lane: {"status": "PASS"} for lane in a.LANES}

    def stable(self, total=309e9, binding=False):
        return {
            "contract": "DEFILLAMA_STABLECOIN_LIQUIDITY_OWNER_v1_1",
            "global": {"total_usd": total, "change_1d_pct": -0.1, "change_7d_pct": 0.2, "change_30d_pct": 1.1},
            "evidence_semantics": {"evidence_role": "SUPPLY_LIQUIDITY", "deployment_confirmation": "NOT_ESTABLISHED"},
            "authority": {"binding": binding, "canonical_acceptance": False, "state_change": False, "portfolio_action": False},
        }

    def breadth(self, retrieved="2026-09-02T06:00:00Z"):
        membership = "b" * 64
        return {
            "contract": "RICH_BREADTH_CHECKPOINT_v1",
            "retrieved_at_utc": retrieved,
            "universe": {"identifier": "COINGECKO_MARKET_CAP_TOP100_FILTERED_EX_STABLECOINS_v1", "version": "TOP100_FILTERED_STABLE_EXCLUSION_RICH_BREADTH_v1_2", "constituent_count": 100, "membership_hash": membership},
            "aggregate": {"constituent_count": 100, "advancers": 31, "decliners": 67, "flat": 2, "advance_ratio": 0.31, "membership_hash": membership},
            "evidence_semantics": {"evidence_role": "PROXY_ONLY", "canonical_compatible": False, "canonical_large_cap_breadth": "UNCONFIRMED", "canonical_broad_alt_breadth": "UNCONFIRMED"},
        }

    def test_stablecoin_supply_only(self):
        value, health = a.normalize_stablecoin(self.stable(), now_utc=NOW)
        self.assertEqual(health["status"], "PASS")
        self.assertEqual(value["evidence_semantics"]["deployment_confirmation"], "NOT_ESTABLISHED")

    def test_stablecoin_missing_not_zero(self):
        value, health = a.normalize_stablecoin(self.stable(None), now_utc=NOW)
        self.assertIsNone(value)
        self.assertEqual(health["status"], "UNAVAILABLE")

    def test_stablecoin_authority_fails(self):
        value, health = a.normalize_stablecoin(self.stable(1, True), now_utc=NOW)
        self.assertIsNone(value)
        self.assertEqual(health["classification"], "STABLECOIN_AUTHORITY_ESCALATION")

    def test_breadth_full_owner_interface_passes_proxy_only(self):
        value, health = a.normalize_breadth(self.breadth(), now_utc=NOW)
        self.assertEqual(health["status"], "PASS")
        self.assertEqual(health["evidence_role"], "PROXY_ONLY")
        self.assertFalse(value["evidence_semantics"]["canonical_compatible"])

    def test_breadth_future_and_stale_fail_closed(self):
        value, health = a.normalize_breadth(self.breadth("2026-09-02T08:00:00Z"), now_utc=NOW)
        self.assertIsNone(value)
        self.assertEqual(health["classification"], "BREADTH_FUTURE_TIMESTAMP")
        value, health = a.normalize_breadth(self.breadth("2026-09-01T20:00:00Z"), now_utc=NOW, max_age=timedelta(hours=8))
        self.assertIsNone(value)
        self.assertEqual(health["status"], "DEGRADED")
        self.assertEqual(health["classification"], "BREADTH_OWNER_STALE")

    def test_crosscheck_independence_and_conflict(self):
        result = a.normalize_crosscheck(0.031, 0.03101, primary_family="BINANCE", crosscheck_family="BINANCE", tolerance_pct=0.25)
        self.assertFalse(result["independent"])
        self.assertEqual(result["status"], "AGREE")
        result = a.normalize_crosscheck(100, 120, primary_family="A", crosscheck_family="B", tolerance_pct=1)
        self.assertTrue(result["independent"])
        self.assertEqual(result["status"], "TRUE_CONFLICT")
        self.assertFalse(result["owner_switch_permitted"])

    def test_crosscheck_missing_and_not_comparable(self):
        self.assertEqual(a.normalize_crosscheck(1, None, primary_family="A", crosscheck_family="B")["status"], "STALE_CROSSCHECK")
        self.assertEqual(a.normalize_crosscheck(None, 1, primary_family="A", crosscheck_family="B")["status"], "STALE_PRIMARY")
        self.assertEqual(a.normalize_crosscheck(1, 2, primary_family="A", crosscheck_family="B", comparable=False)["status"], "NOT_COMPARABLE")

    def test_etf_finality(self):
        good = {"target": {"contract": "DAILY_SETTLED_ETF_CALIBRATION_v2", "session_date": "2026-08-31", "rows": [{"asset": "BTC", "reported_total": 216.7, "session_final": True, "total_parity": True}, {"asset": "ETH", "reported_total": 87.6, "session_final": True, "total_parity": True}]}}
        value, health = a.normalize_etf(good, now_utc=NOW)
        self.assertEqual(health["status"], "PASS")
        self.assertEqual(value["btc_reported_total_musd"], 216.7)
        good["target"]["rows"][1]["session_final"] = False
        value, health = a.normalize_etf(good, now_utc=NOW)
        self.assertIsNone(value)
        self.assertIn("NOT_FINAL", health["classification"])

    def test_missing_json_unavailable(self):
        value, health = a.read_json_lane(FakeSnapshot(), "missing.json")
        self.assertIsNone(value)
        self.assertEqual(health["status"], "UNAVAILABLE")

    def test_decision_lanes_make_discovery_optional_only(self):
        required = a.decision_lanes(self.registry())
        self.assertNotIn("catalyst_context", required)
        self.assertIn("macro_risk", required)
        self.assertEqual(len(required), len(a.LANES) - 1)

    def test_score_separate_dimensions_and_optional_discovery(self):
        score = a.replacement_score(self.registry(), self.health(), None)
        self.assertEqual(score["acquisition_automation_pct"], 100)
        self.assertEqual(score["normalization_validation_automation_pct"], 100)
        self.assertEqual(score["decision_context_readiness_pct"], 100)
        self.assertEqual(score["manual_input_residual_pct"], 0)
        self.assertIsNone(score["packet_parity_pct"])
        self.assertTrue(score["no_blended_marketing_score"])
        health = self.health()
        health["catalyst_context"] = {"status": "DEGRADED"}
        score = a.replacement_score(self.registry(), health, None)
        self.assertEqual(score["decision_context_readiness_pct"], 100)
        health["macro_risk"] = {"status": "UNAVAILABLE"}
        score = a.replacement_score(self.registry(), health, None)
        self.assertLess(score["decision_context_readiness_pct"], 100)

    def test_replay_parity_separate(self):
        score = a.replacement_score(self.registry(), self.health(), {"packet_parity_pct": 91, "packets_replayed": 2, "comparable_fields": 20})
        self.assertEqual(score["packet_parity_pct"], 91)
        self.assertEqual(score["packet_parity_evidence"]["packets"], 2)

    def test_delta_missing(self):
        self.assertIsNone(a.delta(1, None))
        self.assertEqual(a.delta(2, 1)["absolute"], 1)

    def test_write_nonbinding(self):
        packet = {"contract": a.CONTRACT, "packet_generated_at_utc": "2026-09-02T07:00:00Z", "packet_sha256": "a" * 64, "validation_status": "DEGRADED", "decision_context_status": "DEGRADED", "source_snapshot": {"exact_commit_sha": "b" * 40}, "replacement_score": {"manual_input_residual_pct": 0}, "authority": a.AUTHORITY}
        with tempfile.TemporaryDirectory() as directory:
            result = a.write_packet(packet, Path(directory))
            pointer = json.loads((Path(directory) / "LATEST.json").read_text())
            self.assertEqual(pointer["packet_sha256"], "a" * 64)
            self.assertFalse(pointer["authority"]["portfolio_action"])
            self.assertEqual(pointer["decision_context_status"], "DEGRADED")
            self.assertTrue(Path(result["packet_path"]).exists())

    def test_110_deterministic_fail_closed_cases(self):
        for i in range(110):
            mode = i % 5
            if mode == 0:
                result = a.normalize_crosscheck(100, None, primary_family="A", crosscheck_family="B", tolerance_pct=1); expected = "STALE_CROSSCHECK"
            elif mode == 1:
                result = a.normalize_crosscheck(100, 100.2, primary_family="A", crosscheck_family="A", tolerance_pct=1); expected = "AGREE"; self.assertFalse(result["independent"])
            elif mode == 2:
                result = a.normalize_crosscheck(100, 120, primary_family="A", crosscheck_family="B", tolerance_pct=1); expected = "TRUE_CONFLICT"
            elif mode == 3:
                result = a.normalize_crosscheck(24, 26, primary_family="A", crosscheck_family="B", comparable=False); expected = "NOT_COMPARABLE"
            else:
                result = a.normalize_crosscheck(None, 100, primary_family="A", crosscheck_family="B", tolerance_pct=1); expected = "STALE_PRIMARY"
            self.assertEqual(result["status"], expected)
            self.assertFalse(result["owner_switch_permitted"])


if __name__ == "__main__":
    unittest.main()
