"""Native adversarial tests for full-history CN source census.

They assert *no PIT or skill promotion* when original first-known/user delivery
is missing, even when a historical Git file and later outcome both exist.
"""
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.research import task2_cn_all_archives_provenance_v1 as engine


class AllArchiveCensusTests(unittest.TestCase):
    def test_no_lookahead_asof_boundary(self):
        self.assertEqual(engine.next_monday(2026, 46).isoformat(), "2026-11-16T00:00:00+00:00")
        self.assertEqual(engine.next_monday(2026, 45).isoformat(), "2026-11-09T00:00:00+00:00")

    def test_numeric_ranges_reject_bool_nan_infinity(self):
        self.assertFalse(engine.valid_number(True))
        self.assertFalse(engine.valid_number(float("inf")))
        self.assertFalse(engine.valid_number(float("nan")))
        self.assertFalse(engine.valid_number(None))
        self.assertTrue(engine.valid_number(79500))

    def test_outcome_index_has_same_pinned_git_tree_as_source_index(self):
        """Outcome and CN inventories identify one independently checked Git tree."""
        src = engine.load_json(engine.ROOT / engine.SOURCE_INDEX)
        outcome = engine.load_json(engine.ROOT / engine.OUTCOME_INDEX)
        self.assertRegex(src["source_tree_sha_at_inventory"], r"^[0-9a-f]{40}$")
        self.assertEqual(outcome["source_main_tree"], src["source_tree_sha_at_inventory"])
        self.assertEqual(outcome["entry_count"], 53)

    def test_pinned_source_index_covers_all_research(self):
        result = engine.check_inventory(engine.ROOT)
        self.assertGreaterEqual(result["source_file_count"], 2559)
        groups = result["source_file_categories"]
        for key in ("CN_ARCHIVE", "TASK2_AND_RESEARCH_LAB",
                    "HISTORICAL_REALITY_ENGINE", "MASTER_MONDAY_ORIGINAL_ARCHIVE"):
            self.assertGreater(groups[key], 0)

    def test_legacy_may_august_recoveries_not_ex_ante(self):
        rows = engine.legacy_census(engine.ROOT)
        self.assertGreaterEqual(len(rows), 15)
        recovered = [x for x in rows if x["recovered"]]
        self.assertGreater(len(recovered), 0)
        self.assertTrue(all(x["numeric_forecast_eligible"] is False for x in rows))
        self.assertTrue(all(x["publication_issue_time"] == "UNKNOWN_NOT_PROVEN" for x in rows))
        self.assertTrue(all(x["reason"] == "RECOVERED_NOT_ISSUED" for x in recovered if "_RECOVERED" in x["path"]))

    def test_full_census_has_w36_to_w46_and_frozen_controls(self):
        asof = dt.datetime(2026, 11, 13, 12, 59, tzinfo=dt.timezone.utc)
        rows = engine.week_census(engine.ROOT, asof)
        byweek = {row["iso_week"]: row for row in rows}
        for w in range(36, 47):
            self.assertIn(f"2026-W{w:02d}", byweek)
        self.assertFalse(byweek["2026-W36"]["assets"]["BTC"]["range_issued"])
        self.assertFalse(byweek["2026-W38"]["assets"]["ETH"]["range_issued"])
        self.assertTrue(byweek["2026-W39"]["assets"]["BTC"]["range_issued"])
        self.assertEqual(byweek["2026-W46"]["maturity"], "UNMATURED_OR_GAPPED")
        self.assertEqual(byweek["2026-W46"]["statistical_claim"], "NONE_PIT_UNVERIFIED")
        self.assertEqual(byweek["2026-W45"]["provider_first_published"], "UNKNOWN")
        self.assertEqual(byweek["2026-W45"]["consumer_first_delivered"], "UNKNOWN")
        self.assertGreater(byweek["2026-W40"]["internal_claim_count"], 0)

    def test_missing_indexed_week_directory_fails_closed_before_scoring(self):
        # Mutation-sensitive: without the frozen-directory census, glob silently
        # omits W39 and only reaches FROZEN_SOURCE_BYTES_DRIFT for other mock weeks.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (engine.SOURCE_INDEX, engine.OUTCOME_INDEX):
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((engine.ROOT / rel).read_bytes())
            src = engine.load_json(root / engine.SOURCE_INDEX)
            original = [
                row["path"] for row in src["entries"]
                if engine.re.fullmatch(
                    r"05_CYCLE_NAVIGATOR/weekly/[0-9]{4}/W[0-9]{2}/CYCLE_NAVIGATOR_FORECAST_FREEZE[.]json",
                    row["path"])
            ]
            self.assertEqual(len(original), 11)
            for rel in original:
                if "/W39/" in rel:
                    continue  # simulate silent disappearance of entire W39
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("{}")
            with self.assertRaisesRegex(ValueError, "FROZEN_WEEKLY_SOURCE_SET_DRIFT"):
                engine.week_census(root, dt.datetime(2026, 11, 13, tzinfo=dt.timezone.utc))

    def test_extra_unindexed_week_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (engine.SOURCE_INDEX, engine.OUTCOME_INDEX):
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((engine.ROOT / rel).read_bytes())
            src = engine.load_json(root / engine.SOURCE_INDEX)
            original = [
                row["path"] for row in src["entries"]
                if engine.re.fullmatch(
                    r"05_CYCLE_NAVIGATOR/weekly/[0-9]{4}/W[0-9]{2}/CYCLE_NAVIGATOR_FORECAST_FREEZE[.]json",
                    row["path"])
            ]
            for rel in original:
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("{}")
            extra = root / "05_CYCLE_NAVIGATOR/weekly/2026/W47/CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
            extra.parent.mkdir(parents=True, exist_ok=True)
            extra.write_text("{}")
            with self.assertRaisesRegex(ValueError, "FROZEN_WEEKLY_SOURCE_SET_DRIFT"):
                engine.week_census(root, dt.datetime(2026, 11, 13, tzinfo=dt.timezone.utc))

    def test_no_maturity_before_week_close(self):
        asof = dt.datetime(2026, 11, 8, 23, 59, tzinfo=dt.timezone.utc)
        rows = engine.week_census(engine.ROOT, asof)
        byweek = {row["iso_week"]: row for row in rows}
        self.assertEqual(byweek["2026-W45"]["maturity"], "UNMATURED_OR_GAPPED")

    def test_existing_native_pr2113_artifacts_are_not_fabricated(self):
        result = engine.optional_realdata(None)
        self.assertEqual(result["forecast_rows.csv"]["status"], "NOT_ATTACHED")
        self.assertEqual(result["risk_rows.csv"]["status"], "NOT_ATTACHED")

    def test_wrong_csv_digest_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"forecast_rows.csv"
            path.write_text("intentional adversarial corruption\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "REALDATA_ARTIFACT_HASH_MISMATCH"):
                engine.optional_realdata(Path(tmp))

    def test_changed_forecast_bytes_rejected_against_source_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (engine.SOURCE_INDEX, engine.OUTCOME_INDEX):
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((engine.ROOT / rel).read_bytes())
            rel = "05_CYCLE_NAVIGATOR/weekly/2026/W39/CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
            altered = root / rel
            altered.parent.mkdir(parents=True, exist_ok=True)
            altered.write_text('{"btc_range_low": 1, "btc_range_high": 99999999}')
            with self.assertRaisesRegex(ValueError, "FROZEN_SOURCE_BYTES_DRIFT"):
                engine.pinned_bytes(altered, root)

    def test_source_index_self_rewrite_rejected_even_if_content_valid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in (engine.SOURCE_INDEX, engine.OUTCOME_INDEX):
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((engine.ROOT / rel).read_bytes())
            src = root / engine.SOURCE_INDEX
            src.write_bytes(src.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "SOURCE_INDEX_BLOB_CHANGED"):
                engine.pinned_source_map(str(root.resolve()))

    def test_duplicate_inventory_paths_rejected(self):
        index = json.loads((engine.ROOT / engine.SOURCE_INDEX).read_text())
        outcomes = json.loads((engine.ROOT / engine.OUTCOME_INDEX).read_text())
        index["entries"].append(index["entries"][0])
        index["scan_total"] += 1
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root/engine.SOURCE_INDEX).parent.mkdir(parents=True, exist_ok=True)
            (root/engine.SOURCE_INDEX).write_text(json.dumps(index))
            (root/engine.OUTCOME_INDEX).write_text(json.dumps(outcomes))
            with self.assertRaisesRegex(ValueError, "DUPLICATE_SOURCE_PATH"):
                engine.check_inventory(root)

    def test_source_provenance_and_missingness_cannot_be_promoted(self):
        asof = dt.datetime(2026, 11, 13, 12, 59, tzinfo=dt.timezone.utc)
        result = engine.generate(engine.ROOT, asof)
        self.assertFalse(any(x["statistical_claim"] != "NONE_PIT_UNVERIFIED"
                             for x in result["weekly"]))
        self.assertGreater(result["coverage"]["cn_legacy_recovered_files"], 0)
        self.assertGreater(result["coverage"]["legacy_monday_files"], 0)
        self.assertGreater(result["coverage"]["weekly_raw_outcome_packs"], 0)
        self.assertEqual(result["realdata_verified"]["risk_rows.csv"]["status"], "NOT_ATTACHED")


if __name__ == "__main__":
    unittest.main()
