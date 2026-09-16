from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.learning.t10_forward_lineage import build_report


class T10ForwardLineageTests(unittest.TestCase):
    def write(self, root: Path, relative: str, value: str | dict) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, dict):
            path.write_text(json.dumps(value, sort_keys=True))
        else:
            path.write_text(value)

    def complete_fixture(self, root: Path, week: str = "2026-W29") -> dict:
        ledger = f"03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-13__forecast-ledger-{week.lower()}__official.md"
        source = f"owners/{week}/source.md"
        receipt = f"owners/{week}/receipt.json"
        handoff = f"owners/{week}/handoff.md"
        actual = f"actuals/{week}.json"
        score = f"scores/{week}.md"
        source_id = f"ACTUAL-{week}"
        self.write(root, ledger, f"source_master_monday: {source}\n- MM_2026_W29_RANGE_A\n")
        self.write(root, source, "ratified source")
        self.write(root, handoff, f"forecast: {ledger}")
        self.write(
            root,
            receipt,
            {"artifact_paths": {"forecast": ledger, "source": source, "handoff": handoff}},
        )
        self.write(root, actual, {"archive_id": source_id})
        self.write(root, score, f"source_forecast: {ledger}\nsource_actuals: {source_id}\n")
        return {
            week: {
                "source_master_monday": source,
                "ratification_receipt": receipt,
                "cn_handoff": handoff,
                "verified_actual": actual,
                "score": score,
                "actual_link": {"kind": "shared_token", "token": source_id},
            }
        }

    def test_complete_forward_row_has_all_immutable_edges(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = self.complete_fixture(root)
            report = build_report(root, routes)
            row = report["rows"][0]
            self.assertEqual(row["status"], "COMPLETE_SCORED_LINEAGE")
            self.assertEqual(set(row["references"]), {"forecast", "source_master_monday", "ratification_receipt", "cn_handoff", "verified_actual", "score"})
            self.assertTrue(all(ref["immutable"] for ref in row["references"].values()))

    def test_missing_edge_is_exact_and_blocks_scoring(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = self.complete_fixture(root)
            (root / routes["2026-W29"]["cn_handoff"]).unlink()
            report = build_report(root, routes)
            row = report["rows"][0]
            self.assertEqual(row["status"], "INCOMPLETE_SCORING_BLOCKED")
            self.assertIn("cn_handoff:file_missing", row["missing_edges"])

    def test_mutable_latest_pointer_cannot_substitute_for_frozen_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = self.complete_fixture(root)
            old = routes["2026-W29"]["source_master_monday"]
            latest = "owners/2026-W29/LATEST_SOURCE.md"
            self.write(root, latest, (root / old).read_text())
            routes["2026-W29"]["source_master_monday"] = latest
            report = build_report(root, routes)
            self.assertIn("source_master_monday:mutable_reference", report["rows"][0]["missing_edges"])

    def test_w28_stays_unscored_even_when_later_narrative_exists(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = "03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-06__forecast-ledger-2026-w28__official.md"
            self.write(root, ledger, "- MM_2026_W28_RANGE_A")
            self.write(root, "03_WEEKLY_OPERATIONS/master_monday/2026-W28/05_forecast-ledger-lineage-correction.md", "SOURCE_LINEAGE_UNRESOLVED")
            self.write(root, "03_WEEKLY_OPERATIONS/master_monday/2026-W29/03_framework_ratified_final.md", "later actual narrative")
            report = build_report(root, {})
            row = report["rows"][0]
            self.assertEqual(row["status"], "UNSCORED_LINEAGE_GAP")
            self.assertEqual(row["scoring_status"], "BLOCKED")
            self.assertIsNone(row["references"]["source_master_monday"])

    def test_report_is_read_only_for_all_sources(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = self.complete_fixture(root)
            before = {
                path: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in root.rglob("*")
                if path.is_file()
            }
            build_report(root, routes)
            after = {
                path: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after)

    def test_unrouted_future_official_ledger_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ledger = "03_WEEKLY_OPERATIONS/forecast_ledger/2026-08-03__forecast-ledger-2026-w32__official.md"
            self.write(root, ledger, "- MM_2026_W32_RANGE_A")
            report = build_report(root, {})
            self.assertEqual(report["rows"][0]["status"], "INCOMPLETE_SCORING_BLOCKED")
            self.assertIn("owner_route:missing", report["rows"][0]["missing_edges"])


if __name__ == "__main__":
    unittest.main()
