"""Adversarial, source-independent tests for equal-width Task2 historical sidecar."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.research import task2_cn_equal_width_sidecar_v1 as s


def base(**kw):
    data = {"week": "39", "asset": "BTC", "target_mature": "True",
            "forecast_available": "True", "prior_week_available": "True",
            "forecast_low": "95", "forecast_high": "115", "prior_close": "100",
            "actual_low": "90", "actual_high": "110", "actual_close": "101",
            "source_clock_class": "ORIGINAL_IN_REPO_ISSUE_AND_FIRST_DELIVERY_CLOCK_NOT_INDEPENDENTLY_PROVED"}
    data.update(kw)
    return data


class EqualWidthSidecarTests(unittest.TestCase):
    def test_equal_width_not_prior_week_low_high(self):
        x = s.compute([base()])["compared_rows"][0]
        self.assertEqual((x["equal_width_prior_low"], x["equal_width_prior_high"]), (90, 110))
        self.assertEqual(x["forecast"]["full_range_covered"], 0)
        self.assertEqual(x["equal_width_prior"]["full_range_covered"], 1)
        self.assertEqual(x["equal_width_prior"]["width_fraction"], x["forecast"]["width_fraction"])

    def test_interval_score_alpha_close_and_breach(self):
        self.assertEqual(s.interval_score_close(90, 110, 100, .2), 20)
        self.assertEqual(s.interval_score_close(90, 110, 85, .2), 70)
        self.assertEqual(s.interval_score_close(90, 110, 115, .2), 70)
        self.assertAlmostEqual(s.compute([base()])["compared_rows"][0]["forecast"]["boundary_breach_fraction"], .05)

    def test_no_claim_of_pit_or_real_skill_even_with_source_marker(self):
        x = s.compute([base(source_clock_class="PIT_VERIFIED")])
        self.assertEqual(x["science_status"], "RETROSPECTIVE_DESCRIPTION_ONLY_NO_MODEL_PROMOTION")
        self.assertEqual(x["compared_rows"][0]["first_in_main_price_control"], "SOURCE_BLOCKED_NO_VERIFIED_ANCHOR_PRICE")
        self.assertFalse(x["compared_rows"][0]["model_promotion"])

    def test_maturity_w46_excluded(self):
        x = s.compute([base(week="46", target_mature="False")])
        self.assertEqual(x["summary_by_asset"]["BTC"]["independent_week_count"], 0)
        self.assertEqual(x["excluded_rows"][0]["reason"], "NOT_MATURE_OR_MISSING_MATCHED_BASELINE")

    def test_missing_bad_or_forged_baseline_cannot_be_scored(self):
        for value in ("", "nan", "Infinity", "-100", "0", None, True):
            with self.subTest(value=value):
                x = s.compute([base(prior_close=value)])
                self.assertEqual(x["summary_by_asset"]["BTC"]["independent_week_count"], 0)

    def test_duplicated_week_asset_fatal_no_inflated_n(self):
        with self.assertRaisesRegex(ValueError, "duplicate independent"):
            s.compute([base(), base()])

    def test_week_asset_separation(self):
        x = s.compute([base(), base(asset="ETH")])
        self.assertEqual(x["summary_by_asset"]["BTC"]["independent_week_count"], 1)
        self.assertEqual(x["summary_by_asset"]["ETH"]["independent_week_count"], 1)
        self.assertEqual(len(x["compared_rows"]), 2)

    def test_invalid_alpha_is_rejected(self):
        for alpha in (-.1, 0, 1, 2, float("nan"), True):
            with self.subTest(alpha=alpha):
                with self.assertRaises(ValueError):
                    s.compute([base()], alpha)

    def test_bad_actual_order_excluded(self):
        x = s.compute([base(actual_low="120")])
        self.assertEqual(x["excluded_rows"][0]["reason"], "INCONSISTENT_RANGE_OR_OUTCOME")

    def test_cli_deterministic_and_hashbound(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, out = Path(tmp)/"source.csv", Path(tmp)/"out"
            with path.open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=base().keys()); w.writeheader(); w.writerow(base())
            s.main(["--input", str(path), "--out", str(out)])
            first = (out/"equal_width_audit.json").read_bytes()
            s.main(["--input", str(path), "--out", str(out)])
            self.assertEqual(first, (out/"equal_width_audit.json").read_bytes())
            j = json.loads(first)
            self.assertEqual(len(j["source_csv_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
