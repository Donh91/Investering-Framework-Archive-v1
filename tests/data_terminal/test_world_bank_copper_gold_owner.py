from __future__ import annotations

import importlib.util
import csv
import io
import json
import sys
import tempfile
import unittest
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts/data_terminal/world_bank_copper_gold_owner.py"
SPEC = importlib.util.spec_from_file_location("world_bank_copper_gold_owner", MODULE_PATH)
owner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = owner
assert SPEC.loader is not None
SPEC.loader.exec_module(owner)


def column_name(index: int) -> str:
    value, output = index + 1, ""
    while value:
        value, remainder = divmod(value - 1, 26)
        output = chr(65 + remainder) + output
    return output


def periods(start_year: int = 2017, start_month: int = 1, count: int = 115) -> list[str]:
    output = []
    year, month = start_year, start_month
    for _ in range(count):
        output.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            year, month = year + 1, 1
    return output


def workbook(source_periods: list[str], duplicate: bool = False, missing_gold: bool = False, unit_drift: bool = False) -> bytes:
    rows: list[list[object | None]] = [
        ["World Bank Commodity Price Data (The Pink Sheet)"],
        ["monthly prices in nominal US dollars"],
        ["Updated on August 04, 2026"],
        ["Date", "Copper", "Gold"],
        [None, "($/lb)" if unit_drift else "($/mt)", "($/troy oz)"],
    ]
    for index, period in enumerate(source_periods):
        rows.append([
            period.replace("-", "M"),
            7000.0 + index * 10,
            None if missing_gold and index == 3 else 1200.0 + index * 2,
        ])
    if duplicate:
        rows.append(rows[-1])
    shared: list[str] = []
    shared_ids: dict[str, int] = {}

    def shared_id(value: str) -> int:
        if value not in shared_ids:
            shared_ids[value] = len(shared)
            shared.append(value)
        return shared_ids[value]

    xml_rows = []
    for row_number, row in enumerate(rows, 1):
        cells = []
        for index, value in enumerate(row):
            if value is None:
                continue
            reference = f"{column_name(index)}{row_number}"
            if isinstance(value, str):
                cells.append(f'<c r="{reference}" t="s"><v>{shared_id(value)}</v></c>')
            else:
                cells.append(f'<c r="{reference}"><v>{value}</v></c>')
        xml_rows.append(f'<row r="{row_number}">{"".join(cells)}</row>')
    shared_xml = "".join(f"<si><t>{value}</t></si>" for value in shared)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "xl/sharedStrings.xml",
            f'<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">{shared_xml}</sst>',
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
            + "".join(xml_rows)
            + "</sheetData></worksheet>",
        )
    return stream.getvalue()


def build_fixture(source_periods: list[str] | None = None, **kwargs):
    return owner.build(
        workbook(source_periods or periods(), **kwargs),
        "2026-08-27T12:00:00Z",
        "https://example.test/monthly.xlsx",
    )


class WorldBankCopperGoldOwnerTests(unittest.TestCase):
    def test_components_units_ratio_and_features_are_explicit(self):
        data = build_fixture()
        row = data["monthly"][0]
        expected = (7000.0 / 1000) / (1200.0 / owner.TROY_OUNCE_KILOGRAMS)
        self.assertAlmostEqual(row["ratio"], expected, places=12)
        self.assertEqual(row["copper_source_unit"], "USD_PER_METRIC_TON")
        self.assertEqual(row["gold_source_unit"], "USD_PER_TROY_OUNCE")
        self.assertEqual(row["source_timestamp"], "2017-01-31T23:59:59Z")
        self.assertIsNotNone(data["monthly"][-1]["roc_12m_pct"])
        self.assertIsNotNone(data["monthly"][-1]["zscore_24m_population"])

    def test_both_settled_anchors_exclude_unfinished_partner_month(self):
        data = build_fixture()
        self.assertEqual(set(data["settled_2m"]), {"JAN_FEB", "FEB_MAR"})
        self.assertTrue(all(int(row["bar_end_period"][-2:]) % 2 == 0 for row in data["settled_2m"]["JAN_FEB"]))
        self.assertTrue(all(int(row["bar_end_period"][-2:]) % 2 == 1 for row in data["settled_2m"]["FEB_MAR"]))
        self.assertTrue(all(row["settled"] is True for rows in data["settled_2m"].values() for row in rows))
        self.assertFalse(data["validation"]["in_progress_2m_bar_used"])

    def test_gap_duplicate_missing_and_unit_drift_fail_closed(self):
        with self.assertRaisesRegex(owner.OwnerError, "Non-contiguous"):
            build_fixture([*periods(count=100)[:50], *periods(count=100)[51:]])
        with self.assertRaisesRegex(owner.OwnerError, "Duplicate"):
            build_fixture(duplicate=True)
        with self.assertRaisesRegex(owner.OwnerError, "Missing or non-numeric Gold"):
            build_fixture(missing_gold=True)
        with self.assertRaisesRegex(owner.OwnerError, "Unexpected units"):
            build_fixture(unit_drift=True)

    def test_stale_source_is_not_pass(self):
        data = owner.build(workbook(periods(start_year=2015, count=100)), "2026-08-27T12:00:00Z")
        self.assertEqual(data["status"], "STALE")
        self.assertEqual(data["freshness"]["status"], "STALE")

    def test_future_source_timestamp_is_rejected(self):
        with self.assertRaisesRegex(owner.OwnerError, "after retrieval"):
            owner.build(workbook(periods(start_year=2018, count=104)), "2026-08-01T00:00:00Z")

    def test_output_is_idempotent_by_payload_hash_and_zero_authority(self):
        data = build_fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = owner.write_artifacts(root, data)
            revision = root / first["revision_path"]
            revision_bytes = revision.read_bytes()
            second = owner.write_artifacts(root, data)
            self.assertEqual(first["payload_sha256"], second["payload_sha256"])
            self.assertEqual(revision.read_bytes(), revision_bytes)
            self.assertEqual(len(list((root / "revisions").glob("*.json"))), 1)
            self.assertFalse(json.loads((root / "ARTIFACT_MANIFEST.json").read_text())["authority"]["execution_authority"])

    def test_changed_payload_writes_compact_component_delta_not_full_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = build_fixture()
            owner.write_artifacts(root, first)
            changed_periods = periods(count=116)
            second = owner.build(workbook(changed_periods), "2026-09-30T12:00:00Z")
            latest = owner.write_artifacts(root, second)
            receipt = json.loads((root / latest["revision_path"]).read_text())
            self.assertEqual(receipt["revision_kind"], "SOURCE_PAYLOAD_CHANGE")
            self.assertEqual(receipt["component_deltas"], [{
                "change_type": "ADDED",
                "current_copper_source_value": "8150.0",
                "current_gold_source_value": "1430.0",
                "period": "2026-08",
                "previous_copper_source_value": None,
                "previous_gold_source_value": None,
            }])
            self.assertNotIn("monthly", receipt)
            self.assertEqual(len(list((root / "revisions").glob("*.json"))), 2)

    def test_no_silent_network_fallback(self):
        with mock.patch.object(owner.urllib.request, "urlopen", side_effect=OSError("offline")):
            with self.assertRaises(owner.OwnerError) as caught:
                owner.fetch_payload("https://example.invalid", timeout=0.1, retries=0, backoff=0)
        self.assertEqual(caught.exception.status, "NETWORK_ERROR")

    def test_registry_matches_current_source_and_has_no_fallback(self):
        registry = json.loads((ROOT / "02_DATA_PING/data_terminal/source_registry/world_bank_pink_sheet_copper_gold.json").read_text())
        self.assertEqual(registry["url"], owner.SOURCE_URL)
        self.assertEqual(registry["source_id"], owner.SOURCE_ID)
        self.assertEqual(registry["fallback"], "NONE")
        self.assertFalse(registry["authority"]["portfolio_action"])

    def assert_artifacts_are_complete_and_manifest_bound(self, root):
        latest = json.loads((root / "LATEST.json").read_text())
        with (root / "normalized/monthly_observations.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertGreaterEqual(len(rows), 100)
        first_year, first_month = map(int, rows[0]["period"].split("-"))
        self.assertEqual([row["period"] for row in rows], periods(first_year, first_month, len(rows)))
        self.assertEqual(latest["last_period"], rows[-1]["period"])
        self.assertEqual(latest["latest_monthly"]["period"], rows[-1]["period"])
        freshness = latest["freshness"]
        source_timestamp = owner.period_end_iso(rows[-1]["period"])
        self.assertEqual(freshness["latest_source_timestamp"], source_timestamp)
        age = int((owner.parse_timestamp(latest["retrieved_at_utc"]) - owner.parse_timestamp(source_timestamp)).total_seconds())
        self.assertGreaterEqual(age, 0)
        self.assertEqual(freshness["freshness_seconds"], age)
        expected_status = "PASS" if age <= freshness["stale_after_seconds"] else "STALE"
        self.assertEqual(latest["status"], expected_status)
        self.assertEqual(freshness["status"], expected_status)
        revision = json.loads((root / latest["revision_path"]).read_text())
        self.assertEqual(revision["source"]["payload_sha256"], latest["payload_sha256"])
        self.assertEqual(revision["coverage"], {
            "first_period": rows[0]["period"],
            "last_period": rows[-1]["period"],
            "observations": len(rows),
        })
        manifest = json.loads((root / "ARTIFACT_MANIFEST.json").read_text())
        self.assertEqual(set(manifest["members"]), {
            latest["revision_path"], "LATEST.json",
            "normalized/monthly_observations.csv", "derived/settled_2m_features.csv",
        })
        for relative_path, expected_hash in manifest["members"].items():
            self.assertEqual(owner.sha256_bytes((root / relative_path).read_bytes()), expected_hash)
        self.assertFalse(manifest["authority"]["execution_authority"])

    def test_committed_capture_is_complete_and_manifest_bound(self):
        self.assert_artifacts_are_complete_and_manifest_bound(ROOT / "03_DAILY_CAPTURE_LOGS/slow_cycle/copper_gold")

    def test_capture_integrity_accepts_new_publication_and_year_rollover(self):
        # The daily workflow collects before testing. A valid publication must
        # not be rejected just because July 2026 was the original fixture end.
        for count, retrieved_at in [(115, "2026-08-27T12:00:00Z"),
                                    (116, "2026-09-07T12:00:00Z"),
                                    (120, "2027-01-07T12:00:00Z"),
                                    (121, "2027-02-07T12:00:00Z")]:
            with self.subTest(count=count), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                owner.write_artifacts(root, owner.build(workbook(periods(count=count)), retrieved_at))
                self.assert_artifacts_are_complete_and_manifest_bound(root)

    def test_capture_integrity_rejects_corrupted_manifest_member(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            owner.write_artifacts(root, build_fixture())
            member = root / "derived/settled_2m_features.csv"
            member.write_bytes(member.read_bytes() + b"corrupted\n")
            with self.assertRaises(AssertionError):
                self.assert_artifacts_are_complete_and_manifest_bound(root)
