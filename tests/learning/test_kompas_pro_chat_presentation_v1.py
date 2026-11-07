"""P0 chat display contracts: original authority stays separate from analysis."""
import unittest

from scripts.learning.kompas_pro_chat_presentation_v1 import (
    render_chat,
    validate_analysis_overlay,
)
from scripts.learning.kompas_pro_horizon_readback_v2 import HORIZON_IDS

AS_OF = "2026-11-07T15:20:00Z"


def ledger():
    return {"horizons": [{"id": i, "label": i} for i in HORIZON_IDS]}


def official(state="OK"):
    return {
        "contract": "OFFICIAL_DAILY_COMPASS_v1", "data_status": state,
        "compass_id": "CMP-TEST", "compass_sha256": "a" * 64,
        "source_bindings": {"auto_market_state": {"freshness": {"status": "PASS"}, "packet_sha256": "c" * 64}},
        "capitalization_ladder": [
            {"segment": "BTC", "direction": "BEARISH", "action": "HOLD"},
            {"segment": "MICROCAPS", "direction": "MIXED", "action": "HARD_WAIT"},
            {"segment": "MEMES", "direction": "UNAVAILABLE", "action": "UNAVAILABLE"},
        ],
        "issued_at_utc": "2026-11-07T14:40:49Z", "action_now": "HOLD_WAIT",
        "market_reference": {"btc_usdt": 75936.02, "observation_open_utc": "2026-11-07T13:00:00Z"},
        "horizons": {
            "NEXT_12H": {"expected_direction": "DOWN", "action_posture": "HOLD"},
            "NEXT_1_3D": {"expected_direction": "MIXED", "action_posture": "WAIT"},
            "NEXT_5_7D": {"expected_direction": "MIXED", "action_posture": "WAIT"},
            "NEXT_2_3W": {"expected_direction": "MIXED", "action_posture": "WAIT"},
        },
        "protection_tracker": {"pullback_risk_state": "ELEVATED", "confidence_quality": "LOW"},
        "sell_assessment": {"state": "UNAVAILABLE"},
    }


def pointer(state="OK"):
    return {"contract": "OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1",
            "compass_id": "CMP-TEST", "compass_sha256": "a" * 64,
            "issued_at_utc": "2026-11-07T14:40:49Z", "data_status": state,
            "source_packet_sha256": "c" * 64}


def row(method="STRUCTURE_AND_LIQUIDITY"):
    return {
        "classification": "PRO_ANALYSIS_NONBINDING_UNCALIBRATED", "asset": "BTC",
        "quote": "USD", "method": method, "direction": "MIXED",
        "assessed_at_utc": "2026-11-07T15:14:00Z",
        "source_observed_at_utc": "2026-11-07T14:00:00Z",
        "source_refs": ["https://www.coingecko.com/en/coins/bitcoin"],
        "assumptions": ["Retest possible", "Macro/liquidity conditional"],
        "falsifier": "Sustained original close above breakout and improving breadth",
        "cases": {
            "bear": {"low": 70000, "high": 75000},
            "base": {"low": 73500, "high": 78500},
            "bull": {"low": 78500, "high": 84000},
        },
    }


class TestKompasProChatView(unittest.TestCase):
    def test_full_14_rows_two_tables_and_distinct_pro_analysis(self):
        text = render_chat(ledger(), official(), official_pointer=pointer(), as_of_utc=AS_OF,
                           analyst={"H1_3D": row(), "H1_3M": row("CONDITIONAL_MACRO_CYCLE")},
                           interpretation="Neutral to cautious short-term interpretation.")
        self.assertIn("**Officiel handling:** HOLD_WAIT", text)
        self.assertIn("OBSERVATION DOWN", text)
        self.assertIn("OFFICIAL MIXED", text)
        self.assertIn("PRO ANALYSIS, base 73.500–78.500 USD", text)
        self.assertIn("75.936 USDT", text)
        self.assertIn("## Mit taktiske Kompas", text)
        self.assertIn("## Aktivklasser", text)
        self.assertIn("Pullback Radar:** 3/5", text)
        self.assertIn("SELL UNAVAILABLE", text)
        self.assertIn("| BTC | BEARISH | HOLD |", text)
        self.assertIn("| MICROCAPS | MIXED | HARD_WAIT |", text)
        self.assertIn("H1_3M: bear", text)
        self.assertIn("Kildeobserveret 2026-11-07T14:00:00Z", text)
        self.assertTrue(text.rstrip().endswith("Neutral to cautious short-term interpretation."))
        horizon_lines = text.split("## Horisonter, BTC\n")[1].split("\n## Mit taktiske Kompas")[0]
        self.assertEqual(sum(s.startswith("|") and len(s.split("|")) > 2 and s.split("|")[1].strip() in HORIZON_IDS for s in horizon_lines.splitlines()), 14)

    def test_degraded_official_does_not_remove_pro_analysis(self):
        text = render_chat(ledger(), official("DEGRADED"), official_pointer=pointer("DEGRADED"), as_of_utc=AS_OF,
                           analyst={"H1_3D": row()})
        self.assertIn("Official DEGRADED/EXPIRED", text)
        self.assertNotIn("**Officiel handling:** HOLD_WAIT", text)
        self.assertIn("PRO ANALYSIS, base 73.500–78.500 USD", text)
        self.assertNotIn("OFFICIAL MIXED", text)

    def test_missing_or_mismatched_pointer_fails_closed(self):
        x = render_chat(ledger(), official(), as_of_utc=AS_OF, analyst={"H1_3D": row()})
        self.assertNotIn("**Officiel handling:** HOLD_WAIT", x)
        bad_pointer = pointer()
        bad_pointer["compass_sha256"] = "b" * 64
        x = render_chat(ledger(), official(), official_pointer=bad_pointer, as_of_utc=AS_OF)
        self.assertNotIn("OFFICIAL MIXED", x)

    def test_pointer_packet_mismatch_fails_closed(self):
        bad_pointer = pointer()
        bad_pointer["source_packet_sha256"] = "d" * 64
        x = render_chat(ledger(), official(), official_pointer=bad_pointer, as_of_utc=AS_OF)
        self.assertIn("Official DEGRADED/EXPIRED", x)
        self.assertNotIn("| BTC | BEARISH | HOLD |", x)

    def test_stale_actual_market_observation_cannot_keep_official_action_alive(self):
        x = official()
        x["market_reference"]["observation_open_utc"] = "2026-11-07T11:00:00Z"
        text = render_chat(ledger(), x, official_pointer=pointer(), as_of_utc=AS_OF)
        self.assertIn("Official DEGRADED/EXPIRED", text)
        self.assertNotIn("**Officiel handling:** HOLD_WAIT", text)

    def test_older_weekly_analyst_assessment_cannot_be_current(self):
        x = row("CONDITIONAL_MACRO_CYCLE")
        x["assessed_at_utc"] = "2026-10-27T15:14:00Z"
        x["source_observed_at_utc"] = "2026-10-27T14:00:00Z"
        with self.assertRaisesRegex(ValueError, "ASSESSMENT_EXPIRED"):
            validate_analysis_overlay({"H9_12M": x}, as_of_utc=AS_OF)

    def test_private_source_reference_rejected(self):
        x = row()
        x["source_refs"] = ["https://github.com/Donh91/secrets/blob/main/private.json"]
        with self.assertRaisesRegex(ValueError, "SOURCE_REFERENCES"):
            validate_analysis_overlay({"H1_3D": x}, as_of_utc=AS_OF)

    def test_long_range_cannot_be_naive_volatility_extrapolation(self):
        with self.assertRaisesRegex(ValueError, "LONG_RANGE_EXTRAPOLATION"):
            validate_analysis_overlay({"H9_12M": row("VOLATILITY_BASELINE_ONLY")}, as_of_utc=AS_OF)

    def test_analyst_cannot_claim_official_or_probabilities(self):
        for forbidden, value in (("public_issuance_verified", True), ("official_action", "BUY"), ("probability", 0.9)):
            candidate = row()
            candidate[forbidden] = value
            with self.subTest(forbidden=forbidden), self.assertRaisesRegex(ValueError, "AUTHORITY"):
                validate_analysis_overlay({"H1_3D": candidate}, as_of_utc=AS_OF)

    def test_stale_and_future_analyst_input_rejected(self):
        a = row()
        a["source_observed_at_utc"] = "2026-11-05T14:00:00Z"
        with self.assertRaisesRegex(ValueError, "SOURCE_FUTURE_OR_STALE"):
            validate_analysis_overlay({"H1_3D": a}, as_of_utc=AS_OF)
        b = row()
        b["assessed_at_utc"] = "2026-11-08T15:14:00Z"
        with self.assertRaisesRegex(ValueError, "SOURCE_FUTURE_OR_STALE"):
            validate_analysis_overlay({"H1_3D": b}, as_of_utc=AS_OF)

    def test_invalid_bound_and_missing_bull_case_rejected(self):
        a = row()
        a["cases"]["base"] = {"low": 100000, "high": 1}
        with self.assertRaisesRegex(ValueError, "PRICE_BOUNDS_REVERSED"):
            validate_analysis_overlay({"H1_3D": a}, as_of_utc=AS_OF)
        b = row()
        del b["cases"]["bull"]
        with self.assertRaisesRegex(ValueError, "ALL_THREE"):
            validate_analysis_overlay({"H1_3D": b}, as_of_utc=AS_OF)

    def test_no_analysis_does_not_invent_prices(self):
        text = render_chat(ledger(), official(), official_pointer=pointer(), as_of_utc=AS_OF)
        self.assertNotIn("PRO ANALYSIS, base", text)
        self.assertIn("Ikke udstedt / ingen selvstændig analyse", text)
        self.assertIn("Official OK", text)

    def test_expired_official_cannot_produce_action_or_stale_direction(self):
        x = official()
        x["issued_at_utc"] = "2026-11-06T14:40:49Z"
        text = render_chat(ledger(), x, official_pointer=pointer(), as_of_utc=AS_OF, analyst={"H1_3D": row()})
        self.assertIn("Official DEGRADED/EXPIRED", text)
        self.assertNotIn("OFFICIAL MIXED", text)
        self.assertIn("PRO ANALYSIS, base", text)


if __name__ == "__main__":
    unittest.main()
