"""Research-only tests for the original Task15 matured-314 cohort replay.

No original ZIP/source values required in PR CI. The executable independently
checks *real* original artifact bytes when supplied; these are structural tests.
"""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "04_MARKET_LEARNING/handlekompas/research/2026-10-16__task2_matured314_reproduce_v1.py"
RECEIPT = Path(__file__).resolve().parents[2] / "04_MARKET_LEARNING/handlekompas/research/2026-10-16__TASK2_TASK15_ORIGINAL_MATURED314_STRATIFIED_DEV_v1.json"
spec = importlib.util.spec_from_file_location("matured314", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def row(model, price, issue, direction="UP", baseline="DOWN"):
    return {"descriptive_hit": "True" if model else "False",
            "baseline_hit": "True" if price else "False",
            "issue_utc": issue, "direction": direction,
            "baseline_direction": baseline}


class Task2Matured314Tests(unittest.TestCase):
    def test_published_aggregate_is_complete_and_non_promoting(self):
        report = json.loads(RECEIPT.read_text())
        census = report["census"]
        self.assertEqual((census["all_original_slots"], census["all_original_matured_in_ledger"],
                          census["all_original_censored_in_ledger"], census["all_original_no_receipt_in_ledger"]),
                         (1140, 358, 570, 212))
        self.assertEqual(census["original_matured_matched"]+census["original_matured_abstained_no_edge_excluded_from_accuracy"], 358)
        self.assertEqual(sum(census["matured_abstained_horizons"].values()), 44)
        self.assertEqual(census["original_matured_matched"]+census["paired_censored_excluded"]
                         +census["paired_original_no_receipt_excluded"], 824)
        cells = report["by_asset_horizon"]
        for key, expected in (("n",314),("compass_hits",145),("price_hits",142),
                              ("disagree",111),("compass_only",57),("price_only",54)):
            self.assertEqual(sum(c[key] for c in cells), expected, key)
        maturity = report["by_asset_horizon_original_maturity_coverage"]
        for key, expected in (("paired",824),("original_matured",314),
                              ("original_censored",500),("original_no_receipt",10)):
            self.assertEqual(sum(c[key] for c in maturity), expected)
        self.assertEqual(report["status"], audit.RESEARCH_ONLY)
        self.assertEqual(census["independent_event_families_certified"], 0)
        self.assertEqual(report["conclusions"]["after_cost_investor_value"], "UNKNOWN")
        self.assertFalse(report["safety"]["live_rules_changed"])

    def test_disagreement_scoring_is_paired_not_double_counted(self):
        items = [row(True,False,"2026-10-01T01:00:00Z"),
                 row(False,True,"2026-10-01T01:00:00Z"),
                 row(True,True,"2026-10-02T01:00:00Z",direction="UP",baseline="UP"),
                 row(False,False,"2026-10-02T01:00:00Z",direction="UP",baseline="UP")]
        out = audit.stats(items)
        self.assertEqual((out["n"],out["compass_hits"],out["price_hits"]), (4,2,2))
        self.assertEqual((out["compass_only"],out["price_only"],out["disagree"]), (1,1,2))
        self.assertEqual(out["lift_pp"],0)

    def test_unmatched_rows_are_never_added_to_accuracy(self):
        items = [row(True,True,"2026-10-01T01:00:00Z"),
                 {"descriptive_hit":"","baseline_hit":"True"},
                 {"descriptive_hit":"False","baseline_hit":""}]
        self.assertEqual(len(audit.paired(items)),1)

    def test_bootstrap_is_seeded_and_cluster_labeled(self):
        items = [row(True,False,"2026-10-01T01:00:00Z"),
                 row(False,True,"2026-10-01T01:00:00Z"),
                 row(True,False,"2026-10-02T01:00:00Z")]
        self.assertEqual(audit.cluster_interval(items,"clock",200),audit.cluster_interval(items,"clock",200))
        self.assertEqual(audit.cluster_interval(items,"date",200)[0],2)
        report=json.loads(RECEIPT.read_text())
        self.assertLess(report["exploratory_cluster_bootstrap"]["by_utc_issue_date"]["lower_pp"],0)
        self.assertGreater(report["exploratory_cluster_bootstrap"]["by_utc_issue_date"]["upper_pp"],0)

    def test_publication_census_does_not_treat_git_committer_clock_as_vendor_pit(self):
        sample = [
            {"prediction_id":f"m{i}","original_outcome_status":"MATURED",
             "publication_minutes_from_due":39.617,
             "archive_publication_class":"PRESENT_BY_90_MIN_CUTOFF",
             "scorer_would_have_received_source":"UNVERIFIED_EXECUTION_CONTEXT",
             "first_present_main_commit":"a"*40,"source_path":"hourly.csv"}
            for i in range(314)
        ] + [
            {"prediction_id":f"c{i}","original_outcome_status":"CENSORED",
             "publication_minutes_from_due":164.333,
             "archive_publication_class":"FIRST_PRESENT_AFTER_90_MIN_CUTOFF",
             "scorer_would_have_received_source":"UNVERIFIED_EXECUTION_CONTEXT",
             "first_present_main_commit":"b"*40,"source_path":"hourly.csv"}
            for i in range(500)
        ]
        metrics=audit.publication_metrics(sample)
        self.assertEqual((metrics["cases"],metrics["matured"],metrics["censored"]),(814,314,500))
        self.assertEqual((metrics["matured_lower_median_minutes"],metrics["censored_lower_median_minutes"]),(39.617,164.333))
        sample[0]["publication_minutes_from_due"]=100
        with self.assertRaisesRegex(ValueError,"PUBLICATION_CLOCK_FALSE_EVIDENCE"):
            audit.publication_metrics(sample)

    def test_wrong_original_artifact_sha_fails_closed_before_reading(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"notoriginal.zip"
            p.write_bytes(b"not a source artifact")
            with self.assertRaisesRegex(ValueError,"ORIGINAL_ACTIONS_ZIP_SHA_MISMATCH"):
                audit.load_original(p)


if __name__ == "__main__":
    unittest.main()
