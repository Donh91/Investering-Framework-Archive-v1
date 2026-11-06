"""Negative controls for the source-gap diagnostic, not price-model accuracy."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from scripts.learning.kompas_pro_source_gap_report_v1 import build_report

ROOT = Path(__file__).resolve().parents[2]
LEDGER = json.loads((ROOT / "07_PROMPTS_AND_AGENTS/action_compass/KOMPAS_PRO_HORIZON_IMPLEMENTATION_LEDGER_v2.json").read_text())
ASOF = "2026-11-06T08:00:00Z"


def sources():
    op = {"contract":"OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1",
          "compass_id":"C1","compass_sha256":"b"*64,
          "issued_at_utc":"2026-11-06T07:30:00Z"}
    official = {"contract":"OFFICIAL_DAILY_COMPASS_v1","data_status":"OK",
                "compass_id":"C1","compass_sha256":"b"*64,
                "issued_at_utc":"2026-11-06T07:30:00Z",
                "market_now":{"directional_state":"BEARISH"},
                "horizons":{"NEXT_1_3D":{"expected_direction":"MIXED"},
                            "NEXT_5_7D":{"expected_direction":"DOWN"},
                            "NEXT_2_3W":{"expected_direction":"MIXED"}}}
    sp = {"contract":"STRATEGIC_COMPASS_LATEST_POINTER_v1","anchor_id":"SC1",
          "anchor_sha256":"a"*64,"issued_at_utc":"2026-11-02T08:19:08Z"}
    anchor = {"contract":"STRATEGIC_COMPASS_ANCHOR_v1","anchor_id":"SC1",
              "anchor_sha256":"a"*64,"issued_at_utc":"2026-11-02T08:19:08Z",
              "strategic_21_30d":{"btc_direction":"MIXED"},
              "cycle_4_8w":{"direction":"UNAVAILABLE"}}
    week = {"daily_price_path":{"contract":"CN_FROZEN_DAILY_PRICE_PATH_v1",
                                 "forecast_week":"2026-W45",
                                 "BTC":{"status":"UNAVAILABLE","points":[]}}}
    return op, official, sp, anchor, week


def run(*s, asof=ASOF):
    return build_report(LEDGER, *s, as_of_utc=asof)


class KompasProSourceGapTests(unittest.TestCase):
    def test_exact14_and_no_price_publication(self):
        report = run(*sources())
        self.assertEqual(report["contract"],"KOMPAS_PRO_SOURCE_GAP_REPORT_v1")
        self.assertEqual(len(report["rows"]),14)
        self.assertEqual(len(set(x["horizon_id"] for x in report["rows"])),14)
        self.assertTrue(all(x["price_status"]=="NOT_ADMITTED" for x in report["rows"]))
        self.assertTrue(all(x["numeric_low"] is None and x["numeric_high"] is None
                            and x["numeric_expected"] is None for x in report["rows"]))
        self.assertFalse(report["scientific_edge_proven"])
        self.assertFalse(report["portfolio_authority"])

    def test_issued_qualitative_directions_are_kept_but_not_priced(self):
        report = run(*sources())
        rows = {r["horizon_id"]:r for r in report["rows"]}
        self.assertEqual(rows["H1_3D"]["direction"],"MIXED")
        self.assertEqual(rows["H5_7D"]["direction"],"DOWN")
        self.assertEqual(rows["H21_30D"]["direction"],"MIXED")
        self.assertEqual(rows["H21_30D"]["direction_authority"],"STRATEGIC_CONTEXT")
        self.assertEqual(rows["H4_8W"]["direction"],"UNAVAILABLE")
        self.assertEqual(rows["H0_12H"]["direction"],"UNAVAILABLE")
        self.assertIn("TWELVE_HOUR_NOWCAST_IS_NOT_PROSPECTIVE_FORECAST",
                      rows["H0_12H"]["reason_codes"])

    def test_monday_daily_path_cannot_be_minted_from_weekly_envelopes(self):
        op,off,sp,a,w=sources()
        w["btc_range_low"],w["btc_range_high"]=72000,84000
        result=run(op,off,sp,a,w)
        self.assertEqual(result["weekly_source_row_count"],0)
        h=next(x for x in result["rows"] if x["horizon_id"]=="H5_7D")
        self.assertIn("ORIGINAL_WEEKLY_SEVEN_DAY_PATH_MISSING",h["reason_codes"])

    def test_even_seven_daily_rows_need_issuer_receipt_and_attestation(self):
        op,off,sp,a,w=sources()
        w["daily_price_path"]["BTC"]={"status":"PUBLISHED",
                                     "points":[{"expected_close":99999} for _ in range(7)]}
        result=run(op,off,sp,a,w)
        self.assertEqual(result["weekly_source_row_count"],7)
        h=next(x for x in result["rows"] if x["horizon_id"]=="H5_7D")
        self.assertIn("SEVEN_DAILY_ROWS_PRESENT_BUT_ISSUANCE_UNATTESTED",h["reason_codes"])
        self.assertEqual(h["price_status"],"NOT_ADMITTED")
        self.assertIsNone(h["numeric_expected"])

    def test_stale_or_mismatched_owner_fails_closed(self):
        op,off,sp,a,w=sources()
        op["compass_sha256"]="c"*64
        result=run(op,off,sp,a,w)
        self.assertFalse(result["source_ids_consistent_and_current"]["official"])
        self.assertEqual(next(x for x in result["rows"] if x["horizon_id"]=="H1_3D")["direction"],"UNAVAILABLE")
        op,off,sp,a,w=sources()
        sp["anchor_sha256"]="c"*64
        result=run(op,off,sp,a,w)
        self.assertFalse(result["source_ids_consistent_and_current"]["strategic"])
        self.assertEqual(next(x for x in result["rows"] if x["horizon_id"]=="H21_30D")["direction"],"UNAVAILABLE")
        op,off,sp,a,w=sources()
        result=run(op,off,sp,a,w,asof="2026-11-07T08:00:00Z")
        self.assertFalse(result["source_ids_consistent_and_current"]["official"])

    def test_no_synthetic_monthly_or_research_prices(self):
        r=run(*sources())
        rows={x["horizon_id"]:x for x in r["rows"]}
        for h in ("H8_14D","H15_21D","H1_3M","H3_6M","H6_9M","H9_12M"):
            self.assertEqual(rows[h]["direction"],"UNAVAILABLE")
            self.assertEqual(rows[h]["price_status"],"NOT_ADMITTED")
            self.assertTrue(len(rows[h]["reason_codes"])>=2)

    def test_bad_ledger_does_not_silently_change_horizon_set(self):
        op,off,sp,a,w=sources()
        mutated=deepcopy(LEDGER)
        mutated["horizons"].pop()
        with self.assertRaisesRegex(ValueError,"CANONICAL_14_HORIZON_LEDGER_REQUIRED"):
            build_report(mutated,op,off,sp,a,w,as_of_utc=ASOF)


if __name__=="__main__":
    unittest.main()
