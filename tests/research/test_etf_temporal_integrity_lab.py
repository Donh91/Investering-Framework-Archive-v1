"""Offline tests for the ETF temporal-integrity lab (research only; no network, no owner path writes)."""
from __future__ import annotations

import gzip
import json
import sys
import unittest
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "scripts/research/etf_temporal_integrity_lab"
RESULTS = ROOT / "research/etf_temporal_integrity/2026-09-23"
sys.path.insert(0, str(LAB))

import etf_lab_common as C  # noqa: E402
import live_schema_lab as S  # noqa: E402
import policies as P  # noqa: E402
import revisions as R  # noqa: E402

ETH11 = S.FROZEN_ETH[:8] + ["MSSE"] + S.FROZEN_ETH[8:]
ROWS = [["18 Sep 2026", "10.0", "0.0", "1.0", "0.0", "0.0", "0.0", "0.0", "0.0", "2.0", "-1.0", "0.0", "12.0"],
        ["21 Sep 2026", "-5.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "0.0", "1.0", "-4.0"]]


def row(asset, day, source, t, headers, values, total, kind="REAL_TIME_CAPTURE", scope="FUND_LEVEL"):
    known = [v for v in values if v is not None] if values is not None else []
    unknown = [h for h, v in zip(headers or [], values or []) if v is None]
    return {"asset": asset, "session_date": day, "observation_source": source, "observation_kind": kind, "value_scope": scope,
            "observed_at_utc": t, "fund_header_set": headers, "fund_values": values, "reported_total": total,
            "calculated_total": sum(known) if values is not None else None,
            "parity": None if total is None or values is None else abs(sum(known) - total) <= max(0.2, abs(total) * 0.01),
            "unknown_cell_count": len(unknown) if values is not None else None, "unknown_funds": unknown,
            "fund_count": len(headers) if headers else None, "verification_completed_at_utc": None, "not_source_revision": None, "notes": None}


class SchemaBindingPrototypeTest(unittest.TestCase):
    def fixtures(self):
        swapped = list(ETH11)
        i, j = swapped.index("ETHE"), swapped.index("ETH")
        swapped[i], swapped[j] = swapped[j], swapped[i]
        return {
            "current": (S.html_new_layout(ETH11, ROWS), True),
            "old_two_row": (S.html_old_two_row(S.FROZEN_ETH, S.ISSUERS_OLD, [r[:9] + r[10:] for r in ROWS]), True),
            "no_total_label": (S.html_new_layout(ETH11, ROWS, total_label="Tot"), False),
            "no_header": ("<table>" + "".join(S._row(r) for r in ROWS) + "</table>", False),
            "unknown_same_width": (S.html_new_layout([("MSSX" if t == "MSSE" else t) for t in ETH11], ROWS), False),
            "reordered": (S.html_new_layout(swapped, ROWS), False),
            "duplicate": (S.html_new_layout([("ETHE" if t == "ETH" else t) for t in ETH11], ROWS), False),
            "short_total_row": (S.html_new_layout(ETH11, [ROWS[0], ROWS[1][:-1]]), False),
        }

    def test_strict_prototype_accepts_registered_and_fails_closed_otherwise(self):
        for name, (html, ok) in self.fixtures().items():
            with self.subTest(name):
                if ok:
                    rows, headers, mode = S.strict_prototype(html, "ETH")
                    self.assertTrue(rows)
                    self.assertIn("STRICT_SOURCE_TICKER_BINDING", mode)
                else:
                    with self.assertRaises(ValueError):
                        S.strict_prototype(html, "ETH")

    def test_known_additive_revision_is_explicit(self):
        _, headers, mode = S.strict_prototype(self.fixtures()["current"][0], "ETH")
        self.assertEqual(headers[1:-1], ETH11)
        self.assertTrue(mode.endswith("KNOWN_ADDITIVE_SCHEMA_REVISION"))


class RevisionTaxonomyTest(unittest.TestCase):
    H = ["IBIT", "FBTC"]

    def test_late_fund_value(self):
        a = row("BTC", "2026-08-17", "FARSIDE_ETF_OWNER_SNAPSHOT_v4", "2026-08-18T02:19:51Z", self.H, [None, 10.0], 10.0)
        b = row("BTC", "2026-08-17", "DAILY_SETTLED_ETF_CALIBRATION_v2", "2026-08-18T07:01:04Z", self.H, [160.2, 10.0], 170.2)
        self.assertEqual(R.compare(a, b)[0], "LATE_FUND_VALUE")

    def test_new_fund_backfill_and_schema_extension(self):
        a = row("ETH", "2026-08-20", "X", "2026-08-21T07:00:00Z", ["ETHA"], [5.0], 5.0)
        b = row("ETH", "2026-08-20", "Y", "2026-09-23T15:29:04Z", ["ETHA", "MSSE"], [5.0, 1.2], 6.2)
        self.assertEqual(R.compare(a, b)[0], "NEW_FUND_BACKFILL")
        c = row("ETH", "2026-08-20", "Y", "2026-09-23T15:29:04Z", ["ETHA", "MSSE"], [5.0, None], 5.0)
        self.assertEqual(R.compare(a, c)[0], "SCHEMA_EXTENSION")

    def test_source_correction_and_total_recompute(self):
        a = row("BTC", "2026-08-10", "X", "2026-08-11T07:00:00Z", self.H, [1.0, 2.0], 3.0)
        self.assertEqual(R.compare(a, row("BTC", "2026-08-10", "Y", "2026-08-12T07:00:00Z", self.H, [1.0, 4.0], 5.0))[0], "SOURCE_CORRECTION")
        self.assertEqual(R.compare(a, row("BTC", "2026-08-10", "Y", "2026-08-12T07:00:00Z", self.H, [1.0, 2.0], 3.4))[0], "TOTAL_RECOMPUTE")

    def test_zero_filled_export_is_not_a_revision(self):
        live = row("BTC", "2025-01-02", "LAB_LIVE_READ_2026_09_23", "2026-09-23T15:29:03Z", self.H, [5.0, None], 5.0)
        pack = row("BTC", "2025-01-02", "TRUTH_LAYER_HISTORY_PACK_v1", "2026-07-26T19:28:44Z", self.H, [5.0, 0.0], 5.0)
        self.assertIsNone(R.compare(pack, live)[0])


class CompletenessRuleTest(unittest.TestCase):
    def test_all_dash_zero_total_is_never_complete(self):
        r = row("BTC", "2026-09-08", "S", "2026-09-09T05:55:36Z", ["IBIT", "FBTC"], [None, None], 0.0)
        self.assertIs(P.complete_live(r, {}), False)

    def test_structural_dash_carries_forward_but_late_fund_does_not(self):
        prev = row("ETH", "2026-08-14", "S", "t", ["ETHA", "MSSE"], [1.0, None], 1.0)
        struct = row("ETH", "2026-08-17", "S", "t", ["ETHA", "MSSE"], [2.0, None], 2.0)
        late = row("ETH", "2026-08-17", "S", "t", ["ETHA", "MSSE"], [None, 3.0], 3.0)
        idx = P.structural_dash_index([prev, struct])
        self.assertIs(P.complete_live(struct, idx), True)
        idx = P.structural_dash_index([prev, late])
        self.assertIs(P.complete_live(late, idx), False)


class PolicyProofLogicTest(unittest.TestCase):
    def test_session_close_is_proven_lookahead_when_first_observation_is_provisional(self):
        H = ["IBIT", "FBTC"]
        led = [
            row("BTC", "2026-08-17", "FARSIDE_ETF_OWNER_SNAPSHOT_v4", "2026-08-18T02:19:51Z", H, [None, 10.0], 10.0),
            row("BTC", "2026-08-17", "DAILY_SETTLED_ETF_CALIBRATION_v2", "2026-08-18T07:01:04Z", H, [160.2, 10.0], 170.2),
            row("BTC", "2026-08-14", "FARSIDE_ETF_OWNER_SNAPSHOT_v4", "2026-08-18T02:19:51Z", H, [1.0, None], 1.0),
        ]
        led[1]["verification_completed_at_utc"] = "2026-08-18T07:01:05Z"
        attempts = [{"lane": "FLO_OWNER_SNAPSHOT", "at": "2026-08-18T02:19:51Z"}]
        res, per, basis = P.evaluate(led, {}, "LATEST_VINTAGE", attempts=attempts)
        key = ("BTC", "2026-08-17")
        self.assertEqual(per[key]["A_SESSION_CLOSE"]["outcome"], "PROVEN_LOOKAHEAD")
        self.assertEqual(per[key]["B_FIRST_OBSERVED"]["outcome"], "REVISED_AFTER_K")
        self.assertEqual(per[key]["C_FIRST_COMPLETE_OBSERVED"]["outcome"], "CONSISTENT_AT_K")
        self.assertEqual(per[key]["D_FIRST_VERIFIED_FINAL_OBSERVED"]["outcome"], "CONSISTENT_AT_K")
        self.assertGreater(basis["L_hours"], 0)


@unittest.skipUnless((RESULTS / "ETF_VINTAGE_LEDGER.jsonl.gz").exists(), "committed results not present")
class CommittedLedgerInvariantsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with gzip.open(RESULTS / "ETF_VINTAGE_LEDGER.jsonl.gz", "rt") as h:
            cls.rows = [json.loads(line) for line in h]

    def test_every_row_has_a_documented_observation_time(self):
        for r in self.rows:
            self.assertTrue(r["observed_at_utc"], r["ledger_key"])
            self.assertTrue(r["observed_at_basis"], r["ledger_key"])

    def test_append_only_key_is_unique(self):
        keys = [r["ledger_key"] for r in self.rows]
        self.assertEqual(len(keys), len(set(keys)))

    def test_no_observation_precedes_its_session_close(self):
        for r in self.rows:
            self.assertGreater(C.ts(r["observed_at_utc"]), C.session_close_utc(r["session_date"]) - timedelta(seconds=1), r["ledger_key"])

    def test_knowledge_time_status_vocabulary(self):
        self.assertLessEqual({r["session"]["knowledge_time_status"] for r in self.rows}, {"OBSERVED", "LOWER_BOUND_ONLY", "UNKNOWN"})


if __name__ == "__main__":
    unittest.main()
