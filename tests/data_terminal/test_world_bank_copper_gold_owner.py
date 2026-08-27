from __future__ import annotations

import importlib.util
import csv
import io
import json
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

import pytest


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


def test_components_units_ratio_and_features_are_explicit():
    data = build_fixture()
    row = data["monthly"][0]
    expected = (7000.0 / 1000) / (1200.0 / owner.TROY_OUNCE_KILOGRAMS)
    assert row["ratio"] == pytest.approx(expected)
    assert row["copper_source_unit"] == "USD_PER_METRIC_TON"
    assert row["gold_source_unit"] == "USD_PER_TROY_OUNCE"
    assert row["source_timestamp"] == "2017-01-31T23:59:59Z"
    assert data["monthly"][-1]["roc_12m_pct"] is not None
    assert data["monthly"][-1]["zscore_24m_population"] is not None


def test_both_settled_anchors_exclude_unfinished_partner_month():
    data = build_fixture()
    assert set(data["settled_2m"]) == {"JAN_FEB", "FEB_MAR"}
    assert all(int(row["bar_end_period"][-2:]) % 2 == 0 for row in data["settled_2m"]["JAN_FEB"])
    assert all(int(row["bar_end_period"][-2:]) % 2 == 1 for row in data["settled_2m"]["FEB_MAR"])
    assert all(row["settled"] is True for rows in data["settled_2m"].values() for row in rows)
    assert data["validation"]["in_progress_2m_bar_used"] is False


def test_gap_duplicate_missing_and_unit_drift_fail_closed():
    with pytest.raises(owner.OwnerError, match="Non-contiguous"):
        build_fixture([*periods(count=100)[:50], *periods(count=100)[51:]])
    with pytest.raises(owner.OwnerError, match="Duplicate"):
        build_fixture(duplicate=True)
    with pytest.raises(owner.OwnerError, match="Missing or non-numeric Gold"):
        build_fixture(missing_gold=True)
    with pytest.raises(owner.OwnerError, match="Unexpected units"):
        build_fixture(unit_drift=True)


def test_stale_source_is_not_pass():
    data = owner.build(workbook(periods(start_year=2015, count=100)), "2026-08-27T12:00:00Z")
    assert data["status"] == "STALE"
    assert data["freshness"]["status"] == "STALE"


def test_future_source_timestamp_is_rejected():
    with pytest.raises(owner.OwnerError, match="after retrieval"):
        owner.build(workbook(periods(start_year=2018, count=104)), "2026-08-01T00:00:00Z")


def test_output_is_idempotent_by_payload_hash_and_zero_authority():
    data = build_fixture()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = owner.write_artifacts(root, data)
        revision = root / first["revision_path"]
        revision_bytes = revision.read_bytes()
        second = owner.write_artifacts(root, data)
        assert first["payload_sha256"] == second["payload_sha256"]
        assert revision.read_bytes() == revision_bytes
        assert len(list((root / "revisions").glob("*.json"))) == 1
        assert json.loads((root / "ARTIFACT_MANIFEST.json").read_text())["authority"]["execution_authority"] is False


def test_changed_payload_writes_compact_component_delta_not_full_history():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first = build_fixture()
        owner.write_artifacts(root, first)
        changed_periods = periods(count=116)
        second = owner.build(workbook(changed_periods), "2026-09-30T12:00:00Z")
        latest = owner.write_artifacts(root, second)
        receipt = json.loads((root / latest["revision_path"]).read_text())
        assert receipt["revision_kind"] == "SOURCE_PAYLOAD_CHANGE"
        assert receipt["component_deltas"] == [{
            "change_type": "ADDED",
            "current_copper_source_value": "8150.0",
            "current_gold_source_value": "1430.0",
            "period": "2026-08",
            "previous_copper_source_value": None,
            "previous_gold_source_value": None,
        }]
        assert "monthly" not in receipt
        assert len(list((root / "revisions").glob("*.json"))) == 2


def test_no_silent_network_fallback():
    with mock.patch.object(owner.urllib.request, "urlopen", side_effect=OSError("offline")):
        with pytest.raises(owner.OwnerError) as caught:
            owner.fetch_payload("https://example.invalid", timeout=0.1, retries=0, backoff=0)
    assert caught.value.status == "NETWORK_ERROR"


def test_registry_matches_current_source_and_has_no_fallback():
    registry = json.loads((ROOT / "02_DATA_PING/data_terminal/source_registry/world_bank_pink_sheet_copper_gold.json").read_text())
    assert registry["url"] == owner.SOURCE_URL
    assert registry["source_id"] == owner.SOURCE_ID
    assert registry["fallback"] == "NONE"
    assert registry["authority"]["portfolio_action"] is False


def test_committed_baseline_is_current_complete_and_manifest_bound():
    root = ROOT / "03_DAILY_CAPTURE_LOGS/slow_cycle/copper_gold"
    latest = json.loads((root / "LATEST.json").read_text())
    assert latest["status"] == "PASS"
    assert latest["last_period"] == "2026-07"
    assert latest["freshness"]["status"] == "PASS"
    with (root / "normalized/monthly_observations.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 799
    assert rows[0]["period"] == "1960-01"
    assert rows[-1]["period"] == "2026-07"
    manifest = json.loads((root / "ARTIFACT_MANIFEST.json").read_text())
    for relative_path, expected_hash in manifest["members"].items():
        assert owner.sha256_bytes((root / relative_path).read_bytes()) == expected_hash
    assert manifest["authority"]["execution_authority"] is False
