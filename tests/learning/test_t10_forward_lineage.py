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

    def blob_sha(self, path: Path) -> str:
        content = path.read_bytes()
        return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()

    def complete_fixture(self, root: Path, week: str = "2026-W29") -> dict:
        ledger = f"03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-13__forecast-ledger-{week.lower()}__official.md"
        source = f"owners/{week}/source.md"
        receipt = f"owners/{week}/receipt.json"
        handoff = f"owners/{week}/handoff.md"
        actual = f"actuals/{week}.json"
        score = f"scores/{week}.json"
        source_id = f"ACTUAL-{week}"
        self.write(root, ledger, f"source_master_monday: {source}\n- MM_2026_W29_RANGE_A\n")
        self.write(root, source, "ratified source")
        self.write(root, handoff, f"forecast: {ledger}")
        self.write(
            root,
            receipt,
            {"artifact_paths": {"forecast": ledger, "source": source, "handoff": handoff},
             "artifact_verification": [
                 {"path": p, "blob_sha": self.blob_sha(root / p)}
                 for p in (ledger, source, handoff)]},
        )
        self.write(root, actual, {"archive_id": source_id})
        self.write(root, score, {"source_forecast": ledger, "source_actuals": source_id,
                               "rows": [{"forecast_id": "MM_2026_W29_RANGE_A", "score": 0}]})
        route = {
            week: {
                "source_master_monday": source,
                "ratification_receipt": receipt,
                "cn_handoff": handoff,
                "verified_actual": actual,
                "score": score,
                "actual_link": {"kind": "shared_token", "token": source_id},
            }
        }
        route[week]["trusted_blob_bindings"] = {
            edge: self.blob_sha(root / route[week][edge])
            for edge in ("ratification_receipt", "verified_actual", "score")
        }
        return route

    def test_complete_forward_row_has_all_immutable_edges(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = self.complete_fixture(root)
            report = build_report(root, routes)
            row = report["rows"][0]
            self.assertEqual(row["status"], "COMPLETE_SCORED_LINEAGE")
            self.assertEqual(set(row["references"]), {"forecast", "source_master_monday", "ratification_receipt", "cn_handoff", "verified_actual", "score"})
            self.assertTrue(all(row["references"][edge]["immutable"] for edge in row["references"]))
            self.assertEqual(row["score_row"]["json_pointer"], "/rows/0")

    def test_modified_frozen_inputs_are_blocked(self):
        for edge in ("forecast", "source_master_monday", "cn_handoff"):
            with self.subTest(edge=edge), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                routes = self.complete_fixture(root)
                path = next(root.glob("03_WEEKLY_OPERATIONS/forecast_ledger/*")) if edge == "forecast" else root / routes["2026-W29"][edge]
                path.write_text(path.read_text() + "\nretroactive rewrite")
                row = build_report(root, routes)["rows"][0]
                self.assertEqual(row["scoring_status"], "BLOCKED")
                self.assertIn(f"{edge}:frozen_blob_mismatch", row["missing_edges"])
                self.assertFalse(row["references"][edge]["immutable"])

    def test_missing_or_duplicate_frozen_binding_blocks(self):
        for duplicate in (False, True):
            with self.subTest(duplicate=duplicate), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                routes = self.complete_fixture(root)
                path = root / routes["2026-W29"]["ratification_receipt"]
                receipt = json.loads(path.read_text())
                receipt["artifact_verification"] = receipt["artifact_verification"] * 2 if duplicate else []
                self.write(root, str(path.relative_to(root)), receipt)
                self.assertEqual(build_report(root, routes)["rows"][0]["scoring_status"], "BLOCKED")

    def test_week_aggregate_or_other_row_never_scores_forecast(self):
        for rows in ([], [{"forecast_id": "OTHER", "score": 100}],
                     [{"forecast_id": "MM_2026_W29_RANGE_A", "score": None}],
                     [{"forecast_id": "MM_2026_W29_RANGE_A", "score": True}],
                     [{"forecast_id": "MM_2026_W29_RANGE_A", "score": 50}] * 2):
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                routes = self.complete_fixture(root)
                path = root / routes["2026-W29"]["score"]
                score = json.loads(path.read_text())
                score.update(rows=rows, weekly_score=100)
                self.write(root, str(path.relative_to(root)), score)
                routes["2026-W29"]["trusted_blob_bindings"]["score"] = self.blob_sha(path)
                row = build_report(root, routes)["rows"][0]
                self.assertEqual(row["scoring_status"], "BLOCKED")
                self.assertIsNone(row["score_row"])

    def test_empty_official_ledger_fails_gate_even_without_rows(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = self.complete_fixture(root)
            w28 = "03_WEEKLY_OPERATIONS/forecast_ledger/2026-07-06__forecast-ledger-2026-w28__official.md"
            self.write(root, w28, "MM_2026_W28_RANGE_A")
            self.assertEqual(build_report(root, routes)["post_fix_gate"]["status"], "PASS")
            empty = "03_WEEKLY_OPERATIONS/forecast_ledger/2026-08-03__forecast-ledger-2026-w32__official.md"
            for content in ("", "FUTURE_UNRECOGNIZED_ID"):
                self.write(root, empty, content)
                report = build_report(root, routes)
                self.assertEqual(report["discovery"]["empty_or_unrecognized_ledgers"], 1)
                self.assertEqual(report["post_fix_gate"]["status"], "FAIL")

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

    def test_coordinated_artifact_and_receipt_rewrite_cannot_self_authenticate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = self.complete_fixture(root)
            route = routes["2026-W29"]
            ledger = next(root.glob("03_WEEKLY_OPERATIONS/forecast_ledger/*"))
            ledger.write_text(ledger.read_text() + "\ncoordinated rewrite")
            receipt_path = root / route["ratification_receipt"]
            receipt = json.loads(receipt_path.read_text())
            for row in receipt["artifact_verification"]:
                if row["path"] == str(ledger.relative_to(root)):
                    row["blob_sha"] = self.blob_sha(ledger)
            self.write(root, route["ratification_receipt"], receipt)

            row = build_report(root, routes)["rows"][0]
            self.assertEqual(row["scoring_status"], "BLOCKED")
            self.assertIn("ratification_receipt:trusted_blob_mismatch", row["missing_edges"])
            self.assertFalse(row["references"]["ratification_receipt"]["immutable"])

    def test_forecast_id_from_different_week_is_blocked_before_routing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = self.complete_fixture(root)
            route = routes["2026-W29"]
            ledger = next(root.glob("03_WEEKLY_OPERATIONS/forecast_ledger/*"))
            ledger.write_text(ledger.read_text() + "\n- MM_2026_W30_RANGE_WRONG_WEEK\n")
            receipt_path = root / route["ratification_receipt"]
            receipt = json.loads(receipt_path.read_text())
            for binding in receipt["artifact_verification"]:
                if binding["path"] == str(ledger.relative_to(root)):
                    binding["blob_sha"] = self.blob_sha(ledger)
            self.write(root, route["ratification_receipt"], receipt)
            route["trusted_blob_bindings"]["ratification_receipt"] = self.blob_sha(receipt_path)

            report = build_report(root, routes)
            by_id = {row["forecast_id"]: row for row in report["rows"]}
            self.assertEqual(by_id["MM_2026_W29_RANGE_A"]["scoring_status"], "SCORED")
            wrong = by_id["MM_2026_W30_RANGE_WRONG_WEEK"]
            self.assertEqual(wrong["scoring_status"], "BLOCKED")
            self.assertEqual(wrong["embedded_week"], "2026-W30")
            self.assertIn("forecast_id:week_mismatch", wrong["missing_edges"])
            self.assertEqual(report["discovery"]["week_mismatched_forecast_ids"], 1)

    def test_pending_censored_or_ineligible_owner_rows_never_score(self):
        cases = [
            {"row": {"status": "PENDING_MATURITY", "mature": False}},
            {"row": {"maturity_status": "CENSORED"}},
            {"row": {"score_eligible": False}},
            {"row": {"scientific_score_eligible": False}},
            {"document": {"status": "PENDING_MATURITY", "mature": False}},
            {"document": {"eligibility_status": "REJECTED"}},
        ]
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                routes = self.complete_fixture(root)
                route = routes["2026-W29"]
                score_path = root / route["score"]
                score = json.loads(score_path.read_text())
                score.update(case.get("document", {}))
                score["rows"][0].update(case.get("row", {}))
                self.write(root, route["score"], score)
                route["trusted_blob_bindings"]["score"] = self.blob_sha(score_path)

                row = build_report(root, routes)["rows"][0]
                self.assertEqual(row["scoring_status"], "BLOCKED")
                self.assertIsNone(row["score_row"])
                self.assertIn("score_row:explicit_forecast_id_binding_missing_or_invalid", row["missing_edges"])

    def test_explicit_mature_and_eligible_owner_row_can_score(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = self.complete_fixture(root)
            route = routes["2026-W29"]
            score_path = root / route["score"]
            score = json.loads(score_path.read_text())
            score.update(status="FINAL", mature=True, score_eligible=True)
            score["rows"][0].update(status="SCORED", mature=True, score_eligible=True, scientific_score_eligible=True)
            self.write(root, route["score"], score)
            route["trusted_blob_bindings"]["score"] = self.blob_sha(score_path)

            row = build_report(root, routes)["rows"][0]
            self.assertEqual(row["scoring_status"], "SCORED")
            self.assertIsNotNone(row["score_row"])


if __name__ == "__main__":
    unittest.main()
