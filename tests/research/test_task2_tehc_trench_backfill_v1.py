"""Synthetic/adversarial contract tests, no source fetches or forecast promotion."""
from __future__ import annotations

import unittest
import hashlib
import io
import json
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch
from datetime import date, datetime, timedelta, timezone

from scripts.research import task2_tehc_trench_backfill_v1 as m


START = date(2024, 1, 14)
AS_OF = datetime(2025, 2, 20, tzinfo=timezone.utc)


def fixture(length: int = 400):
    days = [(START + timedelta(days=i)).isoformat() for i in range(length)]
    pads = {
        "days": days, "through": days[-1],
        "series": [
            {"chain": "solana", "pad": "pumpfun",
             "volume_usd": [1000 + i * 2 for i in range(length)],
             "tokens_launched": [20 + i % 11 for i in range(length)]},
            {"chain": "robinhood", "pad": "ponsfamily.com",
             "volume_usd": [0 if i < 180 else 100 + i for i in range(length)],
             "tokens_launched": [0 if i < 180 else 8 + i % 9 for i in range(length)]},
        ],
    }
    bots = {
        "days": days, "through": days[-1],
        "series": [
            {"name": "axiom", "volume_usd": [10 + i for i in range(length)],
             "fees_usd": [1 + i / 100 for i in range(length)]}
        ],
    }
    trench = {
        "history": [{"day": d, "score": 30 + (i % 40)} for i, d in enumerate(days)],
        "today": {"day": days[-1], "score": 30 + ((length - 1) % 40)},
    }
    klines = {}
    for k, scale in (("btc", 20000), ("eth", 1500), ("sol", 100)):
        series = []
        for i in range(length + 12):
            d = START + timedelta(days=i)
            val = scale + i * (1 if k == "sol" else 10)
            series.append([int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp()),
                           val, val, val, val, 0, 0, 0])
        klines[k] = {"error": [], "result": {"FAKE_PAIR": series, "last": series[-1][0]}}
    return pads, bots, trench, klines


class TehcHeatOfflineTests(unittest.TestCase):
    def test_fixed_history_no_short_warmup_or_future_rank(self):
        pads, bots, _, _ = fixture()
        out = m.own_history(pads, bots)
        self.assertEqual(len(out), 35)
        self.assertEqual(out[0]["day"], pads["days"][365])
        baseline = [r["own_raw"] for r in out]
        # A huge future day must not change previous-day percentiles.
        pads["series"][0]["volume_usd"][-1] *= 100000
        revised = m.own_history(pads, bots)
        self.assertEqual(baseline[:-1], [r["own_raw"] for r in revised[:-1]])

    def test_zero_ties_explicit_policy(self):
        self.assertEqual(m.percentile(0, [0] * 90, ties="inclusive"), 100)
        self.assertEqual(m.percentile(0, [0] * 90, ties="midrank"), 50)
        with self.assertRaisesRegex(ValueError, "PERCENTILE_TIE_POLICY_INVALID"):
            m.percentile(1, [0], ties="arbitrary")

    def test_duplicated_identity_and_missing_days_fail_closed(self):
        p, b, _, _ = fixture()
        p["series"].append(dict(p["series"][0]))
        with self.assertRaisesRegex(ValueError, "SOURCE_DUPLICATE_SERIES_ID"):
            m.source_daily(p, "pads")
        p["series"].pop()
        p["days"].pop(130)
        with self.assertRaisesRegex(ValueError, "SOURCE_DATES_NOT_CONTIGUOUS"):
            m.source_daily(p, "pads")

    def test_not_available_is_not_zero_and_negative_refused(self):
        p, b, _, _ = fixture()
        p["series"][0]["tokens_launched"][60] = None
        with self.assertRaisesRegex(ValueError, "SOURCE_VALUE_NOT_NUMERIC"):
            m.source_daily(p, "pads")
        p["series"][0]["tokens_launched"][60] = -1
        with self.assertRaisesRegex(ValueError, "SOURCE_VALUE_INVALID"):
            m.source_daily(p, "pads")

    def test_as_of_gate_excludes_unfinished_kraken_candles(self):
        _, _, _, prices = fixture()
        as_of = datetime.combine(START + timedelta(days=399), datetime.min.time(), tzinfo=timezone.utc)
        rows = m.kraken_daily(prices["sol"], as_of)
        self.assertEqual(rows[ (START + timedelta(days=398)).isoformat()], 498)
        self.assertNotIn((START + timedelta(days=399)).isoformat(), rows)
        self.assertNotIn((START + timedelta(days=400)).isoformat(), rows)


    def test_real_kraken_decimal_string_close_and_bad_strings(self):
        _, _, _, price = fixture()
        series = price["sol"]["result"]["FAKE_PAIR"]
        day = (START + timedelta(days=398)).isoformat()
        series[398][4] = "123.45670000"
        out = m.kraken_daily(price["sol"], AS_OF)
        self.assertAlmostEqual(out[day], 123.4567)
        for invalid in ("NaN", "Infinity", " 123 ", "-1", "1,234", "", "0e999"):
            with self.subTest(invalid=invalid):
                series[398][4] = invalid
                with self.assertRaises((ValueError, OverflowError)):
                    m.kraken_daily(price["sol"], AS_OF)

    def test_last_kraken_provider_row_is_partial_even_after_archive_matures(self):
        _, _, _, price = fixture()
        series = price["sol"]["result"]["FAKE_PAIR"]
        last_day = (START + timedelta(days=len(series)-1)).isoformat()
        much_later = datetime(2027, 1, 1, tzinfo=timezone.utc)
        out = m.kraken_daily(price["sol"], much_later)
        self.assertIn((START + timedelta(days=len(series)-2)).isoformat(), out)
        self.assertNotIn(last_day, out)

    def test_vendor_zero_score_to_positive_warming_not_silently_lost(self):
        pads, bots, trench, prices = fixture()
        for entry in trench["history"]:
            entry["score"] = 0
        trench["history"][371]["score"] = 10
        trench["today"]["score"] = 0
        out = m.evaluate(pads, bots, trench, prices, as_of=AS_OF)
        self.assertEqual(out["outcomes"]["groups"]["cold_warming_delta_gte5"]["n"], 1)


    def test_cli_emits_exact_current_input_sha256_without_pit_claim(self):
        pads, bots, trench, kraken = fixture()
        source = {"pads": pads, "bots": bots, "trench": trench, **kraken}
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as td:
            flags = ["tehc-replay", "--as-of-utc", AS_OF.isoformat()]
            hashes = {}
            for key, data in source.items():
                path = Path(td) / (key + ".json")
                raw = json.dumps(data, sort_keys=True).encode("utf-8")
                path.write_bytes(raw)
                hashes[key] = hashlib.sha256(raw).hexdigest()
                flags += ["--" + key, str(path)]
            with patch.object(sys, "argv", flags), redirect_stdout(output):
                m.main()
            parsed = json.loads(output.getvalue())
        self.assertEqual(parsed["snapshot_input_sha256"], hashes)
        self.assertEqual(parsed["snapshot_hash_scope"],
                         "CURRENT_REPLAY_BYTES_ONLY_NOT_HISTORICAL_FIRST_KNOWN")
        self.assertFalse(parsed["original_point_in_time_source_attested"])


    def test_reconstruction_never_reads_future_source_or_vendor_days(self):
        pads, bots, trench, prices = fixture()
        historical_as_of = datetime(2025, 1, 20, tzinfo=timezone.utc)
        past = m.evaluate(pads, bots, trench, prices, as_of=historical_as_of)
        self.assertEqual(past["reconstruction"]["last_day"], "2025-01-19")
        self.assertLess(past["reconstruction"]["n"], 35)
        self.assertIsNone(past["outcomes"]["first_day"])
        # Subsequent as-of future values must not change past diagnostics.
        pads["series"][0]["volume_usd"][-1] *= 100000
        bots["series"][0]["fees_usd"][-1] *= 100000
        trench["history"][-1]["score"] = 0
        trench["today"]["score"] = 0
        after = m.evaluate(pads, bots, trench, prices, as_of=historical_as_of)
        self.assertEqual(past["reconstruction"], after["reconstruction"])
        self.assertEqual(past["outcomes"], after["outcomes"])
        self.assertFalse(after["predictive_edge_admitted"])

    def test_no_prospective_or_market_authority(self):
        pads, bots, trench, kraken = fixture()
        output = m.evaluate(pads, bots, trench, kraken, as_of=AS_OF)
        self.assertEqual(output["contract"], m.CONTRACT)
        self.assertEqual(output["reconstruction"]["n"], 35)
        self.assertGreater(output["outcomes"]["n"], 0)
        self.assertLess(output["outcomes"]["n"], output["reconstruction"]["n"])
        self.assertEqual(output["classification"], "RETROSPECTIVE_VENDOR_BACKFILL_ONLY")
        self.assertFalse(output["original_point_in_time_source_attested"])
        self.assertFalse(output["original_forecast_issued_or_delivered"])
        self.assertFalse(output["predictive_edge_admitted"])
        self.assertFalse(output["action_or_production_authority"])
        self.assertFalse(output["new_scheduled_poll"])
        self.assertEqual(output["calculation"]["lookback_days"], [90, 365])

    def test_bad_asof_and_vendor_score_rejected(self):
        pads, bots, trench, prices = fixture()
        with self.assertRaisesRegex(ValueError, "AS_OF_UTC_REQUIRED"):
            m.evaluate(pads, bots, trench, prices, as_of=datetime(2025, 3, 1))
        trench["history"][-1]["score"] = 101
        with self.assertRaisesRegex(ValueError, "VENDOR_HISTORY_INVALID"):
            m.evaluate(pads, bots, trench, prices, as_of=AS_OF)

    def test_completeness_does_not_treat_source_gap_as_zero(self):
        pads, bots, _, _ = fixture()
        bots["days"].pop(300)
        with self.assertRaisesRegex(ValueError, "SOURCE_DATES_NOT_CONTIGUOUS"):
            m.own_history(pads, bots)

    def test_no_quiet_claim_from_vendor_score(self):
        pads, bots, trench, prices = fixture()
        out = m.evaluate(pads, bots, trench, prices, as_of=AS_OF, ties="midrank")
        self.assertTrue(out["vendor_calendar_day_is_not_first_available_at"])
        self.assertTrue(out["outcomes"]["overlapping_targets_are_not_independent"])
        self.assertTrue(out["outcomes"]["thresholds_explored_after_outcomes_no_confirmatory_claim"])


if __name__ == "__main__":
    unittest.main()
