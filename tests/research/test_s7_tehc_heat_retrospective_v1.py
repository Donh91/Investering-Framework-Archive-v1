"""S7 Tehc heat science: offline, deterministic, fail-closed adversarial tests."""
from __future__ import annotations

import copy
import math
import unittest
from datetime import date, datetime, timedelta, timezone

from scripts.research import s7_tehc_heat_retrospective_v1 as m


def sources(n: int = 80):
    start = date(2025, 1, 1)
    days = [(start + timedelta(days=i)).isoformat() for i in range(n)]
    pad = {
        "window": "all", "through": days[-1], "source": m.PROVIDER, "days": days,
        "series": [
            {"chain": "solana", "pad": "pumpfun",
             "volume_usd": [200.0 + 5 * i for i in range(n)],
             "tokens_launched": [10 + i for i in range(n)]},
            {"chain": "robinhood", "pad": "ponsfamily.com",
             "volume_usd": [10.0 + i for i in range(n)],
             "tokens_launched": [1 + i // 10 for i in range(n)]},
        ],
    }
    bots = {
        "window": "all", "chain": "all", "group": "bot",
        "through": days[-1], "source": m.PROVIDER, "days": days,
        "series": [{"name": "fomo", "volume_usd": [70 + 2 * i for i in range(n)],
                    "fees_usd": [3 + i / 10 for i in range(n)]}],
    }
    vendor = {
        "source": m.PROVIDER,
        "method": {"window_days": 90, "window_days_long": 365,
                   "blend": {"short": 0.6, "long": 0.4},
                   "cooldown": 0.65,
                   "weights": dict(zip(m.FIELDS, m.WEIGHTS))},
        "history": [{"day": d, "score": 60} for d in days[30:]],
        "today": {"day": days[-1], "score": 60},
    }
    def kraken(key: str, mult: float):
        candles = []
        for i in range(n):
            timestamp = int(datetime.combine(start + timedelta(days=i),
                                               datetime.min.time(),
                                               tzinfo=timezone.utc).timestamp())
            px = mult * (1 + i * .002)
            candles.append([timestamp, str(px), str(px + 0.1), str(px - 0.1),
                            str(px), str(px), "2", 10])
        return {"error": [], "result": {key: candles, "last": 0}}
    return pad, bots, vendor, kraken("XXBTZUSD", 50000), kraken("SOLUSD", 100)


class TehcScienceTests(unittest.TestCase):
    def setUp(self):
        self.pads, self.bots, self.vendor, self.btc, self.sol = sources()

    def test_replay_has_research_only_authority_and_conservative_entry(self):
        report = m.build(self.pads, self.bots, self.vendor, self.btc, self.sol)
        self.assertEqual(report["contract"], m.CONTRACT)
        self.assertFalse(report["scientific_pit_admission"])
        self.assertFalse(report["prospective_skill"])
        self.assertFalse(report["market_action_authority"])
        self.assertEqual(report["source_census"]["daily_overlap"], 80)
        self.assertEqual(report["source_census"]["vendor_matched"], 50)
        self.assertEqual(report["outcome_entry_policy"], "DAY_D_PLUS_1_UTC_CLOSE_AFTER_DAILY_VENDOR_OBSERVATION")
        self.assertGreater(report["market_retrospective"]["by_year"]["2025"]["all"]["n"], 30)
        self.assertEqual(report["market_retrospective"]["by_year"]["2026"]["all"]["n"], 0)
        self.assertIn("NO", report["classification"].replace("RETROSPECTIVE_METHOD_CHECK_ONLY", "NO"))

    def test_no_future_data_in_percentile_and_current_day_excluded_from_history(self):
        a = m.heat(m.panel(self.pads, self.bots))
        self.assertEqual(a[0]["day"], self.pads["days"][30])
        self.assertAlmostEqual(a[0]["heat_raw"], 100.0)
        self.assertAlmostEqual(a[0]["heat_equal_weight"], 100.0)
        before = copy.deepcopy(a[15])
        # Change a strictly LATER day. Original earlier score must stay identical.
        self.pads["series"][0]["volume_usd"][70] *= 1_000_000
        b = m.heat(m.panel(self.pads, self.bots))
        self.assertEqual(b[15], before)

    def test_kraken_last_uncommitted_is_always_dropped(self):
        original = m.kraken_daily(self.sol, "SOLUSD")
        last = self.sol["result"]["SOLUSD"][-1]
        last[4] = "999999999"
        self.assertEqual(original, m.kraken_daily(self.sol, "SOLUSD"))
        self.assertNotIn(self.pads["days"][-1], original)

    def test_vintage_method_drift_rejected(self):
        self.vendor["method"]["weights"]["bot_fees"] = 0.21
        with self.assertRaisesRegex(ValueError, "VENDOR_METHOD_DRIFT"):
            m.build(self.pads, self.bots, self.vendor, self.btc, self.sol)

    def test_unequal_source_days_do_not_become_zeros(self):
        self.pads["days"].pop(40)
        with self.assertRaisesRegex(ValueError, "SOURCE_METRIC_LENGTH_MISMATCH|SOURCE_DAILY_GAP"):
            m.panel(self.pads, self.bots)

    def test_missing_metric_or_corrupt_source_fails_closed(self):
        self.bots["series"][0]["fees_usd"][11] = None
        with self.assertRaisesRegex(ValueError, "NONFINITE_OR_MISSING_METRIC"):
            m.panel(self.pads, self.bots)

    def test_quote_parity_requires_explicit_kraken_pair(self):
        with self.assertRaisesRegex(ValueError, "KRAKEN_QUOTE_OR_HISTORY_INVALID"):
            m.kraken_daily(self.btc, "XETHZUSD")

    def test_vendor_history_cannot_duplicate_dates(self):
        self.vendor["history"].append(copy.deepcopy(self.vendor["history"][-1]))
        with self.assertRaisesRegex(ValueError, "VENDOR_SCORE_INVALID"):
            m.vendor_index(self.vendor)

    def test_7day_vol_baseline_uses_entry_and_prior_only(self):
        h = m.heat(m.panel(self.pads, self.bots))
        out = m.dated_outcomes(h, m.vendor_index(self.vendor),
                               m.kraken_daily(self.btc, "XXBTZUSD"),
                               m.kraken_daily(self.sol, "SOLUSD"))
        self.assertTrue(out)
        self.assertTrue(all(0 <= x["realized_sol_vol_prev_7d"] < 1 for x in out))
        self.assertLess(max(x["day"] for x in out), self.pads["days"][-1])
        self.assertTrue(all(math.isfinite(x["relative_solbtc_3d_log"]) for x in out))

    def test_percentile_uses_only_matured_earlier_observations(self):
        self.assertEqual(m.percentile(6, [1, 2, 3, 4, 5]), 100.0)
        self.assertEqual(m.percentile(0, [1, 2, 3, 4, 5]), 0.0)
        with self.assertRaisesRegex(ValueError, "NO_PRIOR_HISTORY"):
            m.percentile(1, [])

    def test_vendor_total_cannot_be_counted_as_independent_launches(self):
        self.assertEqual(len(m.panel(self.pads, self.bots)), 80)
        self.assertEqual(len(m.heat(m.panel(self.pads, self.bots))), 50)
        self.assertEqual(m.summary([])["n"], 0)


if __name__ == "__main__":
    unittest.main()
