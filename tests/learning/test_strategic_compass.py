from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.learning.strategic_compass import alignment_class, materialize, validate_forward_range_candidate

# Existing Official Compass Outcomes PR gate invokes this test module.
# Import the isolated long-range shadow validators to execute their adversarial suite.
from tests.learning.test_strategic_compass_long_range_validation import LongRangeCandidateTests  # noqa: F401
from tests.learning.test_forward_price_shadow import ShadowPriceTests  # noqa: F401
from tests.learning.test_forward_price_source_custody import SourceCustodyTests  # noqa: F401
from tests.learning.test_forward_price_research_oracle import ForwardPriceResearchOracleTests  # noqa: F401
from tests.learning.test_forward_price_admission_horizon_guard import ForwardPriceAdmissionHorizonGuardTests  # noqa: F401
from tests.learning.test_forward_price_public_api_candidate import ForwardPricePublicApiCandidateTests  # noqa: F401
from tests.learning.test_forward_price_binance_native_usdt_candidate import BinanceNativeUsdtSourceTests  # noqa: F401


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def fixture_repo(tmp_path: Path, *, month=True, cycle_direction="UP") -> Path:
    compass_rel = "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/30/CMP-test.json"
    write(tmp_path / compass_rel, {
        "compass_id": "CMP-test",
        "market_reference": {"btc_usdt": 83000, "eth_usdt": 2660, "ethbtc": 0.032},
        "horizons": {
            "NEXT_12H": {"expected_direction": "DOWN", "expected_path": "retest", "action_posture": "HOLD"},
            "NEXT_1_3D": {"expected_direction": "DOWN", "expected_path": "retest", "action_posture": "HOLD"},
            "NEXT_5_7D": {"expected_direction": "SIDEWAYS", "expected_path": "absorption", "action_posture": "HOLD"},
        },
    })
    write(tmp_path / "04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json", {
        "compass_path": compass_rel,
        "compass_sha256": "official-sha",
    })
    projection = {
        "weeks_4_8": {
            "direction": cycle_direction, "summary": "structural bull", "state": "ROTATION",
            "action_posture": "HOLD", "warning": "NONE", "confidence": "MEDIUM",
        }
    }
    if month:
        projection["next_21_30d"] = {
            "direction": "UP", "btc_direction": "UP", "eth_direction": "UP", "ethbtc_direction": "UP", "summary": "recovery then expansion", "regime_destination": "EXPANSION",
            "expected_path": "retest -> absorption -> expansion", "action_posture": "HOLD",
            "falsification": ["breadth fails"], "confidence": "MEDIUM",
            "scenario_semantics": "UNCALIBRATED_SCENARIO_WEIGHT_NOT_PROBABILITY",
            "scenarios": [
                {"label": "BASE", "weight_pct": 55, "thesis": "expansion"},
                {"label": "BULL", "weight_pct": 20, "thesis": "fast expansion"},
                {"label": "BEAR", "weight_pct": 25, "thesis": "breakdown"},
            ],
        }
    cn_rel = "05_CYCLE_NAVIGATOR/weekly/2026/W40"
    write(tmp_path / cn_rel / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json", {
        "status": "READY", "issue_number": 28, "public_issue_number": 27,
        "decision_projection": projection,
    })
    write(tmp_path / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json", {
        "week_dir": cn_rel, "machine_package_sha256": "cn-sha", "iso_year": 2026, "iso_week": 40,
    })
    return tmp_path


class StrategicCompassTests(unittest.TestCase):
    def test_tactical_pullback_structural_bull_class(self):
        self.assertEqual(alignment_class(["DOWN", "DOWN", "SIDEWAYS", "UP", "UP"]), "TACTICAL_PULLBACK_STRUCTURAL_BULL")

    def test_materialize_preserves_horizon_disagreement(self):
        with tempfile.TemporaryDirectory() as td:
            repo = fixture_repo(Path(td))
            result = materialize(repo, datetime(2026, 9, 30, 12, tzinfo=timezone.utc))
            self.assertEqual(result["status"], "CREATED")
            anchor = json.loads((repo / result["anchor_path"]).read_text())
            self.assertEqual(anchor["strategic_21_30d"]["direction"], "UP")
            self.assertEqual(anchor["strategic_21_30d"]["btc_direction"], "UP")
            self.assertEqual(anchor["strategic_21_30d"]["eth_direction"], "UP")
            self.assertEqual(anchor["strategic_21_30d"]["ethbtc_direction"], "UP")
            self.assertEqual(anchor["strategic_21_30d"]["scenario_semantics"], "UNCALIBRATED_SCENARIO_WEIGHT_NOT_PROBABILITY")
            self.assertEqual(anchor["cycle_4_8w"]["direction"], "UP")
            self.assertEqual(anchor["cross_horizon_alignment"]["class"], "TACTICAL_PULLBACK_STRUCTURAL_BULL")
            self.assertFalse(anchor["authority"]["portfolio_execution"])

    def test_missing_month_projection_fails_closed_without_stretching_2_3w(self):
        with tempfile.TemporaryDirectory() as td:
            repo = fixture_repo(Path(td), month=False)
            result = materialize(repo, datetime(2026, 9, 30, 12, tzinfo=timezone.utc))
            anchor = json.loads((repo / result["anchor_path"]).read_text())
            self.assertEqual(anchor["strategic_21_30d"]["direction"], "UNAVAILABLE")
            self.assertFalse(anchor["strategic_21_30d"]["derived_from_2_3w"])
            self.assertEqual(anchor["strategic_21_30d"]["thesis_state"], "DATA_DEGRADED")

    def test_same_sources_are_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            repo = fixture_repo(Path(td))
            now = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)
            first = materialize(repo, now)
            second = materialize(repo, now)
            self.assertEqual(first["status"], "CREATED")
            self.assertEqual(second["status"], "NOOP_SAME_SOURCES")


def forward_range_fixture():
    # SYNTHETIC, no live price or provider assertion.
    from datetime import timedelta
    monday = datetime(2026, 10, 26, tzinfo=timezone.utc)
    windows = []
    for name, left, right in (("D8_14", 7, 14), ("D15_21", 14, 21)):
        windows.append({
            "window": name,
            "start_utc": (monday + timedelta(days=left)).isoformat().replace("+00:00", "Z"),
            "end_utc": (monday + timedelta(days=right)).isoformat().replace("+00:00", "Z"),
            "status": "UNAVAILABLE",
            "low_usd": None, "high_usd": None,
            "reason": "NO_ADMITTED_SOURCE"
        })
    return {
        "contract": "COMPASS_14_21D_RANGE_PREFLIGHT_v1",
        "authority": {"public_issuance": False, "score_allowed": False, "portfolio_action": False},
        "forecast_id": "SYNTHETIC_FORWARD_TEST",
        "forecast_week": "2026-W44",
        "public_issue_number": 31,
        "issued_at_utc": "2026-10-26T08:00:00Z",
        "source": {
            "owner": "CYCLE_NAVIGATOR_WEEKLY",
            "source_contract_id": "EXISTING_WEEKLY_OWNER",
            "sha256": "a" * 64,
            "first_known_at_utc": "2026-10-26T06:50:00Z",
            "cutoff_utc": "2026-10-26T07:00:00Z"
        },
        "revision_of": None,
        "BTC": {"windows": json.loads(json.dumps(windows))},
        "ETH": {"windows": json.loads(json.dumps(windows))}
    }


class ForwardRangePreflightTests(unittest.TestCase):
    def test_explicit_unavailable_is_valid_and_no_forecast_issued(self):
        original = forward_range_fixture()
        before = json.loads(json.dumps(original))
        self.assertEqual(validate_forward_range_candidate(original), original)
        self.assertEqual(original, before)

    def test_no_source_is_valid_for_explicit_unavailable(self):
        row = forward_range_fixture()
        row["source"] = None
        validate_forward_range_candidate(row)

    def test_missing_source_cannot_publish_candidate_prices(self):
        def bad(x):
            x["source"] = None
            x["BTC"]["windows"][0].update(status="CANDIDATE", low_usd=100.0, high_usd=120.0, reason=None)
        self.reject(bad)

    def test_source_bound_sparse_interval_candidate_not_price_path(self):
        row = forward_range_fixture()
        b = row["BTC"]["windows"][0]
        b.update(status="CANDIDATE", low_usd=100.0, high_usd=120.0, reason=None)
        validate_forward_range_candidate(row)
        self.assertNotIn("expected_close", b)

    def reject(self, patch):
        row = forward_range_fixture()
        patch(row)
        with self.assertRaises(ValueError):
            validate_forward_range_candidate(row)

    def test_wrong_iso_week(self):
        self.reject(lambda x: x.update(forecast_week="2026-W99"))

    def test_issued_after_start_of_outcome(self):
        self.reject(lambda x: x.update(issued_at_utc="2026-11-02T00:00:00Z"))

    def test_source_first_known_after_issue(self):
        self.reject(lambda x: x["source"].update(first_known_at_utc="2026-10-27T00:00:00Z"))

    def test_cutoff_before_source_first_known(self):
        self.reject(lambda x: x["source"].update(cutoff_utc="2026-10-26T06:00:00Z"))

    def test_cutoff_after_issued(self):
        self.reject(lambda x: x["source"].update(cutoff_utc="2026-10-26T08:00:01Z"))

    def test_window_crosses_boundaries(self):
        self.reject(lambda x: x["BTC"]["windows"][0].update(end_utc="2026-11-03T00:00:00Z"))

    def test_window_order_is_fixed(self):
        self.reject(lambda x: x["ETH"]["windows"].reverse())

    def test_abstention_cannot_have_price_band(self):
        self.reject(lambda x: x["BTC"]["windows"][0].update(status="ABSTAIN", low_usd=100, high_usd=110))

    def test_missing_source_fields_cannot_become_candidate(self):
        def bad(x):
            x["source"]["first_known_at_utc"] = None
            x["BTC"]["windows"][0].update(status="CANDIDATE", low_usd=100, high_usd=110, reason=None)
        self.reject(bad)

    def test_invalid_numeric_band(self):
        for low, high in ((-1, 110), (120, 110), (float("nan"), 110), (True, 110), (100, float("inf"))):
            with self.subTest(low=low, high=high):
                self.reject(lambda x: x["BTC"]["windows"][1].update(status="CANDIDATE", low_usd=low, high_usd=high, reason=None))

    def test_single_endpoint_is_not_a_band(self):
        self.reject(lambda x: x["BTC"]["windows"][0].update(status="CANDIDATE", low_usd=100, high_usd=None, reason=None))

    def test_spurious_curve_or_outcome_payload_not_allowed(self):
        self.reject(lambda x: x["BTC"]["windows"][0].update(expected_close=110))
        self.reject(lambda x: x.update(realized_return=0.2))

    def test_public_or_score_authority_cannot_be_escalated(self):
        self.reject(lambda x: x["authority"].update(public_issuance=True))
        self.reject(lambda x: x["authority"].update(score_allowed=True))
        self.reject(lambda x: x["authority"].update(portfolio_action=True))

    def test_revision_requires_separate_original_freeze_admission(self):
        self.reject(lambda x: x.update(revision_of="SYNTHETIC_PRIOR_FORECAST"))

    def test_no_issued_claim_with_blank_or_invalid_source_hash(self):
        self.reject(lambda x: x["source"].update(sha256="invalid"))



if __name__ == "__main__":
    unittest.main()
