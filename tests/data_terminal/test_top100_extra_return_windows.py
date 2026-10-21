from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
import urllib.parse
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


OWNER_PATH = Path("scripts/data_terminal/top100_breadth_owner_collector.py")
spec = importlib.util.spec_from_file_location("breadth_extra_window_owner", OWNER_PATH)
owner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(owner)

from scripts.daily_capture import rich_breadth_checkpoint as rich


def fixture(include_windows: bool = True) -> bytes:
    rows = []
    for index in range(101):
        row = {
            "id": "bitcoin" if index == 0 else f"asset-{index}",
            "symbol": "btc" if index == 0 else f"asset{index}",
            "name": f"Asset {index}",
            "market_cap": 10_000_000 - index,
            "current_price": 50 + index,
            "price_change_percentage_24h": 0.1 if index == 0 else 1.5,
        }
        if include_windows:
            row.update({
                "price_change_percentage_7d_in_currency": 2.5 if index != 3 else None,
                "price_change_percentage_30d_in_currency": -4.0 if index != 3 else None,
                "price_change_percentage_200d_in_currency": 12.0 if index != 3 else None,
            })
        rows.append(row)
    return json.dumps(rows, sort_keys=True).encode()


class ExtraWindowCaptureTests(unittest.TestCase):
    def test_legacy_parse_byte_semantics_unchanged(self):
        raw = fixture(False)
        original, old_exclusions, old_aggregate = owner.parse(raw)
        extended, exclusions, aggregate = owner.parse(raw, include_extra_windows=True)
        self.assertEqual(old_aggregate, aggregate)
        self.assertEqual(old_exclusions, exclusions)
        self.assertEqual(len(original), 100)
        self.assertNotIn("extra_return_windows_pct", original[0])
        self.assertEqual(extended[0]["extra_return_windows_pct"], {"7d": None, "30d": None, "200d": None})

    def test_extended_windows_preserve_original_membership_and_24h(self):
        raw = fixture()
        baseline, excluded_old, aggregate_old = owner.parse(raw)
        extended, excluded_new, aggregate_new = owner.parse(raw, include_extra_windows=True)
        self.assertEqual(aggregate_old, aggregate_new)
        self.assertEqual(excluded_old, excluded_new)
        for baseline_row, extended_row in zip(baseline, extended):
            self.assertEqual(baseline_row["asset_id"], extended_row["asset_id"])
            self.assertEqual(baseline_row["change_24h_pct"], extended_row["change_24h_pct"])
            self.assertEqual(extended_row["extra_return_windows_pct"]["7d"], 2.5 if extended_row["source_rank"] != 4 else None)
        self.assertEqual(extended[0]["extra_return_windows_pct"]["30d"], -4.0)
        self.assertEqual(extended[0]["extra_return_windows_pct"]["200d"], 12.0)

    def test_missing_extra_window_is_null_never_zero(self):
        extended, _, _ = owner.parse(fixture(), include_extra_windows=True)
        self.assertEqual(extended[3]["extra_return_windows_pct"], {"7d": None, "30d": None, "200d": None})

    def test_invalid_optional_value_does_not_break_24h_breadth(self):
        for bad in [True, "12.5", float("inf"), float("nan"), [], {}]:
            with self.subTest(bad=str(bad)):
                rows = json.loads(fixture())
                rows[0]["price_change_percentage_30d_in_currency"] = bad
                raw = json.dumps(rows).encode()
                _, _, legacy_aggregate = owner.parse(raw)
                extended, _, original_aggregate = owner.parse(raw, include_extra_windows=True)
                self.assertEqual(legacy_aggregate, original_aggregate)
                self.assertIsNone(extended[0]["extra_return_windows_pct"]["30d"])
                status = owner.extra_window_provenance(extended, raw, "2026-10-21T08:00:00Z")
                self.assertEqual(status["status"], "DEGRADED_OPTIONAL_ONLY")
                self.assertEqual(status["invalid_member_counts"]["30d"], 1)
                self.assertEqual(status["missing_member_counts"]["30d"], 1)
                self.assertFalse(status["authority"]["can_create_outcome_rows"])

    def test_all_optional_fields_absent_stays_null_and_unadmitted(self):
        raw = fixture(include_windows=False)
        extended, _, legacy = owner.parse(raw, include_extra_windows=True)
        status = owner.extra_window_provenance(extended, raw, "2026-10-21T08:00:00Z")
        self.assertEqual(status["status"], "SOURCE_FIELDS_ABSENT_OPTIONAL_ONLY")
        self.assertEqual(status["available_member_counts"], {"7d": 0, "30d": 0, "200d": 0})
        self.assertEqual(status["missing_member_counts"], {"7d": 100, "30d": 100, "200d": 100})
        self.assertEqual(legacy["constituent_count"], 100)
        self.assertFalse(status["provider_first_known_proven"])

    def test_surplus_invalid_window_does_not_poison_selected_members(self):
        # A malformed optional field on nonselected rank 101 cannot cause
        # an outage when every one of the actual 100 members is valid.
        rows = json.loads(fixture())
        rows[100]["price_change_percentage_30d_in_currency"] = "INVALID_SURPLUS"
        selected, _, aggregate = owner.parse(
            json.dumps(rows).encode(), include_extra_windows=True
        )
        self.assertEqual(len(selected), 100)
        self.assertEqual(aggregate["constituent_count"], 100)
        self.assertEqual(selected[-1]["source_rank"], 100)
        # When rank 101 becomes a member, degrade ONLY its optional
        # research window, preserving the original 24h aggregate.
        rows[0]["symbol"] = "usdt"
        raw = json.dumps(rows).encode()
        selected, _, aggregate = owner.parse(raw, include_extra_windows=True)
        legacy, _, old_aggregate = owner.parse(raw)
        self.assertEqual(aggregate, old_aggregate)
        self.assertEqual(selected[-1]["source_rank"], 101)
        self.assertIsNone(selected[-1]["extra_return_windows_pct"]["30d"])
        self.assertEqual(selected[-1]["change_24h_pct"], legacy[-1]["change_24h_pct"])
        capture = owner.extra_window_provenance(selected, raw, "2026-10-21T08:00:00Z")
        self.assertEqual(capture["status"], "DEGRADED_OPTIONAL_ONLY")
        self.assertEqual(capture["invalid_member_counts"]["30d"], 1)
        # One originally missing source value plus rank-101 invalid value => 98 valid.
        self.assertEqual(capture["available_member_counts"]["30d"], 98)
        self.assertEqual(capture["missing_member_counts"]["30d"], 1)
        self.assertFalse(capture["provider_first_known_proven"])

    def test_source_receipt_is_capture_time_only(self):
        raw = fixture()
        constituents, _, aggregate = owner.parse(raw, include_extra_windows=True)
        capture = owner.extra_window_provenance(constituents, raw, "2026-10-21T08:00:00Z")
        self.assertEqual(capture["contract"], "COINGECKO_EXTRA_WINDOWS_CAPTURE_v1")
        self.assertEqual(capture["source_query_price_change_percentage"], "24h,7d,30d,200d")
        self.assertEqual(capture["first_collector_seen_utc"], "2026-10-21T08:00:00Z")
        self.assertEqual(capture["raw_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(capture["membership_hash"], aggregate["membership_hash"])
        self.assertEqual(capture["available_member_counts"], {"7d": 99, "30d": 99, "200d": 99})
        self.assertEqual(capture["missing_member_counts"], {"7d": 1, "30d": 1, "200d": 1})
        self.assertEqual(capture["invalid_member_counts"], {"7d": 0, "30d": 0, "200d": 0})
        self.assertFalse(capture["provider_first_known_proven"])
        self.assertFalse(capture["authority"]["can_create_outcome_rows"])

    def test_owner_legacy_default_preserved(self):
        with tempfile.TemporaryDirectory() as td:
            result = owner.run(fixture(), Path(td), "2026-10-21T08:00:00Z")
            self.assertNotIn("extra_return_capture", result)
            self.assertNotIn("extra_return_windows_pct", result["constituents"][0])
            self.assertEqual(owner.verify(Path(td))["status"], "PASS")

    def test_owner_extended_raw_replay_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = owner.run(fixture(), root, "2026-10-21T08:00:00Z", include_extra_windows=True)
            self.assertEqual(result["aggregate"]["constituent_count"], 100)
            self.assertEqual(result["extra_return_capture"]["available_member_counts"]["7d"], 99)
            self.assertEqual(owner.verify(root)["status"], "PASS")
            snapshot_path = root / "owner_snapshot.json"
            snapshot = json.loads(snapshot_path.read_text())
            snapshot["constituents"][0]["extra_return_windows_pct"]["7d"] = 999.0
            snapshot_path.write_text(json.dumps(snapshot))
            self.assertEqual(owner.verify(root)["status"], "FAIL")

    def test_rich_checkpoint_single_existing_api_call(self):
        raw = fixture()
        with tempfile.TemporaryDirectory() as td:
            with patch.object(rich.owner, "fetch", return_value=raw) as fetching:
                with redirect_stdout(io.StringIO()):
                    result = rich.main(["--output-root", td])
            self.assertEqual(result, 0)
            self.assertEqual(fetching.call_count, 1)
            called = fetching.call_args.args[0]
            query = urllib.parse.parse_qs(urllib.parse.urlparse(called).query)
            self.assertEqual(query["price_change_percentage"], ["24h,7d,30d,200d"])
            saved = json.loads((Path(td) / "LATEST.json").read_text())
            self.assertEqual(saved["aggregate"]["constituent_count"], 100)
            self.assertEqual(saved["extra_return_capture"]["available_member_counts"], {"7d": 99, "30d": 99, "200d": 99})
            self.assertEqual(saved["extra_return_capture"]["raw_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertFalse(saved["authority"]["state_change"])


if __name__ == "__main__":
    unittest.main()
