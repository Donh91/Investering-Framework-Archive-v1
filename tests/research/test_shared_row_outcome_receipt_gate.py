from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "scripts/research"))
import shared_row_outcome_receipt_gate as gate


def fixture():
    cutoff = "2026-11-01T10:00:00Z"
    event_id = "PSR_20261101T100000Z"
    row = {
        "event_id": event_id,
        "observation_timestamp_utc": cutoff,
        "information_cutoff_utc": cutoff,
        "source_version_commit": "1" * 40,
        "source_binding_manifest_sha256": "2" * 64,
        "outcome_24h": "1",
        "mae_24h": "-0.50000000",
        "mfe_24h": "2.00000000",
        "outcome_72h": "",
        "mae_72h": "",
        "mfe_72h": "",
        "outcome_7d": "",
        "mae_7d": "",
        "mfe_7d": "",
    }
    base = {"ethbtc": 0.03, "btc": 100.0, "eth": 3.0}
    end = {"ethbtc": 0.0303, "btc": 101.0, "eth": 3.0603}
    outcome_commit = "3" * 40
    binding = {
        "path": "03_DAILY_CAPTURE_LOGS/hourly/2026/11/2026-11-02.csv",
        "sha256": "4" * 64,
        "bytes": 18000,
        "source_commit": outcome_commit,
        "owner_contract": "HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT",
        "provider": "Binance spot",
    }
    detail = {
        "event_id": event_id,
        "horizon": "24h",
        "observation_timestamp_utc": cutoff,
        "information_cutoff_utc": cutoff,
        "target_timestamp_utc": "2026-11-02T10:00:00Z",
        "selected_end_timestamp_utc": "2026-11-02T10:00:00Z",
        "baseline_timestamp_utc": "2026-11-01T09:00:00Z",
        "sample_count": 26,
        "source_contract": "HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT",
        "row_source_commit": row["source_version_commit"],
        "row_source_binding_sha256": row["source_binding_manifest_sha256"],
        "outcome_source_commit": outcome_commit,
        "outcome_source_bindings": json.dumps([binding], sort_keys=True, separators=(",", ":")),
        "baseline_reconciled": True,
        "matured_at_utc": "2026-11-02T11:00:00Z",
    }
    for name in base:
        detail[f"{name}_baseline"] = base[name]
        detail[f"{name}_end"] = end[name]
        detail[f"{name}_forward_return_pct"] = (end[name] / base[name] - 1) * 100
        detail[f"{name}_mae_pct"] = -0.5
        detail[f"{name}_mfe_pct"] = 2.0
    detail["provenance_hash"] = hashlib.sha256(gate.canonical(detail).encode("utf-8")).hexdigest()
    return row, detail


def signed(detail):
    detail["provenance_hash"] = hashlib.sha256(
        gate.canonical({k: v for k, v in detail.items() if k != "provenance_hash"}).encode("utf-8")
    ).hexdigest()
    return detail


class OutcomeReceiptGateTests(unittest.TestCase):
    def reject(self, row, details):
        with self.assertRaises((ValueError, KeyError, TypeError, OverflowError)):
            gate.verify_row_outcomes(row, gate.detail_index(details))

    def test_valid_source_owner_receipt_and_parent_are_accepted(self):
        row, detail = fixture()
        gate.verify_row_outcomes(row, gate.detail_index([detail]))

    def test_missing_detail_on_matured_row_rejected(self):
        row, _ = fixture()
        self.reject(row, [])

    def test_blank_outcome_with_forged_detail_rejected(self):
        row, detail = fixture()
        row["outcome_24h"] = row["mae_24h"] = row["mfe_24h"] = ""
        self.reject(row, [detail])

    def test_second_detail_for_same_event_and_horizon_rejected(self):
        row, detail = fixture()
        self.reject(row, [detail, copy.deepcopy(detail)])

    def test_altered_detail_value_without_resigning_rejected(self):
        row, detail = fixture()
        detail["ethbtc_end"] = 0.0305
        self.reject(row, [detail])

    def test_forged_resigned_direction_still_fails_parent(self):
        row, detail = fixture()
        row["outcome_24h"] = "0"
        self.reject(row, [detail])

    def test_forged_resigned_path_metric_still_fails_parent(self):
        row, detail = fixture()
        row["mae_24h"] = "-1.00000000"
        self.reject(row, [detail])

    def test_wrong_frozen_row_source_link_rejected(self):
        row, detail = fixture()
        detail["row_source_commit"] = "a" * 40
        self.reject(row, [signed(detail)])

    def test_unavailable_before_target_closed_rejected(self):
        row, detail = fixture()
        detail["matured_at_utc"] = "2026-11-02T10:30:00Z"
        self.reject(row, [signed(detail)])

    def test_label_clock_relative_to_actual_issue_rejected(self):
        row, detail = fixture()
        detail["target_timestamp_utc"] = "2026-11-02T09:00:00Z"
        self.reject(row, [signed(detail)])

    def test_baseline_to_end_sample_count_mismatch_rejected(self):
        row, detail = fixture()
        detail["sample_count"] = 25
        self.reject(row, [signed(detail)])

    def test_fake_provider_in_outcome_source_binding_rejected(self):
        row, detail = fixture()
        bindings = json.loads(detail["outcome_source_bindings"])
        bindings[0]["provider"] = "Fake/other"
        detail["outcome_source_bindings"] = json.dumps(bindings, sort_keys=True, separators=(",", ":"))
        self.reject(row, [signed(detail)])

    def test_invalid_nonfinite_value_in_receipt_rejected(self):
        row, detail = fixture()
        detail["ethbtc_end"] = float("nan")
        self.reject(row, [signed(detail)])

    def test_mismatched_return_and_frozen_source_prices_rejected(self):
        row, detail = fixture()
        detail["ethbtc_forward_return_pct"] = 42.0
        self.reject(row, [signed(detail)])

    def test_pre_matured_empty_parent_without_detail_accepted(self):
        row, _ = fixture()
        for key in ("outcome_24h", "mae_24h", "mfe_24h"):
            row[key] = ""
        gate.verify_row_outcomes(row, gate.detail_index([]))


if __name__ == "__main__":
    unittest.main()
