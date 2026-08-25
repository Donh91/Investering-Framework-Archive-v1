from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PROJECT = Path(__file__).parents[2]
RESEARCH_SCRIPTS = PROJECT / "scripts" / "research"
if str(RESEARCH_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(RESEARCH_SCRIPTS))

import shared_row_tournament_relevance as relevance
import shared_row_tournament_weekly as weekly


FLOOR = "2026-09-30T00:00:00Z"


def runtime(active: bool = True) -> dict:
    return {
        "collection_state": weekly.ACTIVE_COLLECTION_STATE if active else "QUARANTINED_PENDING_POST_REPAIR_EVIDENCE",
        "core_prospective_eligibility_status": weekly.ACTIVE_FLOOR_STATUS if active else "CONTAINMENT_SENTINEL_NOT_AN_ACTIVATION_FLOOR",
        "core_prospective_eligibility_start": FLOOR,
    }


def row(event_id: str, timestamp: str = "2026-10-01T00:00:00Z") -> dict:
    return {
        "event_id": event_id,
        "observation_timestamp_utc": timestamp,
        "information_cutoff_utc": timestamp,
        "source_version_commit": "1" * 40,
        "row_integrity_contract": weekly.ROW_INTEGRITY_CONTRACT,
        "source_binding_manifest": "{}",
        "source_binding_manifest_sha256": "2" * 64,
        "candidate_decisions": json.dumps({"C07_SIMPLE_3": True, "C08_SIMPLE_3_ETF": False}),
        "outcome_24h": "1",
        "outcome_72h": "1",
        "outcome_7d": "1",
        "provenance_hash": "a" * 64,
    }


def divergence(event_id: str, divergence_id: str, provenance: str | None = None) -> dict:
    parent_hash = "a" * 64
    expected = hashlib.sha256((parent_hash + divergence_id).encode("utf-8")).hexdigest()
    return {
        "divergence_id": divergence_id,
        "event_id": event_id,
        "observation_timestamp_utc": "2026-10-01T00:00:00Z",
        "information_cutoff_utc": "2026-10-01T00:00:00Z",
        "candidate_a": "C07_SIMPLE_3",
        "candidate_b": "C08_SIMPLE_3_ETF",
        "decision_a": "true",
        "decision_b": "false",
        "outcome_24h": "1",
        "outcome_72h": "1",
        "outcome_7d": "1",
        "provenance_hash": provenance or expected,
    }


def verifier(candidate: dict, _cutoff) -> dict:
    if candidate["event_id"] == "UNBOUND":
        raise ValueError("source binding reconstruction failed")
    return {"status": "BOUND"}


def write_csv(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for record in records for key in record})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)


class SharedRowConsumerIntegrityTests(unittest.TestCase):
    def adversarial_data(self):
        good = row("GOOD")
        pre_floor = row("PRE_FLOOR", "2026-09-29T23:00:00Z")
        unbound = row("UNBOUND")
        bad_provenance = row("BAD_PROVENANCE")
        bad_provenance["provenance_hash"] = "not-a-sha256"
        rows = [good, pre_floor, unbound, bad_provenance]
        divs = [
            divergence("GOOD", "D_GOOD"),
            divergence("PRE_FLOOR", "D_PRE_FLOOR"),
            divergence("UNBOUND", "D_UNBOUND"),
            divergence("GOOD", "D_BAD_HASH", "0" * 64),
        ]
        return rows, divs

    def test_shared_filter_counts_only_bound_post_floor_rows(self) -> None:
        rows, divs = self.adversarial_data()
        valid_rows, valid_divs, excluded = weekly.filter_consumer_rows(rows, divs, runtime(), verifier)
        self.assertEqual([item["event_id"] for item in valid_rows], ["GOOD"])
        self.assertEqual([item["divergence_id"] for item in valid_divs], ["D_GOOD"])
        self.assertEqual(excluded["pre_floor_or_timestamp"], 1)
        self.assertEqual(excluded["source_binding"], 1)
        self.assertEqual(excluded["immutable_provenance"], 1)
        self.assertEqual(excluded["divergence_parent"], 2)
        self.assertEqual(excluded["divergence_provenance"], 1)

    def test_quarantine_excludes_every_row_and_divergence(self) -> None:
        rows, divs = self.adversarial_data()
        valid_rows, valid_divs, excluded = weekly.filter_consumer_rows(rows, divs, runtime(False), verifier)
        self.assertEqual(valid_rows, [])
        self.assertEqual(valid_divs, [])
        self.assertEqual(excluded["runtime_inactive"], len(rows))
        self.assertEqual(excluded["divergence_parent"], len(divs))

    def test_weekly_and_relevance_use_the_same_fail_closed_filter(self) -> None:
        self.assertIs(relevance.filter_consumer_rows, weekly.filter_consumer_rows)
        rows, divs = self.adversarial_data()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_csv(root / "data" / "PROSPECTIVE_SHARED_ROW_LEDGER.csv", rows)
            write_csv(root / "14_DIVERGENCE_FNP_LEDGER.csv", divs)
            (root / "RUNTIME_STATUS.json").write_text(json.dumps(runtime()))
            (root / "03_CANDIDATE_REGISTRY.json").write_text(json.dumps({"candidates": [{"id": "C07_SIMPLE_3"}, {"id": "C08_SIMPLE_3_ETF"}]}))
            (root / "OWNER_BINDING_MATRIX.json").write_text(json.dumps({"families": [{"family_id": "CORE", "status": "READY"}]}))
            with mock.patch.object(weekly.evidence, "verify_source_bindings", verifier), mock.patch.multiple(
                weekly,
                ROOT=root,
                LED=root / "data" / "PROSPECTIVE_SHARED_ROW_LEDGER.csv",
                FNP=root / "14_DIVERGENCE_FNP_LEDGER.csv",
                REG=root / "03_CANDIDATE_REGISTRY.json",
                OUT=root / "weekly",
            ), mock.patch.object(relevance, "ROOT", root):
                weekly.main()
                relevance.main()
            weekly_report = json.loads((root / "weekly" / "LATEST.json").read_text())
            relevance_report = json.loads((root / "RELEVANCE_STATE.json").read_text())
            self.assertEqual((weekly_report["eligible_rows_total"], weekly_report["divergences_total"]), (1, 1))
            self.assertEqual((relevance_report["eligible_row_n"], relevance_report["divergence_n"]), (1, 1))


if __name__ == "__main__":
    unittest.main()
